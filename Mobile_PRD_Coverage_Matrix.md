> SUPERSEDED by `STATUS.md` (2026-05-06).
> Kept for history.

# Mobile PRD Coverage Matrix

This matrix maps the current full-role Maestro suite to [Mobile_PRD_v2.md](./Mobile_PRD_v2.md).

Status meanings:
- `Covered`: current full E2E proves the core PRD workflow
- `Partial`: some workflow is covered, but not the full PRD requirement
- `Missing`: no current full E2E coverage for that PRD requirement

## 1. Role Summary

| Role / Area | PRD Status | Current E2E | Notes |
| --- | --- | --- | --- |
| Security Guard | Partial | `guard_full_e2e.yaml` | Login, duty start, SOS, checklist submit, visitor logging, checkout, contacts covered |
| Resident | Partial | `resident_full_e2e.yaml` | Login, home, approvals, approval action, alerts covered |
| Security Supervisor | Covered | `security_supervisor_full_e2e.yaml` | Alerts, operations, behavior ticket flow covered |
| Society Manager | Partial | `society_manager_full_e2e.yaml` | Oversight and material ticket creation covered, but not all quantity/RTV business rules |
| Employee | Covered | `employee_full_e2e.yaml` | Attendance state, leave, payslips, documents covered |
| Buyer | Covered | `buyer_full_e2e.yaml` | Material request, invoice acknowledgement, feedback, PO restriction covered |
| Supplier | Covered | `supplier_full_e2e.yaml` | Indent -> PO -> dispatch -> bill covered |
| Vendor | Covered | `vendor_full_e2e.yaml` | Same core material flow as supplier covered |
| AC Technician | Partial | `ac_technician_full_e2e.yaml` | Tasks, material request, proof workspace covered; full closure/proof chain not covered |
| Pest Control Technician | Partial | `pest_control_technician_full_e2e.yaml` | PPE, materials, task visibility covered; resident notification/completion chain not covered |
| Delivery Boy | Partial | `delivery_boy_full_e2e.yaml` | Tasks, manifest, proof workspace covered; strict dispatch-to-proof completion chain still shallow |
| Service Boy | Partial | `service_boy_full_e2e.yaml` | Tasks, supply request, proof workspace covered; deeper closure/inventory coupling not covered |

## 2. PRD Section Coverage

### 2.1 Authentication & Onboarding

| Requirement | Status | Evidence |
| --- | --- | --- |
| Role-based login routes user to correct app shell | Covered | All 10 current full-role E2Es start from role preview login and land in role-specific home |
| OTP/mobile auth flow exists | Partial | Covered indirectly through preview login only, not real OTP backend validation |
| Biometric/location/camera onboarding enforcement | Partial | App has setup surfaces, but current E2Es do not prove strict device-permission enforcement |

### 2.2 Security Guard App

| Requirement | Status | Evidence |
| --- | --- | --- |
| Guard home access | Covered | `guard_full_e2e.yaml` |
| SOS panic workflow | Covered | `guard_full_e2e.yaml` |
| Daily checklist | Partial | `guard_full_e2e.yaml` covers completion and submit in preview-safe mode |
| Visitor entry logging | Covered | `guard_full_e2e.yaml` |
| Emergency contact access | Covered | `guard_full_e2e.yaml` |
| Selfie attendance / duty action | Covered | `guard_full_e2e.yaml` in preview-safe mode |
| Patrol reset / heartbeat | Covered | `guard_full_e2e.yaml` |
| Live resident-linked visitor path | Covered | `guard_resident_visitor_e2e.yaml` owns cross-role sync proof |

### 2.3 Resident App

| Requirement | Status | Evidence |
| --- | --- | --- |
| Visitor approval / rejection | Partial | `resident_full_e2e.yaml` covers approval path; deny path still missing |
| Resident notifications | Partial | `resident_full_e2e.yaml` covers alerts screen visibility, not deep notification behavior |
| Guard-resident decision sync | Covered | `guard_resident_visitor_e2e.yaml` |

### 2.4 Security Supervisor & Society Manager

| Requirement | Status | Evidence |
| --- | --- | --- |
| Alert review and acknowledgement | Covered | `security_supervisor_full_e2e.yaml`, `society_manager_full_e2e.yaml` |
| Operations board refresh and visibility | Covered | both oversight full E2Es |
| Employee behavior ticket creation | Covered | `security_supervisor_full_e2e.yaml` |
| Material quality ticket creation | Covered | `society_manager_full_e2e.yaml` |
| Material quantity mismatch workflow | Partial | society manager flow reaches quantity fields, but not full approval/discrepancy resolution loop |
| RTV / material return exception loop | Missing | not automated |

### 2.5 HRMS

| Requirement | Status | Evidence |
| --- | --- | --- |
| Attendance visibility | Covered | `employee_full_e2e.yaml` |
| Leave submission | Covered | `employee_full_e2e.yaml` |
| Leave approval / rejection by supervisor | Missing | no manager-side HRMS approval flow automated |
| Payslip visibility | Covered | `employee_full_e2e.yaml` |
| Document vault visibility | Covered | `employee_full_e2e.yaml` |
| Reliable downloadable payroll artifacts | Partial | current flow proves row visibility, not final document retrieval |

