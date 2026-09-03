---
name: sap-router-skill
description: >-
  SAP development orchestrator v7.1.0 — Karpathy command format (Think→Simplify→
  Surgical→Verify), healthcheck guardian, self-learning router, caveman-compressed
  output default. Delegates small-scope work to the cavecrew subagents automatically:
  find/search/locate → cavecrew-investigator, fix/edit/rename/typo → cavecrew-builder,
  review/audit/diff → cavecrew-reviewer.
  Multi-protocol: HTTP/OData/RFC/SOAP RFC/BDC. ZROUTER v5 REST gateway. Install pipeline: YDOWN→ZABAPGIT→ZSAPLINK. BDC engine: YFG_SBDC. Test suites: ZODATA_TEST_AUTOMATION_FGR.
  Use for any SAP task.
---

# SAP Router v7.1.0 — Karpathy Command Format

**Behavioral wrapper: every operation follows 4 principles. Healthcheck first.**

**Default output: caveman compression.** Drop articles/filler/pleasantries.
Fragments OK. Code blocks unchanged.

## Runtime root

Resolve `SAP_ROUTER_ROOT` before running router commands. It must point to the
sap-router-skill repository and contain `scripts/source_catalog.py`, `package.json`,
and `.agents/`. Change the working directory to that root before using any relative
`python scripts/...` or `npm run ...` command below. Fail closed if the root is not
configured or invalid; never assume the user's current project is the router repo.

---

## Principle -1 — Delegate Before You Work (RUN FIRST)

**Before doing anything else, classify the request and delegate.** Small-scope work must
NOT be done in the main context — it goes to a cavecrew subagent via the `Agent` tool.
This is the single largest token saving in the whole router; skipping it wastes the
main context on work a cheaper agent handles better.

Match the request against this table. On a match, **immediately call the `Agent` tool**
with the given `subagent_type` and stop — do not pre-read files, do not pre-search, do
not "just check something first". The subagent does the reading.

| Request looks like | `subagent_type` | Why |
|---|---|---|
| find, search, locate, "where is", look up, grep, scan for | `cavecrew-investigator` | read-only lookup, runs on haiku |
| fix, edit, change, rename, remove, add method/field, typo, "single file", "small change" | `cavecrew-builder` | surgical 1-2 file edit |
| review, audit, "check diff", "review this", PR review, merge request | `cavecrew-reviewer` | severity-tagged findings |

Rules:

1. **Builder before investigator.** If the request is to *change* something, send it
   straight to `cavecrew-builder` — it does its own locating. Do not run an
   investigator pass first.
2. **One agent, one call.** Pass the user's request plus the concrete file paths you
   already know. Never paste file contents into the prompt — the agent reads them.
3. **Honour the refusal.** `cavecrew-builder` returns `REFUSE: <reason>` when the change
   exceeds 2 files, adds a feature, or spans a refactor. That is a correct outcome:
   take the work back into the main context and proceed with the full flow below.
   Never re-dispatch the same task to get a different answer.
4. **Escalation is one-way.** `cavecrew-investigator` returns
   `ESCALATE: needs cavecrew-builder` when the task needs an edit. Re-dispatch once to
   the builder with the files it found.
5. **No match → no delegation.** Anything larger — spec implementation, transport,
   deployment, multi-object ABAP work — skips this section entirely and runs the normal
   flow starting at Principle 0.

To confirm the routing decision programmatically:

```
python scripts/sap_router.py route --action "<the user request>"
```

A `strategy` of `caveman-surgical`, `caveman-readonly`, or `caveman-diff-review` means
delegate; the `agent_type` field names the exact `subagent_type` to pass.

---

## Principle 0 — Diagnose without implicit execution

Run `python scripts/healthcheck.py --offline --read-only` first. This checks the
canonical inventory without loading credentials, installing packages or contacting SAP.
For authorized read probes use `--execute --read-only`; select one server with
`--check-mcp ID`. Evidence is returned as JSON with `--json`; persistence requires
`--output PATH`. Offline/degraded is not an operational failure or proof of readiness.

Configured, initialized and domain-ready are separate states. A tool listing does
not prove authentication or an actual read. Never claim mutation authority from a
read probe. Missing credentials must be configured locally, never pasted into chat.
TLS verification must remain enabled.

---

## Principle 1 — Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing, state:

```
ASSUMPTIONS:
- SAP version: S/4HANA 2023, Basis 757
- Module: MM (detected from "material" + "BAPI_MATERIAL_SAVEDATA")
- BAPI parameters: HEADDATA + CLIENTDATA + MATERIALDESCRIPTION
- Authorization: S_DEVELOP + S_TCODE for MM01/MM02/MM03
- Transport: DEV system, client 100

UNCERTAINTIES (if any):
- BAPI_MATERIAL_SAVEDATA field MATERIAL_TYPE: which value for raw materials? (ROH vs HAWA)

TRADEOFFS:
- ADT direct: fastest for source read, cannot create materials
- SOAP RFC: call ANY BAPI via plain HTTP POST, no JCo/pyrfc needed
- ZROUTER RFC: batch BAPI execution, need RFC destination
- GUI fallback: MM01 transaction, requires SAP GUI installed + scripting enabled
- OData BAPI wrapper: IWBEP/BAPI_* via Gateway OData V2
→ RECOMMENDATION: SOAP RFC for single BAPI call, ZROUTER RFC for batch, GUI for single material with config
```

