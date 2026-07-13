---
name: sap-btp-audit-log
description: SAP BTP Audit Log Service — audit trail capture, configuration, compliance (SOC 2, GDPR), audit log viewer, retention policies, OAuth audit integration. Use when implementing audit logging on BTP, configuring compliance audit trails, or capturing security-relevant events.
trigger:
  - audit log configuration on BTP
  - compliance audit trail setup
  - SOC 2 GDPR audit logging
  - CAP audit event logging
  - audit log viewer access
  - security event capture BTP
---

# SAP BTP Audit Log Service

Tamper-proof audit trails for SAP BTP applications — compliance, security, forensics.

## Prerequisites

- SAP BTP subaccount with Cloud Foundry enabled
- CF CLI installed and logged in (`cf login`)
- Audit Log Viewer entitlement on subaccount (free or standard plan)
- CAP project with `@sap/cds` ≥ 7.x (for code-level audit logging)
- Subaccount Auditor role for viewing logs

## 1. Create and Bind the Audit Log Service

```bash
# Create service instance
cf create-service auditlog standard my-auditlog

# Bind to your application
cf bind-service my-app my-auditlog

# Restage to pick up VCAP_SERVICES
cf restage my-app
```

## 2. Log Audit Events in CAP

```javascript
const cds = require('@sap/cds')

module.exports = class OrderService extends cds.ApplicationService {
  async init() {
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

**Audited event categories:**
- **Authentication** — login, token refresh, MFA
- **Authorization** — role assignment, scope grant
- **Data access** — read sensitive entity, export
- **Data modification** — CREATE, UPDATE, DELETE on audited entities
- **Configuration changes** — service bindings, destination changes
- **Admin operations** — user creation, role collection changes

## 3. Enable OAuth Audit in XSUAA

```json
// xs-security.json
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

```bash
# Deploy updated security descriptor
cds compile srv/ -2 xs-security.json > xs-security.gen.json
cf bind-service my-app my-xsuaa -c xs-security.gen.json
cf restage my-app
```

## 4. View and Export Audit Logs

```text
SAP BTP Cockpit → Subaccount → Audit Log Viewer
  → Filter by: time range, event type, user, tenant
  → Export: CSV, JSON
  → Retention: 30 days (free), 90 days (standard), 1 year (enterprise)
```

Alternatively, use the REST API:

```bash
# Fetch audit log entries (requires OAuth token from auditlog service key)
curl "https://auditlog-management.cfapps.<region>.hana.ondemand.com/auditlog/v1/auditlogrecords?time_from=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer $AUDITLOG_TOKEN"
```

## 5. Compliance Coverage

- **SOC 2** — Access controls, change management → Built-in Audit Log Service
- **GDPR Art. 30** — Records of processing activities → Custom audit events
- **ISO 27001 A.12.4** — Logging and monitoring → Built-in + custom events
- **SAP BTP C5** — German BSI cloud compliance → Built-in

## Pitfalls

- **Pitfall: Audit logs are read-only after write**
  - Cause: Immutability is enforced server-side; no update or delete API exists.
  - Solution: Validate and mask data before calling `req.audit()`. PII must be sanitized.

- **Pitfall: Cannot view logs in cockpit**
  - Cause: User lacks the Subaccount Auditor role collection.
  - Solution: Assign role: `BTP Cockpit → Security → Role Collections → Add user to "Subaccount Auditor"`.

- **Pitfall: Custom attributes not appearing in viewer**
  - Cause: The `attributes` array format changed across CAP versions.
  - Solution: Use `[{ name: 'key', value: 'val' }]` format. Verify with `cds --version` ≥ 7.

- **Pitfall: Logs disappear after 30 days**
  - Cause: Free plan retention is 30 days.
  - Solution: Upgrade to standard (90 days) or enterprise (1 year). For longer retention, export to a long-term store (e.g., SAP HANA, S3) via scheduled job.

- **Pitfall: PII leaks into audit log**
  - Cause: Full request payload written to audit attributes.
  - Solution: Explicitly list which fields to audit. Never pass `req.data` wholesale. Mask email, phone, national IDs.

## Verification

```bash
# 1. Verify service instance exists and is bound
cf services | grep my-auditlog

# 2. Confirm binding in VCAP_SERVICES
cf env my-app | grep -A5 auditlog

# 3. Trigger an audited event (e.g., create an order via API)
curl -X POST https://my-app.cfapps.<region>.hana.ondemand.com/odata/v4/Orders \
  -H "Content-Type: application/json" \
  -d '{"ID":"123","total":100}'

# 4. Check Audit Log Viewer in BTP Cockpit — entry should appear within 60 seconds
# 5. Verify via REST API
curl "https://auditlog-management.cfapps.<region>.hana.ondemand.com/auditlog/v1/auditlogrecords" \
  -H "Authorization: Bearer $AUDITLOG_TOKEN"
```
