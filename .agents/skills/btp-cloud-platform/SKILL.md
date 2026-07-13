---
name: btp-cloud-platform
description: SAP BTP Cloud Platform — account hierarchy, entitlements, CLI tools, marketplace services, and platform navigation.
trigger:
  keywords: [BTP cockpit, subaccounts, entitlements, btp CLI, cf CLI, account model, marketplace, service marketplace, platform navigation, global account]
  intent: Navigate SAP BTP platform account model, manage entitlements, and choose the right CLI tool for platform operations
---

# SAP BTP Cloud Platform

Core platform: account model, entitlements, service marketplace, and CLI tooling.

## Prerequisites

- SAP BTP global account with at least one subaccount
- Admin or member role on the target subaccount
- `btp` CLI and `cf` CLI installed locally

## 1. Account Hierarchy

```
Global Account (contract-level)
├── Directory: DEV-DIR (organizational grouping)
│   └── Subaccount: DEV
│       ├── Entitlements (service quotas)
│       ├── CF Org: dev / Space: dev
│       ├── Service Instances (HANA, ABAP, Destination...)
│       └── Subscriptions (Launchpad, Work Zone, Build)
├── Subaccount: PRD
└── Directory: SHARED-DIR
```

## 2. Log In with btp CLI (Account Level)

```bash
btp login --url https://cockpit.btp.cloud.sap
btp list accounts/subaccount
btp list accounts/entitlement --subaccount DEV
```

## 3. Assign Entitlements

```bash
btp assign accounts/entitlement \
  --to-subaccount DEV \
  --for-service abap \
  --plan standard \
  --amount 1
```

Entitlement = what services a subaccount CAN use (assigned from global account).
Quota = how much of a plan can be provisioned.

## 4. Log In with cf CLI (Runtime Level)

```bash
cf login -a https://api.cf.us10.hana.ondemand.com -o dev -s dev
cf marketplace                       # list available services and plans
cf services                          # list existing instances
```

## 5. Create a Service Instance

```bash
cf create-service abap standard my-abap-env
cf create-service hana hana my-hana-db
cf create-service destination lite my-dest
```

## 6. Key Marketplace Services

- **ABAP Environment** — `standard` / `abap_cloud` — Steampunk ABAP development
- **SAP HANA Cloud** — `hana` — Cloud database
- **Destination** — `lite` — HTTP destination management
- **Connectivity** — `standard` — Cloud Connector bridge to on-premise
- **XSUAA** — `application` — Authentication and authorization
- **Application Autoscaler** — `standard` — Auto-scaling CF apps
- **HTML5 App Repository** — `app-host` — Host Fiori/UI5 apps
- **Job Scheduling** — `standard` — Cron-based scheduling
- **Cloud Logging** — `standard` — Centralized logging (OpenSearch)

## btp CLI vs cf CLI — When to Use Which

- **btp CLI** — account management: subaccounts, entitlements, subscriptions, directories
- **cf CLI** — runtime operations: deploy apps, create/bind services, manage spaces

## Pitfalls

- **Subaccount region is immutable**
  - Cause: Region is set at subaccount creation and cannot be changed later.
  - Solution: Create a new subaccount in the desired region, migrate instances and subscriptions.

- **Service creation blocked despite entitlement**
  - Cause: CF org quota or space quota may limit service instances independently of entitlements.
  - Solution: Check `cf org` quota and space quota. Request admin to increase quota if needed.

- **Confusion between btp CLI and cf CLI**
  - Cause: Both tools operate on BTP but at different layers (account vs runtime).
  - Solution: Use `btp` for subaccounts/entitlements/subscriptions. Use `cf` for apps/services/bindings within a space.

- **Entitlement assigned but plan not visible in marketplace**
  - Cause: Entitlement may not have propagated, or the plan name differs from expectation.
  - Solution: Re-check entitlement in BTP Cockpit. Run `btp list accounts/entitlement --subaccount <name>`. Allow a few minutes for propagation.

- **Directory vs subaccount confusion**
  - Cause: Directories group subaccounts but are not billing or runtime entities.
  - Solution: Entitlements and services live on subaccounts, not directories. Use directories only for organizational grouping and bulk entitlement assignment.

## Verification

```bash
# btp CLI — confirm subaccounts and entitlements
btp list accounts/subaccount
btp list accounts/entitlement --subaccount DEV

# cf CLI — confirm runtime is accessible
cf target                             # should show correct org/space
cf marketplace | grep hana            # service should appear if entitled

# BTP Cockpit — visual confirmation
# https://cockpit.btp.cloud.sap → Global Account → Subaccount → Entitlements
```
