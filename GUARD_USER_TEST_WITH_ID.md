# Testing Notifications with Specific Guard User ID

## Your Guard User ID
```
34ed8531-728c-4ef1-b7cc-2144ff45ebd2
```

## Issue Resolution

### Problem 1: SQL Column Names Don't Match
Run this query to see actual columns:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

### Problem 2: Forgot Password / Hardcoded OTP Testing
Since you're testing with hardcoded OTP on mobile, we generate a temporary test token instead.

---

## Solution: 4-Step Testing Process

### Step 1: Create Test User and Get Token

Run this curl command:

```bash
curl -X POST https://wwhbdgwfodumognpkgrf.supabase.co/auth/v1/signup \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxMzYyOTgsImV4cCI6MjA4NTcxMjI5OH0.Iw5KYmIP_OHalA2tyHAiKSI6xQa-EE5urL_4aEygzg0" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser'$(date +%s)'@test.com",
    "password": "TestPass123!"
  }' | jq '.session.access_token'
```

This returns a temporary access token. **Copy this token.**

Expected output:
```
"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MjhkOTBkNC..."
```

### Step 2: Send Notification to Guard User

Replace `[YOUR_TOKEN]` with the token from Step 1:

```bash
curl -X POST \
  https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification \
  -H "Authorization: Bearer [YOUR_TOKEN]" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "34ed8531-728c-4ef1-b7cc-2144ff45ebd2",
    "title": "Guard Test Notification",
    "body": "Testing push notifications system",
    "data": {
      "test_type": "guard_test",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    },
    "channel": "fcm"
  }'
```

### Step 3: Check Response

Expected response:
```json
{
  "success": true,
  "logs": [
    {
      "user_id": "34ed8531-728c-4ef1-b7cc-2144ff45ebd2",
      "channel": "fcm",
      "status": "sent",
      "error_message": null,
      "sent_at": "2026-04-22T01:13:33Z"
    }
  ]
}
```

✅ If you see `"status": "sent"` → Edge Function worked!
❌ If you see `"status": "failed"` → Check `error_message` field for details

### Step 4: Verify End-to-End Delivery

**On Device:**
- Look at Android notification tray (top of screen)
- Should see "Guard Test Notification" within 5-10 seconds
- Tap notification to open app

**In Database:**
Go to Supabase SQL Editor and run:

```sql
SELECT * FROM notification_logs 
WHERE user_id = '34ed8531-728c-4ef1-b7cc-2144ff45ebd2'
ORDER BY created_at DESC 
LIMIT 1;
```

You should see:
- `status = 'sent'`
- `error_message = null`
- `channel = 'fcm'`
- `sent_at` = recent timestamp

---

## Automated One-Liner

If you have `jq` installed, use this one command:

```bash
TOKEN=$(curl -s -X POST https://wwhbdgwfodumognpkgrf.supabase.co/auth/v1/signup \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxMzYyOTgsImV4cCI6MjA4NTcxMjI5OH0.Iw5KYmIP_OHalA2tyHAiKSI6xQa-EE5urL_4aEygzg0" \
  -H "Content-Type: application/json" \
  -d '{"email":"test'$(date +%s)'@test.com","password":"Pass123!"}' | jq -r '.session.access_token') && \
echo "Token: $TOKEN" && \
curl -X POST https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"34ed8531-728c-4ef1-b7cc-2144ff45ebd2","title":"Guard Test","body":"Test notif","channel":"fcm"}' | jq '.'
```

---

## Success Checklist

✅ Curl Step 1 returns `access_token`
✅ Curl Step 2 returns `"status": "sent"`
✅ Entry appears in `notification_logs` table
✅ Notification appears on device in 5-10 seconds
✅ User can tap and open app

**All 5 = END-TO-END SUCCESS! 🎉**

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `jq: command not found` | Install: `brew install jq` |
| Curl Step 1 fails | Check internet connection |
| `"status": "failed"` | Check `error_message` field in response |
| No notification on device | Check device internet, wait 10s, check notification settings |
| Nothing in `notification_logs` | Check curl Step 2 response first - if that failed, function didn't run |

---

## Key Credentials

- **Supabase Project:** wwhbdgwfodumognpkgrf
- **Guard User ID:** 34ed8531-728c-4ef1-b7cc-2144ff45ebd2
- **Edge Function:** send-notification (v8)
- **Firebase Project:** facilitypro-81bde
- **Anon Key:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3aGJkZ3dmb2R1bW9nbnBrZ3JmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxMzYyOTgsImV4cCI6MjA4NTcxMjI5OH0.Iw5KYmIP_OHalA2tyHAiKSI6xQa-EE5urL_4aEygzg0

