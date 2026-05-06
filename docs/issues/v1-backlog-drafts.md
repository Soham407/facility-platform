# v1 Backlog Issue Drafts

Last updated: 2026-05-06

Tracker target: GitHub Issues for `https://github.com/Soham407/Solvesxx_web`.

These are draft vertical slices. They are not published yet. Publish only after the granularity and dependencies are approved.

Publishing trigger:

- Client signs off on `ROADMAP.md` v1, even informally.
- Or the team decides v1 is locked without waiting for client input.

Active buyer/procurement path for these drafts: use `requests` and `request_items` as the current code path, with `sale_bills.request_id` linking back to `requests`. Treat `order_requests` and `order_request_items` as legacy names unless a specific code inspection proves the touched surface still uses them.

## Sanity Check

| Draft | User | Acceptance test | Smallest reproducible demo | Publish readiness |
| --- | --- | --- | --- | --- |
| Disable mobile preview shortcuts in release builds | Release owner, Guard, Resident | Release/staging builds cannot use dev preview phone numbers or preview OTP. | Build/run non-dev mobile config and verify preview credentials are unavailable. | Ready AFK. |
| Guard + Resident HITL staging validation runbook | Guard, Resident, release owner | Real devices prove OTP/session/camera/location basics against staging. | One guard device and one resident device complete the runbook. | Ready HITL after preview shortcut task. |
| Cross-role visitor denial reflection | Guard, Resident | `visitors.approval_status` becomes `denied`, `visitors.rejection_reason` is persisted, and a `notifications` row records the visitor event. | Guard logs one visitor; resident denies; guard view, `visitors`, and `notifications` show the result. | Ready. |
| SOS delivery proof | Guard, Security Supervisor/Society Manager | `panic_alerts` record persists, media uses `guard-secure-media`, oversight can acknowledge/resolve, and `notifications`/`notification_logs` prove delivery attempts. | Guard triggers one SOS; supervisor resolves; DB/logs show alert, media reference, and notification state. | Ready, but device/push/SMS verification stays HITL. |
| Admin workforce identity query cleanup | Admin | Users, employees, and guard profiles load without query errors. | Admin opens setup screen and sees one linked user, employee, and guard profile. | Ready. |
| Admin residence setup query cleanup | Admin | Societies, buildings, flats, residents, and gate/location data load without query errors. | Admin opens residence setup and sees one society, building, flat, resident, and gate/location. | Ready. |
| Admin procurement/service setup query cleanup | Admin | Suppliers, products, and services load without query errors. | Admin opens setup/inventory/service surfaces and sees one supplier, product, and service. | Ready. |
| Society visitor/resident operations query cleanup | Society Manager | Residents, visitors, and gate/location data load through production surfaces. | Society manager sees one resident, one visitor, and one gate/location fixture. | Ready. |
| Security guard operations query cleanup | Society Manager, Security Supervisor | Guards, `panic_alerts`, checklist assignments/responses, and GPS/attendance summary load without broken assumptions. | Security supervisor sees one guard, one alert, one checklist fixture, and one location/attendance signal. | Ready. |
| Inventory alert-to-PO proof | Storekeeper/Admin | Low-stock or reorder condition leads to persisted linked indent/PO using `requests`/`request_items` where buyer/request linkage is needed. | Create low-stock fixture; open alert; start procurement; verify linked PO. | Ready; depends on procurement/service setup fixtures if missing. |
| Buyer request-to-sale-bill existence proof | Buyer, Account/Admin | Buyer creates a request and can see a linked `sale_bills` record. | One buyer request with one item results in one visible sale bill linked by `sale_bills.request_id`. | Ready AFK. |
| Buyer full lifecycle regression tracker | Buyer, Account/Admin | Existing request/invoice/payment/feedback/completed path is tracked as a regression suite, not one feature ticket. | One seeded request traverses invoice, payment, feedback, and completed state. | Tracking issue only, not AFK implementation. |
| Field execution proof persistence | Service Boy/Technician/Delivery Boy | Chosen field role persists evidence and advances backend state visible to the next role. | One assigned task is completed with proof and appears completed on a dashboard. | Decision pending: choose customer-led role or accept service boy by engineering default. |

## Proposed Breakdown

1. **Disable mobile preview shortcuts in release builds**
   - Type: AFK
   - Blocked by: None
   - User stories covered: Release owner can produce a staging/release build where dev preview phone numbers and preview OTP are unavailable.

2. **Guard + Resident HITL staging validation runbook**
   - Type: HITL
   - Blocked by: Disable mobile preview shortcuts in release builds.
   - User stories covered: Guard logs in and starts duty on a real device; resident logs in on a real device; camera, location, session, and logout behavior are recorded.

