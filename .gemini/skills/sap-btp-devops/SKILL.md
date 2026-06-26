---
name: sap-btp-devops
description: SAP BTP DevOps — Continuous Integration and Delivery (CI/CD) service on BTP, CI/CD pipeline configuration, MTA build automation, automated testing (CDS tests, UI tests), transport integration (CTMS), GitHub Actions for BTP, SAP Continuous Integration and Delivery service, Jenkins for BTP. Use when setting up CI/CD for BTP, configuring automated deployment pipelines, integrating tests in BTP CI, or connecting GitHub to BTP deployments.
---

# SAP BTP DevOps

CI/CD on SAP BTP — automated build, test, and deployment pipelines for CAP and Fiori apps.

## SAP Continuous Integration and Delivery Service

```
Git Repository (GitHub / GitLab / Bitbucket)
  → Webhook trigger
    → CI/CD Service (SAP BTP)
      → Build (mbt build / npm build)
        → Test (cds test / unit tests)
          → Lint (eslint / abaplint)
            → Deploy (cf deploy / ctms transport)
              → Success/Fail notification
```

## Pipeline Configuration

```yaml
# .pipeline/config.yml
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
      # Requires human approval before deploying
```

## GitHub Actions for BTP

```yaml
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

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with: { node-version: '20' }

      - name: Install dependencies
        run: npm ci

      - name: Build MTA
        run: |
          npm install -g mbt
          mbt build

      - name: Run tests
        run: npm test

      - name: Deploy to DEV
        run: |
          cf login -a ${{ secrets.CF_API }} -u ${{ secrets.CF_USER }} -p ${{ secrets.CF_PASSWORD }} -o my-org -s dev
          cf deploy mta_archives/*.mtar

      - name: Smoke test
        run: curl -f https://my-app-dev.cfapps.us10.hana.ondemand.com/health

  deploy-prd:
    needs: build-and-deploy
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval
    steps:
      - name: Deploy to PRD
        run: |
          cf login -a ${{ secrets.CF_API }} -u ${{ secrets.CF_USER }} -p ${{ secrets.CF_PASSWORD }} -o my-org -s prd
          cf deploy mta_archives/*.mtar
```

## Transport Integration (CTMS)

```yaml
stages:
  Build: { ... }
  Test:  { ... }
  Transport:
    uploadToTransportManagement:
      transportManagementServiceCredentialsId: ctms-credentials
      nodeName: dev-transport-node
```

## Jenkins Pipeline for BTP

```groovy
pipeline {
  agent any
  environment {
    CF_HOME = tool 'cf-cli'
  }
  stages {
    stage('Build') {
      steps { sh 'mbt build' }
    }
    stage('Test') {
      steps { sh 'npm test' }
    }
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

| Service | Purpose |
|---|---|
| SAP Continuous Integration and Delivery | Built-in CI/CD on BTP |
| GitHub Actions / GitLab CI | External CI, deploy via CF CLI |
| SAP Cloud Transport Management | Transport across landscape nodes |
| SAP Automation Pilot | Automated incident response |

## Gotchas

- **CF CLI auth**: token expires in 12h — use service keys for long-running pipelines
- **MTA deploy timeout**: 60 min default, increase for large deployments
- **PRD deploy needs manual confirmation**: configure environment protection rules
- **GitHub Actions secrets**: store SAP credentials in GH secrets, never in YAML
- **Build cache**: MTA build caches node_modules; clean build on dependency changes
