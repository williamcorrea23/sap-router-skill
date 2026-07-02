---
name: btp-cias
description: BTP Cloud Integration Automation Service (CIAS) — automated setup of on-premise-to-BTP integration
trigger:
  keywords: [cias, cloud integration automation, automated landscape setup, trust configuration automation]
  intent: Automating SAP on-premise → BTP connectivity setup
prerequisites:
  - BTP subaccount with CIAS entitlement (enable via cockpit)
  - ABAP system (S/4HANA, ECC) with ADT services active
  - Cloud Connector target setup (or VM for CIAS agent)
  - SAP Support Portal access for CIAS agent download
  - On-premise user with STRUST + SICF + SM30 authorization
---

# Cloud Integration Automation Service (CIAS)

Automates trust, Cloud Connector, destination, and principal propagation setup between on-premise SAP and BTP.

## Quick Start

```bash
# 1. Enable CIAS in BTP Cockpit → Services → Integration Automation
# 2. Download CIAS agent from SAP Support Portal
# 3. Install agent on Cloud Connector host:
cias-agent --register \
  --tenant <subaccount-subdomain> \
  --user <btp-email> \
  --region us10

# 4. Run task chain (auto-approve):
cias-agent execute-chain \
  --tasks CONFIG_TRUST_ONPREME,CONFIG_CC,CONFIG_DEST_BASIC \
  --auto-approve

# 5. Verify trust:
curl -s -o /dev/null -w "%{http_code}" \
  "https://<system>.abap.cloud.sap/sap/bc/adt/cts"
# Expect: 200
```

## Task Catalog

| Task ID | What It Does | ~Time |
|---|---|---|
| `CONFIG_TRUST_ONPREME` | STRUST certificate exchange + SICF | 5 min |
| `CONFIG_CC` | Cloud Connector install + access control | 10 min |
| `CONFIG_DEST_BASIC` | HTTP destination to ABAP backend | 2 min |
| `CONFIG_DEST_MAIL` | Mail destination | 1 min |
| `CONFIG_DEST_RFC` | RFC destination (for RFC_READ_TABLE, BAPI) | 3 min |
| `CONFIG_SSO_CERT` | SSO certificate exchange | 2 min |
| `CONFIG_PRINCIPAL_PROP` | Principal propagation setup | 5 min |

## Web UI Alternative

BTP Cockpit → Integration Automation → Select landscape template (e.g. S/4HANA + BTP) → Execute → Monitor → Download audit report.

## ZROUTER Integration

```bash
# Via sap-router-skill dispatcher:
python scripts/sap_router.py route --action BASIS_CIAS_CONFIG_TRUST
```

## Pitfalls

- **CIAS agent blocked by firewall** → Cause: inbound rules not defined. Solution: agent needs OUTBOUND-only HTTPS (443); no inbound required.
- **ABAP ADT unavailable** → Cause: `/sap/bc/adt` not active. Solution: activate SICF service `/sap/bc/adt` and ensure `SAP_BC_ADT_ROLE` is assigned.
- **Task returns "already configured"** → Cause: CIAS tasks are idempotent. Solution: re-run safely — CIAS checks current state before applying changes.
- **Agent can't reach BTP** → Cause: outbound proxy or DNS issue. Solution: configure `HTTP_PROXY` env var on agent VM, test with `curl https://cias.cfapps.<region>.hana.ondemand.com`.
- **One CIAS agent per subaccount** → Cause: multiple agents conflict. Solution: register one agent per subaccount; for multi-region, use separate agents.

## Verification

```bash
# Check agent status
cias-agent status

# List completed tasks
cias-agent list-executions --status completed

# Test destination from BTP cockpit
# Cockpit → Connectivity → Destinations → Check Connectivity (HTTP 200)
```