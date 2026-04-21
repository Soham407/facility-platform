# Guard + Resident OTP Switch-Back Plan

This plan is for the point when SMS is available and Guard + Resident must move from the temporary staging email-login path back to the real production auth path: `phone + OTP`.

It is based on the current code and staging setup in this repo.

## 1. Current Auth State

### 1.1 Real Production-Target Path

The intended auth path already exists in code:

- [LoginScreen.tsx](./Solvesxx_mobile/src/screens/auth/LoginScreen.tsx)
- [auth.ts](./Solvesxx_mobile/src/lib/auth.ts)

Current production-target behavior:

- user enters phone number
- app calls `sendOtp()`
- app navigates to OTP screen
- app verifies OTP through Supabase

Relevant functions:

- `sendOtp(rawPhoneNumber)`
- `verifyOtp(phone, token)`

### 1.2 Temporary Staging-Only Path

The temporary bypass also exists in code:

- [EmailLoginScreen.tsx](./Solvesxx_mobile/src/screens/auth/EmailLoginScreen.tsx)
- [LoginScreen.tsx](./Solvesxx_mobile/src/screens/auth/LoginScreen.tsx)
- [auth.ts](./Solvesxx_mobile/src/lib/auth.ts)

Relevant temporary function:

- `signInWithEmailPassword(email, password)`

Current staging-only entry point:

- `qa_login_email_sign_in`
- `EmailLogin` route

This path was added only because SMS OTP is not available yet.

## 2. Goal Of The Switch-Back

After the switch-back:

- Guard and Resident must sign in only through phone + OTP in production
- staging email sign-in must not be available in production builds
- all Guard + Resident release signoff must be repeated on the OTP path

## 3. Exact Code Areas To Change

### 3.1 Mobile UI

Review and update:

- [Solvesxx_mobile/src/screens/auth/LoginScreen.tsx](./Solvesxx_mobile/src/screens/auth/LoginScreen.tsx)
- [Solvesxx_mobile/src/screens/auth/EmailLoginScreen.tsx](./Solvesxx_mobile/src/screens/auth/EmailLoginScreen.tsx)

Required changes:

- remove or gate the `Staging email sign-in` button from production builds
- prevent navigation to `EmailLogin` in production
- keep the OTP login screen as the only visible entry path for production users

### 3.2 Auth Helper

Review and update:

- [Solvesxx_mobile/src/lib/auth.ts](./Solvesxx_mobile/src/lib/auth.ts)

Required changes:

- keep `sendOtp()` and `verifyOtp()` as the only production-supported login helpers
- keep `signInWithEmailPassword()` only if explicitly guarded for internal staging builds
- do not allow email/password sign-in to remain reachable in release builds by accident

### 3.3 Navigation

Review and update:

- [Solvesxx_mobile/src/navigation/AuthNavigator.tsx](./Solvesxx_mobile/src/navigation/AuthNavigator.tsx)
- [Solvesxx_mobile/src/navigation/types.ts](./Solvesxx_mobile/src/navigation/types.ts)

Required changes:

- ensure `EmailLogin` is not exposed in production navigation
- if the route remains for internal builds, gate it behind an explicit staging/dev flag

### 3.4 Maestro / QA

Review and update:

- [qa_agent/maestro/guard_resident_staging_e2e.yaml](./qa_agent/maestro/guard_resident_staging_e2e.yaml)
- [qa_agent/maestro/guard_resident_staging_deny_e2e.yaml](./qa_agent/maestro/guard_resident_staging_deny_e2e.yaml)
- [qa_agent/maestro/guard_checklist_staging_e2e.yaml](./qa_agent/maestro/guard_checklist_staging_e2e.yaml)
- [qa_agent/maestro/guard_sos_staging_e2e.yaml](./qa_agent/maestro/guard_sos_staging_e2e.yaml)

Required changes:

- replace the temporary email sign-in steps with real phone + OTP steps
- use real staging phone numbers for guard and resident
- remove dependence on `qa_login_email_sign_in`
- preserve the rest of the staging workflow checks

## 4. Recommended Implementation Approach

### Option A: Hard Remove Before Release

Use this if you no longer need staging email login once SMS is live.

Do:

- remove the `Staging email sign-in` button from [LoginScreen.tsx](./Solvesxx_mobile/src/screens/auth/LoginScreen.tsx)
- remove `EmailLoginScreen.tsx`
- remove `signInWithEmailPassword()` if it is no longer needed
- remove `EmailLogin` from navigation types and navigator
- update staging Maestro flows to use OTP only

This is the safest production posture.

### Option B: Keep It Behind A Strict Flag

Use this only if you still want internal staging fallback after SMS is live.

Do:

- guard the email-login entry behind an explicit env flag such as `EXPO_PUBLIC_ENABLE_STAGING_EMAIL_LOGIN`
- default it to `false`
- ensure production builds never enable it
- ensure staging-only Maestro runs explicitly enable it only when intended

This is acceptable, but easier to misuse than hard removal.

Recommendation:

- use `Option A` for production release
- use `Option B` only if you genuinely need a short transition period

## 5. Required Data Preparation Before OTP Testing

Before switching the tests to OTP, make sure:

- guard staging user has a real staging phone number
- resident staging user has a real staging phone number
- both users are linked correctly to their role records
- SMS provider can deliver to those numbers
- Supabase OTP is configured for the correct environment

Without that, the code switch-back will be correct but the environment will still fail.

## 6. OTP Retest Checklist

After switching back, rerun these validations specifically on the OTP path.

### 6.1 Guard Login

- guard enters phone number
- OTP arrives
- guard enters OTP
- session opens in the correct guard workspace
- logout works
- re-login works

### 6.2 Resident Login

- resident enters phone number
- OTP arrives
- resident enters OTP
- session opens in the correct resident workspace
- logout works
- re-login works

### 6.3 Cross-Role

Repeat all real staging validations on the OTP path:

- guard create visitor -> resident approve
- guard create visitor -> resident deny
- guard checklist submit
- guard SOS / panic

### 6.4 Negative Cases

- wrong OTP rejected
- expired OTP rejected
- resend OTP works
- rate-limit or retry behavior is understandable

## 7. Release Blockers Specific To OTP

Do not release until all of these are true:

- OTP send works
- OTP verify works
- wrong/expired OTP behavior is acceptable
- guard can complete full login on real device
- resident can complete full login on real device
- temporary staging email login is not reachable in production

## 8. Suggested Execution Order

### Phase 1

1. configure SMS provider
2. verify guard and resident staging phone numbers
3. manually test OTP send + verify for both accounts

### Phase 2

1. switch staging Maestro flows from email login to OTP login
2. rerun:
   - `guard_resident_staging_e2e`
   - `guard_resident_staging_deny_e2e`
   - `guard_checklist_staging_e2e`
   - `guard_sos_staging_e2e`

### Phase 3

1. remove or hard-disable staging email login
2. generate release candidate build
3. perform manual real-device signoff

## 9. Final Recommendation

Current code review judgment:

- the OTP path already exists
- the staging email path is clearly temporary
- the switch-back is straightforward if SMS and phone data are ready

The safest path is:

1. keep current staging email login only until SMS is available
2. switch the staging flows to OTP as soon as SMS works
3. remove the email path before production release
