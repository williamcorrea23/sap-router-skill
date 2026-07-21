# Security Audit and Logging

Auditing ensures traceability of user actions and security events.

### Transactions
| Transaction | Purpose |
|--------------|----------|
| SM19 | Configure audit classes |
| SM20 | Display audit logs |
| SM20N | Enhanced audit analysis |
| SUIM | Review user authorizations |
| SCUL | Log user changes |

### Recommended Audit Settings
- Enable audit for critical objects: S_USER_GRP, S_TABU_DIS, S_TCODE.
- Configure system log retention in RZ10.
- Forward audit data to SIEM if applicable.

### Reporting & Compliance
Use SUIM to extract:
- Roles by user
- Profiles by role
- Users with SAP_ALL/SAP_NEW

Ensure export to CSV or GRC integration for compliance reporting.