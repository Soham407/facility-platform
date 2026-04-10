from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScreenMatch:
    screen_id: str
    label: str


class ScreenClassifier:
    def classify(self, visible_texts: list[str], resource_ids: list[str]) -> ScreenMatch:
        corpus = " | ".join(visible_texts + resource_ids).lower()

        # --- Authentication & Onboarding ---
        if any(k in corpus for k in ("mobile otp sign-in", "otp sign", "enter otp", "auth.mobilenumber",
                                      "biometric", "face id", "fingerprint", "first-time setup",
                                      "geo-fence calibration", "push notification permission")):
            return ScreenMatch("authentication-onboarding", "Authentication / Onboarding")

        # --- Security Guard App ---
        if any(k in corpus for k in ("sos", "panic button", "guard.home", "i am on duty",
                                      "inactivity alert", "clock in", "clock out", "selfie attendance")):
            return ScreenMatch("security-guard-app", "Guard Home")
        if any(k in corpus for k in ("daily checklist", "guard checklist", "guard.checklist",
                                      "parking lights", "water supply", "gate/shutter", "motor pump")):
            return ScreenMatch("security-guard-app", "Guard Checklist")
        if any(k in corpus for k in ("add visitor", "visitor logging", "guard.visitors",
                                      "vehicle number", "destination flat", "approve", "decline",
                                      "daily visitor", "frequent visitor")):
            return ScreenMatch("security-guard-app", "Visitor Logging")
        if any(k in corpus for k in ("emergency contact", "quick dial", "police", "fire brigade",
                                      "ambulance", "guard.emergency")):
            return ScreenMatch("security-guard-app", "Emergency Contacts")

        # --- Security Supervisor & Society Manager ---
        if any(k in corpus for k in ("guard location map", "checklist status board", "panic log",
                                      "visitor stats", "staff attendance", "live monitoring",
                                      "oversight", "guard movement", "supervisor.dashboard",
                                      "manager.dashboard")):
            return ScreenMatch("security-supervisor-society-manager-app", "Supervisor Dashboard")
        if any(k in corpus for k in ("employee behaviour ticket", "sleeping on duty", "absence from post",
                                      "grooming", "unauthorized entry", "rudeness", "ticket.behaviour")):
            return ScreenMatch("security-supervisor-society-manager-app", "Behaviour Ticket")
        if any(k in corpus for k in ("material ticket", "check quantity", "check quality",
                                      "condition status", "batch number", "return ticket",
                                      "ticket.material")):
            return ScreenMatch("security-supervisor-society-manager-app", "Material Ticket")

        # --- HRMS ---
        if any(k in corpus for k in ("leave application", "leave type", "sick leave", "casual leave",
                                      "paid leave", "leave balance", "approve leave", "reject leave",
                                      "hrms.leave")):
            return ScreenMatch("hrms-mobile-features-for-all-staff", "HRMS Leave")
        if any(k in corpus for k in ("payslip", "payroll", "basic salary", "hra", "special allowance",
                                      "provident fund", "esic", "hrms.payslip", "earnings breakdown",
                                      "deductions")):
            return ScreenMatch("hrms-mobile-features-for-all-staff", "HRMS Payslip")
        if any(k in corpus for k in ("document vault", "aadhar", "pan card", "voter id",
                                      "psara", "police verification", "hrms.documents")):
            return ScreenMatch("hrms-mobile-features-for-all-staff", "HRMS Documents")
        if any(k in corpus for k in ("geo-fence", "geo fence", "punch out", "auto punch",
                                      "check in", "check-in", "hrms.attendance")):
            return ScreenMatch("hrms-mobile-features-for-all-staff", "HRMS Attendance")

        # --- Service Workflow Apps ---
        if any(k in corpus for k in ("ac technician", "ac not cooling", "start work", "before photo",
                                      "after photo", "parts used", "work order", "ac.service")):
            return ScreenMatch("service-workflow-apps", "AC Technician")
        if any(k in corpus for k in ("pest control", "ppe checklist", "mask", "gloves",
                                      "eye protection", "apron", "chemical request", "fogging",
                                      "gel application", "pest.service", "treated area")):
            return ScreenMatch("service-workflow-apps", "Pest Control")
        if any(k in corpus for k in ("delivery boy", "picked up", "in transit", "delivered",
                                      "delivery proof", "dispatch", "delivery.status")):
            return ScreenMatch("service-workflow-apps", "Delivery")

        # --- Buyer & Supplier ---
        if any(k in corpus for k in ("place order", "order tracking", "sale bill", "buyer.orders",
                                      "order requested", "order status", "rate service", "feedback")):
            return ScreenMatch("buyer-supplier-mobile-apps", "Buyer")
        if any(k in corpus for k in ("indent inbox", "accept indent", "reject indent",
                                      "po acknowledgement", "dispatch update", "supplier bill",
                                      "received note", "supplier.indent", "buyer portal")):
            return ScreenMatch("buyer-supplier-mobile-apps", "Supplier")

        return ScreenMatch("overview", "Unknown Screen")
