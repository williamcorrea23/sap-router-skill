---
name: sap-btp-feature-flags
description: SAP BTP Feature Flags Service — feature toggles for BTP applications, gradual rollouts, A/B testing, feature lifecycle (dev → beta → GA → deprecated), feature flag evaluation at runtime, integration with CAP and ABAP Cloud, feature flag dashboards. Use when implementing feature flags on BTP, managing gradual rollouts, toggling features per tenant/user, or implementing A/B testing for SAP applications.
---

# SAP BTP Feature Flags Service

Feature toggle management for SAP BTP — controlled rollouts, tenant-specific features, A/B testing.

## Service Instance

```bash
cf create-service feature-flags standard my-feature-flags
cf bind-service my-app my-feature-flags
```

## Define Feature Flags

```json
{
  "features": [
    {
      "name": "new-product-search",
      "description": "Enhanced product search with fuzzy matching",
      "lifecycle": "beta",
      "defaultValue": false,
      "rolloutPercentage": 10,
      "targetTenants": [],
      "rules": {
        "userGroups": ["beta-testers"],
        "timeRange": { "from": "2026-07-01", "to": "2026-08-01" }
      }
    },
    {
      "name": "dark-mode",
      "description": "Dark mode UI theme",
      "lifecycle": "ga",
      "defaultValue": true,
      "rolloutPercentage": 100
    }
  ]
}
```

## Feature Evaluation at Runtime

```javascript
// CAP service with feature flags
const { FeatureFlags } = require('@sap/feature-flags')

module.exports = class ProductService extends cds.ApplicationService {
  async init() {
    this.on('searchProducts', async (req) => {
      const ff = new FeatureFlags()

      // Check if feature is enabled for current user/tenant
      const newSearchEnabled = await ff.isEnabled('new-product-search', {
        tenant: req.tenant,
        user: req.user.id,
        attributes: { group: req.user.groups }
      })

      if (newSearchEnabled) {
        return this.fuzzySearch(req.data.query)  // New implementation
      } else {
        return this.exactSearch(req.data.query)  // Old implementation
      }
    })
    await super.init()
  }
}
```

## Feature Lifecycle

```
Development → Beta → General Availability (GA) → Deprecated → Removed
   (internal)  (10%)   (100%)                    (read-only)  (deleted)
```

## Gradual Rollout

```javascript
// Rollout strategy
const rolloutConfig = {
  "new-checkout-flow": {
    percentage: 25,  // 25% of users
    sticky: true,    // same user always gets same variant
    users: ["VIP_CUSTOMERS"],  // target group
    excludeTenants: ["tenant-test-3"]
  }
}

// A/B test tracking
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

## ABAP Cloud Integration

```abap
" Check feature flag from ABAP Cloud
DATA(lo_ff) = cl_feature_flags_client=>create_for_cloud( ).
DATA(lv_enabled) = lo_ff->is_enabled(
  iv_feature_name = 'Z_NEW_PRODUCT_SEARCH'
  iv_user_id      = sy-uname
  iv_tenant_id    = cl_abap_context_info=>get_tenant_id( )
).

IF lv_enabled = abap_true.
  " Use new implementation
ELSE.
  " Use old implementation
ENDIF.
```

## Dashboard

```
SAP BTP Cockpit → Feature Flags → Dashboard
  └── Features list (name, lifecycle, rollout %, users impacted)
      └── Toggle ON/OFF per tenant
          └── Audit log of all changes
```

## Gotchas

- **Sticky rollout**: user always gets same variant — requires persistence layer
- **Lifecycle enforcement**: deprecated flags warn at runtime; removed flags error
- **Tenant-specific flags**: configure in SaaS registry callback, not in default config
- **Performance**: evaluate at app startup, cache for request duration, do not call per user
- **Maximum flags**: 500 per service instance (standard plan)
