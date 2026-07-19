# FacilityPlatform Workspace

This repository is a workspace entrypoint for the FacilityPlatform projects.

Start here:

- `CONTEXT.md` - current product vocabulary, route map, and role-routing reality found in code.
- `STATUS.md` - current-state status of website, mobile, workspace, and shared backend.
- `ROADMAP.md` - narrow v1 / v2 / not-doing scope.
- `docs/INDEX.md` - documentation map across workspace, web, and mobile.
- `docs/adr/` - accepted architecture and product-scope decisions.
- `WORKSPACE_MAP.md` - workspace layout plus document authority rules.

It preserves:

- planning and audit documents in the root
- `Solvesxx_web` as a Git submodule
- `Solvesxx_mobile` as a Git submodule
- `Solvexx-landingPage-` as a Git submodule
- shared `supabase` assets tracked directly in this repo

To clone the full workspace on another machine:

```bash
git clone --recurse-submodules https://github.com/Soham407/facility-platform.git
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

Current transfer branches:

- website: `root-wip-backup-20260406`
- mobile: `transfer/workspace-20260407`

## Current Reality

- `Solvesxx_web` is the broadest implementation surface and includes substantial Playwright/Vitest coverage assets.
- `Solvesxx_mobile` has real role navigators and Maestro-based QA assets, but it still contains explicit preview/staging-only paths that should not be mistaken for release readiness.
- Root docs should describe current code truth. PRDs, audits, and checklists remain useful, but they are not live status documents.

## Document Authority

- Current-state docs: `README.md`, `CONTEXT.md`, `STATUS.md`, `ROADMAP.md`, `WORKSPACE_MAP.md`
- Planning/spec docs: `PRD.md`, `Mobile_PRD.md`, PRD coverage matrices
- Historical evidence: audit files, release checklists, staging runbooks, `qa_agent/artifacts/*`

Older audit and PRD matrix files remain useful as evidence, but new planning should start from `STATUS.md` and `ROADMAP.md`.
