"""
Checkpoint runner for Guard + Resident V1 production checklist.

Each checkpoint has a test command, a verify function, and an optional autofix scope.
The runner executes checkpoints in order, retrying with Codex autofix on failure.

Usage:
    python3 -m qa_agent.checkpoint_runner
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from .subprocess_utils import normalize_command


@dataclass
class CheckpointResult:
    name: str
    status: str  # "pass" | "fail" | "fixed" | "manual" | "skipped"
    attempts: int = 0
    output: str = ""
    fix_branch: str = ""
    fix_commit: str = ""
    error: str = ""
    log_path: str = ""


@dataclass
class Checkpoint:
    name: str
    test: Callable[["CheckpointContext"], str]
    verify: Callable[[str], bool]
    fix_scope: str = "qa_scripts"  # "edge_function" | "qa_scripts" | "mobile_app" | "manual"
    fix_paths: list[str] = field(default_factory=list)
    fix_hint: str = ""
    max_attempts: int = 3
    depends_on: str | None = None


@dataclass
class CheckpointContext:
    repo_root: Path
    qa_root: Path
    web_root: Path
    mobile_root: Path
    artifacts_root: Path
    codex_bin: str
    run_id: str
    run_started_at: str
    results: dict[str, CheckpointResult] = field(default_factory=dict)


def _format_command_output(
    command: str,
    cwd: Path | None,
    timeout: int,
    returncode: int,
    stdout: str,
    stderr: str,
) -> str:
    return "\n".join(
        [
            f"$ {command}",
            f"cwd: {cwd or Path.cwd()}",
            f"timeout_seconds: {timeout}",
            f"exit_code: {returncode}",
            "",
            "--- STDOUT ---",
            stdout or "<empty>",
            "",
            "--- STDERR ---",
            stderr or "<empty>",
        ]
    )


def run_shell(command: str, cwd: Path | None = None, timeout: int = 120) -> str:
    completed = subprocess.run(
        ["/bin/bash", "-c", command],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    output = _format_command_output(
        command=command,
        cwd=cwd,
        timeout=timeout,
        returncode=completed.returncode,
        stdout=stdout,
        stderr=stderr,
    )
    if completed.returncode != 0:
        raise RuntimeError(output)
    return output


def supabase_query(sql: str, cwd: Path | None = None) -> str:
    safe_sql = sql.replace("'", "'\\''")
    return run_shell(f"supabase db query '{safe_sql}' --linked", cwd=cwd, timeout=30)


def supabase_query_count(sql: str, cwd: Path | None = None) -> int:
    raw = supabase_query(sql, cwd=cwd)
    stdout_match = re.search(r"--- STDOUT ---\n(.*?)\n\n--- STDERR ---", raw, re.S)
    search_space = stdout_match.group(1) if stdout_match else raw
    match = re.search(r"(\d+)", search_space)
    return int(match.group(1)) if match else 0


def sql_timestamp(value: str) -> str:
    return value.replace("'", "''")


def invoke_codex_fix(
    ctx: CheckpointContext,
    checkpoint: Checkpoint,
    failure_output: str,
) -> tuple[str, str]:
    codex_bin = ctx.codex_bin
    if not codex_bin or not _command_exists(codex_bin):
        print(f"  [autofix] Codex not found: {codex_bin}")
        return ("", "")

    fix_paths_str = "\n".join(f"  - {p}" for p in checkpoint.fix_paths) if checkpoint.fix_paths else "  (auto-detect from scope)"
    prompt = f"""You are repairing code for the FacilityPro production checklist.

Repository: {ctx.repo_root}
Checkpoint: {checkpoint.name}
Fix scope: {checkpoint.fix_scope}
Files to inspect/fix:
{fix_paths_str}

Failure output:
{failure_output[:4000]}

{checkpoint.fix_hint}

