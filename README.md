# SAP Router Orchestrator

> **IDE-native SAP development hub** — works directly inside VS Code / Claude Code.
> Skills auto-trigger by file context. ADT MCP connects live to SAP systems.
> No external IDE, no Eclipse, no SAP GUI required for code operations.

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-50%2F50-brightgreen.svg)](.claude/skills/run-sap-router-skill/driver.py)
[![Skills](https://img.shields.io/badge/skills-54-blueviolet.svg)](.claude/skills/)
[![MCPs](https://img.shields.io/badge/mcps-16-orange.svg)](.mcp.json)

**54 skills · 6 CLIs · 16 MCPs · 4 ABAP templates** — ABAP, RAP, CDS, BTP,
CPI, CAP, UI5, Fiori, HANA, Datasphere, SAC, AI Core.

---

## How It Works — Directly in Your IDE

When you open a `.abap`, `.cds`, or `.groovy` file in VS Code, the matching
skill auto-activates. When you ask to read ABAP source or deploy a transport,
the correct MCP server connects to your SAP system live. No context switching.

```
┌──────────────────────────────────────────────────────┐
│                    VS CODE / CLAUDE CODE              │
│                                                       │
│  You type: "read ZCL_MATERIAL_HANDLER source"         │
│       │                                               │
│       ▼                                               │
│  ┌─────────────────────────────────────┐              │
│  │  54 auto-trigger skills             │              │
│  │  ├─ file: *.abap  → abap-code-*    │              │
│  │  ├─ file: *.cds   → cds-view-*     │              │
│  │  ├─ file: *.groovy → cpi-iflow-*   │              │
│  │  ├─ action: BAPI → sap-bapi-*      │              │
│  │  └─ action: transport → sap-trans* │              │
│  ├─────────────────────────────────────┤              │
│  │  16 MCP servers (live SAP)          │              │
│  │  ├─ arc-1 → ADT read/write          │              │
│  │  ├─ aibap → 69 ABAP dev tools       │              │
│  │  ├─ hermes-crewai → BAPI calls      │              │
│  │  └─ sap-cpi → CPI deploy/monitor    │              │
│  ├─────────────────────────────────────┤              │
│  │  6 Python CLIs (offline safety)     │              │
│  │  ├─ route actions                  │              │
│  │  ├─ CSV → BAPI payload             │              │
│  │  ├─ serialize ABAP objects         │              │
│  │  └─ package CPI iFlows             │              │
│  └─────────────────────────────────────┘              │
│       │                                               │
│       ▼                                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐          │
│  │ S/4HANA  │   │ BTP CF   │   │ CPI      │          │
│  │ (ADT)    │   │ (CTM)    │   │ (iFlow)  │          │
│  └──────────┘   └──────────┘   └──────────┘          │
└──────────────────────────────────────────────────────┘
```

**Skills auto-trigger**: opening a `.abap` file activates ABAP patterns.
Mentioning "BAPI call" activates BAPI integration. Typing "transport request"
activates transport management. **ADT MCP servers** connect directly to SAP —
read/write source code, activate objects, execute BAPIs, manage transports.
All from within VS Code.

---

## Installation

### Prerequisites

- **VS Code** + **Claude Code extension** (required)
- Python 3.8+ (for the 6 offline CLIs)
- SAP NetWeaver ≥ 7.40 + ADT services active in SICF (for live MCP)
- Node.js 18+ and npm (for ABAP peer review)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/sap-router-orchestrator.git
cd sap-router-orchestrator
```

### Step 2 — Install Python Dependencies

```bash
# No packages required — CSV works without pip install
# Optional: XLSX support
pip install openpyxl
```

### Step 3 — Configure MCP Servers in VS Code

Copy `.mcp.json` to your workspace root or add to Claude Code `settings.json`:

```bash
# .mcp.json is ready — 16 servers pre-configured
# Each server needs SAP credentials (see below)
cp .mcp.json <your-project>/.mcp.json
```

**SAP credentials — configure the MCPs you intend to use:**

| MCP Server | Environment Variables |
|---|---|
| `arc-1` | `ARC_SAP_URL`, `ARC_SAP_USER`, `ARC_SAP_PASSWORD`, `ARC_SAP_CLIENT` |
| `aibap` | Configure `systems.json` with host, user, password, client |
| `mcp-abap-adt` | `SAP_URL`, `SAP_USERNAME`, `SAP_PASSWORD`, `SAP_CLIENT` |
| `hermes-crewai` | Already configured on the local system |
| `sap-cpi` | Already configured — requires live CPI tenant |
| `mcp-sap-notes` | `SAP_USERNAME`, `SAP_PASSWORD` (me.sap.com account) |

> **Security**: credentials live in local `.env` files (already in `.gitignore`).
> No passwords are committed to the repository.

### Step 4 — Skills Load Automatically

All 54 skills in `.claude/skills/` are auto-discovered by Claude Code when
you open the project. **Zero manual configuration** — each skill has
auto-activation triggers based on file context and keywords.

```bash
# Verify everything works:
python .claude/skills/run-sap-router-skill/driver.py
# → 50 passed, 0 failed
```

### Step 5 (Optional) — Install ABAP Peer Review

```bash
npm install
npm run abap:lint           # Lint all ABAP templates
npm run abap:review         # Full review: lint + security + clean code
```

---

## Daily Usage — Real IDE Examples

### "Read ABAP source code of a SAP class"

```
You (in VS Code chat):
  "read class ZCL_MATERIAL_HANDLER from DEV system"

Auto-trigger skill: sap-adt-cli / abap-code-patterns
MCP called: arc-1 → SAPRead(uri="/sap/bc/adt/oo/classes/zcl_material_handler/source/main")

Result: source appears in chat. You edit, the skill uses SAPWrite to save.
```

### "Create a CPI iFlow with Groovy script"

```
You:
  "create an iFlow that receives orders via HTTPS, transforms with Groovy,
   calls BAPI on S/4HANA, and returns confirmation"

Auto-trigger skill: cpi-iflow-development
CLI called: cpi_iflow_packager.py create → generates iFlow ZIP
MCP called: sap-cpi → deploys iFlow to CPI tenant

Result: iFlow deployed and running, Groovy scripts ready.
```

### "Convert CSV spreadsheet into BAPI calls"

```
You:
  "I have a spreadsheet materials.csv, create all in SAP via BAPI"

Auto-trigger skill: sap-bapi-integration
CLI called: xls_to_bapi.py template + convert
MCP called: hermes-crewai / arc-1 → executes BAPI for each row

Result: JSON payload generated, BAPI called, return validated.
```

### "Review ABAP code before transport"

```
You:
  "review ZCL_ROUTER_HANDLER_MM before releasing to PRD"

Auto-trigger skill: clean-abap + abap-code-review
CLI called: npm run abap:review
MCP called: aibap → syntax_check + run_atc_check + run_unit_tests

Result: HTML report with 9 dimensions, GO/NO-GO decision.
```

---

## What's Included

### 54 Skills (auto-trigger by file context)

| File Trigger | Skills Activated |
|---|---|
| `*.abap` | clean-abap, abap-code-patterns, released-abap-classes, abapgit, abap-sql-amdp, abap-unit-testing, authorization-iam |
| `*.cds` | cds-view-entities, sap-cap |
| `*.bddef` | rap, rap-business-events |
| `*.groovy` | cpi-iflow-development |
| `manifest.json` | sapui5-framework, sap-fiori-tools |
| `mta.yaml` | btp-developer-guide, sap-cap |
| `package.json` (CAP) | sap-cap, btp-best-practices |
| `*.hdbprocedure` | sap-hana-sqlscript |
| `*.xslt` / `*.mmap` | cpi-iflow-development |
| `transport request` | sap-transport-management, btp-cloud-transport-management |

**54 skills = 8 ABAP Core + 7 RAP/CDS/Cloud + 15 BTP + 3 UI5/Fiori +
6 CAP/HANA/AI + 6 SAC/Datasphere + 1 CPI + 5 Security/Infra + 3 Tooling**

### 16 MCPs (live SAP connection from IDE)

| MCP | Tools | Connects To |
|---|---|---|
| `arc-1` | 12 (SAPRead/Write/Search/Activate/Transport/...) | S/4HANA via ADT |
| `aibap` | 69 (source, objects, testing, ST22, BAdI, DEBUG...) | S/4HANA via ADT |
| `mcp-abap-adt` | 13 (GetProgram, GetClass, GetTable, SearchObject...) | S/4HANA via ADT |
| `hermes-crewai` | 21 (ADT, BAPI, HANA, ABAP lint, transport gate...) | S/4HANA + HANA |
| `sap-cpi` | 11 (deploy, messages, keystore, credentials...) | CPI tenant |
| `mcp-sap-notes` | 2 (search, fetch) | me.sap.com |
| `btp-mcp` | 7 (GlobalAccount, Subaccounts, Entitlements...) | BTP cockpit |
| `odata-mcp-proxy` | 32 (CPI admin APIs) | CPI OData |
| `btp-sap-odata-to-mcp` | 3 (discover, metadata, execute) | S/4HANA OData |
| `plugin:ui5` | 10 (create app, linter, API ref) | UI5/SAPUI5 |
| `plugin:sap-fiori-mcp` | 8 (Fiori generation, modification) | SAP Fiori |
| `plugin:mdk-mcp` | 5 (MDK project, deploy) | SAP MDK |
| `plugin:cds-mcp` | 2 (CDS model search, docs) | CAP CDS |
| `plugin:azure` | 50+ (compute, storage, AKS, IaC...) | Azure |
| `plugin:desktop-commander` | 20+ (shells, files, search) | Local filesystem |
| `mobile-webapp-crew` | 17 (Flutter, Android, web) | Mobile/web |

### 6 Python CLIs (offline tools)

| CLI | Quick Start |
|---|---|
| `sap_router.py` | `python scripts/sap_router.py route --action MM_CREATE_MATERIAL` |
| `memory_manager.py` | `python scripts/memory_manager.py init --input MEMORY.md --sys S4H --client 100 --env DEV --usr DEV` |
| `xls_to_bapi.py` | `python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL` |
| `template_repo.py` | `python scripts/template_repo.py seed` |
| `abap_serializer.py` | `python scripts/abap_serializer.py package --source file.abap --name ZCL_FOO --type CLAS --output out/` |
| `cpi_iflow_packager.py` | `python scripts/cpi_iflow_packager.py template --name my-iflow --output my-iflow.zip` |

### 4 ABAP Templates (deploy via ADT MCP)

| Template | Lines | Purpose |
|---|---|---|
| `ZROUTER_DISPATCH.abap` | 1,349 | Full framework — 9 handlers, evaluate_expression, batch, FM |
| `ZCL_ABAP_REPL_V2.abap` | — | SICF HTTP handler + GENERATE SUBROUTINE POOL |
| `ZROUTER_DB_TABLES.abap` | 127 | 5 DDIC tables for code template repository |
| `ZROUTER_CODE_SEARCH.abap` | — | 3 BASIS handler actions for ABAP code search |

---

## ZROUTER Installation on SAP via ADT MCP

**Zero SAP GUI, zero SE80.** Everything via ADT MCP from within VS Code.

SAP prerequisites: NetWeaver ≥ 7.40, `/sap/bc/adt` active in SICF,
user with `S_DEVELOP` + `S_ADT_RES`.

```bash
# Step 1: Create package
aibap: create_object(type="DEVC", name="ZROUTER",
       description="SAP Router Orchestrator")

# Step 2: Create 19 data elements + 5 DDIC tables
aibap: create_object(type="DTEL", name="ZROUTER_TMPL_ID")
# ... (full list in SKILL.md)

# Step 3: Deploy ABAP classes
python scripts/abap_serializer.py package \
  --source templates/ZROUTER_DISPATCH.abap \
  --name ZCL_ZROUTER_DISPATCH --type CLAS --output deploy/
# → Pull deploy/abapgit/ into SAP via abapGit
#   OR: arc-1 SAPWrite directly to class source

# Step 4: Create Function Module
aibap: create_object(type="FUGR", name="ZROUTER")
aibap: create_object(type="FUNC", name="ZROUTER_DISPATCH_FM",
       function_group="ZROUTER")

# Step 5: Activate all and verify
aibap: activate_objects(["ZCL_ZROUTER_DISPATCH","CX_ZROUTER",
       "ZROUTER_DISPATCH_FM","ZROUTER_TMPL_HD","ZROUTER_TMPL_CD",
       "ZROUTER_TMPL_PL","ZROUTER_TMPL_PKG","ZROUTER_TMPL_PKG_T"])
aibap: syntax_check(["ZCL_ZROUTER_DISPATCH","ZROUTER_DISPATCH_FM"])
aibap: run_unit_tests(["ZCL_ZROUTER_DISPATCH"])
```

---

## Project Structure

```
sap-router-skill/
├── README.md                   ← This file
├── SKILL.md                    ← Global skill (master dispatch)
├── LICENSE                     ← MIT
├── CHANGELOG.md
├── .gitignore
├── .mcp.json                   ← 16 MCPs — copy to your workspace
├── .abaplint.json              ← 60+ ABAP lint rules
├── package.json                ← npm scripts (lint, review, CI)
│
├── .claude/skills/             ← 54 skills (auto-load in IDE)
│   ├── run-sap-router-skill/  ← Smoke driver
│   ├── abap-code-patterns/           ← BAPI, GEN SUBROUTINE POOL
│   ├── clean-abap/                   ← Clean ABAP Style Guide
│   ├── rap/                          ← RAP managed/unmanaged
│   ├── cds-view-entities/            ← CDS DEFINE VIEW ENTITY
│   ├── btp-*/ (15 skills)            ← All BTP services
│   ├── sapui5-framework/             ← UI5 patterns + TypeScript
│   ├── sap-cap/                      ← CAP Node.js/Java
│   ├── sap-hana-*/ (3 skills)        ← HANA SQLScript, CLI, ML
│   ├── sap-sac-*/ (4 skills)         ← SAC scripting, planning
│   ├── cpi-iflow-development/        ← CPI Groovy + iFlow ZIP
│   └── ... (full list in SKILL.md)
│
├── .gemini/skills/             ← 1 skill for Antigravity IDE
│
├── scripts/                    ← 6 Python CLIs + 1 JS gate
│   ├── sap_router.py           ← Routing engine
│   ├── memory_manager.py       ← Session memory (MEMORY.md)
│   ├── xls_to_bapi.py          ← CSV/XLSX → BAPI JSON (29 actions)
│   ├── template_repo.py        ← ABAP template repository
│   ├── abap_serializer.py      ← .nugg / abapGit / XML packer
│   ├── cpi_iflow_packager.py   ← CPI iFlow ZIP creator
│   └── abap-review-gate.js     ← CI gate (security/clean/transport)
│
├── templates/                  ← 4 ABAP templates
│   ├── ZROUTER_DISPATCH.abap       ← Full framework
│   ├── ZCL_ABAP_REPL_V2.abap       ← SICF HTTP REPL
│   ├── ZROUTER_DB_TABLES.abap      ← 5 DDIC tables
│   └── ZROUTER_CODE_SEARCH.abap    ← Code search integration
│
├── references/                 ← SAP knowledge base
│   ├── module_maps/            ← 10 SAP module operation maps
│   └── trench_knowledge/       ← 14 domain references
│
├── packages/samples/           ← Sample exports
│   ├── nugg/                   ← Single-file XML format
│   ├── abapgit/                ← Meta + source format
│   ├── xml/                    ← ZDOWNLOAD format
│   └── sample-order-process.zip ← CPI iFlow template
│
└── COMPARISON.md               ← 62-repo cross-reference analysis
```

---

## Routing Engine

| Action contains | Destination | MCP Used |
|---|---|---|
| `read_source`, `search_object`, `syntax_check`, `where_used`, `get_deps`, `code_search` | ARC-1 ADT | arc-1 / aibap / hermes-crewai |
| `sf_*` prefix | sf-mcp OData | SuccessFactors API |
| everything else | ZROUTER RFC | ZROUTER_DISPATCH_FM → 9 handlers |

---

## ABAP Peer Review (abaplint + npm)

```bash
npm install
npm run abap:lint          # Lint all ABAP templates
npm run abap:review        # Full review: lint + security + clean
npm run abap:review:report # HTML report
npm run abap:review:ci     # CI mode: fails on CRITICAL/HIGH
```

Pipeline: `lint → fix → CI gate → 9-dim analysis → transport gate → report`

---

## Related Repositories

62 SAP repositories analyzed and indexed — see [COMPARISON.md](COMPARISON.md).

Key integrations:
- [DevEpos/abap-code-search-tools](https://github.com/DevEpos/abap-code-search-tools) — ABAP full-text search
- [arc-mcp/arc-1](https://github.com/arc-mcp/arc-1) — Enterprise ADT MCP (3,474 tests)
- [Hochfrequenz/aibap.mcp](https://github.com/Hochfrequenz/aibap.mcp) — 69-tool ABAP MCP (Go)
- [secondsky/sap-skills](https://github.com/secondsky/sap-skills) — 37 Claude Code SAP plugins
- [shrek-abaper/sap-engineering-skill](https://github.com/shrek-abaper/sap-engineering-skill) — 4 skills: ADT CLI, review, transport gate, RAP gen

---

## Contributing

PRs and issues welcome. See [SKILL.md](SKILL.md) for the full dispatch table
and 54-skill reference. MIT licensed — use freely.

---

*Not affiliated with or endorsed by SAP SE. MIT licensed.*
