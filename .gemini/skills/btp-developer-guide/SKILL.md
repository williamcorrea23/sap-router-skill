---
name: btp-developer-guide
description: SAP BTP Developer Guide — development reference covering CAP, ABAP Cloud, SAP Build, integration patterns, API Management, Event Mesh, HANA Cloud, CI/CD pipelines, and monitoring. Use as general reference when building BTP applications, choosing services, or designing BTP architectures.
---

# SAP BTP Developer Guide

Comprehensive reference for SAP BTP application development.

## Development Runtimes

| Runtime | Languages | Best For |
|---|---|---|
| Cloud Foundry | Node.js, Java, Python, Go, PHP, .NET | CAP apps, microservices |
| Kyma (Kubernetes) | Any container | Event-driven, custom stacks |
| ABAP Environment | ABAP (cloud-compliant) | ABAP extensions, RAP |
| SAP Build | Low-code/no-code | Citizen developer apps |

## CAP Development Flow

```bash
cds init my-project && cds add mta && cds add app && cds add sample
cds watch              # local dev
mbt build              # build .mtar
cf deploy mta_archives/*.mtar  # deploy to BTP
```

## Integration Patterns

| Pattern | BTP Service | Protocol |
|---|---|---|
| API Proxy | API Management | HTTP/REST, OData |
| Async Messaging | Event Mesh | MQTT, AMQP, CloudEvents |
| B2B/EDI | Trading Partner Management | AS2, OFTP2 |
| File Transfer | Cloud Integration (CPI) | SFTP, (S)FTP |
| Scheduled Jobs | Job Scheduling | REST endpoints via cron |

## CI/CD Pipeline

```yaml
stages:
  - Build: mbt build
  - Test: cds test
  - Lint: eslint && abaplint
  - Deploy DEV: cf deploy *.mtar
  - Deploy PRD: manual approval gate
```

## Monitoring

| Service | Purpose |
|---|---|
| Cloud Logging | Centralized logs (OpenSearch + Kibana) |
| Alert Notification | Proactive alerts |
| Automation Pilot | Automated incident response |

## Gotchas
- Always use MTA for multi-service deployments
- Destinations are subaccount-scoped, not global
- CF memory hard limit — app crashes if exceeded
