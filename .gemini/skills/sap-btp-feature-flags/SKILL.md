---
name: sap-btp-feature-flags
description: SAP BTP Feature Flags Service — feature toggles for BTP applications, gradual rollouts, A/B testing, feature lifecycle management. Use when implementing feature flags on BTP, managing gradual rollouts, toggling features per tenant/user, or integrating feature flags with CAP and ABAP Cloud.
trigger:
  - feature flags BTP setup
  - gradual rollout BTP
  - A/B testing SAP application
  - feature toggle CAP Node.js
  - feature flag ABAP Cloud
  - feature lifecycle management BTP
  - tenant-specific feature toggle
---

# SAP BTP Feature Flags Service

Feature toggle management for SAP BTP — controlled rollouts, tenant-specific features, A/B testing, runtime evaluation.

## Prerequisites

- SAP BTP subaccount with Cloud Foundry enabled
- CF CLI installed and logged in (`cf login`)
- Feature Flags entitlement (standard plan) in the subaccount
- Node.js ≥ 18 and `@sap/feature-flags` package (for CAP integration)
- ABAP Cloud environment (for ABAP-side evaluation)

## 1. Create and Bind the Service Instance

```bash
cf create-service feature-flags standard my-feature-flags
cf bind-service my-app my-feature-flags
cf restage my-app
```

## 2. Define Feature Flags (Dashboard or REST API)

```bash
# Create a flag via REST API
curl -X POST "https://feature-flags.cfapps.<region>.hana.ondemand.com/api/v1/flags" \
  -H "Authorization: Bearer $(cf oauth-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-product-search",
    "description": "Enhanced product search with fuzzy matching",
    "lifecycle": "beta",
    "defaultValue": false,
    "rolloutPercentage": 10,
    "rules": {
      "userGroups": ["beta-testers"],
      "timeRange": { "from": "2026-07-01", "to": "2026-08-01" }
    }
  }'

# List all flags
curl "https://feature-flags.cfapps.<region>.hana.ondemand.com/api/v1/flags" \
  -H "Authorization: Bearer $(cf oauth-token)"
```

## 3. Evaluate Feature Flags at Runtime (CAP/Node.js)

```bash
npm install @sap/feature-flags
```

```javascript
const { FeatureFlags } = require('@sap/feature-flags')

module.exports = class ProductService extends cds.ApplicationService {
  async init() {
    this.on('searchProducts', async (req) => {
      const ff = new FeatureFlags()
      const enabled = await ff.isEnabled('new-product-search', {
        tenant: req.tenant,
        user: req.user.id,
        attributes: { group: req.user.groups }
      })
      if (enabled) {
        return this.fuzzySearch(req.data.query)
      } else {
        return this.exactSearch(req.data.query)
      }
    })
    await super.init()
  }
}
```

## 4. Evaluate Feature Flags in ABAP Cloud

```abap
DATA(lo_ff) = cl_feature_flags_client=>create_for_cloud( ).
DATA(lv_enabled) = lo_ff->is_enabled(
  iv_feature_name = 'Z_NEW_PRODUCT_SEARCH'
  iv_user_id      = sy-uname
  iv_tenant_id    = cl_abap_context_info=>get_tenant_id( )
).
IF lv_enabled = abap_true.
  " New implementation
ELSE.
  " Old implementation
ENDIF.
```

## 5. Gradual Rollout and A/B Testing

```javascript
// Get variant for A/B testing (sticky: same user always gets same variant)
const variant = await ff.getVariant('new-checkout-flow', { user: req.user.id })
if (variant === 'B') {
  req.audit({
    category: 'ab-test',
    object: { type: 'Feature', id: 'new-checkout-flow' },
    attributes: [{ name: 'variant', value: 'B' }]
  })
  return this.newCheckoutFlow(req)
}
```

Rollout config fields: `rolloutPercentage` (0–100), `targetTenants` (allowlist), `excludeTenants`, `userGroups`, `timeRange`.

## Feature Lifecycle

```
Development → Beta → GA → Deprecated → Removed
  (internal)  (10%)  (100%) (read-only)  (deleted)
```

- **Deprecated**: flag still evaluates but logs a warning each access.
- **Removed**: flag evaluation returns error. Remove all code references before setting to Removed.

## When to Use vs Alternatives

- ✅ **Gradual feature rollout** — percentage-based, tenant-scoped
- ✅ **A/B testing** — variant assignment with sticky users
- ✅ **Tenant-specific features** — per-tenant enable/disable
- ❌ **App configuration values** → Use App Configuration Service
- ❌ **Canary releases** → Use Blue-Green Deployment in CF

## Pitfalls

- **Pitfall: Flag evaluated per user instead of per request**
  - Cause: Calling `ff.isEnabled()` for every user in a loop causes N network calls.
  - Solution: Evaluate once per request lifecycle. Cache result for the request scope. Do not evaluate at app startup unless the flag is static.

- **Pitfall: Sticky rollout not working**
  - Cause: No persistence layer configured, so variant assignment resets on restart.
  - Solution: Ensure the Feature Flags service instance has a persistence plan. Sticky rollout uses a hash of user ID — no external store needed, but the service must be running.

- **Pitfall: Deprecated flag crashes production**
  - Cause: Setting lifecycle to "Deprecated" only logs warnings, but "Removed" throws an error at evaluation.
  - Solution: Search codebase for all references to the flag before changing lifecycle. Use `grep -r "flag-name" src/` to find all call sites.

- **Pitfall: Tenant-specific flags ignored**
  - Cause: Flags configured in default config JSON are global. Tenant-specific overrides must go through the SaaS registry callback.
  - Solution: Configure tenant-specific flags via the subscription callback endpoint, not in the default flag definition.

- **Pitfall: Exceeded flag limit**
  - Cause: Standard plan allows max 500 flags per service instance.
  - Solution: Clean up flags in "Removed" lifecycle. Archive and delete unused flags regularly.

## Verification

```bash
# 1. Verify service instance exists and is bound
cf services | grep my-feature-flags
cf env my-app | grep -A5 feature-flags

# 2. Verify flag exists via API
curl "https://feature-flags.cfapps.<region>.hana.ondemand.com/api/v1/flags/new-product-search" \
  -H "Authorization: Bearer $(cf oauth-token)"
# → Should return JSON with flag definition

# 3. Test flag evaluation from app
curl "https://my-app.cfapps.<region>.hana.ondemand.com/odata/v4/Products/searchProducts?query=test" \
  -H "Authorization: Bearer <jwt>"
# → Should return search results (new or old path depending on flag state)

# 4. Verify audit log in BTP Cockpit
# Navigate: BTP Cockpit -> Subaccount -> Feature Flags -> Dashboard
# Note: Audit Log tab availability depends on your Feature Flags service plan
```
