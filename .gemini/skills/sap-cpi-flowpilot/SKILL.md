---
name: sap-cpi-flowpilot
description: >-
  Autonomous SAP Cloud Integration (CPI) co-pilot and lifecycle engine. Use when triaging
  CPI message failures (MPL), packaging or testing iFlow bundles with FlowMate toolkit,
  managing multi-tenant CPI landscapes, validating Groovy/XSLT mappings, or orchestrating
  automated iflow deployment and rollback with fail-closed approval governance.
trigger:
  - cpi copilot
  - flowpilot
  - flowmate
  - cpi triage
  - mpl error analysis
  - cpi multi-tenant
  - iflow testing
  - cpi devops
---

# SAP CPI FlowPilot Autonomous Engine

Orchestration, automated diagnostics, and testing toolkit for SAP Cloud Integration (CPI / SAP Integration Suite).

## Core Capabilities

1. **Intelligent MPL Triage**: Diagnoses Message Processing Logs, extracts error steps, correlates stack traces with Groovy/XSLT exceptions.
2. **FlowMate & DevOps Toolkit**: Automated packaging, linting (CPILint), local XML/Groovy simulation, and contract validation.
3. **Multi-Tenant Routing**: Coordinates artifact replication and configuration across DEV, TEST, and PROD CPI subaccounts.
4. **Governed Lifecycle**: Enforces plan-then-commit workflows for artifact deployments and undeployments via `approval_broker.py`.

## Tool Routing Hierarchy

- **Primary API / Tooling**: `sap-cpi-mcp` (`sap.cpi.artifact.*`, `sap.cpi.message.*`, `sap.cpi.bundle.package`)
- **Web UI Fallback**: `integration-suite-ui-mcp` (Playwright bridge via user session when OAuth API access is blocked)
- **Multi-Tenant Gateway**: `sap.cpi.multitenant.manage`

## Workflow: Incident Triage & Self-Healing

```
[Failed Message MPL] 
       │
       ▼
1. Query Message Log (sap.cpi.message.read)
       │
       ▼
2. Fetch Trace / Attachment (sap.cpi.trace.read)
       │
       ▼
3. Classify Root Cause (Groovy error / Mapping failure / Receiver Timeout / Auth error)
       │
       ▼
4. Generate Fix Plan (Patch Groovy script / Adjust Content Modifier / Re-trigger payload)
       │
       ▼
5. Propose & Commit (approval_broker.py plan -> commit)
```

## CLI Operations

```bash
# Triage failed messages in CPI
python scripts/sap_harness.py run --agent cpi --task "triage failed messages in CPI tenant"

# Validate and package iFlow using local toolkit
python scripts/cpi_iflow_packager.py validate --input src/my-iflow.zip
```
