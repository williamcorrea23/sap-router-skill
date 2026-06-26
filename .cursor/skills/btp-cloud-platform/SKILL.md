---
name: btp-cloud-platform
description: SAP BTP Cloud Platform — global accounts, subaccounts, directories, regions, entitlements, service marketplace, CF org/space management, btp CLI vs cf CLI, quota plans, service binding vs service keys, platform monitoring. Use when navigating BTP cockpit, managing subaccounts, assigning entitlements, or using BTP command-line tools.
---

# SAP BTP Cloud Platform

Core platform services — account model, entitlements, and service management.

## Account Hierarchy

```
Global Account (contract-level)
├── Subaccount: DEV (development)
│   ├── Entitlements (service quotas)
│   ├── Cloud Foundry: org=dev / space=dev
│   ├── Service Instances (ABAP, HANA, Destination, etc.)
│   └── Subscriptions (Launchpad, Work Zone, Build)
├── Subaccount: PRD (production)
└── Directories (organizational grouping)
```

## CLI Tools

```bash
# btp CLI (account management)
btp login --url https://cockpit.btp.cloud.sap
btp list accounts/subaccount
btp assign accounts/entitlement --to-subaccount dev --for-service abap --plan standard

# cf CLI (runtime operations)
cf login -a https://api.cf.us10.hana.ondemand.com -o dev -s dev
cf marketplace  # list available service plans
cf create-service abap standard my-abap
cf services     # list service instances
```

## Service Marketplace Key Services

| Service | Plan | Use Case |
|---|---|---|
| ABAP Environment | standard / abap_cloud | Steampunk ABAP |
| SAP HANA Cloud | hana | Cloud database |
| Destination | lite | HTTP destination management |
| Connectivity | standard | Cloud Connector bridge |
| XSUAA | application | Auth and authorization |
| Application Autoscaler | standard | Auto-scaling CF apps |
| HTML5 Application Repository | app-host | Host Fiori/UI5 apps |
| Job Scheduling | standard | Cron-based scheduling |
| Cloud Logging | standard | Centralized logging (OpenSearch) |

## Entitlements vs Quotas

Entitlement: what services a subaccount CAN use (assigned from global account).
Quota: how much of a service plan a subaccount can provision (assigned with entitlement).

## Gotchas
- Subaccount region is immutable after creation
- CF org quota may block service creation even with entitlements
- btp CLI vs cf CLI — different levels (account vs runtime)
