#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

export QA_LOGIN_ROLE="${QA_LOGIN_ROLE:-buyer}"
export QA_ALLOW_NAVIGATOR="${QA_ALLOW_NAVIGATOR:-1}"
export QA_ALLOW_AUDITOR="${QA_ALLOW_AUDITOR:-1}"
export QA_ALLOW_FIXER="${QA_ALLOW_FIXER:-1}"
export QA_LOOP_LIMIT="${QA_LOOP_LIMIT:-40}"
export QA_IDLE_STALL_LIMIT="${QA_IDLE_STALL_LIMIT:-12}"
export QA_STEP_DELAY_SECONDS="${QA_STEP_DELAY_SECONDS:-2.5}"

cd "$REPO_ROOT"
python3 -m qa_agent.main
