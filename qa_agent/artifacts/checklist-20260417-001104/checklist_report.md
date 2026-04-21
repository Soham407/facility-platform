# Production Checklist Report

Run: `checklist-20260417-001104`
Date: 2026-04-17T00:28:19.392816
Run started at: `2026-04-17T00:11:04.390063+05:30`
Repo root: `/Volumes/Soham/untitled folder/facility-platform`

## Results

| # | Checkpoint | Status | Attempts | Log |
|---|-----------|--------|----------|-----|
| 1 | deploy-dispatch-notification-queue | PASS | 1 | `checkpoint-logs/deploy-dispatch-notification-queue-attempt-1.log` |
| 2 | verify-push-token-registration | MANUAL | 1 | `checkpoint-logs/verify-push-token-registration-attempt-1.log` |
| 3 | staging-e2e-approve | PASS | 1 | `checkpoint-logs/staging-e2e-approve-attempt-1.log` |
| 4 | verify-notification-insertion | PASS | 1 | `checkpoint-logs/verify-notification-insertion-attempt-1.log` |
| 5 | verify-notification-dispatch | FAIL | 2 | `checkpoint-logs/verify-notification-dispatch-attempt-2.log` |
| 6 | staging-e2e-deny | FAIL | 3 | `checkpoint-logs/staging-e2e-deny-attempt-3.log` |
| 7 | staging-e2e-checklist | FAIL | 3 | `checkpoint-logs/staging-e2e-checklist-attempt-3.log` |
| 8 | staging-e2e-sos | PASS | 1 | `checkpoint-logs/staging-e2e-sos-attempt-1.log` |
| 9 | verify-panic-notification | PASS | 1 | `checkpoint-logs/verify-panic-notification-attempt-1.log` |
| 10 | web-admin-backend-verification | PASS | 1 | `checkpoint-logs/web-admin-backend-verification-attempt-1.log` |
| 11 | staging-fallback-audit | PASS | 1 | `checkpoint-logs/staging-fallback-audit-attempt-1.log` |

## Summary: 7/11 passed

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

### staging-e2e-approve — PASS

Attempts: `1`

Log file: `checkpoint-logs/staging-e2e-approve-attempt-1.log`

```
$ '/Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_resident_staging_e2e.sh'
cwd: /Volumes/Soham/untitled folder/facility-platform
timeout_seconds: 300
exit_code: 0

--- STDOUT ---
Emulator already running.
Metro already running on port 8081.
Force-stopping the app for a clean guard/resident staging run
Resetting prior test visitors for Rohit Verna's flat
Running guard resident staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_e2e.yaml
Emulator already running.
Metro already running on port 8081.
Running flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_e2e.yaml
Using device: emulator-5554
Maestro attempt: 1/1
Running on Pixel_10_Pro
 > Flow guard_resident_staging_e2e
Launch app "com.facilitypro.mobile"... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "Development Build" is visible...
  Run flow when "Development Build" is visible... SKIPPED
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is 
```

### verify-notification-insertion — PASS

Attempts: `1`

Log file: `checkpoint-logs/verify-notification-insertion-attempt-1.log`

```
$ supabase db query 'SELECT id, delivery_state, notification_type, created_at
           FROM notifications
           WHERE notification_type = '\''visitor_at_gate'\''
             AND created_at >= '\''2026-04-17T00:11:04.390063+05:30'\''::timestamptz
           ORDER BY created_at DESC
           LIMIT 1;' --linked
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 30
exit_code: 0

--- STDOUT ---
┌──────────────────────────────────────┬────────────────┬───────────────────┬───────────────────────────────┐
│                  id                  │ delivery_state │ notification_type │          created_at           │
├──────────────────────────────────────┼────────────────┼───────────────────┼───────────────────────────────┤
│ 8df52d2e-dacd-4b1b-8740-fbc8513b7069 │ push_queued    │ visitor_at_gate   │ 2026-04-16 18:43:17.844879+00 │
└──────────────────────────────────────┴────────────────┴───────────────────┴───────────────────────────────┘

--- STDERR ---
Initialising login role...
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
                 AND created_at >= '\''2026-04-17T00:11:04.390063+05:30'\''::timestamptz
               ORDER BY created_at DESC
               LIMIT 1;' --linked
cwd: /Volumes/Soham/untitled folder/facility-platform/Solvesxx_web
timeout_seconds: 30
exit_code: 0

--- STDOUT ---
┌──────────────────────────────────────┬────────────────┬───────────────────────────────┐
│                  id                  │ delivery_state │          created_at           │
├──────────────────────────────────────┼────────────────┼───────────────────────────────┤
│ 8df52d2e-dacd-4b1b-8740-fbc8513b7069 │ push_queued    │ 2026-04-16 18:43:17.844879+00 │
└──────────────────────────────────────┴────────────────┴───────────────────────────────┘

--- STDERR ---
Initialising login role...
```

