---
name: sap-router-skill
description: >-
  Master orchestrator for SAP ABAP/BTP development. Routes actions across
  55 domain skills, 6 Python CLIs, 17 MCP servers, and 4 ABAP templates.
  Covers ABAP, RAP, CDS, BTP, CPI, CAP, UI5, Fiori, HANA, Datasphere,
  SAC, AI Core, and security. Use for any SAP development task — this
  skill dispatches to the correct sub-skill, MCP, or CLI automatically.
---

# SAP Router Skill — Global Skill

Master orchestrator for SAP development. One entry point → 55 domain skills.

## Interactive Decision Menu

When a user asks about SAP operations, walk through this decision tree
and present the options clearly before executing.

### Step 1 — What does the user want to do?

```
USER REQUEST
    │
    ├── "Read/view ABAP source code"
    │     → Use ADT MCP DIRECT (fastest, read-only)
    │     → MCP: arc-1 SAPRead / aibap get_source / mcp-abap-adt GetProgram
    │     → Command: "arc-1: read class ZCL_FOO from DEV system"
    │
    ├── "Write/modify ABAP code"
    │     → Use ADT MCP DIRECT (lock/unlock handled automatically)
    │     → MCP: arc-1 SAPWrite / aibap set_source_from_file / patch_source
    │     → Command: "arc-1: write to ZCL_FOO, activate after"
    │
    ├── "Execute BAPI / RFC / functional operation"
    │     → Use ZROUTER RFC (dispatcher handles auth, logging, batching)
    │     → Route: sap_router.py → ZROUTER_DISPATCH_FM
    │     → Command: "python scripts/sap_router.py route --action MM_CREATE_MATERIAL"
    │     → Or: "hermes-crewai sap_bapi_call BAPI_MATERIAL_SAVEDATA ..."
    │
    ├── "Create CPI iFlow / Groovy script"
    │     → Use cpi-iflow-development skill (offline) + sap-cpi MCP (deploy)
    │     → Command: "python scripts/cpi_iflow_packager.py template --name my-flow"
    │     → Deploy: "sap-cpi: deploy_artifact my-flow"
    │
    ├── "Search ABAP code across system"
    │     → ADT path: arc-1 SAPSearch / aibap search_objects
    │     → ZROUTER path: BASIS handler CODE_SEARCH (abap-code-search-tools)
    │     → Quick: code_search → ARC-1 ADT (built-in)
    │     → Deep: BASIS_CODE_SEARCH → ZROUTER RFC (regex, PCRE, 12 types)
    │
    ├── "Code review / quality check"
    │     → Offline: npm run abap:review (abaplint, no SAP needed)
    │     → Live: aibap run_atc_check + syntax_check
    │     → Deep: sap-crew-analysis (7 agents, background)
    │
    ├── "Transport / deploy to production"
    │     → Review first: sap-transport-gate skill (10-dimension risk)
    │     → Execute: aibap release_transport / arc-1 SAPTransport
    │     → ABAP Cloud: gCTS via arc-1 SAPGit
    │
    ├── "Convert Excel/CSV to BAPI calls"
    │     → Offline: xls_to_bapi.py (no SAP needed)
    │     → Command: "python scripts/xls_to_bapi.py convert --input data.csv --module MM --action CREATE_MATERIAL"
    │     → Then route: ZROUTER RFC for actual BAPI execution
    │
    └── "Debug / troubleshoot ABAP error"
        → Syntax: aibap syntax_check (instant, no side effects)
        → Runtime: aibap list_short_dumps + get_short_dump_details
        → Deep: sap-crew-analysis (multi-agent, finds root cause)
```

### Step 2 — ZROUTER vs ADT Direct: Decision Table

