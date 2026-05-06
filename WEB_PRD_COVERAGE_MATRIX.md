> SUPERSEDED by `STATUS.md` (2026-05-06).
> Kept for history.

# Solvesxx Web PRD Coverage Matrix

This matrix is a cleanup-first view of the web app against `PRD.md`.
It is stricter than the phase ledger: if a flow still shows runtime gaps or
demo behavior in live verification, it is marked `partial` even if the phase
file currently says `FULL`.

## Status Legend

- `done` - the PRD area is live and does not need immediate architectural cleanup
- `partial` - the area exists, but there are verified gaps, manual edges, or demo behavior
- `mocked` - the area is represented by UI or placeholder behavior rather than real workflow
- `missing` - the area is not implemented in the web app

## Coverage

| PRD Area | Status | Evidence | Cleanup Focus |
|---|---|---|---|
| Scope / stakeholder model | done | Core roles and app shell are documented in `CONTEXT.md` and the role matrix is in place. | Keep the naming stable while refactoring. |
| Master Data | done | Phase ledger marks company, inventory, services, and HRMS masters as complete. | Low priority; only touch if a dependent flow breaks. |
| Facility Management & Services | partial | Service pages exist, but the live audit still found areas that behave like presentation-layer workflows. | Verify dispatch, evidence capture, and state transitions. |
| Security Guard Monitoring System | partial | Live audit found simulated map behavior, placeholder dispatch, and hardcoded fallback contacts. | Replace demo paths with persisted workflow and real location data. |
| Ticket Generation System (Employee Behaviour) | done | Behavior tickets and related ticket flows are live in the phase ledger. | Keep it aligned with shared ticket patterns. |
| Visitor Management System | done | Visitor logging, resident directory, and notification paths are live. | Preserve privacy-safe directory handling. |
| Air conditioner Services | done | AC service dashboard and technician flows are represented as complete in the phase ledger. | Maintain hook-based data access. |
| Pest Control Services | done | Pest control dashboard and technician workflows are documented as complete. | Keep PPE / chemical expiry logic coherent. |
| Printing & Advertising Services | done | Printing and ad booking are documented as live. | Keep booking dialog and ID-printing flows consistent. |
| Human Resource Management System | partial | Attendance, payroll, and employee document areas are live, but the current audit surfaced runtime cleanup work. | Fix dashboard query mismatches and document type coverage. |
| Inventory | partial | Procurement, reorder alerts, and breadcrumb navigation still show workflow friction. | Repair alert follow-through and route generation. |
| Buyer Dashboard / Material Supply Services | partial | Buyer request flows exist, but billing and completion edges are not fully trustworthy yet. | Verify end-to-end completion and payment handoff. |
| Company Admin | partial | Admin creation and management are live, but the dashboard still needs cleanup at the query edge. | Stabilize admin dashboard data loading. |
| Supplier Workflow | done | Supplier portal, bills, POs, and indents are live. | Keep the supplier seam narrow and testable. |
| Deployment / Field Execution | partial | Service boy and technician interfaces exist, but evidence-capture and action handling still need verification. | Remove stub actions and ensure persistence. |
| Financial Closure & Quality Audit | partial | Reconciliation, bills, ledger, and reports exist, but cross-workflow completion still needs confirmation. | Verify closure and payment transitions. |
| Reports | done | Reports hub and subreports are live. | Preserve the current data contract. |
| Status Tracking & Control | partial | Status transitions exist, but alert-to-action completion still needs cleanup. | Tighten the transition seams and remove placeholders. |
| Company Workflow (Admin) | partial | Admin surface is present, but it still contains the highest-risk runtime queries. | Clean up the dashboard seam first. |
| Buyer Workflow | partial | Request creation and browsing are live, but payment/completion edges remain the weak point. | Keep the workflow end-to-end, not just clickable. |
| Supplier Workflow (Material / Service) | done | Supplier-facing operations are represented as live workflows in the phase ledger. | Verify future changes do not widen the seam. |
| Financial & Feedback | partial | Feedback and billing exist, but some completion paths are still not fully trustworthy. | Remove manual-only branches where the PRD expects automation. |

## First Cleanup Targets

1. Security guard monitoring
2. Admin dashboard / HRMS query mismatches
3. Inventory alert-to-PO flow
4. Buyer billing and payment completion
5. Field execution evidence capture

## Notes

- The phase ledger currently marks almost everything as `FULL`.
- This matrix intentionally records the stricter cleanup view from live verification.
- When a row is marked `partial`, the goal is not to rewrite the whole module first.
- The goal is to find the smallest seam that makes the workflow trustworthy.
