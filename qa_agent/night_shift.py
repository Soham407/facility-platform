from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from .artifacts import ArtifactStore
from .config import NightShiftConfig
from .git_recovery import GitRecovery
from .llm_clients import AuditorClient, FixerClient, NavigatorClient
from .maestro_client import MaestroClient
from .models import FailureContext, RunStep
from .prd_loader import PrdLibrary
from .screen_classifier import ScreenClassifier
from .supabase_reset import SupabaseResetClient


@dataclass
class RunState:
    stalled_steps: int = 0
    last_screen_fingerprint: str = ""
    steps: list[RunStep] = field(default_factory=list)
    findings_total: int = 0
    failures_total: int = 0
    last_failure_summary: str = ""
    last_fix_branch: str = ""
    last_fix_commit: str = ""

    def to_dict(self) -> dict:
        return {
            "stalled_steps": self.stalled_steps,
            "last_screen_fingerprint": self.last_screen_fingerprint,
            "steps": [step.to_dict() for step in self.steps],
            "findings_total": self.findings_total,
            "failures_total": self.failures_total,
            "last_failure_summary": self.last_failure_summary,
            "last_fix_branch": self.last_fix_branch,
            "last_fix_commit": self.last_fix_commit,
        }


class NightShiftRunner:
    def __init__(self, config: NightShiftConfig) -> None:
        self.config = config
        self.run_started_at = time.time()
        self.artifacts = ArtifactStore(config.artifacts_root)
        self.prd = PrdLibrary(config.prd_path, config.prd_chunks_root)
        classifier = ScreenClassifier()
        self.maestro = MaestroClient(config, classifier)
        self.navigator = NavigatorClient(config.gemini, config.allow_navigator)
        self.auditor = AuditorClient(config.claude, config.allow_auditor)
        self.fixer = FixerClient(config.codex, config.allow_fixer, config.repo_root)
        self.git = GitRecovery(config.repo_root, run_started_at=self.run_started_at)
        self.supabase = SupabaseResetClient(config)
        self.state = RunState()

    def run(self) -> int:
        print(f"[qa_agent] artifacts: {self.artifacts.run_root}")
        self.artifacts.append_event("run_started", {"config": self._safe_config_snapshot()})

        for event in self.supabase.reset_if_enabled():
            self.artifacts.append_event("supabase_reset", event)

        self.maestro.prepare_runtime()

        for step_index in range(1, self.config.loop_limit + 1):
            try:
                exit_code = self._run_step(step_index)
                if exit_code != 0:
                    return exit_code
            except Exception as exc:
                self.state.failures_total += 1
                self.state.last_failure_summary = str(exc)
                print(f"[qa_agent] failure before step {step_index}: {exc}")
                failure = FailureContext(
                    failure_type="runner_exception",
                    summary=str(exc),
                    log_excerpt=self.maestro.get_logcat_excerpt(self.config.logcat_lines),
                )
                self.artifacts.append_event("failure", failure)
                self._attempt_fix_capture(failure)
                self._write_run_state()
                self._write_summary()
                return 1

        self._write_run_state()
        self._write_summary()
        self.artifacts.append_event("run_completed", self.state.to_dict())
        print("[qa_agent] run completed")
        return 0

    def _run_step(self, step_index: int) -> int:
        screen = self.maestro.capture_screen()
        fingerprint = self._fingerprint(screen.visible_texts, screen.resource_ids)
        if fingerprint == self.state.last_screen_fingerprint:
            self.state.stalled_steps += 1
        else:
            self.state.stalled_steps = 0
        self.state.last_screen_fingerprint = fingerprint

        self.artifacts.write_text(f"screens/step-{step_index:03d}-hierarchy.xml", screen.ui_hierarchy)
        self.artifacts.write_json(f"screens/step-{step_index:03d}-screen.json", screen)

        prd_chunk = self.prd.get_for_screen(screen.screen_id)
        audit = self.auditor.audit(screen, prd_chunk)
        self.state.findings_total += len(audit.findings)
        self.artifacts.write_json(f"audits/step-{step_index:03d}-audit.json", audit)
        self.artifacts.append_event("audit", {"step": step_index, "audit": audit, "screen_id": screen.screen_id})

        if self.state.stalled_steps >= self.config.idle_stall_limit:
            failure = FailureContext(
                failure_type="stall",
                summary=f"UI stalled for {self.state.stalled_steps} consecutive steps.",
                screen=screen,
                log_excerpt=self.maestro.get_logcat_excerpt(self.config.logcat_lines),
            )
            self.state.failures_total += 1
            self.state.last_failure_summary = failure.summary
            self.artifacts.append_event("failure", failure)
            self._attempt_fix_capture(failure)
            return 1

        action = self.navigator.choose_next_action(screen)
        self.artifacts.write_json(f"actions/step-{step_index:03d}-action.json", action)

        run_step = RunStep(
            index=step_index,
            screen_id=screen.screen_id,
            screen_label=screen.screen_label,
            audit_status=audit.status,
            action_type=action.action_type,
            action_target=action.target,
            notes=action.reason,
        )
        self.state.steps.append(run_step)
        self.artifacts.append_event("step", run_step)

        result = self._execute(action)
        if result.returncode != 0:
            failure = FailureContext(
                failure_type="action_failure",
                summary=result.stderr.strip() or f"Action failed: {action.action_type} {action.target}",
                screen=screen,
                log_excerpt=self.maestro.get_logcat_excerpt(self.config.logcat_lines),
                attempted_action=action,
            )
            self.state.failures_total += 1
            self.state.last_failure_summary = failure.summary
            self.artifacts.append_event("failure", failure)
            self._attempt_fix_capture(failure)
            return 1

        self.maestro.wait_for_settle()
        self._write_run_state()
        return 0

    def _execute(self, action):
        if action.action_type == "tap":
            return self.maestro.tap(action.target)
        if action.action_type == "input":
            return self.maestro.input_text(action.target, action.text)
        if action.action_type == "scroll":
            return self.maestro.scroll_down()
        if action.action_type == "back":
            return self.maestro.back()
        if action.action_type == "wait":
            return self.maestro.wait_only()
        return self.maestro.back()

    def _attempt_fix_capture(self, failure: FailureContext) -> None:
        proposal = self.fixer.propose_fix(failure)
        if proposal is None:
            return
        self.artifacts.write_json("fixes/latest-proposal.json", proposal)
        self.artifacts.append_event("fix_proposal", proposal)
        try:
            git_result = self.git.capture_fix_branch(proposal)
            self.state.last_fix_branch = git_result.get("fix_branch", "")
            self.state.last_fix_commit = git_result.get("commit_sha", "")
            self.artifacts.append_event("git_fix_branch", git_result)
        except Exception as exc:
            self.artifacts.append_event("git_fix_branch_error", {"message": str(exc)})

    def _write_run_state(self) -> None:
        self.artifacts.write_json("run_state.json", self.state.to_dict())

    def _write_summary(self) -> None:
        lines = [
            "# Night Shift QA Run",
            "",
            f"- Steps completed: {len(self.state.steps)}",
            f"- Findings recorded: {self.state.findings_total}",
            f"- Failures recorded: {self.state.failures_total}",
            f"- Artifacts: `{self.artifacts.run_root}`",
        ]
        if self.state.last_failure_summary:
            lines.append(f"- Last failure: `{self.state.last_failure_summary}`")
        if self.state.last_fix_branch:
            lines.append(f"- Fix branch: `{self.state.last_fix_branch}`")
        if self.state.last_fix_commit:
            lines.append(f"- Fix commit: `{self.state.last_fix_commit}`")
        lines.extend(["", "## Recent Steps"])
        for step in self.state.steps[-10:]:
            lines.append(
                f"- Step {step.index}: `{step.screen_label}` audit=`{step.audit_status}` action=`{step.action_type}:{step.action_target}`"
            )
        self.artifacts.write_summary(lines)

    def _fingerprint(self, visible_texts: list[str], resource_ids: list[str]) -> str:
        payload = {"texts": visible_texts[:20], "ids": resource_ids[:20]}
        return json.dumps(payload, sort_keys=True)

    def _safe_config_snapshot(self) -> dict[str, str | int | float | bool]:
        return {
            "emulator_id": self.config.emulator_id,
            "app_id": self.config.app_id,
            "app_start_mode": self.config.app_start_mode,
            "mobile_start_command": self.config.mobile_start_command,
            "app_launch_command": self.config.app_launch_command,
            "loop_limit": self.config.loop_limit,
            "step_delay_seconds": self.config.step_delay_seconds,
            "idle_stall_limit": self.config.idle_stall_limit,
            "allow_navigator": self.config.allow_navigator,
            "allow_auditor": self.config.allow_auditor,
            "allow_fixer": self.config.allow_fixer,
            "reset_before_run": self.config.reset_before_run,
        }


def main() -> int:
    config = NightShiftConfig.load()
    runner = NightShiftRunner(config)
    return runner.run()


if __name__ == "__main__":
    raise SystemExit(main())
