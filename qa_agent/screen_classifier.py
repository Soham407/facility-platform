from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScreenMatch:
    screen_id: str
    label: str


# Text that appears in bottom tab bars — used as secondary classification signal.
# These alone are too ambiguous ("Home" appears everywhere) but help in combination.
_TAB_LABELS = {
    "guard": {"Checklist", "Visitors", "Contacts"},
    "oversight": {"Alerts", "Ops", "Tickets"},
    "hrms": {"Attendance", "Leave", "Payslips", "Documents"},
    "buyer": {"Requests", "Invoices", "Feedback"},
    "service": {"Tasks", "Materials", "Proof"},
    "supplier": {"Indents", "Orders", "Billing"},
}


class ScreenClassifier:
    def classify(self, visible_texts: list[str], resource_ids: list[str]) -> ScreenMatch:
        corpus = " | ".join(visible_texts + resource_ids).lower()

        # ── Authentication ───────────────────────────────────────────────
        if any(k in corpus for k in (
            "mobile otp sign-in", "phase 1", "preview guard", "preview buyer",
            "preview supervisor", "preview manager", "preview hrms",
        )):
            return ScreenMatch("authentication-login", "Login")

        if any(k in corpus for k in (
            "verify otp", "6-digit otp", "verify and continue", "resend otp",
            "code sent to",
        )):
            return ScreenMatch("authentication-otp", "OTP Verification")

        # ── Onboarding (may show after real-account login) ───────────────
        if any(k in corpus for k in (
            "biometric setup", "face id", "fingerprint setup",
            "geo-fence calibration", "calibrat", "profile photo",
            "selfie for your guard id",
        )):
            return ScreenMatch("onboarding", "Onboarding")

        # ── Security Guard ───────────────────────────────────────────────
        if any(k in corpus for k in (
            "security guard", "ready for duty", "selfie clock",
            "i am on duty", "sync queued actions", "attendance actions",
            "visitors inside", "sos events", "queue waiting",
        )):
            return ScreenMatch("guard-home", "Guard Home")

        if any(k in corpus for k in (
            "daily operations", "guard checklist", "parking lights",
            "water supply", "motor pump", "photo proof required",
            "numeric entry", "visual check",
        )):
            return ScreenMatch("guard-checklist", "Guard Checklist")

        if any(k in corpus for k in (
            "gate entry", "visitor logging", "log visitor entry",
            "visitor name", "purpose of visit", "vehicle number",
            "capture visitor photo", "offline-safe entry logging",
            "frequent visitor", "daily visitor",
        )):
            return ScreenMatch("guard-visitors", "Guard Visitors")

        if any(k in corpus for k in (
            "emergency contacts", "quick dial", "police", "fire brigade",
            "ambulance", "guard contacts",
        )):
            return ScreenMatch("guard-contacts", "Guard Contacts")

        # ── Oversight (supervisor + manager) ─────────────────────────────
        if any(k in corpus for k in (
            "security supervision", "society management", "guard location map",
            "live monitoring", "checklist status board", "visitor stats",
            "staff attendance", "refresh oversight", "guard movement",
        )):
            return ScreenMatch("oversight-home", "Oversight Home")

        if any(k in corpus for k in (
            "oversight alerts", "panic log", "sos alert",
            "inactivity alert", "alert feed",
        )):
            return ScreenMatch("oversight-alerts", "Oversight Alerts")

        if any(k in corpus for k in (
            "oversight operations", "patrol log", "operations board",
        )):
            return ScreenMatch("oversight-operations", "Oversight Operations")

        if any(k in corpus for k in (
            "oversight tickets", "behaviour ticket", "material ticket",
            "sleeping on duty", "unauthorized entry", "rudeness",
        )):
            return ScreenMatch("oversight-tickets", "Oversight Tickets")

        # ── HRMS (employee) ──────────────────────────────────────────────
        if any(k in corpus for k in (
            "hrms command deck", "phase 4", "employee-facing",
            "payroll alerts", "hrms home",
        )):
            return ScreenMatch("hrms-home", "HRMS Home")

        if any(k in corpus for k in (
            "punch out", "auto punch", "hrms attendance", "attendance record",
            "check-in", "geo-fence",
        )):
            return ScreenMatch("hrms-attendance", "HRMS Attendance")

        if any(k in corpus for k in (
            "leave application", "leave type", "sick leave", "casual leave",
            "leave balance", "approve leave", "hrms leave",
        )):
            return ScreenMatch("hrms-leave", "HRMS Leave")

        if any(k in corpus for k in (
            "payslip", "basic salary", "hra", "provident fund",
            "earnings breakdown", "deductions", "hrms payslips",
        )):
            return ScreenMatch("hrms-payslips", "HRMS Payslips")

        if any(k in corpus for k in (
            "document vault", "aadhar", "pan card", "psara",
            "police verification", "hrms documents",
        )):
            return ScreenMatch("hrms-documents", "HRMS Documents")

        # ── Buyer ────────────────────────────────────────────────────────
        if any(k in corpus for k in (
            "buyer portal", "order and requisition", "refresh buyer",
        )):
            return ScreenMatch("buyer-home", "Buyer Home")

        if any(k in corpus for k in (
            "buyer requests", "place order", "order tracking", "order status",
            "order requested",
        )):
            return ScreenMatch("buyer-requests", "Buyer Requests")

        if any(k in corpus for k in (
            "buyer invoices", "sale bill", "invoice list",
        )):
            return ScreenMatch("buyer-invoices", "Buyer Invoices")

        if any(k in corpus for k in (
            "buyer feedback", "rate service", "service rating",
        )):
            return ScreenMatch("buyer-feedback", "Buyer Feedback")

        # ── Service workers ──────────────────────────────────────────────
        if any(k in corpus for k in (
            "phase 5", "workspace", "start work", "work order",
            "preview ac technician", "preview pest", "preview delivery",
            "preview service boy",
        )):
            return ScreenMatch("service-home", "Service Home")

        if any(k in corpus for k in (
            "service tasks", "before photo", "after photo", "parts used",
        )):
            return ScreenMatch("service-tasks", "Service Tasks")

        if any(k in corpus for k in (
            "service materials", "material request", "chemical request",
            "ppe checklist", "fogging", "gel application",
        )):
            return ScreenMatch("service-materials", "Service Materials")

        if any(k in corpus for k in (
            "service proof", "delivery proof", "photo evidence", "upload proof",
            "in transit", "delivered",
        )):
            return ScreenMatch("service-proof", "Service Proof")

        # ── Supplier / Vendor ────────────────────────────────────────────
        if any(k in corpus for k in (
            "supplier portal", "vendor portal", "fulfillment desk",
        )):
            return ScreenMatch("supplier-home", "Supplier Home")

        if any(k in corpus for k in (
            "supplier indents", "indent inbox", "accept indent", "reject indent",
        )):
            return ScreenMatch("supplier-indents", "Supplier Indents")

        if any(k in corpus for k in (
            "supplier orders", "po acknowledgement", "dispatch update",
        )):
            return ScreenMatch("supplier-orders", "Supplier Orders")

        if any(k in corpus for k in (
            "supplier billing", "supplier bill", "received note",
        )):
            return ScreenMatch("supplier-billing", "Supplier Billing")

        return ScreenMatch("overview", "Unknown Screen")
