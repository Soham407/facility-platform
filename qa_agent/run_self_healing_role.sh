#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ROLE="${QA_LOGIN_ROLE:-${1:-buyer}}"
MAX_ATTEMPTS="${QA_MAX_ATTEMPTS:-3}"
RETRY_DELAY_SECONDS="${QA_RETRY_DELAY_SECONDS:-6}"
KEYWORD_PATTERN='fail|failed|failure|exception|traceback|timed out|command failed'
RUN_LOG_ROOT="${QA_RUN_LOG_ROOT:-$REPO_ROOT/qa_agent/artifacts/self-heal-logs}"
AUTOFIX_ENABLED="${QA_WATCHDOG_AUTOFIX_ENABLED:-1}"
AUTOFIX_LOG_ROOT="${QA_WATCHDOG_FIX_LOG_ROOT:-$RUN_LOG_ROOT/codex-fixes}"
CODEX_BIN="${QA_WATCHDOG_CODEX_BIN:-codex}"
LAST_WATCHDOG_FIX_BRANCH=""
LAST_WATCHDOG_FIX_COMMIT=""

mkdir -p "$RUN_LOG_ROOT"
mkdir -p "$AUTOFIX_LOG_ROOT"

latest_run_dir() {
  ls -1dt "$REPO_ROOT"/qa_agent/artifacts/run-* 2>/dev/null | head -n 1
}

latest_run_dir_after() {
  local previous_latest="$1"
  local current_latest
  current_latest="$(latest_run_dir)"
  if [[ -z "${current_latest:-}" ]]; then
    return 1
  fi
  if [[ -z "${previous_latest:-}" || "$current_latest" != "$previous_latest" ]]; then
    printf '%s\n' "$current_latest"
    return 0
  fi
  return 1
}

run_failed() {
  local run_dir="$1"
  [[ -f "$run_dir/events.jsonl" ]] || return 1
  rg -q '"event_type": "failure"' "$run_dir/events.jsonl"
}

extract_fix_branch() {
  local run_dir="$1"
  [[ -f "$run_dir/events.jsonl" ]] || return 0
  rg -o '"fix_branch":\s*"[^"]+"' "$run_dir/events.jsonl" | tail -n 1 | sed -E 's/.*"fix_branch":\s*"([^"]+)"/\1/'
}

extract_fix_commit() {
  local run_dir="$1"
  [[ -f "$run_dir/events.jsonl" ]] || return 0
  rg -o '"commit_sha":\s*"[^"]*"' "$run_dir/events.jsonl" | tail -n 1 | sed -E 's/.*"commit_sha":\s*"([^"]*)"/\1/'
}

print_summary_excerpt() {
  local run_dir="$1"
  if [[ -f "$run_dir/summary.md" ]]; then
    echo "Summary:"
    sed -n '1,80p' "$run_dir/summary.md"
  fi
}

extract_failure_summary() {
  local run_dir="$1"
  [[ -f "$run_dir/events.jsonl" ]] || return 0
  python3 - "$run_dir/events.jsonl" <<'PY'
import json
import sys
path = sys.argv[1]
summary = ""
try:
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("event_type") == "failure":
                event_payload = payload.get("payload") or {}
                summary = event_payload.get("summary") or summary
except Exception:
    pass
print(summary)
PY
}

run_step_count() {
  local run_dir="$1"
  [[ -f "$run_dir/run_state.json" ]] || {
    echo "0"
    return 0
  }
  python3 - "$run_dir/run_state.json" <<'PY'
import json
import sys
path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    print(len(payload.get("steps", [])))
except Exception:
    print(0)
PY
}

print_failure_context() {
  local run_dir="$1"
  [[ -f "$run_dir/events.jsonl" ]] || return 0
  echo "Failure summary:"
  tail -n 40 "$run_dir/events.jsonl" | rg '"event_type": "failure"|"event_type": "git_fix_branch"|summary|fix_branch|commit_sha' || true
  print_summary_excerpt "$run_dir"
}

