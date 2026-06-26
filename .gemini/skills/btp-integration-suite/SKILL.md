---
name: btp-integration-suite
description: SAP Integration Suite — Cloud Integration (CPI iFlows), API Management, Open Connectors, Trading Partner Management, Integration Advisor, Event Mesh, PI/PO migration. Use when designing CPI iFlows, managing API proxies, configuring trading partners, or migrating from SAP PI/PO.
---

# SAP Integration Suite

Comprehensive integration platform on SAP BTP.

## Capabilities Overview

| Capability | Use Case | MCP Server |
|---|---|---|
| Cloud Integration | iFlows, mappings, message monitoring | sap-cpi, odata-mcp-proxy |
| API Management | API proxy, rate limiting, analytics | btp-mcp |
| Trading Partner Management | B2B/EDI document exchange | — |
| Open Connectors | 170+ 3rd-party API connectors | — |
| Integration Advisor | ML-based B2B message mapping | — |
| Event Mesh | Async messaging | — |

## Cloud Integration (CPI)

### iFlow Structure
```
Sender (HTTP/SOAP/IDoc/FTP) → Integration Process → Receiver (RFC/OData/SOAP)
                              ├── Content Modifier
                              ├── Message Mapping (XSLT)
                              ├── Groovy Script
                              ├── Router (condition-based)
                              └── Exception Subprocess
```

### Deploy via MCP
```bash
# sap-cpi MCP
sap_cpi_list_packages()
sap_cpi_get_artifact(artifactId="my_iflow", artifactType="IntegrationFlow")
sap_cpi_deploy_artifact(artifactId="my_iflow")
sap_cpi_get_failed_messages(top=20, artifactName="my_iflow")
```

## API Management

```
API Consumer → API Proxy (API Management)
  → Rate limiting, auth (OAuth2/API Key), analytics
    → Backend (SAP S/4HANA OData)
```

## PI/PO Migration Path

| PI Technology | Integration Suite Alternative |
|---|---|
| Adapter Engine | CPI Adapters (SFTP, SOAP, IDoc, etc.) |
| ESR mappings | CPI Message Mapping + Integration Advisor |
| ccBPM processes | CPI Integration Processes |
| SXMB_MONI | CPI Message Processing Logs |

## Gotchas
- CPI iFlow design-time limit: ~10MB per iFlow
- Message size max: 100MB per CPI message
- Groovy: Nashorn engine (ECMAScript 5.1 dialect)
- PI/PO: plan migration timeline — SAP PI 7.5 support ends 2027