If multiple BAPIs, transaction fallbacks, or routing options exist, always present them as an enumerated (numbered) list (1., 2., 3...) to facilitate user selection. If SAP config unclear → ask.

---

## Principle 2 — Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

Routing decision tree — SIMPLEST path wins:

```
User Request
    │
    ▼
1. CAVEMAN scope? (find/fix/review, 1-2 files)
    │ YES → call Agent tool NOW, subagent_type=
    │       cavecrew-investigator | cavecrew-builder | cavecrew-reviewer
    │ STOP here — do not read/search first. See Principle -1.
    │ 60% token savings. Caveman-compressed output.
    ▼
2. ADT available? (read_source, search, syntax_check, activate)
    │ YES → arc-1 (primary) or aibap (secondary)
    │ Self-learn picks best based on latency history.
    ▼
3. BAPI/RFC call? (create/read BAPI, FM execution)
    │ Check if SOAP RFC available (/sap/bc/soap/rfc)
    │ YES → Call BAPI via plain HTTP POST → No JCo/pyrfc needed
    │ Resources: /sap/bc/soap/rfc + /sap/opu/odata/IWBEP/BAPI_*
    │ for Gateway OData BAPI wrapper
    ▼
4. GUI REQUIRED? (SPRO, SM30, SU01, MM01, VA01...)
    │ YES → IMMEDIATE GUI fallback — skip ADT attempt
    │ Missing nav data? → sap-gui-web-enrich → web search for field IDs
    │ Try: mcp-sap-gui → mcp-sap-gui-kts → sapgui-mcp-go
    ▼
5. Functional WRITE? (create material, post document, create order...)
    │ Requires explicit functional context (--functional). Without it →
    │   needs-functional-context, NO BAPI fired (BAPIs fire only when a real
    │   functional action requires them).
    │ With context → BAPI-first dispatch (commit stays in backend), else
    │   SAP GUI write transaction. Optional: --use-zrouter uses ZROUTER RFC
    │   ONLY if the user opted in (zrouter accept). Never the default.
    ▼
6. Spec → code? (implement specification, full workflow)
    │ YES → sap_router.py pipeline → 8 stages
    │ Stage 1: Spec Analysis → Stage 8: Transport Gate
    ▼
7. LLM optimization? (prompt engineering, eval harness)
    │ YES → sap-llm-engineering → evaluate → optimize → retry
```

**Capability routing:** run `python scripts/mcp_launcher.py list --capability CAPABILITY`.
Only enabled providers from `.agents/registries/mcps.json` may launch. The candidate
registry is discovery data, not a fallback execution list. Do not install or promote
candidates implicitly. Retry reads through enabled providers only; an uncertain
write requires reconciliation, not fallback or blind retry.

**CPI route**: use `sap-cpi-mcp` for API/background reads and approved mutations;
use `integration-suite-ui-mcp` only as browser-session fallback. Keep all community
CPI MCP candidates disabled until registry promotion. For tool contracts and source
decisions, load `../cpi-iflow-development/references/cpi-mcp-tool-contracts.md` and
`../cpi-iflow-development/references/cpi-tooling-catalog.md`.

---

### Development and functional access

ADT is development tooling only, never a substitute for business APIs.
Functional writes require explicit functional context, approved target/arguments,
and a suitable BAPI or configured business API. Availability of an HTTP path does
not prove authorization or implementation. ZROUTER remains explicit opt-in.

---

## Principle 3 — Surgical Changes

**Touch only what you must. Clean up only your own mess.**

SAP-specific surgical rules:
- Transport only changed objects — not whole package
- Don't reformat adjacent methods when fixing one
- Don't "improve" CDS views while adding one field
- Match existing naming: ZCL_ prefix if project uses it
- Match existing style: UPPER/lower keywords, indent width
- If you notice unrelated dead code → mention it, don't delete

Caveman compression is the SURGICAL default:
- Drop articles/filler → 60% fewer tokens
- Code blocks preserved exactly
- Security warnings use full clarity

---

## Principle 4 — Goal-Driven Execution

**Define success criteria. Loop until verified.**

Every SAP operation follows this pattern:

```
1. [Spec Analysis]     → verify: module identified, BAPIs listed
2. [Technical Proposal] → verify: reviewed by sap-crew-analysis (7 agents)
3. [Implementation]     → verify: syntax OK, abaplint pass, unit tests green
4. [Peer Review]        → verify: 9-dimension score >= 70/100
5. [Transport]          → verify: transport gate GO, objects in task
```

### Verification Checklist Per Operation Type

**ABAP Code Change:**
```
[ ] aibap syntax_check → no errors
[ ] npm run abap:lint → pass
[ ] aibap run_unit_tests → all green
[ ] sap-crew-analysis (quick mode) → score >= 70
[ ] abap-code-review (9 dimensions) → GO
[ ] sap-transport-gate (10 dimensions) → GO
```

