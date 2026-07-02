---
name: btp-integration-suite
description: >-
  SAP Integration Suite — Cloud Integration (CPI iFlows), API Management, Open Connectors,
  Trading Partner Management, Integration Advisor, Event Mesh, PI/PO migration. Use when
  designing CPI iFlows, managing API proxies, configuring trading partners, migrating from
  SAP PI/PO, or selecting integration capabilities on BTP.
trigger:
  - Integration Suite
  - BTP integration
  - API Management
  - API proxy
  - rate limiting
  - Open Connectors
  - Trading Partner Management
  - Integration Advisor
  - Event Mesh
  - PI/PO migration
  - cloud integration
  - integration advisor
  - edge integration cell
  - BTP capabilities
---

# SAP Integration Suite

Comprehensive integration platform on SAP BTP. Provides Cloud Integration, API Management, Event Mesh, Trading Partner Management, Open Connectors, and Integration Advisor in a single suite.

## Prerequisites

- SAP BTP subaccount with Integration Suite entitlement
- Service Key for Integration Suite (OAuth2 client_credentials)
- Cloud Connector if accessing on-premise systems
- For PI/PO migration: SAP PI 7.5+ system with export access

## Capabilities Overview

- **Cloud Integration (CPI)** — Message routing, transformation, iFlow design. Artifacts: Integration Flow (iFlow). MCP access via `cpi_mcp`.
- **API Management** — API proxy lifecycle, rate limiting, analytics, auth (OAuth2/API Key). Artifacts: API Proxy.
- **Event Mesh** — Event-driven architecture with topics, queues, and subscriptions. Enables async decoupled communication.
- **Trading Partner Management** — B2B/EDI partner onboarding, agreements, document routing. Artifacts: Partner Agreements.
- **Integration Advisor** — ML-assisted B2B message mapping using MIG (Mapping Guidelines) and MAG (Mapping Artifacts).
- **Open Connectors** — 170+ pre-built connectors for non-SAP SaaS APIs (Salesforce, ServiceNow, etc.).
- **Edge Integration Cell** — Hybrid deployment option running CPI runtime on customer Kubernetes cluster.

## Step 1 — Enable Integration Suite

```bash
# Via BTP CLI
btp create services instance integration-suite standard my-integration-suite \
  --subaccount <subaccount-id> \
  --plan standard

# Create service key
btp create services binding my-integration-suite my-key \
  --subaccount <subaccount-id>
```

Or via BTP Cockpit → Subaccount → Services → Instances → Create.

## Step 2 — Configure Cloud Integration (CPI)

Design iFlows following the standard pattern:

```
Sender (HTTPS/SFTP/IDoc) → Content Modifier → Groovy Script → Request-Reply → Receiver
```

Deploy and monitor via MCP:

```bash
# List deployed iFlows
cpi_mcp --tool list_integration_flows

# Deploy new iFlow
cpi_mcp --tool deploy_artifact --params '{"artifactId":"my_iflow","artifactType":"IntegrationFlow"}'

# Check failed messages
cpi_mcp --tool get_runtime_stats --params '{"range":"24h"}'
```

## Step 3 — Set Up API Management

Create API proxy to expose backend with governance:

```
API Consumer → API Proxy (rate limit, auth, analytics) → Backend (S/4HANA OData)
```

1. Integration Suite → API Management → APIs → Create API
2. Define backend endpoint (e.g., S/4HANA OData service URL)
3. Add policies: authentication (OAuth2/API Key), rate limiting, quota
4. Deploy proxy and test via API endpoint

## Step 4 — Configure Trading Partner Management

1. Integration Suite → Trading Partner Management → Partners → Create
2. Define partner profile with EDI identifier (e.g., DUNS, GLN)
3. Create agreement: select sender, receiver, and message type (e.g., ORDERS, INVOIC)
4. Configure EDI separator and envelope settings
5. Deploy agreement and test with sample EDI payload

## Step 5 — Migrate from SAP PI/PO

