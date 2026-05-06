> SUPERSEDED by `STATUS.md` (2026-05-06).
> Kept for history.

# Website Audit Report - Continuation Notes (Harsh Review Update)

**Date:** 2026-05-03
**Reviewer:** Codex
**Target Repo:** `Solvesxx_web`
**Purpose:** Replace the earlier optimistic audit with evidence from actual repo inspection, commands, and browser verification so the next session can continue without repeating the full crawl.

---

## Executive Correction

The previous audit was too generous. It inferred completeness from hook names, migrations, and route count. After actually inspecting the repo, running checks, and driving the UI, the correct read is:

- The app has broad surface area and a real Supabase-backed shell.
- Some core pages do load and show real data.
- The repo is **not in a trustworthy review state** right now.
- Several workflows are still partly simulated, manual-only, or blocked by runtime issues.
- The current working tree is missing a large amount of tracked test and support infrastructure, so claims of enterprise readiness are not defensible yet.

## Current Verification Snapshot

This is the live cleanup view for the web app. It is intentionally stricter than `PHASES.md`, because the goal here is to identify what still needs architectural work.

| Area | Status | Why |
|------|--------|-----|
| Master Data | done | Core admin and catalog masters are documented as complete in the phase ledger and are not currently a cleanup priority. |
| Supplier Workflow | done | Supplier portal, bills, indents, and POs are treated as live workflows in the phase ledger. |
| Visitor Management | done | Visitor, resident directory, and notification paths are fully represented in the phase ledger. |
| Ticket Generation | done | Behavior, quality, and RTV ticket flows are present and live. |
| Reports | done | Reports hub and subreports are modeled as live pages. |
| Services: AC / Pest / Printing | done | These service pages are present as full modules in the phase ledger. |
| Security Guard Monitoring | partial | Live audit shows simulated map/dispatch behavior and hardcoded fallback paths that still need cleanup. |
| Human Resource Management | partial | Attendance, payroll, and document flows exist, but the live audit exposed runtime issues around document handling and dashboard usage. |
| Inventory / Procurement | partial | Core purchasing exists, but reorder alert follow-through and breadcrumb route generation still need hardening. |
| Buyer / Material Supply | partial | Buyer requests are live, but billing/payment and workflow completion still have manual or environment-limited edges. |
| Finance / Audit | partial | Supplier-side finance is strong, but buyer-facing payment and closure paths still deserve verification. |
| Company Admin / Dashboard Ops | partial | Admin dashboard queries and document type coverage still need cleanup. |
| Field Execution | partial | Service boy and technician flows exist, but dashboard actions and evidence capture should be re-verified. |

See `WEB_PRD_COVERAGE_MATRIX.md` for the PRD-by-PRD breakdown.

---

## Repo State Actually Observed

### Git / working tree

- `git branch --show-current` -> `main`
- `git status --porcelain` count -> `224`
- Deleted tracked files -> `216`
- Modified tracked files -> `3`

This matters because the repo currently references many files that are not present in the working tree anymore, especially under `e2e/`, `tests/`, `scripts/`, `docs/`, and even the repo-local `PRD.md`.

### Build / validation commands actually run

- `npm run build` -> **PASS**
- `node_modules\.bin\tsc.cmd --noEmit` -> **PASS**
- `npm run test:unit` -> **FAIL** (`No test files found`)
- `npm run test:e2e:smoke -- --list` -> **FAIL** (`Cannot find module scripts/run-e2e-pack.cjs`)

Important nuance: `next build` prints `Skipping validation of types`, so the green build is not enough by itself.

### Seeded login info confirmed from repo

Found in `supabase/seeds/seed_complete.sql`:

- Test password for seed accounts: `Test@1234`
- Browser login verified with: `admin@test.com` / `Test@1234`

---

## UI Routes Actually Checked

### Public UI checked

- `/` -> loads marketing page
- `/login` -> loads login page
- Login works with `admin@test.com` / `Test@1234`

### Authenticated UI checked in browser

The following routes loaded successfully enough to inspect headings / primary content:

- `/dashboard`
- `/buyer/requests`
- `/buyer/requests/new`
- `/inventory/requests`
- `/inventory/indents/create`
- `/inventory/purchase-orders`
- `/inventory/grn`
- `/finance/supplier-bills`
- `/service-requests`
- `/services/security`
- `/guard`
- `/society/visitors`
- `/tickets/quality`

### Auth / feature-gate behavior checked

- `/settings/admins` -> redirects to `/dashboard?error=forbidden`
- `/service-requests/board` -> redirects to `/dashboard?error=feature_disabled`

So route protection is active, but this also confirms that some workflow surface still exists mostly as feature-gated inventory rather than a usable shipped module.

---

## Critical Findings

### 1. Repo integrity is bad enough to invalidate any "fully tested" claim

Evidence:

- `package.json` still advertises a large test matrix, but the current tree is missing the corresponding files and directories.
- `npm run test:unit` fails because `tests/unit` is missing.
- `npm run test:e2e:smoke -- --list` fails because `scripts/run-e2e-pack.cjs` is missing.

Relevant refs:

- `enterprise-canvas-main/package.json:12`
- `enterprise-canvas-main/package.json:40`
- `enterprise-canvas-main/package.json:45`
- `enterprise-canvas-main/package.json:53`

Harsh verdict:

This repo is currently closer to a partial extraction / damaged working tree than a clean enterprise baseline.

### 2. The main dashboard throws real runtime errors on successful login

Observed live in browser console immediately after login:

- `400` from `employee_documents?...document_type=eq.psara_license...`
- repeated `401` failures from `functions/v1/send-notification`

Root causes found in code:

- `hooks/useMDStats.ts` queries `document_type = "psara_license"`
- `hooks/useEmployeeDocuments.ts` does **not** support `psara_license` in `DocumentType`
- `hooks/useReorderAlerts.ts` sends notifications during alert fetch
- `src/lib/notifications.ts` invokes the edge function directly from the client

Relevant refs:

- `enterprise-canvas-main/hooks/useMDStats.ts:80`
- `enterprise-canvas-main/hooks/useEmployeeDocuments.ts:10`
- `enterprise-canvas-main/hooks/useReorderAlerts.ts:105`
- `enterprise-canvas-main/src/lib/notifications.ts:18`

Harsh verdict:

The admin dashboard is not clean. It is producing backend and edge-function errors during a normal happy-path login.

### 3. Security operations still contain demo-grade behavior

Found in code:

- Live map is explicitly simulated with pseudo-random placement instead of true coordinates.
- Security Command Center says full map integration is "coming soon".
- Dispatch Guard action only shows a success toast; it does not persist a dispatch.
- Guard dashboard falls back to hardcoded emergency phone numbers.
- Patrol logs assign random "Zone 1-4" labels for demo display.

Relevant refs:

- `enterprise-canvas-main/components/dashboards/GuardLiveMap.tsx:57`
- `enterprise-canvas-main/components/dashboards/GuardLiveMap.tsx:71`
- `enterprise-canvas-main/app/(dashboard)/services/security/page.tsx:365`
- `enterprise-canvas-main/app/(dashboard)/services/security/page.tsx:520`
- `enterprise-canvas-main/components/dashboards/GuardDashboard.tsx:1293`
- `enterprise-canvas-main/hooks/usePatrolLogs.ts:111`

Harsh verdict:

The security workflow looks operational in the UI, but key parts are still presentation-layer simulations.

### 4. Reorder alerts are not connected to a real PO-creation workflow

Found in code:

- `useReorderAlerts.createPurchaseOrderFromAlert()` explicitly says PO creation is a placeholder and returns an error telling users to create orders manually.

Relevant refs:

- `enterprise-canvas-main/hooks/useReorderAlerts.ts:214`
- `enterprise-canvas-main/hooks/useReorderAlerts.ts:225`
- `enterprise-canvas-main/hooks/useReorderAlerts.ts:229`

Harsh verdict:

This is a broken cross-workflow promise. Inventory alerts can warn, but cannot complete the stated next step.

### 5. Breadcrumbs generate dead routes

Observed live:

- `/inventory/indents/create` triggered a `404` request to `/inventory/indents?_rsc=...`

Root cause found in code:

- `DynamicBreadcrumbs` blindly constructs parent links from URL segments.
- There is no actual `/inventory/indents` page in the route tree.

Relevant refs:

- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:23`
- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:41`
- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:54`

Harsh verdict:

Basic navigation wiring is still wrong in at least one core supply-chain path.

### 6. Field-service dashboards still ship stub actions

Found in code:

- Service Boy dashboard photo upload action is still a TODO and just shows "Coming soon!"
- Same pattern also appears in technician dashboards discovered during repo scan.

Relevant refs:

- `enterprise-canvas-main/components/dashboards/ServiceBoyDashboard.tsx:82`
- `enterprise-canvas-main/components/dashboards/ServiceBoyDashboard.tsx:84`
- `enterprise-canvas-main/components/dashboards/ServiceBoyDashboard.tsx:87`
- `enterprise-canvas-main/components/dashboards/ACTechnicianDashboard.tsx:93`
- `enterprise-canvas-main/components/dashboards/PestControlTechnicianDashboard.tsx:97`

Harsh verdict:

The field workflow is not fully executable from the dashboard layer. Critical evidence capture actions are still stubbed.

### 7. Buyer billing is not truly end-to-end

Found in code:

- Buyer invoice "Pay Online" intentionally throws a toast saying online checkout is not configured in this environment.
- The page exposes invoice actions, but one of the most important ones is knowingly non-functional.

Relevant refs:

- `enterprise-canvas-main/app/(dashboard)/finance/buyer-invoices/page.tsx:100`
- `enterprise-canvas-main/app/(dashboard)/finance/buyer-invoices/page.tsx:103`

Harsh verdict:

The buyer receivables flow is still partially manual / environment-dependent, not a verified online payment workflow.

---

## Medium Severity Findings

### Feature-freeze / scope drift is real

The codebase still contains a large amount of future-phase or frozen functionality behind flags and middleware redirects.

Relevant refs:

- `enterprise-canvas-main/src/lib/featureFlags.ts:17`
- `enterprise-canvas-main/src/lib/featureFlags.ts:86`
- `enterprise-canvas-main/proxy.ts:147`
- `enterprise-canvas-main/components/shared/RouteGuard.tsx:39`

Harsh verdict:

This repo has a lot of "there but not actually shipped" surface. Route count alone is misleading.

### Product naming is inconsistent

Observed across materials:

- Existing audit says `FacilityPro`
- Shipped UI brand is `SOLVESXX`
- `package.json` name is still `temp_next`

Relevant refs:

- `enterprise-canvas-main/package.json:2`
- `enterprise-canvas-main/src/lib/brand.ts:1`

Harsh verdict:

Repo hygiene and product identity are still messy. It feels like a renamed delivery, not a polished platform baseline.

---

## What Was Not Tested Yet

The following was **not** fully verified in this cycle:

- No data-mutating workflow was executed end-to-end in browser (to avoid polluting seeded data late in the cycle).
- No full procurement lifecycle was executed from new request -> approval -> indent -> PO -> GRN -> bill -> payout.
- No service deployment lifecycle was executed end-to-end with service delivery note + acknowledgment + supplier bill + feedback closeout.
- No role-by-role RBAC verification beyond admin login and route access spot checks.
- No PWA install / offline / camera / push-notification / mobile browser validation.
- No payment gateway / webhook validation.
- No edge-function validation beyond observing the notification failures.
- No clean-database migration replay.
- No automated test suite execution beyond confirming that the currently advertised unit and E2E entry points are broken in this working tree.

---

## Best Current Read Of Workflow Maturity

### Looks structurally real

- Buyer request creation UI
- Inventory request review UI
- Indent / PO / GRN page surface
- Supplier bills page surface
- Service requests page surface
- Society visitor page surface
- Quality tickets page surface

### Looks real but currently unstable / incomplete

- Admin dashboard KPIs and notifications
- Security command center
- Guard operations
- Reorder alert to PO handoff
- Buyer online payment flow
- Technician evidence/photo capture flows

### Explicitly frozen / not currently shipped

- Kanban board under `/service-requests/board`
- Other feature-flagged modules in `src/lib/featureFlags.ts`

---

## Resume Plan For Tomorrow

1. Start from a clean baseline question: is this repo supposed to be reviewed in its current damaged working-tree state, or should a clean checkout/worktree be used first?
2. Fix the runtime blockers first:
   - `useMDStats` invalid `psara_license` query
   - client-side notification spam / 401 edge-function failures
   - breadcrumb dead-link generation
3. Restore verification capability:
   - recover missing `tests/`, `e2e/`, and `scripts/` content or switch to a clean branch/worktree
4. Then run the real workflow pass:
   - material procurement
   - service deployment procurement
   - guard + visitor workflow
   - supplier billing / payout gates
   - buyer billing / payment flow
5. Only after that should anyone claim enterprise readiness.

---

## Bottom Line

This repo is **not a write-off**, but it is also **not honestly audit-clean**.

Right now the most accurate harsh verdict is:

- strong breadth
- mixed implementation depth
- damaged verification surface
- visible runtime errors
- several workflow handoffs still simulated or manual

That is the correct starting point for the next cycle.

---

## 2026-04-05 Delta Update

### What Was Re-Verified Today

Commands rerun against `enterprise-canvas-main`:

- `git branch --show-current` -> `main`
- `git status --porcelain` count -> `228`
- `node_modules\.bin\tsc.cmd --noEmit` -> **PASS**
- `npm run build` -> **PASS**

The repo is still in a dirty and partially damaged state. Today improved runtime behavior, not repo integrity.

### Runtime Fixes Applied And Verified

#### 1. Dashboard compliance KPI no longer throws the invalid document query

Code change:

- `hooks/useMDStats.ts` now calculates guard compliance from verified `police_verification` documents instead of querying unsupported `psara_license` values.
- `components/dashboards/MDDashboard.tsx` now labels the KPI as `Police Verification`.

Relevant refs:

- `enterprise-canvas-main/hooks/useMDStats.ts:87`
- `enterprise-canvas-main/hooks/useMDStats.ts:92`
- `enterprise-canvas-main/components/dashboards/MDDashboard.tsx:236`
- `enterprise-canvas-main/components/dashboards/MDDashboard.tsx:241`

Live browser result on `http://127.0.0.1:3001/dashboard`:

- No console errors on load.
- No `400` request from `employee_documents?...document_type=eq.psara_license...`.
- Observed request is now `employee_documents?...document_type=eq.police_verification...` -> `200`.

Harsh read:

This specific dashboard KPI is no longer broken, but the dashboard only moved from actively wrong to conditionally trustworthy.

#### 2. Passive dashboard load no longer spams the notification edge function

Code change:

- `hooks/useReorderAlerts.ts` no longer triggers outbound notification fan-out during passive alert fetch.
- The hook now only marks alert IDs as seen in-session, leaving delivery responsibility to a future server-side workflow.

Relevant refs:

- `enterprise-canvas-main/hooks/useReorderAlerts.ts:103`
- `enterprise-canvas-main/hooks/useReorderAlerts.ts:105`

Live browser result on `http://127.0.0.1:3001/dashboard`:

- No repeated `401` failures to `functions/v1/send-notification` during page load.
- No `send-notification` requests were observed in the dashboard verification pass.

Harsh read:

The notification spam is suppressed, but the repo still does not have a trustworthy server-side alerting workflow behind reorder events.

#### 3. Inventory indent breadcrumb no longer points at a missing route

Code change:

- `components/shared/DynamicBreadcrumbs.tsx` now treats `/inventory/indents` as a non-linkable ancestor.

Relevant refs:

- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:16`
- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:45`

Live browser result on `http://127.0.0.1:3001/inventory/indents/create`:

- No `_rsc` `404` request to `/inventory/indents`.
- Breadcrumb inspection shows:
  - `Home` -> `/dashboard`
  - `Inventory` -> `/inventory`
  - `Indents` -> no link
  - `Create` -> current page

Harsh read:

This navigation paper cut is fixed. It was never acceptable in a core procurement path.

### Browser State Confirmed Today

Rechecked in the running app on port `3001`:

- `/dashboard` -> loads without the prior dashboard runtime errors
- `/inventory/indents/create` -> loads cleanly; breadcrumb dead-link removed
- `/service-requests/board` -> still redirects to `/dashboard?error=feature_disabled`
- `/settings/admins` -> still redirects to `/dashboard?error=forbidden`

### Residual UI Issue Still Seen Today

- A chart sizing warning still appears in the browser console on dashboard load:
  - `The width(-1) and height(-1) of chart should be greater than 0...`

Harsh read:

The dashboard is cleaner, not clean. There is still at least one UI rendering defect left in the happy path.

### Findings That Remain Valid After Today

These earlier harsh findings still stand and were **not** fixed in this session:

- Repo verification surface is broken because `tests/`, `e2e/`, and `scripts/` assets are missing from the working tree.
- Reorder alerts still do **not** create a real purchase order workflow; the PO handoff remains a placeholder.
- Security operations still contain simulated / demo-grade behavior.
- Field-service dashboards still contain stub actions.
- Buyer online payment is still not configured as a real end-to-end workflow.
- Feature-freeze / gated-route drift is still present.

Relevant unchanged ref for the reorder-alert gap:

- `enterprise-canvas-main/hooks/useReorderAlerts.ts:181`
- `enterprise-canvas-main/hooks/useReorderAlerts.ts:192`
- `enterprise-canvas-main/hooks/useReorderAlerts.ts:199`

### Best Resume Point For Next Session

Start from here instead of redoing the basics:

1. Treat the dashboard `psara_license` failure, notification `401` spam, and indent breadcrumb `404` as **already fixed and browser-verified**.
2. Keep treating the repo as verification-damaged until the missing `tests/`, `e2e/`, and `scripts/` surface is restored or a clean checkout is used.
3. Next workflow pass should focus on what still blocks enterprise credibility:
   - real procurement lifecycle handoff
   - service workflow completion path
   - security workflow persistence vs UI simulation
   - buyer billing / payment execution
   - residual dashboard console warning

### Revised Bottom Line

The repo is in a slightly better operational state than yesterday because three real runtime defects were removed.

That does **not** change the larger verdict:

- the verification harness is still damaged
- several workflow handoffs are still manual or simulated
- enterprise-readiness claims would still be overstated

---

## 2026-04-05 Workflow Continuation - Procurement Controls Pass

### What Was Verified In This Pass

This pass focused on the procurement control chain instead of dashboard cleanup.

Browser-checked today:

- `/inventory/requests`
- `/admin/material-indents`
- `/inventory/purchase-orders`
- `/admin/service-indents`

Code-inspected today:

- `app/(dashboard)/inventory/requests/page.tsx`
- `app/(dashboard)/admin/material-indents/page.tsx`
- `app/(dashboard)/admin/service-indents/page.tsx`
- `app/(dashboard)/inventory/indents/create/page.tsx`
- `app/(dashboard)/inventory/purchase-orders/page.tsx`
- `hooks/useIndents.ts`
- `hooks/usePurchaseOrders.ts`
- `hooks/useGRN.ts`
- `hooks/useSupplierBills.ts`

### New High-Severity Finding 1. Request forwarding bypasses the approval workflow it pretends to have

What the normal indent UI says:

- `inventory/indents/create` exposes a formal path where indents can be created as draft, submitted for approval, and then separately approved.

Relevant refs:

- `enterprise-canvas-main/app/(dashboard)/inventory/indents/create/page.tsx:296`
- `enterprise-canvas-main/app/(dashboard)/inventory/indents/create/page.tsx:306`
- `enterprise-canvas-main/hooks/useIndents.ts:522`
- `enterprise-canvas-main/hooks/useIndents.ts:573`

What the forwarding hubs actually do:

- `inventory/requests` only reviews and accepts/rejects buyer requests.
- Actual material forwarding happens on `/admin/material-indents`.
- Actual service forwarding happens on `/admin/service-indents`.
- Both forwarding screens create a fresh indent and then immediately call `approveIndent(...)` before linking the request.

Relevant refs:

- `enterprise-canvas-main/app/(dashboard)/inventory/requests/page.tsx:117`
- `enterprise-canvas-main/app/(dashboard)/inventory/requests/page.tsx:224`
- `enterprise-canvas-main/app/(dashboard)/admin/material-indents/page.tsx:118`
- `enterprise-canvas-main/app/(dashboard)/admin/material-indents/page.tsx:146`
- `enterprise-canvas-main/app/(dashboard)/admin/service-indents/page.tsx:171`
- `enterprise-canvas-main/app/(dashboard)/admin/service-indents/page.tsx:193`

Browser evidence:

- Sidebar routes are explicitly split:
  - `Buyer Request Review` -> `/inventory/requests`
  - `Material Forwarding` -> `/admin/material-indents`
  - `Service Indents` -> `/admin/service-indents`
- `/admin/service-indents` showed a live accepted request with a `Generate Service Indent` action.

Relevant refs:

- `enterprise-canvas-main/components/layout/AppSidebar.tsx:139`
- `enterprise-canvas-main/components/layout/AppSidebar.tsx:140`
- `enterprise-canvas-main/components/layout/AppSidebar.tsx:283`

Harsh verdict:

This is not a clean approval chain. The system has an approval workflow on paper, then bypasses it in the operational forwarding screens by auto-approving indents during conversion.

