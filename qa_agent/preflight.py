from __future__ import annotations

import socket
import subprocess
from dataclasses import dataclass

from .config import NightShiftConfig
from .maestro_client import MaestroClient
from .screen_classifier import ScreenClassifier
from .subprocess_utils import normalize_command


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str


def _run(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(normalize_command(command), capture_output=True, text=True, timeout=20)
    except Exception as exc:
        return False, str(exc)

    output = (completed.stdout or completed.stderr).strip()
    return completed.returncode == 0, output


def _is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def run_preflight() -> tuple[int, list[CheckResult]]:
    config = NightShiftConfig.load()
    maestro = MaestroClient(config, ScreenClassifier())
    checks: list[CheckResult] = []

    for name, command in (
        ("python", ["python", "--version"]),
        ("node", ["node", "--version"]),
        ("npm", ["npm", "--version"]),
        ("maestro", [config.maestro_command, "--version"]),
        ("adb", [config.adb_command, "version"]),
    ):
        ok, output = _run(command)
        checks.append(CheckResult(name, ok, output))

    ok, output = _run([config.adb_command, "devices", "-l"])
    checks.append(CheckResult("adb devices", ok and config.emulator_id in output, output))

    package_name = "host.exp.exponent" if config.app_start_mode == "expo_go" else config.app_id
    package_ok = maestro.is_package_installed(package_name)
    checks.append(
        CheckResult(
            "installed package",
            package_ok,
            f"Expected package `{package_name}` for startup mode `{config.app_start_mode}`.",
        )
    )

    checks.append(
        CheckResult(
            "metro port",
            _is_port_open(config.metro_port),
            f"Port {config.metro_port} listening={_is_port_open(config.metro_port)}",
        )
    )

    exit_code = 0 if all(item.ok for item in checks) else 1
    return exit_code, checks


def main() -> int:
    exit_code, checks = run_preflight()
    print("Night Shift QA Preflight")
    for item in checks:
        status = "OK" if item.ok else "FAIL"
        print(f"[{status}] {item.name}: {item.details}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