| Scenario | Use ZROUTER RFC | Use ADT MCP Direct | Reason |
|---|---|---|---|
| Read ABAP source (1 object) | ❌ | ✅ arc-1/aibap | Lighter, faster, no FM overhead |
| Read ABAP source (batch 50+ objects) | ❌ | ✅ aibap batch mode | ADT batch is efficient |
| Write ABAP source | ❌ | ✅ arc-1/aibap | Direct lock/unlock, syntax-aware |
| Execute BAPI (single) | ✅ | ❌ | ZROUTER handles auth, log, COMMIT pattern |
| Execute BAPI (batch 100+) | ✅ | ❌ | ZCL_ZROUTER_BATCH atomicity |
| Create material / sales order | ✅ | ❌ | Business logic + BAPI_TRANSACTION_COMMIT |
| Search ABAP code (quick) | ❌ | ✅ arc-1 SAPSearch | ADT indexed search is faster |
| Search ABAP code (regex/PCRE) | ✅ | ❌ | ZCL_ADCOSET_SEARCH_ENGINE in ABAP |
| CPI deploy / monitor | ❌ | ✅ sap-cpi MCP | CPI tenant direct connection |
| Create transport request | ✅ | ✅ Either works | aibap for interactive; ZROUTER for batch/API |
| Release transport | ❌ | ✅ aibap release_transport | Interactive safety gate |
| Code review / ATC check | ❌ | ✅ aibap run_atc_check | Closer to real SAP ATC |
| ABAP Unit tests | ❌ | ✅ aibap run_unit_tests | Direct test execution |
| Generate ABAP code from template | ✅ | ❌ | template_repo.py + evaluate_expression |
| CSV → BAPI (offline prep) | N/A | N/A | xls_to_bapi.py runs locally |

### Step 3 — Command Cheat Sheet

```bash
# ═══ ADT MCP DIRECT (read/write ABAP objects) ═══

# Read source
arc-1: SAPRead  "/sap/bc/adt/oo/classes/zcl_material_handler/source/main"
aibap: get_source(object_uri="/sap/bc/adt/oo/classes/zcl_material_handler/source/main")
mcp-abap-adt: GetClass("ZCL_MATERIAL_HANDLER")

# Write source
arc-1: SAPWrite(uri=".../source/main", content="<new source>")
arc-1: SAPActivate(uri=".../source/main")
aibap: patch_source(object_uri="...", edits=[...])
aibap: activate_object(object_uri="...")

# Search objects
arc-1: SAPSearch(query="MATERIAL", type="CLAS")
aibap: search_objects(query="*MATERIAL*", type="CLAS")

# Test & quality
aibap: syntax_check(["ZCL_MATERIAL_HANDLER"])
aibap: run_atc_check(object_uri="...")
aibap: run_unit_tests(["ZCL_MATERIAL_HANDLER"])

# Transport
aibap: create_transport(text="Bugfix material creation")
aibap: release_transport(trkorr="S4HK900123")

# ═══ ZROUTER RFC (BAPI/functional operations) ═══

# Route check
python scripts/sap_router.py route --action MM_CREATE_MATERIAL  # → ZROUTER RFC
python scripts/sap_router.py route --action BASIS_CODE_SEARCH     # → ZROUTER RFC
python scripts/sap_router.py route --action code_search           # → ARC-1 ADT
python scripts/sap_router.py route --action sf_read_employee      # → sf-mcp

# Execute BAPI (via hermes-crewai or ZROUTER FM)
hermes-crewai: sap_bapi_call(bapi_name="BAPI_MATERIAL_SAVEDATA", params="{...}")
# Or via ZROUTER_DISPATCH_FM called from any RFC-capable MCP

# CSV → BAPI
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL
python scripts/xls_to_bapi.py convert  --input data.csv  --module MM --action CREATE_MATERIAL

# ═══ CPI ═══

# Package iFlow
python scripts/cpi_iflow_packager.py template --name my-flow --output my-flow.zip
python scripts/cpi_iflow_packager.py create --name my-flow --flow flow.xml --scripts script/*.groovy

# Deploy & monitor
sap-cpi: deploy_artifact(artifactId="my-flow", artifactType="IntegrationFlow")
sap-cpi: get_failed_messages(top=20, artifactName="my-flow")

# ═══ ABAP Serialization ═══

# Package for abapGit / nugget / ZDOWNLOAD
python scripts/abap_serializer.py package --source file.abap --name ZCL_FOO --type CLAS --output exports/
python scripts/abap_serializer.py split   --source multi_class.abap --output split/

# ═══ Peer Review ═══

# Static lint
npm run abap:lint
npm run abap:review:ci

# Deep AI analysis (7 agents, background)
python ../sap-crew-agent/sap-crew-agent/sap_crew/run.py --mode quick "Analyze ZCL_MATERIAL_HANDLER for bugs"
```