### New High-Severity Finding 2. The UI explicitly supports direct POs outside the indent chain

Code evidence:

- `inventory/purchase-orders` exposes a direct PO dialog.
- The dialog itself says: `Create a new direct PO. For indent-based POs, use the Indents page.`
- The form only asks for supplier and commercial header fields.
- `createPurchaseOrder()` persists a draft `purchase_orders` header even when no `indent_id` is provided.

Relevant refs:

- `enterprise-canvas-main/app/(dashboard)/inventory/purchase-orders/page.tsx:204`
- `enterprise-canvas-main/app/(dashboard)/inventory/purchase-orders/page.tsx:662`
- `enterprise-canvas-main/app/(dashboard)/inventory/purchase-orders/page.tsx:670`
- `enterprise-canvas-main/app/(dashboard)/inventory/purchase-orders/page.tsx:757`
- `enterprise-canvas-main/hooks/usePurchaseOrders.ts:484`
- `enterprise-canvas-main/hooks/usePurchaseOrders.ts:489`
- `enterprise-canvas-main/hooks/usePurchaseOrders.ts:500`

Browser evidence:

- Verified live dialog text on `/inventory/purchase-orders`:
  - `Raise New Purchase Order`
  - `Create a new direct PO. For indent-based POs, use the Indents page.`
- Verified live dialog fields:
  - `Supplier`
  - `Expected Delivery`
  - `Payment Terms`
  - `Shipping Address`
  - `Notes`
- No indent selector or requisition link is part of the direct-create dialog.

Nuance:

- `sendToVendor()` does block sending a PO with zero items.
- That reduces embarrassment later, but it does not fix the control problem that header-only orphan POs can be created outside the approved-request path.

Relevant refs:

- `enterprise-canvas-main/hooks/usePurchaseOrders.ts:948`
- `enterprise-canvas-main/hooks/usePurchaseOrders.ts:952`

Harsh verdict:

The app still permits procurement to branch into an uncontrolled side road. That weakens any claim that the requisition -> approval -> PO chain is enforced.

### New Medium-Severity Finding 3. Admin workflow breadcrumbs still point at a missing `/admin` route

Browser evidence:

- `/admin/material-indents` breadcrumb renders `Admin` linking to `/admin`.
- `/admin/service-indents` breadcrumb does the same.
- Both routes triggered `_rsc` `404` failures against `/admin?...` in the browser console.

Code root cause:

- `DynamicBreadcrumbs` only exempts `/inventory/indents` from blind parent-link generation.
- `/admin` is not exempted, even though there is no actual `/admin` landing page in the route tree.

Relevant refs:

- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:16`
- `enterprise-canvas-main/components/shared/DynamicBreadcrumbs.tsx:45`

Harsh verdict:

The earlier breadcrumb fix was too narrow. Admin workflow pages still leak dead parent routes.

### Important Positive Read So This Does Not Get Misread As Total Fiction

The downstream material flow looks substantially more real than the request-forwarding layer:

- PO -> GRN creation from PO is implemented.
- GRN -> supplier bill creation is implemented.
- Supplier bills enforce accepted-GRN gating before billing.

Relevant refs:

- `enterprise-canvas-main/hooks/useGRN.ts:396`
- `enterprise-canvas-main/hooks/useGRN.ts:433`
- `enterprise-canvas-main/hooks/useSupplierBills.ts:333`
- `enterprise-canvas-main/hooks/useSupplierBills.ts:354`
- `enterprise-canvas-main/hooks/useSupplierBills.ts:413`
- `enterprise-canvas-main/hooks/useSupplierBills.ts:432`

Harsh read:

The back half of procurement is more credible than the front half. The biggest trust problem is not that PO/GRN/bill tables are fake; it is that request intake, approval discipline, and PO control are inconsistent.

### What Was Not Executed In This Pass

Still not executed end-to-end in browser:

- No actual `Generate Indent` mutation
- No actual direct PO creation
- No actual GRN creation
- No actual supplier bill creation

Reason:

- I kept this pass non-mutating so the audit remains evidence-driven without polluting seeded records mid-review.

### Best Resume Point After This Pass

If the next session continues procurement verification, start here:

1. Decide whether auto-approving indents in the forwarding hubs is intentional business policy or a workflow defect.
2. Decide whether direct POs are a legitimate exception flow or a control bug.
3. Fix the remaining `/admin` breadcrumb dead-link generation if continuing code cleanup.
4. If safe to mutate seeded data, run one controlled path end-to-end:
   - accepted request
   - forwarded indent
   - PO
   - GRN
   - supplier bill
   - payout recording

---

## 2026-04-05 Clean Baseline + First Workflow Run

### Clean Baseline Created

A detached clean audit worktree was created from current `HEAD`:

- `enterprise-canvas-main/.worktrees/audit-main-clean`
- commit: `f7947d1`

This matters because the earlier missing-verification surface was partly a damaged working-tree problem, not purely a branch problem.

### What The Clean Worktree Restored

Observed in the clean worktree:

- `tests/` present
- `e2e/` present
- `scripts/` present
- `docs/` present
- `PRD.md` present

Counts observed:

- `tests` file count -> `45`
- `e2e` file count -> `32`

Harsh read:

The dirty main worktree exaggerated how broken the harness was. The branch itself is still not clean, but it is more testable than the earlier workspace state suggested.

### Validation Results From The Clean Baseline

Commands run against `enterprise-canvas-main/.worktrees/audit-main-clean`:

- TypeScript compile using parent dependencies -> **PASS**
- `npm run test:unit` -> **FAIL** (real failing suites, not missing files)
- `npm run build` -> **PASS** after copying local `.env.local` into the worktree
- `npm run test:e2e:smoke -- --list` -> **PASS** after wiring local Playwright package paths into the worktree

Important nuance:

- The clean worktree still needs local environment bootstrap (`.env.local`) to behave like the main repo.
- The E2E runner assumes a local `node_modules/playwright` path, so the audit worktree needed Playwright package wiring before the harness became runnable.

### New Finding 1. Unit tests are real in the clean baseline, and several still fail

Observed unit suite result:

- `36` test files executed
- `31` passed
- `5` failed

Failures observed:

- `tests/unit/procurement-rate-verification.test.ts` -> mocking failure (`Cannot access 'mockSupabase' before initialization`)
- `tests/unit/service-deployment.contract.test.ts` -> missing migration file `supabase/migrations/20260401000005_patch_procurement_super_admin_policies.sql`
- `tests/unit/hrms-module.contract.test.ts` -> assertion failure
- `tests/unit/security-guard-module.contract.test.ts` -> assertion failure
- `tests/unit/service-deployment-types.contract.test.ts` -> assertion failure

Harsh verdict:

A clean baseline does **not** produce a green unit suite. That means some of the remaining problems are branch-level regressions or stale contract tests, not just workspace damage.

### New Finding 2. The first true procurement workflow audit is blocked before browser assertions

Workflow run executed:

- targeted Playwright wave-2 scenario: `procurement-material-supply-chain workflow`
- spec: `e2e/features-wave2.spec.ts`
- dispatcher: `e2e/helpers/workflows.ts`

What this scenario is supposed to verify:

- buyer request
- PO
- GRN
- supplier bill
- buyer invoice
- reconciliation
- cross-role visibility in buyer, admin, and account portals

Relevant refs:

- `enterprise-canvas-main/e2e/feature-matrix.ts:659`
- `enterprise-canvas-main/e2e/feature-matrix.ts:667`
- `enterprise-canvas-main/e2e/helpers/workflows.ts:632`
- `enterprise-canvas-main/e2e/helpers/workflows.ts:639`

Actual failure:

- The workflow dies during seeded chain creation before the browser checks start.
- Failure occurs when the helper advances the request status through forwarding states.
- The database rejects the transition with:
  - `No active rate contract found for one or more items in this indent. Verify rates before forwarding.`

Relevant refs:

- `enterprise-canvas-main/e2e/helpers/workflows.ts:377`
- `enterprise-canvas-main/e2e/helpers/workflows.ts:391`
- `enterprise-canvas-main/supabase/migrations/20260401081548_procurement_rate_verification_gate.sql:91`
- `enterprise-canvas-main/supabase/migrations/20260401081548_procurement_rate_verification_gate.sql:100`

Harsh verdict:

The first real procurement chain does not currently complete from the clean baseline. That is a much stronger result than the earlier route-only smoke checks.

### New Finding 3. The workflow fixture is likely inconsistent with the rate-verification gate

Evidence:

- `e2e/.feature-fixtures.json` captures a concrete `productId` and `supplierId` for the procurement chain.
- `scripts/provision-feature-fixtures.cjs` carries those IDs into fixture state.
- File-wide search of `scripts/provision-feature-fixtures.cjs` found no `supplier_products` or `supplier_rates` provisioning.
- The procurement gate for material forwarding explicitly requires an active supplier-product rate contract.

Relevant refs:

- `enterprise-canvas-main/e2e/.feature-fixtures.json`
- `enterprise-canvas-main/scripts/provision-feature-fixtures.cjs:615`
- `enterprise-canvas-main/scripts/provision-feature-fixtures.cjs:616`
- `enterprise-canvas-main/supabase/migrations/20260401081548_procurement_rate_verification_gate.sql:63`
- `enterprise-canvas-main/supabase/migrations/20260401081548_procurement_rate_verification_gate.sql:71`

Harsh verdict:

The procurement workflow harness appears internally inconsistent: it seeds the supplier and product identity, but not the rate-contract data the DB now requires to forward material requests.

### New Finding 4. Material forwarding UX is weaker than service forwarding UX under the same gate philosophy

Observed in code:

- `admin/service-indents` fetches and displays active rate information and disables forwarding until a valid service rate exists.
- `admin/material-indents` has no comparable rate-verification summary, no supplier-rate precheck UI, and no disabled-state guard tied to material rates.
- Yet the DB trigger still hard-blocks request forwarding when material rate contracts are missing.

Relevant refs:

- `enterprise-canvas-main/app/(dashboard)/admin/service-indents/page.tsx:66`
- `enterprise-canvas-main/app/(dashboard)/admin/service-indents/page.tsx:103`
- `enterprise-canvas-main/app/(dashboard)/admin/service-indents/page.tsx:419`
- `enterprise-canvas-main/app/(dashboard)/admin/service-indents/page.tsx:475`
- `enterprise-canvas-main/app/(dashboard)/admin/material-indents/page.tsx:85`
- `enterprise-canvas-main/app/(dashboard)/admin/material-indents/page.tsx:172`
- `enterprise-canvas-main/app/(dashboard)/admin/material-indents/page.tsx:356`

Harsh verdict:

Material procurement is currently harsher on the operator than service deployment. Service forwarding tells the user rate state up front; material forwarding appears to rely on a late DB rejection instead.

### Best Resume Point After This Run

If continuing from this checkpoint:

1. Audit `/inventory/supplier-products` and `/inventory/supplier-rates` as procurement prerequisites.
2. Decide whether the missing material rate fixtures are a harness bug only, or also reflect incomplete default platform setup.
3. Provision valid supplier-product + supplier-rate data for the clean baseline.
4. Rerun `procurement-material-supply-chain workflow` after that setup.

## Procurement Module Closure - 2026-04-05

Scope of this closure:

- This closes the procurement module audit in the clean detached baseline at `enterprise-canvas-main/.worktrees/audit-main-clean`.
- This does **not** close the full website audit.

### What was actually broken

The original procurement workflow failure was not one bug. It was a stack of mismatches:

1. Material forwarding was weaker than service forwarding.
   - `admin/material-indents` did not surface supplier-rate prerequisites up front.
   - The database still hard-blocked forwarding when material rate contracts were missing.
   - Result: operator-facing UX was relying on a late DB rejection instead of a preflight check.

2. The procurement fixture chain was incomplete for the new DB gate.
   - `scripts/provision-feature-fixtures.cjs` seeded supplier and product identity.
   - It did **not** seed the supplier-product mapping and active supplier rate rows now required by the procurement rate-verification gate.

3. The Playwright procurement helper created the indent without `supplier_id`.
   - `e2e/helpers/workflows.ts` was inserting the indent record without the supplier link.
   - That made the DB rate gate impossible to satisfy even after valid rate data existed.

4. Browser auth handoff was too soft for middleware-protected routes.
   - Login succeeded, but client-side route transitions were still bouncing back to `/login` during the E2E flow.
   - Full document navigation after login was required so the next request carried the fresh auth context through middleware.

### Additional repo/platform reality discovered during closure

The linked database is behind some repo assumptions.

Observed schema drift in the live linked DB:

- `supplier_products.is_active` does not exist
- `supplier_rates.effective_to` does not exist

Harsh implication:

Some repo code assumed a newer procurement schema than the linked environment actually provides. The fixture and verification path had to be adapted to the live schema instead of the theoretical one.

### What was changed in the clean audit baseline

Changes made to get procurement to a real pass state:

- `app/(dashboard)/admin/material-indents/page.tsx`
  - added material rate-contract summary and loading state
  - added request-item rate precheck before forwarding
  - disabled forwarding when supplier-rate coverage is incomplete
  - used active supplier contract rates for indent estimates instead of blindly trusting base product rate

- `scripts/provision-feature-fixtures.cjs`
  - now provisions supplier-product links and active supplier rates needed by the procurement chain
  - adapted to the older linked DB schema

- `e2e/helpers/workflows.ts`
  - fixed indent creation to persist `supplier_id`

- `app/login/page.tsx`
  - changed post-login navigation to full document navigation so middleware-protected routes stop bouncing to `/login`

- `e2e/helpers/auth.ts`
  - hardened login waiting logic for the E2E runner

- `tests/unit/procurement-rate-verification.contract.test.ts`
  - updated to cover the new material-procurement rate-verification contract

### Verification results

Direct verification completed in the clean audit baseline:

- Procurement rate-verification contract test: `PASS`
- TypeScript compile (`tsc --noEmit`): `PASS`
- Procurement fixture provisioning script: `PASS`
- Targeted end-to-end workflow `procurement-material-supply-chain workflow`: `PASS`

Broader procurement-billing pack result:

- parallel/default worker run: flaky due login/session routing contention
- sequential run with `--workers 1`: `12/12 PASS`

Harsh interpretation:

- Procurement business flow is now materially working in the clean baseline.
- The remaining instability is in parallel auth/session behavior of the E2E harness, not in the underlying procurement chain itself.

### Closeout verdict

This is the first module that can be called meaningfully complete from an audit standpoint.

What that means:

- procurement is now closed in the clean audit baseline
- the full website audit is still **not** complete
- residual risk remains around parallel Playwright auth/session stability
- that residual risk should be tracked as platform/test-harness instability, not as a procurement workflow failure

### Best Resume Point After Procurement Closure

If continuing tomorrow after procurement:

1. Keep using the clean detached baseline, not the dirty main worktree.
2. Treat procurement as closed unless a new regression appears.
3. Next module should be selected based on business risk, not route count.
4. If E2E parallelism matters, isolate the auth/session flake separately from module audits.

## Service Ops Deployment Chain Audit - 2026-04-05

Scope of this pass:

- This pass audited the `service deployment chain`, not the entire Service Ops module.
- `AC job execution chain` was **not** started yet because the deployment chain still had enough real defects to justify finishing this slice first.
- All work below was done in the clean detached baseline at `enterprise-canvas-main/.worktrees/audit-main-clean`.

### What was fixed in code during this pass

Service deployment had multiple separate failures, not one bug.

1. Supplier accept was blocked before the handler even ran.
   - `proxy.ts` was denying `/api/supplier/service-indent-response` with `403 Forbidden - insufficient permissions`.
   - Fix in clean baseline:
     - exempted `/api/supplier/service-indent-response` from path-level middleware RBAC
     - kept role and supplier-ownership checks inside the route

2. Supplier accept then failed inside the route.
   - The service accept route originally tried to jump request status directly from `indent_forwarded` to `po_issued`.
   - The DB request-state guard correctly rejected that skip.
   - Fix in clean baseline:
     - `app/api/supplier/service-indent-response/route.ts`
     - now advances the request through `indent_accepted` before `po_issued`
     - also accepts idempotent re-entry from `indent_accepted`

3. Admin deployment confirmation was poisoning the billing gate.
   - `components/dialogs/ServiceAcknowledgmentDialog.tsx` was overwriting `service_acknowledgments.status` to `confirmed`
   - supplier billing code only accepts `service_acknowledgments.status = 'acknowledged'`
   - Fix in clean baseline:
     - admin confirmation now keeps the acknowledgment row in `acknowledged`
     - SPO status still advances to `deployment_confirmed`

4. Service delivery UI had stale schema assumptions.
   - `components/dialogs/ServiceDeliveryNoteDialog.tsx` still queried `company_locations.name`
   - `hooks/usePersonnelDispatches.ts` still embedded a non-working join path for `service_po_id`
   - Fix in clean baseline:
     - moved location lookups to `location_name`
     - removed the broken embedded SPO join and now resolves SPO numbers separately

### Verification completed

Build/runtime verification:

- `tsc --noEmit`: `PASS`
- `npm run build`: `PASS`
- targeted service contract pack:
  - `tests/unit/service-deployment.contract.test.ts`
  - `tests/unit/service-deployment-types.contract.test.ts`
  - `tests/unit/service-delivery.contract.test.ts`
  - `tests/unit/supplier-portal.contract.test.ts`
  - `tests/unit/supplier-billing-gate.contract.test.ts`
  - result: `22/22 PASS`

Live browser verification completed against `http://127.0.0.1:3000`:

