# SAP Router Skill — Multi-IDE Agent Instructions

> **89 skills mirrored across 4 IDEs — same SKILL.md content in each.**
>
> All skills auto-trigger by file context and keyword. See SKILL.md for master dispatch.

## Implemented v6 operating model

Canonical source is `.agents/skills` plus `.agents/registries/mcp-capabilities.json`.
Claude and Gemini skill trees are generated mirrors; Codex and Cursor reuse `.agents/skills`
through AGENTS/rules/agent assets instead of maintaining duplicate skill trees.

Generate/check IDE assets:

```bash
python scripts/generate_ide_assets.py generate --targets all
python scripts/generate_ide_assets.py check
```

Capability routing is fail-closed:

```bash
python scripts/validate_catalog.py --strict
python scripts/mcp_launcher.py list --capability sap.cpi.message.read
python scripts/mcp_launcher.py list --capability sap.apim.proxy.read
```

## Dynamic local asset discovery

Before selecting an SAP skill or MCP for a task that is not an exact static
route, query the repository-owned catalog. The search ranks canonical skills,
reviewed MCPs, and bundled snapshots together:

```bash
python scripts/source_catalog.py search "task description"
python scripts/mcp_launcher.py search --query "task description"
```

Use the highest relevant enabled/reviewed result. A bundled MCP with status
`disabled_candidate` is evidence for review, never authorization to execute it.
All bundled code lives under `bundled/`; routing does not fetch GitHub at runtime.

CPI/APIM/Fiori/UI5/CAP now route through API/CLI/plugin MCPs first and use Web UI MCP
fallbacks (`integration-suite-ui-mcp`, `apim-ui-mcp`) only when background access is blocked.
The Web UI bridge uses the logged-in browser session and does not accept credential values.

Mutating capabilities use plan/approval/commit semantics. Local approval state is handled by:

```bash
python scripts/approval_broker.py plan --capability sap.apim.proxy.deploy --target DEV
```

## What this project is

40 Python operational scripts plus Node.js review gates — no live SAP system required
credentials required. Everything runs offline.

## Routing rules (v4.2.0 — ADT-first, GUI-fallback, caveman-optimized)

Decision tree:
1. CAVEMAN DELEGATION? (fix/find/review, 1-2 files) → cavecrew-investigator/builder/reviewer
2. ADT AVAILABLE? (read_source, search, activate...) → ARC-1 / aibap / mcp-abap-adt
3. GUI FALLBACK? (SPRO, SM30, SU01, MM01, VA01...) → mcp-sap-gui (25 transactions)
4. FUNCTIONAL WRITE? (BAPI batch) → needs explicit --functional context (else needs-functional-context, NO BAPI fired); then BAPI-first / SAP GUI dispatch. ZROUTER RFC only if opted in (zrouter accept).
5. SPEC→PIPELINE? → sap_router.py pipeline (8 stages)
6. LLM / RAG? (prompt optimization, doc retrieval) → sap-llm-engineering skill + RAG routing (Pinecone, Supabase pgvector, Azure AI Search)

| Action contains | Destination |
|---|---|
| `fix`, `edit`, `rename`, `typo` | cavecrew-builder (1-2 files only) |
| `find`, `search`, `locate`, `where is` | cavecrew-investigator (60% token savings) |
| `review`, `audit`, `code review` | cavecrew-reviewer (severity-tagged) |
| `code_search`, `read_source`, `syntax_check`, `where_used`, `get_deps` | ARC-1 ADT |
| `sf_*` prefix | sf-mcp (OData) |
| `SPRO`, `SM30`, `SU01`, `PFCG`, `MM01`, `VA01`, `FB01`, etc. | SAP GUI Scripting (mcp-sap-gui) |
| `pipeline`, `spec`, `implement specification` | sap_router.py pipeline → 8 stages |
| anything else | SAP GUI scripting (mcp-sap-gui) default |

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

## Action-to-BAPI mapping (29 actions / 9 modules)

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

Functional WRITE actions need explicit --functional context (else needs-functional-context, no BAPI fired); they then dispatch BAPI-first / SAP GUI. ZROUTER RFC is opt-in only (zrouter accept) — never the default. ADT ops and `code_search` → ARC-1 ADT. `sf_*` → sf-mcp.

## RTK and Context Mode Optimization Rules (MANDATORY)

To keep token consumption low (saving 60-90% on terminal commands and 98% on tool outputs):

### RTK (Rust Token Killer) Rules
1. **Always prefix CLI/shell commands with `rtk`** in powershell/bash sessions (e.g., `rtk git status`, `rtk cargo test`, `rtk npm install`).
2. Do NOT prefix commands that are interactive, or those specified in `exclude_commands` (e.g., `curl`, `playwright`).
3. Use `rtk gain` to check token savings and `rtk discover` to find optimization opportunities.

### Context Mode Rules
1. **Think in Code**: Always write short scripts to analyze large outputs instead of reading raw files into context. Use `ctx_execute` (or `ctx_execute_file`) to execute scripts and print only the final answer.
2. **Sandbox Execution**: Use `ctx_execute` or `ctx_batch_execute` to execute any tool calls that generate large outputs (like `python scripts/healthcheck.py` or ADT/RAG searches) to reduce raw output size by 98%.
3. **Fetch Hardening**: Use `ctx_fetch_and_index` instead of curl/wget to index URLs into SQLite and search them via `ctx_search`.
4. **Session Continuity**: Use `ctx_checkpoint` to save session state, and `ctx_restore` to restore the state when the conversation is compacted.
