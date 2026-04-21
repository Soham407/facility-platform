#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FLOW_PATH="$REPO_ROOT/qa_agent/maestro/guard_push_trigger_staging.yaml"
MOBILE_ROOT="$REPO_ROOT/Solvesxx_mobile"

QA_GUARD_AVD_NAME="${QA_GUARD_AVD_NAME:-Pixel_10}"
QA_GUARD_DEVICE_ID="${QA_GUARD_DEVICE_ID:-}"
QA_METRO_PORT="${QA_METRO_PORT:-8081}"
ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
ANDROID_EMULATOR_BIN="${ANDROID_EMULATOR_BIN:-$ANDROID_SDK_ROOT/emulator/emulator}"
ADB_BIN="${QA_ADB_COMMAND:-$ANDROID_SDK_ROOT/platform-tools/adb}"

EMULATOR_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-emulator.log"
METRO_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-metro.log"

TARGET_FLAT_ID="1ae71b6b-fc10-4fcf-8005-c7f0c90f16f8"
TARGET_VISITOR_NAME="Staging Push Test"

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

running_emulator_ids() {
  "$ADB_BIN" devices | awk 'NR>1 && $2 == "device" && $1 ~ /^emulator-/ { print $1 }'
}

emulator_process_running() {
  pgrep -f "emulator.*-avd[[:space:]]+$QA_GUARD_AVD_NAME" >/dev/null 2>&1
}

device_avd_name() {
  "$ADB_BIN" -s "$1" emu avd name 2>/dev/null | tr -d '\r'
}

device_for_avd_name() {
  local id
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    if [[ "$(device_avd_name "$id")" == "$QA_GUARD_AVD_NAME" ]]; then
      printf '%s\n' "$id"
      return 0
    fi
  done < <(running_emulator_ids)
  return 1
}

wait_for_device() {
  local attempts=0
  until device_for_avd_name >/dev/null 2>&1; do
    attempts=$((attempts + 1))
    if (( attempts > 180 )); then
      echo "Timed out waiting for emulator $QA_GUARD_AVD_NAME to boot." >&2
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
  if [[ -n "$QA_GUARD_DEVICE_ID" ]]; then
    echo "Using explicit guard device: $QA_GUARD_DEVICE_ID"
    return
  fi

  if device_for_avd_name >/dev/null 2>&1; then
    echo "Guard emulator already running: $QA_GUARD_AVD_NAME"
    return
  fi

  if emulator_process_running; then
    echo "Guard emulator process already running for $QA_GUARD_AVD_NAME. Waiting for boot..."
    wait_for_device
    echo "Guard emulator ready: $(device_for_avd_name)"
    return
  fi

  ensure_command "$ANDROID_EMULATOR_BIN" "Android emulator"
  ensure_command "$ADB_BIN" "adb"

  echo "Starting guard emulator: $QA_GUARD_AVD_NAME"
  nohup "$ANDROID_EMULATOR_BIN" -avd "$QA_GUARD_AVD_NAME" >"$EMULATOR_LOG" 2>&1 &
  wait_for_device
  echo "Guard emulator ready: $(device_for_avd_name)"
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

DEVICE_ID="$QA_GUARD_DEVICE_ID"
if [[ -z "$DEVICE_ID" ]]; then
  DEVICE_ID="$(device_for_avd_name)"
fi
if [[ -z "$DEVICE_ID" ]]; then
  echo "No connected guard device found. Checked QA_GUARD_DEVICE_ID and AVD name $QA_GUARD_AVD_NAME." >&2
  exit 1
fi

echo "Using guard device: $DEVICE_ID ($QA_GUARD_AVD_NAME)"
echo "Force-stopping the app on the guard device"
"$ADB_BIN" -s "$DEVICE_ID" shell am force-stop com.facilitypro.mobile >/dev/null

echo "Resetting prior push-test visitors for Rohit Verna's flat"
supabase db query "
delete from public.visitors
where flat_id = '$TARGET_FLAT_ID'
  and visitor_name = '$TARGET_VISITOR_NAME';
" --linked >/dev/null

if [[ ! -f "$FLOW_PATH" ]]; then
  echo "Maestro flow not found: $FLOW_PATH" >&2
  exit 1
fi

echo "Running guard push trigger flow: $FLOW_PATH"
maestro --device "$DEVICE_ID" test "$FLOW_PATH"

echo "Verifying pending visitor in Supabase"
VISITOR_RESULT="$(supabase db query "
select
  visitor_name,
  flat_id,
  approval_status,
  entry_time
from public.visitors
where flat_id = '$TARGET_FLAT_ID'
  and visitor_name = '$TARGET_VISITOR_NAME'
order by entry_time desc
limit 1;
" --linked)"

echo "$VISITOR_RESULT"

if [[ "$VISITOR_RESULT" != *"$TARGET_VISITOR_NAME"* ]]; then
  echo "No push-test visitor row was created." >&2
  exit 1
fi

if [[ "$VISITOR_RESULT" != *"pending"* ]]; then
  echo "Push-test visitor row was created but is not pending." >&2
  exit 1
fi

echo "Guard push trigger completed. Watch the resident device for the notification."
