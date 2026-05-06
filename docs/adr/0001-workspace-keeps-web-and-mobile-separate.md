# ADR 0001: Keep Web And Mobile As Separate Repos Under A Workspace

Date: 2026-05-06

## Status

Accepted

## Context

The workspace currently contains separate repos for `Solvesxx_web`, `Solvesxx_mobile`, and `Solvexx-landingPage-`. The product is messy, but the mess is not only caused by repo separation. The web app and mobile app have different runtimes, release paths, test tools, dependencies, and operational risks.

Merging the repos now would combine unrelated cleanup with production-readiness work and make it harder to see which app owns a defect.

## Decision

Keep the apps as separate repos for now. Use the root workspace as the coordination layer for source-of-truth docs, roadmap, status, and shared Supabase context.

## Consequences

- Root docs own product vocabulary, v1 status, roadmap, and cross-app decisions.
- App repos own implementation, tests, migrations, and app-specific documentation.
- Cross-app work must name the exact surfaces it touches: web route, mobile screen, table/RPC, storage bucket, and notification path.
- A future monorepo decision can be revisited after v1 workflows are stable.

