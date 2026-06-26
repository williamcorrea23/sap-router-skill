---
name: sap-router-skill
description: >-
  Direct SAP development orchestrator — verifies ADT connection, checks
  project objects, routes to ZROUTER or ADT MCP. 68 domain skills, 6 CLIs,
  11 public SAP MCPs, 4 ABAP templates. Use for any SAP task.
---

# SAP Router — Direct

**When invoked: verify first, then act. Always start with Step 0.**

---

## Step 0 — System Check (RUN FIRST)

Before ANY operation, verify what's available:

```
1. ADT CONNECTION
   → arc-1: SAPDiagnose or aibap: get_object_info(name="ZROUTER")
   → Read .env / systems.json for host, client, user
   → Report: "Connected to S4H DEV (192.168.1.100:8000, client 100)"

2. PROJECT OBJECTS
   → Check templates/ : 4 ABAP templates (ZROUTER_DISPATCH, REPL_V2, DB_TABLES, CODE_SEARCH)
   → Check scripts/   : 6 CLIs (sap_router, memory_manager, xls_to_bapi, template_repo, abap_serializer, cpi_iflow_packager)
   → Check packages/  : samples ready for deploy

3. REPOSITORY CONTEXT
   → Read AGENTS.md for routing rules
   → Read .mcp.json for available MCPs
   → Read SKILL.md for skill dispatch
```

---

## Step 1 — What to Do

Answer with a single decision + command:

| User says | Route | Execute |
|---|---|---|
| "read ZCL_*" / "get source" | ADT direct | `arc-1: SAPRead(uri=".../source/main")` |
| "write/activate Z*" | ADT direct | `arc-1: SAPWrite → SAPActivate` |
| "create material/order/BAPI" | ZROUTER RFC | `python scripts/sap_router.py route --action MM_CREATE_MATERIAL` |
| "search ABAP code" | ADT direct | `arc-1: SAPSearch(query="...")` |
| "search ABAP code regex" | ZROUTER RFC | `sap_router.py route --action BASIS_CODE_SEARCH` |
| "create CPI iFlow" | CLI + deploy | `cpi_iflow_packager.py template` then `sap-cpi deploy` |
| "review ABAP / lint" | npm | `npm run abap:review` |
| "debug ABAP errors" | Analysis | `read source → analyze with clean-abap + sap-crew-analysis` |
| "transport request" | ADT direct | `aibap: create_transport → release_transport` |
| "CSV to BAPI" | CLI offline | `xls_to_bapi.py convert` |
| "serialize ABAP" | CLI offline | `abap_serializer.py package` |

---

## Step 2 — Execute

Run the command. Show the result. No fluff.

### ADT Direct Commands

```
arc-1 SAPRead     → read source, metadata, CDS, tables
arc-1 SAPWrite    → create/update/delete source
arc-1 SAPActivate → activate single or batch objects
arc-1 SAPSearch   → object search + full-text
arc-1 SAPTransport → list, create, release transport
aibap get_source  → read with batch support (arrays of URIs)
aibap syntax_check → check without saving
aibap run_unit_tests → execute ABAP Unit
```

### ZROUTER RFC Commands

```
MM:   CREATE_MATERIAL GET_MATERIAL CREATE_PO CHANGE_PO
SD:   CREATE_ORDER CHANGE_ORDER CREATE_INVOICE CREATE_DELIVERY
FI:   POST_DOCUMENT CHECK_ACCOUNTS REVERSE_DOCUMENT
QM:   CREATE_INSPECTION RECORD_RESULTS
PP:   CREATE_ORDER CONFIRM_ORDER READ_BOM READ_ROUTING
WM:   GOODS_MOVEMENT CREATE_TO
CO:   CREATE_INTERNAL_ORDER ACTIVITY_ALLOC
HCM:  READ_EMPLOYEE CREATE_INFOTYPE
BASIS: CREATE_REQUEST RELEASE_REQUEST ST22_SCAN CODE_ANALYSIS CODE_SEARCH
```

### CLI Quick Start

```bash
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL
python scripts/xls_to_bapi.py convert --input data.csv --module MM --action CREATE_MATERIAL
python scripts/template_repo.py seed
python scripts/abap_serializer.py package --source file.abap --name ZCL_FOO --type CLAS --output out/
python scripts/cpi_iflow_packager.py template --name my-flow --output my-flow.zip
npm run abap:lint
npm run abap:review
```

---

## Project Objects Reference

### ABAP Templates (4)