watchdog_capture_fix_branch() {
  local stamp_file="$1"
  local role="$2"
  local attempt="$3"

  python3 - "$REPO_ROOT" "$stamp_file" "$role" "$attempt" <<'PY'
import subprocess
import sys
from datetime import datetime
from pathlib import Path

repo_root = Path(sys.argv[1])
stamp_file = Path(sys.argv[2])
role = sys.argv[3]
attempt = sys.argv[4]

def run(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "command failed")
    return completed.stdout.strip()

paths = []
for path in (repo_root / "qa_agent").rglob("*"):
    if not path.is_file():
        continue
    try:
        if path.stat().st_mtime < stamp_file.stat().st_mtime:
            continue
    except FileNotFoundError:
        continue
    relative = path.relative_to(repo_root).as_posix()
    if relative.startswith("qa_agent/artifacts/") or "/__pycache__/" in relative or relative.endswith(".pyc"):
        continue
    paths.append(relative)

paths = sorted(set(paths))
if not paths:
    print("NO_CHANGES")
    raise SystemExit(0)

original_branch = run(["git", "branch", "--show-current"]) or "main"
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
branch_name = f"fix/watchdog-{role}-{attempt}-{timestamp}"
run(["git", "checkout", "-b", branch_name])
run(["git", "add", "--", *paths])

diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
if diff.returncode == 0:
    run(["git", "checkout", original_branch])
    print("NO_STAGED_DIFF")
    raise SystemExit(0)

commit_message = f"fix: watchdog self-heal {role} QA automation"
run(["git", "commit", "-m", commit_message])
commit_sha = run(["git", "rev-parse", "HEAD"])
run(["git", "checkout", original_branch])
print(f"BRANCH={branch_name}")
print(f"COMMIT={commit_sha}")
PY
}

