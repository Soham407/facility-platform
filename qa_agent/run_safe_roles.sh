#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MOBILE_ROOT="$REPO_ROOT/Solvesxx_mobile"

QA_AVD_NAME="${QA_AVD_NAME:-Pixel_10_Pro}"
QA_METRO_PORT="${QA_METRO_PORT:-8081}"
QA_ROLE_LIST="${QA_ROLE_LIST:-buyer employee security_supervisor society_manager supplier vendor ac_technician pest_control_technician delivery_boy service_boy}"
QA_MAX_ATTEMPTS="${QA_MAX_ATTEMPTS:-3}"

ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
ANDROID_EMULATOR_BIN="${ANDROID_EMULATOR_BIN:-$ANDROID_SDK_ROOT/emulator/emulator}"
ADB_BIN="${QA_ADB_COMMAND:-$ANDROID_SDK_ROOT/platform-tools/adb}"

EMULATOR_LOG="${TMPDIR:-/tmp}/qa-safe-roles-emulator.log"
METRO_LOG="${TMPDIR:-/tmp}/qa-safe-roles-metro.log"
RESULTS_LOG="${TMPDIR:-/tmp}/qa-safe-roles-results.log"

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

emulator_running() {
  "$ADB_BIN" devices | awk 'NR>1 {print $1}' | grep -q '^emulator-'
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
  echo "Emulator ready."
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

run_roles() {
  cd "$REPO_ROOT"
  local failed_roles=()
  : >"$RESULTS_LOG"
  for role in ${(z)QA_ROLE_LIST}; do
    echo "=== Running $role ==="
    if QA_LOGIN_ROLE="$role" QA_MAX_ATTEMPTS="$QA_MAX_ATTEMPTS" ./qa_agent/run_self_healing_role.sh "$role"; then
      echo "$role PASS" | tee -a "$RESULTS_LOG"
    else
      echo "$role FAIL" | tee -a "$RESULTS_LOG"
      failed_roles+=("$role")
    fi
  done

  echo "Role results:"
  cat "$RESULTS_LOG"

  if (( ${#failed_roles[@]} > 0 )); then
    echo "Failed roles: ${failed_roles[*]}" >&2
    return 1
  fi

  return 0
}

start_emulator_if_needed
start_metro_if_needed
run_roles

echo "Safe role sweep complete."
echo "Emulator log: $EMULATOR_LOG"
echo "Metro log: $METRO_LOG"
echo "Results log: $RESULTS_LOG"
