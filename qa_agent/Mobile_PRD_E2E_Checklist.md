# Mobile PRD E2E Checklist

Source: [Mobile_PRD.md](/Volumes/Soham/untitled%20folder/facility-platform/Mobile_PRD.md)

## How To Use This

- Use this as the source of truth for mobile E2E coverage.
- Mark each item as `Not Started`, `Automated`, `Manual Only`, or `Blocked`.
- Automate deterministic UI flows first.
- Leave push notifications, GPS edge cases, camera/photo upload, and cross-role approval loops as second-pass tests unless the app is already stable.

## Priority Bands

- `P0`: must work before trusting overnight E2E
- `P1`: high-value business flow
- `P2`: secondary or dependency-heavy

## Global Flows

### Authentication & Session

- `P0` Login with mobile number + OTP routes user to correct role home.
- `P0` Preview-role login routes user to correct role home in QA builds.
- `P0` Biometric setup prompt appears on first-time setup when applicable.
- `P1` Device registration / notification permission prompt appears during onboarding.
- `P1` Geo-fence calibration prompt appears during onboarding for applicable roles.
- `P1` Guard first-time flow requires profile photo capture.
- `P1` Session restores correctly on app relaunch before expiry.
- `P2` Session auto-logout after 8 hours of inactivity.

### Non-Functional / Cross-Cutting

- `P0` App launches to home in under 3 seconds on a warmed test device.
- `P1` Screens remain usable on minimum supported width.
- `P1` High-contrast / low-light readability works for guard-facing screens.
- `P2` Guard checklist works offline and syncs when network returns.
- `P2` Emergency contacts remain accessible offline.
- `P2` SOS queues offline and dispatches once network returns.

## Security Guard

### P0

- Login lands on guard home.
- Home shows SOS, Clock In/Clock Out, Daily Checklist, Emergency Contacts.
- Clock In launches attendance flow and records selfie + GPS gate.
- Clock Out follows the same gated flow.
- Daily Checklist opens with pending items for the shift.
- Checklist item can be marked with Yes/No or numeric input.
- Completed checklist submits and becomes locked.
- Emergency Contacts screen opens and exposes quick-dial items.

### P1

- SOS single tap triggers alert flow without confirmation.
- SOS remains active until acknowledged by manager flow.
- Visitor logging creates a new visitor with name, phone, photo, flat.
- Frequent visitor flow allows selecting an existing visitor instead of re-entry.
- Visitor approval result returns to guard screen.
- Parking lights checklist captures on/off state.
- Water supply checklist captures pump status and tank reading.
- Gate/shutter checklist captures lock confirmation.
- Guard can tap `I am on duty` to reset inactivity warning.

### P2

- Inactivity alert fires after 30 minutes without movement.
- Checklist reminder arrives if checklist not started by 9:00 AM.
- Continuous location streaming begins after SOS.
- Visitor SMS/push payload content is correct.

## Security Supervisor

### P0

- Login lands on monitoring dashboard.
- Dashboard shows guard map, checklist board, panic log, visitor stats, attendance.
- Panic log item opens detail view.
- Supervisor can acknowledge active SOS.

### P1

- Checklist board reflects green/red state per guard.
- Attendance drill-down shows timestamps and GPS data.
- Visitor stats drill-down opens by gate.
- Inactivity alert appears in supervisor flow.

### P2

- Guard map refreshes every 60 seconds.
- Push alerts arrive for SOS and inactivity events.

## Society Manager

### P0

- Login lands on manager oversight dashboard.
- Manager sees active panic feed and can acknowledge alerts.
- Material ticket opens from delivery-trigger workflow.
- Employee behaviour ticket can be created and submitted.

### P1

- Employee behaviour ticket captures category, severity, description, media.
- Material ticket captures quantity, quality, condition, batch, photo evidence.
- Approving material ticket completes inventory handoff state.
- Rejecting material ticket creates return/follow-up state.

### P2

- Push notification arrives when a delivery vehicle is logged.
- Low stock alert notification appears when inventory threshold is crossed.

## Employee / HRMS Staff

### P0

- Login lands on HRMS home.
- Check In requires selfie + GPS validation.
- Check Out requires selfie + GPS validation.
- Leave application can be created with type, dates, reason.
- Leave balance is visible on home or leave screen.
- Payslip list shows available monthly payslips.
- Document vault shows uploaded identity documents.

