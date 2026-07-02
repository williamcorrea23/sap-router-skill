---
name: btp-cloud-transport-management
description: SAP Cloud Transport Management (CTM) — transport landscape nodes, content export/import between BTP subaccounts, import queue management, gCTS for ABAP Cloud, Content Agent automation. Use when configuring cloud transports or troubleshooting CTM import failures.
trigger:
  - user needs to move content between BTP subaccounts or environments
  - user configures transport nodes or import queues in CTM
  - user troubleshoots failed CTM imports or stuck queues
  - user sets up gCTS for ABAP Cloud or Content Agent for automated exports
---

# SAP BTP Cloud Transport Management (CTM)

## Prerequisites

- BTP Global Account with entitlement for **Transport Management Service** (plan: `standard`)
- At least two subaccounts configured (e.g., DEV → TST → PRD)
- For on-premise CTS+: SAP Solution Manager 7.2 FP03+ or CTS+ with WebDisp
- For gCTS: ABAP Cloud environment (Steampunk / Embedded Steampunk) with Git access
- `cf` CLI logged in to target subaccounts

## 1. Enable CTM Service

```bash
# Create service instance in source subaccount (DEV)
cf create-service cts standard ctm-dev

# Create in target subaccount (TST)
cf create-service cts standard ctm-tst
```

## 2. Configure Transport Landscape

```
DEV Subaccount ──export──▶ CTM Node (DEV)
                              │
                         import queue
                              │
                           ▼
TST Subaccount ◀──import── CTM Node (TST)
                              │
                         import queue
                              │
                           ▼
PRD Subaccount ◀──import── CTM Node (PRD)
```

Via BTP Cockpit → **Transport Management** → **Landscape**:
1. Add DEV node (type: Content Source)
2. Add TST node (type: Content Target, parent: DEV)
3. Add PRD node (type: Content Target, parent: TST)

## 3. Export Content from Source

```bash
# Via cockpit: Transport Management → Source Subaccount → Export
# Select content (apps, destinations, subscriptions, etc.)
# Or via Content Agent (automated):
```

Enable Content Agent to auto-export on subscription changes:
- BTP Cockpit → **Content Agent** → **Configuration**
- Set source = DEV subaccount, target = CTM import queue

## 4. Import to Target Node

```bash
# Via cockpit: Transport Management → Target Node → Import Queue
# Queue auto-processes every 5 minutes by default
```

Manual import: **Import Queue** → select transport → **Import**

## 5. gCTS for ABAP Cloud

```
ABAP Cloud DEV ──▶ gCTS ──▶ Git Repository ──▶ gCTS ──▶ TST ──▶ PRD
```

```bash
# Configure gCTS in ABAP Cloud (transaction SCTS_TRANSPORT)
# 1. Create Git repository for ABAP transport objects
# 2. Register repository in gCTS configuration
# 3. Export transport → commit to Git → push
# 4. On target: pull from Git → import to ABAP system
```

## 6. Schedule Automated Transports

Via BTP Cockpit → **Transport Management** → **Schedules**:
- Create schedule for DEV → TST (e.g., nightly at 02:00)
- PRD import requires manual approval gate

## Pitfalls

**Failed import blocks entire queue**
- Cause: Import queue is sequential — one failure stops all subsequent transports for that node
- Solution: Either fix the failing transport or select it → **Skip**. Resolved items process next cycle (5 min).

**Content not appearing in target subaccount**
- Cause: Content was not explicitly exported from source before transport
- Solution: Manually trigger export from DEV node, or verify Content Agent is enabled and subscribed

**gCTS sync fails with Git authentication error**
- Cause: Git credentials expired or repository URL changed
- Solution: Update credentials in SCTS_TRANSPORT → Repository Settings, verify SSH key or PAT has write access

**Import takes longer than expected**
- Cause: Queue processes every 5 minutes; large transports are sequential, not parallel
- Solution: Wait for next cycle or trigger manual import. For urgency, use **Import Now** button

**Cloud Connector destinations not transported**
- Cause: Cloud Connector configs are environment-specific, not included in CTM transport
- Solution: Manually configure Cloud Connector on target subaccount. Only destination definitions inside BTP are transported.

## Verification

```bash
# Check CTM service is bound
cf services | grep cts

# Verify landscape configuration via API
cf curl "/v3/service_instances/<ctm-instance-guid>/parameters"
```

Confirm in BTP Cockpit:
- [ ] Landscape shows DEV → TST → PRD chain
- [ ] Import queue has no items in "Failed" state
- [ ] Last transport timestamp matches expected schedule
- [ ] Content Agent shows green status for source subaccount
- [ ] gCTS: `git log` on ABAP repo shows recent transport commits
