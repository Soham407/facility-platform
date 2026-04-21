#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MOBILE_ROOT="$REPO_ROOT/Solvesxx_mobile"
MAESTRO_ROOT="$REPO_ROOT/qa_agent/maestro"

FLOW_NAME="${1:-buyer}"
QA_AVD_NAME="${QA_AVD_NAME:-Pixel_10_Pro}"
QA_METRO_PORT="${QA_METRO_PORT:-8081}"
QA_MAESTRO_MAX_ATTEMPTS="${QA_MAESTRO_MAX_ATTEMPTS:-3}"
QA_MAESTRO_RETRY_DELAY_SECONDS="${QA_MAESTRO_RETRY_DELAY_SECONDS:-5}"

ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
ANDROID_EMULATOR_BIN="${ANDROID_EMULATOR_BIN:-$ANDROID_SDK_ROOT/emulator/emulator}"
ADB_BIN="${QA_ADB_COMMAND:-$ANDROID_SDK_ROOT/platform-tools/adb}"

EMULATOR_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-emulator.log"
METRO_LOG="${TMPDIR:-/tmp}/qa-maestro-smoke-metro.log"

resolve_flow_path() {
  case "$FLOW_NAME" in
    buyer)
      printf '%s\n' "$MAESTRO_ROOT/buyer_smoke.yaml"
      ;;
    *_full_e2e)
      printf '%s\n' "$MAESTRO_ROOT/${FLOW_NAME}.yaml"
      ;;
    *.yaml)
      printf '%s\n' "$FLOW_NAME"
      ;;
    *)
      printf '%s\n' "$MAESTRO_ROOT/${FLOW_NAME}_smoke.yaml"
      ;;
  esac
}

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

matches_disconnect_error() {
  local output="$1"
  local pattern="device '.*' not found|tcp:7001|Connection refused|gRPC timeout|UNAVAILABLE|io exception"
  if command -v rg >/dev/null 2>&1; then
    printf '%s\n' "$output" | rg -qi "$pattern"
    return $?
  fi
  printf '%s\n' "$output" | grep -Eiq "$pattern"
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

reconnect_adb() {
  "$ADB_BIN" start-server >/dev/null 2>&1 || true
  "$ADB_BIN" reconnect offline >/dev/null 2>&1 || true
  wait_for_emulator
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

run_flow() {
  local flow_path="$1"
  if [[ ! -f "$flow_path" ]]; then
    echo "Maestro flow not found: $flow_path" >&2
    exit 1
  fi

  cd "$REPO_ROOT"
  local attempt=1
  while (( attempt <= QA_MAESTRO_MAX_ATTEMPTS )); do
    local device_id
    device_id="$(connected_emulator_id)"
    if [[ -z "$device_id" ]]; then
      echo "No connected emulator found. Reconnecting adb..."
      reconnect_adb
      device_id="$(connected_emulator_id)"
    fi
    if [[ -z "$device_id" ]]; then
      echo "No connected emulator found after adb reconnect." >&2
      exit 1
    fi

    echo "Running flow: $flow_path"
    echo "Using device: $device_id"
    echo "Maestro attempt: $attempt/$QA_MAESTRO_MAX_ATTEMPTS"

    set +e
    local output
    output="$(maestro --device "$device_id" test "$flow_path" 2>&1)"
    local exit_code=$?
    set -e
    printf '%s\n' "$output"

    if (( exit_code == 0 )); then
      return 0
    fi

    if matches_disconnect_error "$output"; then
      if (( attempt == QA_MAESTRO_MAX_ATTEMPTS )); then
        echo "Maestro failed after retrying ADB/device disconnects." >&2
        return "$exit_code"
      fi
      echo "Detected transient Maestro/ADB disconnect. Reconnecting and retrying in ${QA_MAESTRO_RETRY_DELAY_SECONDS}s..."
      reconnect_adb
      sleep "$QA_MAESTRO_RETRY_DELAY_SECONDS"
      attempt=$((attempt + 1))
      continue
    fi

    return "$exit_code"
  done
}

FLOW_PATH="$(resolve_flow_path)"

start_emulator_if_needed
start_metro_if_needed
run_flow "$FLOW_PATH"

echo "Emulator log: $EMULATOR_LOG"
echo "Metro log: $METRO_LOG"
