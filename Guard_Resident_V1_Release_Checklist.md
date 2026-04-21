# Guard + Resident V1 Release Checklist

This is the strict release checklist for shipping `Security Guard` and `Resident` as the only production-supported mobile roles in v1.

It reflects what is already validated on the shared Supabase staging environment and what still blocks a real client release.

## 1. Current Status

### 1.1 Already Done On Staging

- `guard_resident_staging_e2e.yaml` passes
- `guard_resident_staging_deny_e2e.yaml` passes
- `guard_checklist_staging_e2e.yaml` passes
- `guard_sos_staging_e2e.yaml` passes

What that means is already proven against the real backend:

- guard can sign in through the temporary staging login path
- resident can sign in through the temporary staging login path
- guard can create a visitor entry
- resident can approve a visitor
- resident can deny a visitor
- guard can see approved state reflected back
- denied state is persisted correctly in Supabase
- guard can submit the daily checklist
- checklist submission is stored with `is_complete = true`
- guard can trigger SOS / panic
- panic alert is stored with real coordinates in Supabase

### 1.2 Not Production-Ready Yet

The app is not production-ready yet because these are still open:

- phone + OTP auth is not restored and validated
- staging email sign-in still exists
- real push notification delivery is not validated
- real-device camera validation is not signed off
- real-device GPS / permission validation is not signed off
- final web/admin onboarding readiness is not signed off

## 2. Mobile Release Checklist

### 2.1 Guard

Done:

- login works in staging with temporary email sign-in
- visitor create flow works against Supabase
- visitor approve reflection works against Supabase
- checklist submit works against Supabase
- SOS panic works against Supabase
- emergency/home navigation paths are stable in staging automation

Still required before release:

- restore `phone + OTP` as the real auth path
- remove/disable staging email sign-in in release builds
- manually validate camera path on a real device
- manually validate location permission and live GPS behavior on a real device
- manually validate app fresh install / restart / resume behavior
- manually validate sign-out and re-login behavior with production auth path

### 2.2 Resident

Done:

- login works in staging with temporary email sign-in
- pending approval queue works against Supabase
- approve path works against Supabase
- deny path works against Supabase

Still required before release:

- restore `phone + OTP` as the real auth path
- remove/disable staging email sign-in in release builds
- manually validate notification arrival and in-app handling
- manually validate resident session persistence and logout behavior

### 2.3 Cross-Role

Done:

- guard creates visitor -> resident approves -> guard sees approved
- guard creates visitor -> resident denies -> backend stores denied state and rejection reason

Still required before release:

- validate push/notification behavior for both approve and deny paths
- validate repeated runs with real society data
- validate real user onboarding data for multiple residents/flats, not just the current staging pair

## 3. Web And Backend Release Checklist

### 3.1 Must Be Working From Web/Admin Side

- resident provisioning on web
- resident to `auth_user_id` linking
- resident to flat/building mapping
- guard to employee to security-guard mapping
- guard to site / company location assignment
- checklist master data exists and is stable
- panic alert records are visible to operations/admin users
- visitor records are queryable and operationally visible from web/admin

### 3.2 Shared Backend Must Be Stable

Already effectively validated:

- `create_mobile_visitor`
- `get_guard_visitors`
- `get_resident_pending_visitors`
- `approve_visitor`
- `deny_visitor`
- `submit_mobile_guard_checklist`
- `start_mobile_panic_alert`

Still required before release:

- verify migration state is clean and reproducible on production
- verify storage policies for guard/resident media in production env
- verify notification insert path and downstream delivery path
- verify real OTP auth provider configuration
- verify production environment variables and secrets

## 4. Release Blockers

These are hard blockers. Do not call the app client-ready until all are done.

### 4.1 Auth

- SMS provider configured
- phone + OTP implemented as the production auth path
- real OTP login tested for guard
- real OTP login tested for resident
- staging email sign-in removed or fully disabled in production builds

### 4.2 Notifications

- resident receives visitor notification in real conditions
- notification tap opens the right screen
- panic escalation notification path is verified
- push-token registration is working

### 4.3 Real Device Validation

- camera permission deny/grant tested
- location permission deny/grant tested
- fresh install tested
- app background/resume tested
- low network / reconnect tested
- at least 2 Android devices tested

### 4.4 Admin / Operations Readiness

- real resident onboarding process works
- real guard assignment process works
- support person can identify and fix a broken resident/guard mapping
- support person can inspect visitor and panic records from web/admin

## 5. Nice-To-Haves

These are useful, but they should not block Guard + Resident v1 if the core release blockers are done.

- deeper frequent visitor automation
- richer resident history views
- broader supervisor mobile coverage
- advanced analytics / dashboards
- non-v1 role hardening

## 6. Definition Of Release Ready

Guard + Resident v1 is release-ready only when all of these are true:

1. approve staging flow passes
2. deny staging flow passes
3. checklist staging flow passes
4. SOS staging flow passes
5. phone + OTP works for both roles
6. staging email login is disabled in production
7. push notifications are validated
8. real-device camera and GPS validation are signed off
9. web/admin onboarding and assignment flows are signed off
10. a full manual demo succeeds on real devices

## 7. Recommended Next Steps

### Immediate

1. keep the current staging flows as the baseline regression suite
2. add a push-notification validation checklist
3. prepare the OTP switch-back plan

### When SMS Is Ready

1. remove staging email login from production path
2. test guard OTP login
3. test resident OTP login
4. rerun all Guard + Resident staging flows
5. perform manual real-device signoff

## 8. Final Judgment Right Now

Current judgment:

- `Implementation readiness: strong`
- `Staging backend readiness: strong`
- `Production readiness: not complete yet`

The app is now in a good pre-release state for Guard + Resident, but it is still waiting on:

- OTP
- push validation
- real-device permission validation
- final web/admin operational signoff
