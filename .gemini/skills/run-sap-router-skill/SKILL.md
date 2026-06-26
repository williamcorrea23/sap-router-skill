---
name: run-sap-router-skill
description: >-
  Run, smoke-test, and drive the SAP Router Orchestrator CLI (sap_router.py,
  memory_manager.py, xls_to_bapi.py, template_repo.py, abap_serializer.py).
  Use when asked to run, start, build, test, verify, or smoke-test the
  sap-router-skill, its routing engine, MEMORY.md compaction,
  XLS/CSV-to-BAPI converter, template repository, or ABAP serializer.
---

# Run: sap-router-orchestrator

Five standalone Python 3 CLIs under `scripts/`. **No live SAP system, network,
or credentials needed** — routing is a static lookup table, `memory_manager`
is local file I/O, `xls_to_bapi` parses CSV/XLSX. Everything runs offline.

| Script | Purpose |
|---|---|
| `sap_router.py` | Routing engine: ADT vs ZROUTER RFC vs sf-mcp |
| `memory_manager.py` | Session context file (MEMORY.md) lifecycle |
| `xls_to_bapi.py` | CSV/XLSX → BAPI JSON payload converter |
| `template_repo.py` | Offline ABAP template repository with `{{placeholders}}` |
| `abap_serializer.py` | Multi-format ABAP packer: .nugg, abapGit, ZDOWNLOAD XML |

All paths below are relative to the unit root (`sap-router-skill/`).

## Prerequisites

- Python 3.8+ (verified on 3.14.4). On Windows the interpreter is `python`.
- No third-party packages required for CSV. **XLSX support is optional** —
  `pip install openpyxl` only if you pass `.xlsx` files; `.csv` always works.

## Run (agent path) — smoke driver

```bash
python .claude/skills/run-sap-router-skill/driver.py
```

Exit `0` = all 44 checks passed; `1` = a check failed (offending line printed).
The driver creates and deletes its own temp workspace — it touches no project
files. Use it as the regression gate after editing any script in `scripts/`.

## Run (manual, individual CLIs)

```bash
# Routing
python scripts/sap_router.py route --action MM_CREATE_MATERIAL

# Session memory lifecycle
python scripts/memory_manager.py init --input MEMORY.md --sys S4H --client 100 --env DEV --usr DEVELOPER
python scripts/memory_manager.py add  --input MEMORY.md --module MM --action-name CreateMaterial --status OK --fields '{"obj":"MAT123"}'
python scripts/memory_manager.py verify --input MEMORY.md

# XLS/CSV -> BAPI payload (9 modules)
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL
python scripts/xls_to_bapi.py convert  --input data.csv  --module MM --action CREATE_MATERIAL

# Template repository
python scripts/template_repo.py init
python scripts/template_repo.py seed
python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL --values '{"HEADER":"h"}'

# ABAP serializer
python scripts/abap_serializer.py package --source file.abap --name ZCL_FOO --type CLAS --output out/
python scripts/abap_serializer.py extract --input file.nugg --output out/
```

## Gotchas

- **Generated template is NOT valid input.** `xls_to_bapi.py template` writes
  field descriptions as row 2. Replace row 2 with real data first.
- **`memory_manager.py add` silently auto-inits** a missing MEMORY.md with
  hard-coded defaults `S4H/100/DEV`. No error raised.
- **Hard caps**: max 20 active blocks, File ≤100 lines. `verify` exits 1 if exceeded.
- **9 SAP modules**: `MM`, `SD`, `FI`, `QM`, `PP`, `WM`, `CO`, `HCM`, `BASIS`.
  Unknown module/action exits 1 with "Available:" list.
- **`route` never validates against a catalog** — unknown actions fall through
  to ZROUTER RFC default. It's a classifier, not a validator.
- **`template_repo.py resolve`** uses Python string substitution. For ABAP runtime
  eval, use `GENERATE SUBROUTINE POOL` pattern in ZROUTER_DISPATCH v2.
- **`abap_serializer.py` `_class_to_type`** auto-detects from name prefix:
  `ZCL_`→CLAS, `ZIF_`→INTF, `ZCX_`→CLAS, other `Z*`→PROG.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: openpyxl` | `pip install openpyxl`, or use `.csv` instead of `.xlsx`. |
| `convert` reports missing required fields on fresh template | You fed the template's description row as data — see first gotcha. |
| `verify` exits 1 "exceeds 100 lines" | Run `memory_manager.py compact --input MEMORY.md`. |
| `template_repo add` says "0 placeholders" | ABAP file has no `{{PLACEHOLDER}}` markers. Add some or use `seed`. |
