# SAP Transport MCP

MCP server for SAP Change and Transport System (CTS). Gives Claude governed, auditable access to transport requests — list, inspect, create, release, and delete — via the SAP ADT REST API.

Built on [`sap-mcp-server-template`](https://github.com/Nidhideep/sap-mcp-server-template).

---

## What It Does

- Lists open and released transport requests
- Inspects transport contents (tasks, ABAP objects)
- Checks import queue on target systems (QA, PRD)
- Creates new transport requests with governance-validated descriptions
- Releases transports for import — with mandatory object verification and user confirmation
- Deletes unreleased transports — blocked if already released
- Supports multi-system DEV/QA/PRD in a single server instance

---

## Tech Stack

- TypeScript + Node.js ≥18
- `@modelcontextprotocol/sdk` — MCP server
- `axios` — HTTP client (supports mTLS for X.509 cert auth)
- `fast-xml-parser` — SAP ADT XML response handling
- `zod` — runtime schema validation
- SAP ADT REST API (`/sap/bc/adt/cts/`) over HTTPS

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Node.js | v18 or later — `node --version` to check |
| SAP NetWeaver | **7.56 or later** (or a patched 7.40/7.50/7.52 SP with the CTS ADT node backport) — the `/sap/bc/adt/cts/` ICF node was introduced in NetWeaver 7.56. Earlier releases do not expose the `transportrequests` REST endpoint and will return unexpected results. Ask your Basis admin to confirm your NetWeaver release and SP level. |
| SAP user | `S_ADT_RES` authorization, role `SAP_BC_DWB_ABAPDEVELOPER` (ask your Basis admin if unsure) |
| ICF service | `/sap/bc/adt/` and `/sap/bc/adt/cts/` activated — run transaction `SICF` in SAP GUI, navigate to `default_host → sap → bc → adt → cts` and activate. Ask Basis admin if not active. |
| Network | HTTPS access to SAP host — VPN required for most on-prem systems |
| Claude Code | CLI or desktop app installed |

### Finding your SAP connection details

Open **SAP Logon Pad** (or ask your Basis team):

| `.env` variable | Where to find it |
|-----------------|-----------------|
| `SAP_HOSTNAME` | SAP Logon → right-click system → Properties → Application Server |
| `SAP_SYSNR` | SAP Logon → right-click system → Properties → System Number (2 digits, e.g. `00`) |
| `SAP_CLIENT` | The 3-digit number on the SAP login screen (e.g. `100`) |
| `SAP_USERNAME` | Your SAP user ID (same as you type to log in) |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/Nidhideep/sap-transport-mcp
cd sap-transport-mcp
npm install
```

### 2. Run setup

```bash
npm run setup
```

This creates `.env` from `.env.example` and generates `.mcp.json` with the absolute path to `dist/src/index.js` already filled in. Safe to re-run — never overwrites an existing `.env`.

### 3. Fill in your SAP credentials

Open `.env` and replace the placeholder values:

```env
SAP_HOSTNAME=your-sap-host.example.com   # → your real hostname
SAP_SYSNR=00                              # → 2-digit system number
SAP_CLIENT=100                            # → 3-digit client number
SAP_USERNAME=your_user                    # → your SAP user ID
SAP_PASSWORD=your_password                # → your SAP password
```

> **Not sure where to find these?** Open SAP Logon Pad → right-click your system → Properties.
> `SAP_CLIENT` is the 3-digit number on the SAP login screen.

### 4. Build

```bash
npm run build
```

### 5. Run preflight check

```bash
npm run preflight
```

This validates every variable, detects any remaining placeholder values, and tests a live HTTPS connection to your SAP system — before you register with Claude Code.

Example output when everything is ready:
```
  ✓ SAP_HOSTNAME = dev.sap.company.com
  ✓ SAP_USERNAME is set
  ✓ dist/src/index.js exists
  ✓ SAP ADT responded HTTP 200 — connection OK

All checks passed. You are ready to connect to Claude Code.
```

If any check fails, the script tells you exactly what to fix.

### 6. Register with Claude Code

`.mcp.json` was created by `npm run setup` and is ready to use as a **project-level** config (active when Claude Code is opened in this folder).

For **user-level** registration (active in all sessions), copy the server entry into `~/.claude/mcp.json`.

**Restart Claude Code after registering** — MCP servers load at startup.

### 7. Confirm tools are available

In Claude Code, ask:
```
What SAP transport tools do you have available?
```

Claude should list all 8 tools. If not, see [troubleshooting.md](docs/troubleshooting.md).

### 8. First test with DRY_RUN

Set `DRY_RUN=true` in `.env`, rebuild, and try the tools — read tools work normally, write tools are blocked safely:

```bash
# .env → DRY_RUN=true
npm run build
```

Set back to `false` when ready for live writes.

---

## Available Tools

### Read Tools

| Tool | Description |
|------|-------------|
| `transport_list_systems` | List configured SAP systems |
| `transport_list_requests` | List transport requests (filter by owner/status) |
| `transport_get_request` | Full transport details: tasks, objects, status |
| `transport_list_objects` | ABAP objects in a transport |
| `transport_check_import_queue` | Pending imports on a target system |

### Write Tools

| Tool | Description | Risk |
|------|-------------|------|
| `transport_create_request` | Create a new transport request | Low |
| `transport_release_request` | Release transport for import | **High — irreversible** |
| `transport_delete_request` | Delete an unreleased transport | High |

---

## Standard Workflow

```
1. transport_list_systems       → confirm systemId values
2. transport_list_requests      → find open transports
3. transport_get_request        → inspect contents
4. transport_list_objects       → verify ABAP objects
5. transport_check_import_queue → check target system queue
6. [user confirms]
7. transport_release_request    → release with policy checks + verify
```

See [examples/release-workflow.md](examples/release-workflow.md) for a full walkthrough.

---

## Multi-System Setup (DEV / QA / PRD)

Set `SYSTEMS_CONFIG` in `.env`:

```env
SYSTEMS_CONFIG=[
  {"id":"DEV","hostname":"dev.sap.co","sysnr":"00","client":"100","language":"EN","isDefault":true},
  {"id":"QA","hostname":"qa.sap.co","sysnr":"01","client":"200","language":"EN","isDefault":false}
]
```

Every tool accepts an optional `systemId` parameter. Omit it to use the default system.

---

## Governance Rules

- Release is irreversible — Claude requires explicit user confirmation + shows full object list
- Empty transports (0 objects) cannot be released
- Released transports cannot be deleted
- Transport description must be ≥10 characters
- All writes are audit-logged (stderr JSON with timestamp, transport number, object count)
- `DRY_RUN=true` blocks all write tools — use for testing

See [docs/governance.md](docs/governance.md) for full policy details.

---

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for:
- Auth failures (Basic/certificate)
- Connection errors (VPN, port, ICF activation)
- CSRF token issues
- Policy violation errors

---

## Reference

- [Transport Field Reference](docs/transport-field-reference.md)
- [Authentication Setup](docs/authentication.md)
- [Governance Policy](docs/governance.md)
- [Release Workflow Example](examples/release-workflow.md)
- [SAP ADT Documentation](https://help.sap.com/docs/ABAP_PLATFORM_NEW/c238d694b825421f940829321ffa326a/4ec805126e391014adc9fffe4e204223.html)