| PI/PO Component | Integration Suite Replacement |
|---|---|
| Adapter Engine | CPI Adapters (SFTP, SOAP, IDoc, OData, etc.) |
| ESR mappings | CPI Message Mapping + Integration Advisor |
| ccBPM processes | CPI Integration Processes (BPMN 2.0) |
| SXMB_MONI | CPI Message Processing Logs (Web UI) |
| Integration Repository | CPI Web UI → Design → Integration Flows |

Migration approach:
1. Export PI/PO objects (ESR + ID directory) using `SAP PI Migration Tool`
2. Map each communication channel to CPI adapter
3. Rebuild mappings using CPI Message Mapping or XSLT
4. Replace ccBPM with CPI integration processes
5. Test end-to-end before cutover

## Step 6 — Use Open Connectors for Non-SAP APIs

```bash
# Example: Query Salesforce via Open Connector
# Configure in Integration Suite → Open Connectors → Instances
# Get connector instance token and use in iFlow Request-Reply step
```

Supported connectors: Salesforce, ServiceNow, Workday, SharePoint, Box, Slack, and 170+ more.

## PI/PO Migration Timeline

- SAP PI 7.5 support ends **2027** — plan migration before end-of-support
- SAP PO 7.5 support ends **2027** (mainstream) / **2030** (extended)
- Assessment: 2-4 weeks; migration: 3-12 months depending on complexity

## Integration Patterns

- **A2A (Application-to-Application)**: S/4HANA ↔ SuccessFactors via CPI iFlow with OData adapters
- **B2B (Business-to-Business)**: EDI X12/EDIFACT via Trading Partner Management + AS2 adapter
- **B2G (Business-to-Government)**: Government API integration with certificate-based auth
- **Event-driven**: S/4HANA business events → Event Mesh → multiple subscribers
- **Hybrid**: Cloud CPI → Cloud Connector → on-premise SAP (RFC/IDoc)

## Pitfalls

- **iFlow design-time size limit ~10MB** — Cause: Large scripts/schemas bloat the iFlow. Solution: Move complex logic to external scripts referenced by path; split into multiple iFlows.
- **Message size exceeds 100MB** — Cause: Batch payloads too large. Solution: Use Splitter to break into smaller messages; process in chunks.
- **Groovy uses Nashorn (ECMAScript 5.1)** — Cause: Modern JS features (let, arrow functions, promises) not supported. Solution: Use Groovy-native syntax; avoid ES6+ patterns.
- **PI/PO migration underestimates effort** — Cause: ccBPM logic and ESR mappings don't auto-convert. Solution: Budget 3-12 months; manually rebuild complex mappings; test each interface.
- **Open Connector auth confusion** — Cause: Each connector instance has its own token, not BTP OAuth. Solution: Get connector-specific token from Open Connectors UI; pass in iFlow Authorization header.
- **Event Mesh message loss** — Cause: Queue not set to persistent or subscriber offline. Solution: Configure dead-letter queue; set queue accessType to EXCLUSIVE with retry.
- **Integration Suite vs classic CPI URL mismatch** — Cause: Integration Suite uses `integrationsuite.cfapps.*`; classic CPI uses `it-cpi.cfapps.*`. Solution: Use the URL from your Service Key JSON.

## Verification

1. **Integration Suite enabled**: BTP Cockpit → Services → Instances shows Integration Suite in "Started" state
2. **CPI accessible**: `cpi_mcp --tool list_integration_flows` returns flow list without error
3. **API proxy works**: Send request to proxy endpoint, verify rate limiting and auth policies fire
4. **Trading partner agreement active**: Send test EDI message, verify it routes to correct receiver
5. **Migration completeness**: All PI/PO interfaces have CPI equivalent deployed and tested end-to-end
6. **Open Connector reachable**: Test connector instance returns data from target SaaS API
7. **Event Mesh delivers**: Publish test event to topic, verify subscriber queue receives message
