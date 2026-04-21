# Guard + Resident V1 Release Scope

## Goal

Ship a first client-facing mobile release where only these roles are production-supported:

- Security Guard
- Resident

Other roles may still exist in the app, but they are not part of the promised v1 production scope.

## Recommended Timeline

- Staging-ready pilot: `1 to 2 weeks`
- Client-usable v1: `2 to 4 weeks`
- Safer polished release: `4 to 5 weeks`

This assumes daily focused work, stable backend support, and that the release scope stays limited to Guard + Resident.

## V1 Product Scope

### Security Guard

Required for v1:
- OTP login
- duty start / duty end
- location refresh
- SOS panic trigger
- checklist completion and submission
- visitor entry logging
- visitor checkout
- emergency contacts

### Resident

Required for v1:
- OTP login
- resident home
- pending visitor approvals
- approve visitor
- deny visitor
- resident alerts / notification history

### Cross-Role

Required for v1:
- guard logs visitor
- resident sees pending approval
- resident approves visitor
- resident denies visitor
- guard/resident sync works correctly

## Current E2E Status

### Guard

Current automated files:
- [guard_full_e2e.yaml](./qa_agent/maestro/guard_full_e2e.yaml)
- [guard_resident_visitor_e2e.yaml](./qa_agent/maestro/guard_resident_visitor_e2e.yaml)

What is covered now:
- guard OTP login
- duty start in preview-safe mode
- SOS trigger in preview-safe mode
- patrol reset
- checklist completion and submit in preview-safe mode
- visitor logging
- visitor checkout
- emergency contacts

Judgment:
- `Implementation E2E: strong`
- `PRD E2E: mostly covered for v1`
- `Production E2E: not complete yet`

Why not production-complete yet:
- preview-safe location is not the same as real device GPS validation
- preview-safe selfie/SOS evidence is not the same as real camera capture
- offline queue behavior is not deeply validated yet
- real notification delivery is not proven yet

### Resident

Current automated files:
- [resident_full_e2e.yaml](./qa_agent/maestro/resident_full_e2e.yaml)
- [resident_deny_visitor_e2e.yaml](./qa_agent/maestro/resident_deny_visitor_e2e.yaml)

What is covered now:
- resident OTP login
- resident home
- approvals screen
- approve visitor
- deny visitor
- alerts screen

Judgment:
- `Implementation E2E: strong`
- `PRD E2E: mostly covered for v1`
- `Production E2E: not complete yet`

Why not production-complete yet:
- resident alerts screen is covered, but not deep push-delivery validation
- real backend approval timing and timeout behavior are not fully proven
- frequent visitor path is not yet production-validated

### Cross-Role

Current automated file:
- [guard_resident_visitor_e2e.yaml](./qa_agent/maestro/guard_resident_visitor_e2e.yaml)

What is covered now:
- guard logs visitor
- resident receives approval queue item
- resident approves visitor

What is still missing for stronger v1 confidence:
- deny-path reflection back to guard as a dedicated cross-role check
- timeout path
- frequent visitor repeat path

Judgment:
- `Implementation E2E: partial-to-strong`
- `PRD E2E: not complete`

## Honest Answer: Is E2E Complete For Guard + Resident?

No, not fully complete for production.

Yes, it is strong enough to say:
- the main role-local flows work
- the main approval loop exists
- the app is on a serious path toward a Guard + Resident v1

No, it is not enough yet to say:
- this is fully production-ready for clients

## What Still Needs To Be Done For Client-Ready V1

### 1. Real Environment Validation

- test Guard + Resident against staging backend, not only preview mode
- validate real OTP flow
- validate real visitor creation and resident approval records
- validate session persistence and logout

### 2. Device Capability Validation

- test camera on real Android devices
- test location permission and GPS behavior
- test app resume/background behavior
- test low-network / reconnect behavior

### 3. Notification Validation

- verify resident receives visitor alert notification
- verify guard-side and resident-side updates after action
- verify SOS escalation delivery path

### 4. Remaining Workflow Gaps

- add cross-role deny reflection test
- add timeout path test if timeout is part of client promise
- test frequent visitor workflow if it is part of v1 promise

### 5. Release Hardening

- disable dev preview shortcuts in release build
- remove or disable temporary staging email/password login before release
- configure release env vars and secrets
- signed release APK / AAB
- crash/error monitoring
- minimal analytics / logging
- release checklist and UAT signoff

## Suggested V1 Definition

You should call v1 production-ready only when all of the below are true:

1. Guard and Resident workflows pass on staging with real backend data.
2. Guard duty, SOS, visitor entry, resident approval, and resident denial all work on real devices.
3. Push/notification behavior is validated for the flows you promise clients.
4. Release build has no preview/dev shortcuts enabled.
5. Client UAT signs off the Guard + Resident journey.

## Suggested Immediate Plan

### Week 1

- finish Guard + Resident PRD automation gaps
- add cross-role deny-path E2E
- run Guard + Resident suite repeatedly until stable

### Week 2

- switch validation to staging/backend-backed environment
- test real OTP, notifications, camera, location
- fix defects found from real-device testing

### Week 3

- UAT with client scenarios
- release hardening
- signed release candidate

### Week 4

- final bug fixes
- client rollout / pilot deployment

## Recommendation

For v1, keep the market promise narrow:

- production-supported: Guard + Resident
- visible but not promised: all other roles

That is the fastest realistic way to get client value without waiting for the entire multi-role mobile PRD to become equally mature.
