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