3. **Cross-role visitor denial reflection**
   - Type: AFK
   - Blocked by: Guard + Resident HITL staging validation runbook for production validation; can start in code before that.
   - User stories covered: Guard logs a visitor; resident denies the visitor; guard sees the denied state; `visitors` and `notifications` persist the decision.

4. **SOS delivery proof**
   - Type: AFK with HITL device verification
   - Blocked by: Guard + Resident HITL staging validation runbook for device and notification proof.
   - User stories covered: Guard triggers panic; `panic_alerts` and `guard-secure-media` persist alert/evidence; supervisor/society manager acknowledges/resolves; `notifications`/`notification_logs` record delivery state.

5. **Admin workforce identity query cleanup**
   - Type: AFK
   - Blocked by: None
   - User stories covered: Admin can read users, employees, and security guard profiles needed for v1 guard setup.

6. **Admin residence setup query cleanup**
   - Type: AFK
   - Blocked by: None
   - User stories covered: Admin can read societies, buildings, flats, residents, and gate/location data needed for guard/resident workflows.

7. **Admin procurement/service setup query cleanup**
   - Type: AFK
   - Blocked by: None
   - User stories covered: Admin can read suppliers, products, and services needed for inventory, procurement, and service fixtures.

8. **Society visitor/resident operations query cleanup**
   - Type: AFK
   - Blocked by: Admin residence setup query cleanup only if shared fixtures are missing.
   - User stories covered: Society manager can open resident, visitor, and gate/location operations without broken query assumptions.

9. **Security guard operations query cleanup**
   - Type: AFK
   - Blocked by: Admin workforce identity query cleanup only if shared fixtures are missing.
   - User stories covered: Security supervisor/society manager can open guard, panic alert, checklist, GPS, and attendance operations without broken query assumptions.

10. **Inventory alert-to-PO proof**
   - Type: AFK
   - Blocked by: Admin procurement/service setup query cleanup only if fixture/master data is missing.
   - User stories covered: Low-stock/reorder condition creates actionable procurement path; PO can be generated and linked to the stock need.

11. **Buyer request-to-sale-bill existence proof**
   - Type: AFK
   - Blocked by: Admin procurement/service setup query cleanup if buyer/product fixtures are missing.
   - User stories covered: Buyer creates a request with `requests`/`request_items`; account/admin path creates or exposes a linked `sale_bills` record.

12. **Buyer full lifecycle regression tracker**
   - Type: Tracking / HITL review
   - Blocked by: Buyer request-to-sale-bill existence proof and Inventory alert-to-PO proof.
   - User stories covered: Full buyer request lifecycle reaches invoice, payment, feedback, and completed state. This is a regression suite target, not one AFK feature ticket.

13. **Field execution proof persistence**
   - Type: AFK after role choice
   - Blocked by: Role choice for the first proof path: service boy, delivery boy, AC technician, or pest technician.
   - User stories covered: One field role sees a task, captures proof, submits completion, and backend state advances with evidence.

## Draft Issue Bodies

### 1. Disable mobile preview shortcuts in release builds

**What to build**

Make staging/release mobile builds unable to use dev preview credentials and preview OTP flows.

**Acceptance criteria**

- [ ] `getDevPreviewCredentials`, `isDevPreviewPhone`, `isDevPreviewOtp`, and related preview paths are unavailable outside dev/explicit preview builds.
- [ ] Release/staging build does not display or accept hardcoded preview phone numbers or `123456` preview OTP.
- [ ] Demo OTP backend use remains explicit and environment-gated.
- [ ] A small test, config check, or runbook command proves release/staging config disables preview auth.

**Smallest reproducible demo**

Run the mobile app in staging/release config and verify preview credentials are not shown and do not authenticate.

**Blocked by**

None - can start immediately.

### 2. Guard + Resident HITL staging validation runbook

**What to build**

Validate the Guard + Resident mobile v1 path on staging with real backend data and real devices.

**Acceptance criteria**

- [ ] Guard can log in with real OTP/session and start/end duty.
- [ ] Resident can log in with real OTP/session and see resident home/approvals.
- [ ] Camera, location permission, app resume/background behavior, and logout/session persistence are recorded in the runbook.
- [ ] The runbook names device model, OS version, build/env, tester, date, and pass/fail evidence.
- [ ] Failures are filed as separate defects with logs, screenshots, device details, and exact build/env.

**Smallest reproducible demo**

One guard device and one resident device complete login, guard duty start/end, resident home/approvals visibility, logout, and session persistence checks on staging.

**Blocked by**

Disable mobile preview shortcuts in release builds.

### 3. Cross-role visitor denial reflection

**What to build**

Complete and verify the visitor denial path across guard and resident roles: guard logs a visitor, resident denies, guard sees the result, and the system records the decision.

**Acceptance criteria**