## Quick Dispatch

```
User request → sap-router-orchestrator (this skill)
  ├── ABAP code?        → abap-code-patterns, clean-abap, abap-*
  ├── RAP/CDS?          → rap, cds-view-entities, rap-business-events
  ├── BTP platform?     → btp-* (15 skills)
  ├── CPI/integration?  → btp-integration-suite, sap-cpi MCP
  ├── ABAP object CRUD? → hermes-crewai sap_adt_cli, arc-1, aibap
  ├── Fiori/UI5?        → sapui5-framework, sap-fiori-tools
  ├── CAP app?          → sap-cap, cds-mcp
  ├── HANA/SQLScript?   → sap-hana-*, abap-sql-amdp
  ├── SAC/Datasphere?   → sap-sac-*, sap-datasphere
  ├── AI/ML?            → sap-ai-core, sap-cloud-sdk-ai, sap-hana-ml
  ├── Transport?        → sap-transport-management, sap-transport-gate
  ├── Code search?      → sap-code-search, ZCL_ADCOSET_SEARCH_ENGINE
  ├── BAPI execution?   → sap-bapi-integration, xls_to_bapi.py
  ├── Code review?      → abap-code-review (Hermes), clean-abap
  ├── Deep ABAP debug?  → sap-crew-analysis (7 agents, 4-phase, background)
  ├── Security audit?   → sap-dependency-security, authorization-iam
  └── CLI/test?         → sap_router.py, memory_manager.py, driver.py
```

## All 55 Skills by Domain