**BAPI/Material Create:**
```
[ ] BAPI executed without E/A-type messages
[ ] BAPIRET2 TABLES checked (not just IMPORTING RETURN)
[ ] BAPI_TRANSACTION_COMMIT with WAIT = 'X'
[ ] Verify in target system: MM03 for material, VA03 for order
[ ] BAL log entry created
```

**CPI iFlow:**
```
[ ] iFlow deployed to CPI tenant
[ ] Test message processed (no errors in MPL)
[ ] Response payload matches expected structure
[ ] Groovy script linted (cpi:lint)
```

**GUI Transaction:**
```
[ ] Transaction navigated successfully
[ ] All required fields populated
[ ] No unexpected popups/dynpros
[ ] Result captured via ALV read or screenshot
[ ] Session closed cleanly
```

### Pipeline Execution

```bash
# Full pipeline (all 8 stages with verification at each)
python scripts/sap_router.py pipeline --spec requirements.md

# Fast pipeline (skip deep analysis)
python scripts/sap_router.py pipeline --spec requirements.md --mode fast

# Resume from stage after fixing verification failure
python scripts/sap_router.py pipeline --spec requirements.md
```

### Self-Learn Feedback Loop

```bash
# After every MCP call — learn from outcome
npm run learn:mcp -- --mcp arc-1 --latency 245 --success true

# After every routing decision — track success
npm run learn:route -- --action MM_CREATE_MATERIAL --success true

# Inject learned context into next routing decision
npm run learn:ctx
```

---

## Quick Dispatch Table

| User says | Route | Execute + Verify |
|---|---|---|
| "read ZCL_*" / "get source" | ADT (self-learn best) | arc-1 SAPRead → verify: source returned |
| "write/activate Z*" | ADT direct | arc-1 SAPWrite → SAPActivate → syntax check |
| "create material/order" (functional) | BAPI dispatch (--functional) | BAPI → BAPIRET2 check → MM03/VA03 verify. ZROUTER only if opted in. |
| functional write w/o --functional | needs-functional-context | classify only — no BAPI fired out of context |
| "call BAPI without JCo" / "BAPI via HTTP" | SOAP RFC | HTTP POST /sap/bc/soap/rfc → parse SOAP response → verify |
| "run stages in parallel" / big spec | dispatch-plan / crew-dispatch | emit wave plan; same-wave agents launch concurrently |
| "SPRO / SM30 / SU01 / MM01 / VA01..." | GUI IMMEDIATE | mcp-sap-gui navigate → execute → verify |
| "GUI data missing for tcode X" | GUI + web enrich | WebSearch SAP Help → build BDC → cache |
| "find/where is X" | `Agent(subagent_type="cavecrew-investigator")` | delegate immediately → 60% token savings |
| "fix typo in ZCL_X line 42" | `Agent(subagent_type="cavecrew-builder")` | 1-2 file surgical edit; honour `REFUSE:` |
| "review diff/PR" | `Agent(subagent_type="cavecrew-reviewer")` | severity-tagged findings, read-only |
| "implement spec" | Pipeline 8-stage | spec → proposal → implement → lint → review → transport |
| "healthcheck" | healthcheck.py | .env check → MCP probes → missing prompt |
| "learn from this" | self_learn.py | record outcome → adapt routing → persist |
| "RAG search for X" | RAG connector | Pinecone/Supabase/Azure → retrieve → generate |
| "optimize LLM prompt for ABAP" | sap-llm-engineering | evaluate → optimize prompt → retry |

---

## Project inventory

Canonical source: `.agents/`. There are 165 skills and 11 enabled MCP servers.
The 62 disabled candidates plus the planned SmartForms entry are not launchable.
Use `python scripts/validate_catalog.py --strict` and
`python scripts/source_catalog.py search "task description"` for current inventory.
Regenerate IDE assets rather than copying edited skill bodies.
For Python runtime requirements, follow each executable's actual version constraint.

---

## Install ZROUTER on SAP (OPTIONAL — opt-in only, never the engine)

ZROUTER is an OPTIONAL RFC accelerator. Routing never auto-probes or
auto-installs it. Ask first: `python scripts/sap_router.py zrouter offer`
(default: decline; a decline is persisted in `zrouter_optin.json`). Only after
`python scripts/sap_router.py zrouter accept` do the steps below apply:

```bash
# 1. Create package
aibap: create_object(type="DEVC", name="ZROUTER")

# 2. Create DDIC + deploy ABAP classes
aibap: create_object(type="TABL", name="ZROUTER_TMPL_HD")
python scripts/abap_serializer.py package --source templates/zrouter_dispatch.prog.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/

# 3. Create Function Module
aibap: create_object(type="FUGR", name="ZROUTER")
aibap: create_object(type="FUNC", name="ZROUTER_DISPATCH_FM", function_group="ZROUTER")

# 4. Activate + test
aibap: activate_objects(["ZCL_ZROUTER_DISPATCH","CX_ZROUTER","ZROUTER_DISPATCH_FM"])
python scripts/sap_router.py route --action MM_CREATE_MATERIAL --functional --use-zrouter
```
