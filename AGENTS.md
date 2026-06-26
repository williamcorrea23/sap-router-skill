# SAP Router Orchestrator — Agent Instructions

> **Codex / OpenAI / any agent host**: this file is the entry point.
> Claude Code uses `.claude/skills/run-sap-router-skill/SKILL.md`.
> Antigravity uses `.gemini/skills/run-sap-router-skill/SKILL.md`.
> All three point to the same `driver.py`.

## What this project is

Three standalone Python 3 CLIs — no live SAP system, no network, no
credentials required. Everything runs offline:

| Script | Purpose |
|---|---|
| `scripts/sap_router.py` | Routing engine: ADT vs ZROUTER RFC vs sf-mcp |
| `scripts/memory_manager.py` | Session context file (MEMORY.md) lifecycle |
| `scripts/xls_to_bapi.py` | CSV/XLSX → BAPI JSON payload converter |
| `scripts/template_repo.py` | Offline ABAP template repository with `{{placeholders}}` |
| `scripts/abap_serializer.py` | Multi-format ABAP packer: .nugg, abapGit, ZDOWNLOAD XML |

## Run / verify

```bash
python .claude/skills/run-sap-router-skill/driver.py
# Exit 0 = all 44 checks passed. No project files modified.
```

Requires Python 3.8+. No packages needed for CSV; `pip install openpyxl`
for XLSX support only.

## Routing rules

| Action contains | Destination |
|---|---|
| `code_search`, `read_source`, `search_object`, `syntax_check`, `where_used`, `get_deps` | ARC-1 ADT |
| `sf_*` prefix | sf-mcp (OData) |
| anything else | ZROUTER RFC (ZROUTER_DISPATCH_FM) |

## Memory session commands

```bash
python scripts/memory_manager.py init   --input MEMORY.md --sys S4H --client 100 --env DEV --usr DEVELOPER
python scripts/memory_manager.py add    --input MEMORY.md --module MM --action-name CreateMaterial --status OK
python scripts/memory_manager.py verify --input MEMORY.md
python scripts/memory_manager.py compact --input MEMORY.md
```

Caps: 20 active blocks max, 100 lines total. Older blocks auto-archive.

## XLS converter commands

```bash
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL
python scripts/xls_to_bapi.py convert  --input data.csv  --module MM --action CREATE_MATERIAL
```

## Action-to-BAPI mapping (26 actions / 9 modules)

| Module | Action | Background BAPI/FM | BAPI Params |
|---|---|---|---|
| MM | CREATE_MATERIAL | `BAPI_MATERIAL_SAVEDATA` | BAPIMATHEAD + MARA/MARAX + MARC/MARCX + MAKT table |
| MM | GET_MATERIAL | `BAPI_MATERIAL_GETALL` | MATNR → data + return |
| MM | CREATE_PO | `BAPI_PO_CREATE1` | BAPIMEPOHEADER/X + ITEM/X + ACCOUNT + COND |
| MM | CHANGE_PO | `BAPI_PO_CHANGE` | BAPIMEPOHEADER/X + ITEM/X + POSCHEDULE |
| SD | CREATE_ORDER | `BAPI_SALESORDER_CREATEFROMDAT2` | BAPISDHD1/X + ORDER_ITEMS_IN + PARTNERS + SCHEDULES |
| SD | CHANGE_ORDER | `BAPI_SALESORDER_CHANGE` | SALESDOCUMENT + ORDER_HEADER_IN/X + ITEM/X |
| SD | CREATE_INVOICE | `BAPI_BILLINGDOC_CREATEMULTIPLE` | BILLINGDATAIN (BAPIVBRK) + CONDITIONDATAIN |
| SD | CREATE_DELIVERY | `BAPI_OUTB_DELIVERY_CREATE_SLS` | SALES_ORDER_ITEMS + SHIP_POINT |
| FI | POST_DOCUMENT | `BAPI_ACC_DOCUMENT_POST` | BAPIACHE09 + ACCOUNTGL + ACCOUNTPAYABLE + ACCOUNTRECEIVABLE + ACCOUNTTAX |
| FI | CHECK_ACCOUNTS | `BAPI_GL_GETACCOUNTSALDO` | ACCOUNT + COMP_CODE + FISCAL_YEAR |
| FI | REVERSE_DOCUMENT | `BAPI_ACC_DOCUMENT_REV_POST` | BAPIACREV (OBJ_KEY + COMP_CODE + REASON_REV) |
| QM | CREATE_INSPECTION | `CO_QM_INSPECTION_LOT_CREATE` | I_MATERIAL + I_WERK + I_INSP_TYPE |
| QM | RECORD_RESULTS | `BAPI_INSPOPER_RECORDRESULTS` | INSPLOT + INSPOPER + CHAR_RESULTS table |
| PP | CREATE_ORDER | `BAPI_PRODORD_CREATE` | ORDERDATA (BAPI_PP_ORDER_CREATE) |
| PP | CONFIRM_ORDER | `BAPI_PRODORDCONF_CREATE_TT` | TIMETICKETS table (BAPI_PP_TIMETICKET) |
| PP | READ_BOM | `CS_BOM_EXPL_MAT_V2` | MATNR + WERKS + CAPID → STB table |
| PP | READ_ROUTING | `BAPI_ROUTING_GETDETAIL` | MATERIAL + PLANT + ROUTING_GROUP |
| WM | GOODS_MOVEMENT | `BAPI_GOODSMVT_CREATE` | GM_HEAD_01 + GM_CODE + GM_ITEM_CREATE table |
| WM | CREATE_TO | `L_TO_CREATE_SINGLE` | I_LGNUM + I_BWLVS + I_MATNR + source/dest bins |
| CO | CREATE_INTERNAL_ORDER | `BAPI_INTERNALORDER_CREATE` | I_MASTER_DATA (BAPI2075_7) |
| CO | ACTIVITY_ALLOC | `BAPI_CO_ALLOCACTUALS` | CONTROLLINGAREA + sender/receiver |
| HCM | READ_EMPLOYEE | `BAPI_EMPLOYEE_GETDATA` | EMPLOYEE_ID + INFOTYPE |
| HCM | CREATE_INFOTYPE | `BAPI_EMPLOYEE_ENQUEUE` + `PA_INFOTYPE_INSERT` | EMPLOYEE_ID + INFOTYPE + subtype + dates |
| BASIS | CREATE_REQUEST | `TR_INSERT_REQUEST_WITH_TASKS` | IV_TYPE + IV_TEXT → EV_REQUEST |
| BASIS | RELEASE_REQUEST | `TR_RELEASE_REQUEST` | IV_TRKORR |
| BASIS | ST22_SCAN | `SELECT FROM SNAP` | SNAP.DATUM range filter |
| BASIS | CODE_ANALYSIS | `TRINT_INSPECT_OBJECTS` | IV_MODE + IT_E071 objects table |
| BASIS | CODE_SEARCH | `ZCL_ADCOSET_SEARCH_ENGINE` | query + mode (STRING/REGEX/PCRE) + object_type + package + max_results |
| BASIS | CODE_SEARCH_STATS | `ZCL_ADCOSET_SEARCH_ENGINE` | package + owner → counts per object type |
| BASIS | CODE_SEARCH_ADT | `ZCL_ADCOSET_SEARCH_ENGINE` + ADT URIs | Same as CODE_SEARCH + build_adt_uri for each hit |

