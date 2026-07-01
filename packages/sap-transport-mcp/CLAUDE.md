# Claude Behavior Contract — SAP Transport MCP

## Governing Standard

Before making any change to this server, read:

```
../personal-enterprise-brain/ontology/mcp/sap-mcp-standard.md
```

## What This Server Does

This MCP server provides governed access to the SAP Change and Transport System (CTS).
It allows Claude to list, inspect, create, release, and delete SAP transport requests
via the SAP ADT REST API — with full governance and audit logging.

Supported systems: configured via `SYSTEMS_CONFIG` or individual `SAP_*` env vars.

---

## Standard Workflow — Claude Must Follow This Sequence

When a user asks to release or manage a transport:

1. `transport_list_systems` — confirm available systems
2. `transport_list_requests` — show open transports for the user
3. `transport_get_request` — inspect the specific transport (tasks + objects)
4. `transport_list_objects` — confirm expected ABAP objects are present
5. `transport_check_import_queue` — verify target system queue status
6. **Present the full object list to the user and ask for explicit confirmation**
7. `transport_release_request` — only after confirmed

**Release is irreversible.** Step 6 is mandatory. Never skip it.

---

## What Claude Must NOT Do

- Call `transport_release_request` without first showing the object list to the user
- Skip verification after any write operation
- Expose SAP technical field names (`TRKORR`, `AS4TEXT`, `TRSTATUS`) in responses
- Suggest committing `.env` or `.mcp.json`
- Attempt to import transports into production directly — import is a Basis team responsibility
- Bypass the governance layer in `config/policy.ts`

---

## Tool Reference

### Read Tools (always safe)
| Tool | When to use |
|------|-------------|
| `transport_list_systems` | First call — confirms systemId values |
| `transport_list_requests` | Discover open transports |
| `transport_get_request` | Inspect a specific transport |
| `transport_list_objects` | Verify object list before release |
| `transport_check_import_queue` | Check target system backlog |

### Write Tools (require care)
| Tool | Risk | Pre-condition |
|------|------|---------------|
| `transport_create_request` | Low | Description ≥10 chars |
| `transport_release_request` | **High — irreversible** | Objects > 0, user confirmed |
| `transport_delete_request` | High — permanent | Status = Modifiable |

---

## Governance Rules

1. Release is **irreversible** — export cannot be undone without Basis team intervention
2. Empty transports (0 objects) cannot be released — enforced in policy.ts
3. Released transports cannot be deleted — enforced in policy.ts
4. All writes are audit-logged (console.error → stderr) with timestamp, transport number, object count, target system
5. `DRY_RUN=true` blocks all writes — use for testing and staging

---

## Transport Number Format

Valid format: `[A-Z]{3}K[0-9]{6}` — e.g. `DEVK900123`
- First 3 letters = system SID (DEV, QAS, PRD)
- K = transport request type indicator
- 6 digits = sequential number

---

## Auth Setup

See `docs/authentication.md`. Set `AUTH_METHOD=basic` or `AUTH_METHOD=certificate` in `.env`.
Never hardcode credentials in any source file.
