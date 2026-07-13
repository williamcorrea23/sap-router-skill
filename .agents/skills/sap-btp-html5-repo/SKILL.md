---
name: sap-btp-html5-repo
description: SAP BTP HTML5 Application Repository — deploy and host SAPUI5/Fiori/HTML5 apps on BTP, app router configuration, versioning, integration with Launchpad Service. Use when deploying Fiori/UI5 apps to BTP, configuring app router for HTML5 apps, or managing UI5 app lifecycle.
trigger:
  - deploy Fiori app BTP
  - HTML5 app repository setup
  - app router xs-app.json configuration
  - UI5 app deploy html5-apps-repo
  - launchpad service integration
  - html5 deployer MTA
---

# SAP BTP HTML5 Application Repository

Host and serve SAPUI5/Fiori/HTML5 applications on SAP BTP — managed app hosting with built-in app router and Launchpad integration.

## Prerequisites

- SAP BTP subaccount with Cloud Foundry enabled
- CF CLI installed and logged in (`cf login`)
- HTML5 Application Repository entitlement (app-host plan)
- Node.js ≥ 18 and a built Fiori/UI5 app (`dist/` folder)
- XSUAA service instance for authentication
- SAP BAS or local dev environment with `mbt` and `@sap/html5-deployer`

## 1. Create the Service Instance

```bash
cf create-service html5-apps-repo app-host my-repo
cf create-service-key my-repo my-key
```

## 2. Configure App Router (xs-app.json)

```json
{
  "welcomeFile": "/index.html",
  "authenticationMethod": "route",
  "routes": [
    {
      "source": "^/sap/opu/odata/(.*)$",
      "target": "/sap/opu/odata/$1",
      "destination": "S4HANA_BACKEND",
      "csrfProtection": true,
      "authenticationType": "xsuaa"
    },
    {
      "source": "^/(.*)$",
      "target": "$1",
      "localDir": "webapp",
      "authenticationType": "xsuaa"
    }
  ]
}
```

Key fields: `source` (regex match), `destination` (CF destination name), `localDir` (static file path), `authenticationType` (`xsuaa` or `none`).

## 3. Deploy a Fiori App (CLI)

```bash
cd my-fiori-app
npm install
npm run build

npx @sap/html5-deployer deploy \
  --service-instance my-repo \
  --source ./dist \
  --app-name com.myorg.myapp
```

App becomes available at:
`https://<launchpad>.launchpad.cfapps.<region>.hana.ondemand.com/sites#myapp`

## 4. Deploy via MTA (Production)

```yaml
# mta.yaml
modules:
  - name: my-fiori-app
    type: html5
    path: app
    requires:
      - name: my-repo
      - name: my-xsuaa
      - name: s4hana-destination
    parameters:
      app-name: com.myorg.myapp

resources:
  - name: my-repo
    type: org.cloudfoundry.managed-service
    parameters:
      service: html5-apps-repo
      service-plan: app-host
```

```bash
mbt build
cf deploy mta_archives/my-fiori-app_1.0.0.mtar
```

## 5. Version Management and Rollback

```bash
# Deploy a specific version
npx @sap/html5-deployer deploy --app-version 2.1.0

# List all versions of an app
cf html5-list --app-name com.myorg.myapp

# Rollback to a previous version
cf html5-rollback --app-name com.myorg.myapp --version 2.0.0
```

## App Lifecycle

```
Create → Upload → Deploy → Test → Promote (Dev → Prod)
  ↑                                              ↓
  └────────── Update (new version) ──────────────┘
```

## When to Use vs Alternatives

- ✅ **SAPUI5/Fiori apps** — Native BTP hosting with Launchpad integration
- ✅ **Multi-version app management** — Built-in versioning and rollback
- ❌ **Static HTML without auth** → Use CF staticfile buildpack directly
- ❌ **React/Angular apps** → Use CF nginx buildpack or Kyma container

## Pitfalls

- **Pitfall: App name rejected on deploy**
  - Cause: Name must match `com.<org>.<appname>` — lowercase, dotted, globally unique.
  - Solution: Use a consistent naming convention. Check existing names with `cf html5-list` before deploying.

- **Pitfall: App not visible in Launchpad**
  - Cause: App not registered with Launchpad Service, or missing `sap.app` crossNavigation config in `manifest.json`.
  - Solution: Add `crossNavigation.inbounds` to `manifest.json`. Ensure the Launchpad Service subscription exists and the app is assigned to the same subaccount.

- **Pitfall: CORS errors when calling backend OData**
  - Cause: Browser blocks cross-origin requests. App router destination not configured for CORS.
  - Solution: Route all backend calls through the app router `xs-app.json` destination. Do not call the backend directly from the browser.

- **Pitfall: Deploy fails with "file too large"**
  - Cause: Maximum app size is 200 MB per version.
  - Solution: Exclude `node_modules/`, `test/`, and source maps from the dist folder. Use `.cfignore` or build config to strip dev assets.

- **Pitfall: Stale assets served after redeploy**
  - Cause: App router and CDN cache static assets aggressively.
  - Solution: Use hash-based filenames (e.g., `Component-ab12cd.js`) in the UI5 build config. This forces cache busting on version change.

## Verification

```bash
# 1. Verify service instance
cf services | grep my-repo

# 2. Verify app was deployed
cf html5-list --app-name com.myorg.myapp
# → Should list deployed versions

# 3. Test app router serves the app
curl "https://my-approuter.cfapps.<region>.hana.ondemand.com/index.html"
# → Should return HTML (redirect to login if auth required)

# 4. Verify OData destination works through app router
curl "https://my-approuter.cfapps.<region>.hana.ondemand.com/sap/opu/odata/sap/ZMY_SRV/EntitySet?\$top=1" \
  -H "Authorization: Bearer <jwt>"
# → Should return OData JSON, not CORS error

# 5. Verify app in Launchpad
# Open: https://<launchpad>.launchpad.cfapps.<region>.hana.ondemand.com/sites
# → App should appear in the site navigation
```
