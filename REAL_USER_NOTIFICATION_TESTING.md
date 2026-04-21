# Real User Notification Testing Guide

## 🎯 Testing Notifications on Live Guard/Resident Users

This guide walks you through testing push notifications on real security guards or residents in your system.

---

## 🔍 5-Step Testing Process

### Step 1️⃣ - Verify Push Token Registration

**Go to:** https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/sql/new

Run this query:
```sql
SELECT 
  id,
  user_id,
  token,
  is_active,
  created_at,
  updated_at
FROM push_tokens
ORDER BY created_at DESC
LIMIT 20;
```

**✅ What to look for:**
- Token should exist for the user (created recently)
- `is_active` should be `true`
- Token is a long string starting with `ExponentPushToken`

**❌ If no token found:**
- App hasn't registered the push token yet
- Check:
  - Is the app running in foreground?
  - Did the user grant notification permissions?
  - Is device internet working?
  - Check app console for token registration errors

---

### Step 2️⃣ - Find the Guard/Resident User ID

Query the users table:
```sql
SELECT 
  id,
  email,
  phone,
  first_name,
  last_name,
  role,
  status,
  created_at
FROM users
WHERE role IN ('guard', 'security_guard', 'resident', 'user')
ORDER BY created_at DESC
LIMIT 10;
```

**📌 Copy the `id` from the user you want to test** - you'll need this for the next step.

---

### Step 3️⃣ - Get the User's Authentication Token (JWT)

You have 3 options:

#### Option A: From Browser Developer Tools
1. Open FacilityPro web app in browser
2. Press `F12` to open Developer Tools
3. Go to **Console** tab
4. Run this command:
   ```javascript
   localStorage.getItem('sb-auth-token')
   ```
5. Copy the entire token (long string with dots in it)

#### Option B: From Supabase CLI
```bash
cd /Volumes/Soham/untitled\ folder/facility-platform
supabase auth users list
```
Find the user and get their session token.

#### Option C: From Mobile App (if debug menu available)
- Open app settings
- Look for "Debug" or "Show Token" option
- Copy the token displayed

**📌 Save the token - you'll use it in the next step**

---

### Step 4️⃣ - Send Test Notification via curl

Open terminal and run:

```bash
curl -X POST \
  https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "title": "FacilityPro Test",
    "body": "This is a test notification from your facility management system",
    "data": {
      "test": "true",
      "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    },
    "channel": "fcm"
  }'
```

**Replace:**
- `YOUR_JWT_TOKEN` - The token from Step 3
- `YOUR_USER_ID` - The user ID from Step 2

**✅ Expected Response:**
```json
{
  "success": true,
  "logs": [
    {
      "user_id": "abc123...",
      "channel": "fcm",
      "status": "sent",
      "error_message": null,
      "sent_at": "2026-04-22T00:55:59.000Z"
    }
  ]
}
```

**If you get `"status": "failed"`:**
- Check the `error_message` field
- Common errors:
  - `"messaging/registration-token-not-registered"` = Token is invalid
  - `"Invalid credential"` = Firebase service account issue

---

### Step 5️⃣ - Verify Delivery

#### On the Device ✅
1. Look at the Android device notification panel
2. You should see a notification with title "FacilityPro Test"
3. Tap the notification to open the app
4. Notification should appear within 5-10 seconds

#### In the Database ✅
Query the notification logs:
```sql
SELECT 
  id,
  user_id,
  channel,
  status,
  error_message,
  sent_at,
  created_at
FROM notification_logs
WHERE created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC
LIMIT 10;
```

You should see:
- `channel` = `'fcm'`
- `status` = `'sent'`
- `error_message` = `null`

---

## 🎯 Quick Verification Checklist

| Check | Query | Expected |
|-------|-------|----------|
| **Token exists?** | `SELECT * FROM push_tokens WHERE is_active = true;` | Token found, `is_active=true` |
| **Function worked?** | `curl` command response | `"status": "sent"` |
| **Firebase OK?** | notification_logs status | `"status": "sent"`, no error |
| **Device received?** | Check notification tray | Notification appears in 5-10s |

---

## ❌ Troubleshooting

### "curl: 401 Unauthorized"
- **Cause:** JWT token is invalid or expired
- **Fix:** Get a fresh token from browser console or CLI

### "curl: 404 Not Found"
- **Cause:** Wrong Edge Function URL
- **Fix:** Use exact URL: `https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification`

### Response shows `"status": "failed"`
- **Check:** `error_message` in the response
- **Common causes:**
  - `"messaging/registration-token-not-registered"` → Token is dead (will auto-disable)
  - Firebase Admin SDK initialization failed → Check FIREBASE_SERVICE_ACCOUNT secret
  - Service account has no permissions → Check Firebase console

### Notification appears in logs but NOT on device
- Device may not have internet (but somehow sent the token)
- Check device's notification settings (app may be muted)
- Try toggling airplane mode on/off
- Restart the app on device

### No entry in notification_logs
- Edge Function may have crashed
- Check Supabase function logs: https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/functions/send-notification

---

## 🚀 Testing Real Scenarios

### Test 1: Basic Notification
```json
{
  "user_id": "USER_ID",
  "title": "Hello Guard",
  "body": "Test notification",
  "channel": "fcm"
}
```

### Test 2: With Action Data
```json
{
  "user_id": "USER_ID",
  "title": "Panic Alert",
  "body": "Emergency reported in Zone A",
  "data": {
    "action": "panic_alert",
    "zone": "zone-a",
    "severity": "high"
  },
  "channel": "fcm"
}
```

### Test 3: Visitor Approval
```json
{
  "user_id": "USER_ID",
  "title": "New Visitor Request",
  "body": "Approve visitor entry for John Smith",
  "data": {
    "action": "visitor_approval",
    "visitor_id": "visitor-123",
    "approval_required": "true"
  },
  "channel": "fcm"
}
```

---

## 📊 Success Indicators

✅ **Full Success:**
1. Curl response shows `"status": "sent"`
2. Entry appears in notification_logs with `status = 'sent'`
3. Notification appears on device within 10 seconds
4. User can tap and open the app

✅ **Partial Success (Token Issue):**
1. Curl response shows `"status": "failed"`
2. Error: `"messaging/registration-token-not-registered"`
3. Token gets auto-disabled in database
4. Fix: User needs to close and reopen app to get new token

✅ **Infrastructure Working:**
1. Edge Function responds (no 500 error)
2. Database logs created (notification_logs updated)
3. Even if device doesn't receive, infrastructure is OK

---

## 🔐 Key Details for Testing

- **Firebase Project:** facilitypro-81bde
- **Sender ID:** 675663268881
- **Edge Function:** `send-notification` (version 8)
- **Supabase Project:** wwhbdgwfodumognpkgrf
- **Database Tables:**
  - `push_tokens` - Device tokens
  - `notification_logs` - Delivery history
  - `users` - User profiles

---

## 💡 Pro Tips

1. **Always check push_tokens FIRST** - if no token, notification can't be sent
2. **Curl response tells you if Edge Function worked** - check status field
3. **notification_logs tells you if Firebase accepted it** - check status and error_message
4. **Device notification may take 5-10 seconds** - be patient before declaring failure
5. **Expired tokens are auto-disabled** - user will get new token on app restart

---

## 📌 Bookmark These URLs

- **Supabase SQL Editor:** https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/sql/new
- **Edge Function Logs:** https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/functions/send-notification
- **Database Viewer:** https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/editor/18 (push_tokens table)
