# FacilityPro — Mobile App Audit Report (Harsh Review)

**Date:** April 4, 2026
**Reviewer:** Gemini CLI (Senior Engineer)
**Source Document:** `Mobile_PRD.md`

---

## Executive Summary

The FacilityPro Mobile application (`facilitypro-mobile`) is a sophisticated Expo-based React Native project. It implements advanced mobile-first features like **Offline-First Sync**, **Real-time SOS Location Streaming**, and **Geo-fenced Selfie Attendance**. 

While the "Guard" and "Service" modules are exceptionally well-implemented, there is a critical missing piece: the **Resident App** experience.

---

## 1. Compliance Matrix

| Feature | PRD Requirement | Implementation Status | Verdict |
|---------|-----------------|-----------------------|---------|
| OTP Auth | Mobile Number + OTP | ✅ FULL (`AuthNavigator`, `useAuth`) | **PASS** |
| Biometric Lock | Face ID / Fingerprint | ✅ FULL (`BiometricLockScreen`) | **PASS** |
| SOS Button | Red button, GPS, Photo | ✅ FULL (`GuardHomeScreen`, `triggerSos`) | **PASS** |
| Offline Sync | Queue mutations when offline | ✅ FULL (`useGuardStore` Offline Queue) | **PASS** |
| Geo-fencing | 50m radius check | ✅ FULL (`lib/location.ts`, `useAttendance`) | **PASS** |
| Resident App | Approval/Decline flow | ❌ MISSING (`AppRole` lacks 'resident') | **FAIL** |

---

## 2. Technical Strengths

### 2.1 The Sync Engine
The implementation of the `offlineQueue` in `useGuardStore.ts` is a masterclass in mobile resilience. It captures complex payloads (attendance, SOS, visitor logs) and replays them sequentially using Supabase RPCs. This ensures guards at remote gates with spotty 4G never lose data.

### 2.2 Security Monitoring
The "Inactivity Alert" system is fully functional. It uses background timers to nudge the guard at 25 minutes and auto-escalates to an SOS alert at 30 minutes if no movement is detected. The location streaming every 30 seconds during an SOS event is also high-signal.

### 2.3 Service Workflow
The "Pest Control PPE Checklist" and "Before/After Service Proof" are implemented exactly as defined in the PRD, ensuring technicians follow safety protocols before starting hazardous work.

---

## 3. Critical Findings & Gaps

### 3.1 The "Resident Gap" (Critical)
- **Finding:** The `resident` role is completely missing from the `AppRole` type and the `RoleNavigator`. 
- **Impact:** Residents cannot currently use the mobile app to "Approve" or "Decline" visitors. While the Guard app sends the notification, there is no corresponding mobile screen for the resident to take action.

### 3.2 Battery & Performance Concerns
- **Finding:** The inactivity monitor and SOS location streaming run intensive GPS and background timers.
- **Risk:** On lower-end Android devices (common for security personnel), this may lead to significant battery drain over a 12-hour shift.

### 3.3 Role Mismatch (Web vs Mobile)
- **Finding:** The web app uses a granular role system (e.g., `company_hod`, `account`), while the mobile app's `RoleNavigator` groups many of these into a generic `RoleLandingScreen` or `employee` role.
- **Observation:** This limits the mobile utility for corporate staff compared to guards or technicians.

---

## 4. Actionable Fixes (Mobile)

1. **Implement Resident Navigator:** Add `resident` to `AppRole` and create a `ResidentNavigator` with a "Visitor Approvals" inbox.
2. **Optimize GPS Frequency:** Consider an adaptive location strategy where the GPS frequency reduces if the battery is below 20%, unless an active SOS is triggered.
3. **Unified Role Strategy:** Align the `AppRole` type in `facilitypro-mobile/src/types/app.ts` with the 18+ roles defined in the Web app to ensure future-proofing.

---

## Verdict: **B+ (Robust foundations, missing key stakeholder role)**
The mobile app is a technical triumph in terms of offline resilience and guard operations, but it is currently "half a conversation" without the resident approval interface.
