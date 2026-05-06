# ADR 0004: Roles And Auth Model

Date: 2026-05-06

## Status

Accepted

## Context

The system uses Supabase Auth with application role records and role-aware navigation. Web role access is defined in `Solvesxx_web/src/lib/auth/roles.ts`. Mobile role routing is defined in `Solvesxx_mobile/src/navigation/RoleNavigator.tsx`. Schema migrations include `roles`, `users`, `user_roles`, `role_permissions`, `employees`, `security_guards`, and `residents`.

Some identities are employee-based. Residents use resident records. Guards are employees with guard profiles. Mobile also contains dev preview profiles and demo OTP backend support.

## Decision

Keep role identity anchored in Supabase Auth plus application profile tables:

- `users`/roles for web app users.
- `employees` for workforce members.
- `security_guards` for guard-specific profile data.
- `residents` with `auth_user_id` for resident app access.
- `user_roles`/`role_permissions` where granular access is needed.

Navigation may hide routes, but RLS/RPC/server checks are the authority.

## Consequences

- New role work must update web access, mobile routing if applicable, seed data, RLS, and tests together.
- Guard logic must account for both employee identity and guard profile identity.
- Resident logic must resolve through `residents.auth_user_id = auth.uid()` for privacy-sensitive flows.
- Release builds must not depend on dev preview OTP/profiles.

