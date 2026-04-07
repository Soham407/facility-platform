# Facility Management & Services
## Mobile Application — Product Requirements Document
**Mobile-Only Edition | Version 1.0 | February 2026**

---

## Table of Contents
1. [Overview & Scope](#1-overview--scope)
2. [Authentication & Onboarding](#2-authentication--onboarding)
3. [Security Guard App](#3-security-guard-app)
4. [Security Supervisor & Society Manager App](#4-security-supervisor--society-manager-app)
5. [HRMS — Mobile Features for All Staff](#5-hrms--mobile-features-for-all-staff)
6. [Service Workflow Apps](#6-service-workflow-apps)
7. [Buyer & Supplier Mobile Apps](#7-buyer--supplier-mobile-apps)
8. [Notification Architecture](#8-notification-architecture)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Out of Scope (Mobile Edition)](#10-out-of-scope-mobile-edition)
- [Appendix — Workflow Status Codes](#appendix--workflow-status-codes-mobile-reference)

---

## 1. Overview & Scope

This document defines the product requirements for the mobile application component of the Facility Management & Services (FMS) platform. It covers all user-facing mobile screens, interactions, and functionality across all mobile stakeholder roles. Desktop/web-only administration panels are out of scope.

### 1.1 Mobile Stakeholders

| Role | Mobile Responsibilities |
|---|---|
| **Security Guard** | Patrol check-ins, panic alerts, daily checklist, visitor entry logging, emergency contacts |
| **Security Supervisor** | Guard monitoring dashboard, incident ticket management, alert review |
| **Society Manager** | Operational oversight, ticket generation, material approvals, staff monitoring |
| **Delivery Boy** | Delivery status updates, order dispatch confirmations |
| **Service Boy** | Task assignment, work progress updates, attendance check-in |
| **Supplier / Vendor** | Indent review & acceptance, PO acknowledgment, dispatch updates, billing |
| **Buyer** | Order requests, order tracking, invoice receipt, feedback submission |

---

## 2. Authentication & Onboarding

### 2.1 Login
- Mobile Number + OTP login (primary method)
- Role-based routing after login — each role is directed to its own home screen
- Biometric unlock (Face ID / Fingerprint) for subsequent sessions
- Session expiry: auto-logout after 8 hours of inactivity

### 2.2 First-Time Setup
- Profile photo capture (mandatory for guards — used for selfie attendance)
- Device registration and push notification permission request
- Geo-fence calibration prompt: app walks user to their primary work location to set baseline GPS

---

## 3. Security Guard App

The Guard App is the most feature-rich mobile experience. Guards have limited literacy requirements considered; the UI uses large icons and minimal text.

### 3.1 Home Screen

| Feature | Description |
|---|---|
| **SOS Panic Button** | Full-width RED button prominently placed. Single tap triggers instant alert with GPS snapshot to Society Manager and all Committee Members via push notification + SMS. |
| **Clock In / Clock Out** | Selfie-based attendance. Camera opens automatically; photo is timestamped and GPS-stamped. Geo-fence validation runs before allowing check-in. |
| **Daily Checklist** | Shortcut to today's incomplete checklist items. Badge shows count of pending tasks. |
| **Emergency Contacts** | One-tap quick-dial list: Police, Fire, Ambulance, Electrician, Plumber. |

### 3.2 Panic / SOS System

- **Trigger:** Single tap on the red SOS button (no confirmation step to avoid delay)
- **Payload sent:** Guard ID, Name, GPS coordinates (lat/lng), Timestamp, Photo (auto-captured)
- **Recipients:** Society Manager app push notification + SMS; Security Supervisor push notification
- **Resolution:** Manager must acknowledge the alert from the dashboard; alert stays active until acknowledged
- **GPS tracking:** Continuous location streaming begins upon SOS trigger until manager resolves

### 3.3 Daily Operational Checklist

Checklist items are configured via the Daily Checklist Master in the admin portal and pushed to the guard's app at the start of each shift.

- Each item has a **Yes / No** toggle or numeric value input (e.g., water tank level in %)
- Photo evidence upload is available on each item (optional by default, mandatory for critical items)
- **Parking Lights:** guard logs time of lights ON (evening) and OFF (morning)
- **Water Supply:** motor pump status (Running/Stopped) + tank level reading
- **Gate/Shutter Check:** confirmation that secondary gates are locked
- Auto-reminder: push notification sent if checklist is not started by a configurable time (default **9:00 AM**)
- Completed checklist is submitted and locked; edits require supervisor override

### 3.4 Inactivity & Patrol Alert

- **Static Alert:** if the guard's GPS does not change by more than 10 metres for 30 minutes during an active shift, the system triggers an Inactivity Alert to the Supervisor
- Guard receives a gentle vibration + sound nudge 5 minutes before the inactivity threshold
- Guard can tap **"I am on duty"** to reset the timer if they are legitimately stationary (e.g., on post)

### 3.5 Visitor Entry Logging

- Guard opens **Add Visitor** screen from the home menu
- Captures: Name, Phone Number, Photo (camera), Vehicle Number (optional)
- Selects destination flat from the Society Family Database (searchable dropdown)
- System sends automated SMS/push notification to the resident: *"Dear Resident, [Name] is at the gate for Flat [X]"*
- Resident can **approve or decline** from their app; result is shown on the guard's screen within 30 seconds
- **Daily / Frequent Visitors:** separate list for maids, drivers, milkmen — guard selects from list rather than re-entering details

### 3.6 Emergency Contact Directory

A quick-dial screen accessible from the home screen with one-tap calling. Contacts are configured by the Society Manager and cannot be edited by guards.

---

## 4. Security Supervisor & Society Manager App

### 4.1 Live Monitoring Dashboard

| Feature | Description |
|---|---|
| **Guard Location Map** | Real-time map showing all on-duty guards' GPS positions, refreshed every 60 seconds |
| **Checklist Status Board** | Green / Red indicators per guard — green = all checklist items complete, red = pending items |
| **Panic Log Feed** | Live feed of active SOS alerts; tapping an alert shows guard location and triggers acknowledgement flow |
| **Visitor Stats** | Total entries today / this week with drill-down by gate |
| **Staff Attendance** | Check-in / check-out log for all security personnel with timestamps and GPS |

### 4.2 Ticket Management

#### Employee Behaviour Ticket
- Manager selects staff member from dropdown
- Selects category: Sleeping on Duty, Rudeness, Absence from Post, Grooming/Uniform, Unauthorized Entry
- Assigns severity: **Low (Warning)** / **Medium (Serious)** / **High (Critical)**
- Adds incident description text + optional photo/video evidence
- Date & time auto-captured
- Ticket submitted to admin portal and a copy sent to the employee's profile

#### Material Ticket (Quality & Quantity Check)
- Triggered when a delivery vehicle is logged at the gate by the security guard
- Manager receives push notification to inspect goods
- Opens **Material Ticket** form — fills in: Check Quantity (ordered vs received) and Check Quality (Good / Damaged / Expired / Leaking)
- Condition status, photo evidence, and batch number captured
- If **Approved:** items are added to the relevant inventory module
- If **Rejected:** a Return Ticket is auto-generated for vendor follow-up

---

## 5. HRMS — Mobile Features for All Staff

### 5.1 Smart Attendance with Geo-Fencing

- **Selfie Attendance:** staff opens app → taps Check In → front camera activates → photo taken → GPS validated → check-in recorded
- **Geo-Fence Validation:** check-in is only permitted if the device GPS is within 50 metres of the registered Company Location for that employee
- **Auto Punch-Out:** if the employee's GPS moves outside the geo-fence for more than 15 consecutive minutes, the system flags the record and notifies the supervisor
- Check-out follows the same selfie + GPS process

### 5.2 Leave Management

- Staff submits leave application through the app: selects Leave Type (Sick / Casual / Paid), start date, end date, reason
- Supervisor receives a push notification to **Approve** or **Reject**
- Employee gets an in-app notification with the decision
- Real-time leave balance shown on the staff home screen

### 5.3 Payslip & Payroll View

- Staff can view and download their monthly payslip as a PDF directly from the app
- **Earnings breakdown:** Basic Salary, HRA, Special Allowance, Overtime
- **Deductions breakdown:** PF, PT, ESIC
- Historical payslips accessible for the last 12 months

### 5.4 Document Vault

- Staff can view their uploaded ID documents (Aadhar, PAN, Voter ID)
- Security staff can view their PSARA certificate and Police Verification status
- Upload replacement or updated documents from mobile camera or gallery

---

## 6. Service Workflow Apps

### 6.1 AC Technician App

- Receive service request notification (e.g., *"AC not cooling — Wing B, Flat 304"*)
- Tap **Start Work** — GPS and timestamp logged automatically
- Upload **"Before"** photo of the unit
- Log parts used from Equipment Supply (select item + quantity; deducted from stock)
- Upload **"After"** photo
- Tap **Complete** — work order closed and Society Manager notified

### 6.2 Pest Control Technician App

- **PPE Checklist:** before starting any job, technician must check off all protective gear items (Mask, Gloves, Eye Protection, Apron) — cannot proceed until complete
- **Attendance with Photo & GPS:** same selfie + geo-fence mechanism as HRMS
- **Chemical Request:** technician submits a material request for specific chemicals + quantities; manager approves in-app
- **Service Proof:** upload Before and After photos of treated areas
- **Resident Notification:** system auto-sends SMS/push to affected flats — *"Pest control at 4 PM. Keep kids/pets away and cover food."*

### 6.3 Delivery Boy App

- View active delivery orders assigned to this role
- Update order status: **Picked Up → In Transit → Delivered**
- Capture delivery proof: photo of delivered goods at the destination
- Buyer and Admin receive push notifications on each status change

---

## 7. Buyer & Supplier Mobile Apps

### 7.1 Buyer App

| Feature | Description |
|---|---|
| **Place Order** | Select service category, specify grade/role/product, set quantity and duration, submit order request |
| **Order Tracking** | Live status feed: Requested → Accepted → Indent Sent → PO Raised → Dispatched → Delivered |
| **Accept / Reject** | Buyer can accept or reject a proposed quotation or order terms from the admin |
| **Invoice & Payment** | View and download the Sale Bill; mark payment as settled |
| **Feedback** | Rate service quality after delivery (star rating + free-text comment); required to close the order |
| **Notifications** | Push alerts for every status change on the buyer's orders |

### 7.2 Supplier / Vendor App

| Feature | Description |
|---|---|
| **Indent Inbox** | View incoming indents forwarded by the Company Admin with full line-item details |
| **Accept / Reject Indent** | Tap to confirm availability or decline with a reason |
| **PO Acknowledgement** | Confirm receipt of the formal Purchase Order (status: Received PO) |
| **Dispatch Update** | Mark goods as dispatched (status: Dispatch PO); enter vehicle number and estimated arrival |
| **Received Note Upload** | Upload delivery note or challan as a photo or PDF |
| **Bill Submission** | Generate and submit Supplier Bill within the app; track payment status (Pending → Paid) |
| **Notifications** | Push alerts for new indents, PO issuance, payment updates |

---

## 8. Notification Architecture

All push notifications are delivered via **Firebase Cloud Messaging (FCM)**. Fallback to SMS is triggered if the app push is undelivered after 60 seconds.

| Notification | Route | Priority |
|---|---|---|
| **SOS / Panic Alert** | Guard → Manager, Supervisor (push + SMS) | CRITICAL — bypasses Do Not Disturb |
| **Visitor at Gate** | Guard → Resident of destination flat (push + SMS with visitor photo) | High |
| **Inactivity Alert** | System → Supervisor (push). Triggered after 30 min no GPS movement | High |
| **Checklist Reminder** | System → Guard (push). If checklist not opened by 9:00 AM | Medium |
| **Order Status Change** | System → Buyer (push) at every workflow transition | Medium |
| **New Indent** | System → Supplier (push + SMS) when admin forwards an indent | High |
| **Material Delivery** | Guard → Manager (push) when delivery vehicle is logged | High |
| **Leave Decision** | System → Employee (push) when supervisor approves/rejects | Medium |
| **Payslip Ready** | System → Employee (push) when monthly payslip is generated | Low |
| **Pest Control Alert** | System → Resident (push + SMS) 2 hours before scheduled treatment | High |
| **Low Stock Alert** | System → Manager (push) when inventory item drops below reorder level | Medium |

---

## 9. Non-Functional Requirements

### 9.1 Platform Support
- **Android:** version 10 and above
- **iOS:** version 14 and above
- Minimum screen size: 5 inches / 360dp wide

### 9.2 Offline Capability
- Guard daily checklist: writable offline, syncs when connectivity is restored
- Emergency contacts: cached locally — always accessible without network
- SOS button: queues alert locally and fires the moment network is available if offline at trigger time

### 9.3 Performance
- App launch to home screen: **< 3 seconds** on mid-range Android device
- Selfie attendance photo capture and upload: **< 5 seconds** on 4G
- Push notification delivery: **< 10 seconds** end-to-end for standard alerts; **< 5 seconds** for SOS

### 9.4 Security & Privacy
- All API calls over HTTPS with certificate pinning
- Biometric data (selfies) stored encrypted on server; not shared with third parties
- Role-based access: each user sees only data relevant to their role
- Visitor personal data (photo, phone) purged after **90 days** per retention policy

### 9.5 Accessibility
- Minimum tap target size: 44×44 dp
- High-contrast mode support for guards operating in low-light environments
- Text size follows OS accessibility settings

---

## 10. Out of Scope (Mobile Edition)

The following features are managed exclusively through the web admin portal and are **not in scope** for the mobile application:

- Master data configuration (Role, Designation, Product, Supplier, Leave Type, Holiday masters)
- Company-level financial reporting and ledger management
- Purchase Order generation (PO is created on web; mobile stakeholders only receive and respond)
- Payroll calculation and payslip generation (calculation runs on server; mobile is view-only)
- Advertising and printing module management
- Society Family Database administration

---

## Appendix — Workflow Status Codes (Mobile Reference)

| Status | Meaning |
|---|---|
| **Order Requested** | Buyer has submitted an order; awaiting Admin review |
| **Accepted** | Admin approved the order request |
| **Pending** | Admin placed order on hold for further review |
| **Rejected** | Admin denied the request; buyer notified |
| **Indent Forward** | Admin has sent the internal demand to the Supplier |
| **Indent Accept** | Supplier confirmed they can fulfill the indent |
| **Indent Reject** | Supplier declined; Admin must identify alternate vendor |
| **Received PO** | Supplier acknowledged receipt of the Purchase Order |
| **Dispatch PO** | Supplier has dispatched the goods |
| **Deployment Confirmed** | Service staff have arrived and been verified on-site |
| **Sale Bill Paid** | Buyer has settled the invoice with the Company |
| **Supplier Bill Paid** | Company has settled payment with the Supplier |
| **END** | All obligations fulfilled; feedback submitted and bills paid |
