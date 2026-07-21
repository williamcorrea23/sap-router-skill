---
name: run-sap-router-skill
description: >-
  Run, smoke-test, and drive the SAP Router Skill CLI (sap_router.py,
  memory_manager.py, xls_to_bapi.py, template_repo.py, abap_serializer.py,
  cpi_iflow_packager.py). Use when asked to run, start, build,
  test, verify, or smoke-test the sap-router-skill, its routing
  engine, MEMORY.md compaction, or the XLS/CSV-to-BAPI converter.
trigger:
  keywords: [run, smoke-test, router, cli, sap-router, skill, memory, bapi, xls, csv]
  intent: >-
    Use when running, smoke-testing, building, or verifying the SAP Router Skill CLI, routing engine, or data converters.
---

# Run: sap-router-skill

> **Multi-IDE:** Same `driver.py` works on Codex, Antigravity, and Codex.
> Codex → this file. Antigravity → `.gemini/skills/run-sap-router-skill/SKILL.md`.
> Codex → `AGENTS.md` at unit root. All point to the same driver.

The repository now contains 40 Python operational scripts under `scripts/`.
The core smoke gate remains self-contained: **no live SAP system, network,
or credentials needed** — routing is a static lookup table, `memory_manager`
is local file I/O, `xls_to_bapi` parses CSV/XLSX. Everything runs offline.

| Script | Purpose |
|---|---|
| `sap_router.py` | Routing engine: ADT-first; SAP GUI scripting fallback (mcp-sap-gui); sf-mcp |
| `memory_manager.py` | Session context file (MEMORY.md) lifecycle |
| `xls_to_bapi.py` | CSV/XLSX → BAPI JSON payload converter |
| `template_repo.py` | Offline ABAP template repository with `{{placeholders}}` |
| `abap_serializer.py` | Multi-format ABAP packer: .nugg, abapGit, ZDOWNLOAD XML |

The agent path is the smoke driver: it launches every CLI surface against a
throwaway workspace and asserts exit codes + output.

## Repository-owned skill/MCP discovery

For ambiguous SAP tasks, search the unified local catalog before choosing a
skill or MCP:

```bash
python scripts/source_catalog.py search "task description"
python scripts/mcp_launcher.py search --query "task description"
```

Bundled MCP snapshots are fail-closed (`disabled_candidate`) until reviewed and
promoted in `.agents/registries/mcps.json`. No runtime GitHub lookup is allowed.

All paths below are relative to the unit root (`sap-router-skill/`).

## Prerequisites

- Python 3.8+ (verified on 3.14.4). On Windows the interpreter is `python`.
- No third-party packages required for CSV. **XLSX support is optional** —
  `pip install openpyxl` only if you pass `.xlsx` files; `.csv` always works.

## Run (agent path) — smoke driver

```bash
python .Codex/skills/run-sap-router-skill/driver.py
```

Exit `0` = all 62 checks passed; `1` = a check failed (offending line printed).
The driver creates and deletes its own temp workspace — it touches no project
files (ZROUTER opt-in state is redirected to a temp file via
`SAP_ROUTER_OPTIN_FILE`, so the smoke run never mutates the real decision).
Use it as the regression gate after editing any script in `scripts/`.

Verified output this session:

```text
62 passed, 0 failed
```

## Run (manual, individual CLIs)

