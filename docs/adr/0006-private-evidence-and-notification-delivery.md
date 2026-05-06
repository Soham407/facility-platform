# ADR 0006: Private Evidence And Notification Delivery

Date: 2026-05-06

## Status

Accepted

## Context

The product handles privacy-sensitive media: visitor photos, guard attendance selfies, panic/checklist evidence, PPE photos, service evidence, delivery proof, material arrival proof, supplier bills, and employee documents.

The product also relies on notifications through in-app records, FCM, SMS/MSG91, queues/logs, and mobile notification stores. Current status marks notification delivery as partial because surfaces exist but production delivery is not fully proven.

## Decision

Evidence media is private by default. Use private Supabase Storage buckets, RLS-protected metadata, and signed URLs for read access. Notification success must be recorded as persisted queue/log/in-app state plus delivery validation for critical v1 paths.

## Consequences

- Avoid public URLs for visitor, guard, resident, staff, or service evidence unless the file is intentionally public.
- Critical v1 notification paths are visitor-at-gate, resident decision, guard SOS, panic acknowledgment/resolution, and procurement/status changes.
- A button that queues a toast but does not write data or notification evidence is not v1 complete.
- Real-device staging validation is required for push/location/camera behavior that browser or simulator tests cannot prove.