### P1

- Payslip detail shows earnings and deductions.
- Historical payslips for 12 months are accessible.
- Document replacement upload works from camera or gallery.
- Supervisor leave decision is reflected in employee app.

### P2

- Auto punch-out / supervisor flag occurs after leaving geo-fence for 15 minutes.
- Payslip-ready notification arrives.

## AC Technician

### P0

- Login lands on assigned work/task home.
- Assigned service request is visible.
- `Start Work` records timestamp and GPS.
- Before photo upload works.
- After photo upload works.
- `Complete` closes work order.

### P1

- Parts-used flow records item + quantity.
- Parts usage reduces inventory-backed selection state.
- Manager notification is sent on completion.

## Pest Control Technician

### P0

- Login lands on pest-control task home.
- PPE checklist must be completed before work can proceed.
- Attendance requires selfie + GPS.
- Before and After proof uploads work.

### P1

- Chemical request can be submitted with material + quantity.
- Work completion proof closes the task.
- Resident-facing scheduled-treatment notice is triggered by schedule.

### P2

- Manager approval path for chemical request is reflected in technician app.
- Resident push/SMS wording matches PRD intent.

## Delivery Boy

### P0

- Login lands on delivery task/order home.
- Active delivery orders are visible.
- Status can move from `Picked Up` to `In Transit`.
- Status can move from `In Transit` to `Delivered`.
- Delivery proof photo upload works.

### P1

- Buyer/admin receive visible state changes after each transition.
- Delivered state cannot be completed without proof when required.

## Service Boy

### P0

- Login lands on service task home.
- Assigned tasks are visible.
- Attendance check-in is accessible.
- Work progress/status can be updated.

### P1

- Task completion updates manager-visible state.
- Attendance follows selfie + GPS rules if service boy is under HRMS attendance.

## Buyer

### P0

- Login lands on buyer home.
- Home exposes Requests, Invoices, Feedback, and order-entry path.
- Buyer can create a service/material order request.
- Order status feed shows progression for an existing order.
- Buyer can open invoice / sale bill view.
- Buyer can submit feedback needed to close an order.

### P1

- Buyer can accept proposed quotation / order terms.
- Buyer can reject proposed quotation / order terms.
- Payment can be marked settled when invoice is ready.
- Push-notification-driven order status updates are visible in app state.

### P2

- Full status chain is represented correctly:
  `Requested -> Accepted -> Indent Sent -> PO Raised -> Dispatched -> Delivered -> END`

## Supplier / Vendor

### P0

- Login lands on supplier/vendor home.
- Indent inbox shows incoming indents.
- Supplier can accept an indent.
- Supplier can reject an indent with reason.
- Supplier can acknowledge PO receipt.
- Supplier can mark dispatch with vehicle number and ETA.
- Supplier can upload delivery note / challan.
- Supplier can submit supplier bill.

### P1

- Payment status flow is visible from `Pending` to `Paid`.
- New indent and PO issuance states are reflected in the app.

### P2

- PDF upload path works in addition to photo upload.
- Push notification arrives for new indent and payment update.

## PRD Out-Of-Scope Guards

These should be tested as negative assertions so the mobile app does not drift beyond scope.

- `P0` Mobile app does not expose master-data configuration screens.
- `P0` Mobile app does not generate Purchase Orders directly.
- `P1` Mobile app does not expose payroll calculation logic; payslip is view-only.
- `P1` Mobile app does not expose desktop/web-only admin panels.

## Recommended First Maestro Suite

Build these first before anything else:

1. Auth smoke by role: buyer, employee, supplier, vendor, security_supervisor.
2. Guard smoke: login, clock in, checklist open, contacts open.
3. Buyer smoke: login, requests tab, invoices tab, feedback tab.
4. Supplier smoke: login, indents, orders/PO, billing.
5. HRMS smoke: login, attendance, leave, payslips, documents.

## Recommended Second Maestro Suite

1. Manager ticket flows.
2. Delivery status progression.
3. AC technician work completion flow.
4. Pest control PPE + proof flow.
5. Cross-role approval loops where one role triggers another.

## Manual / Device-Lab Only Cases

- Push notification delivery timing.
- SMS fallback.
- Camera/photo-quality validation.
- GPS drift / geo-fence boundary behavior.
- Offline queue/retry behavior.
- 8-hour inactivity logout.

