---
name: sap-btp-saas
description: SAP BTP SaaS application patterns — multi-tenant application design on BTP, SaaS registry, subscription management, tenant onboarding/offboarding, tenant-aware persistence (HDI containers), XSUAA tenant mode, CAP SaaS patterns, SaaS metering, tenant lifecycle. Use when building multi-tenant applications on SAP BTP, implementing SaaS subscription flows, or designing tenant isolation patterns.
---

# SAP BTP SaaS Patterns

Multi-tenant application architecture on SAP BTP — tenant isolation, subscriptions, lifecycle.

## Multi-Tenant Architecture

```
SaaS Application (Provider Subaccount)
├── SaaS Registry (subscription management)
├── XSUAA (dedicated tenant mode)
│   ├── Tenant 1 → Role Collections
│   ├── Tenant 2 → Role Collections
│   └── Tenant N ...
├── HANA HDI (per-tenant containers)
│   ├── Tenant 1 → HDI Container (isolated)
│   ├── Tenant 2 → HDI Container (isolated)
│   └── Tenant N ...
└── CAP App (single deployment, tenant-aware routing)
```

## Tenant Isolation Patterns

| Pattern | Isolation Level | Use Case |
|---|---|---|
| Shared schema (discriminator) | Low (WHERE tenant_id = ?) | Small tenants, same schema |
| Shared DB, separate schemas | Medium (schema per tenant) | Medium tenants, HANA HDI |
| Separate DB per tenant | High (dedicated HDI) | Large tenants, compliance |
| Separate deployment | Maximum (dedicated app) | Premium tier, isolated infra |

## SaaS Registry (BTP)

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

## CAP SaaS (multi-tenant)

```javascript
// srv/saas-handler.js — subscription lifecycle callbacks
const cds = require('@sap/cds')

module.exports = class SaaSHandler extends cds.ApplicationService {
  async init() {
    // Called when a new tenant subscribes
    this.on('UPDATE', '/saas/subscription', async (req) => {
      const { subscribedTenantId, subscriptionAppId } = req.data
      // Create isolated HDI container for tenant
      await cds.deploy(`./gen/db`, {
        credentials: {
          database: 'HANA',
          schema: subscribedTenantId,
          hdi_container: `${subscriptionAppId}-${subscribedTenantId}`
        }
      })
      return { subscriptionUrl: `https://${subscribedTenantId}.my-app.com` }
    })

    // Called when tenant unsubscribes
    this.on('DELETE', '/saas/subscription', async (req) => {
      const { unsubscribedTenantId } = req.data
      // Clean up tenant data
      await cds.run(DROP.HDI_CONTAINER(unsubscribedTenantId))
    })
    await super.init()
  }
}
```

## XSUAA Tenant Mode

```json
{
  "xsappname": "my-saas-app",
  "tenant-mode": "shared", // shared or dedicated
  "scopes": [
    { "name": "$XSAPPNAME.User" },
    { "name": "$XSAPPNAME.Admin" }
  ],
  "role-templates": [
    { "name": "User", "scope-references": ["$XSAPPNAME.User"] },
    { "name": "Admin", "scope-references": ["$XSAPPNAME.Admin","$XSAPPNAME.User"] }
  ]
}
```

## Tenant Lifecycle

```
Onboarding
  → Subscribe (consumer clicks "Subscribe" in BTP cockpit)
    → SaaS Registry calls onSubscription callback
      → CAP deploys per-tenant HDI container
        → Tenant URL generated (https://<tenant>.app.com)
          → Consumer can access app

Offboarding
  → Unsubscribe (consumer clicks "Unsubscribe")
    → SaaS Registry calls onUnsubscription callback
      → CAP drops per-tenant HDI container
        → Tenant data deleted (or archived)
```

## Gochas

- **HDI container per tenant** — isolated but HANA memory per container adds up
- **XSUserApp tenant-mode: "shared"** — means shared UAA for all tenants. "dedicated" = separate
- **Subscription callback timeout**: 30 seconds — keep logic async
- **Tenant URL format**: `https://<subaccount-subdomain>-<app-name>.cfapps.<region>.hana.ondemand.com`
- **SaaS metering** — custom metrics via BTP Metering service for tenant billing
