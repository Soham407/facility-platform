# FacilityPlatform Context

Last updated: 2026-05-06

This workspace coordinates the Solvesxx facility management product across:

- `Solvesxx_web` - the primary Next.js web application.
- `Solvesxx_mobile` - the Expo / React Native role app.
- `Solvexx-landingPage-` - the marketing site.
- `supabase` and `Solvesxx_web/supabase` - database, RLS, storage, Edge Function, and seed assets.

The code is the source of truth for this document. PRDs describe intended scope; this file describes the product language that already exists in code, schema, routes, and tests.

## Current Stack

- Web: Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, Radix / shadcn-style primitives, Supabase, Firebase Cloud Messaging, Playwright, Vitest.
- Mobile: Expo 55, React Native 0.83, React Navigation, Zustand, React Query, Supabase, Expo Camera, Expo Location, Expo Notifications, Expo Local Authentication.
- Backend: Supabase Postgres, Auth, RLS, Storage, Realtime, RPC functions, Edge Functions.

## Workspace Roles

These are application roles found in web auth, mobile navigation, schema, and seed/migration files:

- `super_admin` - platform-level administrator with full web access.
- `admin` - company/system administrator with full web access.
- `company_md` - management dashboard / report / finance role.
- `company_hod` - company operations and HR role.
- `account` - finance and payroll role.
- `buyer` - material request, invoice acknowledgement, and feedback role.
- `supplier` - indent, PO, dispatch, and bill role.
- `vendor` - supplier-like role using the supplier portal/navigation.
- `security_guard` - guard duty, visitor entry, checklist, GPS, and SOS role.
- `security_supervisor` - security oversight, alerts, operations, and tickets role.
- `society_manager` - society oversight, resident/security operations, compliance, and service requests role.
- `resident` - visitor approvals, visitor history, notifications, and community role.
- `employee` - mobile HRMS self-service role.
- `delivery_boy` - delivery task and proof role.
- `service_boy` - field service task, material, and proof role.
- `ac_technician` - AC service task and material role.
- `pest_control_technician` - pest-control task, PPE, chemical, and proof role.
- `storekeeper` - inventory and material ticket role.
- `site_supervisor` - society, tickets, attendance, and service request role.

## Core Domain Terms

- Company: the operating organization using the platform. Code stores company setup mostly through admin/company routes, employees, users, departments, company locations, events, and system config.
- Society: a residential site managed by the platform. Societies contain buildings, flats, residents, gates/locations, visitors, guards, and society-level security operations.
- Building: a named or coded structure within a society.
- Flat: a residential unit within a building.
- Resident: a person linked to a flat. In production flows, residents should resolve through `residents.auth_user_id = auth.uid()`.
- Guard: a security employee with a `security_guards` profile and assigned location/gate. Guard identity is bridged through employee/auth records.
- Visitor: a person logged at the gate or invited by a resident. Visitor lifecycle includes entry, resident approval/denial, frequent visitor flagging, checkout, photo metadata, and resident notifications.
- Panic Alert: an emergency escalation from guard-side flows. Related code also uses guard panic alerts, alert acknowledgment, alert resolution, SMS, push, and live location.
- Daily Checklist: guard checklist items and responses for shift compliance.
- GPS Tracking: periodic guard location tracking, geofence validation, inactivity detection, and oversight visibility.
- Buyer Request: the material request surface used by buyers. Code uses both `requests`/`request_items` and legacy `order_requests`/`order_request_items`; new work should prefer the active code path it is touching and document any migration.
- Indent: internal procurement request generated or forwarded from buyer/material needs.
- Purchase Order: supplier/vendor order generated from indents and progressed through sent, acknowledged, dispatched, and received states.
- GRN / Material Receipt: goods receipt and quality/quantity checkpoint for delivered materials.
- Purchase Bill: supplier-side bill/invoice for procurement.
- Sale Bill: buyer-facing billing document.
- Reconciliation: finance matching between PO, GRN/material receipt, purchase bill, sale bill, payments, and ledger entries.
- Inventory: product stock, stock transactions, warehouses, batches, reorder rules, expiry alerts, and shortage notes.
- Service Request: operational service ticket/request for AC, pest control, plantation, printing/advertising, housekeeping, pantry, general maintenance, security services, or field work.
- Job Session: technician/service execution record with status, start/completion timing, location, and before/after/evidence media.
- Service Delivery Note: service-side delivery/completion document.
- Service Purchase Order: supplier/service-provider PO for service work.
- Work Master: configured work/task catalogue for services. Some older code/schema names use `work_master` and `services_wise_work`.
- Employee Behavior Ticket: HR/security ticket for employee conduct.
- Material Ticket: quality, quantity, or return/RTV ticket for material issues.
- RTV Ticket: return-to-vendor workflow for rejected/damaged/incorrect material.
- Notification: in-app/push/SMS message. Code uses notifications tables, notification logs/queues, FCM, MSG91, and mobile notification stores.
- Evidence: uploaded proof such as visitor photo, attendance selfie, checklist photo, service proof, delivery proof, PPE verification, job photos, or documents.

