#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FLOW_PATH="$REPO_ROOT/qa_agent/maestro/guard_resident_staging_e2e.yaml"
MOBILE_ROOT="$REPO_ROOT/Solvesxx_mobile"

QA_AVD_NAME="${QA_AVD_NAME:-Pixel_10_Pro}"
QA_METRO_PORT="${QA_METRO_PORT:-8081}"
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
ANDROID_EMULATOR_BIN="${ANDROID_EMULATOR_BIN:-$ANDROID_SDK_ROOT/emulator/emulator}"
ADB_BIN="${QA_ADB_COMMAND:-$ANDROID_SDK_ROOT/platform-tools/adb}"

EMULATOR_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-emulator.log"
METRO_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-metro.log"

TARGET_FLAT_ID="1ae71b6b-fc10-4fcf-8005-c7f0c90f16f8"
TARGET_VISITOR_NAME="Staging Approve Visitor 01"
DENY_VISITOR_NAME="Staging Deny Visitor 01"

ensure_command() {
  local command_path="$1"
  local label="$2"
  if [[ ! -x "$command_path" ]]; then
    echo "$label not found or not executable: $command_path" >&2
    exit 1
  fi
}

port_open() {
  nc -z 127.0.0.1 "$1" >/dev/null 2>&1
}

connected_emulator_id() {
  "$ADB_BIN" devices | awk 'NR>1 && $2 == "device" && $1 ~ /^emulator-/ { print $1; exit }'
}

emulator_running() {
  [[ -n "$(connected_emulator_id)" ]]
}

wait_for_emulator() {
  local attempts=0
  until emulator_running; do
    attempts=$((attempts + 1))
    if (( attempts > 180 )); then
      echo "Timed out waiting for emulator to boot." >&2
      exit 1
    fi
    sleep 2
  done
}

wait_for_metro() {
  local attempts=0
  until port_open "$QA_METRO_PORT"; do
    attempts=$((attempts + 1))
    if (( attempts > 120 )); then
      echo "Timed out waiting for Metro on port $QA_METRO_PORT." >&2
      exit 1
    fi
    sleep 2
  done
}

start_emulator_if_needed() {
  if emulator_running; then
    echo "Emulator already running."
    return
  fi

  ensure_command "$ANDROID_EMULATOR_BIN" "Android emulator"
  ensure_command "$ADB_BIN" "adb"

  echo "Starting emulator: $QA_AVD_NAME"
  nohup "$ANDROID_EMULATOR_BIN" -avd "$QA_AVD_NAME" >"$EMULATOR_LOG" 2>&1 &
  wait_for_emulator
  echo "Emulator ready: $(connected_emulator_id)"
}

start_metro_if_needed() {
  if port_open "$QA_METRO_PORT"; then
    echo "Metro already running on port $QA_METRO_PORT."
    return
  fi

  echo "Starting Metro on port $QA_METRO_PORT"
  (
    cd "$MOBILE_ROOT"
    nohup npx expo start --dev-client --clear --port "$QA_METRO_PORT" >"$METRO_LOG" 2>&1 &
  )
  wait_for_metro
  echo "Metro ready."
}

start_emulator_if_needed
start_metro_if_needed

echo "Force-stopping the app for a clean guard/resident staging run"
"$ADB_BIN" shell am force-stop com.facilitypro.mobile >/dev/null

echo "Resetting prior test visitors for Rohit Verna's flat"
supabase db query "
delete from public.visitors
where flat_id = '$TARGET_FLAT_ID'
  and visitor_name in ('$TARGET_VISITOR_NAME', '$DENY_VISITOR_NAME');
" --linked >/dev/null

echo "Running guard resident staging flow: $FLOW_PATH"
QA_MAESTRO_MAX_ATTEMPTS="${QA_MAESTRO_MAX_ATTEMPTS:-1}" \
  "$REPO_ROOT/qa_agent/run_maestro_smoke.sh" "$FLOW_PATH"

echo "Verifying approved visitor in Supabase"
VISITOR_RESULT="$(supabase db query "
select
  visitor_name,
  flat_id,
  approval_status,
  approved_by_resident,
  decision_at,
  entry_time
from public.visitors
where flat_id = '$TARGET_FLAT_ID'
  and visitor_name = '$TARGET_VISITOR_NAME'
order by entry_time desc
limit 1;
" --linked)"

echo "$VISITOR_RESULT"

if [[ "$VISITOR_RESULT" != *"$TARGET_VISITOR_NAME"* ]]; then
  echo "No staging visitor row was created." >&2
  exit 1
fi

if [[ "$VISITOR_RESULT" != *"approved"* ]]; then
  echo "Visitor row was created but did not reach approved state." >&2
  exit 1
fi

if [[ "$VISITOR_RESULT" != *"true"* ]]; then
  echo "Visitor row was created but resident approval was not recorded." >&2
  exit 1
fi