### staging-e2e-deny — FAIL

Attempts: `3`

Log file: `checkpoint-logs/staging-e2e-deny-attempt-3.log`

```
$ '/Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_resident_staging_deny_e2e.sh'
cwd: /Volumes/Soham/untitled folder/facility-platform
timeout_seconds: 300
exit_code: 1

--- STDOUT ---
Emulator already running.
Metro already running on port 8081.
Force-stopping the app for a clean guard/resident deny staging run
Resetting prior test visitors for Rohit Verna's flat
Running guard resident deny staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_deny_e2e.yaml
Emulator already running.
Metro already running on port 8081.

--- STDERR ---
Initialising login role...
A new version of Supabase CLI is available: v2.90.0 (currently installed v2.84.2)
We recommend updating regularly for new features and bug fixes: https://supabase.com/docs/guides/cli/getting-started#updating-the-supabase-cli
Maestro flow not found: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_resident_staging_deny_e2e.yaml
```

### staging-e2e-checklist — FAIL

Attempts: `3`

Log file: `checkpoint-logs/staging-e2e-checklist-attempt-3.log`

```
$ '/Volumes/Soham/untitled folder/facility-platform/qa_agent/run_guard_checklist_staging_e2e.sh'
cwd: /Volumes/Soham/untitled folder/facility-platform
timeout_seconds: 300
exit_code: 1

--- STDOUT ---
Emulator already running.
Metro already running on port 8081.
Force-stopping the app for a clean guard checklist staging run
Resetting today's guard checklist response for a clean backend verification
Running guard checklist staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_checklist_staging_e2e.yaml
Emulator already running.
Metro already running on port 8081.

--- STDERR ---
Initialising login role...
A new version of Supabase CLI is available: v2.90.0 (currently installed v2.84.2)
We recommend updating regularly for new features and bug fixes: https://supabase.com/docs/guides/cli/getting-started#updating-the-supabase-cli
Maestro flow not found: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_checklist_staging_e2e.yaml
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
Force-stopping the app for a clean guard SOS staging run
Resetting today's guard panic alerts for a clean backend verification
Running guard SOS staging flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_sos_staging_e2e.yaml
Emulator already running.
Metro already running on port 8081.
Running flow: /Volumes/Soham/untitled folder/facility-platform/qa_agent/maestro/guard_sos_staging_e2e.yaml
Using device: emulator-5554
Maestro attempt: 1/1
Running on Pixel_10_Pro
 > Flow guard_sos_staging_e2e
Launch app "com.facilitypro.mobile"... COMPLETED
Run _dismiss_developer_menu.yaml...
  Run flow when "Development Build" is visible...
  Run flow when "Development Build" is visible... SKIPPED
  Run flow when "This is the developer menu." is visible...
  Run flow when "This is the developer menu." is visible... SKIPPED
  Run flow when "T
```

### verify-panic-notification — PASS

Attempts: `1`

Log file: `checkpoint-logs/verify-panic-notification-attempt-1.log`

```
$ supabase db query 'SELECT id, delivery_state, notification_type, created_at
           FROM notifications
           WHERE notification_type IN ('\''panic_alert'\'', '\''panic_resolved'\'')
             AND created_at >= '\''2026-04-17T00:11:04.390063+05:30'\''::timestamptz
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
