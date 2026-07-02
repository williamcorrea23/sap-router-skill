---
name: sap-btp-saas
description: >
  SAP BTP SaaS Registry — multi-tenant application design, subscription management,
  tenant onboarding/offboarding, HDI container isolation, XSUAA tenant mode,
  CAP SaaS patterns. Use when building multi-tenant apps on BTP or implementing
  SaaS subscription flows.
trigger:
  keywords:
    - btp saas registry
    - multi-tenant application btp
    - tenant onboarding subscription
    - hdi container per tenant
    - xsuaa tenant mode shared dedicated
    - cap saas multi-tenant
    - saas subscription callback
  intent: "Build or configure a multi-tenant SaaS application on SAP BTP"
---

# SAP BTP SaaS Registry

Multi-tenant application architecture on SAP BTP — tenant isolation, subscriptions, lifecycle management.

## Prerequisites

- SAP BTP provider subaccount with Cloud Foundry enabled
- `cf` CLI installed and authenticated
- Entitlements for: **SaaS Registry**, **XSUAA**, **HANA HDI** (or managed HANA)
- CAP application deployed and working in single-tenant mode first
- Admin access to BTP Cockpit for consumer subaccount subscription

## Architecture Overview

```
Provider Subaccount
├── SaaS Registry  (subscription management)
├── XSUAA (tenant-mode: shared)
├── HANA HDI (per-tenant containers)
└── CAP App (single deployment, tenant-aware routing)
    ├── onSubscription callback → creates HDI container
    ├── onUnsubscription callback → drops HDI container
    └── Tenant-aware DB connections via @sap/cds-mtxs
```

## Steps

### 1. Configure XSUAA for Multi-Tenancy

```json
// xs-security.json
{
  "xsappname": "my-saas-app",
  "tenant-mode": "shared",
  "scopes": [
    { "name": "$XSAPPNAME.User" },
    { "name": "$XSAPPNAME.Admin" }
  ],
  "role-templates": [
    { "name": "User", "scope-references": ["$XSAPPNAME.User"] },
    { "name": "Admin", "scope-references": ["$XSAPPNAME.Admin", "$XSAPPNAME.User"] }
  ]
}
```

```bash
cf create-service xsuaa application my-xsuaa -c xs-security.json
```

### 2. Create SaaS Registry Service Instance

```json
// saas-registry.json
{
  "appName": "my-saas-app",
  "appUrls": {
    "getDependencies": "https://my-app.cfapps.us10.hana.ondemand.com/callback/v1.0/dependencies",
    "onSubscription": "https://my-app.cfapps.us10.hana.ondemand.com/callback/v1.0/tenants/{tenantId}"
  }
}
```

```bash
cf create-service saas-registry application my-saas-registry -c saas-registry.json
```

### 3. Implement CAP Subscription Callbacks

```javascript
// srv/saas-handler.js
const cds = require('@sap/cds');

module.exports = class SaaSHandler extends cds.ApplicationService {
  async init() {
    // onSubscription — called when consumer subscribes
    this.on('UPDATE', '/saas/subscription', async (req) => {
      const { subscribedTenantId, subscriptionAppId } = req.data;
      // CAP auto-provisions HDI container via mtxs
      return { subscriptionUrl: `https://${subscribedTenantId}.my-app.com` };
    });

    // onUnsubscription — called when consumer unsubscribes
    this.on('DELETE', '/saas/subscription', async (req) => {
      const { unsubscribedTenantId } = req.data;
      // CAP auto-deprovisions tenant container
      return {};
    });

    await super.init();
  }
};
```

### 4. Configure CAP for Multi-Tenancy

```json
// package.json (excerpt)
{
  "cds": {
    "requires": {
      "db": { "kind": "hana", "multi-tenant": true },
      "auth": { "kind": "xsuaa" }
    },
    "mtx": {
      "plugin": true
    }
  }
}
```

### 5. Deploy and Register the SaaS App

```bash
mbt build -t ./mta_archives
cf deploy ./mta_archives/my-saas-app_1.0.0.mtar

# Verify SaaS Registry knows the app
cf service my-saas-registry
```

### 6. Consumer Subscribes (BTP Cockpit)

1. Consumer opens their subaccount in BTP Cockpit
2. Navigate to **Instances and Subscriptions** → **Create** → select the SaaS app
3. Click **Subscribe**
4. SaaS Registry calls `onSubscription` callback → CAP provisions HDI container
5. Consumer accesses app at `https://<consumer-subdomain>.my-app.com`

## Tenant Isolation Patterns

- **Shared schema** (discriminator column): low isolation, `WHERE tenant_id = ?` — for small tenants
- **Shared DB, separate schemas** (HDI per tenant): medium isolation — default CAP approach
- **Separate DB per tenant**: high isolation — for compliance-heavy tenants
- **Separate deployment**: maximum isolation — premium tier only

## Pitfalls

| # | Pitfall | Cause | Solution |
|---|---------|-------|----------|
| 1 | Subscription callback times out | Callback takes >30 seconds (HDI provisioning is slow) | Keep callback async; return 200 immediately, provision in background job |
| 2 | `403 Forbidden` on tenant access | XSUAA `tenant-mode` not set to `shared` | Recreate XSUAA instance with `"tenant-mode": "shared"` in xs-security.json |
| 3 | HDI container creation fails | HANA instance out of memory or too many containers | Monitor HANA memory; consider shared-schema for small tenants |
| 4 | Consumer can't find app in BTP cockpit | SaaS Registry not deployed or `appName` mismatch | Verify `cf service my-saas-registry` shows "create succeeded"; check `appName` matches MTA ID |
| 5 | Tenant data bleeds between tenants | Missing tenant filter in CDS or raw SQL queries | Always use CAP service layer (auto-tenant-filtered); never bypass with raw SQL |
| 6 | Offboarding leaves orphaned containers | `onUnsubscription` callback errors silently | Add try/catch + logging in DELETE handler; verify container dropped via HANA cockpit |
| 7 | `getDependencies` callback missing | Not implemented in CAP service | Implement GET `/callback/v1.0/dependencies` returning `[{ appId, appName }]` |

## Verification

```bash
# Check SaaS Registry service is provisioned
cf service my-saas-registry

# Check app is running and callbacks respond
curl -s https://my-app.cfapps.us10.hana.ondemand.com/callback/v1.0/dependencies \
  -H "Authorization: Bearer $TOKEN"

# List subscribed tenants
cf service my-saas-registry  # shows bound app

# In BTP Cockpit (provider subaccount):
# → Instances and Subscriptions → verify app appears with "Subscribed" consumers
```

Confirm:
- Consumer subaccount can subscribe via BTP Cockpit
- After subscription, HDI container exists in HANA (check via HANA cockpit)
- Tenant URL returns app with correct tenant-specific data
- Unsubscribe triggers container cleanup (no orphaned HDI containers)
