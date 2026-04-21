# Guard + Resident Remote Staging Audit

Updated: 2026-04-12
Project ref: `wwhbdgwfodumognpkgrf`

## Summary

The linked Supabase project is already capable of supporting Guard + Resident mobile staging work.

The core backend functions are present.
The biggest remaining staging gaps are:
- push tokens are not set up
- staging data is noisy for deterministic testing
- only a small number of resident accounts are auth-linked
- OTP is intentionally deferred

## Mobile RPC vs Linked Project

## Required mobile RPCs

From `Solvesxx_mobile/src/lib/mobileBackend.ts`:
- `create_mobile_visitor`
- `get_guard_visitors`
- `checkout_visitor`
- `start_mobile_panic_alert`
- `get_resident_pending_visitors`
- `approve_visitor`
- `deny_visitor`
- `set_resident_frequent_visitor`
- `submit_mobile_guard_checklist`

## Remote result

Confirmed present on linked project:
- `approve_visitor`
- `checkout_visitor`
- `create_mobile_visitor`
- `deny_visitor`
- `get_guard_visitors`
- `get_resident_pending_visitors`
- `set_resident_frequent_visitor`
- `start_mobile_panic_alert`
- `submit_mobile_guard_checklist`

Conclusion:
- no Guard + Resident mobile RPC is missing from the linked project

## Remote Schema / Infra State

Confirmed on linked project:
- `security_guards`: `1` row
- `residents`: `9` rows
- `daily_checklists`: `2` active rows
- storage bucket `visitor-photos`: present
- storage bucket `guard-secure-media`: present

Conclusion:
- minimum schema and storage support is present

## Remote Users Ready For Testing

## Guard

Confirmed fully wired guard:
- `guard@test.com`
- `guard_code = GRD-001`
- `security_guards` row exists
- `employees.auth_user_id` exists

Conclusion:
- you have at least one real staging guard account ready

## Residents

Confirmed auth-linked residents:
- `resident@test.com` -> `RES-001` -> `Rajesh Kumar`
- `rohit@test.com` -> `RES-7AD49B` -> `Rohit Verna`

Residents without auth linkage still exist:
- `RES-002`
- `RES-003`
- `RES-004`
- `RES-005`
- plus several family-member rows

Conclusion:
- you have at least one real resident account ready
- but the resident dataset is only partially auth-linked

## Notifications / Push State

Remote counts:
- `notifications`: `141`
- `push_tokens`: `0`

Conclusion:
- notification records exist
- real mobile push delivery is not staged yet
- push registration remains a missing step

## Staging Data Quality

Remote counts:
- pending visitors: `168`

Conclusion:
- staging visitor data is already noisy
- deterministic mobile validation will be harder unless you:
  - use isolated test users / flats
  - clean pending visitor rows
  - or create a dedicated staging scenario for guard/resident v1

## Remote Migration State

Linked project is almost fully up to date.

Only local migration not yet applied remotely:
- `20260407090000_extend_employee_document_types.sql`

Impact on Guard + Resident:
- none for the current Guard + Resident staging slice
- this missing migration is unrelated to the core visitor/checklist flow

## What Is Missing For Guard + Resident Staging

These are the real missing items now:

1. Push token registration
- `push_tokens` is empty
- resident push notification testing is not ready yet

2. Clean staging test data
- `168` pending visitors means your test environment is noisy
- you need isolated test flats/users or cleanup routines

3. Broader resident auth linkage
- only a subset of resident rows are auth-linked
- enough for testing exists, but not enough for broad rollout confidence

4. OTP validation
- intentionally deferred
- acceptable for now, but staging sign-in is not fully release-ready until tested

## What Is Not Missing

These are already in place:
- core Guard + Resident mobile RPCs
- at least one real guard user
- at least one real resident user
- checklist rows
- visitor media bucket
- secure guard media bucket
- notification table activity

## Recommendation

Use the current linked project for Guard + Resident staging, but first do this:

1. Reserve one guard test account:
- `guard@test.com`

2. Reserve one resident test account:
- `resident@test.com`

3. Create a dedicated staging cleanup routine for visitor state:
- either SQL cleanup for pending visitors tied to test flats
- or a separate staging flat/user pair only for mobile testing

4. Defer OTP and push validation until later, as planned, but clearly mark them as open release blockers.

## Final Verdict

The linked Supabase project is ready enough for non-OTP Guard + Resident staging integration.

The main missing items are not RPCs.
They are:
- clean test data
- push token setup
- broader auth-linked resident coverage
- eventual OTP validation
