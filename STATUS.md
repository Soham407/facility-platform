# FacilityPlatform Status

Last updated: 2026-05-06

This is the current source-of-truth status index for v1 planning. Older audits and matrices remain useful as evidence, but new planning should start here.

Status meanings:

- Working e2e: implemented and covered by meaningful end-to-end or workflow tests.
- Partial: implemented but has runtime gaps, shallow verification, preview-only behavior, query mismatches, or unproven transitions.
- UI only / stubbed: visible but not backed by a trustworthy workflow.
- Not started: no meaningful implementation found.

## Workspace

| Area | Status | Evidence | Next action |
| --- | --- | --- | --- |
| Root workspace structure | Partial | `README.md`, `WORKSPACE_MAP.md`, dirty root and submodule state. | Keep root as coordination layer; avoid feature work here. |
| Web app | Partial | `Solvesxx_web` has extensive modules, tests, migrations, and audits. | Prioritize cleanup and workflow truth over new scope. |
| Mobile app | Partial | Role app exists with guard/resident/buyer/supplier/service/HRMS/oversight flows. | Narrow production promise to Guard + Resident first. |
| Landing page | Partial | Separate `Solvexx-landingPage-` repo exists. | Defer until product app is stable. |
| Shared Supabase assets | Partial | Root `Reference__schema.sql`, root `supabase`, web migrations and functions. | Treat `Solvesxx_web/supabase` as the richer implementation source. |

## Web App Status

| PRD area | Status | Evidence | Current risk |
| --- | --- | --- | --- |
| Scope / stakeholder model | Working e2e | Roles, dashboard app shell, role access map, E2E role packs. | Keep role names stable across web/mobile/schema. |
| Master data | Working e2e | Company, role, designation, employees, products, suppliers, services, work masters. | Low risk unless a dependent workflow changes. |
| Company admin | Partial | Admin/user management and dashboards exist. | Dashboard query edges and admin workflow consistency need cleanup. |
| HRMS | Partial | Attendance, payroll, leave, shifts, documents, recruitment surfaces exist. | Query mismatches, document type coverage, and approval paths need verification. |
| Society/security | Partial | Societies, residents, visitors, panic alerts, guards, checklists, GPS, contacts. | Guard monitoring has simulated/fallback paths and real-time/device gaps. |
| Guard web | Partial | `/guard`, `/test-guard`, guard management and society flows. | Must separate real production workflow from test/demo surfaces. |
| Resident web | Partial | `/resident`, `/test-resident`, society resident surfaces. | Resident directory/privacy and visitor decision paths need regression coverage. |
| Visitor management | Working e2e | Visitor logging, resident directory, notification paths, visitor approval RPCs. | Maintain privacy-safe resident directory and deny/timeout tests. |
| Buyer dashboard/material supply | Partial | Buyer request, invoice, payment, feedback surfaces exist. | Billing/completion handoff remains high risk. |
| Supplier/vendor workflow | Working e2e | Supplier portal, indents, POs, bills, dispatch flows. | Protect supplier workflow state transitions. |
| Inventory/procurement | Partial | Product catalog, indents, POs, GRN, stock, warehouses, reorder and shortage logic. | Alert-to-PO and route/breadcrumb assumptions need verification. |
| Finance/reconciliation | Partial | Purchase bills, sale bills, reconciliation, payments, ledger, reports. | Cross-document closure and payment transitions must be tested end-to-end. |
| Field execution | Partial | Service boy, delivery, technician, job sessions, proof workspaces. | Evidence capture and action persistence need proof, not just UI clicks. |
| Service requests | Partial | Request list/board/detail/new, service categories, job sessions. | State transitions and dispatch/closure flows need tightening. |
| AC services | Partial | AC service and technician surfaces exist. | Full proof/closure chain not yet production-proven. |
| Pest control | Partial | Pest workflows, PPE, chemicals, expiry, spill kits. | PPE completion and chemical issuance rules need regression protection. |
| Plantation/horticulture | Partial | Horticulture zones/plans/tasks and service feedback exist. | Lower v1 priority; avoid expanding before core workflows stabilize. |
| Printing/advertising | Partial | Printing ad spaces/bookings and ID printing exist. | Lower v1 priority; verify persistence before promising. |
| Tickets/RTV/material quality | Partial | Behavior tickets, incidents, quality, quantity, RTV tables and screens. | Return/exception loops need stronger acceptance tests. |
| Reports | Working e2e | Reports hub and analytics loaders exist. | Keep data contracts stable. |
| Notifications | Partial | FCM, MSG91, notifications table/logs/queue, mobile notification surfaces. | Push/SMS delivery is not fully production-validated. |
| Assets/QR | Partial | Assets, QR codes, QR scans, `/scan/[id]`. | Not v1 critical; avoid extra work until operations stabilize. |

