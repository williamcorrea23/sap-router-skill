---
name: btp-cloud-foundry
description: >-
  SAP BTP Cloud Foundry runtime — CF CLI operations, org/space management,
  cf push/deploy, service marketplace, service instance/binding lifecycle,
  CF logs and troubleshooting, manifest.yml authoring, CF auto-scaling,
  route management, buildpack selection, CF security (XSUAA, CF UAA).
  Use when deploying apps to Cloud Foundry, managing CF orgs/spaces,
  troubleshooting CF deployments, or configuring CF services on BTP.
  Triggers on: "Cloud Foundry", "cf push", "cf deploy", "CF org", "CF space",
  "cf marketplace", "cf logs", "manifest.yml", "buildpack", "CF route",
  "BTP CF", "BTP Cloud Foundry", "cf create-service".
---

# BTP Cloud Foundry — CF CLI, Deploy, & Lifecycle

Full Cloud Foundry runtime management on SAP BTP.

## Architecture

```
cf CLI / MCP
    │
    ▼
┌──────────────────────────────────────────┐
│  Cloud Foundry Runtime (BTP)             │
│                                           │
│  Org: my-org                              │
│    Space: dev    Space: qa   Space: prd  │
│      │              │            │        │
│      ▼              ▼            ▼        │
│  ┌───────┐    ┌───────┐   ┌───────┐     │
│  │ App   │    │ App   │   │ App   │     │
│  │ CAP   │    │ CAP   │   │ CAP   │     │
│  │ +XSUAA│    │ +XSUAA│   │ +XSUAA│     │
│  └───────┘    └───────┘   └───────┘     │
└──────────────────────────────────────────┘
```

## CF CLI Quick Reference

### Authentication & Targeting

```bash
# Login to BTP CF API endpoint
cf login -a https://api.cf.us10.hana.ondemand.com

# Target specific org and space
cf target -o my-org -s dev

# List available orgs and spaces
cf orgs
cf spaces

# Check current target
cf target
```

### Application Deployment

```bash
# Standard push
cf push my-app

# Push with custom manifest
cf push my-app -f manifest.yml

# Push with specific buildpack
cf push my-app -b nodejs_buildpack

# Push without starting
cf push my-app --no-start

# Zero-downtime deploy (blue-green)
cf push my-app-green
cf map-route my-app-green cfapps.us10.hana.ondemand.com -n my-app
cf unmap-route my-app cfapps.us10.hana.ondemand.com -n my-app
cf stop my-app
cf rename my-app my-app-old
cf rename my-app-green my-app
```

### manifest.yml

```yaml
---
applications:
- name: my-cap-app
  buildpack: nodejs_buildpack
  memory: 256M
  disk_quota: 512M
  instances: 2
  routes:
  - route: my-cap-app.cfapps.us10.hana.ondemand.com
  services:
  - my-xsuaa
  - my-destination
  - my-hdi-container
  env:
    NODE_ENV: production
    CDS_ENVIRONMENT: production
    SAP_JWT_TRUST_ACL: '[{"clientid":"*","identityzone":"*"}]'
  health-check-type: http
  health-check-http-endpoint: /health
```

### Service Management

```bash
# List marketplace services
cf marketplace

# List services in current space
cf services

# Create service instance
cf create-service xsuaa application my-xsuaa -c xs-security.json

# Create HDI container
cf create-service hana hdi-shared my-hdi-container

# Bind service to app
cf bind-service my-app my-xsuaa

# Unbind and rebind
cf unbind-service my-app my-xsuaa
cf bind-service my-app my-xsuaa

# Service keys
cf create-service-key my-service my-key
cf service-key my-service my-key
```

### Troubleshooting

```bash
# App logs (recent)
cf logs my-app --recent

# Stream logs
cf logs my-app

# App status and events
cf app my-app
cf events my-app

# SSH into container (if enabled)
cf ssh my-app

# Check environment variables
cf env my-app

# Restart / restage
cf restart my-app
cf restage my-app

# Check CF events at org-level
cf events
```

## Integration with SAP Router

```python
# sap_router.py routing entry for CF operations
CF_ACTIONS = {
    'cf_deploy': {
        'destination': 'CF CLI',
        'command': 'cf push',
        'description': 'Deploy app to Cloud Foundry',
    },
    'cf_service': {
        'destination': 'CF CLI',
        'command': 'cf create-service / cf bind-service',
        'description': 'Manage CF services',
    },
    'cf_logs': {
        'destination': 'CF CLI',
        'command': 'cf logs --recent',
        'description': 'Troubleshoot CF app',
    },
}
```

## mta.yaml Integration (CAP on CF)

```yaml
_schema-version: "3.1"
ID: my-cap-app
version: 1.0.0
description: "CAP Application deployed to CF"

modules:
- name: my-cap-app-srv
  type: nodejs
  path: gen/srv
  requires:
  - name: my-cap-app-db
  - name: my-cap-app-xsuaa
  - name: my-cap-app-destination
  provides:
  - name: srv-api
    properties:
      srv-url: ${default-url}

- name: my-cap-app-db-deployer
  type: hdb
  path: gen/db
  requires:
  - name: my-cap-app-db

- name: my-cap-app-approuter
  type: approuter.nodejs
  path: app/router
  requires:
  - name: my-cap-app-xsuaa
  - name: srv-api
    group: destinations
    properties:
      forwardAuthToken: true
      name: srv-api
      url: ~{srv-url}

resources:
- name: my-cap-app-db
  type: com.sap.xs.hdi-container

- name: my-cap-app-xsuaa
  type: org.cloudfoundry.managed-service
  parameters:
    service: xsuaa
    service-plan: application

- name: my-cap-app-destination
  type: org.cloudfoundry.managed-service
  parameters:
    service: destination
    service-plan: lite
```

## Gotchas

- **CF memory quota**: Default BTP CF org has limited memory. Check `cf org-users` and quotas.
- **Buildpack order**: SAP buildpacks have specific version requirements. Pin `buildpack` in manifest.
- **XSUAA binding**: Must happen before app start. Missing binding → 401 on all endpoints.
- **AppRouter with destinations**: The `forwardAuthToken: true` setting must match XSUAA config.
- **CF marketplace on BTP**: Some plans are region-specific. Verify `cf marketplace -s <service>`.
- **Instance limits**: CF trial accounts limited to 1GB memory, 2 instances.
- **Route collision**: Blue-green deploy must use unique temporary hostnames to avoid route conflicts.
- **SSH disabled by default**: `cf enable-ssh my-app` needed before `cf ssh`. Production apps often disable SSH.