invoke_script_autofix() {
  local role="$1"
  local attempt="$2"
  local run_dir="$3"
  local attempt_log="$4"

  LAST_WATCHDOG_FIX_BRANCH=""
  LAST_WATCHDOG_FIX_COMMIT=""

  if [[ "$AUTOFIX_ENABLED" != "1" ]]; then
    echo "Watchdog script autofix disabled."
    return 0
  fi

  if ! command -v "$CODEX_BIN" >/dev/null 2>&1; then
    echo "Codex CLI not found: $CODEX_BIN"
    return 0
  fi

  local stamp_file
  stamp_file="$(mktemp)"
  touch "$stamp_file"

  local run_dir_value="${run_dir:-none}"
  local failure_summary=""
  if [[ -n "${run_dir:-}" ]]; then
    failure_summary="$(extract_failure_summary "$run_dir")"
  fi
  local fix_log="$AUTOFIX_LOG_ROOT/${role}-attempt-${attempt}.log"
  local prompt
  prompt=$(cat <<EOF
You are repairing the QA automation code, not the mobile application UI.

Repository: $REPO_ROOT
Role under test: $role
Failed artifact directory: $run_dir_value
Attempt log: $attempt_log
Last failure summary: ${failure_summary:-unknown}

Task:
1. Inspect the latest QA artifact and the qa_agent automation code.
2. Fix only the QA automation scripts under qa_agent/ and qa_agent/*.sh.
3. Do not modify Solvesxx_mobile/ or Solvesxx_web/.
4. Apply the smallest deterministic fix so the same role can be retried immediately.
5. Prefer selector handling, retry logic, result detection, and watchdog logic changes over app changes.
6. At the end, print a short summary of what you changed.
EOF
)

  echo "Running Codex watchdog autofix for role $role..."
  set +e
  "$CODEX_BIN" exec --full-auto --skip-git-repo-check --cd "$REPO_ROOT" "$prompt" 2>&1 | tee "$fix_log"
  local codex_status=${pipestatus[1]}
  set -e
  rm -f "$stamp_file.tmp" 2>/dev/null || true

  if (( codex_status != 0 )); then
    echo "Codex watchdog autofix exited non-zero: $codex_status"
    rm -f "$stamp_file"
    return 0
  fi

  local branch_capture_output
  set +e
  branch_capture_output="$(watchdog_capture_fix_branch "$stamp_file" "$role" "$attempt" 2>&1)"
  local capture_status=$?
  set -e
  rm -f "$stamp_file"

  if (( capture_status != 0 )); then
    echo "Watchdog fix branch capture failed:"
    echo "$branch_capture_output"
    return 0
  fi

  if [[ "$branch_capture_output" == *"BRANCH="* ]]; then
    LAST_WATCHDOG_FIX_BRANCH="$(printf '%s\n' "$branch_capture_output" | sed -n 's/^BRANCH=//p' | tail -n 1)"
    LAST_WATCHDOG_FIX_COMMIT="$(printf '%s\n' "$branch_capture_output" | sed -n 's/^COMMIT=//p' | tail -n 1)"
    echo "Watchdog fix branch: $LAST_WATCHDOG_FIX_BRANCH"
    echo "Watchdog fix commit: $LAST_WATCHDOG_FIX_COMMIT"
  else
    echo "$branch_capture_output"
  fi
}

cd "$REPO_ROOT"

attempt=1
while (( attempt <= MAX_ATTEMPTS )); do
  echo "=== Role $ROLE | attempt $attempt/$MAX_ATTEMPTS ==="
  previous_latest="$(latest_run_dir || true)"
  attempt_log="$RUN_LOG_ROOT/${ROLE}-attempt-${attempt}.log"

  set +e
  QA_LOGIN_ROLE="$ROLE" ./qa_agent/run_overnight.sh 2>&1 | tee "$attempt_log"
  command_status=${pipestatus[1]}
  set -e
  run_dir="$(latest_run_dir_after "$previous_latest" || latest_run_dir || true)"
  saw_failure_keyword=0
  if [[ -f "$attempt_log" ]] && rg -Eiq "$KEYWORD_PATTERN" "$attempt_log"; then
    saw_failure_keyword=1
  fi
  step_count=0
  if [[ -n "${run_dir:-}" ]]; then
    step_count="$(run_step_count "$run_dir")"
  fi

  if (( command_status == 0 )) && [[ -n "${run_dir:-}" ]] && ! run_failed "$run_dir" && (( saw_failure_keyword == 0 )) && (( step_count > 0 )); then
    echo "Role $ROLE completed without recorded failure."
    print_summary_excerpt "$run_dir"
    exit 0
  fi

  if [[ -n "${run_dir:-}" ]] && run_failed "$run_dir"; then
    echo "Run failed for role $ROLE in $run_dir"
    print_failure_context "$run_dir"
  elif (( command_status != 0 )); then
    echo "Run exited non-zero for role $ROLE (status $command_status)."
  elif (( saw_failure_keyword == 1 )); then
    echo "Failure keywords detected in live output for role $ROLE."
  elif (( step_count == 0 )); then
    echo "Run produced no executed QA steps for role $ROLE."
  else
    echo "Run ended without a clean success signal for role $ROLE."
  fi

  if [[ -n "${run_dir:-}" ]]; then
    fix_branch="$(extract_fix_branch "$run_dir")"
    fix_commit="$(extract_fix_commit "$run_dir")"
    if [[ -n "${fix_branch:-}" ]]; then
      echo "Fix branch: $fix_branch"
    fi
    if [[ -n "${fix_commit:-}" ]]; then
      echo "Fix commit: $fix_commit"
    fi
  fi

  if (( attempt == MAX_ATTEMPTS )); then
    echo "Reached max attempts for $ROLE"
    exit 1
  fi

  invoke_script_autofix "$ROLE" "$attempt" "${run_dir:-}" "$attempt_log"
  if [[ -n "${LAST_WATCHDOG_FIX_BRANCH:-}" ]]; then
    echo "Retry will use watchdog fix branch output from $LAST_WATCHDOG_FIX_BRANCH"
  fi
  echo "Retrying $ROLE after self-heal attempt in ${RETRY_DELAY_SECONDS}s..."
  sleep "$RETRY_DELAY_SECONDS"
  attempt=$((attempt + 1))
done

exit 1