All functional actions route to ZROUTER RFC. ADT ops and `code_search` go to ARC-1 ADT. `sf_*` go to sf-mcp.

## Template repository commands

```bash
python scripts/template_repo.py init                                                  # Create blank repo
python scripts/template_repo.py seed                                                  # Populate 9 starter templates
python scripts/template_repo.py list                                                  # List all templates
python scripts/template_repo.py add --file template.abap --module MM --action FOO     # Import from ABAP file
python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL --values '{"HEADER":"h"}'  # Substitute placeholders
python scripts/template_repo.py export --template MM_CREATE_MATERIAL --format json    # Export for abapGit/nugget
```

## ABAP serializer commands

```bash
python scripts/abap_serializer.py generate --source file.abap --name ZCL_FOO --type CLAS --format nugg --output out/
python scripts/abap_serializer.py generate --source file.abap --name ZCL_FOO --type CLAS --format abapgit --output out/
python scripts/abap_serializer.py package  --source file.abap --name ZCL_FOO --type CLAS --output out/  # All 3 formats
python scripts/abap_serializer.py extract  --input file.nugg --output out/
python scripts/abap_serializer.py split    --source multi_class.abap --output out/
python scripts/abap_serializer.py list-formats
```

## ZROUTER_DISPATCH v2 additions

- `zcl_zrouter_handler_abstract=>evaluate_expression` uses `GENERATE SUBROUTINE POOL` + `PERFORM` for dynamic ABAP expression evaluation at runtime. Available in all handler subclasses.
- `templates/ZCL_ABAP_REPL_V2.abap` — improved SICF REPL with `/UI2/CL_JSON`, optional X-API-KEY, CSRF header check, `mode: "expr"` for lightweight `GENERATE SUBROUTINE POOL` eval vs `mode: "full"` for WRITE-capturing `SUBMIT`.

## Key gotchas

- Template row 2 = field descriptions — **not** valid data row. Replace before converting.
- `memory_manager add` auto-inits a missing MEMORY.md silently with defaults.
- `route` is a classifier, not a validator — unknown actions silently fall to ZROUTER.
- **`template_repo.py` works offline** — resolves placeholders via Python string substitution. ABAP runtime eval uses `GENERATE SUBROUTINE POOL` (see ZROUTER_DISPATCH v2).
- **`abap_serializer.py` `_class_to_type`** auto-detects from name prefix: `ZCL_`→CLAS, `ZIF_`→INTF, `ZCX_`→CLAS, other `Z*`→PROG. Use explicit `--type` to override.
