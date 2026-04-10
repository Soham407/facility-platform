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
