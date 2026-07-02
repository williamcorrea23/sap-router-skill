---
name: sap-btp-devops
description: SAP BTP DevOps — CI/CD pipeline configuration, MTA build automation, automated testing, transport integration (CTMS), GitHub Actions for BTP, SAP Continuous Integration and Delivery service, Jenkins. Use when setting up CI/CD for BTP, configuring deployment pipelines, or connecting Git to BTP deployments.
trigger:
  - CI/CD pipeline BTP setup
  - MTA build automation
  - GitHub Actions BTP deploy
  - SAP Continuous Integration and Delivery
  - CTMS transport management
  - Jenkins pipeline BTP
  - automated testing BTP pipeline
---

# SAP BTP DevOps

CI/CD on SAP BTP — automated build, test, and deployment pipelines for CAP and Fiori applications.

## Prerequisites

- SAP BTP subaccount with CF enabled
- Git repository (GitHub, GitLab, or Bitbucket)
- CF CLI installed: `cf install-plugin MTAPlugin` (MTA deploy plugin)
- `mbt` (MTA Build Tool): `npm install -g mbt`
- Node.js ≥ 18, npm ≥ 9
- SAP Continuous Integration and Delivery service entitlement (optional, for BTP-native CI/CD)
- For production deploys: CF credentials stored as CI secrets

## 1. Configure SAP CI/CD Service Pipeline

```yaml
# .pipeline/config.yml — placed in repo root
general:
  productiveBranch: main
  buildTool: mta

stages:
  Build:
    mtaBuild:
      buildTarget: CF
      mtaBuildTool: cloudMbt

  Test:
    npmTest:
      command: npm test

  Lint:
    npmLint:
      command: npm run lint

  Deploy to DEV:
    cfDeploy:
      deployType: standard
      cfApiEndpoint: https://api.cf.us10.hana.ondemand.com
      cfOrg: my-org
      cfSpace: dev
      deployTool: mtaDeployPlugin

  Deploy to PRD:
    cfDeploy:
      cfSpace: prd
      manualConfirmation: required
```

```bash
# Add webhook in Git provider pointing to CI/CD service
# BTP Cockpit → Continuous Integration and Delivery → Add repository → Connect webhook
```

## 2. GitHub Actions Pipeline (Alternative)

```yaml
# .github/workflows/btp-cicd.yml
name: BTP CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm install -g mbt && mbt build
      - run: npm test
      - name: Deploy to DEV
        run: |
          cf login -a ${{ secrets.CF_API }} -u ${{ secrets.CF_USER }} \
            -p ${{ secrets.CF_PASSWORD }} -o my-org -s dev
          cf deploy mta_archives/*.mtar
      - name: Smoke test
        run: curl -f https://my-app-dev.cfapps.us10.hana.ondemand.com/health

  deploy-prd:
    needs: build-and-deploy
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to PRD
        run: |
          cf login -a ${{ secrets.CF_API }} -u ${{ secrets.CF_USER }} \
            -p ${{ secrets.CF_PASSWORD }} -o my-org -s prd
          cf deploy mta_archives/*.mtar
```

## 3. Transport Integration (CTMS)

```yaml
# Add to .pipeline/config.yml stages
Transport:
  uploadToTransportManagement:
    transportManagementServiceCredentialsId: ctms-credentials
    nodeName: dev-transport-node
```

## 4. Jenkins Pipeline (Alternative)

```groovy
pipeline {
  agent any
  stages {
    stage('Build')   { steps { sh 'mbt build' } }
    stage('Test')    { steps { sh 'npm test' } }
    stage('Deploy DEV') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'btp-credentials',
          usernameVariable: 'CF_USER', passwordVariable: 'CF_PASSWORD')]) {
          sh 'cf login -a $CF_API -u $CF_USER -p $CF_PASSWORD -o dev -s dev'
          sh 'cf deploy mta_archives/*.mtar'
        }
      }
    }
  }
}
```

## Key Services

- **SAP Continuous Integration and Delivery** — Built-in CI/CD on BTP, no infrastructure needed
- **GitHub Actions / GitLab CI** — External CI, deploy via CF CLI
- **SAP Cloud Transport Management (CTMS)** — Transport across landscape nodes
- **SAP Automation Pilot** — Automated incident response and remediation

## Pitfalls

- **Pitfall: CF CLI token expires during long pipeline runs**
  - Cause: CF session tokens expire after ~12 hours; long deploys or queued jobs fail mid-run.
  - Solution: Use service keys or deploy keys for non-interactive auth. Re-auth before the deploy step if pipeline is long.

- **Pitfall: MTA deploy times out**
  - Cause: Default deploy timeout is 60 minutes; large MTARs with many modules can exceed this.
  - Solution: Run `cf deploy --timeout 120` to extend. Split large MTAs into smaller deployment units.

- **Pitfall: Production deploy without approval**
  - Cause: No manual confirmation gate configured for PRD stage.
  - Solution: In SAP CI/CD set `manualConfirmation: required`. In GitHub Actions use `environment: production` with required reviewers.

- **Pitfall: Secrets exposed in pipeline logs**
  - Cause: CF credentials printed in debug output or echo statements.
  - Solution: Store credentials in GitHub Secrets / Jenkins Credentials / CI/CD service credentials. Never `echo $CF_PASSWORD`. Mask output in CI settings.

- **Pitfall: Build cache hides dependency changes**
  - Cause: MTA build caches `node_modules`; stale cache breaks after package.json update.
  - Solution: Run `npm ci` (clean install) before `mbt build`. Clear cache: `rm -rf node_modules .mta_archives` on dependency changes.

- **Pitfall: Smoke test passes but app is unhealthy**
  - Cause: `/health` endpoint returns 200 even when dependent services are down.
  - Solution: Add deeper checks in smoke test — query an OData endpoint, verify DB connectivity, check service bindings.

## Verification

```bash
# 1. Verify pipeline config is valid
# SAP CI/CD: BTP Cockpit → CI/CD → Pipelines → Validate config
# GitHub Actions: push to PR branch → check Actions tab for green build

# 2. Build locally to catch errors before CI
mbt build
ls mta_archives/*.mtar  # MTAR should exist

# 3. Verify deployment
cf apps
cf env my-app-dev | grep VCAP_SERVICES  # Services bound

# 4. Run smoke test
curl -f https://my-app-dev.cfapps.us10.hana.ondemand.com/health
curl -f https://my-app-dev.cfapps.us10.hana.ondemand.com/odata/v4/Orders  # API works

# 5. Verify CTMS transport uploaded
# BTP Cockpit → Transport Management → dev-transport-node → New entry should appear
```