## Mobile App Status

| Role / area | Status | Evidence | Current risk |
| --- | --- | --- | --- |
| Auth / onboarding | Partial | OTP, email login, biometric, profile photo, geofence calibration. | Dev preview profiles and demo OTP paths must be disabled/validated for release. |
| Security Guard | Partial | Guard home, duty, SOS, checklist, visitor logging, checkout, contacts. | Real GPS, camera, push, offline/reconnect, and staging backend validation needed. |
| Resident | Partial | Home, approvals, visitor history, community, notifications. | Real push delivery, denial reflection, timeout/frequent visitor paths need proof. |
| Guard + Resident cross-role | Partial | Cross-role visitor approval path exists. | Deny reflection, timeout, and real backend timing need validation. |
| Security Supervisor | Working e2e | Oversight alerts, operations, live guards, tickets. | Not v1 production promise unless explicitly approved. |
| Society Manager | Partial | Oversight and material ticket creation. | Quantity mismatch and RTV loops incomplete. |
| Employee/HRMS | Working e2e | Attendance, leave, payslips, documents. | Manager-side approval and downloadable artifacts not fully proven. |
| Buyer | Working e2e | Request, invoice acknowledgement, feedback. | Broader commercial/quotation flows not present. |
| Supplier/vendor | Working e2e | Indents, orders, dispatch, billing. | ETA/challan/upload/payment progression incomplete. |
| AC technician | Partial | Tasks, material request, proof workspace. | Full proof-to-completion chain incomplete. |
| Pest technician | Partial | PPE, materials, task visibility. | Resident notification and completion chain incomplete. |
| Delivery boy | Partial | Tasks, manifest/proof workspace. | Strict dispatch-to-proof chain incomplete. |
| Service boy | Partial | Tasks, supply requests, proof workspace. | Inventory deduction/downstream stock effect incomplete. |
| Notifications | Partial | Role notification surfaces and local notification store. | Push transport itself not production-proven. |

## Highest Priority Cleanup Targets

1. Guard + Resident mobile production validation.
2. Web society/security guard monitoring and visitor decision truth.
3. Web admin/dashboard/HRMS query mismatches.
4. Web inventory alert-to-PO and GRN quality/quantity gates.
5. Web buyer billing/payment/completion handoff.
6. Web field execution proof persistence.
7. Notification delivery validation across guard/resident/SOS/visitor flows.

## Old Documents

Use this file as the starting point. Consult older files only for evidence:

- `WEB_PRD_COVERAGE_MATRIX.md`
- `Mobile_PRD_Coverage_Matrix.md`
- `WEBSITE_AUDIT.md`
- `MOBILE_AUDIT.md`
- `WEB_CLEANUP_BACKLOG.md`
- `CORRECTED_AUDIT_2026-04-21.md`
- `Guard_Resident_V1_Release_Scope.md`
- `Guard_Resident_V1_Release_Checklist.md`
- `AUDIT_REPORTS/*`

