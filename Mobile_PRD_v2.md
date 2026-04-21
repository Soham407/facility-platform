# Facility Management & Services
## Mobile Application — Product Requirements Document v2

**Purpose**

This document is the corrected mobile-only PRD derived from the main [PRD.md](./PRD.md). It is intended to be a cleaner mobile test contract than the current [Mobile_PRD.md](./Mobile_PRD.md), while staying realistic about what the mobile app currently implements.

This version does 3 things explicitly:
- aligns mobile scope with the main system PRD
- separates currently implemented mobile workflows from partial or future scope
- adds missing mobile actors such as the Resident app

## 1. Scope

The mobile app covers operational, workforce, resident-facing, and procurement workflows that need quick action in the field. Desktop and admin-heavy setup remains outside mobile scope unless explicitly listed here.

### 1.1 Mobile Stakeholders

| Role | Primary Mobile Responsibility | Current Alignment |
| --- | --- | --- |
| Security Guard | SOS, checklist, visitor entry, contacts, patrol status | Implemented |
| Resident | visitor approval, resident notifications | Implemented |
| Security Supervisor | alerts, operations board, behavior/material tickets | Implemented |
| Society Manager | operational oversight, material-quality tickets, staff monitoring | Partial |
| Employee | attendance, leave, payslips, documents | Implemented |
| Buyer | material request, order tracking, invoice acknowledgement, feedback | Implemented for material workflow |
| Supplier / Vendor | indent response, PO acknowledgement, dispatch, billing | Implemented for core flow |
| AC Technician | assigned work, material requests, proof workspace | Partial |
| Pest Control Technician | assigned work, PPE, chemical requests, proof workspace | Partial |
| Delivery Boy | task progress, manifest view, delivery proof workspace | Partial |
| Service Boy | task progress, supply requests, proof workspace | Partial |

### 1.2 Mobile-Only Principle

The mobile app is for execution, acknowledgement, approvals, proof capture, and field visibility. It is not the primary surface for master data, policy definition, vendor onboarding, or large-scale reporting.

## 2. Alignment With Main PRD

The main [PRD.md](./PRD.md) contains both service-deployment workflows and material-supply workflows. The mobile product must not blur these.

### 2.1 Material Supply Flows Covered on Mobile

- Buyer order/request creation
- Supplier or vendor indent accept/reject
- purchase order acknowledgement
- dispatch update
- bill submission
- buyer invoice acknowledgement
- buyer feedback

### 2.2 Service Deployment Flows Covered on Mobile

- field task visibility
- attendance/proof workspace
- material request from service staff
- oversight ticket generation
- guard and resident visitor/SOS workflows

### 2.3 Desktop / Admin-Primary Areas

- master data setup
- supplier and service catalog administration
- buyer commercial configuration
- quotation comparison and allocation logic
- final finance control and reconciliation
- bulk dashboards and management reporting

## 3. Authentication & Onboarding

### 3.1 Login

- Mobile number + OTP is the primary login mode.
- Device session should remain active until logout or admin revocation.
- Role-based redirection must land users in the correct navigator after authentication.

### 3.2 First-Time Setup

- Face registration or biometric setup may be required for roles using attendance or guarded access.
- Location permission is required for geo-fenced attendance and patrol-related monitoring.
- Camera permission is required where proof, selfie attendance, or visitor capture is part of the role.

### 3.3 Current Alignment

- OTP and role-based preview/auth flows: Implemented
- biometric/face onboarding shell: Implemented
- production-grade device-policy enforcement across all flows: Partial

## 4. Security Guard App

### 4.1 Core Scope

- home dashboard with shift context
- SOS panic action
- daily checklist
- visitor entry logging
- emergency contact access

### 4.2 Required Workflow

1. Guard logs in and lands on guard home.
2. Guard can trigger SOS with location context.
3. Guard can complete operational checklist items.
4. Guard can log visitors, including frequent visitors.
5. Guard can access one-tap emergency contacts.

### 4.3 Visitor Management Dependency

- Resident must receive approval or rejection requests on mobile.
- Guard must see resident decision reflected back in the app.

### 4.4 Current Alignment

