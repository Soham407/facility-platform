# Production Checklist Report

Run: `checklist-20260416-233804`
Date: 2026-04-16T23:56:28.702032
Run started at: `2026-04-16T23:38:04.478823+05:30`
Repo root: `/Volumes/Soham/untitled folder/facility-platform`

## Results

| # | Checkpoint | Status | Attempts | Log |
|---|-----------|--------|----------|-----|
| 1 | deploy-dispatch-notification-queue | PASS | 1 | `checkpoint-logs/deploy-dispatch-notification-queue-attempt-1.log` |
| 2 | verify-push-token-registration | MANUAL | 1 | `checkpoint-logs/verify-push-token-registration-attempt-1.log` |
| 3 | staging-e2e-approve | FAIL | 3 | `checkpoint-logs/staging-e2e-approve-attempt-3.log` |
| 4 | verify-notification-insertion | SKIP | 0 | `checkpoint-logs/verify-notification-insertion-attempt-0.log` |
| 5 | verify-notification-dispatch | FAIL | 2 | `checkpoint-logs/verify-notification-dispatch-attempt-2.log` |
| 6 | staging-e2e-deny | FAIL | 3 | `checkpoint-logs/staging-e2e-deny-attempt-3.log` |
| 7 | staging-e2e-checklist | FIXED | 2 | `checkpoint-logs/staging-e2e-checklist-attempt-2.log` |
| 8 | staging-e2e-sos | PASS | 1 | `checkpoint-logs/staging-e2e-sos-attempt-1.log` |
| 9 | verify-panic-notification | PASS | 1 | `checkpoint-logs/verify-panic-notification-attempt-1.log` |
| 10 | web-admin-backend-verification | PASS | 1 | `checkpoint-logs/web-admin-backend-verification-attempt-1.log` |
| 11 | staging-fallback-audit | PASS | 1 | `checkpoint-logs/staging-fallback-audit-attempt-1.log` |

## Summary: 6/11 passed

### deploy-dispatch-notification-queue — PASS

Attempts: `1`

Log file: `checkpoint-logs/deploy-dispatch-notification-queue-attempt-1.log`

```
$ supabase functions deploy dispatch-notification-queue
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 120
exit_code: 0

--- STDOUT ---
Deployed Functions on project wwhbdgwfodumognpkgrf: dispatch-notification-queue
You can inspect your deployment in the Dashboard: https://supabase.com/dashboard/project/wwhbdgwfodumognpkgrf/functions

--- STDERR ---
WARNING: Docker is not running
Uploading asset (dispatch-notification-queue): supabase/functions/dispatch-notification-queue/deno.json
Uploading asset (dispatch-notification-queue): supabase/functions/dispatch-notification-queue/index.ts
```

### verify-push-token-registration — MANUAL

Attempts: `1`

Log file: `checkpoint-logs/verify-push-token-registration-attempt-1.log`

```
$ supabase db query 'SELECT count(*) AS cnt
           FROM push_tokens pt
           JOIN auth.users u ON u.id = pt.user_id
           WHERE pt.is_active = true
             AND COALESCE(pt.token_type, '\''fcm'\'') = '\''fcm'\''
             AND lower(u.email) IN ('\''guard@test.com'\'', '\''rohit@test.com'\'', '\''resident@test.com'\'');' --linked
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 30
exit_code: 0

--- STDOUT ---
┌─────┐
│ cnt │
├─────┤
│ 0   │
└─────┘

--- STDERR ---
Initialising login role...
```

### staging-e2e-approve — FAIL

Attempts: `3`

Log file: `checkpoint-logs/staging-e2e-approve-attempt-3.log`

