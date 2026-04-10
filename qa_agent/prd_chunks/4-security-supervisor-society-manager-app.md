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
