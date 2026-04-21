# Guard + Resident Staging Integration Plan

Updated: 2026-04-12

## Goal

Move the mobile Guard + Resident flows from preview-safe local testing to real staging flows backed by the shared Supabase project.

## Key Finding

This is not a greenfield integration.

`Solvesxx_mobile` already calls real backend RPCs for the core Guard + Resident workflows:

- visitor destination lookup via `search_resident_destinations`
- visitor creation via `create_mobile_visitor`
- guard visitor list via `get_guard_visitors`
- visitor checkout via `checkout_visitor`
- panic alert via `start_mobile_panic_alert`
- resident pending approvals via `get_resident_pending_visitors`
- resident approve via `approve_visitor`
- resident deny via `deny_visitor`
- frequent visitor toggle via `set_resident_frequent_visitor`
- guard checklist submission via `submit_mobile_guard_checklist`

Evidence:
- [mobileBackend.ts](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/lib/mobileBackend.ts:187)
- [GuardVisitorsScreen.tsx](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/screens/guard/GuardVisitorsScreen.tsx:87)
- [ResidentApprovalsScreen.tsx](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/screens/resident/ResidentApprovalsScreen.tsx:60)
- [GuardChecklistScreen.tsx](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/screens/guard/GuardChecklistScreen.tsx:67)

## What Still Makes Mobile Non-Production

The remaining gap is not "missing backend wiring". The remaining gap is:

- preview mode still exists and is used heavily in E2E
- real OTP and session behavior are not yet the primary test target
- real camera/location/push flows are not yet validated end to end on staging
- release hardening is not done yet

## Phase 1: Staging Preconditions

### 1. Confirm staging env values in mobile

Required env vars:
- `EXPO_PUBLIC_SUPABASE_URL`
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`

Evidence:
- [supabase.ts](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/lib/supabase.ts:4)

Acceptance:
- mobile app connects to the same staging Supabase project used by web
- no empty env fallback in staging builds

### 2. Confirm RPCs exist in linked Supabase project

Must exist:
- `create_mobile_visitor`
- `get_guard_visitors`
- `checkout_visitor`
- `start_mobile_panic_alert`
- `get_resident_pending_visitors`
- `approve_visitor`
- `deny_visitor`
- `set_resident_frequent_visitor`
- `submit_mobile_guard_checklist`

Acceptance:
- all RPCs exist in the linked project
- parameter names match current mobile calls exactly

### 3. Confirm staging users and roles

Need real staging users for:
- one `security_guard`
- one `resident`

Acceptance:
- both can sign in with real OTP or controlled staging OTP path
- both map correctly to expected role/profile rows

## Phase 2: Replace Preview As The Main Validation Path

### 4. Keep preview only as local fallback

Current situation:
- guard and resident screens support preview/local flows
- real backend paths already exist beside them

Goal:
- preview remains useful for local deterministic testing
- staging validation must run against real backend paths, not preview bridges

Acceptance:
- dedicated staging test accounts are used for Guard + Resident validation
- staging E2E avoids preview shortcuts

### 5. Add a staging Guard + Resident test runbook

Must cover:
- guard OTP login
- resident OTP login
- guard creates visitor using live resident lookup
- resident sees approval request
- resident approves
- resident denies
- guard sees final state

Acceptance:
- this becomes the primary UAT path for Guard + Resident v1

## Phase 3: Real Device Integration Checks

### 6. Visitor photo upload

Current status:
- mobile already uploads visitor media before `create_mobile_visitor`

Evidence:
- [mobileBackend.ts](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/lib/mobileBackend.ts:199)

Needed:
- validate on real device
- confirm upload lands in the correct storage bucket
- confirm resident can view the visitor image

Acceptance:
- photo upload works on staging from device
- resident approval card renders uploaded image correctly

### 7. Guard panic flow

Current status:
- mobile already calls `start_mobile_panic_alert`

Evidence:
- [mobileBackend.ts](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/lib/mobileBackend.ts:291)

Needed:
- validate real location capture
- validate real photo capture path
- confirm alert reaches supervisor/notification path if included in v1

Acceptance:
- panic alert is persisted in staging
- location and media are stored correctly

### 8. Guard checklist flow

Current status:
- mobile already fetches checklist items and submits via RPC outside preview

Evidence:
- [GuardChecklistScreen.tsx](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/screens/guard/GuardChecklistScreen.tsx:67)
- [mobileBackend.ts](/Volumes/Soham/untitled%20folder/facility-platform/Solvesxx_mobile/src/lib/mobileBackend.ts:445)

Needed:
- validate checklist fetch against real data
- validate checklist submit persistence for the staging guard

Acceptance:
- submitted checklist row exists in staging DB
- reminder/incomplete logic sees real submitted state correctly

## Phase 4: Cross-Role Validation

### 9. Approve path

Flow:
- guard logs visitor
- resident receives pending item
- resident approves
- guard sees approved state

Acceptance:
- all state transitions come from backend, not preview store

### 10. Deny path

Flow:
- guard logs visitor
- resident denies
- guard sees denied state

Acceptance:
- rejection reason and status are visible where expected

### 11. Frequent visitor path

Flow:
- resident marks visitor frequent
- repeat visit is auto-approved if PRD/staging policy allows

Acceptance:
- repeat visit behavior matches backend function rules

## Phase 5: Notifications And Sessions

### 12. Push notification registration

Needed:
- register mobile push token in staging
- verify resident receives approval notification

Acceptance:
- push token is saved
- resident receives actionable visitor notification

### 13. OTP and auth lifecycle

Needed:
- validate real OTP send
- validate OTP verify
- validate session persistence after app restart
- validate sign out and re-login

Acceptance:
- no preview-only auth dependency for Guard + Resident staging UAT

## Phase 6: Release Hardening

### 14. Disable dev/preview shortcuts for release builds

Needed:
- preview entry points must not be available in production client builds

Acceptance:
- release build exposes only real auth paths

### 15. Add Guard + Resident staging checklist

Required final gate:
- guard login works
- resident login works
- visitor create works
- approve works
- deny works
- checkout works
- checklist submit works
- panic works
- push arrives
- media upload works

## Recommended Execution Order

1. Confirm staging env values in mobile.
2. Confirm all required RPCs exist on the linked Supabase project.
3. Provision one real staging guard and one real staging resident.
4. Run manual staging validation for visitor create -> approve -> guard reflection.
5. Run manual staging validation for visitor create -> deny -> guard reflection.
6. Validate checklist and panic on real devices.
7. Validate push notifications and session persistence.
8. Remove or gate preview entry points in release builds.

## Fastest Path To A Client-Usable V1

For the first real client version, the shortest path is:

- keep preview mode for local/internal testing only
- make staging-backed Guard + Resident the official validation path
- treat other roles as non-production for v1

## Final Verdict

You do not need to build a new backend for Guard + Resident mobile.

You need to:
- switch the main validation target from preview to staging
- verify the real device flows
- harden release behavior

That is a much smaller and more realistic path to a client-ready v1.