| # | Skill | Domain | Purpose |
|---|---|---|---|
| 1 | `abap-code-patterns` | ABAP Core | BAPI/RFC, GENERATE SUBROUTINE POOL, DDIC, Clean ABAP |
| 2 | `clean-abap` | ABAP Core | SAP Clean ABAP Style Guide rules |
| 3 | `released-abap-classes` | ABAP Core | C1/C2/C3 release contracts, XCO, cl_abap* |
| 4 | `abapgit` | ABAP Core | Git-based ABAP version control, CI/CD |
| 5 | `abap-sql-amdp` | ABAP Core | AMDP classes, CDS table functions, HANA SQLScript |
| 6 | `abap-unit-testing` | ABAP Core | ABAP Unit, test doubles, CDS test framework |
| 7 | `badi-enhancement` | ABAP Core | BAdI, enhancement spots, customer exits |
| 8 | `authorization-iam` | ABAP Core | AUTHORITY-CHECK, PFCG, IAM, DCL |
| 9 | `atc-cloudification` | ABAP Core | ATC checks, quality gates, cloud readiness |
| 10 | `rap` | RAP | RESTful ABAP Programming — managed/unmanaged |
| 11 | `rap-business-events` | RAP | Event-driven RAP, Event Mesh integration |
| 12 | `cds-view-entities` | CDS | DEFINE VIEW ENTITY, annotations, MDE |
| 13 | `abap-cloud` | Cloud | Steampunk, ABAP Cloud restrictions, released APIs |
| 14 | `abap-cloud-migration` | Cloud | ATC cloud readiness, Dynpro→Fiori migration |
| 15 | `odata-abap` | OData | CDS-exposed OData, SEGW, V4 Gateway |
| 16 | `sap-bapi-integration` | Integration | BAPI discovery, BAPIRET2, 9 modules |
| 17 | `btp-abap-environment` | BTP | BTP ABAP Environment service instance management |
| 18 | `btp-best-practices` | BTP | BTP architecture patterns, runtime selection |
| 19 | `btp-build-work-zone` | BTP | SAP Build Work Zone configuration |
| 20 | `btp-business-application-studio` | BTP | BAS dev spaces, extensions, terminal |
| 21 | `btp-cias` | BTP | Cloud Integration Automation Service |
| 22 | `btp-cloud-logging` | BTP | OpenTelemetry, Kibana, structured logging |
| 23 | `btp-cloud-identity` | BTP | IAS, IPS, AMS, XSUAA migration |
| 24 | `btp-cloud-platform` | BTP | BTP cockpit, subaccounts, entitlements |
| 25 | `btp-cloud-transport-management` | BTP | CTM, gCTS, transport nodes, import queues |
| 26 | `btp-connectivity` | BTP | Cloud Connector, principal propagation, mTLS |
| 27 | `btp-developer-guide` | BTP | CAP, ABAP Cloud, CI/CD, monitoring |
| 28 | `btp-integration-suite` | BTP | CPI, API Management, TPM, Event Mesh |
| 29 | `btp-job-scheduling` | BTP | Cron jobs, REST endpoint scheduling |
| 30 | `btp-master-data-integration` | BTP | MDI, master data harmonization |
| 31 | `btp-service-manager` | BTP | Service instances, bindings, keys |
| 32 | `sapui5-framework` | UI5 | Async loading, OData binding, TypeScript |
| 33 | `sap-fiori-tools` | UI5 | Fiori Elements, manifest configuration |
| 34 | `sap-fiori-apps-reference` | UI5 | App library, activation, Spaces and Pages |
| 35 | `sap-cap` | CAP | CDS model, service handlers, Fiori, MTA |
| 36 | `sap-hana-sqlscript` | HANA | Procedures, table functions, CE functions |
| 37 | `sap-hana-cli` | HANA | hdbsql, Database Explorer |
| 38 | `sap-hana-ml` | HANA | PAL, APL, HANA ML Python client |
| 39 | `sap-ai-core` | AI | ML deployment, workflows, model serving |
| 40 | `sap-cloud-sdk-ai` | AI | LLM orchestration, RAG, document grounding |
| 41 | `sap-datasphere` | Data | Data modeling, federation, analytical models |
| 42 | `sap-sac-scripting` | Analytics | SAC scripting API, custom widgets |
| 43 | `sap-sac-planning` | Analytics | Planning models, allocations, data actions |
| 44 | `sap-sac-custom-widget` | Analytics | Web component widgets for SAC |
| 45 | `sap-sac-test-automation` | Analytics | Playwright tests for SAC |
| 46 | `sap-hana-cloud-data-intelligence` | Data | DI Cloud, data quality, lineage |
| 47 | `sap-dependency-security` | Security | Supply-chain, MCP trust, audit |
| 48 | `sap-api-style` | Standard | SAP API documentation standards |
| 49 | `btp-diagram-generator` | Infra | Mermaid/PlantUML BTP diagrams |
| 50 | `sap-rpt1` | FI/CO | Local GAAP regulatory reporting |
| 51 | `sap-code-search` | Tooling | abap-code-search-tools + ADT |
| 52 | `sap-transport-management` | Tooling | CTS, TR lifecycle, abapGit |
| 53 | `cpi-iflow-development` | CPI | Groovy scripts, iFlow ZIP, flow.xml |
| 54 | `sap-crew-analysis` | AI/QA | 7-agent background ABAP debug, 9-dim analysis |
| 55 | `run-sap-router-skill` | Tooling | Smoke driver, CLI execution |

## MCP Servers (17)

