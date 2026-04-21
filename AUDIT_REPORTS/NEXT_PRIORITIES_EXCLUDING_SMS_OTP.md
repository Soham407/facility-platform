# Next Priorities (Excluding SMS/OTP Authentication)
**Date:** April 21, 2026  
**Question:** "So except SMS/OTP what next thing to do?"

---

## TL;DR - Quick Answer

After SMS/OTP implementation, do these 5 things in order:

| # | Priority | Task | Effort | Timeline | Owner |
|---|----------|------|--------|----------|-------|
| 1️⃣ | 🔴 CRITICAL | Push Notifications (FCM/APNs) | HIGH (1-2 wks) | Week 2-3 | Backend |
| 2️⃣ | 🔴 CRITICAL | Real Device Testing | MEDIUM (3-5 days) | Week 2-3 | QA/Mobile |
| 3️⃣ | 🟢 EASY ⭐ | Database Migrations | LOW (1 day) | **THIS WEEK** | Backend |
| 4️⃣ | 🟡 HIGH | E2E Test Infrastructure | MEDIUM (3-5 days) | Week 3-4 | QA |
| 5️⃣ | 🔴 CRITICAL | Admin/Ops Readiness | MEDIUM (1 week) | Week 3-4 | Operations |

---

## 1️⃣ PRIORITY 1: Push Notifications (FCM/APNs)

### Status: 🔴 CRITICAL BLOCKER
Residents won't get visitor notifications without this

### What To Do

#### A. Configure Firebase Cloud Messaging (FCM)
- Set up Firebase project for Android push notifications
- Effort: **3 days**
- Owner: Backend engineer

