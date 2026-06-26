---
name: sap-btp-launchpad
description: SAP BTP Launchpad Service — Fiori Launchpad on BTP, app hosting in HTML5 Application Repository, site configuration, content providers, tile catalog, roles and authorization, SAP Build Work Zone vs Launchpad Service. Use when hosting Fiori apps on BTP, configuring the Fiori Launchpad on BTP, or deciding between Launchpad Service and SAP Build Work Zone.
---

# SAP BTP Launchpad Service

Fiori Launchpad on SAP BTP — host SAPUI5/Fiori apps, configure sites, manage content.

## Architecture

```
SAP BTP Launchpad Service
├── Sites (launchpad instances)
│   ├── Content (apps, groups, catalogs)
│   ├── Roles (who can access what)
│   └── Themes (branding)
├── HTML5 Application Repository
│   └── Deployed Fiori/UI5 apps
└── Destination Service
    └── Backend connections (S/4HANA, CAP services)
```

## Site Configuration

```json
// CommonDataModel.json — site descriptor
{
  "sap.cloud.portal": {
    "config": {
      "siteId": "procurement-portal",
      "title": "Procurement Hub",
      "theme": "sap_horizon",
      "groups": [
        {
          "id": "purchasing",
          "title": "Purchasing",
          "tiles": [
            { "appId": "create-po", "title": "Create PO" },
            { "appId": "manage-pos", "title": "Manage POs" }
          ]
        }
      ]
    }
  }
}
```

## HTML5 Application Repository

```bash
# Create HTML5 repo service instance
cf create-service html5-apps-repo app-host my-html5-repo

# Deploy Fiori app
cf push my-fiori-app --no-start
cf bind-service my-fiori-app my-html5-repo
cf start my-fiori-app

# App URL in Launchpad:
# https://<launchpad-subdomain>.launchpad.cfapps.<region>.hana.ondemand.com
```

## Launchpad Service vs Build Work Zone

| Feature | Launchpad Service | Build Work Zone (Advanced) |
|---|---|---|
| Fiori app hosting | ✅ | ✅ |
| Custom themes | ✅ | ✅ |
| UI Integration Cards | ❌ | ✅ |
| Workspaces | ❌ | ✅ |
| Knowledge Graph | ❌ | ✅ |
| External content federation | Limited | ✅ |
| Mobile (SAP Mobile Start) | ✅ | ✅ |
| Best for | Simple Fiori portal | Enterprise portal with widgets |

## Content Providers

```
Launchpad Service → Content Provider → SAP S/4HANA (federated content)
                                    → CAP App (local HTML5 repo)
                                    → URL App (external)
```

## Roles

```
Role Collections (BTP Cockpit)
├── Launchpad_Admin → configure sites, manage content
├── Purchaser → see Purchasing group tiles
└── Viewer → see Dashboard group tiles only
```

## Gotchas

- **HTML5 app name format**: `com.myorg.appname` — must be unique
- **Launchpad subdomain**: auto-generated, can be customized in BTP cockpit
- **Content federation cache**: 5 min delay after S/4HANA changes
- **Site max tiles**: 200 per group recommended for performance
