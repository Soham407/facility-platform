#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FLOW_PATH="$REPO_ROOT/qa_agent/maestro/guard_checklist_staging_e2e.yaml"
MOBILE_ROOT="$REPO_ROOT/Solvesxx_mobile"

QA_AVD_NAME="${QA_AVD_NAME:-Pixel_10_Pro}"
QA_METRO_PORT="${QA_METRO_PORT:-8081}"
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
ANDROID_EMULATOR_BIN="${ANDROID_EMULATOR_BIN:-$ANDROID_SDK_ROOT/emulator/emulator}"
ADB_BIN="${QA_ADB_COMMAND:-$ANDROID_SDK_ROOT/platform-tools/adb}"

EMULATOR_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-emulator.log"
METRO_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-metro.log"

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

echo "Force-stopping the app for a clean guard checklist staging run"
"$ADB_BIN" shell am force-stop com.facilitypro.mobile >/dev/null

echo "Resetting today's guard checklist response for a clean backend verification"
supabase db query "
delete from public.checklist_responses
where employee_id = '11111111-1111-1111-1111-111111111111'
  and response_date = current_date;
" --linked >/dev/null

echo "Running guard checklist staging flow: $FLOW_PATH"
QA_MAESTRO_MAX_ATTEMPTS="${QA_MAESTRO_MAX_ATTEMPTS:-1}" \
  "$REPO_ROOT/qa_agent/run_maestro_smoke.sh" "$FLOW_PATH"

echo "Verifying latest checklist submission in Supabase"
CHECKLIST_RESULT="$(supabase db query "
select checklist_id, employee_id, submitted_at, is_complete
from public.checklist_responses
where employee_id = '11111111-1111-1111-1111-111111111111'
  and response_date = current_date
order by submitted_at desc
limit 1;
" --linked)"

echo "$CHECKLIST_RESULT"

if [[ "$CHECKLIST_RESULT" == *'"rows": []'* ]]; then
  echo "No checklist response was created for today." >&2
  exit 1
fi

if [[ "$CHECKLIST_RESULT" != *"11111111-1111-1111-1111-111111111111"* ]]; then
  echo "Checklist response row for the guard employee was not returned." >&2
  exit 1
fi

if [[ "$CHECKLIST_RESULT" != *"true"* ]]; then
  echo "Checklist response was created but is_complete is false." >&2
  exit 1
fi
