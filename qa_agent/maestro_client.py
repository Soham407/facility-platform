from __future__ import annotations

import os
import re
import subprocess
import socket
import tempfile
import time
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from .config import NightShiftConfig, split_command
from .models import ActionDecision, ScreenSnapshot
from .screen_classifier import ScreenClassifier
from .subprocess_utils import normalize_command, powershell_executable


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class MaestroClient:
    def __init__(self, config: NightShiftConfig, classifier: ScreenClassifier) -> None:
        self.config = config
        self.classifier = classifier

    def _maestro(self, *subcommand: str) -> list[str]:
        """Build a Maestro CLI argv with the correct --device flag."""
        return [self.config.maestro_command, "--device", self.config.emulator_id, *subcommand]

    def capture_screen(self) -> ScreenSnapshot:
        hierarchy = self._run(self._maestro("hierarchy")).stdout
        if not hierarchy.strip():
            raise RuntimeError("Maestro hierarchy returned empty output.")

        visible_texts, resource_ids, package_name = self._extract_tokens(hierarchy)
        match = self.classifier.classify(visible_texts, resource_ids)
        return ScreenSnapshot(
            screen_id=match.screen_id,
            screen_label=match.label,
            ui_hierarchy=hierarchy,
            visible_texts=visible_texts[:80],
            resource_ids=resource_ids[:80],
            package_name=package_name,
        )

    def tap(self, target: str) -> CommandResult:
        flow = self._build_tap_flow(target)
        return self._run_flow(flow)

    def input_text(self, target: str, text: str) -> CommandResult:
        selector = self._tap_selector(target)
        flow = (
            f"appId: {self.config.app_id}\n"
            "---\n"
            f"- tapOn:\n{selector}\n"
            f'- inputText: "{_escape_yaml_string(text)}"\n'
        )
        return self._run_flow(flow)

    def scroll_down(self) -> CommandResult:
        flow = f"appId: {self.config.app_id}\n---\n- scroll\n"
        return self._run_flow(flow)

    def back(self) -> CommandResult:
        return self._run(
            [self.config.adb_command, "-s", self.config.emulator_id, "shell", "input", "keyevent", "KEYCODE_BACK"],
            allow_failure=True,
        )

    def launch(self) -> CommandResult:
        if self.config.app_launch_command.strip():
            return self._run(self._command_from_text(self.config.app_launch_command), allow_failure=True)

        package = self._launch_package_name()
        return self._run(
            [self.config.adb_command, "-s", self.config.emulator_id, "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"],
            allow_failure=True,
        )

    def stop_app(self) -> CommandResult:
        if self.config.app_stop_command.strip():
            return self._run(self._command_from_text(self.config.app_stop_command), allow_failure=True)

        package = self._launch_package_name()
        return self._run(
            [self.config.adb_command, "-s", self.config.emulator_id, "shell", "am", "force-stop", package],
            allow_failure=True,
        )

    def get_logcat_excerpt(self, lines: int) -> str:
        result = self._run(
            [self.config.adb_command, "-s", self.config.emulator_id, "logcat", "-d", "-t", str(lines)],
            allow_failure=True,
        )
        return result.stdout or result.stderr

    def wait_for_settle(self) -> None:
        time.sleep(self.config.step_delay_seconds)

    def wait_only(self) -> CommandResult:
        time.sleep(self.config.step_delay_seconds)
        return CommandResult(returncode=0, stdout="", stderr="")

    def prepare_runtime(self) -> None:
        self._wait_for_device()

        if self.config.mobile_start_command.strip():
            if not self._is_local_port_open(self.config.metro_port):
                self._start_background_command(self.config.mobile_start_command)
                self._wait_for_local_port(self.config.metro_port, timeout_seconds=120)

        elif self.config.app_start_mode in {"dev_client", "expo_go"}:
            if not self._is_local_port_open(self.config.metro_port):
                default_command = "npx expo start --dev-client --clear --port {port}"
                if self.config.app_start_mode == "expo_go":
                    default_command = "npx expo start --clear --port {port}"
                self._start_background_command(default_command.format(port=self.config.metro_port))
                self._wait_for_local_port(self.config.metro_port, timeout_seconds=120)

        package = self._launch_package_name()
        if not self.is_package_installed(package):
            raise RuntimeError(
                f"Required app package is not installed on the emulator: {package}. "
                "Install the dev client/build first or switch startup mode."
            )

        self.stop_app()
        time.sleep(1.0)
        self.launch()
        time.sleep(6.0)
        self._enter_app_from_dev_client()

    def _run(self, command: list[str], allow_failure: bool = False, timeout: int = 30) -> CommandResult:
        try:
            completed = subprocess.run(
                normalize_command(command), capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            if allow_failure:
                return CommandResult(returncode=1, stdout="", stderr=f"Command timed out after {timeout}s: {' '.join(command)}")
            raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(command)}")
        result = CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        if not allow_failure and completed.returncode != 0:
            raise RuntimeError(f"Command failed: {' '.join(command)}\n{completed.stderr}")
        return result

    def _command_from_text(self, command: str) -> list[str]:
        return split_command(command)

    def _launch_package_name(self) -> str:
        if self.config.app_start_mode == "expo_go":
            return "host.exp.exponent"
        return self.config.app_id

    def _wait_for_device(self, timeout_seconds: int = 20) -> None:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            result = self._run([self.config.adb_command, "-s", self.config.emulator_id, "get-state"], allow_failure=True)
            if "device" in (result.stdout or "").lower():
                return
            time.sleep(1.0)
        raise RuntimeError(f"Android device {self.config.emulator_id} is not available.")

    def _start_background_command(self, command: str) -> None:
        subprocess.Popen(
            [powershell_executable(), "-NoProfile", "-Command", command],
            cwd=self.config.mobile_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _is_local_port_open(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            return sock.connect_ex(("127.0.0.1", port)) == 0

    def _wait_for_local_port(self, port: int, timeout_seconds: int) -> None:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if self._is_local_port_open(port):
                return
            time.sleep(1.0)
        raise RuntimeError(f"Timed out waiting for local port {port}.")

    def is_package_installed(self, package_name: str) -> bool:
        result = self._run(
            [self.config.adb_command, "-s", self.config.emulator_id, "shell", "pm", "list", "packages", package_name],
            allow_failure=True,
        )
        normalized = result.stdout.strip().lower()
        return f"package:{package_name.lower()}" in normalized

    def _enter_app_from_dev_client(self) -> None:
        if self.config.app_start_mode != "dev_client":
            return

        for _ in range(8):
            snapshot = self.capture_screen()
            texts = {text.strip() for text in snapshot.visible_texts}

            if "Mobile OTP Sign-In" in texts:
                return

            if "FacilityPro" in texts:
                self.tap("FacilityPro")
                time.sleep(8.0)
                continue

            metro_entry = f"http://10.0.2.2:{self.config.metro_port}"
            if metro_entry in texts:
                self.tap(metro_entry)
                time.sleep(8.0)
                continue

            if "Continue" in texts:
                self.tap("Continue")
                time.sleep(3.0)
                continue

            if "Go home" in texts:
                self.tap("Go home")
                time.sleep(4.0)
                self.launch()
                time.sleep(6.0)
                continue

            if "Got it" in texts:
                self.tap("Got it")
                time.sleep(2.0)
                continue

            time.sleep(2.0)

    def _build_tap_flow(self, target: str) -> str:
        selector = self._tap_selector(target)
        return (
            f"appId: {self.config.app_id}\n"
            "---\n"
            f"- tapOn:\n{selector}\n"
        )

    def _tap_selector(self, target: str) -> str:
        # resource-ids look like  com.package:id/button_name  or  com.package:type/name
        # URLs (http://host:port/path) must NOT be treated as resource-ids.
        if target.startswith("qa_"):
            return f'    id: "{_escape_yaml_string(target)}"'
        if re.search(r":[a-zA-Z]+/", target):
            package_prefix = f"{self.config.app_id}:id/"
            if target.startswith(package_prefix):
                target = target[len(package_prefix):]
            return f'    id: "{_escape_yaml_string(target)}"'
        return f'    text: "{_escape_yaml_string(target)}"'

    def _run_flow(self, yaml_content: str) -> CommandResult:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(yaml_content)
            flow_path = fh.name
        try:
            return self._run(self._maestro("test", flow_path), allow_failure=True, timeout=60)
        finally:
            try:
                os.unlink(flow_path)
            except OSError:
                pass

    def _extract_tokens(self, hierarchy: str) -> tuple[list[str], list[str], str | None]:
        visible_texts: list[str] = []
        resource_ids: list[str] = []
        package_name: str | None = None

        json_start = hierarchy.find("{")
        if json_start != -1:
            try:
                payload = json.loads(hierarchy[json_start:])
                self._walk_json_node(payload, visible_texts, resource_ids)
                return visible_texts, resource_ids, package_name
            except json.JSONDecodeError:
                pass

        try:
            root = ET.fromstring(hierarchy)
        except ET.ParseError:
            return visible_texts, resource_ids, package_name

        for node in root.iter():
            if package_name is None:
                package_name = node.attrib.get("package")
            text_value = (node.attrib.get("text") or "").strip()
            if text_value and text_value not in visible_texts:
                visible_texts.append(text_value)
            resource_id = (node.attrib.get("resource-id") or "").strip()
            if resource_id and resource_id not in resource_ids:
                resource_ids.append(resource_id)

        return visible_texts, resource_ids, package_name

    def _walk_json_node(self, node: object, visible_texts: list[str], resource_ids: list[str]) -> None:
        if not isinstance(node, dict):
            return

        attributes = node.get("attributes")
        if isinstance(attributes, dict):
            text_value = str(attributes.get("text") or "").strip()
            if text_value and text_value not in visible_texts:
                visible_texts.append(text_value)

            accessibility_text = str(attributes.get("accessibilityText") or "").strip()
            if accessibility_text and accessibility_text not in visible_texts:
                visible_texts.append(accessibility_text)

            resource_id = str(attributes.get("resource-id") or "").strip()
            if resource_id and resource_id not in resource_ids:
                resource_ids.append(resource_id)

        children = node.get("children")
        if isinstance(children, list):
            for child in children:
                self._walk_json_node(child, visible_texts, resource_ids)


def _escape_yaml_string(value: str) -> str:
    """Escape backslashes and double-quotes for embedding in a YAML double-quoted scalar."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def fallback_action_for_screen(screen: ScreenSnapshot) -> ActionDecision:
    if screen.screen_id == "authentication-onboarding":
        if any("Send OTP" in text for text in screen.visible_texts):
            return ActionDecision("tap", "Send OTP", "Fallback auth progression")
        return ActionDecision("tap", "Continue", "Fallback auth continuation")
    if screen.screen_id == "buyer-supplier-mobile-apps":
        for candidate in ("Requests", "Invoices", "Feedback", "Refresh buyer feed"):
            if candidate in screen.visible_texts:
                return ActionDecision("tap", candidate, "Fallback buyer navigation")
    if screen.screen_id == "security-guard-app":
        for candidate in ("Checklist", "Visitor Logging", "Emergency contacts"):
            if candidate in screen.visible_texts:
                return ActionDecision("tap", candidate, "Fallback guard navigation")
    return ActionDecision("back", "BACK", "Fallback recovery action")
