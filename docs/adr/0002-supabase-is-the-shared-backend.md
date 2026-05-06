# ADR 0002: Supabase Is The Shared Backend

Date: 2026-05-06

## Status

Accepted

## Context

Both web and mobile use Supabase for Auth, Postgres, RLS, Storage, Realtime, and RPC/Edge Function behavior. The web repo contains the richer migration history and function set. Mobile consumes Supabase directly and through RPC functions for guard/resident/service/oversight flows.

Introducing a separate backend now would increase drift and delay v1 readiness.

## Decision

Supabase remains the shared backend for v1. Business truth should live in Postgres tables, RLS policies, RPC functions, storage metadata, and Edge Functions where the workflow needs server authority.

## Consequences

- UI-only success is not completion. v1 workflows must leave persisted records.
- Role access must be enforced by RLS/server logic, not only by web/mobile navigation.
- Mobile preview flows are allowed for development but cannot be treated as production proof.
- Schema/RPC changes should be verified against both web and mobile consumers when they touch shared flows.

