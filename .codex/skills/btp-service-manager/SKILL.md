---
name: btp-service-manager
description: SAP BTP Service Manager — service instance lifecycle, service binding, service key management, service plan selection, instance parameters, service broker integration, instance sharing across CF spaces. Use when creating/managing BTP service instances, binding services to applications, or troubleshooting service provisioning failures.
---

# SAP BTP Service Manager

Lifecycle management for BTP service instances.

## Service Instance Lifecycle

```
Create Instance → Bind to App → Use → Unbind → Delete Instance
       ↓                              ↓
   Service Key                    Rotate Keys
```

## CF CLI Commands

```bash
cf marketplace                    # list service plans
cf create-service hana hdi-shared my-hdi  # create HANA HDI container
cf create-service-key my-hdi my-key      # create service key
cf service-key my-hdi my-key             # view key JSON
cf bind-service my-app my-hdi            # bind to application
cf unbind-service my-app my-hdi          # unbind
cf delete-service my-hdi                 # delete instance
```

## Service Keys vs Binding

| Feature | Service Key | Binding |
|---|---|---|
| Scope | Any BTP space | Same CF space |
| Credential format | JSON (+url, +user, +password) | VCAP_SERVICES env var |
| Rotation | Manual | Re-bind |
| Always use when | External access, monitoring tools | App-internal access |

## Instance Sharing

```bash
cf share-service my-hdi -s other-space  # share instance to another CF space
```

## Gotchas
- Service instances are subaccount-scoped by default
- Some plans (lite/free) cannot be upgraded to standard — re-create
- Service key exposes credentials — rotate regularly
- Instance deletion may fail if bindings exist — unbind first
