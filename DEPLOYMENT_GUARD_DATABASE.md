# Guard Role Database Migration Deployment Guide

**Status:** 4 new migrations ready to deploy  
**Date:** 2026-04-21  
**Supabase Project:** wwhbdgwfodumognpkgrf

---

## What's Being Deployed

Four new database migrations to support guard role features:

1. **GPS Tracking** - Real-time location during shifts
2. **Panic Alerts** - SOS button event logging
3. **Photo Storage** - Visitor and checklist photo metadata
4. **RPC Functions** - Backend APIs for mobile app

---

## Migration Files

Located in: `Solvesxx_web/supabase/migrations/`

| Timestamp | File | Tables | Functions |
|-----------|------|--------|-----------|
| 20260421131717 | guard_gps_tracking.sql | guard_gps_tracking | - |
| 20260421131800 | guard_panic_alerts.sql | guard_panic_alerts | - |
| 20260421131850 | guard_photo_storage.sql | visitor_photo_metadata, checklist_photo_evidence | - |
| 20260421131900 | guard_rpc_functions.sql | - | 6 RPC functions |

---

## Pre-Deployment Checklist

- [ ] Backup current Supabase database
- [ ] Verify `employees` table exists (guard references)
- [ ] Verify `residents` table exists (resident references)
- [ ] Verify `shifts` table exists (shift context)
- [ ] Verify `checklist_items` table exists (checklist references)
- [ ] Verify `visitors` table exists (visitor references)
- [ ] Verify `roles` table exists (RLS policy checks)
- [ ] Network access to Supabase project

---

## Deployment Steps

### Step 1: Navigate to project directory

```bash
cd /Volumes/Soham/untitled\ folder/facility-platform/Solvesxx_web
```

### Step 2: Verify migrations are present

```bash
ls supabase/migrations/ | grep "20260421"
```

Expected output:
```
20260421131717_guard_gps_tracking.sql
20260421131800_guard_panic_alerts.sql
20260421131850_guard_photo_storage.sql
20260421131900_guard_rpc_functions.sql
```

### Step 3: Check Supabase link status

```bash
supabase status
```

Should show project ref: `wwhbdgwfodumognpkgrf`

### Step 4: (Optional) Test locally first

```bash
supabase db reset
```

This applies all migrations locally to catch any issues.

### Step 5: Deploy to production

```bash
supabase db push
```

The CLI will:
1. Compare local migrations with remote
2. Show which new migrations will be applied
3. Apply them in order to the remote database

**Expected output:**
```
Remote database linked to project wwhbdgwfodumognpkgrf
Applying migration 20260421131717...
Applying migration 20260421131800...
Applying migration 20260421131850...
Applying migration 20260421131900...
✓ All migrations applied successfully
```

---

## Post-Deployment Verification

### Verify Tables Created

```bash
supabase db schema
```

Should show these new tables:
- `guard_gps_tracking`
- `guard_panic_alerts`
- `visitor_photo_metadata`
- `checklist_photo_evidence`

### Verify Functions Created

Access Supabase Dashboard:
1. Go to SQL Editor
2. Run: `SELECT proname FROM pg_proc WHERE proname LIKE 'record_guard%' OR proname LIKE 'trigger_panic%' OR proname LIKE 'acknowledge_panic%' OR proname LIKE 'resolve_panic%' OR proname LIKE 'get_%';`

Should return:
- record_guard_gps_tracking
- trigger_panic_alert
- acknowledge_panic_alert
- resolve_panic_alert
- get_active_panic_alerts
- get_guard_location_history

### Test RPC Function Calls

In Supabase Dashboard SQL Editor, test each function:

```sql
-- Test 1: GPS tracking
SELECT record_guard_gps_tracking(
  'employee-uuid-here'::uuid,
  19.0760::numeric,
  72.8777::numeric,
  10
);

-- Test 2: Panic alert
SELECT trigger_panic_alert(
  'employee-uuid-here'::uuid,
  19.0760::numeric,
  72.8777::numeric
);

-- Test 3: Get active alerts
SELECT * FROM get_active_panic_alerts();

-- Test 4: Location history
SELECT * FROM get_guard_location_history('employee-uuid-here'::uuid, 24);
```

---

## Rollback Procedure

If deployment fails or issues are found:

### Option 1: Full Reset (Local Testing)

```bash
cd Solvesxx_web
supabase db reset
```

This removes all changes and reapplies migrations from start.

### Option 2: Manual Rollback (Production)

**WARNING:** Only if necessary. Contact Supabase support first.

```bash
-- Drop new functions
DROP FUNCTION IF EXISTS record_guard_gps_tracking CASCADE;
DROP FUNCTION IF EXISTS trigger_panic_alert CASCADE;
DROP FUNCTION IF EXISTS acknowledge_panic_alert CASCADE;
DROP FUNCTION IF EXISTS resolve_panic_alert CASCADE;
DROP FUNCTION IF EXISTS get_active_panic_alerts CASCADE;
DROP FUNCTION IF EXISTS get_guard_location_history CASCADE;

-- Drop new tables
DROP TABLE IF EXISTS guard_gps_tracking CASCADE;
DROP TABLE IF EXISTS guard_panic_alerts CASCADE;
DROP TABLE IF EXISTS visitor_photo_metadata CASCADE;
DROP TABLE IF EXISTS checklist_photo_evidence CASCADE;
```

