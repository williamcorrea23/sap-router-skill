---
name: sap-router-skill
description: >-
  SAP development orchestrator v4.0 — Karpathy command format (Think→Simplify→
  Surgical→Verify), healthcheck guardian, self-learning router, caveman-compressed
  output default. 78 skills, 22 MCPs (3 GUI + 3 RAG + CPI + CF + APIM + sf-mcp + sap-rfc + 4 plugins), 10 CLIs. Routes: ADT →
  GUI (immediate) → RFC → Pipeline. RAG-ready: Pinecone, Supabase, Azure.
  Use for any SAP task.
---

# SAP Router v4.0 — Karpathy Command Format

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

2. **MCPs connected**: probes all 22 MCPs
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

If multiple BAPIs exist → present options. If SAP config unclear → ask.

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
4. BAPI batch? (create material, post document, create order...)
    │ YES → ZROUTER RFC via ZROUTER_DISPATCH_FM
    ▼
5. Spec → code? (implement specification, full workflow)
    │ YES → sap_router.py pipeline → 8 stages
    │ Stage 1: Spec Analysis → Stage 8: Transport Gate
    ▼
6. LLM optimization? (prompt engineering, eval harness)
    │ YES → sap-llm-engineering → evaluate → optimize → retry
```

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
| "create material/order" | ZROUTER RFC | BAPI → BAPIRET2 check → MM03/VA03 verify |
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

### Skills (78 — v4.0)

`abap` `abap-cloud` `abap-cloud-migration` `abap-code-patterns` **`abap-code-review`** `abap-sql-amdp` `abap-unit-testing` `abapgit` `atc-cloudification` `authorization-iam` `badi-enhancement` `btp-abap-environment` `btp-best-practices` `btp-build-work-zone` `btp-business-application-studio` **`btp-cloud-foundry`** `btp-cias` `btp-cloud-identity` `btp-cloud-logging` `btp-cloud-platform` `btp-cloud-transport-management` `btp-connectivity` `btp-developer-guide` `btp-diagram-generator` `btp-integration-suite` `btp-job-scheduling` `btp-master-data-integration` `btp-service-manager` `cds-view-entities` `clean-abap` `cpi-iflow-development` **`karpathy-guidelines`** `odata` `odata-abap` `rap` `rap-business-events` `released-abap-classes` `run-sap-router-skill` `sap-ai-core` `sap-api-policy` `sap-api-style` `sap-bapi-integration` `sap-btp-audit-log` `sap-btp-credential-store` `sap-btp-devops` `sap-btp-document-mgmt` `sap-btp-feature-flags` `sap-btp-html5-repo` `sap-btp-kyma` `sap-btp-launchpad` `sap-btp-saas` `sap-build` `sap-cap` `sap-cloud-sdk-ai` `sap-code-search` `sap-crew-analysis` `sap-datasphere` `sap-dependency-security` `sap-fiori-apps-reference` `sap-fiori-tools` `sap-gui-scripting` **`sap-gui-web-enrich`** `sap-hana-cli` `sap-hana-cloud-data-intelligence` `sap-hana-ml` `sap-hana-sqlscript` `sap-llm-engineering` `sap-rap-gen` `sap-rpt1` `sap-sac-custom-widget` `sap-sac-planning` `sap-sac-scripting` `sap-sac-test-automation` **`sap-self-learn`** **`sap-transport-gate`** `sap-transport-management` `sap-workflow-pipeline` `sapui5-framework`

**Bold** = NEW v4.0 (6 added: abap-code-review, btp-cloud-foundry, karpathy-guidelines, sap-gui-web-enrich, sap-self-learn, sap-transport-gate)

### MCPs (22 — v4.0)

**Core (HIGH):** `arc-1` `aibap`
**ADT (MEDIUM):** `mcp-abap-adt`
**GUI (3 tiers):** `mcp-sap-gui` `mcp-sap-gui-kts` `sapgui-mcp-go`
**RFC (MEDIUM):** `sap-rfc-mcp-server` (ZROUTER dispatch)
**CPI:** `sap-cpi` (iFlow deploy + monitoring)
**CF Runtime:** `cf-cli-mcp` (Cloud Foundry deploy + operations)
**APIM:** `sap-api-management` (API proxy lifecycle)
**HCM:** `sf-mcp` (SuccessFactors OData)
**BTP/OData:** `btp-mcp` `odata-mcp-proxy` `btp-sap-odata-to-mcp`
**Docs:** `mcp-sap-notes`
**Plugins:** `ui5` `fiori-mcp` `mdk-mcp` `cds-mcp`
**RAG (v4.0, pre-ready):** `pinecone-rag` `supabase-rag` `azure-ai-search`

### CLIs (10 — v4.0)

`sap_router.py` `memory_manager.py` `healthcheck.py` `self_learn.py` `fallback_engine.py` `zrouter_bootstrap.py` `xls_to_bapi.py` `template_repo.py` `abap_serializer.py` `cpi_iflow_packager.py`

---

## Install ZROUTER on SAP

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
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
```
