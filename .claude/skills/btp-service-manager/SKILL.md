---
name: btp-service-manager
description: SAP BTP Service Manager — service instance lifecycle, binding, service keys, instance sharing, and provisioning troubleshooting.
trigger: user asks about creating BTP service instances, binding services, service keys, or fixing provisioning failures
---

# SAP BTP Service Manager

Lifecycle management for BTP service instances: create, bind, key, share, unbind, delete.

## Prerequisites

- CF CLI logged in to target org/space
- Target service entitlement assigned to the subaccount (check in BTP Cockpit → Entitlements)
- Sufficient quota for the chosen service plan

## 1. Explore the Marketplace

```bash
cf marketplace                       # list all available services
cf marketplace -s hana               # show plans for a specific service
```

## 2. Create a Service Instance

```bash
# Example: HANA HDI container
cf create-service hana hdi-shared my-hdi

# Example: with custom parameters (JSON)
cf create-service hana hdi-shared my-hdi -c '{"database_id":"abc-123"}'

# Check provisioning status (wait for "create succeeded")
cf services
```

## 3. Create a Service Key (External Access)

```bash
cf create-service-key my-hdi my-key
cf service-key my-hdi my-key          # view credentials JSON
```

Use service keys when an external tool or different subaccount needs access.

## 4. Bind Service to Application

```bash
cf bind-service my-app my-hdi
cf restage my-app                     # restart to pick up VCAP_SERVICES

# Verify binding injected into environment
cf env my-app | grep -A 20 hana
```

## 5. Share Instance Across CF Spaces

```bash
cf share-service my-hdi -s other-space
```

The shared instance is read-accessible in the target space for binding.

## 6. Unbind and Delete

```bash
cf unbind-service my-app my-hdi       # unbind first
cf delete-service-key my-hdi my-key   # delete keys
cf delete-service my-hdi              # then delete instance
```

## Service Key vs Binding — Quick Reference

- **Service Key** — any space, JSON credentials, manual rotation. Use for external access / monitoring tools.
- **Binding** — same CF space, injected into `VCAP_SERVICES`, re-bind to rotate. Use for app-internal access.

## Pitfalls

- **Instance deletion fails with bindings active**
  - Cause: Active bindings or service keys block deletion.
  - Solution: Unbind all apps and delete all service keys first, then retry `cf delete-service`.

- **Lite/free plan cannot be upgraded in place**
  - Cause: Some plans do not support in-place plan changes.
  - Solution: Create a new instance on the target plan, migrate data, rebind apps, then delete the old instance.

- **Service instances are subaccount-scoped**
  - Cause: Instances exist only within the subaccount where they were created.
  - Solution: Use `cf share-service` for cross-space access within the same subaccount. For cross-subaccount, use service keys or multitenant sharing.

- **Provisioning stuck in "create in progress"**
  - Cause: Backend provider delay, quota exhaustion, or entitlement not assigned.
  - Solution: Check entitlements in BTP Cockpit. If entitled, wait 5–10 min. If still stuck, open an SAP support ticket with the instance ID.

- **Service key credentials exposed**
  - Cause: Keys are long-lived JSON credentials stored in plaintext.
  - Solution: Rotate keys regularly — delete old key, create new key, update consumers. Never commit keys to version control.

## Verification

```bash
# Instance is provisioned
cf services | grep my-hdi              # status should show "create succeeded"

# Service key is valid
cf service-key my-hdi my-key           # should return JSON with credentials

# App has the binding
cf env my-app | grep -A 5 hana         # VCAP_SERVICES should contain the instance

# Shared instance visible in other space
cf target -s other-space && cf services | grep my-hdi
```