```bash
# Routing: dev op -> ARC-1 ADT; ADT-unavailable -> SAP GUI scripting (mcp-sap-gui); sf_* -> sf-mcp
python scripts/sap_router.py route --action read_source                       # -> ARC-1 (ADT)
python scripts/sap_router.py route --action MM_CREATE_MATERIAL                 # -> needs-functional-context (no BAPI fired)
python scripts/sap_router.py route --action MM_CREATE_MATERIAL --functional    # -> BAPI dispatch (functional context)

# Parallel subagent dispatch (same-wave agents launch concurrently)
python scripts/sap_router.py dispatch-plan --spec requirements.md              # wave plan for stages 2-8
python scripts/sap_router.py crew-dispatch --task "find the leak then review the diff"  # concurrent cavecrew agents

# ZROUTER opt-in (optional RFC accelerator; never auto-installed)
python scripts/sap_router.py zrouter offer      # show the install offer (default: decline)
python scripts/sap_router.py zrouter decline    # persisted; routing stays ADT-first -> SAP GUI scripting
python scripts/sap_router.py zrouter accept     # then: zrouter install
python scripts/sap_router.py zrouter status     # current opt-in + enabled flag

# Session memory lifecycle (writes MEMORY.md at the given path)
python scripts/memory_manager.py init --input MEMORY.md --sys S4H --client 100 --env DEV --usr DEVELOPER
python scripts/memory_manager.py add  --input MEMORY.md --module MM --action-name CreateMaterial --status OK --fields '{"obj":"MAT123","tr":"S4HK900001"}'
python scripts/memory_manager.py verify --input MEMORY.md   # exit 0 if valid
python scripts/sap_router.py status --memory-file MEMORY.md

# XLS/CSV -> BAPI payload (9 modules: MM, SD, FI, QM, PP, WM, CO, HCM, BASIS)
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL
python scripts/xls_to_bapi.py convert  --input data.csv  --module MM --action CREATE_MATERIAL

# Template repository (offline code templates with {{placeholders}})
python scripts/template_repo.py init
python scripts/template_repo.py seed
python scripts/template_repo.py list
python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL --values '{"HEADER":"h","DESCRIPTION":"d"}'

# ABAP serializer (multi-format ABAP packer/unpacker)
python scripts/abap_serializer.py generate --source file.abap --name ZCL_FOO --type CLAS --format nugg --output out/
python scripts/abap_serializer.py package  --source file.abap --name ZCL_FOO --type CLAS --output out/
python scripts/abap_serializer.py extract  --input file.nugg --output out/
python scripts/abap_serializer.py split    --source multi_class.abap --output out/
```

## Gotchas (battle scars from this session)

- **Generated template is NOT valid input.** `xls_to_bapi.py template` writes
  the field descriptions as row 2 (e.g. "Material type (e.g. FERT)"). Feeding
  that file straight back into `convert`/`validate` fails required-field
  validation. Replace row 2 with real data first.
- **`memory_manager.py add` silently auto-inits** a missing MEMORY.md with
  hard-coded defaults `S4H/100/DEV` and user `$USERNAME`. If you skip `init`,
  your session header is wrong, not absent — no error is raised.
- **Hard caps enforced on write**: max 20 active blocks (older ones roll into a
  `## ARCHIVE` single-line summary), and the whole file must stay ≤100 lines.
  `verify` exits 1 if a block exceeds 2 detail lines or the file exceeds 100.
- **8 SAP modules field-defined**: `MM`, `SD`, `FI`, `QM`, `PP`, `WM`, `CO`, `HCM`, `BASIS`.
  Unknown module/action exits 1 with an "Available:" list — not a crash.
- **`route` never validates the action against a catalog** — unknown actions
  fall through to the SAP GUI scripting fallback (mcp-sap-gui) default — never BLOCKED. It's a classifier, not a validator.
- **Functional WRITE actions are gated** — `CREATE_*`, `CHANGE_*`, `POST_*`,
  `GOODS_MOVEMENT`, etc. return `needs-functional-context` (no BAPI fired) unless
  `--functional` is passed. BAPIs fire only when a real functional action requires
  them — a bare token (smoke test) never auto-fires one. Pure reads and explicit
  `*_GUI` actions are not gated.
- **ZROUTER is opt-in, never the engine.** Routing never auto-probes or
  auto-installs it. `--use-zrouter` is honoured only after `zrouter accept`;
  a `zrouter decline` is persisted (in `zrouter_optin.json`) and routing keeps
  working ADT-first -> SAP GUI scripting with no ZROUTER dependency.
- **`template_repo.py resolve` requires double quotes in --values JSON on Windows.**
  Use single-quote wrapping on the outside: `--values '{"KEY":"val"}'` works on both
  Windows and Unix. Double-quote-wrapped JSON on cmd.exe may break.
- **`abap_serializer.py` `_class_to_type` auto-detects from name prefix.**
  `ZCL_` → CLAS, `ZIF_` → INTF, `ZCX_` → CLAS, other `Z*` → PROG. Use explicit
  `--type` if your naming convention differs.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: openpyxl` | `pip install openpyxl`, or use `.csv` instead of `.xlsx`. |
| `convert` reports missing required fields on a fresh template | You fed the template's description row as data — see first gotcha. |
| `verify` exits 1 "exceeds 100 lines" | MEMORY.md got too big; run `python scripts/memory_manager.py compact --input MEMORY.md`. |
| `route`/`status` print nothing | `status` shells out to `memory_manager.py show`; pass a real `--memory-file` path. |
| `template_repo add` says "0 placeholders" | The ABAP file has no `{{PLACEHOLDER}}` markers. Add placeholders or use `seed` for pre-built templates. |
| `abap_serializer extract` "No source found" | `.nugg` file may be malformed — the CDATA block must contain valid source. |