- guard home/checklist/contacts/visitor screens: Implemented
- resident decision sync in mobile experience: Implemented at app-surface level
- production SLA guarantees such as 30-second approval propagation: Partial until backend-validated

## 5. Resident App

This role must be explicit because the main PRD requires resident-side participation in visitor approval.

### 5.1 Core Scope

- approve or reject incoming visitors
- view current resident notifications
- access resident home summary

### 5.2 Required Workflow

1. Resident receives visitor alert.
2. Resident can approve or reject from mobile.
3. Guard-facing state updates after resident action.

### 5.3 Current Alignment

- resident home, approvals, notifications: Implemented
- end-to-end guard-resident sync against production backend: Partial until integrated backend validation

## 6. Security Supervisor & Society Manager App

Security Supervisor and Society Manager share an oversight shell, but the PRD expects slightly different operating emphasis.

### 6.1 Shared Scope

- live alerts
- operations board
- ticket creation and acknowledgement
- visibility into guard activity, visitors, and checklist/attendance context

### 6.2 Security Supervisor

- acknowledge alert events
- create employee-behavior tickets
- monitor guard and site operations

### 6.3 Society Manager

- oversee operations board
- create material-quality / quantity tickets
- review staff and site operations
- act on exceptions requiring management review

### 6.4 Required Ticket Types

- employee behavior
- material quality
- material quantity mismatch
- return-to-vendor / material return exception when applicable

### 6.5 Current Alignment

- alerts, operations board, behavior ticketing: Implemented
- material ticket flow with batch / quantity fields: Partial
- deeper inventory-discrepancy and RTV loop tied to backend inventory control: Future / Partial

## 7. HRMS Mobile

### 7.1 Employee Self-Service

- selfie + geo-fenced attendance
- leave request submission
- payslip visibility
- document vault visibility

### 7.2 Required Workflow

1. Employee checks attendance state.
2. Employee submits leave request.
3. Employee can view latest payslip row.
4. Employee can access employment documents.

### 7.3 Main PRD Dependency

The main PRD also expects approval routing and payroll/document access. Mobile scope covers employee self-service first.

### 7.4 Current Alignment

- attendance, leave, payslips, documents: Implemented
- manager approval workflow inside mobile app: Partial / not primary mobile scope
- reliable downloadable payslip PDF links in all environments: Partial

## 8. Service Workflow Apps

These roles share a common mobile field-work shell. The corrected scope should separate what is currently reliable from what is still aspirational.

### 8.1 Shared Field Scope

- assigned task visibility
- work progression visibility
- material request submission
- attendance/proof workspace

### 8.2 AC Technician

- receives AC complaint/task
- views parts/equipment requests
- can raise spare/material request
- uses proof workspace

Current alignment:
- task visibility and material request loop: Implemented
- end-to-end camera/location-backed completion and manager notification closure: Partial

### 8.3 Pest Control Technician

- PPE checklist
- chemical/material request
- task visibility
- proof workspace

Current alignment:
- PPE + material request flow: Implemented
- resident pre-service notification and final compliance closure: Partial

### 8.4 Delivery Boy

- delivery task visibility
- manifest view
- status/proof workspace

Current alignment:
- task + manifest + proof workspace: Implemented
- strict completion proof and buyer/admin notification chain: Partial

### 8.5 Service Boy

- task visibility
- supply/material request
- proof workspace

Current alignment:
- task + supply request flow: Implemented
- rich completion proof and downstream inventory deduction: Partial

## 9. Buyer App

The main PRD contains both service-subscription buyer behavior and material-supply buyer behavior. The current mobile app aligns with the material-supply path and should be defined that way unless expanded.

### 9.1 Mobile Buyer Scope

- create material/procurement request
- track request pipeline
- review invoice
- acknowledge or dispute invoice
- submit delivery/quality feedback

### 9.2 Explicit Non-Scope For Current Buyer Mobile

- PO generation by buyer
- master commercial setup
- service grade/designation planning
- subscription renewal/cancellation orchestration

### 9.3 Required Workflow

1. Buyer creates request.
2. Buyer sees request in pipeline.
3. Buyer acknowledges invoice.
4. Buyer submits feedback.

