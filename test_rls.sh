#!/usr/bin/env bash
# RLS smoke-test using existing guard (sohamb1@gmail.com) and resident (resident@test.com)
# Uses admin magic-link to mint tokens without needing passwords.

set -euo pipefail

SUPABASE_URL="https://wwhbdgwfodumognpkgrf.supabase.co"
ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxMzYyOTgsImV4cCI6MjA4NTcxMjI5OH0.Iw5KYmIP_OHalA2tyHAiKSI6xQa-EE5urL_4aEygzg0"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDEzNjI5OCwiZXhwIjoyMDg1NzEyMjk4fQ.NcWmV8qrc1ONvVFk1MCwS1ThYouB8sAzXBiXQm6-2N4"

GUARD_EMAIL="sohamb1@gmail.com"
RESIDENT_EMAIL="resident@test.com"

PASS=0
FAIL=0

ok()      { echo "  ✅  $1"; PASS=$((PASS+1)); }
fail()    { echo "  ❌  $1"; FAIL=$((FAIL+1)); }
info()    { echo "  ℹ️   $1"; }
section() { echo; echo "── $1 ──"; }

# Mint a session token for a user via admin magic-link (no password required)
get_token() {
  local email="$1"
  local link_resp token hashed action_link

  link_resp=$(curl -s \
    -X POST \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" \
    -H "Content-Type: application/json" \
    "$SUPABASE_URL/auth/v1/admin/generate_link" \
    --data "{\"type\":\"magiclink\",\"email\":\"$email\"}")

  hashed=$(echo "$link_resp" | jq -r '.hashed_token // empty')
  if [[ -z "$hashed" ]]; then
    echo ""
    return
  fi

  # Exchange the token — follow redirect to extract access_token from fragment
  local redirect
  redirect=$(curl -s -o /dev/null -w "%{redirect_url}" \
    "$SUPABASE_URL/auth/v1/verify?token=$hashed&type=magiclink&redirect_to=http://localhost:3000")

  token=$(echo "$redirect" | sed 's/.*access_token=\([^&]*\).*/\1/' | grep -v '^http' || true)
  echo "$token"
}

rls_select() {
  local token="$1" table="$2" extra="${3:-}"
  curl -s \
    -H "apikey: $ANON_KEY" \
    -H "Authorization: Bearer $token" \
    "$SUPABASE_URL/rest/v1/$table?select=id&limit=5$extra"
}

# ── 1. Service role table access ─────────────────────────────────────────────
section "Service role — table existence"

for t in security_guards attendance_logs panic_alerts guard_patrol_logs gps_tracking \
          checklist_responses checklist_assignments residents visitors; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" \
    "$SUPABASE_URL/rest/v1/$t?limit=1")
  [[ "$code" == "200" || "$code" == "206" ]] \
    && ok "$t accessible" \
    || fail "$t returned HTTP $code"
done

# ── 2. Guard token ───────────────────────────────────────────────────────────
section "Guard auth ($GUARD_EMAIL)"

GUARD_TOKEN=$(get_token "$GUARD_EMAIL")

if [[ -z "$GUARD_TOKEN" ]]; then
  fail "Could not mint guard token"
else
  ok "Guard session minted"

  for table in security_guards attendance_logs panic_alerts guard_patrol_logs visitors; do
    resp=$(rls_select "$GUARD_TOKEN" "$table")
    err=$(echo "$resp" | jq -r 'if type=="object" then .code // empty else empty end' 2>/dev/null || true)
    if [[ -n "$err" ]]; then
      msg=$(echo "$resp" | jq -r '.message // .hint // "RLS error"' 2>/dev/null || echo "RLS error")
      fail "$table SELECT → $msg"
    else
      count=$(echo "$resp" | jq 'if type=="array" then length else 0 end' 2>/dev/null || echo "0")
      ok "$table SELECT → $count row(s)"
    fi
  done
fi

# ── 3. Resident token ────────────────────────────────────────────────────────
section "Resident auth ($RESIDENT_EMAIL)"

RESIDENT_TOKEN=$(get_token "$RESIDENT_EMAIL")

if [[ -z "$RESIDENT_TOKEN" ]]; then
  fail "Could not mint resident token"
else
  ok "Resident session minted"

  # Own residents row
  resp=$(rls_select "$RESIDENT_TOKEN" "residents")
  err=$(echo "$resp" | jq -r 'if type=="object" then .code // empty else empty end' 2>/dev/null || true)
  if [[ -n "$err" ]]; then
    msg=$(echo "$resp" | jq -r '.message // .hint // "RLS error"' 2>/dev/null || echo "RLS error")
    fail "residents SELECT → $msg"
  else
    count=$(echo "$resp" | jq 'if type=="array" then length else 0 end' 2>/dev/null || echo "0")
    [[ "$count" -gt 0 ]] \
      && ok "residents SELECT → $count row(s) (own profile visible)" \
      || fail "residents SELECT → 0 rows (can't see own profile)"
  fi

  # Own visitors
  resp=$(rls_select "$RESIDENT_TOKEN" "visitors")
  err=$(echo "$resp" | jq -r 'if type=="object" then .code // empty else empty end' 2>/dev/null || true)
  [[ -n "$err" ]] \
    && fail "visitors SELECT (resident) → $(echo "$resp" | jq -r '.message // "RLS error"' 2>/dev/null || echo "RLS error")" \
    || ok "visitors SELECT (resident) → no RLS error"
fi

# ── 4. Isolation: resident must not see security_guards ─────────────────────
section "Isolation check"

if [[ -n "$RESIDENT_TOKEN" ]]; then
  resp=$(rls_select "$RESIDENT_TOKEN" "security_guards")
  count=$(echo "$resp" | jq 'if type=="array" then length else 0 end' 2>/dev/null || echo "0")
  err=$(echo "$resp" | jq -r 'if type=="object" then .code // empty else empty end' 2>/dev/null || true)
  if [[ "$count" -eq 0 ]]; then
    ok "security_guards → 0 rows for resident (correct isolation)"
  elif [[ -n "$err" ]]; then
    ok "security_guards → blocked by RLS for resident (correct)"
  else
    fail "security_guards → $count rows visible to resident — ISOLATION BREACH"
  fi
else
  info "Skipped (no resident token)"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo
echo "════════════════════════════════"
echo "  Results: ✅ $PASS passed  ❌ $FAIL failed"
echo "════════════════════════════════"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