---

## Storage Bucket Setup

After migrations are deployed, create and configure Supabase storage buckets:

### Bucket 1: visitor-photos

```bash
# Via Supabase Dashboard:
1. Go to Storage
2. Click "Create bucket"
3. Name: visitor-photos
4. Public: Yes (to generate URLs for resident approval)
5. Click Create
```

Then add RLS policy:
```sql
-- Allow guards to upload visitor photos
CREATE POLICY "Guards can upload visitor photos"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'visitor-photos'
  AND auth.uid() = (SELECT user_id FROM employees WHERE id = (auth.uid()))
);

-- Allow anyone with URL to view (public photos)
CREATE POLICY "Public read access to visitor photos"
ON storage.objects FOR SELECT
USING (bucket_id = 'visitor-photos');
```

### Bucket 2: checklist-evidence

```bash
# Via Supabase Dashboard:
1. Go to Storage
2. Click "Create bucket"
3. Name: checklist-evidence
4. Public: No (private, for managers only)
5. Click Create
```

Then add RLS policy:
```sql
-- Allow guards to upload
CREATE POLICY "Guards can upload checklist photos"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (
  bucket_id = 'checklist-evidence'
  AND auth.uid() = (SELECT user_id FROM employees WHERE id = (auth.uid()))
);

-- Allow managers to read
CREATE POLICY "Managers can read checklist photos"
ON storage.objects FOR SELECT TO authenticated
USING (
  bucket_id = 'checklist-evidence'
  AND EXISTS (
    SELECT 1 FROM employees e
    WHERE e.user_id = auth.uid()
    AND e.role_id IN (SELECT id FROM roles WHERE name IN ('society_manager', 'security_supervisor'))
  )
);
```

---

## Mobile App Integration

After deployment, the mobile app can use these functions:

### GPS Tracking (GuardHomeScreen.tsx)
```typescript
const gpsSyncResult = await mobileBackend.rpc('record_guard_gps_tracking', {
  p_guard_id: guardId,
  p_latitude: location.coords.latitude,
  p_longitude: location.coords.longitude,
  p_accuracy_meters: location.coords.accuracy,
  p_is_within_fence: isWithinFence,
  p_shift_id: shiftId
});
```

### Panic Alert (PanicButton.tsx)
```typescript
const alertResult = await mobileBackend.rpc('trigger_panic_alert', {
  p_guard_id: guardId,
  p_latitude: location.coords.latitude,
  p_longitude: location.coords.longitude,
  p_shift_id: shiftId
});
```

### Manager Dashboard (Web)
```typescript
// Fetch active alerts
const activeAlerts = await supabase.rpc('get_active_panic_alerts');

// Fetch guard location history
const locationHistory = await supabase.rpc('get_guard_location_history', {
  p_guard_id: guardId,
  p_hours_back: 24
});

// Acknowledge alert
await supabase.rpc('acknowledge_panic_alert', {
  p_alert_id: alertId,
  p_acknowledged_by: managerId
});
```

---

## Troubleshooting

### Error: "relation 'employees' does not exist"

**Cause:** Employee table missing or renamed  
**Fix:** Check that `employees` table exists in database

### Error: "relation 'guard_gps_tracking' already exists"

**Cause:** Migration already applied  
**Fix:** This is expected if pushing again. No action needed.

### Error: "function 'record_guard_gps_tracking' does not exist"

**Cause:** RPC function migration not applied  
**Fix:** Run `supabase db push` again to ensure migration 20260421131900 is applied

### Slow GPS queries on large datasets

**Cause:** Missing indexes or too much data  
**Fix:** Verify indexes were created and consider archiving old GPS data

### Photo uploads failing

**Cause:** Storage bucket RLS policies incorrect  
**Fix:** Check bucket policies in Supabase Dashboard → Storage → Policies

---

## Success Criteria

Deployment is successful when:

✅ All 4 migrations applied without errors  
✅ 4 new tables visible in database  
✅ 6 new RPC functions callable  
✅ RLS policies enforced (test with different user roles)  
✅ Storage buckets created with correct permissions  
✅ Mobile app GPS tracking calls succeed  
✅ Manager dashboard displays panic alerts  
✅ Location history queries return results  

---

## Support & Documentation

- **Supabase Dashboard:** https://app.supabase.com/projects/wwhbdgwfodumognpkgrf/editor
- **Database Schema Guide:** See DATABASE_SCHEMA_GUIDE.md
- **Mobile Implementation:** See Solvesxx_mobile/src/lib/gpsService.ts
- **Mobile RPC Usage:** See Solvesxx_mobile/src/lib/smsService.ts

---

**Deployment Ready:** 2026-04-21 13:20 IST  
**Contact:** Copilot Implementation Agent
