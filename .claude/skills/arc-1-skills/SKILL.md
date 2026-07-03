---
name: arc-1-skills
description: ARC-1 agentic SAP development skills (arc-mcp/arc-1/skills). Reference for ADT tools, code activation, and automated ABAP editing. Covers the 8 arc-1 MCP tools (SAPContext, SAPDiagnose, SAPLint, SAPManage, SAPNavigate, SAPRead, SAPSearch, SAPTransport), the read-edit-activate-transport flow, and arc-1's role as PRIMARY ADT MCP in the routing tree.
trigger:
  keywords: [arc-1, adt tools, sapread, sapmanage, saptransport, code activation, abap editing, adt mcp, object activation, transport request]
  intent: Using the arc-1 MCP server to read, search, edit, activate, and transport ABAP objects over ADT as the primary development channel
prerequisites:
  - arc-1 MCP configured in .mcp.json and healthy (npm run hc — criticality HIGH)
  - SAP host, user, and password set in .env (validated by npm run hc:prompt)
  - Developer authorization on the target system (S_DEVELOP) for write operations
  - Modifiable transport request or local package ($TMP) for changes
---

# ARC-1 — Primary ADT MCP for Agentic ABAP Development

arc-1 is the PRIMARY ADT MCP of this orchestrator. All ADT-class operations (read source,
edit, activate, lint, transport) route to arc-1 first, then aibap (secondary), then
mcp-sap-gui (fallback). See `scripts/sap_router.py` (`SapRouter.get_route()`).

## 1. Tool Map — When to Use Which

| Tool | Use for |
| --- | --- |
| **SAPContext** | System/session context — SID, client, user, release. Call first in a new session |
| **SAPSearch** | Find objects by name/type when you do not know the exact object name |
| **SAPNavigate** | Jump between related objects — includes, super/subclasses, where-used |
| **SAPRead** | Read source code and metadata of a known object (class, program, CDS, table) |
| **SAPLint** | Static checks (syntax, ATC-style) on source BEFORE activation |
| **SAPManage** | Create / modify / activate / delete objects — all write operations |
| **SAPDiagnose** | Short dumps (ST22-style), traces, runtime diagnostics after failures |
| **SAPTransport** | List / create / assign / release transport requests |

Rule of thumb: read-only questions -> SAPSearch/SAPRead/SAPNavigate.
Changes -> SAPLint -> SAPManage -> SAPTransport. Failures -> SAPDiagnose.

## 2. Route Through the Orchestrator

```bash
# Let the router pick arc-1 (ADT-first) for the action:
npm run router -- --action ADT_READ_SOURCE
python scripts/sap_router.py route --action ADT_EDIT_CLASS

# Force GUI fallback only when ADT cannot do it (SPRO, dynpro):
npm run router:gui -- --action SPRO_CONFIG
```

If arc-1 is down, the TieredFallback engine (`scripts/fallback_engine.py`) cascades
ADT -> RFC -> GUI -> BDC -> Offline -> Manual. Do not hand-code fallbacks.

## 3. Typical Flow: Read -> Edit -> Activate -> Transport

1. **Context** — `SAPContext` to confirm system/client (never assume DEV).
2. **Locate** — `SAPSearch` for the object; `SAPNavigate` to find the exact include/method.
3. **Read** — `SAPRead` to get current source. Edit surgically (Karpathy: touch only what's needed).
4. **Lint** — `SAPLint` on the modified source. Fix findings before writing.
5. **Write** — `SAPManage` to save the change (object goes INACTIVE).
6. **Activate** — `SAPManage` activate. An inactive object is invisible to runtime.
7. **Transport** — `SAPTransport` to assign the object to a modifiable request. Release only at gate (`npm run abap:review:transport`).
8. **Verify** — `SAPRead` the active version back; `SAPDiagnose` if execution dumps.

## 4. Health and Learning

```bash
# Probe arc-1 (HIGH criticality) + .env completeness:
npm run hc
npm run hc:prompt      # interactive fix for missing SAP_HOST/SAP_USER/SAP_PASSWORD

# Feed routing telemetry so self_learn.py keeps arc-1 primary:
npm run learn:mcp -- --mcp arc-1 --latency 245 --success true
npm run learn:route -- --action ADT_EDIT_CLASS --success true
```

## Pitfalls

- **401/403 on every arc-1 call** → Cause: SAP credentials missing or wrong in .env, or user lacks S_DEVELOP. Solution: run `npm run hc:prompt` to fill SAP host/user/password; confirm developer role with Basis.
- **"Object locked by user X"** → Cause: object is edit-locked in SE80/ADT by another session (or a stale lock of your own). Solution: retry later or ask the lock owner to release (SM12); never force-delete locks on shared objects.
- **Change saved but behavior unchanged** → Cause: object left INACTIVE — SAPManage save without activate. Solution: always activate after write and re-read the active version to confirm.
- **Activation fails with syntax errors** → Cause: edit broke dependent objects or lint step was skipped. Solution: run `SAPLint` before `SAPManage` write; use `SAPNavigate` where-used to check dependents; `SAPDiagnose` for details.
- **"Not assigned to a transport" on save** → Cause: object in a transportable package but no modifiable request. Solution: `SAPTransport` create/assign a workbench request first, or use $TMP for throwaway objects.
- **arc-1 timeout / connection refused** → Cause: MCP server down or SAP host unreachable. Solution: `npm run hc` to confirm; router auto-falls back to aibap then GUI — do not bypass the fallback engine.

## Verification

```bash
# 1. arc-1 healthy and env complete:
npm run hc

# 2. Router resolves an ADT action to arc-1 (primary):
python scripts/sap_router.py route --action ADT_READ_SOURCE

# 3. After an edit: SAPRead the object and confirm version = active,
#    then gate before release:
npm run abap:review:transport
```

## Related

- **sap-router-skill** — master routing tree (ADT -> arc-1 first, GUI fallback)
- **sap-adt-cli** — ADT REST access via CLI when MCP tooling is unavailable
- **abap-code-review** — 9-dimension GO/NO-GO gate before SAPTransport release
- **sap-transport-gate / sap-transport-management** — transport landscape rules
- **karpathy-guidelines** — Think, Simplify, Surgical, Goal-Verify wrapper for every edit
