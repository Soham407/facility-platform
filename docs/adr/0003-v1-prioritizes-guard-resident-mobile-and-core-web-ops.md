# ADR 0003: v1 Prioritizes Guard + Resident Mobile And Core Web Operations

Date: 2026-05-06

## Status

Accepted

## Context

The PRDs include a broad facility platform: admin, buyer, supplier, inventory, finance, HRMS, society/security, services, AC, pest control, plantation, printing, advertising, assets, QR, reports, and mobile role apps.

The current implementation already covers many of these areas, but status evidence shows many are partial. Guard + Resident is the narrowest mobile release slice with clear client value and existing implementation momentum.

## Decision

v1 production promise is:

- Mobile: Security Guard + Resident.
- Web: the core operations required to support Guard + Resident and the basic buyer/supplier/inventory/finance path already built.

Other mobile roles and extended service modules may remain visible or partially built, but they are not v1 production commitments unless explicitly promoted.

## Consequences

- v1 issues should prefer hardening existing flows over adding modules.
- Tests and runbooks should focus first on guard duty, SOS, checklist, visitor approval/denial, notifications, admin master data, procurement, inventory receipt, billing, and field proof.
- Client demos must be explicit about what is production-supported versus preview/partial.