| Server | Tools | Use When |
|---|---|---|
| `hermes-crewai` | 21 (ADT, BAPI, HANA, ABAP lint, transport gate) | Any ABAP/SAP operation |
| `sap-cpi` | 11 (CPI deploy, messages, keystore) | CPI iFlow management |
| `arc-1` | 12 (SAPRead/Write/Search/Activate/Transport) | Enterprise ADT MCP |
| `aibap` | 69 (source, objects, testing, ST22, BAdI, DEBUG) | Full ABAP development |
| `mcp-abap-adt` | 13 (GetProgram, GetClass, GetTable, SearchObject) | Lightweight ADT access |
| `mcp-sap-notes` | 2 (search, fetch) | SAP Notes lookup |
| `btp-mcp` | 7 (GlobalAccount, Subaccounts, Entitlements) | BTP admin |
| `odata-mcp-proxy` | 32 entity sets (CPI admin APIs) | CPI OData operations |
| `btp-sap-odata-to-mcp` | 3 (discover, metadata, execute) | S/4HANA OData queries |
| `plugin:azure:azure` | 50+ (compute, storage, AKS, SQL, IaC) | Azure infra |
| `plugin:desktop-commander` | 20+ (shells, files, search) | Local filesystem ops |
| `plugin:ui5` | 10 (create app, linter, API ref) | UI5 development |
| `plugin:sap-fiori-mcp` | 8 (Fiori generation, modification) | Fiori apps |
| `plugin:mdk-mcp` | 5 (MDK project, deploy) | Mobile Development Kit |
| `plugin:cds-mcp` | 2 (CDS model search, docs) | CAP CDS models |
| `mobile-webapp-crew` | 17 (Flutter, adb, gradle, npm) | Mobile/web app dev |
| `sap-crew-local` | 1 (sap_crew_delegate — 7 agents, 4 modes) | Background ABAP analysis, debug, review |

## Python CLIs (6)

| CLI | Purpose | Quick Start |
|---|---|---|
| `sap_router.py` | Routing engine | `python scripts/sap_router.py route --action MM_CREATE_MATERIAL` |
| `memory_manager.py` | Session memory | `python scripts/memory_manager.py init --input MEMORY.md --sys S4H --client 100 --env DEV --usr DEV` |
| `xls_to_bapi.py` | CSV→BAPI | `python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL` |
| `template_repo.py` | Template repo | `python scripts/template_repo.py seed` |
| `abap_serializer.py` | ABAP packer | `python scripts/abap_serializer.py package --source file.abap --name ZCL_FOO --type CLAS --output out/` |

## ABAP Templates (4)

| Template | Purpose |
|---|---|
| `ZROUTER_DISPATCH.abap` | Full dispatch framework — 9 handlers, evaluate_expression, batch, FM |
| `ZCL_ABAP_REPL_V2.abap` | SICF HTTP handler with GENERATE SUBROUTINE POOL + /UI2/CL_JSON |
| `ZROUTER_DB_TABLES.abap` | 5 DDIC tables for code template repository |
| `ZROUTER_CODE_SEARCH.abap` | abap-code-search-tools integration — 3 BASIS handler actions |

## CPI iFlow Packager

```bash
python scripts/cpi_iflow_packager.py template --name my-iflow --output my-iflow.zip
python scripts/cpi_iflow_packager.py create --name my-iflow --flow flow.xml --scripts script/*.groovy --output my-iflow.zip
python scripts/cpi_iflow_packager.py validate --input my-iflow.zip
python scripts/cpi_iflow_packager.py list --input my-iflow.zip
python scripts/cpi_iflow_packager.py extract --input my-iflow.zip --output src/
```

See `cpi-iflow-development` skill for full Groovy patterns, iFlow XML structure, and CPI best practices.

## Routing Rules

| Action contains | Destination | MCP/Tool |
|---|---|---|
| `read_source`, `search_object`, `syntax_check`, `where_used`, `get_deps`, `code_search` | ARC-1 ADT | hermes-crewai sap_adt_cli / arc-1 / aibap |
| `sf_*` | sf-mcp (OData) | SuccessFactors API |
| everything else | ZROUTER RFC | ZROUTER_DISPATCH_FM → 9 module handlers |

## ZROUTER Installation via ADT MCP

Install the full ZROUTER framework on any SAP system using ADT MCP tools.
Requires: SAP NetWeaver ≥ 7.40, ADT services active (`/sap/bc/adt` in SICF),
user with `S_DEVELOP` and `S_ADT_RES` authorizations.

### Step 1: Create Package

```bash
# Via hermes-crewai ADT CLI (sap_adt_cli)
# or arc-1 SAPWrite / aibap create_object

# Check if package exists
hermes-crewai: sap_adt_cli get-package ZROUTER

# Create if missing
aibap: create_object(type="DEVC", name="ZROUTER", description="SAP Router Orchestrator")
```

### Step 2: Create DDIC Tables (5 tables)

