# FacilityPlatform Roadmap

Last updated: 2026-05-06

This roadmap is intentionally narrower than the PRDs. The product already has broad implementation surface area; v1 means the smallest set of workflows that must be trustworthy end-to-end.

## v1 Definition

v1 is client-usable when the following are true:

- Guard + Resident mobile workflows pass against staging with real backend data and real devices.
- Web admin can manage the required master data, guards, residents, suppliers, products, service setup, and billing support data without broken dashboard/query paths.
- Visitor management, guard duty, SOS, checklist, resident approval/denial, and notifications work without preview shortcuts.
- Buyer request -> indent/PO -> supplier dispatch -> receipt/GRN -> bill/payment/feedback can be demonstrated with persisted records.
- Field/service execution success actions persist evidence and advance real workflow state.
- Critical flows have repeatable evidence: Playwright/Maestro where possible, plus real-device staging runbooks where automation cannot prove device capabilities.

## v1 Must Work End-To-End

| Workflow | Required for v1 | Current status | Next proof |
| --- | --- | --- | --- |
| Mobile guard login and duty | Real OTP/session, duty start/end, selfie/location where promised. | Partial | Staging device run with preview shortcuts off. |
| Mobile guard checklist | Checklist assignment, completion, evidence, submission. | Partial | Backend-backed checklist submit and evidence proof. |
| Mobile guard SOS | Panic alert creation, location/evidence, supervisor/SMS/push escalation. | Partial | Real device and notification delivery proof. |
| Mobile guard visitor logging | Visitor entry, photo, resident selection, checkout. | Partial | Staging visitor record and private media proof. |
| Mobile resident decision | Pending visitor, approve, deny, notification history. | Partial | Cross-role approve and deny reflection on staging. |
| Web society/security oversight | Guards, visitors, residents, panic alerts, checklists, GPS. | Partial | Remove simulated/fallback paths for promised v1 flows. |
| Web admin/master data | Roles, users, employees, guards, societies, flats, residents, suppliers, products, services. | Partial | Role-scoped smoke tests for critical create/update actions. |
| Buyer material request | Buyer request creation, request items, status progression. | Partial | Persisted request through procurement handoff. |
| Supplier procurement | Indent, PO acknowledgement, dispatch, supplier bill. | Working e2e | Regression test around status transitions. |
| Inventory receipt | GRN/material receipt, quality/quantity handling, stock movement. | Partial | Alert-to-PO and GRN gate tests. |
| Finance closure | Purchase bill, sale bill, reconciliation, payment status, feedback. | Partial | End-to-end closure test with persisted linked records. |
| Field execution proof | Service task, material request, proof capture, completion. | Partial | Persisted evidence and status transition tests. |
| Notifications | Visitor-at-gate, SOS, order/status notifications. | Partial | Delivery validation for push/SMS/in-app queues. |

## v2 / Later

These can stay visible or partially built, but they should not block v1 unless the client explicitly adds them to the v1 promise:

- Full HRMS payroll automation and manager-side HR approval depth.
- Full AC service lifecycle beyond task/material/proof basics.
- Full pest-control chemical/PPE/resident notification lifecycle.
- Plantation/horticulture workflows.
- Printing and advertising commercial workflows.
- Asset QR and maintenance expansion.
- Advanced reports and analytics.
- Full RTV/material return exception loop.
- Buyer quotation/commercial acceptance flows.
- Vendor ETA/challan upload and deeper payment tracking.
- Offline queue hardening beyond Guard + Resident critical paths.

## Not Doing For v1

- No new modules.
- No landing-page polish as a substitute for product readiness.
- No broad UI redesign unless it fixes a workflow-blocking usability issue.
- No promise that every role in mobile is production-supported.
- No merge of web/mobile repos until the current source-of-truth docs and v1 status are stable.

## Work Gate

Every new feature or cleanup issue should include:

- Problem statement: who uses it and why it matters.
- Current evidence: code path, table/RPC, screen, test, or audit reference.
- Acceptance criteria: persisted data, state transition, notification, and role permissions when applicable.
- Verification plan: unit/API/E2E/runbook/device check.
- Documentation check: update `CONTEXT.md`, `STATUS.md`, `ROADMAP.md`, or an ADR if the work changes product language or architectural decisions.

## Recommended Next Issues

1. Disable mobile preview shortcuts in release builds.
2. Guard + Resident HITL staging validation runbook.
3. Cross-role visitor deny reflection: guard logs visitor, resident denies, guard sees result, `visitors` and `notifications` records exist.
4. SOS delivery proof: guard panic alert creates `panic_alerts`, uses `guard-secure-media` for evidence, and records `notifications` / `notification_logs`.
5. Admin workforce identity query cleanup: users, employees, and guard profiles.
6. Admin residence setup query cleanup: societies, buildings, flats, residents, and gate/location data.
7. Admin procurement/service setup query cleanup: suppliers, products, and services.
8. Society visitor/resident operations query cleanup: residents, visitors, and gate/location data.
9. Security guard operations query cleanup: guards, panic alerts, checklists, GPS/attendance signals.
10. Inventory alert-to-PO proof using active `requests` / `request_items` where buyer/request linkage is needed.
11. Buyer request-to-sale-bill existence proof using active `requests`, `request_items`, and `sale_bills.request_id`.
12. Buyer full lifecycle regression tracker: request, sale bill, payment, feedback, completed.
13. Field execution proof persistence after choosing the first client-relevant field role.