1. Admin forward
   - page: `/admin/service-indents`
   - request: `REQ-E2E-SVC-001`
   - verified supplier/rate contract surfaced in UI
   - forwarding succeeded

2. Supplier accept
   - page: `/supplier/indents`
   - `Accept` now works
   - request advanced into issued SPO state instead of dying with `403` or `500`

3. Supplier SPO acknowledgment
   - page: `/supplier/service-orders`
   - `SPO-01002` acknowledged successfully

4. Supplier delivery note upload
   - page: `/supplier/service-orders`
   - delivery note uploaded successfully
   - SPO advanced to `DELIVERY NOTE UPLOADED`

5. Admin/site confirmation
   - page: `/inventory/service-purchase-orders`
   - `Acknowledge Deployment` succeeded
   - `SPO-01002` advanced to `DEPLOYMENT CONFIRMED`

6. Supplier billing handoff
   - page: `/supplier/bills/new`
   - before the acknowledgment fix, the service bill UI showed `Acknowledgment Required`
   - after the fix and rerun, the warning disappeared and submit became enabled
   - supplier bill submission succeeded
   - created bill: `BILL-2026-000004`
   - supplier invoice number used: `SVC-E2E-001`

### Database evidence captured

Verified rows after this pass:

- request `REQ-E2E-SVC-001`
  - still linked to service indent `IND-2026-0003`
  - still linked to SPO `SPO-01002`

- service purchase order
  - `SPO-01002`
  - status: `deployment_confirmed`

- service acknowledgment
  - row exists for `SPO-01002`
  - status: `acknowledged`
  - headcount expected/received: `3 / 3`

- service delivery note
  - row exists for `SPO-01002`
  - status: `pending`

- supplier bill
  - `BILL-2026-000004`
  - linked to `SPO-01002`
  - status: `submitted`
  - payment status: `unpaid`

### Harsh findings still open

1. `personnel_dispatches` is still structurally wrong for service deployments.
   - direct DB verification proved `personnel_dispatches.service_po_id` still references `purchase_orders`, not `service_purchase_orders`
   - inserting a dispatch for `SPO-01002` fails with:
     - `insert or update on table "personnel_dispatches" violates foreign key constraint "personnel_dispatches_service_po_id_fkey"`
   - result:
     - no personnel dispatch rows were created for this deployment
     - the delivery note path looks more complete in the UI than it is in the data model
   - harsh verdict:
     - service deployment is still missing a trustworthy personnel-dispatch ledger

2. Request status propagation for service billing is still broken.
   - after successful supplier bill submission, the originating request did **not** advance
   - direct DB check shows `REQ-E2E-SVC-001` still at `po_issued`
   - direct DB verification proves why:
     - `po_issued -> bill_generated` is blocked by the generic request-state trigger as an illegal skip
   - `hooks/useSupplierPortal.ts` currently attempts that update but does not check the failed update response
   - result:
     - the bill exists
     - the request tracking trail is stale
   - harsh verdict:
     - the service billing edge works operationally but not truthfully in the request audit trail

### Service deployment verdict

This workflow is no longer stubbed.

What is now genuinely real in the clean baseline:

- admin service indent forwarding
- supplier accept
- supplier SPO acknowledgment
- delivery note upload
- admin/site deployment confirmation
- supplier bill creation

What prevents calling the service deployment chain fully closed:

- `personnel_dispatches` is still wired to the wrong table and never records the deployed staff
- request-state propagation still does not reach `bill_generated`

Harsh summary:

- the front-to-middle service deployment chain is now materially real
- the deeper traceability layer is still compromised
- this is a strong partial close on Service Ops, not a full module close

### Mutation note for tomorrow

This pass was mutating.

Live test data now exists for the clean baseline:

- request: `REQ-E2E-SVC-001`
- SPO: `SPO-01002`
- service delivery note row created
- supplier bill created: `BILL-2026-000004`

