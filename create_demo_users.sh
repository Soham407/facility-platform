#!/usr/bin/env bash
# Creates guard.demo and resident.demo auth users via Supabase Admin API
# Then prints their UUIDs so you can run the seed SQL

set -euo pipefail

SUPABASE_URL="https://wwhbdgwfodumognpkgrf.supabase.co"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDEzNjI5OCwiZXhwIjoyMDg1NzEyMjk4fQ.NcWmV8qrc1ONvVFk1MCwS1ThYouB8sAzXBiXQm6-2N4"

create_user() {
  local email="$1"
  local password="$2"
  local resp
  resp=$(curl -s \
    -X POST \
    -H "apikey: $SERVICE_KEY" \
    -H "Authorization: Bearer $SERVICE_KEY" \
    -H "Content-Type: application/json" \
    "$SUPABASE_URL/auth/v1/admin/users" \
    --data "{\"email\":\"$email\",\"password\":\"$password\",\"email_confirm\":true}")

  local uid
  uid=$(echo "$resp" | jq -r '.id // empty')

  if [[ -n "$uid" ]]; then
    echo "✅  $email  →  $uid"
    echo "$uid"
  else
    local err
    err=$(echo "$resp" | jq -r '.msg // .message // .error_description // "unknown"')
    # User may already exist — try to fetch
    if echo "$err" | grep -qi "already\|exists"; then
      echo "ℹ️   $email already exists, fetching UUID..."
      local list
      list=$(curl -s \
        -H "apikey: $SERVICE_KEY" \
        -H "Authorization: Bearer $SERVICE_KEY" \
        "$SUPABASE_URL/auth/v1/admin/users?page=1&per_page=200")
      uid=$(echo "$list" | jq -r --arg e "$email" '.users[] | select(.email==$e) | .id' 2>/dev/null | head -1)
      if [[ -n "$uid" ]]; then
        echo "✅  $email  →  $uid"
        echo "$uid"
      else
        echo "❌  Could not find $email: $err"
        echo ""
      fi
    else
      echo "❌  Failed to create $email: $err"
      echo ""
    fi
  fi
}

echo "Creating demo auth users..."
echo

# Capture only the UUID lines (second echo in create_user)
GUARD_UUID=$(create_user "guard.demo@facilitypro.local" "FacilityPro@2026" | tail -1)
RESIDENT_UUID=$(create_user "resident.demo@facilitypro.local" "FacilityPro@2026" | tail -1)

echo
if [[ -n "$GUARD_UUID" && -n "$RESIDENT_UUID" ]]; then
  echo "════════════════════════════════════════════════"
  echo "  GUARD_AUTH_UUID    = $GUARD_UUID"
  echo "  RESIDENT_AUTH_UUID = $RESIDENT_UUID"
  echo "════════════════════════════════════════════════"
  echo
  echo "Next: open GUARD_RESIDENT_SEED.sql, replace:"
  echo "  GUARD_AUTH_UUID     → $GUARD_UUID"
  echo "  RESIDENT_AUTH_UUID  → $RESIDENT_UUID"
  echo "  GUARD_PHONE         → your test phone (e.g. 9876543210)"
  echo "  RESIDENT_PHONE      → your test phone (same or different)"
  echo
  echo "Then run the SQL in Supabase Studio → SQL Editor."
else
  echo "⚠️  One or both UUIDs missing — check errors above."
fi
