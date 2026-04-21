# Guard + Resident Backend Reusability Audit

Updated: 2026-04-12

## Goal

Assess whether `Solvesxx_web` plus the shared Supabase backend already provide the core backend infrastructure needed for a Guard + Resident mobile v1.

## Overall Judgment

Yes. The web + Supabase side is already strong enough that the backend is probably not the primary blocker for a Guard + Resident mobile v1.

The current main blocker is mobile integration maturity:
- moving mobile off preview-safe flows and onto real staging/backend flows
- validating real OTP, real permissions, real notifications, and real cross-role sync

## What Already Exists And Can Be Reused

### 1. Shared role auth and routing

Evidence:
- `Solvesxx_web/app/login/page.tsx`
- `Solvesxx_web/src/lib/auth/roles.ts`

What exists:
- role-based login redirect for `resident`, `security_guard`, `security_supervisor`
- role access map already includes dedicated resident and guard route families

Implication for mobile:
- role model is already established across the same product
- mobile should align to the same role names and auth expectations

### 2. Guard checklist backend RPC

Evidence:
- `Solvesxx_web/supabase/migrations/20260402020000_mobile_checklist_submission.sql`

What exists:
- authenticated RPC `submit_mobile_guard_checklist(...)`
- guard-only enforcement with `is_guard()`
- upsert behavior for daily checklist submission

Implication for mobile:
- guard checklist should not remain preview-only
- mobile can integrate directly to this RPC for staging/prod

### 3. Visitor creation decision path for mobile

Evidence:
- `Solvesxx_web/supabase/migrations/20260406011000_security_ops_visitor_decision_path_fix.sql`

What exists:
- authenticated guard-only RPC `create_mobile_visitor(...)`
- resident approval requirement for resident-bound visitors
- auto-approve path for approved frequent visitors
- delivery bypass path
- 30-second approval deadline
- notification enqueue for resident approval requests

Implication for mobile:
- this is the core backend contract for Guard + Resident visitor flow
- mobile should reuse this rather than maintaining parallel preview-only visitor state long-term

### 4. Resident approve / deny visitor lifecycle

Evidence:
- `Solvesxx_web/supabase/migrations/20260330000009_visitor_lifecycle_rpc_repairs.sql`

What exists:
- resident-only approval/deny RPC repairs
- flat ownership checks
- immutability protections so guards cannot alter approval fields and residents cannot alter guard-owned fields

Implication for mobile:
- resident approval/deny behavior already has backend-level role protection
- mobile should bind to these real lifecycle functions for staging/prod

### 5. Notifications infrastructure

Evidence:
- `Solvesxx_web/src/lib/notifications.ts`
- `Solvesxx_web/supabase/migrations/20260406011000_security_ops_visitor_decision_path_fix.sql`

What exists:
- generic `send-notification` function invocation helper
- visitor arrival notification helper
- mobile notification queue inserts in visitor creation flow

Implication for mobile:
- the backend notification model already exists
- mobile still needs real push registration and real client handling

### 6. Visitor photo storage

Evidence:
- `Solvesxx_web/supabase/migrations/20260324000005_visitor_photos_storage_policy.sql`
- resident/visitor storage policies in `20260206192815_add_rls_helpers_and_policies_v3_fixed_params.sql`

What exists:
- `visitor-photos` storage bucket
- RLS-aware access policies
- guard upload path support

Implication for mobile:
- real visitor image upload is feasible on the shared backend
- current mobile preview-safe photo shortcuts should eventually be replaced with real upload

### 7. Guard inactivity and checklist reminder automation

Evidence:
- `Solvesxx_web/supabase/functions/check-inactivity/index.ts`
- `Solvesxx_web/supabase/functions/check-checklist/index.ts`
- `Solvesxx_web/supabase/migrations/20260402022000_notification_queue_and_retention.sql`

What exists:
- edge-function support for inactivity detection
- checklist reminder logic
- cron wiring for daily mobile checklist reminders

Implication for mobile:
- backend jobs already exist for guard operational compliance
- mobile still needs staging validation that these jobs trigger the right user-facing effects

### 8. Resident / visitor RLS and helper functions

Evidence:
- `Solvesxx_web/supabase/migrations/20260206140702_create_auth_helper_functions.sql`
- `Solvesxx_web/supabase/migrations/20260206192815_add_rls_helpers_and_policies_v3_fixed_params.sql`
- `Solvesxx_web/supabase/migrations/20260206140750_fix_rls_policies_visitors.sql`

What exists:
- `get_resident_id()`
- `is_resident()`
- residents can read/update own record
- guards can view residents
- resident visitor access rules

Implication for mobile:
- the shared database already has role-aware resident/visitor protection
- this is a strong sign that backend is reusable, not a blocker

## What Is Already Verified On Web Side

Evidence:
- `Solvesxx_web/docs/PRD_GAP_REGISTER.md`
- `Solvesxx_web/docs/PRODUCTION_READINESS_FIX_PLAN.md`

Signals:
- guard workflow E2E is documented as green for routine/checklist/panic surface
- production readiness for web branch is estimated around `82/100`
- targeted E2E suites exist for guard workflows

Interpretation:
- web/backend side is materially ahead of mobile
- mobile should reuse this maturity instead of duplicating logic in preview mode

## What Mobile Still Needs Before Guard + Resident v1 Is Staging-Ready

### 1. Replace preview-only data bridges with real Supabase integration

Needed:
- guard visitor creation should call real backend lifecycle path
- resident approval/deny should use real backend state, not preview bridging

### 2. Validate real OTP and sessions

Needed:
- real auth provider flow
- session persistence
- logout/session-expiry handling

### 3. Validate camera + location on real devices

Needed:
- visitor photo upload to `visitor-photos`
- guard selfie/attendance evidence if part of v1 promise
- location capture for duty start / panic context if part of v1 promise

### 4. Validate push notifications end to end

Needed:
- resident receives visitor approval notification on staging
- guard/supervisor panic and checklist reminders are visible where promised

### 5. Validate cross-role reflection against real backend

Needed:
- guard logs visitor
- resident sees request from backend
- resident approves/denies
- guard sees resulting state from backend, not only preview store

## Risks / Caveats

These do not negate reuse, but they matter:

- `Solvesxx_web/src/lib/auth/roles.ts` still includes test routes like `/test-guard` and `/test-resident`
- review docs mention some security/timezone concerns in checklist and notification functions
- web docs classify guard workflow as `implemented+partial`, not fully complete

Interpretation:
- backend looks reusable and strong
- but the final Guard + Resident v1 still needs staging validation and some hardening

## Recommendation

For Guard + Resident mobile v1:

1. Treat web + Supabase as the primary backend contract.
2. Stop expanding preview-only mobile behavior except where needed for local E2E.
3. Build a staging-backed mobile integration slice for:
   - guard login
   - create visitor
   - resident approve/deny
   - guard sees final status
4. Validate notifications, image upload, and location on real devices.

## Final Verdict

If your question is:

"Can mobile reuse the existing website + Supabase backend for Guard + Resident v1?"

The answer is:

Yes, very likely.

If your question is:

"Is the Guard + Resident mobile app production-ready just because this backend exists?"

The answer is:

No. Mobile still needs real staging integration, permission validation, and release hardening.