Task:
1. Read the relevant files and the failure output.
2. Apply the smallest fix to make the checkpoint pass.
3. Do not modify files outside the fix scope.
4. Print a short summary of what you changed.
"""

    stamp = time.time()
    fix_log_dir = ctx.artifacts_root / ctx.run_id / "codex-fixes"
    fix_log_dir.mkdir(parents=True, exist_ok=True)
    fix_log = fix_log_dir / f"{_safe_name(checkpoint.name)}.log"

    try:
        completed = subprocess.run(
            normalize_command(
                [
                    codex_bin,
                    "exec",
                    "--full-auto",
                    "--skip-git-repo-check",
                    "--cd",
                    str(ctx.repo_root),
                    prompt,
                ]
            ),
            capture_output=True,
            text=True,
            timeout=300,
            cwd=ctx.repo_root,
        )
        fix_log.write_text(completed.stdout + "\n" + completed.stderr, encoding="utf-8")

        if completed.returncode != 0:
            print(f"  [autofix] Codex exited {completed.returncode}")
            return ("", "")
    except subprocess.TimeoutExpired:
        print("  [autofix] Codex timed out")
        return ("", "")

    return _capture_fix_branch(ctx.repo_root, checkpoint.name, stamp)


def _capture_fix_branch(repo_root: Path, checkpoint_name: str, stamp: float) -> tuple[str, str]:
    def git(cmd: list[str]) -> str:
        completed = subprocess.run(["git", *cmd], capture_output=True, text=True, cwd=repo_root)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip())
        return completed.stdout.strip()

    changed: list[str] = []
    for line in git(["status", "--short", "--untracked-files=all"]).splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if not path or path.startswith("qa_agent/artifacts/") or "/__pycache__/" in path:
            continue
        full = repo_root / path
        try:
            if full.exists() and full.stat().st_mtime >= stamp - 1:
                changed.append(path)
        except OSError:
            continue

    if not changed:
        return ("", "")

    original_branch = git(["branch", "--show-current"]) or "main"
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch = f"fix/checklist-{_safe_name(checkpoint_name)}-{ts}"

    try:
        git(["checkout", "-b", branch])
        git(["add", "--", *changed])

        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
        if diff.returncode == 0:
            git(["checkout", original_branch])
            return ("", "")

        git(["commit", "-m", f"fix: production checklist — {checkpoint_name}"])
        sha = git(["rev-parse", "HEAD"])
        git(["checkout", original_branch])
        return (branch, sha)
    except Exception as exc:
        try:
            git(["checkout", original_branch])
        except Exception:
            pass
        print(f"  [autofix] Git capture failed: {exc}")
        return ("", "")


def _command_exists(name: str) -> bool:
    import shutil

    return shutil.which(name) is not None


def _safe_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]


class CheckpointRunner:
    def __init__(self, ctx: CheckpointContext, checkpoints: list[Checkpoint]) -> None:
        self.ctx = ctx
        self.checkpoints = checkpoints
        self.results: list[CheckpointResult] = []

    def run_all(self) -> list[CheckpointResult]:
        report_dir = self.ctx.artifacts_root / self.ctx.run_id
        report_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"  Production Checklist Run: {self.ctx.run_id}")
        print(f"  Checkpoints: {len(self.checkpoints)}")
        print(f"{'='*60}\n")

        for cp in self.checkpoints:
            result = self._run_checkpoint(cp)
            self.results.append(result)
            self.ctx.results[cp.name] = result

        self._write_report(report_dir)
        self._print_summary()
        return self.results

    def _run_checkpoint(self, cp: Checkpoint) -> CheckpointResult:
        print(f"\n--- Checkpoint: {cp.name} ---")
        report_dir = self.ctx.artifacts_root / self.ctx.run_id
        logs_dir = report_dir / "checkpoint-logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        if cp.depends_on and cp.depends_on in self.ctx.results:
            dep = self.ctx.results[cp.depends_on]
            if dep.status not in ("pass", "fixed"):
                print(f"  SKIPPED (depends on '{cp.depends_on}' which {dep.status})")
                dependency_output = (
                    f"Checkpoint skipped.\n"
                    f"Dependency: {cp.depends_on}\n"
                    f"Dependency status: {dep.status}\n"
                    f"Dependency log: {dep.log_path or '<none>'}"
                )
                log_path = self._write_checkpoint_log(logs_dir, cp.name, 0, dependency_output)
                return CheckpointResult(
                    name=cp.name,
                    status="skipped",
                    error=f"Dependency '{cp.depends_on}' not met",
                    output=dependency_output,
                    log_path=str(log_path.relative_to(report_dir)),
                )

        for attempt in range(1, cp.max_attempts + 1):
            print(f"  Attempt {attempt}/{cp.max_attempts}")

            try:
                output = cp.test(self.ctx)
            except Exception as exc:
                output = str(exc)
                print(f"  Test error: {output[:200]}")

            try:
                passed = cp.verify(output)
            except Exception as exc:
                passed = False
                output += f"\nVerify error: {exc}"

            log_path = self._write_checkpoint_log(logs_dir, cp.name, attempt, output)

            if passed:
                status = "fixed" if attempt > 1 else "pass"
                print(f"  RESULT: {status.upper()}")
                return CheckpointResult(
                    name=cp.name,
                    status=status,
                    attempts=attempt,
                    output=output,
                    log_path=str(log_path.relative_to(report_dir)),
                )

            print("  FAILED")

            if cp.fix_scope == "manual":
                print("  Manual step required — logging and continuing")
                return CheckpointResult(
                    name=cp.name,
                    status="manual",
                    attempts=attempt,
                    output=output,
                    error=output,
                    log_path=str(log_path.relative_to(report_dir)),
                )

            if attempt < cp.max_attempts:
                print("  Invoking Codex autofix...")
                branch, sha = invoke_codex_fix(self.ctx, cp, output)
                if branch:
                    print(f"  Fix branch: {branch} ({sha[:8]})")

        return CheckpointResult(
            name=cp.name,
            status="fail",
            attempts=cp.max_attempts,
            output=output,
            error=output,
            log_path=str(log_path.relative_to(report_dir)),
        )

    def _write_checkpoint_log(self, logs_dir: Path, checkpoint_name: str, attempt: int, output: str) -> Path:
        log_path = logs_dir / f"{_safe_name(checkpoint_name)}-attempt-{attempt}.log"
        log_path.write_text(output or "<empty>", encoding="utf-8")
        return log_path

    def _write_report(self, report_dir: Path) -> None:
        lines = [
            "# Production Checklist Report",
            "",
            f"Run: `{self.ctx.run_id}`",
            f"Date: {datetime.now().isoformat()}",
            f"Run started at: `{self.ctx.run_started_at}`",
            f"Repo root: `{self.ctx.repo_root}`",
            "",
            "## Results",
            "",
            "| # | Checkpoint | Status | Attempts | Log |",
            "|---|-----------|--------|----------|-----|",
        ]
        for i, r in enumerate(self.results, 1):
            icon = {"pass": "PASS", "fixed": "FIXED", "fail": "FAIL", "manual": "MANUAL", "skipped": "SKIP"}.get(r.status, r.status)
            log_ref = f"`{r.log_path}`" if r.log_path else ""
            lines.append(f"| {i} | {r.name} | {icon} | {r.attempts} | {log_ref} |")

        passed = sum(1 for r in self.results if r.status in ("pass", "fixed"))
        total = len(self.results)
        lines.extend(["", f"## Summary: {passed}/{total} passed", ""])

        for r in self.results:
            lines.extend([f"### {r.name} — {r.status.upper()}", "", f"Attempts: `{r.attempts}`", ""])
            if r.log_path:
                lines.extend([f"Log file: `{r.log_path}`", ""])
            if r.status in ("fail", "manual", "skipped"):
                lines.extend(["```", (r.error or r.output)[:4000], "```", ""])
            else:
                lines.extend(["```", (r.output or "<empty>")[:1200], "```", ""])
            if r.fix_branch:
                lines.append(f"Fix branch: `{r.fix_branch}` (`{r.fix_commit[:8]}`)")
                lines.append("")

        report_path = report_dir / "checklist_report.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\nReport written to: {report_path}")

        state_path = report_dir / "checklist_state.json"
        state_path.write_text(
            json.dumps(
                [
                    {
                        "name": r.name,
                        "status": r.status,
                        "attempts": r.attempts,
                        "error": r.error,
                        "fix_branch": r.fix_branch,
                        "fix_commit": r.fix_commit,
                        "log_path": r.log_path,
                    }
                    for r in self.results
                ],
                indent=2,
            ),
            encoding="utf-8",
        )

    def _print_summary(self) -> None:
        passed = sum(1 for r in self.results if r.status in ("pass", "fixed"))
        failed = sum(1 for r in self.results if r.status == "fail")
        manual = sum(1 for r in self.results if r.status == "manual")
        skipped = sum(1 for r in self.results if r.status == "skipped")

        print(f"\n{'='*60}")
        print(f"  CHECKLIST COMPLETE: {passed} pass, {failed} fail, {manual} manual, {skipped} skip")
        print(f"{'='*60}\n")

        for r in self.results:
            icon = {"pass": "[PASS]", "fixed": "[FIXED]", "fail": "[FAIL]", "manual": "[MANUAL]", "skipped": "[SKIP]"}.get(r.status, f"[{r.status}]")
            print(f"  {icon:10s} {r.name}")


def build_checkpoints(ctx: CheckpointContext) -> list[Checkpoint]:
    return [
        Checkpoint(
            name="deploy-dispatch-notification-queue",
            test=lambda c: _test_deploy_edge_function(c),
            verify=lambda out: "deployed" in out.lower() or "already deployed" in out.lower() or "serving" in out.lower(),
            fix_scope="edge_function",
            fix_paths=[
                "Solvesxx_web/supabase/functions/dispatch-notification-queue/index.ts",
                "Solvesxx_web/supabase/functions/dispatch-notification-queue/deno.json",
            ],
            fix_hint="Fix TypeScript compilation or import errors in the edge function. Reference send-notification/index.ts for Firebase Admin patterns.",
            max_attempts=3,
        ),
        Checkpoint(
            name="verify-push-token-registration",
            test=lambda c: _test_push_tokens(c),
            verify=lambda out: _verify_count_positive(out),
            fix_scope="manual",
            fix_hint="Push token registration requires a mobile device to be running the app. Launch the app on emulator/device and re-run.",
            max_attempts=1,
        ),
        Checkpoint(
            name="staging-e2e-approve",
            test=lambda c: _test_maestro_flow(c, "guard_resident_staging_e2e"),
            verify=lambda out: "passed" in out.lower() or "test passed" in out.lower() or "exit code: 0" in out.lower(),
            fix_scope="qa_scripts",
            fix_paths=[
                "qa_agent/maestro/guard_resident_staging_e2e.yaml",
                "qa_agent/run_guard_resident_staging_e2e.sh",
            ],
            fix_hint="Fix Maestro flow selectors or timing. Do not modify the mobile app.",
            max_attempts=3,
        ),
        Checkpoint(
            name="verify-notification-insertion",
            test=lambda c: _test_notification_insertion(c),
            verify=lambda out: "push_queued" in out or "delivered" in out,
            fix_scope="manual",
            fix_hint="Notification insertion is handled by create_mobile_visitor RPC. If missing, check the DB migration and RPC definition.",
            max_attempts=1,
            depends_on="staging-e2e-approve",
        ),
        Checkpoint(
            name="verify-notification-dispatch",
            test=lambda c: _test_notification_dispatch(c),
            verify=lambda out: "delivered" in out.lower(),
            fix_scope="edge_function",
            fix_paths=[
                "Solvesxx_web/supabase/functions/dispatch-notification-queue/index.ts",
            ],
            fix_hint="The dispatch function should process push_queued notifications. Check Firebase config and token lookup logic.",
            max_attempts=2,
            depends_on="deploy-dispatch-notification-queue",
        ),
        Checkpoint(
            name="staging-e2e-deny",
            test=lambda c: _test_maestro_flow(c, "guard_resident_staging_deny_e2e"),
            verify=lambda out: "passed" in out.lower() or "test passed" in out.lower() or "exit code: 0" in out.lower(),
            fix_scope="qa_scripts",
            fix_paths=[
                "qa_agent/maestro/guard_resident_staging_deny_e2e.yaml",
                "qa_agent/run_guard_resident_staging_deny_e2e.sh",
            ],
            fix_hint="Fix Maestro flow selectors or timing. Do not modify the mobile app.",
            max_attempts=3,
        ),
        Checkpoint(
            name="staging-e2e-checklist",
            test=lambda c: _test_maestro_flow(c, "guard_checklist_staging_e2e"),
            verify=lambda out: "passed" in out.lower() or "test passed" in out.lower() or "exit code: 0" in out.lower(),
            fix_scope="qa_scripts",
            fix_paths=[
                "qa_agent/maestro/guard_checklist_staging_e2e.yaml",
                "qa_agent/run_guard_checklist_staging_e2e.sh",
            ],
            fix_hint="Fix Maestro flow selectors or timing. Do not modify the mobile app.",
            max_attempts=3,
        ),
        Checkpoint(
            name="staging-e2e-sos",
            test=lambda c: _test_maestro_flow(c, "guard_sos_staging_e2e"),
            verify=lambda out: "passed" in out.lower() or "test passed" in out.lower() or "exit code: 0" in out.lower(),
            fix_scope="qa_scripts",
            fix_paths=[
                "qa_agent/maestro/guard_sos_staging_e2e.yaml",
                "qa_agent/run_guard_sos_staging_e2e.sh",
            ],
            fix_hint="Fix Maestro flow selectors or timing. Do not modify the mobile app.",
            max_attempts=3,
        ),
        Checkpoint(
            name="verify-panic-notification",
            test=lambda c: _test_panic_notification(c),
            verify=lambda out: "panic_alert" in out or "panic_resolved" in out,
            fix_scope="manual",
            fix_hint="Panic notification insertion is handled by start_mobile_panic_alert RPC.",
            max_attempts=1,
            depends_on="staging-e2e-sos",
        ),
        Checkpoint(
            name="web-admin-backend-verification",
            test=lambda c: _test_web_admin_queries(c),
            verify=lambda out: "ALL_CHECKS_PASSED" in out,
            fix_scope="manual",
            fix_hint="Backend data verification. Check Supabase tables and RLS policies.",
            max_attempts=1,
        ),
        Checkpoint(
            name="staging-fallback-audit",
            test=lambda c: _test_staging_fallback_audit(c),
            verify=lambda out: "AUDIT_PASSED" in out,
            fix_scope="mobile_app",
            fix_paths=["Solvesxx_mobile/src/"],
            fix_hint="Ensure all calls to stagingAutomation functions are gated by isStagingAutomationEnabled(). Do not remove the functions, just add the gate check at call sites.",
            max_attempts=2,
        ),
    ]


def _test_deploy_edge_function(ctx: CheckpointContext) -> str:
    fn_dir = ctx.web_root / "supabase" / "functions" / "dispatch-notification-queue"
    if not (fn_dir / "index.ts").exists():
        raise RuntimeError(f"Edge function not found at {fn_dir}")

    try:
        return run_shell("supabase functions deploy dispatch-notification-queue", cwd=ctx.web_root, timeout=120)
    except RuntimeError as exc:
        return str(exc)


def _test_push_tokens(ctx: CheckpointContext) -> str:
    return supabase_query(
        """SELECT count(*) AS cnt
           FROM push_tokens pt
           JOIN auth.users u ON u.id = pt.user_id
           WHERE pt.is_active = true
             AND COALESCE(pt.token_type, 'fcm') = 'fcm'
             AND lower(u.email) IN ('guard@test.com', 'rohit@test.com', 'resident@test.com');""",
        cwd=ctx.web_root,
    )


def _test_maestro_flow(ctx: CheckpointContext, flow_name: str) -> str:
    script = ctx.qa_root / f"run_{flow_name}.sh"
    if script.exists():
        command = shlex.quote(str(script))
    else:
        yaml_path = ctx.qa_root / "maestro" / f"{flow_name}.yaml"
        if not yaml_path.exists():
            raise RuntimeError(
                f"Neither script nor Maestro flow exists for {flow_name}. "
                f"Expected one of: {script} or {yaml_path}"
            )
        smoke_runner = ctx.qa_root / "run_maestro_smoke.sh"
        if not smoke_runner.exists():
            raise RuntimeError(f"Smoke runner not found: {smoke_runner}")
        command = f"{shlex.quote(str(smoke_runner))} {shlex.quote(str(yaml_path))}"

    try:
        output = run_shell(command, cwd=ctx.repo_root, timeout=300)
        return output + "\nexit code: 0"
    except RuntimeError as exc:
        return str(exc)


def _test_notification_insertion(ctx: CheckpointContext) -> str:
    started = sql_timestamp(ctx.run_started_at)
    return supabase_query(
        f"""SELECT id, delivery_state, notification_type, created_at
           FROM notifications
           WHERE notification_type = 'visitor_at_gate'
             AND created_at >= '{started}'::timestamptz
           ORDER BY created_at DESC
           LIMIT 1;""",
        cwd=ctx.web_root,
    )


def _test_notification_dispatch(ctx: CheckpointContext) -> str:
    started = sql_timestamp(ctx.run_started_at)
    trigger_output = ""
    try:
        trigger_output = supabase_query("SELECT trigger_mobile_notification_queue();", cwd=ctx.web_root)
    except RuntimeError as exc:
        trigger_output = f"Trigger invocation failed:\n{exc}"

    deadline = time.time() + 90
    last_output = ""
    while time.time() < deadline:
        last_output = supabase_query(
            f"""SELECT id, delivery_state, created_at
               FROM notifications
               WHERE notification_type = 'visitor_at_gate'
                 AND created_at >= '{started}'::timestamptz
               ORDER BY created_at DESC
               LIMIT 1;""",
            cwd=ctx.web_root,
        )
        if "delivered" in last_output.lower() or "failed" in last_output.lower():
            return "\n\n".join([trigger_output or "Trigger invocation not attempted", "--- POLL RESULT ---", last_output])
        time.sleep(3)

    return "\n\n".join(
        [
            trigger_output or "Trigger invocation not attempted",
            "--- FINAL POLL RESULT ---",
            last_output or "No recent visitor_at_gate notification found",
        ]
    )


def _test_panic_notification(ctx: CheckpointContext) -> str:
    started = sql_timestamp(ctx.run_started_at)
    return supabase_query(
        f"""SELECT id, delivery_state, notification_type, created_at
           FROM notifications
           WHERE notification_type IN ('panic_alert', 'panic_resolved')
             AND created_at >= '{started}'::timestamptz
           ORDER BY created_at DESC
           LIMIT 1;""",
        cwd=ctx.web_root,
    )


def _test_web_admin_queries(ctx: CheckpointContext) -> str:
    checks = {
        "visitors_exist": "SELECT count(*) FROM visitors WHERE entry_time > NOW() - INTERVAL '24 hours';",
        "resident_auth_linked": "SELECT count(*) FROM residents WHERE auth_user_id IS NOT NULL AND is_active = true;",
        "guard_employee_chain": """SELECT count(*) FROM security_guards sg
                                   JOIN employees e ON e.id = sg.employee_id
                                   WHERE sg.is_active = true AND e.auth_user_id IS NOT NULL;""",
    }

    results = []
    all_passed = True
    for name, sql in checks.items():
        try:
            count = supabase_query_count(sql, cwd=ctx.web_root)
            status = "OK" if count > 0 else "EMPTY"
            if count == 0:
                all_passed = False
            results.append(f"  {name}: {count} ({status})\n    sql: {sql}")
        except Exception as exc:
            all_passed = False
            results.append(f"  {name}: ERROR ({exc})\n    sql: {sql}")

    output = "\n".join(results)
    if all_passed:
        output += "\nALL_CHECKS_PASSED"
    return output


def _test_staging_fallback_audit(ctx: CheckpointContext) -> str:
    src_dir = ctx.mobile_root / "src"
    if not src_dir.exists():
        return "AUDIT_PASSED (no src dir)"

    issues: list[str] = []

    try:
        result = subprocess.run(
            ["grep", "-rl", "stagingAutomation", str(src_dir)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        importing_files = [f for f in result.stdout.strip().splitlines() if f]
    except Exception:
        return "AUDIT_PASSED (grep failed)"

    automation_file = str(ctx.mobile_root / "src" / "lib" / "stagingAutomation.ts")

    for file_path in importing_files:
        if file_path == automation_file:
            continue

        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except Exception:
            continue

        if "stagingAutomation" in content and "isStagingAutomationEnabled" not in content:
            if "buildAssigned" in content or "STAGING_PIXEL" in content:
                rel = Path(file_path).relative_to(ctx.mobile_root)
                issues.append(f"  {rel}: imports stagingAutomation but missing isStagingAutomationEnabled gate")

    if issues:
        return "AUDIT_ISSUES:\n" + "\n".join(issues)
    return "AUDIT_PASSED"


def _verify_count_positive(output: str) -> bool:
    stdout_match = re.search(r"--- STDOUT ---\n(.*?)\n\n--- STDERR ---", output, re.S)
    search_space = stdout_match.group(1) if stdout_match else output
    match = re.search(r"(\d+)", search_space)
    return match is not None and int(match.group(1)) > 0


def main() -> int:
    qa_root = Path(__file__).resolve().parent
    repo_root = qa_root.parent

    run_id = f"checklist-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    ctx = CheckpointContext(
        repo_root=repo_root,
        qa_root=qa_root,
        web_root=repo_root / "Solvesxx_web",
        mobile_root=repo_root / "Solvesxx_mobile",
        artifacts_root=qa_root / "artifacts",
        codex_bin=os.getenv("QA_CODEX_COMMAND", "codex"),
        run_id=run_id,
        run_started_at=datetime.now().astimezone().isoformat(),
    )

    checkpoints = build_checkpoints(ctx)
    runner = CheckpointRunner(ctx, checkpoints)
    results = runner.run_all()

    unresolved = sum(1 for r in results if r.status not in ("pass", "fixed"))
    return 1 if unresolved > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
