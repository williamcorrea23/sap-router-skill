---
name: btp-best-practices
description: SAP BTP development best practices — Cloud Foundry vs Kyma, multi-tenancy, CAP on BTP, destination management, XSUAA security, resilience patterns (circuit breaker, retry), observability, cost optimization, CI/CD pipeline design. Use when designing BTP solutions, choosing BTP services, or implementing BTP deployment pipelines.
---

# SAP BTP Best Practices

## Runtime Selection

| Criterion | Cloud Foundry | Kyma (K8s) |
|---|---|---|
| Language support | Java, Node.js, Python, Go, PHP | Any container |
| Scaling | App auto-scaler | Kubernetes HPA |
| CAP support | Native | Containerized |
| Complexity | Lower | Higher (K8s knowledge needed) |

## CAP on BTP

```bash
cds init my-project && cds add mta && cds add app && cds add sample
mbt build
cf deploy mta_archives/my-app.mtar
```

## MTA Structure

```yaml
_schema-version: "3.1"
ID: my-app
version: 1.0.0
modules:
  - name: my-app-srv
    type: nodejs
    path: gen/srv
    requires:
      - name: my-app-hdi
      - name: my-app-xsuaa
    parameters:
      memory: 512M
resources:
  - name: my-app-hdi
    type: com.sap.xs.hdi-container
  - name: my-app-xsuaa
    type: org.cloudfoundry.managed-service
    parameters:
      service: xsuaa
      service-plan: application
```

## XSUAA Security

```json
{
  "xsappname": "my-app",
  "tenant-mode": "dedicated",
  "scopes": [
    { "name": "$XSAPPNAME.User" },
    { "name": "$XSAPPNAME.Admin" }
  ],
  "role-templates": [
    { "name": "User", "scope-references": ["$XSAPPNAME.User"] },
    { "name": "Admin", "scope-references": ["$XSAPPNAME.User","$XSAPPNAME.Admin"] }
  ]
}
```

## Destination Configuration

Example destination for on-premise SAP S/4HANA via Cloud Connector:

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

## Resilience Patterns

| Pattern | Config | When |
|---|---|---|
| Circuit Breaker | 50% threshold, 30s reset | Unstable downstream |
| Retry | 3x, exponential backoff (1s/2s/4s) | Transient failures |
| Timeout | 60s default, configurable | Long-running calls |
| Bulkhead | Max 10 concurrent | Resource isolation |

## CI/CD Pipeline

```yaml
stages:
  - Build: mbt build
  - Test: cds test
  - Lint: eslint
  - Deploy DEV: cf deploy *.mtar
  - Smoke: curl health endpoint
  - Deploy PRD: manual approval gate
```

## Monitoring

| Service | Purpose |
|---|---|
| SAP Cloud Logging | Centralized logs (OpenSearch + Kibana) |
| SAP Alert Notification | Proactive alerts |
| SAP Automation Pilot | Automated incident response |
| BTP Cockpit | Service health dashboard |

## Gotchas

- MTA ID must match xsappname in xs-security.json
- XSUAA token TTL: 12h default — plan for refresh logic
- On-premise destinations need Cloud Connector + trust config
- CF memory hard limit — app instance crashes if exceeded
- Service instance quotas: check subaccount entitlements before deploy
