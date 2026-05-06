# ADR 0005: Master Data And Workflow Truth

Date: 2026-05-06

## Status

Accepted

## Context

The platform has many master-data tables and workflow tables. Recent refactoring work shows repeated helper extraction across admin, supplier bills, sale bills, employees, societies, work master, pest control, printing, inventory, and service pages.

The main risk is not missing screens; it is screens showing success while state transitions, persistence, or downstream handoffs remain fake or shallow.

## Decision

Treat master data as the base of workflow truth. A workflow is not complete until the relevant table/RPC/state transition is updated and the next role can see the result.

Core workflow truth includes:

- Buyer request, indent, PO, GRN/material receipt, purchase bill, sale bill, payment, feedback.
- Visitor entry, resident decision, checkout, notification history.
- Guard duty, GPS, checklist, panic alert, acknowledgment, resolution.
- Service request, job session, material request, evidence, completion.
- Inventory stock transactions, reorder/shortage, expiry, quality/quantity tickets.

## Consequences

- New cleanup should target workflow seams, not isolated page polish.
- State transitions should be centralized in RPCs/helpers where multiple roles depend on them.
- Tests should assert persisted records and cross-role visibility, not only UI clicks.
- Existing status constants and database enums/check constraints should be reused before adding new status strings.

