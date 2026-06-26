---
name: btp-cloud-transport-management
description: SAP Cloud Transport Management (CTM) — transport landscape nodes, CTS+ for BTP, content transport between subaccounts, import queues, transport scheduling, gCTS for ABAP Cloud, Content Agent service, landscape configuration. Use when configuring cloud transports, moving content between BTP subaccounts, or troubleshooting CTM import failures.
---

# SAP Cloud Transport Management (CTM)

Content lifecycle management across BTP subaccounts.

## Landscape Configuration

```
DEV Subaccount → CTM Node → TST Subaccount → CTM Node → PRD Subaccount
  (source)       (queue)     (target)                     (target)
```

## Transport Nodes

| Node Type | Role |
|---|---|
| Content Source | Export point (DEV subaccount) |
| Content Target | Import point (TST, PRD subaccount) |
| Cloud Transport Node | BTP-only node (no SAP on-premise connection) |

## gCTS (Git-based CTS for ABAP Cloud)

ABAP Cloud uses gCTS instead of traditional transport requests:
```
ABAP Cloud DEV → gCTS → Git Repository → gCTS → TST → PRD
```

## Import Queue

- Processes every 5 minutes by default
- Manual import from queue via "Import Queue" UI
- Failed import blocks all subsequent imports until resolved or skipped

## Content Agent

Automatically exports Fiori/UI5/CAP content from source subaccount for transport.

## Gotchas
- Imports are sequential per target — one at a time
- Content must be explicitly exported before transport
- Failed import blocks the queue for that target node
