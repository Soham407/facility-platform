> SUPERSEDED by `STATUS.md` (2026-05-06).
> Kept for history.

# Solvesxx Web Cleanup Backlog

This is not a feature roadmap. It is the order of operations for making the web app
structurally trustworthy before more features are added.

Source inputs:

- `PRD.md`
- `Solvesxx_web/.ai_context/CONTEXT.md`
- `Solvesxx_web/graphify-out/GRAPH_REPORT.md`
- `WEBSITE_AUDIT.md`

## Priority 0: Make the repo readable

### Goal

Make it obvious what the web app contains, what is real, and what is still simulated.

### Work

- Confirm the active context docs and keep them current.
- Use the graph report and phase notes as the source of truth for module status.
- Clean up workspace naming so `Solvesxx_web` is the clear primary repo.
- Stop adding new code to shallow or temporary files unless they are part of an explicit cleanup.

### Exit criteria

- A new engineer can tell what the app is from the root docs in under five minutes.
- The web repo has one clear current context and one clear backlog source.

## Priority 1: Audit PRD coverage

### Goal

Build a factual matrix of what the client asked for versus what the app actually ships.

### Work

- Break the PRD into major modules: company, buyer, supplier, society, security, HRMS, inventory, services, finance, reports.
- Mark each item as `done`, `partial`, `mocked`, or `missing`.
- Track the highest-risk gaps first: security flows, buyer workflows, inventory workflows, and dashboard operations.
- Record which pages are real, which are gated, and which are presentation-only.

### Exit criteria

- Every major PRD section has a status.
- The team can say what is complete without relying on memory.

## Priority 2: Remove architectural friction in the web app

### Goal

Increase depth in the modules that are doing the most work.

### Highest-friction areas

- Dashboard operations
- API routes
- Inventory catalog
- Admin workflows
- HRMS attendance and payroll
- Society panic alerts

### Work

- Consolidate repeated data access into domain hooks.
- Move repeated route logic into shared helpers or a seam with one clear adapter.
- Reduce page-level duplication in dashboard and admin screens.
- Replace demo behavior with real persistence where the PRD expects actual workflow completion.

### Exit criteria

- A module can be changed in one place without editing the same rule across many pages.
- The interface is smaller than the implementation noise behind it.

## Priority 3: Fix the highest-risk user promises

### Goal

Stop the app from showing successful UI while the backend path is still fake or broken.

### Work

- Validate all major submit actions end in real persistence.
- Remove placeholder toasts for critical actions.
- Repair dead routes and broken breadcrumb assumptions.
- Check that notifications, alerts, and workflow transitions actually resolve the next step.

### Exit criteria

- A “success” action means the workflow completed, not just that the button clicked.

## Priority 4: Strengthen tests around the important flows

### Goal

Make the cleanup stick.

### Work

- Add or repair tests around the buyer, inventory, security, and admin flows.
- Keep smoke tests for the paths that matter most to the PRD.
- Use tests to lock in the new module boundaries once they are cleaned up.

### Exit criteria

- The important flows have test coverage that would catch accidental regressions.

## Practical Order To Work In

1. Workspace readability
2. PRD coverage matrix
3. Dashboard / API / inventory cleanup
4. Security and workflow correctness
5. Tests and regression locking

## What Not To Do

- Do not start by polishing UI.
- Do not build new features before the cleanup matrix exists.
- Do not treat placeholders as complete implementations.
- Do not clean the landing page before the web app is stable.
