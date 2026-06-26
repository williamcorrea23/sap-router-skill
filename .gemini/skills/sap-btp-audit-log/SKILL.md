---
name: sap-btp-audit-log
description: SAP BTP Audit Log Service — audit trail capture, audit log configuration, event logging patterns, compliance audit trails (SOC 2, GDPR), audit log viewer, retention policies, OAuth audit integration, service binding for CAP apps. Use when implementing audit logging on BTP, configuring compliance audit trails, or capturing security-relevant events for regulatory requirements.
---

# SAP BTP Audit Log Service

Tamper-proof audit trails for SAP BTP applications — compliance, security, forensics.

## Service Instance

```bash
cf create-service auditlog standard my-auditlog
cf bind-service my-app my-auditlog
```

## What Gets Audited

| Event Type | Example |
|---|---|
| Authentication | User login, token refresh, MFA |
| Authorization | Role assignment, scope grant |
| Data access | Read sensitive entity, export |
| Data modification | CREATE, UPDATE, DELETE on audited entities |
| Configuration changes | Service bindings, destination changes |
| Admin operations | User creation, role collection changes |

## Audit Logging in CAP

```javascript
const cds = require('@sap/cds')

module.exports = class OrderService extends cds.ApplicationService {
  async init() {
    // Audit all modifications to Orders
    this.after(['CREATE','UPDATE','DELETE'], 'Orders', (data, req) => {
      req.audit({
        category: 'data-modification',
        object: { type: 'Order', id: data.ID },
        user: req.user.id,
        tenant: req.tenant,
        attributes: [{ name: 'event', value: req.event }]
      })
    })
    await super.init()
  }
}
```

## Audit Log Viewer

```
SAP BTP Cockpit → Audit Log Viewer → Subaccount level
  → Filter by: time range, event type, user, tenant
  → Export: CSV, JSON
  → Retention: 30 days (free), 90 days (standard), 1 year (enterprise)
```

## Compliance Coverage

| Regulation | Audit Requirement | Covered By |
|---|---|---|
| SOC 2 | Access controls, change management | Audit Log Service |
| GDPR Art. 30 | Records of processing activities | Audit customization |
| ISO 27001 | A.12.4 Logging and monitoring | Built-in + custom |
| SAP BTP C5 | German BSI cloud compliance | Audit Log Service |

## OAuth Audit Integration

```json
// XSUAA configuration with audit
{
  "xsappname": "my-audited-app",
  "oauth2-configuration": {
    "audit-logs": {
      "enabled": true,
      "events": ["token-issued", "token-refreshed", "token-revoked"]
    }
  }
}
```

## Gotchas

- **Audit log is read-only** after write — immutable by design
- **Audit viewer access**: needs subaccount auditor role
- **Custom audit fields**: use `attributes` array for structured metadata
- **Audit log retention**: 30 days free, configure longer retention in service plan
- **PII in audit logs**: mask sensitive data before writing (GDPR compliance)
