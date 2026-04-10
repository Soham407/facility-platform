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
