# FacilityPlatform Workspace

This repository is a workspace entrypoint for the FacilityPlatform projects.

Start here:

- `CONTEXT.md` - actual product vocabulary and architecture as found in code.
- `STATUS.md` - current v1 status across web, mobile, workspace, and shared backend.
- `ROADMAP.md` - narrow v1 / v2 / not-doing scope.
- `docs/adr/` - accepted architecture and product-scope decisions.
- `WORKSPACE_MAP.md` - workspace layout and cleanup rules.

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

Older audit and PRD matrix files remain useful as evidence, but new planning should start from `STATUS.md` and `ROADMAP.md`.
