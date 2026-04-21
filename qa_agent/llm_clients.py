from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from .config import CliConfig
from .maestro_client import fallback_action_for_screen
from .models import ActionDecision, AuditFinding, AuditResult, FailureContext, FixProposal, ScreenSnapshot
from .prd_loader import PrdChunk
from .subprocess_utils import normalize_command


def _run_cli(command: str, prompt: str, timeout_seconds: int, cwd: Path | None = None) -> str:
    argv = CliConfig(command=command).argv
    if not argv:
        raise RuntimeError("LLM command is empty.")
    argv = normalize_command(argv)
    completed = subprocess.run(
        [*argv, prompt],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        cwd=cwd,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"{command} returned {completed.returncode}")
    return completed.stdout.strip()


class NavigatorClient:
    def __init__(self, cli: CliConfig, enabled: bool) -> None:
        self.cli = cli
        self.enabled = enabled

    def choose_next_action(self, screen: ScreenSnapshot) -> ActionDecision:
        if not self.enabled:
            return fallback_action_for_screen(screen)

        prompt = f"""
You are Gemini, the Navigator for an autonomous mobile QA system.
Choose exactly one next action for the current screen.

Return strict JSON with keys:
- action_type: tap|back|wait|input|scroll
- target: exact visible text, exact resource-id, or BACK (omit for scroll/wait)
- text: (required only for input) the string to type into the focused field
- reason: one short sentence

Rules:
- Prefer deterministic progress over random exploration.
- Use "input" to type into text fields (phone number, OTP, search). Include "text" with the value to type.
- Use "scroll" when the screen has a list or more content below the fold.
- Do not choose destructive actions unless the UI clearly requires them.
- Do not invent text that is not visible (except for "text" in input actions).

Visible texts:
{json.dumps(screen.visible_texts[:40], ensure_ascii=True)}

Resource IDs:
{json.dumps(screen.resource_ids[:40], ensure_ascii=True)}
"""
        try:
            raw = _run_cli(self.cli.command, prompt, self.cli.timeout_seconds)
            payload = _extract_json(raw)
            return ActionDecision(
                action_type=str(payload.get("action_type", "wait")).strip().lower(),
                target=str(payload.get("target", "BACK")).strip(),
                text=str(payload.get("text", "")).strip(),
                reason=str(payload.get("reason", "")).strip(),
                metadata={"raw_response": raw},
            )
        except Exception as exc:
            decision = fallback_action_for_screen(screen)
            decision.metadata["navigator_error"] = str(exc)
            return decision


class AuditorClient:
    def __init__(self, cli: CliConfig, enabled: bool) -> None:
        self.cli = cli
        self.enabled = enabled

    def audit(self, screen: ScreenSnapshot, prd_chunk: PrdChunk) -> AuditResult:
        if not self.enabled:
            return AuditResult(status="skipped", summary="Auditor disabled.")

        prompt = f"""
You are Claude Code, the Auditor in an overnight mobile QA system.
Compare the observed screen against the PRD.

Return strict JSON with keys:
- status: pass|warning|fail
- summary: short summary
- findings: array of objects with severity, title, details, expected, observed

Observed screen label: {screen.screen_label}
Observed screen id: {screen.screen_id}
Visible texts: {json.dumps(screen.visible_texts[:60], ensure_ascii=True)}
Resource IDs: {json.dumps(screen.resource_ids[:60], ensure_ascii=True)}

Relevant PRD chunk:
{prd_chunk.content[:6000]}
"""
        try:
            raw = _run_cli(self.cli.command, prompt, self.cli.timeout_seconds)
            payload = _extract_json(raw)
            findings = [
                AuditFinding(
                    severity=str(item.get("severity", "info")),
                    title=str(item.get("title", "Untitled finding")),
                    details=str(item.get("details", "")),
                    expected=str(item.get("expected", "")),
                    observed=str(item.get("observed", "")),
                )
                for item in payload.get("findings", [])
            ]
            return AuditResult(
                status=str(payload.get("status", "warning")),
                summary=str(payload.get("summary", "No summary provided.")),
                findings=findings,
                raw_response=raw,
            )
        except Exception as exc:
            return AuditResult(
                status="warning",
                summary=f"Auditor unavailable: {exc}",
                findings=[],
            )


class FixerClient:
    def __init__(self, cli: CliConfig, enabled: bool, repo_root: Path) -> None:
        self.cli = cli
        self.enabled = enabled
        self.repo_root = repo_root

    def propose_fix(self, failure: FailureContext) -> FixProposal | None:
        if not self.enabled:
            return None

        prompt = f"""
You are Codex, the Fixer in an overnight mobile QA system.
Inspect the repository, apply the smallest code changes needed to address the failure, and then return strict JSON.

Return strict JSON with keys:
- title
- branch_name
- commit_message

Failure context:
{json.dumps(failure.to_dict(), ensure_ascii=True)[:7000]}
"""
        try:
            raw = self._run_fixer(prompt)
            payload = _extract_json(raw)
            return FixProposal(
                title=str(payload.get("title", "night-shift fix")).strip(),
                branch_name=_sanitize_git_ref(str(payload.get("branch_name", "fix/night-shift-issue")).strip()),
                commit_message=str(payload.get("commit_message", "fix: night shift issue")).strip(),
                raw_response=raw,
            )
        except Exception:
            return None

    def _run_fixer(self, prompt: str) -> str:
        argv = CliConfig(command=self.cli.command).argv
        if not argv:
            raise RuntimeError("Fixer command is empty.")

        executable = Path(argv[0]).name.lower()
        if executable == "codex" and (len(argv) == 1 or argv[1] != "exec"):
            return self._run_codex_exec(argv[0], prompt)
        return _run_cli(self.cli.command, prompt, self.cli.timeout_seconds, cwd=self.repo_root)

    def _run_codex_exec(self, executable: str, prompt: str) -> str:
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "branch_name": {"type": "string"},
                "commit_message": {"type": "string"},
            },
            "required": ["title", "branch_name", "commit_message"],
            "additionalProperties": False,
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as schema_file:
            json.dump(schema, schema_file)
            schema_path = schema_file.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as output_file:
            output_path = output_file.name

        command = [
            executable,
            "exec",
            "--full-auto",
            "--skip-git-repo-check",
            "--cd",
            str(self.repo_root),
            "--output-schema",
            schema_path,
            "--output-last-message",
            output_path,
            prompt,
        ]
        try:
            completed = subprocess.run(
                normalize_command(command),
                capture_output=True,
                text=True,
                timeout=max(self.cli.timeout_seconds, 300),
                cwd=self.repo_root,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or f"{executable} returned {completed.returncode}")
            return Path(output_path).read_text(encoding="utf-8").strip()
        finally:
            Path(schema_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in LLM response.")
    return json.loads(raw[start : end + 1])


def _sanitize_git_ref(value: str) -> str:
    value = value.lower().replace(" ", "-")
    value = re.sub(r"[^a-z0-9/_-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if not value:
        return "fix/night-shift-issue"
    if "/" not in value:
        return f"fix/{value}"
    return value
