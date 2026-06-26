---
name: sap-btp-html5-repo
description: SAP BTP HTML5 Application Repository — deploy and host HTML5/SAPUI5/Fiori apps on BTP, app lifecycle management, versioning, app router configuration, xs-app.json patterns, integration with Launchpad Service, CI/CD for HTML5 apps. Use when deploying Fiori/UI5 apps to BTP, configuring app router for HTML5 apps, or managing UI5 app lifecycle on SAP BTP.
---

# SAP BTP HTML5 Application Repository

Host and serve SAPUI5/Fiori/HTML5 applications on SAP BTP — managed app hosting with built-in app router.

## Service Instance

```bash
cf create-service html5-apps-repo app-host my-repo
cf create-service-key my-repo my-key
```

## App Router (xs-app.json)

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

## Deploying a Fiori App

```bash
# 1. Build UI5 app
cd my-fiori-app
npm install
npm run build

# 2. Package with HTML5 deployer
npx @sap/html5-deployer deploy \
  --service-instance my-repo \
  --source ./dist \
  --app-name com.myorg.myapp

# 3. App available at:
# https://<launchpad>.launchpad.cfapps.us10.hana.ondemand.com/sites#myapp
```

## MTA Integration

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
      service-url: ~{my-repo/url}

resources:
  - name: my-repo
    type: org.cloudfoundry.managed-service
    parameters:
      service: html5-apps-repo
      service-plan: app-host
```

## App Lifecycle

```
Create → Upload → Deploy → Test → Promote (Dev → Prod)
  ↑                                              ↓
  └────────── Update (new version) ──────────────┘
```

## Version Management

```bash
# Deploy specific version
npx @sap/html5-deployer deploy --app-version 2.1.0

# List versions
cf html5-list --app-name com.myorg.myapp

# Rollback to previous version
cf html5-rollback --app-name com.myorg.myapp --version 2.0.0
```

## Gotchas

- **App name format**: `com.<org>.<appname>` — lowercase, dotted, globally unique
- **File size limit**: 200MB per app version
- **Asset caching**: app router caches static assets — add hash to filenames for cache busting
- **CORS**: configured in xs-app.json destination, not in app code
- **Redirect after login**: xs-app.json `welcomeFile` handles post-auth redirect
