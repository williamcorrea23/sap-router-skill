---
name: sap-fiori-apps-reference
description: SAP Fiori Apps Reference — Fiori app library navigation, app ID lookup (Fxxxx), SAP Fiori lighthouse apps, app activation in S/4HANA (F1748), business role assignment, tile catalog management, Spaces and Pages configuration, SAP Mobile Start. Use when looking up Fiori app IDs, activating Fiori apps, or configuring the Fiori Launchpad content catalog.
---

# SAP Fiori Apps Reference

SAP Fiori app library navigation, activation, and configuration.

## Fiori App Library

Browse at: https://fioriappslibrary.hana.ondemand.com

Search by: app name, app ID (Fxxxx), transaction code, business role.

## App Activation (S/4HANA)

```
Transaction: /N/UI2/FLPD_CUST (Fiori Launchpad Designer)
  → Create Catalog → Add Tile → Select App ID
    → Configure Target Mapping (semantic object + action)

  Transaction: /N/UI2/FLPD_CONF (Fiori Launchpad Content Manager)
  → Create Group → Add Tile from Catalog
```

## App ID Format

```
Fxxxx — SAP standard app (e.g. F1511 = Create Purchase Order)
Zxxxx — Custom app
```

## Business Role Assignment

```
Transaction: PFCG → Create Role → Menu → SAP Fiori Tile Catalog
  → Add catalog to role menu
  → Assign role to users
```

## Spaces and Pages (S/4HANA 2021+)

Replaces traditional Fiori groups:
```
Space: "Procurement"
├── Page: "Purchase Orders"
│   ├── App: F1511 (Create PO)
│   └── App: F2705 (Manage POs)
└── Page: "Contracts"
    └── App: F2400 (Manage Contracts)
```

## SAP Mobile Start

Fiori apps automatically available in SAP Mobile Start app:
- Same Fiori tiles, same catalog
- Push notifications via SAP Notification service
- Offline-capable for approved apps

## Gotchas
- App may need IAM business catalog assignment (not just PFCG)
- Launchpad cache: run /IWFND/CACHE_CLEANUP after catalog changes
- Some Fiori apps require additional setup (Gateway, backend activation)
- Fiori Launchpad URL: https://<host>:<port>/sap/bc/ui2/flp
