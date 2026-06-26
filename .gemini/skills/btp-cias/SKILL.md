---
name: btp-cias
description: Cloud Integration Automation Service (CIAS) — automated integration setup, task catalog, landscape discovery, automated connectivity configuration, CIAS agent deployment. Use when automating SAP BTP connectivity setup, configuring integration landscapes, or running CIAS automated tasks for SAP-to-BTP integration.
---

# Cloud Integration Automation Service (CIAS)

Automates the integration setup between SAP on-premise systems and SAP BTP services. CIAS eliminates manual configuration steps for trust, connectivity, and destinations.

## What CIAS Automates

| Automation | Manual Equivalent |
|---|---|
| Trust configuration | STRUST certificate exchange + SICF setup |
| Cloud Connector setup | SCC installation + access control mapping |
| Destination configuration | BTP cockpit destination creation |
| Principal propagation | STRUST + BTP trust + user mapping |
| Integration monitoring alerts | Manual CC health checks |

## Architecture

```
CIAS Agent (on-premise, near Cloud Connector)
  ↓ HTTPS (outbound only, port 443)
CIAS Service (SAP BTP)
  ↓ REST API
CIAS Web UI (BTP Cockpit or standalone)
```

## CIAS Agent Installation

```bash
# Download from SAP Support Portal → Software Downloads
# Install on Cloud Connector host or dedicated VM
cias-agent --register \
  --tenant <subaccount-subdomain> \
  --user <btp-email> \
  --region us10
```

## Task Catalog

| Task ID | Description | Time |
|---|---|---|
| CONFIG_TRUST_ONPREME | Establish trust between BTP and ABAP system | ~5 min |
| CONFIG_CC | Install and configure Cloud Connector | ~10 min |
| CONFIG_DEST_BASIC | Create HTTP destination to ABAP backend | ~2 min |
| CONFIG_DEST_MAIL | Configure mail destination | ~1 min |
| CONFIG_DEST_RFC | Configure RFC destination | ~3 min |
| CONFIG_SSO_CERT | Exchange SSO certificates | ~2 min |
| CONFIG_PRINCIPAL_PROP | Set up principal propagation | ~5 min |

## Execution

```bash
# Run single task
cias-agent execute --task CONFIG_TRUST_ONPREME \
  --params '{"abap_system": "S4H", "client": "100"}'

# Run task chain (sequentially)
cias-agent execute-chain \
  --tasks CONFIG_TRUST_ONPREME,CONFIG_CC,CONFIG_DEST_BASIC \
  --auto-approve
```

## CIAS Web UI

1. Navigate to BTP Cockpit → Integration Automation
2. Select landscape template (SAP S/4HANA + BTP)
3. Review task list → Execute → Monitor progress
4. Download execution report for audit

## ZROUTER Integration

ZROUTER_DISPATCH BASIS handler can trigger CIAS automation tasks via BTP REST APIs for zero-touch landscape setup:

```python
# sap_router.py routes CIAS automation tasks
python scripts/sap_router.py route --action BASIS_CIAS_CONFIG_TRUST
# → "ZROUTER RFC" (dispatches to BASIS handler)
```

## Gotchas

- CIAS agent only needs outbound HTTPS (port 443) — no inbound firewall rules needed
- Agent must be on same network as Cloud Connector (or have internal network access)
- One CIAS agent per BTP subaccount
- Tasks are idempotent — re-running checks current state, only applies changes if needed
- Full automation depends on ABAP system having ADT services active