### 9.4 Current Alignment

- material request, invoice acknowledgement, feedback: Implemented
- buyer-side quotation/commercial acceptance from broader service PRD: Future / not in current mobile app

## 10. Supplier / Vendor App

Supplier and Vendor mobile currently map best to the material-supply workflow from the main PRD.

### 10.1 Mobile Supplier Scope

- review forwarded indent
- accept or reject indent
- acknowledge purchase order
- update dispatch details
- submit supplier bill

### 10.2 Optional Future Scope

- ETA tracking
- challan / delivery-note attachment upload
- personnel credential attachment for service deployment
- deeper payment tracking states beyond basic queue visibility

### 10.3 Required Workflow

1. Supplier receives forwarded indent.
2. Supplier accepts indent.
3. Supplier acknowledges PO.
4. Supplier enters dispatch details.
5. Supplier submits bill.

### 10.4 Current Alignment

- core indent -> PO -> dispatch -> bill flow: Implemented
- upload-heavy logistics and deep finance tracking: Partial / Future

## 11. Notifications

### 11.1 Critical Mobile Notifications

- SOS / panic
- visitor at gate
- inactivity / patrol issue
- new indent
- order status change
- leave status update
- material/service exception alerts

### 11.2 Current Alignment

- notification surfaces are represented in mobile role workflows
- exact push delivery guarantees, escalation timing, and SMS fallback require backend validation and should not be assumed complete from UI alone

## 12. Non-Functional Requirements

### 12.1 Platforms

- Android required
- iOS supported where business rollout requires it

### 12.2 Performance

- core role dashboard should load quickly on common mid-range devices
- important actions should provide immediate visible acknowledgement

### 12.3 Offline / Degraded Operation

- critical actions should queue or degrade gracefully where feasible
- offline guarantees must be defined per workflow, not assumed universally

### 12.4 Security & Privacy

- role-based access only
- PII minimization for visitor and staff data
- retention policy for visitor media and contact details

## 13. Out of Scope

- master data management
- role/designation/product/supplier master maintenance
- complex MIS / BI dashboards
- bulk finance reconciliation
- admin allocation and workflow orchestration consoles
- desktop-first reporting and exports

## 14. Implementation Alignment Snapshot

This snapshot is intended to keep product expectations honest during E2E planning.

| Area | Status | Note |
| --- | --- | --- |
| Guard operational app | Implemented | Core screens and workflow surfaces exist |
| Resident visitor approval app | Implemented | Must remain part of mobile scope |
| Oversight app | Implemented / Partial | Core alerts and tickets exist; deeper material exception flow still maturing |
| HRMS employee self-service | Implemented | Manager-side approval loop is not equally mature on mobile |
| Buyer material workflow | Implemented | Material-oriented, not full buyer subscription/service scope |
| Supplier/vendor material workflow | Implemented | Core dispatch and billing flow exists |
| AC technician workflow | Partial | Reliable task/material flow exists; richer completion proof still maturing |
| Pest technician workflow | Partial | PPE + materials strong; full resident/compliance workflow still broader than app proof |
| Delivery workflow | Partial | Good task/manifest base; final delivery proof chain can deepen |
| Service boy workflow | Partial | Good task/material base; deeper closure/inventory coupling remains future work |

## 15. Next Product Decisions Needed

Before using mobile E2E as strict PRD compliance evidence, these decisions should be locked:

1. Should Buyer mobile remain material-only, or expand to the service-subscription workflow from the main PRD?
2. Should Supplier/Vendor mobile include delivery-note uploads and detailed payment state tracking in the current phase?
3. Is Resident app officially first-class scope in mobile release planning? It should be.
4. Which service-role completion requirements are mandatory now versus phase-next: GPS, before/after proof, resident notifications, stock deduction?
5. Is HRMS manager approval a required mobile feature or a desktop/admin responsibility for this phase?

## 16. Use In QA

When writing E2E against this PRD:
- treat each role section as the acceptance source of truth
- mark each item as Implemented, Partial, Future, or Not Automated
- do not claim PRD compliance for items intentionally marked Partial or Future

