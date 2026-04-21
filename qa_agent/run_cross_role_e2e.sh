#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

QA_CROSS_ROLE_LIST="${QA_CROSS_ROLE_LIST:-qa_agent/maestro/guard_resident_visitor_e2e.yaml}"
QA_CROSS_ROLE_RESULTS_LOG="${QA_CROSS_ROLE_RESULTS_LOG:-${TMPDIR:-/tmp}/qa-cross-role-e2e-results.log}"
QA_MAESTRO_MAX_ATTEMPTS="${QA_MAESTRO_MAX_ATTEMPTS:-1}"

typeset -a flows
flows=(${=QA_CROSS_ROLE_LIST})

: > "$QA_CROSS_ROLE_RESULTS_LOG"

pass_count=0
fail_count=0

for flow in "${flows[@]}"; do
  echo "=== Running $flow ==="
  if QA_MAESTRO_MAX_ATTEMPTS="$QA_MAESTRO_MAX_ATTEMPTS" "$SCRIPT_DIR/run_maestro_smoke.sh" "$flow"; then
    echo "PASS $flow" | tee -a "$QA_CROSS_ROLE_RESULTS_LOG"
    pass_count=$((pass_count + 1))
  else
    echo "FAIL $flow" | tee -a "$QA_CROSS_ROLE_RESULTS_LOG"
    fail_count=$((fail_count + 1))
  fi
done

echo ""
echo "Cross-role E2E summary"
cat "$QA_CROSS_ROLE_RESULTS_LOG"
echo "Passed: $pass_count"
echo "Failed: $fail_count"

if (( fail_count > 0 )); then
  exit 1
fi
