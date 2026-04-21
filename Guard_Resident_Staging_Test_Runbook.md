# Guard + Resident Staging Test Runbook

Updated: 2026-04-13
Project ref: `wwhbdgwfodumognpkgrf`

## Goal

Run Guard + Resident mobile staging validation against the real shared Supabase backend, while OTP and push remain intentionally deferred.

## Test Accounts

Use this pair:

- Guard: `guard@test.com`
- Resident: `rohit@test.com`

Why this pair:

- guard account is fully wired to a real `security_guards` row
- resident account is auth-linked
- resident flat is much cleaner than `RES-001`

## Verified Remote Identity Mapping

### Guard

- email: `guard@test.com`
- guard code: `GRD-001`
- guard id: `729c33ef-160d-45de-afdb-c811b391f70e`
- assigned location id: `39b1148a-6976-4caf-b020-4f2134d322cb`

### Resident

- email: `rohit@test.com`
- resident code: `RES-7AD49B`
- resident name: `Rohit Verna`
- flat id: `1ae71b6b-fc10-4fcf-8005-c7f0c90f16f8`

## Why Not Use `resident@test.com`

Do not use `resident@test.com` as the main test resident right now.

Reason:
- its flat currently has about `160` pending visitors
- that makes deterministic testing noisy and slow

## Scope For This Runbook

Included:
- real backend visitor creation
- resident pending approvals
- approve path
- deny path
- guard-side visitor status refresh
- guard checklist submit
- guard panic alert write

Deferred on purpose:
- real OTP provider validation
- real push delivery validation

## Preconditions

### Mobile env

The mobile app must point to the linked Supabase project using:
- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`

### Temporary staging auth path

Until SMS OTP is configured, use the temporary staging-only email/password sign-in path in mobile.

Use:
- `guard@test.com`
- `rohit@test.com`

Default seeded password:
- `Test@1234`

Important:
- this path is for internal staging only
- it must be removed or disabled before production release

### App mode

For these tests:
- do not use preview login
- do not use offline mode

### Device

Prefer one real Android device first.

Emulator is acceptable for early staging smoke, but real-device validation is more important for:
- camera
- location
- app lifecycle

## Recommended Cleanup Before Each Test Round

Use this SQL in Supabase SQL editor before running the guard/resident staging cycle for `rohit@test.com`.

```sql
delete from public.visitors
where flat_id = '1ae71b6b-fc10-4fcf-8005-c7f0c90f16f8'
  and approval_status = 'pending';
```

Optional stronger cleanup for that resident flat:

```sql
delete from public.visitors
where flat_id = '1ae71b6b-fc10-4fcf-8005-c7f0c90f16f8'
  and entry_time > now() - interval '7 days';
```

Use the stronger cleanup only if you explicitly want to wipe recent visitor noise for that flat.

## Test 1: Guard Creates Visitor -> Resident Approves

### Guard side

1. Log in as `guard@test.com`
2. Open visitors
3. Search/select resident destination for `Rohit Verna`
4. Create one new visitor with unique name:
   - `Staging Approve Visitor 01`
5. Save visitor

Expected:
- save succeeds
- visitor appears in guard list
- approval status is `pending`

### Resident side

1. Log in as `rohit@test.com`
2. Open approvals
3. Find `Staging Approve Visitor 01`
4. Approve visitor

Expected:
- resident action succeeds
- approval disappears or moves out of pending state

### Guard verification

1. Refresh guard visitors
2. Find `Staging Approve Visitor 01`

Expected:
- guard sees approved state from backend

## Test 2: Guard Creates Visitor -> Resident Denies

### Guard side

1. Create another unique visitor:
   - `Staging Deny Visitor 01`

Expected:
- visitor is created in pending state

### Resident side

1. Open approvals
2. Find `Staging Deny Visitor 01`
3. Deny visitor

Expected:
- deny action succeeds

### Guard verification

1. Refresh guard visitors
2. Find `Staging Deny Visitor 01`

Expected:
- guard sees denied/rejected state from backend

## Test 3: Guard Visitor Checkout

Precondition:
- use a visitor already approved or otherwise inside

Steps:
1. On guard side, select an inside visitor
2. Checkout visitor

Expected:
- checkout succeeds
- visitor leaves the inside list

## Test 4: Guard Checklist Submit

Steps:
1. Log in as `guard@test.com`
2. Open checklist
3. Complete the active checklist items
4. Submit checklist

Expected:
- submit succeeds
- checklist response persists to backend

Optional verification SQL:

```sql
select employee_id, checklist_id, response_date, is_complete, submitted_at
from public.checklist_responses
order by submitted_at desc
limit 10;
```

## Test 5: Guard Panic Alert

Steps:
1. Log in as `guard@test.com`
2. Trigger panic flow
3. Attach location/media if available in the current staging device setup

Expected:
- panic alert write succeeds
- alert is visible in backend/oversight feed

Optional verification SQL:

```sql
select id, alert_type, status, triggered_at, guard_id
from public.panic_alerts
order by triggered_at desc
limit 10;
```

## Test 6: Frequent Visitor Path

Steps:
1. Resident marks a visitor as frequent
2. Guard re-creates that same visitor for the same flat

Expected:
- behavior should match backend policy
- if auto-approve path is active, visitor should bypass pending state

Note:
- this is useful, but not as critical as approve/deny for the first staging slice

## Pass Criteria For Non-OTP Staging Slice

This staging slice is considered successful if:

- guard can create a visitor for `rohit@test.com`
- resident sees that visitor in approvals
- resident can approve
- resident can deny
- guard sees final state after resident action
- guard can submit checklist
- guard can create panic alert

## Known Open Gaps After This Runbook

These will still remain open:

- real OTP provider validation
- real push notification delivery
- release build hardening
- production sign-off

That is acceptable for the current phase, as long as you keep them listed as explicit blockers.

## Best Execution Order

1. Run cleanup SQL for `rohit@test.com` flat.
2. Test approve path.
3. Test deny path.
4. Test guard-side reflection.
5. Test checklist submit.
6. Test panic alert write.
7. Only after those are stable, move to OTP and push validation.

## Final Recommendation

Use this runbook as your first real staging validation target for mobile.

Do not spend more time expanding preview flows before these staging tests are clean.