### 2.6 Service Workflow Apps

| Requirement | Status | Evidence |
| --- | --- | --- |
| AC task visibility | Covered | `ac_technician_full_e2e.yaml` |
| AC equipment/material request | Covered | `ac_technician_full_e2e.yaml` |
| AC completion with proof and manager notification | Partial | proof workspace exists, but full completion chain is not automated |
| Pest PPE checklist | Covered | `pest_control_technician_full_e2e.yaml` |
| Pest chemical request | Covered | `pest_control_technician_full_e2e.yaml` |
| Pest resident pre-service notification | Missing | not automated |
| Delivery task visibility | Covered | `delivery_boy_full_e2e.yaml` |
| Delivery manifest visibility | Covered | `delivery_boy_full_e2e.yaml` |
| Delivery status progression with final proof | Partial | proof workspace exists; deep completion rules not asserted |
| Service boy task visibility | Covered | `service_boy_full_e2e.yaml` |
| Service boy supply request | Covered | `service_boy_full_e2e.yaml` |
| Inventory deduction / downstream stock effect | Missing | not automated |

### 2.7 Buyer App

| Requirement | Status | Evidence |
| --- | --- | --- |
| Buyer can create request | Covered | `buyer_full_e2e.yaml` |
| Buyer sees request in pipeline | Covered | `buyer_full_e2e.yaml` |
| Buyer invoice acknowledgement | Covered | `buyer_full_e2e.yaml` |
| Buyer feedback submission | Covered | `buyer_full_e2e.yaml` |
| Buyer cannot generate PO from mobile | Covered | `buyer_full_e2e.yaml` with `assertNotVisible: "Generate PO"` |
| Buyer quotation/commercial acceptance from broader service PRD | Missing | not present in current mobile app flow |

### 2.8 Supplier / Vendor App

| Requirement | Status | Evidence |
| --- | --- | --- |
| Indent accept / reject | Covered | supplier/vendor full E2Es cover accept path |
| PO acknowledgement | Covered | supplier/vendor full E2Es |
| Dispatch update | Covered | supplier/vendor full E2Es |
| Bill submission | Covered | supplier/vendor full E2Es |
| ETA / delivery-note / challan upload | Missing | not automated and not strongly represented in current app |
| Payment status progression beyond bill queue visibility | Partial | billing queue covered, full finance progression not covered |

### 2.9 Notifications

| Requirement | Status | Evidence |
| --- | --- | --- |
| Role notifications surface in app flows | Partial | many screens imply notifications/state updates, but push delivery is not directly validated |
| SOS critical push + SMS chain | Missing | not automated |
| Visitor-at-gate resident alert | Missing | not automated |
| Order status push chain | Partial | workflow state changes covered, push transport itself not validated |

## 3. Full E2E Files Used

- [guard_full_e2e.yaml](./qa_agent/maestro/guard_full_e2e.yaml)
- [resident_full_e2e.yaml](./qa_agent/maestro/resident_full_e2e.yaml)
- [buyer_full_e2e.yaml](./qa_agent/maestro/buyer_full_e2e.yaml)
- [employee_full_e2e.yaml](./qa_agent/maestro/employee_full_e2e.yaml)
- [supplier_full_e2e.yaml](./qa_agent/maestro/supplier_full_e2e.yaml)
- [vendor_full_e2e.yaml](./qa_agent/maestro/vendor_full_e2e.yaml)
- [security_supervisor_full_e2e.yaml](./qa_agent/maestro/security_supervisor_full_e2e.yaml)
- [society_manager_full_e2e.yaml](./qa_agent/maestro/society_manager_full_e2e.yaml)
- [ac_technician_full_e2e.yaml](./qa_agent/maestro/ac_technician_full_e2e.yaml)
- [pest_control_technician_full_e2e.yaml](./qa_agent/maestro/pest_control_technician_full_e2e.yaml)
- [delivery_boy_full_e2e.yaml](./qa_agent/maestro/delivery_boy_full_e2e.yaml)
- [service_boy_full_e2e.yaml](./qa_agent/maestro/service_boy_full_e2e.yaml)

## 3.1 Cross-Role E2E Files Used

- [guard_resident_visitor_e2e.yaml](./qa_agent/maestro/guard_resident_visitor_e2e.yaml)

## 4. Highest-Value Gaps

These are the next gaps to close if you want PRD-level confidence instead of only implementation-level confidence.

1. Add resident deny-path coverage.
2. Deepen society manager for RTV / material return exception handling.
3. Deepen service-role flows for true completion/proof rules, not just task/material visibility.
4. Add stronger notification-side assertions where the PRD requires them.
5. Decide whether buyer/supplier mobile should include broader service-subscription/commercial workflows from the main PRD.

## 5. Current Bottom Line

The current suite is strong for:
- implemented role routing
- material workflow execution
- employee self-service
- oversight ticketing

The current suite is still weak for:
- full deny/timeout variants in guard-resident workflows
- deep service-completion rules
- strict notification and backend-SLA validation
