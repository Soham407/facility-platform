#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MOBILE_ROOT="$REPO_ROOT/Solvesxx_mobile"
WEB_ROOT="$REPO_ROOT/Solvesxx_web"
ARTIFACTS_ROOT="$REPO_ROOT/qa_agent/artifacts"

EMULATOR_ID="${QA_EMULATOR_ID:-emulator-5554}"
QA_AVD_NAME="${QA_AVD_NAME:-Pixel_10_Pro}"
METRO_PORT="${QA_METRO_PORT:-8081}"
SKIP_EMULATOR="${QA_SKIP_EMULATOR:-0}"
ADB_CMD="${QA_ADB_COMMAND:-adb}"
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
ANDROID_EMULATOR_BIN="${ANDROID_EMULATOR_BIN:-$ANDROID_SDK_ROOT/emulator/emulator}"

if [[ ! -x "$ADB_CMD" ]] && [[ -z "${QA_ADB_COMMAND:-}" ]]; then
  for candidate in \
    "$HOME/Library/Android/sdk/platform-tools/adb" \
    "/opt/homebrew/bin/adb" \
    "/usr/local/bin/adb"; do
    if [[ -x "$candidate" ]]; then
      ADB_CMD="$candidate"
      break
    fi
  done
fi

echo "============================================================"
echo "  Guard + Resident V1 Production Checklist"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""
echo "  Repo:     $REPO_ROOT"
echo "  Mobile:   $MOBILE_ROOT"
echo "  Web:      $WEB_ROOT"
echo "  Emulator: $EMULATOR_ID"
echo "  Metro:    port $METRO_PORT"
echo ""

mkdir -p "$ARTIFACTS_ROOT"
SESSION_LOG="$ARTIFACTS_ROOT/production-checklist-session-$(date '+%Y%m%d-%H%M%S').log"
exec > >(tee -a "$SESSION_LOG") 2>&1

echo "Session log: $SESSION_LOG"
echo ""

wait_for_device() {
  local deadline=$((SECONDS + 180))
  echo "Waiting for emulator $EMULATOR_ID..."
  while (( SECONDS < deadline )); do
    if "$ADB_CMD" -s "$EMULATOR_ID" get-state 2>/dev/null | grep -q "device"; then
      echo "Emulator ready."
      return 0
    fi
    sleep 2
  done
  echo "WARNING: Emulator not available after 180s. Continuing anyway."
  return 1
}

ensure_command() {
  local command_path="$1"
  local label="$2"
  if [[ ! -x "$command_path" ]]; then
    echo "$label not found or not executable: $command_path" >&2
    exit 1
  fi
}

connected_emulator_id() {
  "$ADB_CMD" devices | awk 'NR>1 && $2 == "device" && $1 ~ /^emulator-/ { print $1; exit }'
}

emulator_running() {
  [[ -n "$(connected_emulator_id)" ]]
}

start_emulator_if_needed() {
  if emulator_running; then
    echo "Emulator already running."
    return 0
  fi

  ensure_command "$ANDROID_EMULATOR_BIN" "Android emulator"
  ensure_command "$ADB_CMD" "adb"

  echo "Starting emulator: $QA_AVD_NAME"
  nohup "$ANDROID_EMULATOR_BIN" -avd "$QA_AVD_NAME" >"${TMPDIR:-/tmp}/qa-production-checklist-emulator.log" 2>&1 &
  wait_for_device
}

is_port_open() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1
    return $?
  fi

  if command -v nc >/dev/null 2>&1; then
    nc -z 127.0.0.1 "$port" >/dev/null 2>&1
    return $?
  fi

  python3 - "$port" <<'PY' >/dev/null 2>&1
import socket
import sys

port = int(sys.argv[1])
s = socket.socket()
s.settimeout(1.0)
try:
    s.connect(("127.0.0.1", port))
except OSError:
    raise SystemExit(1)
finally:
    s.close()
raise SystemExit(0)
PY
}

metro_listener_info() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$port" -sTCP:LISTEN || true
  else
    echo "Listener details unavailable (lsof not installed)"
  fi
}

start_metro_if_needed() {
  if is_port_open "$METRO_PORT"; then
    echo "Metro already running on port $METRO_PORT."
    metro_listener_info "$METRO_PORT"
    return 0
  fi

  echo "Starting Metro dev server on port $METRO_PORT..."
  cd "$MOBILE_ROOT"
  npx expo start --dev-client --clear --port "$METRO_PORT" &
  local metro_pid=$!
  cd "$REPO_ROOT"

  local deadline=$((SECONDS + 120))
  while (( SECONDS < deadline )); do
    if is_port_open "$METRO_PORT"; then
      echo "Metro started (pid $metro_pid)."
      return 0
    fi
    sleep 2
  done

  echo "WARNING: Metro did not start within 120s."
  return 1
}

if [[ "$SKIP_EMULATOR" != "1" ]]; then
  start_emulator_if_needed || true
  start_metro_if_needed || true
  echo ""
fi

echo "Starting checkpoint runner..."
echo ""

cd "$REPO_ROOT"

export QA_CODEX_COMMAND="${QA_CODEX_COMMAND:-codex}"
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1

set +e
python3 -u -m qa_agent.checkpoint_runner
checklist_exit=$?
set -e

echo ""
if (( checklist_exit == 0 )); then
  echo "============================================================"
  echo "  ALL CHECKPOINTS PASSED"
  echo "============================================================"
else
  echo "============================================================"
  echo "  SOME CHECKPOINTS FAILED — see report in qa_agent/artifacts/"
  echo "============================================================"
fi

exit $checklist_exit
