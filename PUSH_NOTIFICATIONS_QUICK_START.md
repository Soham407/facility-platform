# 🚀 Push Notifications Quick Start

## Your Firebase Project Details
```
Project Name: facilitypro-81bde
Project ID: facilitypro-81bde
Sender ID: 675663268881
Android Package: com.facilitypro.mobile
API Key: AIzaSyD9C78ZQ24pUmb_z9-DSzLb0fKfcLzu4TE
Console: https://console.firebase.google.com
```

## Current Infrastructure ✅
- Firebase Cloud Messaging: READY
- google-services.json: PRESENT
- Supabase Edge Function: DEPLOYED
- Service Account: CONFIGURED
- Mobile SDK: INSTALLED

## 5-Step Verification Process

### Step 1: Firebase Console Verification (15 min)
```
URL: https://console.firebase.google.com
Action: 
1. Select project "facilitypro-81bde"
2. Go to Cloud Messaging
3. Verify "Enabled" status
4. Note Server API Key
```

### Step 2: Verify Service Account (10 min)
```
In Firebase Console:
1. Settings (gear) → Service Accounts
2. Check firebase-adminsdk-*@facilitypro-81bde.iam.gserviceaccount.com exists
3. If missing, click "Generate new private key"
```

### Step 3: Update Supabase Secret (10 min)
```bash
# Download private key from Firebase → Project Settings → Service Accounts
# Copy entire JSON content
cd Solvesxx_web
supabase secrets set FIREBASE_SERVICE_ACCOUNT='<paste-json>'
supabase functions deploy send-notification
```

### Step 4: Test Edge Function (10 min)
```bash
# Test with curl
curl -X POST "https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-uuid>",
    "title": "Test",
    "body": "Test notification",
    "channel": "fcm"
  }'

# Expected response:
# {"results": [{"success": true, "messageId": "0:...", "channel": "fcm"}]}
```

### Step 5: Test on Real Device (2-3 hours)
```bash
# Build APK
cd Solvesxx_mobile
npm run build:android
adb install android/app/build/outputs/apk/release/app-release.apk

# Launch app, login, grant notification permission
# Send test notification from web dashboard
# Verify notification received and tap-to-open works
```

## Files to Reference

### Backend
- `Solvesxx_web/supabase/functions/send-notification/index.ts` - Edge Function
- `Solvesxx_web/lib/notificationService.ts` - Web notification service

### Mobile
- `Solvesxx_mobile/src/lib/notifications.ts` - Mobile notification handler
- `Solvesxx_mobile/google-services.json` - Firebase config
- `Solvesxx_mobile/android/app/google-services.json` - Android config

### Database
- `push_tokens` table - Stores device tokens
- `notification_queue` table - Queues notifications for sending
- `notifications` table - Stores sent notifications

## Environment Variables Needed

```
FIREBASE_SERVICE_ACCOUNT=<service-account-json>
ALLOWED_ORIGIN=http://127.0.0.1:3000 (for local testing)
SUPABASE_URL=https://wwhbdgwfodumognpkgrf.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
```

## Success Indicators

✅ Function returns 200 OK (not 401)
✅ Device receives notification within 5 seconds
✅ Tapping notification opens correct screen
✅ Multiple notifications can be sent consecutively
✅ Works with new and existing push tokens

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Bad JWT | Use fresh token, check user_id |
| Notification not received | Token invalid | Verify device registered, token is_active |
| FCM Disabled | Service not enabled | Enable Cloud Messaging in Firebase |
| Auth fails | Bad service account | Regenerate and upload to Supabase |
| CORS error | ALLOWED_ORIGIN not set | Run: supabase secrets set ALLOWED_ORIGIN='...' |

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Firebase Verification | 15 min | Ready |
| Service Account Setup | 10 min | Ready |
| Supabase Config | 10 min | Ready |
| Edge Function Test | 10 min | Ready |
| Mobile Integration | 2-3 hours | Needs real device |
| **TOTAL** | **4-5 hours** | **CAN START NOW** |

---

**Ready to start? Follow the detailed guide in PUSH_NOTIFICATIONS_SETUP.md**