Use `templates/ZROUTER_DB_TABLES.abap` — contains SE11-ready field definitions.

```bash
# Via aibap MCP — create table by name (DDIC activation auto-creates in DB)
aibap: create_object(type="TABL", name="ZROUTER_TMPL_HD")
aibap: create_object(type="TABL", name="ZROUTER_TMPL_CD")
aibap: create_object(type="TABL", name="ZROUTER_TMPL_PL")
aibap: create_object(type="TABL", name="ZROUTER_TMPL_PKG")
aibap: create_object(type="TABL", name="ZROUTER_TMPL_PKG_T")

# Activate all
aibap: activate_objects(["ZROUTER_TMPL_HD","ZROUTER_TMPL_CD","ZROUTER_TMPL_PL",
       "ZROUTER_TMPL_PKG","ZROUTER_TMPL_PKG_T"])
```

### Step 3: Create DDIC Data Elements

```bash
# Create data elements referenced by tables
aibap: create_object(type="DTEL", name="ZROUTER_TMPL_ID")
aibap: create_object(type="DTEL", name="ZROUTER_MODULE")
aibap: create_object(type="DTEL", name="ZROUTER_ACTION")
aibap: create_object(type="DTEL", name="ZROUTER_VERSION")
aibap: create_object(type="DTEL", name="ZROUTER_TITLE")
aibap: create_object(type="DTEL", name="ZROUTER_DESCR")
aibap: create_object(type="DTEL", name="ZROUTER_CATEG")
aibap: create_object(type="DTEL", name="ZROUTER_BOOL")
aibap: create_object(type="DTEL", name="ZROUTER_SRCSYS")
aibap: create_object(type="DTEL", name="ZROUTER_LINE_NO")
aibap: create_object(type="DTEL", name="ZROUTER_CODE_LINE")
aibap: create_object(type="DTEL", name="ZROUTER_PLACEHOLDER")
aibap: create_object(type="DTEL", name="ZROUTER_PL_DEFAULT")
aibap: create_object(type="DTEL", name="ZROUTER_PL_TYPE")
aibap: create_object(type="DTEL", name="ZROUTER_PL_DESCR")
aibap: create_object(type="DTEL", name="ZROUTER_PL_MAXLEN")
aibap: create_object(type="DTEL", name="ZROUTER_PKG_ID")
aibap: create_object(type="DTEL", name="ZROUTER_PKG_NAME")
aibap: create_object(type="DTEL", name="ZROUTER_EXPORT_FMT")
```

### Step 4: Deploy ABAP Classes via ADT Source Write

```bash
# Option A: Via aibap patch_source (line-by-line)
# Read template, split into source lines, call set_source_from_file

# Option B: Via arc-1 SAPWrite (intent-based)
arc-1: SAPWrite(object_uri="/sap/bc/adt/oo/classes/zcl_zrouter_dispatch/source/main",
       content="<source from templates/ZROUTER_DISPATCH.abap>")
arc-1: SAPActivate(object_uri="/sap/bc/adt/oo/classes/zcl_zrouter_dispatch/source/main")

# Option C: Via abapGit pull (recommended for multi-object)
# 1. Serialize templates with abap_serializer.py
python scripts/abap_serializer.py package \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output abapgit_export/
# 2. Push to Git, pull via abapGit in SAP GUI
# Or use /UI5/CL_JSON to parse and write via ADT

# Option D: Via hermes-crewai sap_adt_cli (interactive)
hermes-crewai: sap_adt_cli get-class ZCL_ZROUTER_DISPATCH  # check existence
hermes-crewai: sap_adt_cli write-source --class ZCL_ZROUTER_DISPATCH  # write
hermes-crewai: sap_adt_cli activate ZCL_ZROUTER_DISPATCH  # activate
```

### Step 5: Create Function Module

```bash
# Create function group first
aibap: create_object(type="FUGR", name="ZROUTER")

# Create function module ZROUTER_DISPATCH_FM
aibap: create_object(type="FUNC", name="ZROUTER_DISPATCH_FM",
       function_group="ZROUTER")

# Write source
arc-1: SAPWrite(object_uri="/sap/bc/adt/functions/groups/zrouter/fmodules/zrouter_dispatch_fm/source",
       content="<extract FM section from ZROUTER_DISPATCH.abap>")
```