```
$ '/Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_resident_staging_e2e.sh'
cwd: /Volumes/Soham/untitled folder/facility-platform
timeout_seconds: 300
exit_code: 1

--- STDOUT ---
Emulator already running.
Metro already running on port 8081.
Clearing Android app state for a clean guard/resident staging run
Resetting prior test visitors for Rohit Verna's flat
Running guard resident staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_e2e.yaml
Emulator already running.
Metro already running on port 8081.
Running flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_e2e.yaml
Using device: emulator-5554
Maestro attempt: 1/1
Running on Pixel_10_Pro
 > Flow guard_resident_staging_e2e
Launch app "com.facilitypro.mobile" with clear state... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
Run _dismiss_developer_menu.yaml... COMPLETED
Run flow when "Development Build" is visible...
  Tap on "http://10.0.2.2:8081"... COMPLETED
Run flow when "Development Build" is visible... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
Run _dismiss_developer_menu.yaml... COMPLETED
Assert that "Mobile OTP Sign-In" is visible... COMPLETED
Assert that "Mobile OTP Sign-In" is visible... COMPLETED
Scrolling DOWN until id: qa_login_email_sign_in is visible with speed 40, visibility percentage 100%, timeout 20000 ms, with centering disabled... COMPLETED
Tap on id: qa_login_email_sign_in... COMPLETED
Assert that "Email Sign-In" is visible... COMPLETED
Tap on id: qa_email_login_email... COMPLETED
Erase text... COMPLETED
Input text guard@test.com... COMPLETED
Hide Keyboard... COMPLETED
Tap on id: qa_email_login_password... COMPLETED
Erase text... COMPLETED
Input text Test@1234... COMPLETED
Hide Keyboard... COMPLETED
Scrolling DOWN until id: qa_email_login_submit is visible with speed 40, visibility percentage 100%, timeout 15000 ms, with centering disabled... COMPLETED
Tap on id: qa_email_login_submit... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
Run _dismiss_developer_menu.yaml... COMPLETED
Run flow when id: qa_onboarding_biometric_skip is visible...
Run flow when id: qa_onboarding_biometric_skip is visible... SKIPPED
Run flow when id: qa_onboarding_biometric_continue is visible...
Run flow when id: qa_onboarding_biometric_continue is visible... SKIPPED
Run flow when id: qa_onboarding_geo_refresh is visible...
  Tap on id: qa_onboarding_geo_refresh... COMPLETED
  Assert that id: qa_onboarding_geo_complete is visible... COMPLETED
  Tap on id: qa_onboarding_geo_complete... COMPLETED
Run flow when id: qa_onboarding_geo_refresh is visible... COMPLETED
Assert that id: qa_guard_tab_home is visible... COMPLETED
Assert that id: qa_guard_tab_home is visible... COMPLETED
Tap on id: qa_guard_tab_visitors... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
Run _dismiss_developer_menu.yaml... COMPLETED
Assert that "Visitor Logging" is visible... COMPLETED
Tap on id: qa_guard_visitor_name... COMPLETED
Input text Staging Approve Visitor 01... COMPLETED
Hide Keyboard... COMPLETED
Tap on id: qa_guard_visitor_phone... COMPLETED
Input text 9876543210... COMPLETED
Hide Keyboard... COMPLETED
Tap on id: qa_guard_visitor_purpose... COMPLETED
Input text Guest visit... COMPLETED
Hide Keyboard... COMPLETED
Tap on id: qa_guard_visitor_destination... COMPLETED
Input text Rohit Verna... COMPLETED
Hide Keyboard... COMPLETED
Assert that id: qa_guard_destination_result_0 is visible... 
```

### verify-notification-insertion — SKIPPED

Attempts: `0`

Log file: `checkpoint-logs/verify-notification-insertion-attempt-0.log`

```
Dependency 'staging-e2e-approve' not met
```

### verify-notification-dispatch — FAIL

Attempts: `2`

Log file: `checkpoint-logs/verify-notification-dispatch-attempt-2.log`

```
$ supabase db query 'SELECT trigger_mobile_notification_queue();' --linked
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 30
exit_code: 0

--- STDOUT ---
┌───────────────────────────────────┐
│ trigger_mobile_notification_queue │
├───────────────────────────────────┤
│                                   │
└───────────────────────────────────┘

--- STDERR ---
Initialising login role...

--- FINAL POLL RESULT ---

$ supabase db query 'SELECT id, delivery_state, created_at
               FROM notifications
               WHERE notification_type = '\''visitor_at_gate'\''
                 AND created_at >= '\''2026-04-16T23:38:04.478823+05:30'\''::timestamptz
               ORDER BY created_at DESC
               LIMIT 1;' --linked
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 30
exit_code: 0

--- STDOUT ---
┌──────────────────────────────────────┬────────────────┬───────────────────────────────┐
│                  id                  │ delivery_state │          created_at           │
├──────────────────────────────────────┼────────────────┼───────────────────────────────┤
│ 6a0a5070-058c-4d33-9c01-02fc4732a1a1 │ push_queued    │ 2026-04-16 18:14:19.427744+00 │
└──────────────────────────────────────┴────────────────┴───────────────────────────────┘

--- STDERR ---
Initialising login role...
```

