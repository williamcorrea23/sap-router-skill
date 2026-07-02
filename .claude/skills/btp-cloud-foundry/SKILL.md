---
name: btp-cloud-foundry
description: SAP BTP Cloud Foundry runtime — CF CLI operations, deployment, service lifecycle, troubleshooting, manifest authoring.
trigger:
  - cloud foundry
  - cf push
  - cf deploy
  - cf org
  - cf space
  - cf marketplace
  - cf logs
  - manifest.yml
  - buildpack
  - cf route
  - btp cf
  - cf create-service
  - cf bind-service
prerequisites:
  - CF CLI v8+ installed (https://github.com/cloudfoundry/cli/releases)
  - BTP subaccount with Cloud Foundry environment enabled
  - Org and space already created in BTP Cockpit
  - Network access to CF API endpoint
---

# BTP Cloud Foundry — Deploy, Manage, & Troubleshoot

## 1. Login and Target

```bash
# Login to BTP CF API (region-specific endpoint)
cf login -a https://api.cf.us10.hana.ondemand.com

# Target specific org and space
cf target -o my-org -s dev

# Verify current target
cf target
```

## 2. Deploy Application

```bash
# Standard push (uses manifest.yml if present)
cf push my-app

# Push with custom manifest
cf push my-app -f manifest-prod.yml

# Push with specific buildpack
cf push my-app -b nodejs_buildpack

# Push without starting (for binding services first)
cf push my-app --no-start
```

## 3. Author manifest.yml

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
  health-check-type: http
  health-check-http-endpoint: /health
```

## 4. Manage Services

```bash
# List marketplace services and plans
cf marketplace
cf marketplace -s xsuaa

# Create service instance
cf create-service xsuaa application my-xsuaa -c xs-security.json
cf create-service hana hdi-shared my-hdi-container
cf create-service destination lite my-destination

# Bind service to app
cf bind-service my-app my-xsuaa

# Create and view service keys
cf create-service-key my-xsuaa my-key
cf service-key my-xsuaa my-key

# List all services in space
cf services
```

## 5. Zero-Downtime Deploy (Blue-Green)

```bash
# Deploy new version with temporary route
cf push my-app-green

# Map production route to new version
cf map-route my-app-green cfapps.us10.hana.ondemand.com -n my-app

# Unmap route from old version
cf unmap-route my-app cfapps.us10.hana.ondemand.com -n my-app

# Stop and rename old version
cf stop my-app
cf rename my-app my-app-old
cf rename my-app-green my-app
```

## 6. Troubleshoot

```bash
cf logs my-app --recent    # recent logs
cf logs my-app             # stream live logs
cf app my-app              # app status and instances
cf events my-app           # crash/start/stop events
cf env my-app              # VCAP_SERVICES and env vars
cf enable-ssh my-app && cf ssh my-app   # SSH into container
cf restart my-app          # restart with same droplet
cf restage my-app          # rebuild droplet (needed after new bindings)
```

## 7. Deploy CAP App with mta.yaml

```bash
mbt build                              # build MTA archive
cf deploy mta_archives/my-cap-app_1.0.0.mtar   # deploy to CF
cf mta my-cap-app                      # verify deployment
```

## Verification

```bash
# Check app is running
cf app my-app
# Expected: #0 running, state=RUNNING

# Health check endpoint
curl -s https://my-app.cfapps.us10.hana.ondemand.com/health
# Expected: 200 OK

# Verify service bindings
cf env my-app | grep -A5 VCAP_SERVICES
# Expected: JSON with bound service credentials

# Check org quota usage
cf org-quota my-org
```

## Pitfalls

1. **App crashes immediately after push (401 on all endpoints)**
   - Cause: XSUAA service not bound before app start, or binding created after staging.
   - Solution: `cf push my-app --no-start` → `cf bind-service my-app my-xsuaa` → `cf start my-app`.

2. **Memory quota exceeded**
   - Cause: BTP CF trial accounts limited to 1GB total. Paid accounts have org-level quotas.
   - Solution: Check `cf org-quota my-org`. Reduce `memory` in manifest or stop unused apps.

3. **Route collision during blue-green deploy**
   - Cause: Both old and new apps mapped to same hostname simultaneously without unique temp name.
   - Solution: Use `-green` suffix for new version. Map route only after green is healthy.

4. **SSH fails with "not enabled"**
   - Cause: SSH disabled by default on BTP CF for security.
   - Solution: `cf enable-ssh my-app` then `cf restage my-app`. Disable in production.

5. **Restage needed after binding new service**
   - Cause: VCAP_SERVICES env vars are injected at staging time, not runtime.
   - Solution: After `cf bind-service`, run `cf restage my-app` to pick up new credentials.

6. **Buildpack version mismatch**
   - Cause: SAP buildpacks have version-specific Node.js/Java requirements. Unpinned buildpack auto-updates may break.
   - Solution: Pin buildpack version in manifest: `buildpack: nodejs_buildpack#1.8.0`.

7. **Service plan not available in region**
   - Cause: Some BTP service plans are region-specific (e.g. HANA not available in all regions).
   - Solution: Check `cf marketplace -s <service>` to verify plan availability before creating.
