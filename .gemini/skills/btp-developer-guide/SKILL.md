---
name: btp-developer-guide
description: SAP BTP Developer Guide — runtime selection, CAP/ABAP Cloud/SAP Build, integration patterns, CI/CD, monitoring
trigger:
  keywords: [btp developer, runtime selection, cap vs abap, btp architecture, cf vs kyma, build app on btp]
  intent: Designing and building applications on SAP BTP
prerequisites:
  - BTP cockpit access (global account + subaccount)
  - cf CLI logged in (`cf login -a api.cf.<region>.hana.ondemand.com`)
  - Node.js 20+ (for CAP) or ABAP Cloud dev environment
  - BAS or VS Code with CDS plugin (for CAP)
---

# SAP BTP Developer Guide

## 1. Choose Runtime

| Runtime | Best For | Languages |
|---|---|---|
| **Cloud Foundry** | CAP apps, microservices, stateless APIs | Node.js, Java, Python, Go |
| **Kyma** | Event-driven, custom Docker stacks | Any container |
| **ABAP Environment** | RAP Cloud extensions, Steampunk | ABAP (clean core) |
| **SAP Build** | Citizen dev, low-code process automation | LCNC |

## 2. CAP Quick Start

```bash
cds init my-project && cd cds-project
cds add mta && cds add app --ui5 && cds add sample
cds watch                    # http://localhost:4004
npx cds add xsuaa            # authentication
npx cds add hana             # production DB
mbt build                    # → mta_archives/*.mtar
cf deploy mta_archives/*.mtar
```

## 3. Integration Patterns

| Pattern | BTP Service | Protocol |
|---|---|---|
| REST/OData Proxy | API Management | HTTP |
| Async Events | Event Mesh | MQTT, CloudEvents |
| B2B/EDI | TPM | AS2, OFTP2 |
| File Transfer | CPI | SFTP |
| Scheduled Jobs | Job Scheduling | Cron-triggered REST |

## 4. CI/CD Pipeline

```yaml
# .pipeline/config.yml
stages:
  - Build: mbt build
  - Test: cds test --coverage
  - Lint: eslint src/ && abaplint --format json
  - Deploy DEV: cf deploy mta_archives/*.mtar -f
  - Deploy PRD: manual approval → cf deploy mta_archives/*.mtar
```

## 5. Monitoring

| Service | What It Monitors |
|---|---|
| Cloud Logging | Centralized logs via OpenSearch + Kibana dashboards |
| Alert Notification | Proactive alerts (email, webhook, Slack) |
| Automation Pilot | Automated incident response (remediation) |

## Pitfalls

- **No MTA wrapper** → Cause: deploying individual apps without MTA. Solution: always use `cds add mta` and deploy via `mbt build` → `cf deploy`.
- **Destinations not found** → Cause: destinations are subaccount-scoped. Solution: create destinations in the same subaccount as the consuming app; use `cf env APP_NAME` to verify binding.
- **CF memory crash** → Cause: app exceeds memory limit. Solution: check `cf app APP_NAME` for mem usage; scale with `cf scale APP_NAME -m 256M`.
- **Kyma vs CF confusion** → Cause: choosing runtime by familiarity. Solution: prefer CF for stateless CAP/API workloads; Kyma for event-heavy, polyglot, or stateful container stacks.
- **Missing xs-security.json** → Cause: app deployed without authentication. Solution: `cds add xsuaa` generates the security descriptor; customize scopes/roles in `xs-security.json`.

## Verification

```bash
cf apps                                    # list deployed apps
cf services                                # list service instances
cf logs APP_NAME --recent                  # recent logs
curl https://<app>.cfapps.<region>.hana.ondemand.com/health -s
```