---
name: sap-router-skill
description: >-
  SAP development orchestrator v5.0.0 — Karpathy command format (Think→Simplify→
  Surgical→Verify), healthcheck guardian, self-learning router, caveman-compressed
  output default. 85 skills, 35 MCPs (+18 planned), 15 CLIs. Multi-protocol: HTTP/OData/RFC/BDC. ZROUTER v5 REST gateway. Install pipeline: YDOWN→ZABAPGIT→ZSAPLINK. BDC engine: YFG_SBDC. Test suites: ZODATA_TEST_AUTOMATION_FGR.
  Use for any SAP task.
---

# SAP Router v5.0.0 — Karpathy Command Format

**Behavioral wrapper: every operation follows 4 principles. Healthcheck first.**

**Default output: caveman compression.** Drop articles/filler/pleasantries.
Fragments OK. Code blocks unchanged.

---

## Principle 0 — Healthcheck First (RUN ALWAYS)

```
python scripts/healthcheck.py
```

Before ANY operation, verify:

1. **.env exists**: `python scripts/healthcheck.py --prompt-missing`
   → If missing: prompt user for ARC_SAP_URL, ARC_SAP_USER, ARC_SAP_PASSWORD, ARC_SAP_CLIENT
   → Show: `cp .env.template .env` + edit instructions

2. **MCPs connected**: probes all 35 MCPs (+18 planned)
   → HIGH criticality: arc-1, aibap (block on failure)
   → MEDIUM: mcp-abap-adt, mcp-sap-gui, btp-sap-odata-to-mcp (warn)
   → OPTIONAL: RAG connectors (Pinecone, Supabase, Azure) — pre-ready, activate later

3. **Self-learn context**: `python scripts/self_learn.py context`
   → Load learned MCP reliability, system features, routing preferences

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
- ZROUTER RFC: batch BAPI execution, need RFC destination
- GUI fallback: MM01 transaction, requires SAP GUI installed + scripting enabled
→ RECOMMENDATION: ZROUTER RFC for batch, GUI for single material with config
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
    │ YES → cavecrew-investigator/builder/reviewer
    │ 60% token savings. Caveman-compressed output.
    ▼
2. ADT available? (read_source, search, syntax_check, activate)
    │ YES → arc-1 (primary) or aibap (secondary)
    │ Self-learn picks best based on latency history.
    ▼
3. GUI REQUIRED? (SPRO, SM30, SU01, MM01, VA01...)
    │ YES → IMMEDIATE GUI fallback — skip ADT attempt
    │ Missing nav data? → sap-gui-web-enrich → web search for field IDs
    │ Try: mcp-sap-gui → mcp-sap-gui-kts → sapgui-mcp-go
    ▼
4. Functional WRITE? (create material, post document, create order...)
    │ Requires explicit functional context (--functional). Without it →
    │   needs-functional-context, NO BAPI fired (BAPIs fire only when a real
    │   functional action requires them).
    │ With context → BAPI-first dispatch (commit stays in backend), else
    │   SAP GUI write transaction. Optional: --use-zrouter uses ZROUTER RFC
    │   ONLY if the user opted in (zrouter accept). Never the default.
    ▼
5. Spec → code? (implement specification, full workflow)
    │ YES → sap_router.py pipeline → 8 stages
    │ Stage 1: Spec Analysis → Stage 8: Transport Gate
    ▼
6. LLM optimization? (prompt engineering, eval harness)
    │ YES → sap-llm-engineering → evaluate → optimize → retry
