# FacilityPlatform Workspace Map

This root folder is a coordination layer for three separate apps plus shared assets.
It should stay small, readable, and mostly free of feature work.

## Document Classes

- Current-state docs: `README.md`, `CONTEXT.md`, `STATUS.md`, `ROADMAP.md`, `WORKSPACE_MAP.md`
- Planning/spec docs: `PRD.md`, `Mobile_PRD.md`, PRD coverage matrices
- Historical evidence: audits, release checklists, staging runbooks, `AUDIT_REPORTS/`, `qa_agent/artifacts/`

If two documents disagree, prefer the current-state docs for "what exists now" and treat PRDs/audits as intent or history.

## What Lives Here

- `PRD.md` - the client scope for the overall platform
- `README.md` - workspace entrypoint and submodule notes
- `docs/INDEX.md` - cross-workspace documentation map
- `Solvesxx_web/` - the main web application; highest priority for cleanup
- `Solvesxx_mobile/` - the mobile companion app; second priority
- `Solvexx-landingPage-/` - marketing / landing site; third priority
- `supabase/` - shared Supabase assets tracked in this workspace
- `AUDIT_REPORTS/` - historical audits and verification notes

## Working Order

1. Work in `Solvesxx_web/` first unless the task is explicitly mobile or landing-page related.
2. Use `Solvesxx_mobile/` after the web app is structurally stable.
3. Leave `Solvexx-landingPage-/` for last.
4. Treat the root folder as an index, not a feature workspace.

## Current Workspace Problem

The workspace metadata is inconsistent:

- `.gitmodules` still names the web submodule `enterprise-canvas-main`
- the actual folder in this checkout is `Solvesxx_web`
- the root git status is dirty across the root and nested repos

That mismatch is a navigation problem, not just a naming problem. It makes it harder to know which repo you are editing and which files belong to which app.

## Cleanup Rules

- Do not mix root cleanup with feature implementation.
- Do not move or rename nested repos until the submodule mapping is understood.
- Do not treat generated or temporary files as workspace structure.
- Keep new root-level docs short and explicit.

## Recommended Root-Level Docs

- `CONTEXT.md` - current product language and architecture from actual code/schema.
- `STATUS.md` - source-of-truth implementation status with explicit validation gaps.
- `ROADMAP.md` - v1 / v2 / not-doing scope.
- `docs/adr/` - decisions future agents should not re-litigate.
- `WEBSITE_AUDIT.md` - current web audit and findings
- `MOBILE_AUDIT.md` - mobile audit and findings
- `WORKSPACE_MAP.md` - this file
- `WEB_CLEANUP_BACKLOG.md` - prioritized cleanup order for `Solvesxx_web`

For new work, treat audit files as evidence, PRDs as intent, and `STATUS.md` / `ROADMAP.md` as the planning entrypoint.

## First Cleanup Tasks

- Confirm the intended submodule names and paths.
- Decide whether the root should keep the current folder names or align them with the Git metadata.
- Use one naming convention consistently across README, `.gitmodules`, and local work habits.
- Keep the web app as the canonical place for architecture cleanup.