| Template | What It Is |
|---|---|
| `templates/ZROUTER_DISPATCH.abap` | Full framework — exception class, 3 interfaces, 4 infra classes, 9 module handlers, dispatcher, batch, RFC FM |
| `templates/ZCL_ABAP_REPL_V2.abap` | SICF HTTP handler — GENERATE SUBROUTINE POOL eval, X-API-KEY auth, CSRF |
| `templates/ZROUTER_DB_TABLES.abap` | 5 DDIC tables — template header, code body, placeholders, packages, assignments |
| `templates/ZROUTER_CODE_SEARCH.abap` | abap-code-search-tools wrapper — 3 BASIS handler actions, 12 object types |

### Python CLIs (6)

| CLI | Purpose |
|---|---|
| `sap_router.py` | Action routing: ADT vs ZROUTER RFC vs sf-mcp |
| `memory_manager.py` | MEMORY.md session context lifecycle |
| `xls_to_bapi.py` | CSV/XLSX → BAPI JSON (29 actions, 9 modules) |
| `template_repo.py` | ABAP template repo with {{placeholders}} |
| `abap_serializer.py` | .nugg / abapGit / ZDOWNLOAD XML packer |
| `cpi_iflow_packager.py` | CPI iFlow ZIP create/validate/extract |

### Public SAP MCPs (11)

`arc-1` (12 tools), `aibap` (69 tools), `mcp-abap-adt` (13 tools), `mcp-sap-notes` (2 tools), `btp-mcp` (7 entities), `odata-mcp-proxy` (32 entities), `btp-sap-odata-to-mcp` (3 tools), `ui5` (10 tools), `fiori-mcp` (8 tools), `mdk-mcp` (5 tools), `cds-mcp` (2 tools)

### Skills (68)

`abap` `abap-cloud` `abap-cloud-migration` `abap-code-patterns` `abap-sql-amdp` `abap-unit-testing` `abapgit` `atc-cloudification` `authorization-iam` `badi-enhancement` `btp-abap-environment` `btp-best-practices` `btp-build-work-zone` `btp-business-application-studio` `btp-cias` `btp-cloud-identity` `btp-cloud-logging` `btp-cloud-platform` `btp-cloud-transport-management` `btp-connectivity` `btp-developer-guide` `btp-diagram-generator` `btp-integration-suite` `btp-job-scheduling` `btp-master-data-integration` `btp-service-manager` `cds-view-entities` `clean-abap` `cpi-iflow-development` `odata` `odata-abap` `rap` `rap-business-events` `released-abap-classes` `run-sap-router-skill` `sap-ai-core` `sap-api-style` `sap-bapi-integration` `sap-btp-audit-log` `sap-btp-credential-store` `sap-btp-devops` `sap-btp-document-mgmt` `sap-btp-feature-flags` `sap-btp-html5-repo` `sap-btp-kyma` `sap-btp-launchpad` `sap-btp-saas` `sap-build` `sap-cap` `sap-cloud-sdk-ai` `sap-code-search` `sap-crew-analysis` `sap-datasphere` `sap-dependency-security` `sap-fiori-apps-reference` `sap-fiori-tools` `sap-hana-cli` `sap-hana-cloud-data-intelligence` `sap-hana-ml` `sap-hana-sqlscript` `sap-rap-gen` `sap-rpt1` `sap-sac-custom-widget` `sap-sac-planning` `sap-sac-scripting` `sap-sac-test-automation` `sap-transport-management` `sapui5-framework`

---

## Install ZROUTER on SAP (6 Steps)

```bash
# 1. Create package
aibap: create_object(type="DEVC", name="ZROUTER")

# 2. Create DDIC data elements (19)
aibap: create_object(type="DTEL", name="ZROUTER_TMPL_ID")

# 3. Create DDIC tables (5)
aibap: create_object(type="TABL", name="ZROUTER_TMPL_HD")

# 4. Deploy ABAP classes
python scripts/abap_serializer.py package --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/
# Pull deploy/abapgit/ into SAP via abapGit or arc-1 SAPWrite directly

# 5. Create Function Group + FM
aibap: create_object(type="FUGR", name="ZROUTER")
aibap: create_object(type="FUNC", name="ZROUTER_DISPATCH_FM", function_group="ZROUTER")

# 6. Activate + test
aibap: activate_objects(["ZCL_ZROUTER_DISPATCH","CX_ZROUTER","ZROUTER_DISPATCH_FM"])
aibap: syntax_check(["ZCL_ZROUTER_DISPATCH","ZROUTER_DISPATCH_FM"])
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
# → "ZROUTER RFC"
```
