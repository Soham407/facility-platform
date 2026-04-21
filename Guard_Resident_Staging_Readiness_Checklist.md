# Guard + Resident Staging Readiness Checklist

This checklist is for moving the mobile app from preview-backed E2E confidence to a staging build that is realistic enough for client validation.

It is intentionally limited to:
- Security Guard
- Resident

## 1. What Your Current E2E Already Proves

Current automated coverage proves:
- guard role can log in and navigate core guard surfaces
- resident role can log in and navigate core resident surfaces
- guard can log a visitor
- resident can approve a visitor
- resident can deny a visitor
- guard and resident can complete the core visitor approval loop in preview mode

What that does **not** prove yet:
- real backend synchronization
- real OTP transport and expiry
- real push notifications
- real camera/GPS behavior on physical devices
- real timeout behavior
- release-build behavior with preview shortcuts removed

## 2. Direct Answer To Your Question

This run:

```text
Tap on id: qa_resident_deny_visitor_0... COMPLETED
Assert that id: qa_resident_approvals_message is visible... COMPLETED
Assert that "Visitor denied successfully." is visible... COMPLETED
```

means:
- the resident-side deny workflow works in the current automated setup

It does **not** automatically mean:
- the full guard-side reflection of denial is proven
- the real backend/notification path is production-ready
- the app is fully staging-ready

So that result is good and important, but it is still only one part of staging readiness.

## 3. Staging Readiness Criteria

The Guard + Resident staging build should only be called ready when all of these are true.

### 3.1 Environment

- staging backend is deployed and stable
- staging database schema matches the app build
- real OTP provider is configured for staging
- push notification provider is configured for staging
- media/file storage works in staging
- environment variables are separated from dev/preview

### 3.2 Release Configuration

- preview shortcuts are disabled in staging release builds
- temporary staging email/password login is disabled or removed before production release
- debug-only helper text is removed or hidden
- release signing is configured
- version name and build number are correct
- API endpoints point to staging, not preview mocks

### 3.3 Guard Role

- real OTP login works
- session persists correctly after restart
- duty start works on physical device
- location permission request works correctly
- GPS snapshot is captured correctly
- SOS works with real camera/location behavior
- checklist can be completed on physical device
- required evidence capture works
- visitor entry is saved to staging backend
- visitor checkout updates correctly
- contacts screen works without crashing

### 3.4 Resident Role

- real OTP login works
- resident home loads from staging backend
- pending approvals show real visitor entries
- approve action works against backend
- deny action works against backend
- alerts/inbox loads correctly
- frequent visitor behavior works if included in v1 scope

### 3.5 Cross-Role Guard -> Resident

- guard logs visitor on staging
- resident sees that exact visitor in pending approvals
- resident approval reflects correctly to backend state
- resident denial reflects correctly to backend state
- guard-side status updates correctly after resident decision
- repeated runs do not corrupt state

### 3.6 Notifications

- resident receives visitor-at-gate notification
- guard-side workflow still works if push permission is denied
- SOS escalation triggers expected notification path
- notification tap opens the correct screen

### 3.7 Real Device Validation

- test on at least 2 Android devices
- test with camera permission denied then granted
- test with location permission denied then granted
- test on poor network
- test app background/resume
- test app fresh install

## 4. Required Automated Test Set Before Staging Signoff

These should all pass before calling the build staging-ready:

- [guard_full_e2e.yaml](./qa_agent/maestro/guard_full_e2e.yaml)
- [resident_full_e2e.yaml](./qa_agent/maestro/resident_full_e2e.yaml)
- [resident_deny_visitor_e2e.yaml](./qa_agent/maestro/resident_deny_visitor_e2e.yaml)
- [guard_resident_visitor_e2e.yaml](./qa_agent/maestro/guard_resident_visitor_e2e.yaml)

Recommended addition:
- a dedicated `guard_resident_deny_visitor_e2e.yaml` that proves the deny path across both roles

## 5. Manual QA Required Before Client Demo

Even if the E2Es pass, manually verify:

1. Guard logs in with real staging OTP.
2. Guard triggers SOS and the event reaches the correct management channel.
3. Guard completes checklist with photo evidence.
4. Guard creates a visitor entry with real staging data.
5. Resident receives and acts on that visitor request.
6. Guard sees the updated approval/denial state.
7. Visitor checkout works end to end.

## 6. Blocking Issues That Must Be Resolved Before Staging Signoff

Treat these as blockers:

- any OTP failure
- any crash in guard or resident flows
- any mismatch between resident decision and guard-side state
- camera or location permission dead-ends
- missing SOS event record
- visitor entry created but not visible to resident
- resident decision saved but not persisted

## 7. Nice-To-Have But Not Staging Blockers

- polished animations
- perfect copy
- broader multi-role support
- deep analytics dashboards
- non-v1 role hardening

## 8. Definition Of Staging Ready

Guard + Resident are staging-ready when:

1. the 4 existing automated E2Es pass consistently
2. staging backend replaces preview assumptions for the same workflows
3. real OTP works
4. real camera and location flows work on physical devices
5. resident decision correctly reflects into backend and guard state
6. preview/dev-only entry paths are disabled for the staging release build
7. temporary staging email/password login is removed before production rollout

## 9. Definition Of Client Demo Ready

Guard + Resident are client-demo ready when staging-ready is done plus:

1. at least one full manual end-to-end demo succeeds on real devices
2. key notifications are visible and understandable
3. crash/error monitoring is enabled
4. the team knows how to recover from failed OTP / failed sync / denied permissions

## 10. Recommended Next Steps

1. Create `guard_resident_deny_visitor_e2e.yaml`.
2. Run all 4 current Guard/Resident E2Es together as a focused suite.
3. Prepare a staging environment for Guard + Resident only.
4. Re-run the same suite on staging-backed flows.
5. Perform manual device QA with camera, GPS, and notifications.
