---
name: sap-btp-launchpad
description: >
  SAP BTP Launchpad Service — host Fiori/UI5 apps, configure launchpad sites,
  manage HTML5 app repo, content providers, roles. Use when setting up a
  Fiori Launchpad on BTP or choosing between Launchpad Service and Build Work Zone.
trigger:
  keywords:
    - btp launchpad service
    - fiori launchpad on btp
    - html5 application repository
    - launchpad site configuration
    - content provider federation
    - launchpad vs work zone
  intent: "Configure or host Fiori apps on SAP BTP Launchpad Service"
---

# SAP BTP Launchpad Service

Host SAPUI5/Fiori apps on BTP, configure launchpad sites, manage content and roles.

## Prerequisites

- SAP BTP subaccount with Cloud Foundry enabled
- `cf` CLI installed and authenticated (`cf login`)
- A Fiori/UI5 app built and ready to deploy (MTA or standalone)
- Entitlements for: **Launchpad Service**, **HTML5 Application Repository**, **Destination Service**
- Admin role collection `Launchpad_Admin` assigned to your user

## Steps

### 1. Create Required Service Instances

```bash
# HTML5 Application Repository (hosts deployed app static content)
cf create-service html5-apps-repo app-host my-html5-repo

# HTML5 Application Repository (runtime — serves apps to launchpad)
cf create-service html5-apps-repo app-runtime my-html5-runtime

# Launchpad Service instance
cf create-service launchpad standard my-launchpad
```

### 2. Deploy a Fiori App to HTML5 Repository

```bash
# If using MTA — deploy with mbt
mbt build -t ./mta_archives
cf deploy ./mta_archives/my-app_1.0.0.mtar

# If standalone — push app, bind repo, restage
cf push my-fiori-app --no-start
cf bind-service my-fiori-app my-html5-repo
cf start my-fiori-app
```

### 3. Configure Launchpad Site (CommonDataModel.json)

```json
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

### 4. Set Up Content Provider (Federated Content from S/4HANA)

1. In BTP Cockpit → subaccount → **Destinations** → create destination to S/4HANA
2. Set properties: `Type=HTTP`, `Authentication=PrincipalPropagation`, `WebIDEUsage=odata_gen`
3. Launchpad Service → **Content Providers** → add destination
4. Federated catalogs appear in site editor within ~5 minutes

### 5. Assign Role Collections

```
Launchpad_Admin  → configure sites, manage content
Purchaser        → see Purchasing group tiles
Viewer           → see Dashboard group tiles only
```

Assign via BTP Cockpit → **Role Collections** → select collection → add user.

### 6. Launchpad Service vs Build Work Zone — Decision Guide

- **Launchpad Service**: simple Fiori portal, tiles, themes, content federation. Best for straightforward app hosting.
- **Build Work Zone (Advanced)**: adds UI Integration Cards, Workspaces, Knowledge Graph, advanced external federation. Best for enterprise portals with widgets and content aggregation.

## Pitfalls

| # | Pitfall | Cause | Solution |
|---|---------|-------|----------|
| 1 | App not visible in launchpad | HTML5 repo not bound or app not deployed to `app-host` | Verify `cf services` shows repo; redeploy with `cf bind-service` then restage |
| 2 | Tiles show error "App not found" | `appId` in CommonDataModel.json doesn't match deployed app ID | Check `manifest.json` → `sap.app/id`; use exact same value in tile config |
| 3 | Federated content missing or stale | Content provider cache (5 min) hasn't refreshed | Wait 5 min or click "Refresh" in Content Providers panel |
| 4 | Users can't see tiles | Role collection not assigned to user | BTP Cockpit → Role Collections → add user to appropriate collection |
| 5 | Launchpad URL returns 404 | Wrong subdomain or site not published | Check site status = "Published" in Launchpad Service cockpit; verify subdomain |
| 6 | Performance degradation | Too many tiles in one group (>200) | Split tiles across multiple groups; keep ≤200 per group |

## Verification

```bash
# Check service instances exist
cf services | grep -E "html5|launchpad"

# Verify app is deployed to HTML5 repo
cf apps
# App should show as "started" with bound html5-apps-repo service

# Access launchpad site
# URL format: https://<launchpad-subdomain>.launchpad.cfapps.<region>.hana.ondemand.com
# Open in browser → verify tiles render → click a tile → app loads
```

Confirm in BTP Cockpit:
- Launchpad Service → site status = **Published**
- Site editor shows all groups and tiles
- Test user with `Viewer` role sees only Dashboard tiles