### Step 6: Verify Installation

```bash
# Syntax check all objects
aibap: syntax_check(["ZCL_ZROUTER_DISPATCH","ZCL_ZROUTER_HANDLER_MM",
       "ZCL_ZROUTER_HANDLER_SD","ZCL_ZROUTER_HANDLER_FI",
       "ZCL_ZROUTER_HANDLER_QM","ZCL_ZROUTER_HANDLER_PP",
       "ZCL_ZROUTER_HANDLER_WM","ZCL_ZROUTER_HANDLER_CO",
       "ZCL_ZROUTER_HANDLER_HCM","ZCL_ZROUTER_HANDLER_BASIS",
       "ZROUTER_DISPATCH_FM","CX_ZROUTER"])

# Run ABAP Unit tests
aibap: run_unit_tests(["ZCL_ZROUTER_DISPATCH"])

# Verify routing works
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
# → "ZROUTER RFC"
```

### Post-Install: Seed Templates

```bash
# Populate code template repository
python scripts/template_repo.py init && python scripts/template_repo.py seed
# 12 templates ready — export as JSON for abapGit import or direct ADT write
```

## ABAP Peer Review Flow (abaplint via npm)

Pre-release ABAP code review pipeline powered by abaplint.

### Setup

```bash
npm install
# Installs abaplint + @abaplint/cli + SAP ruleset
```

### Lint Scripts (package.json)

```bash
npm run abap:lint          # Lint all ABAP in templates/ + scripts/
npm run abap:lint:fix      # Auto-fix where possible
npm run abap:lint:ci       # CI mode — fails on any finding
npm run abap:review        # Full peer review: lint + security + clean code
npm run abap:review:report # Generate HTML review report
```

### Peer Review Pipeline

```
┌─────────────────────────────────────────────────────────┐
│  1. npm run abap:lint                                    │
│     ↓                                                    │
│  2. Resolve findings (CRITICAL → HIGH → MEDIUM)         │
│     ↓                                                    │
│  3. npm run abap:lint:ci  (gate check)                   │
│     ↓                                                    │
│  4. abap-code-review skill (9-dimension analysis)        │
│     ↓                                                    │
│  5. sap-transport-gate skill (10-dimension TR gate)     │
│     ↓                                                    │
│  6. npm run abap:review:report  → sign-off document     │
└─────────────────────────────────────────────────────────┘
```

### Review Dimensions (9)

| # | Dimension | Checked by | Tools |
|---|---|---|---|
| SEC | SQL injection, dynamic code, OS calls | abaplint + manual | `abap:lint:ci` |
| AUTH | AUTHORITY-CHECK, S_DEVELOP, IAM | Manual review | abap-code-review |
| DATA | Error handling, ENQUEUE, COMMIT | abaplint rules | `abap:lint` |
| PERF | SELECT in loop, SELECT *, full scans | abaplint rules | `abap:lint` |
| STD | Deprecated stmts, hardcoding, Clean ABAP | abaplint + clean-abap | `abap:lint` |
| INTERFACE | RFC, OData, params, timeout | Manual review | abap-code-review |
| CHANGE | TR objects, shared INCLUDEs, SAP mods | Manual review | sap-transport-management |
| COMP | PII, dual-control, CDHDR/CDPOS logging | Manual review | abap-code-review |
| FUNC | Requirements coverage (needs spec) | Manual review | abap-code-review |

### CI/CD Integration

```yaml
# .github/workflows/abap-review.yml
name: ABAP Peer Review
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run abap:lint:ci
      - run: npm run abap:review:report
      - uses: actions/upload-artifact@v3
        with:
          name: abap-review-report
          path: abap-review-report.html
```

## Verified

```
Smoke tests:  50/50 passed
Python version: 3.14.4
Platform: Windows 11
Skills: 55
MCPs: 17
CLIs: 6
Templates: 4
xls_to_bapi actions: 29 (9 modules)
template_repo seeds: 12
Repos analyzed: 62/62
```
