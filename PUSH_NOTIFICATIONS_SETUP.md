# 🔔 Push Notifications Implementation Guide

**Date:** April 22, 2026
**Project:** FacilityPro Mobile & Web
**Status:** Starting Configuration Phase

---

## 📋 Overview

This document guides you through setting up Firebase Cloud Messaging (FCM) for push notifications to residents and guards.

### Current State
✅ Firebase project created: **facilitypro-81bde**
✅ Android app registered: **com.facilitypro.mobile**
✅ google-services.json in codebase
✅ Supabase Edge Function ready: `send-notification`
✅ Mobile notification SDK installed

### What Will Be Done
- Verify Firebase configuration
- Test Edge Function with real tokens
- Test on physical Android device
- Verify visitor notification flow
- Verify panic alert flow
- (Optional) Setup APNs for iOS

---

## ⏰ Timeline

| Phase | Task | Duration | Dependencies |
|-------|------|----------|--------------|
| 1 | Firebase Verification | 30 min | Firebase console access |
| 2 | Service Account Setup | 15 min | Phase 1 complete |
| 3 | Supabase Configuration | 10 min | Firebase service account |
| 4 | Edge Function Testing | 30 min | Phase 3 complete |
| 5 | Mobile Integration | 2-3 hours | Android device + APK |
| 6 | E2E Testing | 1 hour | All above complete |
| **Total** | | **4-5 hours** | Can run in parallel |

---

## 🚀 Phase 1: Firebase Console Verification (30 min)

### Task 1.1: Access Firebase Console
1. Open https://console.firebase.google.com
2. Log in with your Firebase account
3. Select project **facilitypro-81bde**
4. Bookmark this page for easy access

### Task 1.2: Verify Cloud Messaging
1. In left sidebar under "Messaging", click "Cloud Messaging"
2. **VERIFY:** Status shows "Enabled"
3. **NOTE:** Server API Key (will need this if generating new service account)
4. **VERIFY:** Sender ID = 675663268881 (matches google-services.json)

### Task 1.3: Verify Android App Registration
1. In left sidebar, click "Project Settings" (gear icon)
2. Go to "General" tab → scroll to "Your apps"
3. **VERIFY:** App listed as "com.facilitypro.mobile" (Android)
4. **VERIFY:** google-services.json link available (if needed to download)

### Task 1.4: Check Service Account
1. In "Project Settings", click "Service Accounts" tab
2. Click "Firebase Admin SDK"
3. **VERIFY:** Service account email visible: `firebase-adminsdk-*@facilitypro-81bde.iam.gserviceaccount.com`
4. **OPTION A (if key exists):** "Existing keys" shown
5. **OPTION B (if key missing):** Click "Generate New Private Key" button

**Output from Phase 1:** ✅ / ⚠️ / ❌ - Firebase is ready / needs attention / blocked

---

## 🔑 Phase 2: Service Account Key Setup (15 min)

**Prerequisites:** Phase 1 completed with ✅ status

### Task 2.1: Check Current Service Account
1. Run this command in terminal:
```bash
cd /Volumes/Soham/untitled\ folder/facility-platform/Solvesxx_web
supabase secrets list | grep FIREBASE
```

2. **VERIFY:** You see output like:
```
FIREBASE_SERVICE_ACCOUNT  | [hash]
```

### Task 2.2: Generate New Key (if needed)
1. In Firebase Console, Project Settings → Service Accounts
2. Click "Generate new private key"
3. Browser downloads `facilitypro-81bde-[timestamp].json`
4. Open this file and verify it has:
   - `"type": "service_account"`
   - `"project_id": "facilitypro-81bde"`
   - `"private_key": "-----BEGIN PRIVATE KEY-----..."`

### Task 2.3: Update Supabase Secret (if key changed)
1. Run this command:
```bash
cd /Volumes/Soham/untitled\ folder/facility-platform/Solvesxx_web

# Copy the full JSON content from the downloaded file
# Then run:
supabase secrets set FIREBASE_SERVICE_ACCOUNT='<paste-full-json-here>'
```

2. **VERIFY:** Command succeeds with message like "Successfully updated secret"

**Output from Phase 2:** ✅ Service account verified / 🔄 Updated with new key

---

## ⚙️ Phase 3: Supabase Configuration (10 min)

**Prerequisites:** Phase 2 completed

### Task 3.1: Verify Edge Function Secrets
1. Run:
```bash
supabase secrets list
```

2. **VERIFY** you see all three:
   - ✅ FIREBASE_SERVICE_ACCOUNT
   - ✅ SUPABASE_URL  
   - ✅ SUPABASE_ANON_KEY

### Task 3.2: Set ALLOWED_ORIGIN (for CORS)
1. Run:
```bash
# For local testing:
supabase secrets set ALLOWED_ORIGIN='http://127.0.0.1:3000'

# For production (later):
# supabase secrets set ALLOWED_ORIGIN='https://your-domain.com'
```

2. **VERIFY:** Command succeeds

### Task 3.3: Deploy Edge Function
1. Run:
```bash
cd Solvesxx_web
supabase functions deploy send-notification
```

2. **VERIFY:** Output shows "Deployed successfully" or similar

**Output from Phase 3:** ✅ All secrets configured and function deployed

---

## 🧪 Phase 4: Edge Function Testing (30 min)

**Prerequisites:** Phase 3 completed

### Task 4.1: Test with Curl Command
1. You need:
   - A valid push token (from mobile app or test)
   - A valid JWT token from your test user
   - Your Supabase URL

