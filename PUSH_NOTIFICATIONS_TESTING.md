# Push Notifications Testing Guide - April 22, 2026

## ✅ COMPLETED SETUP
- [x] Firebase service account configured in Supabase
- [x] Cloud Messaging API V1 enabled
- [x] Edge Function `send-notification` deployed (version 8)
- [x] Metro bundler running on port 8081
- [x] Android APK built

## 📱 TESTING FLOW (Step by Step)

### Step 1: Create Demo User in Supabase
**Go to:** https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/sql/new

```sql
-- Create demo user with authenticated role
INSERT INTO auth.users (
  instance_id, id, aud, role, email, encrypted_password,
  email_confirmed_at, created_at, updated_at,
  raw_user_meta_data
) 
SELECT 
  '00000000-0000-0000-0000-000000000000',
  gen_random_uuid(), 'authenticated', 'authenticated',
  'demo@facilitypro.in', crypt('demo1234', gen_salt('bf')),
  NOW(), NOW(), NOW(),
  jsonb_build_object('phone', '+919876543210', 'first_name', 'Demo', 'last_name', 'User')
WHERE NOT EXISTS (SELECT 1 FROM auth.users WHERE email = 'demo@facilitypro.in');

-- Add to users table
INSERT INTO users (id, email, phone, first_name, last_name, role, status, created_at)
SELECT id, email, raw_user_meta_data->>'phone', 
  raw_user_meta_data->>'first_name', raw_user_meta_data->>'last_name',
  'resident', 'active', NOW()
FROM auth.users WHERE email = 'demo@facilitypro.in'
ON CONFLICT (id) DO NOTHING;

-- Verify
SELECT id, email FROM users WHERE email = 'demo@facilitypro.in';
```

### Step 2: Install APK on Android Device
```bash
# Your APK is already built at:
# Solvesxx_mobile/android/app/build/outputs/apk/release/app-release.apk

# Connect your Android device via USB and:
adb install -r Solvesxx_mobile/android/app/build/outputs/apk/release/app-release.apk

# Or use Android Studio's device manager to install
```

### Step 3: Launch App & Authenticate
1. Open FacilityPro app on device
2. Login with:
   - Email: `demo@facilitypro.in`
   - Password: `demo1234`
3. Allow push notification permissions when prompted
4. App will:
   - Get Expo push token from Firebase
   - Store token in `push_tokens` table
   - Subscribe to notification broadcasts

### Step 4: Send Test Notification via Edge Function

**Option A: Using curl (from any terminal)**
```bash
# Get a valid user JWT token first (from web app or API)
# Then send notification:

curl -X POST \
  https://wwhbdgwfodumognpkgrf.supabase.co/functions/v1/send-notification \
  -H "Authorization: Bearer YOUR_USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID_HERE",
    "title": "Test Notification",
    "body": "This is a test from push notifications system",
    "data": {
      "test_id": "test_001",
      "timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"
    },
    "channel": "fcm"
  }'
```

**Option B: Using Supabase Web Function UI**
1. Go to https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/functions/send-notification
2. Click "Test" or use the built-in API tester
3. Provide the JSON payload with user_id and message

**Option C: From Mobile App (if UI has test button)**
- Navigate to settings/debug menu
- Find "Send Test Notification" button
- Click and check device for incoming notification

### Step 5: Verify Notification Delivery
✅ **Check these on the device:**
- Notification appears in system tray
- App can be opened from notification tap
- Notification data is logged in `notification_logs` table

✅ **Check Supabase:**
```sql
-- View all sent notifications
SELECT * FROM notification_logs 
WHERE created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC;

-- View active tokens
SELECT user_id, token, is_active FROM push_tokens 
WHERE user_id = 'YOUR_USER_ID';
```

## 🔧 TROUBLESHOOTING

**Notification not received:**
1. Check if FCM token is registered: `SELECT * FROM push_tokens WHERE is_active = true;`
2. Check Firebase service account is valid (FIREBASE_SERVICE_ACCOUNT secret)
3. Check notification_logs for error messages
4. Verify app is running and has notification permissions

**Token not registering:**
1. Check if Expo push token request succeeded
2. Verify internet connectivity on device
3. Check app logs for Expo token errors

**Curl command 401 Unauthorized:**
1. Ensure you have a valid user JWT token (not service key)
2. Token must be for an authenticated user

## 📊 METRO & DEV SETUP

**Metro is currently running:**
```
Port: 8081
URL: exp+facilitypro-mobile://expo-development-client/?url=http://192.168.1.15:8081
QR Code displayed in terminal
```

**Commands in Metro Terminal:**
- `a` - Open on Android emulator/device
- `i` - Open on iOS simulator
- `r` - Reload app
- `m` - Toggle menu
- `?` - Show all commands

**To connect device to Metro:**
1. Scan the QR code with your device camera
2. Or use: `adb shell am start -a android.intent.action.VIEW -d "exp://192.168.1.15:8081"`

## 🎯 NEXT AFTER TESTING
1. Verify end-to-end notification delivery works
2. Test panic alert notifications
3. Test visitor approval notifications  
4. Test notification tapping and routing logic
5. Ready for real device production testing