- [ ] Guard can create a visitor entry through `create_mobile_visitor` or the active guard visitor path.
- [ ] Resident can deny through `deny_visitor`.
- [ ] The `visitors` row persists `approval_status = 'denied'`, `rejection_reason`, and relevant decision timestamp/actor fields where present.
- [ ] A `notifications` row with `notification_type = 'visitor_at_gate'` or the existing visitor decision notification type is persisted for the same visitor/resident flow.
- [ ] Guard-side visitor view reflects the denied result without manual data edits.
- [ ] Automated coverage proves the path, or a runbook records why automation cannot prove a specific device/notification step.

**Smallest reproducible demo**

Guard logs one visitor for one resident; resident denies that visitor; guard view, `visitors`, and `notifications` show the denied decision.

**Blocked by**

Code work can start immediately. Production validation depends on the Guard + Resident HITL staging validation runbook.

### 4. SOS delivery proof

**What to build**

Prove the guard SOS workflow from panic trigger through persisted alert, private media, oversight visibility, acknowledgement/resolution, and notification delivery evidence.

**Acceptance criteria**

- [ ] Guard panic action creates a persisted `panic_alerts` record through `start_mobile_panic_alert` or the active panic path.
- [ ] Evidence media, if captured, stores in the existing private `guard-secure-media` bucket.
- [ ] Security supervisor or society manager can see, acknowledge, and resolve the alert.
- [ ] `notifications` records exist for in-app delivery state.
- [ ] `notification_logs` records delivery attempts/failures when the dispatch Edge Function is involved.
- [ ] Push/SMS delivery is validated on staging or marked with a specific blocker.
- [ ] Tests or runbook cover failure states: no location, notification failure, repeated panic tap.

**Smallest reproducible demo**

Guard triggers one SOS; supervisor or society manager acknowledges and resolves it; `panic_alerts`, `guard-secure-media` when media exists, `notifications`, and `notification_logs` show the alert and delivery state.

**Blocked by**

Guard + Resident HITL staging validation runbook for device and notification proof.

### 5. Admin workforce identity query cleanup

**What to build**

Stabilize admin reads for the identity records needed to assign and support guards.

**Acceptance criteria**

- [ ] Admin can open the relevant dashboard/company/admin setup surface without Supabase query errors.
- [ ] Admin can read one linked `users` record.
- [ ] Admin can read one linked `employees` record.
- [ ] Admin can read one linked `security_guards` profile.
- [ ] Smoke coverage fails on the current broken query class and passes when these three surfaces load.

**Smallest reproducible demo**

Admin opens setup and sees one linked user, employee, and guard profile without query errors.

**Blocked by**

None - can start immediately.

### 6. Admin residence setup query cleanup

**What to build**

Stabilize admin reads for the residence records needed by guard/resident visitor flows.

**Acceptance criteria**

- [ ] Admin can read one `societies` record.
- [ ] Admin can read one `buildings` record linked to the society.
- [ ] Admin can read one `flats` record linked to the building.
- [ ] Admin can read one `residents` record linked to the flat.
- [ ] Admin can read one gate/location record from the active location source.
- [ ] Smoke coverage fails on the current broken query class and passes when these surfaces load.

**Smallest reproducible demo**

Admin opens residence setup and sees one society, building, flat, resident, and gate/location without query errors.

**Blocked by**

None - can start immediately.

### 7. Admin procurement/service setup query cleanup

**What to build**

Stabilize admin reads for the procurement and service setup records needed by buyer, inventory, and field-execution proofs.

**Acceptance criteria**

- [ ] Admin can read one `suppliers` record.
- [ ] Admin can read one `products` record.
- [ ] Admin can read one `services` record.
- [ ] Any demo-only fallback data in these v1-critical setup paths is removed or clearly feature-gated.
- [ ] Smoke coverage fails on the current broken query class and passes when these surfaces load.

**Smallest reproducible demo**

Admin opens procurement/service setup surfaces and sees one supplier, product, and service without query errors.

**Blocked by**

None - can start immediately.

### 8. Society visitor/resident operations query cleanup

**What to build**

Stabilize the society manager operations surface for residents, visitors, and gate/location data.

**Acceptance criteria**

- [ ] Society manager can open society visitor/resident pages without Supabase query errors.
- [ ] Resident data loads through the production resident surface, not a test/demo fallback.
- [ ] Visitor data loads through `visitors` and reflects current approval/checkout fields.
- [ ] Gate/location data loads from the active location source.
- [ ] Smoke coverage asserts at least one loaded persisted record per surface.

**Smallest reproducible demo**

Society manager opens visitor/resident operations and sees one resident, one visitor, and one gate/location fixture without manual data edits.

**Blocked by**

Admin residence setup query cleanup only if shared fixtures are missing.

### 9. Security guard operations query cleanup

**What to build**

Stabilize the security operations surface for guards, panic alerts, checklists, and location/attendance signals.

**Acceptance criteria**