If rerunning the same chain tomorrow, either reuse this state intentionally or reset these service fixtures first.

### Best Resume Point After This Run

1. Decide whether to repair `personnel_dispatches.service_po_id` to reference `service_purchase_orders`.
2. Decide whether service requests need a separate status path, or a service-safe bridge, for `bill_generated`.
3. Only after those two structural fixes, continue to `AC job execution chain`.

## Service Ops Module Closure - 2026-04-05

This section supersedes the earlier partial Service Ops conclusion above.

Service Ops is now closed in the clean audit baseline at:

- `enterprise-canvas-main/.worktrees/audit-main-clean`

This closeout is based on live browser workflows, rebuilt production-bundle verification, direct database checks, and targeted contract coverage.

### What was fixed after the earlier partial Service Ops audit

1. Service deployment dispatch FK
   - `personnel_dispatches.service_po_id` was repointed to `service_purchase_orders`
   - migration already applied earlier in this cycle:
     - `supabase/migrations/20260405000000_service_ops_closure.sql`

2. Service billing request-state propagation
   - service supplier bills now advance the originating request to `bill_generated` through server-side DB logic instead of silently failing in the client

3. AC completion truth mismatch
   - `complete_service_task(...)` now writes both `completion_notes` and `resolution_notes`
   - UI validation now matches the DB truth rule
   - migration applied:
     - `supabase/migrations/20260405010000_service_ops_completion_truth.sql`

4. Service deployment overlap bug
   - the supplier dispatch overlap check was falsely treating withdrawn dispatches as active because of a malformed `.not(...).or(...)` filter
   - fixed in:
     - `hooks/usePersonnelDispatches.ts`
     - `components/dialogs/ServiceDeliveryNoteDialog.tsx`

5. Delivery-note verification truth gap
   - admin deployment acknowledgment now also verifies the latest service delivery note instead of leaving it permanently `pending`
   - fixed in:
     - `components/dialogs/ServiceAcknowledgmentDialog.tsx`

6. Service workflow automation debt
   - `service-deployment-chain` is no longer deferred in Wave 2
   - it now runs as a real automated workflow in:
     - `e2e/helpers/workflows.ts`
     - `e2e/feature-matrix.ts`

7. Fixture hygiene for supplier deployment staff
   - feature fixtures now release stale open dispatches for the visible supplier employee before workflow runs
   - fixed in:
     - `scripts/provision-feature-fixtures.cjs`

### Verification performed in the final closure pass

Passed:

- `npx vitest run tests/unit/service-delivery.contract.test.ts tests/unit/service-deployment.contract.test.ts tests/unit/service-ops-closure.contract.test.ts tests/unit/supplier-billing-gate.contract.test.ts`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `npx playwright test e2e/features-wave2.spec.ts --grep "service-deployment-chain workflow" --project=chromium --workers=1 --reporter=line`
- `npx playwright test e2e/features-wave2.spec.ts --grep "ac-job-execution-chain workflow" --project=chromium --workers=1 --reporter=line`

Important reproducibility note:

- the local test app runs `next start`, not `next dev`
- client-side workflow fixes were only reflected after rebuilding and restarting the test app

### Final database evidence captured

Latest service deployment run:

- request
  - `REQ-SVC-57716EB2`
  - status: `bill_generated`

- service purchase order
  - `SPO-01013`
  - status: `deployment_confirmed`

- service delivery note
  - row id: `7f88b82d-9579-4092-9cfa-eedd6b57df00`
  - status: `verified`
  - `verified_at` populated

- personnel dispatch
  - row id: `1ee126ac-7410-4309-8694-048c35a54716`
  - status: `dispatched`

- service acknowledgment
  - row id: `33c53257-34a4-492b-827d-9f8be63e1f32`
  - status: `acknowledged`
  - headcount received: `1`
  - grade verified: `true`

- supplier bill
  - `BILL-2026-000007`
  - supplier invoice: `SINV-E0AE72A5`
  - status: `submitted`

Latest AC workflow verification:

- `ac-job-execution-chain workflow` passed again after the final Service Ops closure changes
- the AC completion regression remains closed in the same rebuilt baseline

### Service Ops verdict

Service Ops is now the second module I can treat as closed in the clean audit baseline.

Closed with real end-to-end evidence:

- `service-deployment-chain`
- `ac-job-execution-chain`

Harsh summary:

- Service Ops is no longer a partial or mostly-manual claim
- the high-risk workflow defects found earlier in this module were real, and they are now fixed
- the module now has repeatable browser coverage plus DB-backed evidence

### Resume point after this closeout

Do **not** reopen Service Ops unless a fresh regression appears.

Next best audit target:

1. `Society / Security`, or
2. `HRMS`

## Real Branch Stabilization Pass - 2026-04-05

This section distinguishes module closure in the detached clean audit baseline from module closure on a real `main`-derived branch.

Real-branch stabilization was performed in:

- `enterprise-canvas-main/.worktrees/integration-main`
- branch: `integration/main-stabilize`

Reason:

- the root `enterprise-canvas-main` checkout is still heavily dirty and not a safe integration target
- a clean `main`-derived worktree was required to verify whether the closed module fixes still held in a real branch context

### Modules now re-verified on the real branch

Re-verified and closed on the integration branch:

- `procurement`
- `Service Ops`

### Real-branch delta that had to be fixed

The clean-baseline module fixes did not port as a perfect no-op.

A real branch-only client-safety defect surfaced immediately during browser verification:

1. Login redirect race after successful auth
   - first browser attempt could authenticate correctly but still bounce back to `/login`
   - root cause:
     - the login page redirected before the Supabase auth cookie was durably visible to middleware
   - result:
     - protected-route workflows could fail on the first request even though auth itself succeeded
   - fix applied in:
     - `app/login/page.tsx`
   - hardening added:
     - role extraction now tolerates `roles` as either an object or array
     - redirect now waits briefly for the persisted auth cookie before navigating

Verification of the login repair:

- minimal Playwright login loop before fix:
  - `1/5` failed by remaining on `/login`
- minimal Playwright login loop after fix:
  - `5/5` landed on `/buyer`

### Real-branch verification performed

Passed on `integration/main-stabilize`:

- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npx vitest run tests/unit/procurement-rate-verification.contract.test.ts tests/unit/service-delivery.contract.test.ts tests/unit/service-deployment-types.contract.test.ts tests/unit/service-deployment.contract.test.ts tests/unit/service-ops-closure.contract.test.ts tests/unit/supplier-billing-gate.contract.test.ts tests/unit/supplier-portal.contract.test.ts`
- `npm run build`
- `npm run test:e2e:setup:roles`
- `npm run test:e2e:setup:features`
- `npx playwright test e2e/features-wave2.spec.ts --grep "procurement-material-supply-chain workflow" --project=chromium --workers=1 --reporter=line`
- `npx playwright test e2e/features-wave2.spec.ts --grep "service-deployment-chain workflow" --project=chromium --workers=1 --reporter=line`
- `npx playwright test e2e/features-wave2.spec.ts --grep "ac-job-execution-chain workflow" --project=chromium --workers=1 --reporter=line`

Important DB / migration note:

- `supabase migration list` confirmed that:
  - `20260405000000_service_ops_closure.sql`
  - `20260405010000_service_ops_completion_truth.sql`
  were already applied on the linked remote database
- no additional Service Ops DB push was required during this stabilization pass

### Real-branch verdict

`procurement` and `Service Ops` are no longer only "closed in the audit baseline".

They are now also closed on a clean real branch derived from `main`, with browser re-verification.

Harsh summary:

- the clean audit work was real and portable
- the real branch still exposed one important auth race that would have made the app look defective to a client
- that defect is now fixed in the integration branch
- `procurement` and `Service Ops` are the only modules I can currently treat as closed on a real branch

### Next module

Start `Society / Security` from the stabilized integration branch, not from the dirty root checkout.

## Society / Security Module Closure - 2026-04-06

This section closes `Society / Security` on the stabilized real-branch worktree:

- `enterprise-canvas-main/.worktrees/integration-main`
- branch: `integration/main-stabilize`

This was not a shallow route crawl. Closure is based on repeated browser runs, direct Supabase runtime checks under real role sessions, targeted contract coverage, and schema repairs where the linked database had drifted from the repo.

### What was actually broken during this pass

The harsh version:

1. Resident invite flow was still broken
   - the resident portal still used a raw `visitors` insert path
   - live failure: `42P17 infinite recursion detected in policy for relation "visitors"`

2. Resident complaint / service-request flow was broken
   - the resident dashboard passed the resident-row UUID into `service_requests.requester_id`
   - live `service_requests` RLS expected the auth user id, not the resident table id
   - the table also had no self-create insert policy for this browser path

3. Panic alert history page was partially broken
   - `usePanicAlertHistory` still asked PostgREST for `resolver:employees!panic_alerts_resolved_by_fkey(...)`
   - live failure: `PGRST200 Could not find a relationship between 'panic_alerts' and 'employees' in the schema cache`
   - result: `/society/panic-alerts` rendered `Failed to load alerts`

4. Panic alert resolution truth was broken in the linked database
   - the live `panic_alerts.resolved_by` foreign key still pointed at `users`, not `employees`
   - the app was correctly writing employee ids after the earlier hook fix
   - live failure:
     - `insert or update on table "panic_alerts" violates foreign key constraint "panic_alerts_resolved_by_fkey"`
     - detail: key not present in table `users`

5. The `security_supervisor` fixture account was not fully real
   - the auth user existed
   - the linked `users.employee_id` existed
   - but the employee row still had `auth_user_id = null`
   - result:
     - panic resolution under `security_supervisor` could only write `resolved_by = null`
     - browser verification failed the audit-truth check even after the FK repair

### What was fixed

1. Resident invite RPC repair
   - added:
     - `supabase/migrations/20260406012000_security_ops_resident_invite_rpc.sql`
   - browser hook moved from raw insert to:
     - `create_resident_invited_visitor(...)`
   - fixed in:
     - `hooks/useResident.ts`

2. Resident complaint / service-request auth contract repair
   - added:
     - `supabase/migrations/20260406013000_service_requests_self_serve_insert_policy.sql`
   - resident dashboard now uses auth user id, not resident row id, for request filtering
   - resident complaint creation no longer forces `requester_id = residentId`
   - fixed in:
     - `components/dashboards/ResidentDashboard.tsx`

3. Panic alert history query repair
   - removed the unnecessary `resolver` join from the panic history fetch
   - fixed in:
     - `hooks/usePanicAlertHistory.ts`

4. Panic alert resolution FK repair
   - added:
     - `supabase/migrations/20260406014000_panic_alerts_resolved_by_fk_repair.sql`
   - this migration:
     - drops the stale `panic_alerts_resolved_by_fkey`
     - maps old auth-user values to `employees.id`
     - nulls irreparable leftovers
     - recreates the FK against `public.employees(id)`

5. Fixture repair for employee linkage drift
   - `scripts/provision-feature-fixtures.cjs`
   - `ensureEmployee(...)` now repairs stale existing employee rows instead of accepting them unchanged
   - this was required to repair `supervisor@test.com` -> employee linkage in the current linked database

6. UI verification pack updates
   - `e2e/society-security-interactions.spec.ts`
   - resident quick actions were updated to match the real UI contract:
     - notifications live in the global header bell popover
     - complaint copy is now `Raise Request` / `Raise a Service Request`
   - the prior test expectations were stale, but the resident invite and resident complaint failures behind them were real and were fixed first

### Direct runtime verification performed

Passed:

- `npx vitest run tests/unit/security-guard-module.contract.test.ts tests/api/resident-module.contract.spec.ts tests/unit/visitor-lifecycle.contract.test.ts tests/unit/notifications-module.contract.test.ts`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `supabase db push`
  - applied:
    - `20260406012000_security_ops_resident_invite_rpc.sql`
    - `20260406013000_service_requests_self_serve_insert_policy.sql`
    - `20260406014000_panic_alerts_resolved_by_fk_repair.sql`

Direct database proofs captured during this pass:

- resident invite RPC under `resident@test.com`
  - created a real pre-approved visitor row
  - verified fields:
    - `approved_by_resident = true`
    - `approval_status = 'approved'`
    - `entry_time = null`
    - `decision_at` populated

- resident service-request insert under `resident@test.com`
  - direct insert into `service_requests` now succeeds when:
    - `created_by = auth.uid()`
    - `requester_id = auth.uid()`

- panic history query under `societymanager@test.com`
  - the page query now succeeds without `PGRST200`

- panic resolution under `societymanager@test.com`
  - direct update now writes:
    - `is_resolved = true`
    - `resolved_by = <employee id>`

- panic resolution under `supervisor@test.com`
  - failed first because the employee fixture was not linked
  - passed after repairing the feature-fixture script and reprovisioning

### Browser verification performed

Passed:

- `npx playwright test e2e/guard-routine.spec.ts e2e/features-society-security.spec.ts e2e/society-security-interactions.spec.ts --project=chromium --workers=1 --reporter=line`
  - result: `36 passed, 1 skipped`

- `npx playwright test e2e/features-wave2.spec.ts --grep "visitor-society-chain workflow" --project=chromium --workers=1 --reporter=line`
  - result: `1 passed`

Important reproducibility note:

- after frontend hook changes, the local test app had to be rebuilt and restarted
- after fixture-script changes, `node scripts/provision-feature-fixtures.cjs` had to be rerun so `security_supervisor` became a real employee-linked account

### Society / Security verdict

`Society / Security` is now the third module I can treat as closed on the stabilized integration branch.

Closed with real evidence:

- resident invite flow
- resident complaint / request flow
- visitor approval / denial flow
- visitor management UI actions
- panic alert history + resolve flow
- guard routine surface
- visitor-society chain workflow

Harsh summary:

- this module was not “mostly fine”
- it had real workflow defects, real schema drift, and real seed-data dishonesty
- those issues are now repaired in the integration baseline
- the module now has repeatable browser proof, not just code review confidence

### Next best module

Start `HRMS` next from `integration/main-stabilize`.

## HRMS Module Audit - 2026-04-06

This pass audited `HRMS` on the stabilized real-branch worktree:

- `enterprise-canvas-main/.worktrees/integration-main`
- branch: `integration/main-stabilize`

This was not a route-only crawl. The main audited business chain was:

- `security_guard` attendance clock-in
- `security_guard` leave submission
- `security_supervisor` / `admin` leave-review visibility
- approved leave sync into attendance truth
- `admin` payroll-cycle creation and payslip generation
- `account` read-only payroll review

### HRMS pages and roles mapped in this pass

Primary workflow routes audited:

- `/hrms/attendance`
- `/hrms/leave`
- `/hrms/payroll`

Primary roles exercised:

- `security_guard`
- `security_supervisor`
- `admin`
- `account`

Supporting surfaces inspected for closure judgment:

- `/company/employees`
- `/hrms/leave/config`
- repo search for payroll master-data maintenance UI

### What was actually broken

The harsh version:

1. `security_supervisor` role truth was inconsistent across attendance and leave
   - the attendance page and leave page treated `security_supervisor` as a non-manager role
   - real impact:
     - supervisor could miss the `Smart Attendance` manager view
     - supervisor leave-review visibility was inconsistent with the intended workflow

2. `society_manager` route access did not match leave page behavior
   - the leave page allowed management behavior, but route RBAC still omitted `/hrms/leave`

3. Leave truth did not flow cleanly into attendance / payroll
   - approved leave needed to materialize as attendance truth
   - payroll attendance summaries also mishandled `late`, `paid_leave`, and `unpaid_leave`

4. Payroll generation SQL was not production-true against the live schema
   - the old salary-calculation path still referenced missing employee salary fields
   - real failure before repair:
     - `record "v_employee" has no field "basic_salary"`

5. Payroll UI permissions were false for read-only roles
   - `account` could see payroll mutation controls that should have been admin-only

6. Payroll smoke and workflow tests were stale against the repaired UI contract
   - account payroll smoke still expected `New Cycle`
   - the HRMS workflow harness also needed to select the generated cycle explicitly
   - a login/session flake in the auth helper could strand the smoke suite on an already-authenticated dashboard

7. The account payroll UI dropped employee identity in the real browser
   - after a successful admin-generated payroll cycle, the `account` view rendered the payslip row as `Unknown`
   - root cause:
     - `payslips` were readable
     - the `employees` join was blocked for `account` by RLS

### What was fixed

1. Attendance manager role repair
   - `app/(dashboard)/hrms/attendance/page.tsx`
   - `security_supervisor` is now treated as an attendance-manager role

2. Leave manager role and route repair
   - `app/(dashboard)/hrms/leave/page.tsx`
   - `src/lib/auth/roles.ts`
   - `security_supervisor` is now treated as a leave-manager role
   - `society_manager` route access now includes `/hrms/leave`

3. Attendance / payroll leave-status normalization
   - `hooks/useAttendance.ts`
   - `hooks/usePayroll.ts`
   - `paid_leave` and `unpaid_leave` now map correctly into attendance display and payroll summaries
   - `late` now counts as present for payroll purposes

4. Payroll action gating repair
   - `app/(dashboard)/hrms/payroll/page.tsx`
   - payroll mutation controls are now limited to `admin` and `super_admin`

5. HRMS workflow-truth migration
   - `supabase/migrations/20260406020000_hrms_workflow_truth_repairs.sql`
   - applied with `supabase db push`
   - repaired:
     - `leave_applications` RLS
     - `payroll_cycles` RLS
     - `payslips` RLS
     - leave-to-attendance sync triggers
     - geofence validation for non-clock-in attendance rows
     - salary calculation SQL against the real schema
     - payroll generation SQL so missing salary structure now fails honestly instead of crashing

6. Account payroll identity repair
   - `supabase/migrations/20260406023000_hrms_payroll_employee_visibility.sql`
   - applied with `supabase db push`
   - `account` and `super_admin` can now read employee rows required for payroll joins
   - result:
     - account payroll rows now show `Security Guard` instead of `Unknown`

7. HRMS workflow coverage hardening
   - `e2e/helpers/workflows.ts`
   - `e2e/helpers/auth.ts`
   - `e2e/feature-matrix.ts`
   - `tests/unit/hrms-module.contract.test.ts`
   - the workflow now verifies the generated cycle from the account view and asserts employee identity
   - the auth helper now clears stale cookies before retrying role login

### Verified in this pass

Database truth verified directly:

- approved leave backfills / syncs into `attendance_logs`
- direct guard leave insert under `guard@test.com` succeeds under RLS
- direct supervisor approval update succeeds under RLS
- payroll calculation now returns an honest master-data error when salary structure is missing
- after salary-structure seed data, payroll generation produces a real payslip and skips unconfigured employees explicitly
- after the employee-visibility repair, `account@test.com` can read the guard employee row and the payslip join returns the employee name

Automated verification passed:

- `npx vitest run tests/unit/hrms-module.contract.test.ts`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `npx playwright test e2e/features-hrms-service.spec.ts e2e/features-wave2.spec.ts --project=chromium --workers=1 --reporter=line --grep "hrms-(attendance|leave|payroll) smoke|hrms-attendance-leave-payroll-chain workflow"`

Browser verification passed on the live UI:

- guard dashboard showed geo-fence `Within Range (0m)` and active attendance state
- guard submitted a real leave application with reason `MCP-HRMS-20260406-BROWSER`
- supervisor attendance UI showed `Smart Attendance`
- leave-review UI showed the new guard request and final approved state
- admin created a real `June 2027` payroll cycle from the browser
- admin generated payslips from the browser and the UI showed a real computed row:
  - `Security Guard`
  - `PS-2027-06-0001`
  - `₹2,481`
- account payroll UI showed the same `June 2027` cycle in read-only mode
- account payroll UI showed `Security Guard` after the RLS repair
- account payroll UI did **not** expose `New Cycle` or `Generate Payslips`

### Untested or not fully re-audited in this pass

These HRMS surfaces were not taken through the same end-to-end browser truth chain today:

- `/hrms/recruitment`
- `/hrms/documents`
- `/hrms/shifts`
- `/hrms/holidays`
- `/hrms/events`
- `/hrms/specialized-profiles`
- full employee lifecycle from `/company/employees/create` through profile completion and payroll readiness

### Hard blocker

HRMS is still blocked from honest closure on the integration branch by missing payroll master-data maintenance.

Evidence:

- repo search found no UI route or app surface for maintaining `employee_salary_structure`
- payroll generation still depends on that master data
- the repaired SQL now reports this honestly as:
  - `Employee salary structure is not configured`
- payroll verification in this pass required DB-seeded salary structure for the guard employee

Harsh conclusion:

- the attendance -> leave -> payroll chain now works when payroll master data already exists
- the product still does not expose a credible in-app way to maintain that required salary structure
- that means payroll onboarding is not fully shippable from the UI alone

### HRMS verdict

`HRMS` is **not closed** on the stabilized integration branch.

Status by category:

- `verified`
  - attendance manager view
  - guard leave submission
  - leave approval visibility
  - leave sync into attendance truth
  - admin payroll create + generate
  - account read-only payroll review
- `fixed`
  - supervisor role mismatches
  - society-manager leave routing mismatch
  - leave/payroll status normalization
  - payroll SQL/schema drift
  - payroll action gating
  - account payroll employee-name visibility
  - stale HRMS smoke/workflow/auth harness expectations
- `untested`
  - recruitment
  - compliance/document vault
  - shift / holiday / events / specialized-profile flows
  - full employee-master-to-payroll-master onboarding
- `blocked`
  - no discoverable salary-structure maintenance UI for payroll prerequisites

Resume point if HRMS continues:

1. Build or expose a real salary-structure maintenance surface for payroll master data.
2. Re-run the attendance -> leave -> payroll chain without DB-only salary seeding.
3. Audit the remaining HRMS submodules that were not taken through browser truth in this pass.

## HRMS Module Audit Continuation - 2026-04-06

This continuation resolved the blocker above on the same stabilized integration worktree:

- `enterprise-canvas-main/.worktrees/integration-main`
- branch: `integration/main-stabilize`

The focus was not a route crawl. The specific closure target was the missing in-app payroll master-data step inside the already-audited chain:

- employee compensation setup
- attendance-backed leave truth
- payroll-cycle creation
- payslip generation
- read-only account review

### What failed in this continuation

1. The product still had no credible in-app UI to maintain `employee_salary_structure`
   - payroll depended on salary structure
   - the prior HRMS pass had to seed this in the database to complete payroll truth

2. The first compensation-UI implementation still failed the real browser workflow
   - Playwright and live browser automation reached the compensation screen
   - but the controlled numeric inputs reset before submit
   - real result:
     - `Save Compensation` produced `Configure at least one payroll component before saving.`

### What was fixed in this continuation

1. Salary-structure maintenance UI was added to the employee dossier
   - `app/(dashboard)/company/employees/[id]/page.tsx`
   - new `Compensation` tab
   - admin `Payroll Setup` entry point on the employee dossier
   - payroll-setup deep link from the employee directory

2. A real compensation editor was added for payroll prerequisites
   - `components/forms/EmployeeCompensationPanel.tsx`
   - supports the payroll component set used by the current engine:
     - `B`
     - `HRA`
     - `SA`
     - `TA`
     - `MA`
   - shows payroll readiness state and current active structure

3. Salary-structure data access and save path were added for the UI
   - `hooks/useEmployeeSalaryStructure.ts`
   - `supabase/migrations/20260406030000_hrms_salary_structure_ui_support.sql`
   - applied with `supabase db push`
   - repaired:
     - `salary_components` RLS for the live app-role model
     - `employee_salary_structure` RLS for the live app-role model
     - secure RPC `upsert_employee_salary_component(...)` for versioned in-app maintenance

4. The compensation form was repaired after the first browser failure
   - `components/forms/EmployeeCompensationPanel.tsx`
   - the failing controlled numeric inputs were replaced with a form-driven submit path that reads actual field values at save time
   - result:
     - real browser input now persists
     - compensation save now writes live salary-structure records

5. HRMS workflow coverage was updated to use the real UI instead of DB-only master-data seeding
   - `e2e/helpers/workflows.ts`
   - `tests/unit/hrms-module.contract.test.ts`
   - the workflow now configures compensation from `/company/employees/[id]?tab=compensation` before payroll generation

### Verified in this continuation

Automated verification passed:

- `npx vitest run tests/unit/hrms-module.contract.test.ts`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `npx playwright test e2e/features-hrms-service.spec.ts e2e/features-wave2.spec.ts --project=chromium --workers=1 --reporter=line --grep "hrms-(attendance|leave|payroll) smoke|hrms-attendance-leave-payroll-chain workflow"`

Browser verification passed on the live UI:

- admin opened `/company/employees/11111111-1111-1111-1111-111111111111?tab=compensation`
- compensation UI showed `Payroll Ready`
- current active structure rendered real component amounts for the guard employee
- account opened `/hrms/payroll`
- account switched to `April 2027`
- payroll registry showed a real computed row for:
  - `Security Guard`
  - `PS-2027-04-0001`
  - `₹5,295`
- account payroll remained read-only with no payroll mutation controls

### Untested in this continuation

These surfaces remain outside the browser-truth scope of this continuation and are still not re-audited here:

- `/hrms/recruitment`
- `/hrms/documents`
- `/hrms/shifts`
- `/hrms/holidays`
- `/hrms/events`
- `/hrms/specialized-profiles`

### Blocked

- none for the audited attendance -> leave -> payroll chain

### HRMS verdict after continuation

`HRMS` is **closed on the stabilized integration branch for the audited real workflow chain**.

Status by category:

- `verified`
  - in-app compensation maintenance
  - guard attendance -> leave -> approval truth
  - admin payroll create + generate
  - account read-only payroll review with employee identity visible
- `fixed`
  - missing salary-structure maintenance UI
  - salary-structure UI save path and RLS support
  - compensation form browser-input reset defect
- `untested`
  - recruitment
  - compliance/document vault
  - shift / holiday / events / specialized-profile flows
- `blocked`
  - none for the audited core chain

## Platform Master / Admin & Master Data Audit - 2026-04-06

Audit run executed on the same stabilized integration worktree only:

- `enterprise-canvas-main/.worktrees/integration-main`
- branch: `integration/main-stabilize`

This was not treated as a page crawl. The audited core workflow chains were:

- super admin:
  - `/settings/admins` invite admin
  - `/settings/permissions` mutate and save role permissions
  - `/settings/company` update system configuration
  - `/settings/audit-logs` verify audit truth
- admin:
  - `/company/designations` create designation
  - `/company/employees/create` onboard employee against real designation data
  - `/company/users` provision linked application user
- admin:
  - `/company/locations` create and edit operational site master data

### What failed

1. Platform configuration was still gated as admin-only instead of permission truth
   - `/settings/company` and `useSystemConfig` were not aligned with `platform.config.manage`

2. Employee onboarding UI was lying about persisted workflow
   - create-employee exposed fake role/location expectations that were not actually persisted by that flow

3. Company locations was audit-false placeholder UI
   - `/company/locations` exposed dead actions and no real create/edit persistence

4. Designations failed live admin workflow with `403`
   - real browser flow hit `rest/v1/designations?select=*`
   - this was a database truth defect, not just a UI issue

5. User provisioning page crashed in the real UI
   - `/company/users` rendered Radix Select with an empty item value
   - live runtime error:
     - `A <Select.Item /> must have a value prop that is not an empty string.`

6. Provisioning dialog did not refresh the parent table after success
   - the modal advanced to the temporary-password state
   - but the newly created row was not guaranteed to appear in the main list until a manual refresh

7. RBAC source-of-truth contract was stale
   - the repo now enforces path access through `proxy.ts`
   - the contract still referenced removed `middleware.ts`

### What was fixed

1. System configuration permission truth was repaired
   - `hooks/useSystemConfig.ts`
   - `app/(dashboard)/settings/company/page.tsx`
   - `supabase/migrations/20260406040000_platform_master_system_config_permission_truth.sql`
   - `tests/rls/platform-master-system-config.contract.spec.ts`
   - `tests/unit/platform-master.contract.test.ts`

2. Employee onboarding was made audit-honest
   - `hooks/useEmployees.ts`
   - `app/(dashboard)/company/employees/create/page.tsx`
   - fake role/location persistence claims were removed
   - designation selection now uses real designation master data

3. Real location CRUD replaced placeholder UI
   - `src/types/company.ts`
   - `hooks/useCompanyLocations.ts`
   - `components/dialogs/CompanyLocationDialog.tsx`
   - `app/(dashboard)/company/locations/page.tsx`
   - dead placeholder actions were removed
   - real create, edit, activate, and deactivate flows were wired to Supabase

4. Designations and company-locations master-data RLS truth was repaired
   - `supabase/migrations/20260406050000_platform_master_master_data_rls_truth.sql`
   - `tests/rls/platform-master-master-data.contract.spec.ts`
   - admin-tier write access now matches the live app-role model
   - authenticated read access now supports real workflow loading

5. User provisioning runtime and refresh defects were repaired
   - `components/dialogs/ProvisionUserDialog.tsx`
   - empty Select item value was replaced with a sentinel option
   - successful provisioning now triggers parent refresh before the temporary-password handoff screen

6. The stale RBAC source contract was repaired
   - `tests/rls/rbac-source.contract.spec.ts`
   - contract now points at `proxy.ts`

7. Platform runtime workflow coverage was made audit-truthful
   - `e2e/helpers/workflows.ts`
   - the `super-admin-runtime-chain` scenario now mutates role permissions through `/settings/permissions`
   - DB-side role edits are no longer used as a shortcut for that verification

### Verified

Automated verification passed:

- `npx vitest run tests/unit/platform-permissions.test.ts tests/unit/platform-audit.test.ts tests/unit/company-module.contract.test.ts tests/unit/platform-master.contract.test.ts tests/unit/auth-roles.test.ts tests/api/super-admin-admins.contract.spec.ts tests/rls/rbac-source.contract.spec.ts tests/rls/platform-master-system-config.contract.spec.ts tests/rls/platform-master-master-data.contract.spec.ts`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `npx playwright test e2e/features-platform-master.spec.ts e2e/features-wave2.spec.ts --project=chromium --workers=1 --reporter=line --grep "company-users smoke|company-designations smoke|company-locations smoke|super-admin-runtime-chain smoke|super-admin-runtime-chain workflow"`

Browser verification passed on the live UI:

- super admin updated `/settings/company` and audit logs showed `system_config.updated`
- super admin invited real admin `Audit Platform Admin 738295`
- super admin verified `/settings/permissions` save path with a non-critical role
  - toggled `Buyer` `platform.audit_logs.view` on
  - saved successfully
  - audit logs showed `role.permissions_updated`
  - toggled the same permission back off
  - audit logs showed the reversal to preserve baseline state
- admin created designation `Audit Designation AUD-053360`
- admin created employee `Audit Employee053360`
- admin provisioned linked user `audit.employee.053360@example.com`
- admin created and edited location `Audit Gate AUDLOC-617344`

### Untested or only smoke-verified in this pass

These surfaces were not taken through the same harsh end-to-end mutation chain today:

- deeper admin lifecycle beyond invite generation:
  - admin suspension
  - admin role reassignment
  - password-reset follow-through
- broader company-master surfaces outside the audited chain
- non-platform operational master pages that appear under other module families

### Blocked

- none for the audited Platform Master / Admin & Master Data core workflow chain

### Platform Master verdict

`Platform Master / Admin & Master Data` is **closed on the stabilized integration branch for the audited real core workflow chain**.

Status by category:

- `verified`
  - platform admin invite
  - role-permission save and audit persistence
  - system configuration update
  - audit-log truth
  - designation -> employee -> linked user provisioning chain
  - location create/edit persistence
- `fixed`
  - permission-model mismatch on system configuration
  - false employee-onboarding claims
  - dead company-locations UI
  - designations/company-locations RLS defects
  - company-users runtime crash
  - user-list refresh bug after provisioning
  - stale RBAC contract source
- `untested`
  - broader master-data and admin-maintenance surfaces outside the chain above
- `blocked`
  - none

## HRMS Secondary Surfaces Audit - 2026-04-06

This pass finished the previously deferred `HRMS` secondary surfaces on the same stabilized integration worktree:

- `enterprise-canvas-main/.worktrees/integration-main`
- branch: `integration/main-stabilize`

The audited browser-truth surfaces were:

- `/hrms/recruitment`
- `/hrms/documents`
- `/hrms/shifts`
- `/hrms/holidays`
- `/hrms/events`
- `/hrms/specialized-profiles`

### What failed

1. Recruitment BGV truth was incomplete
   - candidates in `background_check` could still be advanced to `offered` without all required BGV rows being verified
   - the page exposed no real in-page verify/reject path for police, address, education, and employment checks

2. Documents upload was broken live
   - the real `/hrms/documents` upload flow failed with `Bucket not found`
   - the linked database was missing the storage contract the UI actually uses: `employee-documents`

3. Shifts was still audit-false
   - `Create Shift` and row actions were not wired to real persistence
   - after wiring the UI, the live create path still failed because `public.shifts` was missing `description`

4. Holidays was a shallow page shell
   - `/hrms/holidays` bypassed the real hook layer and the add/remove controls were not an honest management workflow

5. Events was a shallow page shell
   - `/hrms/events` lacked a truthful schedule/update flow
   - status-only updates also needed defensive payload handling so legacy `event_name` synchronization stays safe

6. Specialized profiles lacked real maintenance UI
   - `/hrms/specialized-profiles` had no truthful add/edit path for `technician_profiles`

7. The targeted Playwright verification harness was not rerunnable
   - `scripts/provision-feature-fixtures.cjs` reused stable `employee_shift_assignments` ids without handling previously inactive rows
   - targeted smoke verification failed until fixture seeding was made idempotent

### What was fixed

1. Recruitment workflow truth
   - `hooks/useCandidates.ts`
   - `app/(dashboard)/hrms/recruitment/page.tsx`
   - required BGV types are now computed from real `background_verifications`
   - `Make Offer` is blocked until the required checks are verified
   - the BGV panel now exposes real `Verify` and `Reject` actions and refreshes candidate readiness truth

2. Documents storage + RLS truth
   - `supabase/migrations/20260406190000_hrms_secondary_surface_truth_repairs.sql`
   - restored `employee-documents` bucket
   - restored employee/admin storage policies needed by the upload/verify workflow

3. Shift management truth
   - `app/(dashboard)/hrms/shifts/page.tsx`
   - `supabase/migrations/20260406193000_hrms_shifts_description_column.sql`
   - `Create Shift` now persists real rows
   - row-level `Assign Guard` now performs real assignment updates
   - the missing `shifts.description` schema gap was repaired

4. Holiday management truth
   - `app/(dashboard)/hrms/holidays/page.tsx`
   - page now uses `useHolidays`
   - add/remove now persists against real holiday rows instead of a shallow shell

5. Events management truth
   - `app/(dashboard)/hrms/events/page.tsx`
   - `hooks/useCompanyEvents.ts`
   - schedule/complete/cancel controls are now wired to the real data layer
   - legacy `event_name` is only synchronized when title updates are actually present

6. Specialized profile truth
   - `app/(dashboard)/hrms/specialized-profiles/page.tsx`
   - `hooks/useTechnicians.ts`
   - add/edit dialogs now persist real `technician_profiles`
   - technician list refresh is now deterministic after create/update

7. Regression protection for this audit scope
   - `tests/unit/hrms-module.contract.test.ts`
   - added source contracts for recruitment gating, documents/shifts/holidays/events/specialized-profile hook wiring, and the new migrations
   - `scripts/provision-feature-fixtures.cjs`
   - shift-assignment fixture seeding is now rerunnable after manual audit mutation

### Verified

Automated verification passed:

- `npx vitest run tests/unit/hrms-module.contract.test.ts`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `npx playwright test e2e/features-hrms-service.spec.ts e2e/features-platform-master.spec.ts --project=chromium --workers=1 --reporter=line --grep "hrms-recruitment smoke|hrms-documents smoke|hrms-shifts smoke|hrms-holidays smoke|hrms-events smoke|hrms-specialized-profiles smoke"`

Real browser verification passed on the live UI:

- recruitment:
  - existing `background_check` candidate `CAND-2026-0002` could not access `Make Offer` until all four required BGV checks were verified
  - after verifying all four checks in the BGV panel, `Make Offer` became available
  - interviewing candidate `CAND-2026-003` was moved through the real UI to `background_check`
  - BGV evidence upload succeeded and the candidate persisted with `status = background_check` and `bgv_initiated_at = 2026-04-06T14:51:59.167+00:00`
- documents:
  - uploaded a real file for `AC Technician (E2E-ACTECH)`
  - verified the uploaded document through the row action menu
- shifts:
  - created `AUDIT-SHIFT-1440`
  - reassigned `Security Guard` through the real `Assign Guard` dialog
- holidays:
  - created `Audit Holiday 1441`
  - removed the same row through the live remove action
- events:
  - created `Audit Event 1442`
  - completed it through the live status action
- specialized profiles:
  - created a real specialized profile for `Society Manager (E2E-SOCIETYMGR)`
  - reopened that profile in the edit dialog and persisted updated skills/certifications:
    - `Edit Proof 1452`
    - `Edit Cert 1452`

### Untested or only partially tested in this pass

These paths were not taken through the same full mutation chain in this pass:

- recruitment:
  - screening/interview scheduling/create-candidate variations
  - offer -> hire/convert-to-employee finalization
- documents:
  - reject path
  - signed-download path
  - expiry/renewal handling
- shifts:
  - explicit unassign path
- events:
  - cancel path
- specialized profiles:
  - inactive-profile lifecycle beyond active edit/update
- historical data cleanup for legacy BGV row labels outside the required four-check workflow

### Blocked

- none for the audited HRMS secondary-surface workflow paths

### HRMS secondary verdict

`HRMS secondary surfaces` are **closed on the stabilized integration branch for the audited real workflow paths above**.

Combined with the earlier attendance -> leave -> payroll closure, `HRMS` remains closed on the stabilized integration branch for the audited workflow scope.

Status by category:

- `verified`
  - recruitment BGV start + verification gate truth
  - document upload + verify
  - shift create + assign
  - holiday add + remove
  - event schedule + complete
  - specialized profile create + edit
  - targeted Playwright smoke coverage for these surfaces
- `fixed`
  - missing `employee-documents` storage contract
  - false recruitment offer gating
  - dead shift/holiday/event/specialized-profile actions
  - missing `shifts.description` schema support
  - non-idempotent shift-assignment fixture provisioning
- `untested`
  - alternate branch actions listed above
- `blocked`
  - none

## Stabilized Integration Branch Release-Hardening Regression - 2026-04-06

### What was tested

Cross-module automated regression was rerun against the stabilized integration worktree after the core-module and HRMS-secondary audit fixes:

- `npx playwright test e2e/features-platform-master.spec.ts e2e/features-procurement-billing.spec.ts e2e/features-society-security.spec.ts e2e/features-hrms-service.spec.ts --project=chromium --workers=1 --reporter=line`
- `npx playwright test e2e/features-wave2.spec.ts --project=chromium --workers=1 --reporter=line`
- `npm run test:backend`
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
- `npm run build`
- `npm run test:unit`

This pass intentionally focused on branch-wide regression truth. No separate manual browser walkthrough was repeated beyond the live UI verification already recorded inside the individual module audit sections above.

### What failed initially

1. Service Ops board route was falsely frozen
   - `/service-requests/board` redirected to `/dashboard?error=feature_disabled` during the broad Playwright pass
   - that was a real branch regression because the Service Ops audit had already closed the board workflow as in-scope and live

2. Three unit contracts were stale or broken
   - `tests/unit/personnel-dispatch-overlap.test.ts` still asserted the older overlap-query shape
   - `tests/unit/procurement-rate-verification.test.ts` used a hoisted mock pattern that failed under Vitest module hoisting
   - `tests/unit/feature-flags.test.ts` timed out under full-suite load even though the feature-flag behavior was correct

3. Procurement-rate unit tests produced false stderr noise
   - the success-path mock did not cover the `fetchRequests()` refresh call
   - expected error paths were logging into the suite output, obscuring real regressions

### What was fixed

1. Service Ops route-freeze truth
   - `src/lib/featureFlags.ts`
   - `tests/unit/feature-flags.test.ts`
   - removed the stale `KANBAN_BOARD` freeze mapping for `/service-requests/board`
   - removed the stale `Kanban Board` frozen nav assertion

2. Stale unit contracts
   - `tests/unit/personnel-dispatch-overlap.test.ts`
   - updated the source contract to the current truthful overlap gate:
     - active-status inclusion set
     - `overlapEndDate` normalization
     - `.lte("start_date", overlapEndDate)`
     - current `.or(...)` overlap window

3. Procurement-rate test harness stability
   - `tests/unit/procurement-rate-verification.test.ts`
   - `tests/unit/procurement-rate-verification.logic.test.ts`
   - made the Supabase mock hoist-safe
   - completed the mocked request refresh path
   - suppressed expected console-error noise so the suite output stays regression-meaningful

### Verified

All branch-level automated verification listed above passed after the fixes.

Playwright branch regression outcome:

- wave 1 cross-module feature set:
  - `70/70 passed`
- wave 2 cross-role workflow set:
  - `6/6 passed`

Non-browser branch regression outcome:

- `npm run test:backend`
  - passed
- `D:\Projects\FacilityPlatform\enterprise-canvas-main\node_modules\.bin\tsc.cmd --noEmit`
  - passed
- `npm run build`
  - passed
- `npm run test:unit`
  - passed
  - `38/38` files
  - `158/158` tests

### Untested or only partially tested in this pass

- no fresh manual browser walkthrough beyond the previously recorded per-module live UI audits
- previously documented alternate-path gaps from the module sections above remain alternate-path gaps until specifically audited

### Blocked

- none for the stabilized integration branch within the already-audited workflow scope

### Stabilized branch verdict

The stabilized integration branch is **green for the audited core workflow scope plus the audited HRMS secondary surfaces**.

Status by category:

- `verified`
  - cross-module feature regression
  - cross-role workflow regression
  - backend/API/RLS/edge verification via `npm run test:backend`
  - `tsc --noEmit`
  - production build
  - full unit suite
- `fixed`
  - false Service Ops board freeze on the stabilized branch
  - stale overlap and feature-flag source contracts
  - broken/noisy procurement-rate test harness
- `untested`
  - no new manual browser pass in this release-hardening slice
  - alternate branches already called out in prior module sections
- `blocked`
  - none
