---
name: sap-transport-management
description: Plan, validate, and govern SAP CTS transport requests, release queues, imports, and transport evidence.
---

# SAP Transport Management

Use for CTS, transport request, release, import queue, and transport-gate tasks.

## Safety contract

- Read and validate first; never release or import from an inferred target.
- Mutations require explicit plan, approval, and commit semantics.
- Record request ID, source/target system, object scope, and verification evidence.
- Route through `sap-transport-gate` and the capability registry; use SAP GUI or RFC only as an approved fallback.

For a dry run, report the proposed transport operation and blockers without calling a write-capable MCP.