### staging-e2e-deny — FAIL

Attempts: `3`

Log file: `checkpoint-logs/staging-e2e-deny-attempt-3.log`

```
Neither script nor Maestro flow exists for guard_resident_staging_deny_e2e. Expected one of: /Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_resident_staging_deny_e2e.sh or /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_deny_e2e.yaml
```

### staging-e2e-checklist — FIXED

Attempts: `2`

Log file: `checkpoint-logs/staging-e2e-checklist-attempt-2.log`

```
$ '/Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_checklist_staging_e2e.sh'
cwd: /Volumes/Soham/untitled folder/facility-platform
timeout_seconds: 300
exit_code: 0

--- STDOUT ---
Emulator already running.
Metro already running on port 8081.
Clearing Android app state for a clean guard checklist staging run
Resetting today's guard checklist response for a clean backend verification
Running guard checklist staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_checklist_staging_e2e.yaml
Emulator already running.
Metro already running on port 8081.
Running flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_checklist_staging_e2e.yaml
Using device: emulator-5554
Maestro attempt: 1/1
Running on Pixel_10_Pro
 > Flow guard_checklist_staging_e2e
Launch app "com.facilitypro.mobile" with clear state... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
Run _dismiss_developer_menu.yaml... COMPLETED
Run flow when "Development Build" is visible...
  Tap on "http://10.0.2.2:8081"... COMPLETED
Run 
```

### staging-e2e-sos — PASS

Attempts: `1`

Log file: `checkpoint-logs/staging-e2e-sos-attempt-1.log`

```
$ '/Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_sos_staging_e2e.sh'
cwd: /Volumes/Soham/untitled folder/facility-platform
timeout_seconds: 300
exit_code: 0

--- STDOUT ---
Emulator already running.
Metro already running on port 8081.
Seeding staging guard profile photo to bypass first-time guard photo onboarding
Clearing Android app state for a clean guard SOS staging run
Resetting today's guard panic alerts for a clean backend verification
Running guard SOS staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_sos_staging_e2e.yaml
Emulator already running.
Metro already running on port 8081.
Running flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_sos_staging_e2e.yaml
Using device: emulator-5554
Maestro attempt: 1/1
Running on Pixel_10_Pro
 > Flow guard_sos_staging_e2e
Launch app "com.facilitypro.mobile" with clear state... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
Run _dismiss_developer_menu.yaml... COMPLETED
Run flow when "Development Build" is visible...
  Tap on "h
```

### verify-panic-notification — PASS

Attempts: `1`

Log file: `checkpoint-logs/verify-panic-notification-attempt-1.log`

```
$ supabase db query 'SELECT id, delivery_state, notification_type, created_at
           FROM notifications
           WHERE notification_type IN ('\''panic_alert'\'', '\''panic_resolved'\'')
             AND created_at >= '\''2026-04-16T23:38:04.478823+05:30'\''::timestamptz
           ORDER BY created_at DESC
           LIMIT 1;' --linked
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 30
exit_code: 0

--- STDOUT ---
<empty>

--- STDERR ---
Initialising login role...
```

### web-admin-backend-verification — PASS

Attempts: `1`

Log file: `checkpoint-logs/web-admin-backend-verification-attempt-1.log`

```
  visitors_exist: 1 (OK)
    sql: SELECT count(*) FROM visitors WHERE entry_time > NOW() - INTERVAL '24 hours';
  resident_auth_linked: 2 (OK)
    sql: SELECT count(*) FROM residents WHERE auth_user_id IS NOT NULL AND is_active = true;
  guard_employee_chain: 1 (OK)
    sql: SELECT count(*) FROM security_guards sg
                                   JOIN employees e ON e.id = sg.employee_id
                                   WHERE sg.is_active = true AND e.auth_user_id IS NOT NULL;
ALL_CHECKS_PASSED
```

### staging-fallback-audit — PASS

Attempts: `1`

Log file: `checkpoint-logs/staging-fallback-audit-attempt-1.log`

```
AUDIT_PASSED
```
