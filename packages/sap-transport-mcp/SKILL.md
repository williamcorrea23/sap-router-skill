---
name: sap-transport-mcp
description: >
  Manage SAP transport requests directly from Claude — list open and released
  transports, inspect their ABAP objects, check import queues, create new
  requests, release transports for import, and delete unreleased requests.
  Built with governance controls: DRY_RUN mode, mandatory verification before
  release, and full audit logging. Use this when managing SAP change and
  transport workflows, auditing what's in a transport before release, or
  checking what is queued for import into QA or production.
  Requires SAP NetWeaver 7.56+ with the ADT CTS REST API enabled.
license: MIT
compatibility: Node.js >= 18.0.0, SAP NetWeaver 7.56+ with ADT CTS services activated
metadata:
  author: Nidhideep Bhandari
  repository: https://github.com/Nidhideep/sap-transport-mcp
  npm: https://www.npmjs.com/package/sap-transport-mcp
  category: enterprise
  tags: sap, transport, cts, change-management, abap, governance
---

# SAP Transport MCP Server

MCP server for SAP Change and Transport System (CTS). Gives Claude governed,
auditable access to transport requests via the SAP ADT REST API.

## When to use this skill

Use this skill when:
- Listing open transport requests in a DEV system
- Inspecting what ABAP objects are inside a transport before releasing
- Checking the import queue for QA or PRD — "what's waiting to go to production?"
- Creating a new transport request
- Releasing a transport after confirming its contents
- Auditing who owns which transports

## Tools

| Tool | Description |
|------|-------------|
| `transport_list_requests` | List transport requests (filter by owner, status, system) |
| `transport_get_request` | Get full details: description, status, tasks, and all ABAP objects |
| `transport_list_objects` | List ABAP objects inside a specific transport |
| `transport_check_import_queue` | Check what transports are queued for a target system |
| `transport_create_request` | Create a new Workbench or Customizing transport |
| `transport_release_request` | Release a transport — verifies objects exist first |
| `transport_delete_request` | Delete an unreleased transport (blocked if already released) |
| `transport_list_systems` | List configured SAP systems |

## Setup

```bash
npm install -g sap-transport-mcp
# or from source:
git clone https://github.com/Nidhideep/sap-transport-mcp
cd sap-transport-mcp && npm install && npm run build
cp .env.example .env   # fill in SAP_HOSTNAME, SAP_USERNAME, SAP_PASSWORD
```

Register with Claude Code:
```bash
claude mcp add sap-transport -- node /absolute/path/to/dist/src/index.js
```

## Required environment variables

| Variable | Description |
|----------|-------------|
| `SAP_HOSTNAME` | SAP server hostname or IP |
| `SAP_SYSNR` | System number (2 digits, e.g. `00`) |
| `SAP_CLIENT` | Client number (e.g. `100`) |
| `SAP_USERNAME` | SAP username |
| `SAP_PASSWORD` | SAP password |

Set `DRY_RUN=true` to block all write operations (create, release, delete).

## Example prompts

- "List all open transports owned by me in the DEV system"
- "What ABAP objects are in transport DEVK900123?"
- "What transports are queued for production?"
- "Create a new workbench transport for the Q2 material master changes"
- "Release transport DEVK900456 — confirm the object list first"