```

**Cascading MCP Fallback**:
If a tool call to the primary `mcp_server` fails (due to connection timeout, missing credentials, or server errors), the agent must inspect the `mcp_servers` list returned by the router and iteratively execute the tool on the next server in the list until one succeeds, or until all options are exhausted.
- Advanced ABAP: `abap-mcp` → `arc-1` → `aibap` → `mcp-abap-adt`
- Standard ADT: `arc-1` → `abap-mcp` → `aibap` → `mcp-abap-adt`
- Cloud ALM: `mcp-calm-server` → `cloud-alm-itsm`
- Transports: `sap-transport-mcp` → `abap-mcp` → `arc-1` → `aibap`
- GUI Fallbacks: `mcp-sap-gui` → `mcp-sap-gui-kts` → `sapgui-mcp-go`

**Self-learn adapts routing**: tracks MCP latency, success rates, auto-prefers faster paths.
`python scripts/self_learn.py best-mcp --candidates "arc-1,aibap,mcp-abap-adt"` → returns best.

**RAG pre-ready**: Pinecone, Supabase, Azure AI Search connectors configured in .mcp.json.
Activate by uncommenting vars in .env. No code changes needed.

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
python scripts/sap_router.py pipeline --spec requirements.md --resume-from stage4
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
| "run stages in parallel" / big spec | dispatch-plan / crew-dispatch | emit wave plan; same-wave agents launch concurrently |
| "SPRO / SM30 / SU01 / MM01 / VA01..." | GUI IMMEDIATE | mcp-sap-gui navigate → execute → verify |
| "GUI data missing for tcode X" | GUI + web enrich | WebSearch SAP Help → build BDC → cache |
| "find/where is X" | cavecrew-investigator | delegate → 60% token savings |
| "fix typo in ZCL_X line 42" | cavecrew-builder | 1-2 file surgical edit |
| "review diff/PR" | cavecrew-reviewer | severity-tagged findings |
| "implement spec" | Pipeline 8-stage | spec → proposal → implement → lint → review → transport |
| "healthcheck" | healthcheck.py | .env check → MCP probes → missing prompt |
| "learn from this" | self_learn.py | record outcome → adapt routing → persist |
| "RAG search for X" | RAG connector | Pinecone/Supabase/Azure → retrieve → generate |
| "optimize LLM prompt for ABAP" | sap-llm-engineering | evaluate → optimize prompt → retry |

---

## Project Objects

### Skills (85 — v5.0.0)

- abap
- abap-cloud
- abap-cloud-migration
- abap-code-patterns
- abap-code-review
- abap-sql-amdp
- abap-unit-testing
- abapgit
- arc-1-skills
- atc-cloudification
- authorization-iam
- badi-enhancement
- btp-abap-environment
- btp-best-practices
- btp-build-work-zone
- btp-business-application-studio
- btp-cias
- btp-cloud-foundry
- btp-cloud-identity
- btp-cloud-logging
- btp-cloud-platform
- btp-cloud-transport-management
- btp-connectivity
- btp-developer-guide
- btp-diagram-generator
- btp-integration-suite
- btp-job-scheduling
- btp-master-data-integration
- btp-service-manager
- cds-view-entities
- claude-abap-skills
- clean-abap
- cpi-iflow-development
- karpathy-guidelines
- odata
- odata-abap
- rap
- rap-business-events
- released-abap-classes
- run-sap-router-skill
- sap-ai-core
- sap-api-policy
- sap-api-style
- sap-bapi-integration
- sap-btp-audit-log
- sap-btp-credential-store
- sap-btp-devops
- sap-btp-document-mgmt
- sap-btp-feature-flags
- sap-btp-html5-repo
- sap-btp-kyma
- sap-btp-launchpad
- sap-btp-saas
- sap-build
- sap-cap
- sap-claude-skills
- sap-cloud-sdk-ai
- sap-code-search
- sap-commerce-skill
- sap-crew-analysis
- sap-datasphere
- sap-datasphere-plugin
- sap-dependency-security
- sap-fiori-apps-reference
- sap-fiori-tools
- sap-gui-scripting
- sap-gui-web-enrich
- sap-hana-cli
- sap-hana-cloud-data-intelligence
- sap-hana-ml
- sap-hana-sqlscript
- sap-llm-engineering
- sap-rap-gen
- sap-rpt1
- sap-sac-custom-widget
- sap-sac-planning
- sap-sac-scripting
- sap-sac-test-automation
- sap-self-learn
- sap-skills
- sap-transport-gate
- sap-transport-management
- sap-workflow-pipeline
- sapui5-framework
- superclaude-for-sap

85 skills total (v5.0.0). Covers: ABAP Core, BTP, CDS/RAP, OData, CPI, HANA, SAC, Fiori/UI5, Datasphere, Workflow, AI/LLM, Code Review, Transport.

### MCPs (35 MCPs (+18 planned))

**Configured (35):** arc-1, aibap, mcp-abap-adt, mcp-sap-gui, mcp-sap-gui-kts, sapgui-mcp-go, mcp-sap-notes, btp-mcp, odata-mcp-proxy, btp-sap-odata-to-mcp, plugin:ui5:ui5-mcp-server, plugin:sap-fiori-mcp-server:fiori-mcp, plugin:mdk-mcp:mdk-mcp, plugin:cds-mcp:cds-mcp, pinecone-rag, supabase-rag, sf-mcp, sap-rfc-mcp-server, azure-ai-search, sap-pi-mcp, bw-modeling-mcp, erpl-adt, odata-mcp-go, cloud-alm-itsm, datasphere-mcp, steampunk-mcp, sapient-mcp, sap-cpi, cf-cli-mcp, sap-api-management, mcp-integration-suite, ci-mcp-server, abap-mcp, mcp-calm-server, sap-transport-mcp

**Planned / Roadmap (18):** mcp-abap-abap-adt-api, dassian-adt, adt-ls, sapgui-mcp, sap-gui-mcp-jduncan, cpi-mcp-server, mcp-ci-python, btp-is-ci-mcp-server, sap-cpi-mcp-backup, cap-mcp-plugin, hana-mcp-server, vibing-steampunk, sap-mcp, abap-mcp-adt-powerup, mcp-hub, sap-ai-mcp-servers, sap-mcp-config, mcp-sap-docs

### CLIs (15 — v5.0.0)

- `abap_serializer.py`
- `btp_diagram.py`
- `check_gui_scripting.py`
- `cpi_client.py`
- `cpi_iflow_packager.py`
- `fallback_engine.py`
- `hdi_lint.py`
- `healthcheck.py`
- `memory_manager.py`
- `rag_ingest.py`
- `sap_router.py`
- `self_learn.py`
- `template_repo.py`
- `xls_to_bapi.py`
- `zrouter_bootstrap.py`

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
python scripts/abap_serializer.py package --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/

# 3. Create Function Module
aibap: create_object(type="FUGR", name="ZROUTER")
aibap: create_object(type="FUNC", name="ZROUTER_DISPATCH_FM", function_group="ZROUTER")

# 4. Activate + test
aibap: activate_objects(["ZCL_ZROUTER_DISPATCH","CX_ZROUTER","ZROUTER_DISPATCH_FM"])
python scripts/sap_router.py route --action MM_CREATE_MATERIAL --functional --use-zrouter
```