2. Run this test:
```bash
# Get your JWT (from mobile app test or use a test user's token)
JWT_TOKEN="<your-jwt-token>"
SUPABASE_URL="https://wwhbdgwfodumognpkgrf.supabase.co"
PUSH_TOKEN="<test-push-token>"

curl -X POST "${SUPABASE_URL}/functions/v1/send-notification" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"<user-uuid>\",
    \"title\": \"Test Notification\",
    \"body\": \"This is a test from Firebase\",
    \"channel\": \"fcm\"
  }"
```

3. **EXPECTED RESPONSE:**
```json
{
  "results": [
    {
      "success": true,
      "messageId": "0:...",
      "channel": "fcm"
    }
  ]
}
```

4. **VERIFY:** No 401 / 403 errors (auth is working)

### Task 4.2: Check Logs
1. In Supabase Dashboard → Edge Functions → send-notification
2. Click "Logs" tab
3. **VERIFY:** Recent function invocation shows (within last 5 min)
4. **CHECK:** No error messages in logs

**Output from Phase 4:** ✅ Function executes without errors / ❌ Debug logs show issue

---

## 📱 Phase 5: Mobile Integration Testing (2-3 hours)

**Prerequisites:** Phase 4 completed

### Task 5.1: Build Test APK
```bash
cd Solvesxx_mobile
npm install
npm run build:android
```

This creates: `Solvesxx_mobile/android/app/build/outputs/apk/release/app-release.apk`

### Task 5.2: Install on Physical Device
1. Connect Android device via USB
2. Run: `adb install Solvesxx_mobile/android/app/build/outputs/apk/release/app-release.apk`
3. Launch app: "FacilityPro" or "Solvesxx"
4. **VERIFY:** App launches without crashes

### Task 5.3: Test Push Token Registration
1. Login with test user credentials
2. **VERIFY:** App requests notification permission
3. Grant permission when prompted
4. **VERIFY:** App shows "Notifications enabled" or similar

### Task 5.4: Test Notification Receipt
1. Use web dashboard or API to send test notification
2. **VERIFY:** Notification appears on device within 5 seconds
3. **VERIFY:** Notification can be tapped/opened
4. **VERIFY:** Tapping opens correct screen (e.g., visitors list)

### Task 5.5: Test Visitor Approval Notification
1. Create visitor via web admin
2. Approve visitor as guard/supervisor
3. **VERIFY:** Resident receives notification on mobile
4. **VERIFY:** Notification says "Visitor Approved"
5. **VERIFY:** Tapping notification shows visitor details

### Task 5.6: Test Panic Alert Notification
1. Trigger panic/SOS from guard mobile app
2. **VERIFY:** Supervisors receive notification
3. **VERIFY:** Notification includes location info
4. **VERIFY:** Tapping marks as acknowledged

**Output from Phase 5:** ✅ All notifications work end-to-end / ⚠️ Partial success (specify which)

---

## 📲 Phase 6: APNs Setup for iOS (Optional - 1 hour)

**Only do this if supporting iOS**

### Task 6.1: Create APNs Certificate
1. Go to https://developer.apple.com → Account
2. Go to "Certificates, Identifiers & Profiles"
3. Create new "Apple Push Notification service SSL Certificate"
4. Follow Apple's steps to create
5. Download as `.p8` file

### Task 6.2: Upload to Firebase
1. Firebase Console → Cloud Messaging
2. Click "APNs Authentication Key"
3. Upload `.p8` file
4. **VERIFY:** Certificate shows as valid

### Task 6.3: Test on iOS
1. Build iOS app: `npm run build:ios`
2. Run on iPhone simulator or real device
3. Send test notification
4. **VERIFY:** Notification appears

---

## ✅ Final Verification Checklist

Before marking as complete, verify:

- [ ] Firebase Cloud Messaging is Enabled
- [ ] Service account configured in Supabase
- [ ] ALLOWED_ORIGIN set correctly
- [ ] send-notification function deployed
- [ ] Function executes without auth errors
- [ ] Push notification received on Android device
- [ ] Visitor approval notification works end-to-end
- [ ] Panic alert notification works end-to-end
- [ ] Notification tap-to-navigate works
- [ ] Multiple devices tested (if 2+ available)
- [ ] (Optional) iOS APNs configured and tested

---

## 🚨 Troubleshooting

### Problem: Function returns 401 Unauthorized
**Cause:** JWT token invalid or expired
**Solution:** 
- Use freshly generated JWT
- Verify token has correct user_id
- Check SUPABASE_ANON_KEY matches

### Problem: Notification not received on device
**Cause:** 1) Device not registered for FCM, 2) Token invalid, 3) FCM down
**Solution:**
- Check push_tokens table for device
- Verify token is marked is_active=true
- Check device internet connection
- Wait 5-10 seconds (network latency)

### Problem: Firebase project shows "Disabled"
**Cause:** Cloud Messaging not enabled in project
**Solution:**
- Go to Firebase Console
- Click "Cloud Messaging"
- Click "Enable Cloud Messaging"
- Wait 1-2 minutes

### Problem: Service account auth fails
**Cause:** Service account JSON invalid or corrupted
**Solution:**
- Generate fresh private key
- Copy entire JSON to Supabase secret
- Verify no extra spaces or line breaks
- Redeploy function

---

## 📊 Success Criteria

✅ **COMPLETE** when:
1. Firebase project verified and working
2. Edge Function can send notifications
3. Real Android device receives notifications
4. Visitor flow notifications work
5. Panic alert notifications work
6. All taps navigate correctly

🎉 **Then Release-Ready!**

---

## 📞 Next Steps

After Phase 5 completion:
1. Real device testing with QA team
2. E2E test suite for notifications
3. Performance testing under load
4. Release documentation
5. Production deployment