- [ ] Security supervisor can open allowed security operations pages without Supabase query errors.
- [ ] Guard data loads through `security_guards` and linked employee/user identity where needed.
- [ ] Panic alert data loads through `panic_alerts`.
- [ ] Checklist assignment/response data loads through the active checklist tables.
- [ ] GPS/attendance summary uses the active guard location/attendance source.
- [ ] Smoke coverage asserts at least one loaded persisted record per critical surface.

**Smallest reproducible demo**

Security supervisor sees one guard, one panic alert, one checklist assignment/response, and one location/attendance signal without broken query assumptions.

**Blocked by**

Admin workforce identity query cleanup only if shared fixtures are missing.

### 10. Inventory alert-to-PO proof

**What to build**

Prove that an inventory alert or reorder condition can become an actionable procurement path ending in a linked PO.

**Acceptance criteria**

- [ ] Low-stock/reorder fixture or real data can be created repeatably.
- [ ] The alert/reorder condition appears in the inventory UI.
- [ ] User can start or navigate to the correct procurement action from the alert.
- [ ] Resulting indent/PO is persisted and linked to the product/stock need.
- [ ] If buyer/request linkage is needed, it uses active `requests`/`request_items`, not legacy `order_requests`/`order_request_items`.
- [ ] Breadcrumbs/routes do not break during the flow.
- [ ] Automated coverage asserts database records, not only UI state.

**Smallest reproducible demo**

Create one product below reorder threshold; open inventory alert; generate or navigate to procurement; verify one linked indent/PO exists.

**Blocked by**

Admin procurement/service setup query cleanup if supplier/product/service fixtures are missing.

### 11. Buyer request-to-sale-bill existence proof

**What to build**

Prove the first buyer billing slice: buyer creates a request and later sees a linked sale bill. Do not try to prove the full 13-state lifecycle in this issue.

**Acceptance criteria**

- [ ] Buyer can create one material request in active `requests`.
- [ ] Request items persist in active `request_items`.
- [ ] Account/admin path or fixture creates one `sale_bills` record linked by `sale_bills.request_id`.
- [ ] Buyer can see the linked sale bill in the buyer invoice surface.
- [ ] Test asserts `requests`, `request_items`, and `sale_bills` rows.
- [ ] No touched code path writes to legacy `order_requests` or `order_request_items`.

**Smallest reproducible demo**

One buyer creates one material request with one item; one sale bill exists with `sale_bills.request_id = requests.id`; buyer invoice page shows that bill.

**Blocked by**

Admin procurement/service setup query cleanup if buyer/product/service fixtures are missing.

### 12. Buyer full lifecycle regression tracker

**What to build**

Track the full buyer lifecycle as a regression target after the narrower request-to-sale-bill slice works. This should not be published as a single AFK implementation issue.

**Acceptance criteria**

- [ ] Regression target is documented as request, sale bill, payment, buyer feedback, and completed request state.
- [ ] Existing coverage such as `buyer-request-invoice-payment-feedback.spec.ts` is reviewed for whether it seeds too much state versus proving live workflow.
- [ ] Missing transitions are split into smaller AFK issues before implementation.
- [ ] The tracker links to the smaller buyer/procurement/finance issues instead of owning their implementation.

**Smallest reproducible demo**

One seeded `requests` row linked to `sale_bills` reaches paid status, `buyer_feedback` exists, and `requests.status = 'completed'`.

**Blocked by**

Buyer request-to-sale-bill existence proof and Inventory alert-to-PO proof.

### 13. Field execution proof persistence

**What to build**

Make one field execution path trustworthy end-to-end: assigned task, proof capture, completion, and backend status transition.

**Acceptance criteria**

- [ ] One first field role is chosen before publish: service boy, delivery boy, AC technician, or pest technician.
- [ ] A task for that role can be assigned from existing backend data.
- [ ] Assigned role can see the task in web or mobile.
- [ ] Proof/evidence capture stores in the intended private bucket/table path.
- [ ] Completion action advances the persisted task/job/session state.
- [ ] Next role or dashboard sees the updated state.
- [ ] Automated test or runbook proves persistence and evidence access.

**Smallest reproducible demo**

One chosen field role opens one assigned task, uploads one proof item, completes the task, and a dashboard/backend query shows the completed state with evidence.

**Blocked by**

Choose the first field role before publishing. If no client role is known, recommended default is service boy for engineering generality, but that choice should be captured in an ADR before publish.

## Review Questions

- Is the buyer active path decision correct for v1: `requests`/`request_items`, with `order_requests`/`order_request_items` treated as legacy?
- Should the first field execution proof follow a known client role, or should we write an ADR choosing service boy by engineering generality?
- Should supplier/vendor aliasing get its own ADR before any supplier/vendor v1 issue is published?
- Publish to GitHub only after `ROADMAP.md` v1 is locked?

