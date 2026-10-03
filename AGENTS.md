# SAP Router Skill for Codex

Canonical source: `.agents/`.
Karpathy wrapper: mandatory. Caveman compression: default.
Do not copy or fork skill bodies here; regenerate from canonical source.

Runtime root:
- `SAP_ROUTER_ROOT` must point to the canonical sap-router-skill repository.
- change the working directory to `SAP_ROUTER_ROOT` before relative commands.
- fail closed if `scripts/source_catalog.py` is not present there.

Dynamic local discovery:
- search skills: `python scripts/source_catalog.py search "task description"`
- search MCPs: `python scripts/mcp_launcher.py search --query "task description"`
- bundled MCPs are disabled candidates until reviewed; no runtime GitHub lookup.

Local optimization:
- prefer `rtk` for supported verbose CLI commands.
- use Context Mode for large outputs, indexed fetches, and session checkpoints.

Parity proof:
- skills: 203 sha256:046f6d52886520160ec0c76373806fd76f42ea8b489ebbe57b54e61fd29919fd
- profiles: 38 sha256:e746d5f5374f567c00e178b16645e378521476723efc61383bdc562f25d9c827
- registries: 14 sha256:e98ac633c7685dfb67cb878c1ae16833b0dcfccac5865035f5862c5fde42caf5

Run:
`python scripts/generate_ide_assets.py check`

--- project-doc ---

# SAP Router Skill & Harness — Multi-IDE Agent Instructions

> **203 canonical skills available across Claude, Codex, Gemini Antigravity, and Cursor.**
>
> | IDE | Skill Directory | Entry Point |
> |---|---|---|
> | **Claude Code** | .claude/skills/ (203 generated skills) | .claude/skills/run-sap-router-skill/SKILL.md |
> | **Antigravity (Gemini)** | .gemini/skills/ (203 generated skills) | .gemini/skills/run-sap-router-skill/SKILL.md |
> | **Codex / OpenAI** | .codex/AGENTS.md (shared canonical instructions) | .codex/AGENTS.md |
> | **Cursor** | .cursor/AGENTS.md (shared canonical instructions) | .cursor/AGENTS.md |
>
> All skills auto-trigger by file context and keyword. See SKILL.md for master dispatch.
> **Current (v7.1.0):** `sap_harness.py` (controlled agent execution + eval suite) + ZROUTER Remote FileSystem adapter + Automation Pilot & Skill-Share pipelines.

## SAP Harness v7.1 (Controlled Multi-Agent & Eval Engine)

```bash
# Autonomous mission execution
python scripts/sap_harness.py run --agent cpi --task "triage failed messages in CPI"

# Evaluation & Benchmark test suite (Offline Hermetic by default)
python scripts/sap_harness.py eval --suite all
python scripts/sap_harness.py benchmark

# Specialized subagent directory
python scripts/sap_harness.py agents

# Test ZROUTER Remote FileSystem integration (for vscode_abap_remote_fs)
python scripts/sap_harness.py test-remote-fs

# Automation Pilot MCP compiler & Skill packager
python scripts/automation_pilot_compiler.py --catalog cf --command ListCfOrgs
python scripts/skill_packager.py sap-cpi-flowpilot --slack-json
```

## Implemented v7 operating model

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

CPI/APIM/Fiori/UI5/CAP now route through API/CLI/plugin MCPs first and use Web UI MCP
fallbacks (`integration-suite-ui-mcp`, `apim-ui-mcp`) only when background access is blocked.
The Web UI bridge uses the logged-in browser session and does not accept credential values.

`apim-ui-mcp` carries two API Management channels and reports which one each call used.
OAuth `client_credentials` on an `apiportal-apiaccess` service key is SAP's documented path
and wins whenever it is configured; the logged-in browser session is an undocumented fallback
for reads and tests, running `fetch()` inside the page so cookies never leave the browser.
Scope is API lifecycle only — proxies, products, policies, key value maps and their tests —
never business data; SAP API Policy v.4.2026a §2.2.2 points agentic business-API access at the
Integration Suite MCP Gateway instead, which `apim_mcp_gateway_probe` checks the tenant for.

Mutating capabilities use plan/approval/commit semantics. Local approval state is handled by:

```bash
python scripts/approval_broker.py plan --capability sap.apim.proxy.deploy --target DEV
```

## What this project is

40 Python operational scripts plus Node.js review gates — no live SAP system required
credentials required. Everything runs offline:

| Script | Purpose |
|---|---|
| `scripts/sap_router.py` | Routing engine: ADT-first; SAP GUI scripting fallback (mcp-sap-gui); sf-mcp; ZROUTER RFC opt-in |
| `scripts/memory_manager.py` | Session context file (MEMORY.md) lifecycle |
| `scripts/xls_to_bapi.py` | CSV/XLSX → BAPI JSON payload converter |
| `scripts/template_repo.py` | Offline ABAP template repository with `{{placeholders}}` |
| `scripts/abap_serializer.py` | Multi-format ABAP packer: .nugg, abapGit, ZDOWNLOAD XML |
| `scripts/cpi_iflow_packager.py` | CPI iFlow ZIP create/validate/extract |
| `scripts/fallback_engine.py` | 6-tier cascading fallback with retry, verification, 36 mapped actions |
| `scripts/healthcheck.py` | Probes 12 configured MCPs (+70 fail-closed planned candidates), validates .env, generates interactive prompts |
| `scripts/self_learn.py` | Hermes-style context adaptation — tracks MCP latency/reliability, adapts routing |
| `scripts/zrouter_bootstrap.py` | ZROUTER probe + install (ADT/GUI/Offline) + fallback mapping |
| `scripts/btp_diagram.py` | BTP architecture diagram generator from skill references |
| `scripts/check_gui_scripting.py` | SAP GUI scripting readiness probe (RZ11 + SAPLogon check) |
| `scripts/hdi_lint.py` | SAP HANA HDI container linting and validation |
| `scripts/cpi_client.py` | CPI iFlow HTTP client with OAuth and CSRF support |
| `scripts/rag_ingest.py` | RAG ingestion pipeline for SAP documentation indexing |

## Run / verify

```bash
python .claude/skills/run-sap-router-skill/driver.py
# Exit 0 = all 78 checks passed. No project files modified.
```

Requires Python 3.11+ for the router and controlled harness. No packages needed for CSV; `pip install openpyxl`
for XLSX support only.

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

## Template repository commands

```bash
python scripts/template_repo.py init                                                  # Create blank repo
python scripts/template_repo.py seed                                                  # Populate 12 starter templates
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
- `route` is a classifier, not a validator — unknown actions fall to SAP GUI scripting. Functional writes are gated on --functional. ZROUTER is opt-in, never the default.
- **`template_repo.py` works offline** — resolves placeholders via Python string substitution. ABAP runtime eval uses `GENERATE SUBROUTINE POOL` (see ZROUTER_DISPATCH v2).
- **`abap_serializer.py` `_class_to_type`** auto-detects from name prefix: `ZCL_`→CLAS, `ZIF_`→INTF, `ZCX_`→CLAS, other `Z*`→PROG. Use explicit `--type` to override.

@RTK.md
