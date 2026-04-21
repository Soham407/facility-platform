#!/bin/bash

# FacilityPro Guard Notification Test Script
# Tests push notifications on guard user: 34ed8531-728c-4ef1-b7cc-2144ff45ebd2

echo "🔐 Step 1: Creating test user and getting auth token..."

# Get access token
RESPONSE=$(curl -s -X POST https://wwhbdgwfodumognpkgrf.supabase.co/auth/v1/signup \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxMzYyOTgsImV4cCI6MjA4NTcxMjI5OH0.Iw5KYmIP_OHalA2tyHAiKSI6xQa-EE5urL_4aEygzg0" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser'$(date +%s)'@test.com","password":"Pass123!"}')

TOKEN=$(echo "$RESPONSE" | jq -r '.session.access_token' 2>/dev/null)

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
  echo "❌ Failed to get token. Response:"
  echo "$RESPONSE" | jq '.'
  exit 1
fi

echo "✅ Token received: ${TOKEN:0:50}..."

echo ""
echo "📤 Step 2: Sending notification to guard user..."

# Send notification
NOTIF_RESPONSE=$(curl -s -X POST https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"34ed8531-728c-4ef1-b7cc-2144ff45ebd2","title":"Guard Test Notification","body":"Testing push notifications system","channel":"fcm"}')

echo "📬 Response:"
echo "$NOTIF_RESPONSE" | jq '.'

echo ""
echo "✅ Check:"
echo "  1. Look at device notification tray (5-10 seconds)"
echo "  2. Run SQL: SELECT * FROM notification_logs WHERE user_id = '34ed8531-728c-4ef1-b7cc-2144ff45ebd2' ORDER BY created_at DESC LIMIT 1;"
echo "  3. Should show: status='sent', error_message=null"