Steps:
1. Go to Firebase Console (https://console.firebase.google.com)
2. Create/select project for this facility platform
3. Generate Android API key
4. Configure FCM in app
5. Test message delivery

#### B. Configure Apple Push Notifications (APNs)
- Set up for iOS push notifications (if supporting iOS)
- Effort: **3 days**
- Owner: Backend engineer

Steps:
1. Create APNs certificate in Apple Developer
2. Upload to Supabase
3. Configure APNs provider
4. Test message delivery

#### C. Test Visitor Approval Notification
- When guard creates visitor → resident gets notification
- Effort: **2 days**
- Owner: QA + Mobile engineer

Test scenarios:
- Notification appears immediately after visitor created
- Notification content is correct
- Tapping notification opens visitors list
- Works on multiple devices

#### D. Test Panic Escalation Notification
- When guard triggers panic → supervisor notified
- Effort: **2 days**
- Owner: QA + Mobile engineer

Test scenarios:
- Panic alert sent immediately
- Supervisor receives notification
- Includes location info
- Can be marked as resolved

#### E. Test Notification Tap Routing
- Clicking notification opens correct screen
- Effort: **1 day**
- Owner: QA

### Why This Is #1
- If notifications don't work → app is useless for residents
- Residents won't know about visitors
- Supervisors won't get alerts

### Timeline
- Start: Week 1 (can run parallel with SMS/OTP)
- Complete: End of Week 2
- Blocks: E2E testing

### Files to Monitor
```
Solvesxx_mobile/src/lib/notificationService.ts
Solvesxx_web/lib/notificationService.ts
Solvesxx_mobile/src/providers/NotificationProvider.tsx
```

---

## 2️⃣ PRIORITY 2: Real Device Testing

### Status: 🔴 CRITICAL BLOCKER
Unknown behavior in production environment

### What To Do

#### A. Test Camera Permissions
- Guard needs to capture visitor photos on real device
- Effort: **2 days**
- Owner: QA + Mobile engineer

Test scenarios:
- User denies permission → app handles gracefully
- User grants permission → camera opens
- Photo capture works
- Photo upload succeeds
- Test on 2+ Android devices

#### B. Test GPS Tracking on Real Device
- Guard needs location tracking
- Effort: **2 days**
- Owner: QA + Mobile engineer

Test scenarios:
- GPS initializes and captures location
- Accuracy is acceptable (within 50m)
- Battery drain is reasonable
- Works both foreground and background
- Location updates in real-time

#### C. Test Network Loss Scenarios
- App should handle network disconnects
- Effort: **1 day**
- Owner: QA

Test scenarios:
- App behavior with no network (airplane mode)
- App recovery when network returns
- Queued actions sync correctly
- No data loss

#### D. Test App Lifecycle Events
- App should handle various lifecycle states
- Effort: **2 days**
- Owner: QA + Mobile engineer

Test scenarios:
- Fresh install → first login works
- App in background → location still tracked
- App resumed → state preserved
- Force close → app restarts cleanly

#### E. Real Device Testing - Android
- Full end-to-end testing on real devices
- Effort: **3 days**
- Owner: QA + Mobile engineer

Requirements:
- Test on 2+ physical Android devices
- Complete full workflows
- Document any issues
- Verify fixes

### Why This Is #2
- Can run in parallel with notifications setup
- Identifies hardware/OS issues early
- Only way to truly validate production readiness

### Timeline
- Start: Week 1 (get devices ordered)
- Execute: Week 2-3
- Complete: End of Week 3

### Devices Needed
- 2+ Android physical devices (different models if possible)
- Request from procurement immediately

---

## 3️⃣ PRIORITY 3: Database Migration Deployment

### Status: 🟢 EASY - DO THIS FIRST! ⭐

This is the **quickest win** - only 1 day, no dependencies, highest ROI

### What To Do

Deploy 4 migrations to production Supabase:

1. **20260421131717_guard_gps_tracking.sql**
   - Creates guard_gps_tracking table
   - Stores real-time guard locations

2. **20260421131800_guard_panic_alerts.sql**
   - Creates guard_panic_alerts table
   - Logs panic/SOS events

3. **20260421131850_guard_photo_storage.sql**
   - Creates visitor_photo_metadata table
   - Creates checklist_photo_evidence table

4. **20260421131900_guard_rpc_functions.sql**
   - Creates 6 backend RPC functions
   - APIs for mobile app

### Step-by-Step Deployment

```bash
# Step 1: Navigate to project
cd /Volumes/Soham/untitled\ folder/facility-platform/Solvesxx_web

# Step 2: Verify files exist
ls -la supabase/migrations/ | grep "202604"

# Step 3: Check connection
supabase status

# Step 4: Create backup (IMPORTANT!)
# Go to Supabase Dashboard → Settings → Backups → "Back up now"

# Step 5: Test locally first
supabase db reset

# Step 6: Preview changes
supabase db push --dry-run

# Step 7: Deploy to production
supabase db push

# Step 8: Verify in Supabase Dashboard
# Check: Table Editor shows new tables
# Check: SQL Editor shows new functions
```

### Verification Checklist

After deployment, verify:
- [ ] 4 new tables created in production
- [ ] 6 RPC functions accessible
- [ ] RLS policies enforced
- [ ] No data corruption
- [ ] Unit tests still pass

### Why This Is #3 (But Can Do Today!)
- Highest ROI: 1 day for production feature
- Independent: doesn't depend on auth/notifications
- Unblocks: guard features in production
- Can be done immediately

### Timeline
- Start: **THIS WEEK** (today/tomorrow)
- Complete: 1 day
- No blockers

### Effort
- **LOW: Only 1 day**
- No complexity
- Well-tested migrations

---

## 4️⃣ PRIORITY 4: E2E Test Infrastructure

### Status: 🟡 HIGH PRIORITY

Full workflow validation before release

### What To Do

#### A. Fix E2E Test Environment
- Resolve npm module path issues
- Get tests running locally
- Effort: **2 days**

#### B. Run Full E2E Test Suite
- Execute all guard/resident workflows
- Effort: **1 day**

#### C. Add OTP Auth Tests
- Add SMS/OTP flow to automated tests
- Effort: **2 days**

#### D. Add Notification Tests
- Add push notification delivery tests
- Effort: **2 days**

### Why This Is #4
- Validates all features work together
- Catches integration issues
- Requires #1 (notifications) ready first

### Timeline
- Start: Week 3
- Complete: Week 4

---

## 5️⃣ PRIORITY 5: Admin/Ops Readiness

### Status: 🔴 CRITICAL BLOCKER

Support team needs documented procedures

### What To Do

#### A. Validate Resident Onboarding
- Create resident on web
- Link to flat/building
- Assign to user account
- Effort: **2 days**

#### B. Validate Guard Assignment
- Create guard on web
- Assign to location/shift
- Activate guard
- Effort: **2 days**

#### C. Admin Troubleshooting Procedures
- Document: How to fix broken resident mapping
- Document: How to fix broken guard assignment
- Document: Emergency data recovery
- Effort: **1 day**

#### D. Visitor & Panic Data Inspection
- Verify: Visitor records visible from web
- Verify: Panic alerts queryable
- Verify: Support can find/fix data
- Effort: **1 day**

### Why This Is #5
- Most features must work first
- Support team needs training
- Can happen in parallel with testing

### Timeline
- Start: Week 3
- Complete: Week 4

---

## 📅 Week-by-Week Execution Plan

### WEEK 1 (This Week)
```
Monday:
  □ Deploy database migrations (1 day)
  □ Backup production database

Tuesday-Thursday:
  □ Start FCM/APNs configuration
  □ Order Android test devices (2+ units)
  □ Get Firebase Console access

Friday:
  □ Verify migrations deployed
  □ Confirm FCM/APNs setup begun
  □ Device procurement confirmed
```

### WEEK 2
```
Mon-Wed:
  □ Complete FCM configuration
  □ Complete APNs configuration

Thu-Fri:
  □ Test visitor notifications (2 days)
  □ Test panic notifications (2 days)
  □ Begin Android device testing
```

### WEEK 3
```
Mon-Tue:
  □ Complete real device testing
  □ Document hardware findings

Wed-Thu:
  □ Fix E2E test environment
  □ Begin admin workflow validation

Fri:
  □ Run full E2E test suite
```

### WEEK 4
```
Mon-Tue:
  □ Add OTP auth tests to E2E
  □ Add notification tests to E2E

Wed-Thu:
  □ Complete admin procedures documentation
  □ Final verification testing

Fri:
  □ All systems ready for release
```

---

## 👥 Team Assignments

### Backend Engineer
- Deploy database migrations (1 day)
- Configure FCM (3 days)
- Configure APNs (3 days)
- Test notification delivery (2 days)
- **Total: ~1.5 weeks**

### Mobile/QA Engineer
- Test on Android devices (5 days)
- Document hardware findings (1 day)
- Test notifications on real devices (3 days)
- **Total: ~1.5 weeks**

### QA Engineer
- Fix E2E test environment (2 days)
- Run full test suite (1 day)
- Add auth tests (2 days)
- Add notification tests (2 days)
- **Total: ~1 week**

### Operations/Admin
- Validate resident onboarding (2 days)
- Validate guard assignment (2 days)
- Document troubleshooting (1 day)
- Data inspection setup (1 day)
- **Total: ~1 week**

---

## 🎯 Immediate Next Steps (Today/Tomorrow)

### Priority 1: Deploy Migrations (1 Day Task)
```bash
cd Solvesxx_web
supabase db push
```

### Priority 2: Order Test Devices
- Get 2+ Android devices from procurement
- Budget: ~$2-3K
- Timeline: 1-2 weeks delivery

### Priority 3: Get Firebase Access
- Request Firebase Console access
- Request Apple Developer access
- Timeline: 1-2 days for credentials

### Priority 4: Schedule Team Meeting
- Assign task owners
- Confirm timelines
- Allocate resources

---

## ⏱️ Total Timeline (All Tasks)

| Task | Duration | Start | Complete |
|------|----------|-------|----------|
| SMS/OTP Auth | 1-2 weeks | Week 1 | Week 2 |
| Push Notifications | 1-2 weeks | Week 1 | Week 2 |
| Device Testing | 3-5 days | Week 2 | Week 3 |
| Migrations | 1 day | **Today** | **Today** |
| E2E Tests | 3-5 days | Week 3 | Week 4 |
| Admin/Ops | 1 week | Week 3 | Week 4 |
| **Total** | **4 weeks** | **This Week** | **Mid-May** |

**Critical Path:** 3-4 weeks (with parallel work)  
**Target Release:** Mid-May 2026

---

## 📊 Success Criteria

Before release, all of these must be TRUE:

✅ Migrations deployed to production  
✅ Push notifications working end-to-end  
✅ Hardware tested on real devices  
✅ E2E tests passing  
✅ Admin workflows validated  
✅ Documentation complete  
✅ No critical bugs remaining  
✅ Performance acceptable  
✅ Support team trained  
✅ Backup procedures documented  

---

## 🚨 Risk Mitigation

### High Risk Items
- **Hardware incompatibilities**: Mitigate with early device testing
- **Notification delivery failures**: Mitigate with staging validation
- **Migration issues**: Mitigate with backup + dry-run

### Contingency Plans
- Device issues? → Have backup devices ready
- Notification provider down? → Have failover plan
- Migration fails? → Restore from backup

---

## 📞 Questions?

For each task, review:
1. The detailed task breakdown above
2. Team member assignments
3. Timeline and dependencies
4. Success criteria

If blocked:
- Check dependencies
- Contact team lead
- Escalate if critical

---

**Report Generated:** 2026-04-21  
**Status:** Ready for execution  
**Confidence:** High (based on codebase analysis)
