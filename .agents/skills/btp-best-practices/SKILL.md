---
name: btp-best-practices
description: SAP BTP enterprise architecture best practices — runtime selection (CF vs Kyma), CAP project setup, MTA structure, XSUAA security, destination management, resilience patterns, CI/CD pipeline design, observability, cost optimization. Use when designing BTP solutions or implementing deployment pipelines.
trigger:
  - user designs a new BTP application or architecture
  - user chooses between Cloud Foundry and Kyma runtime
  - user sets up CAP project with MTA, XSUAA, or destinations
  - user implements resilience (circuit breaker, retry) or CI/CD on BTP
  - user needs BTP cost optimization or observability guidance
---

# SAP BTP Best Practices

## Prerequisites

- BTP Global Account with entitlements for: CF runtime, XSUAA, HANA (or HDI), Destination Service
- `cf` CLI with MultiApps plugin: `cf install-plugin multiapps`
- CAP CLI: `npm install -g @sap/cds-dk`
- MBT (MTA Build Tool): `npm install -g mbt`
- Git repository for source control

## 1. Choose Runtime: Cloud Foundry vs Kyma

- **Cloud Foundry** — Java/Node.js/Python/Go, native CAP support, simpler ops, auto-scaler
- **Kyma (K8s)** — any container, HPA scaling, Istio service mesh, higher complexity

**Rule:** Default to CF unless you need custom containers, sidecars, or K8s-native features.

## 2. Create a CAP Project with MTA

```bash
cds init my-project
cd my-project
cds add mta      # generates mta.yaml
cds add app      # adds UI (SAP Fiori elements)
cds add xs-security  # adds xs-security.json
cds add hana     # adds HANA persistence
```

## 3. Build and Deploy

```bash
mbt build
cf deploy mta_archives/my-project_1.0.0.mtar
```

## 4. MTA Structure

```yaml
_schema-version: "3.1"
ID: my-project
version: 1.0.0
modules:
  - name: my-project-srv
    type: nodejs
    path: gen/srv
    requires:
      - name: my-project-hdi
      - name: my-project-xsuaa
    parameters:
      memory: 512M
resources:
  - name: my-project-hdi
    type: com.sap.xs.hdi-container
  - name: my-project-xsuaa
    type: org.cloudfoundry.managed-service
    parameters:
      service: xsuaa
      service-plan: application
      config: xs-security.json
```

## 5. Configure XSUAA Security

```json
{
  "xsappname": "my-project",
  "tenant-mode": "dedicated",
  "scopes": [
    { "name": "$XSAPPNAME.User" },
    { "name": "$XSAPPNAME.Admin" }
  ],
  "role-templates": [
    { "name": "User", "scope-references": ["$XSAPPNAME.User"] },
    { "name": "Admin", "scope-references": ["$XSAPPNAME.User", "$XSAPPNAME.Admin"] }
  ]
}
```

## 6. Destination for On-Premise S/4HANA

```json
{
  "Name": "s4hana-backend",
  "Type": "HTTP",
  "URL": "https://s4hana.internal.corp:443",
  "ProxyType": "OnPremise",
  "Authentication": "PrincipalPropagation",
  "sap-client": "100"
}
```

Requires Cloud Connector installed and configured with trust to BTP subaccount.

## 7. Resilience Patterns

- **Circuit Breaker** — 50% failure threshold, 30s reset → unstable downstreams
- **Retry** — 3 attempts, exponential backoff (1s/2s/4s) → transient failures
- **Timeout** — 60s default, per-service configurable → long-running calls
- **Bulkhead** — max 10 concurrent requests → resource isolation

For CAP: `cds require @sap/cds-feature-resilience` (Node.js) or `resilience4j` (Java).

## 8. CI/CD Pipeline

```yaml
stages:
  - build:     mbt build
  - test:      cds test
  - lint:      eslint && cds lint
  - deploy-dev:  cf deploy mta_archives/*.mtar
  - smoke:     curl -sf https://dev.app.example.com/health
  - deploy-prd: manual approval gate
```

## 9. Observability

- **SAP Cloud Logging** — centralized logs (OpenSearch + Kibana dashboard)
- **SAP Alert Notification** — proactive alerts on service events
- **SAP Automation Pilot** — automated incident response runbooks
- **BTP Cockpit** — service health and metric dashboards

## 10. Cost Optimization

- Use `cf scale` to right-size memory (start 256M, increase on OOM)
- Enable auto-scaler to scale down during off-hours
- Use HANA Cloud with `data_volume_limit` sized to actual usage
- Review entitlements quarterly — remove unused service instances

## Pitfalls

**Deploy fails: "service instance not found"**
- Cause: MTA references a resource name that doesn't match an existing service instance
- Solution: Ensure resource `name` in mta.yaml matches `cf services` output exactly

**XSUAA token expires mid-session**
- Cause: Default token TTL is 12 hours; no refresh token configured
- Solution: Implement token refresh in app interceptor; or increase `oauth2-configuration.token-validity` in xs-security.json

**On-premise destination returns 403**
- Cause: Cloud Connector trust not established or Principal Propagation not configured
- Solution: Verify Cloud Connector → subaccount trust in BTP Cockpit; check principal propagation mapping in Cloud Connector

**App crashes with "memory exceeded"**
- Cause: CF hard memory limit — app OOM-killed if container exceeds allocation
- Solution: `cf scale my-app -m 1G` or optimize memory leaks; monitor via `cf app my-app`

**Service quota exceeded on deploy**
- Cause: Subaccount entitlements insufficient for requested service plan
- Solution: BTP Cockpit → Entitlements → increase quota for the service, or remove unused instances

**MTA ID mismatch causes XSUAA conflict**
- Cause: MTA `ID` differs from `xsappname` in xs-security.json
- Solution: Keep MTA `ID` and `xsappname` identical to avoid scope registration errors

## Verification

```bash
# Verify deployment
cf apps
cf services

# Health check
curl -sf https://<app-route>/health

# Verify XSUAA scopes
cf env my-project-srv | grep -A20 xsuaa

# Check destination connectivity
cf curl "/v3/service_instances/<destination-guid>/parameters"
```

Confirm:
- [ ] `cf deploy` completes with zero errors
- [ ] App health endpoint returns 200
- [ ] XSUAA scopes match role-templates in xs-security.json
- [ ] Destination service resolves on-premise backend via Cloud Connector
- [ ] No services in `cf services` show "create failed" status