## Main Web Surfaces

The authenticated web app lives under `Solvesxx_web/app/(dashboard)`:

- `/dashboard` - role dashboards and operational overview.
- `/company` - roles, designations, employees, users, and admin/company setup.
- `/hrms` - attendance, payroll, leave, recruitment, shifts, documents, holidays, and events.
- `/inventory` - products, categories, suppliers, POs, GRN, warehouses, rates, stock, and alerts.
- `/finance` - reconciliation, supplier bills, sale bills, compliance, budget, payments, ledger, and reports.
- `/society` - societies, residents, visitors, panic alerts, emergency contacts, and security operations.
- `/guard` - guard-facing web surface.
- `/resident` - resident-facing web surface.
- `/service-requests` - service request list/board/detail/new flows.
- `/services` - AC, pest control, plantation, printing/advertising, security services, and service masters.
- `/service-boy` and `/delivery` - field execution surfaces.
- `/buyer` - buyer portal.
- `/supplier` - supplier/vendor portal.
- `/tickets` - behavior, incident, quality, and RTV ticket surfaces.
- `/reports` - analytics/reporting hub.
- `/assets` and `/scan/[id]` - assets, QR codes, QR scans, and asset scan landing.

## Main Mobile Surfaces

The mobile app routes by role:

- Guard tabs: home, checklist, visitors, contacts.
- Resident tabs: home, approvals, visitors, community, notifications.
- Oversight tabs: home, alerts, operations, tickets, announcements.
- HRMS tabs: home, attendance, leave, payslips, documents.
- Service tabs: home, tasks, materials, proof.
- Buyer tabs: home, requests, invoices, feedback.
- Supplier tabs: home, indents, orders, billing.
- Auth/onboarding: phone OTP, email login, biometric setup, profile photo, geofence calibration.

Mobile currently contains dev preview profiles and preview-safe flows. Production readiness requires validating real OTP, device camera, location, push delivery, session persistence, and release builds without preview shortcuts.

## Important State Machines

- Buyer/material request: `pending -> accepted/rejected -> indent_generated -> indent_forwarded -> indent_accepted/indent_rejected -> po_issued -> po_received -> po_dispatched -> material_received -> material_acknowledged -> bill_generated -> paid -> feedback_pending -> completed`, with `cancelled` added later in web migrations.
- Service request: `open -> assigned -> in_progress -> on_hold -> completed -> closed`, with cancellation supported.
- Job session: `started -> paused -> completed`, with cancellation supported.
- Supplier PO: active code includes `sent_to_vendor`, `acknowledged`, `dispatched`, and received/material receipt states.
- Guard visitor: entry/logged by guard, pending resident decision, approved/denied, optional frequent visitor flag, checkout.
- Panic alert: active, acknowledged, resolved.
- Mobile service tasks: assigned, in progress, awaiting material, completed/delivered, with delivery-specific picked-up/in-transit states.
- HRMS leave/payroll/documents: separate status sets exist in schema and code; new work should use the existing domain constants or database enum/check constraint.

## Storage Buckets And Media

Known buckets and evidence areas include:

- `visitor-photos` - private visitor photos.
- `visitor-evidence` - mobile visitor/checklist evidence legacy bucket reference.
- `guard-secure-media` - private panic/checklist guard media.
- `attendance-selfies` - guard attendance selfies.
- `checklist-evidence` - checklist evidence photos.
- `ppe-verification` - pest-control PPE media.
- `service-evidence` - service photos/video.
- `delivery-proof` - delivery photos/PDF proof.
- `material-arrivals` - material arrival evidence.
- `supplier-bills` - supplier bill files.
- `staff-compliance-docs` - employee/compliance documents.
- `bill-documents` or bill document storage migrations - finance bill document proof.

Private media should be read through signed URLs or RLS-protected metadata, not public links.

## Current Truth About Scope

- The web app has broad module coverage, but many high-risk workflows are still marked partial because audits found simulated paths, query mismatches, or unproven end-to-end transitions.
- The mobile app has stronger implementation coverage for role-local flows, especially guard/resident, but production confidence still depends on real backend/device/push validation.
- Guard + Resident is the narrowest realistic v1 mobile promise.
- Web v1 should focus on making existing admin, society/security, buyer, supplier, inventory, finance, and field-execution paths trustworthy instead of adding new modules.

