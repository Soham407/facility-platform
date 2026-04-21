#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

QA_FULL_ROLE_LIST="${QA_FULL_ROLE_LIST:-guard_full_e2e resident_full_e2e buyer_full_e2e employee_full_e2e supplier_full_e2e security_supervisor_full_e2e society_manager_full_e2e vendor_full_e2e ac_technician_full_e2e pest_control_technician_full_e2e delivery_boy_full_e2e service_boy_full_e2e}"
QA_FULL_RESULTS_LOG="${QA_FULL_RESULTS_LOG:-${TMPDIR:-/tmp}/qa-full-e2e-results.log}"
QA_MAESTRO_MAX_ATTEMPTS="${QA_MAESTRO_MAX_ATTEMPTS:-1}"

typeset -a roles
roles=(${=QA_FULL_ROLE_LIST})

: > "$QA_FULL_RESULTS_LOG"

pass_count=0
fail_count=0

for role in "${roles[@]}"; do
  echo "=== Running $role ==="
  if QA_MAESTRO_MAX_ATTEMPTS="$QA_MAESTRO_MAX_ATTEMPTS" "$SCRIPT_DIR/run_maestro_smoke.sh" "$role"; then
    echo "PASS $role" | tee -a "$QA_FULL_RESULTS_LOG"
    pass_count=$((pass_count + 1))
  else
    echo "FAIL $role" | tee -a "$QA_FULL_RESULTS_LOG"
    fail_count=$((fail_count + 1))
  fi
done

echo ""
echo "Full E2E summary"
cat "$QA_FULL_RESULTS_LOG"
echo "Passed: $pass_count"
echo "Failed: $fail_count"

if (( fail_count > 0 )); then
  exit 1
fi
