---
name: superclaude-for-sap
description: Superclaude for SAP reference (babamba2/superclaude-for-sap). Includes advanced agent prompts, macros, and shortcut mappings for SAP — power-user macro phrases that expand to full sap-router-orchestrator flows.
trigger:
  keywords: [superclaude, macro, shortcut, alias, power user, quick command, agent prompt, delegation shortcut, command expansion]
  intent: Expanding short power-user macro phrases into full orchestrator npm/CLI flows (routing, pipeline, review, fallback, caveman delegation)
prerequisites:
  - Node.js + npm — all macros run from the sap-router-skill repo root
  - Python 3.10+ (scripts/ directory: sap_router.py, fallback_engine.py, healthcheck.py)
  - .env configured — run `npm run hc:prompt` once before first macro use
  - Optional for GUI fallback tiers: SAPGUI installed with scripting enabled (`npm run gui:check`)
---

# Superclaude for SAP — Macro and Shortcut Layer

A **macro** is a short command phrase the user types (or Codex recognizes) that expands to a full
orchestrator flow. Every macro below is grounded in a real npm script from `package.json`.
Adapted from babamba2/superclaude-for-sap for this repo's router, pipeline, and fallback engine.

## 1. Macro Table

| Macro | Expands to | When |
|---|---|---|
| `probe` | `npm run hc` | Session start — health of 53 MCPs + .env completeness |
| `probe fix` | `npm run hc:prompt` | Healthcheck found missing .env vars — interactive fill |
| `route X` | `npm run router -- --action X` | Single action, ADT-first (e.g. `MM_CREATE_MATERIAL`) |
| `route gui X` | `npm run router:gui -- --action X` | Skip ADT, go straight to SAP GUI automation |
| `cave <task>` | `npm run router:caveman -- "<task>"` | Small bounded task — router picks a cavecrew agent |
| `spec scan` | `npm run spec:analyze -- requirements.md` | Classify a spec before committing to the pipeline |
| `spec run` | `npm run pipeline -- requirements.md` | Full 8-stage spec-to-transport pipeline |
| `spec fast` | `npm run pipeline:fast -- requirements.md` | Trusted spec — skip optional pipeline stages |
| `review` | `npm run abap:review` | Lint + security + Clean ABAP on `templates/**/*.abap` |
| `ship it` | `npm run abap:review:transport` | Pre-release transport gate (GO/NO-GO) |
| `zprobe` | `npm run zrouter:probe` | Check if ZROUTER RFC handler is installed on SAP |
| `fallback X` | `npm run fallback:execute -- X` | Action failed — cascade 6 tiers (ADT→RFC→GUI→BDC→Offline→Manual) |
| `map X` | `npm run fallback:map -- X` | Show the tier plan for action X without executing anything |
| `gui ok?` | `npm run gui:check` | Verify SAPGUI scripting is enabled before GUI-tier macros |
| `all green` | `npm run validate:all` | Full gate: healthcheck + abaplint CI + router status |

Extended macros: `diagram <file>` → `npm run btp:diagram -- landscape.json` (BTP architecture diagram),
`hdi lint <path>` → `npm run hana:hdi-lint -- db/src` (HDI artifact lint).

## 2. Caveman Delegation Shortcuts

One entry point — the router decides which cavecrew agent handles the task:

```bash
npm run router:caveman -- "find where MATNR conversion exit is called"
```

| Task shape | Agent chosen | Output |
|---|---|---|
| Locate code, "where is X", map directory | `cavecrew-investigator` | file:line table, read-only |
| 1-2 file surgical edit, rename, typo fix | `cavecrew-builder` | caveman diff receipt |
| Review a diff/branch/file | `cavecrew-reviewer` | one line per finding, severity-tagged |

Delegate when scope is bounded and obvious; subagent output is caveman-compressed (~60% smaller),
so the main context lasts longer. Do NOT delegate new features or 3+ file refactors — builder refuses.

## 3. Advanced Agent Prompt Patterns

**Dry-run first on any non-trivial spec** — see stage plan and routing decisions with zero SAP writes:

```bash
python scripts/sap_router.py pipeline --mode dry-run --spec req.md
```

Then commit to a real run:

```bash
npm run pipeline -- req.md          # full 8 stages: spec -> code -> lint -> transport
npm run pipeline:fast -- req.md     # fast mode when the dry-run showed no ambiguity
```

**Parallel waves** — independent actions belong in one prompt so the orchestrator batches them:

```
route MM_CREATE_MATERIAL + route FI_POST_DOCUMENT + zprobe   (no shared state -> run as one wave)
```

**Self-learn feedback** — teach the router after each macro so future routes improve:

```bash
npm run learn:mcp -- --mcp arc-1 --latency 245 --success true
npm run learn:route -- --action MM_CREATE_MATERIAL --success true
```

## 4. Data Macros (CSV to BAPI)

```bash
# "sheet MM CREATE_MATERIAL" -> generate a CSV template with the right BAPI fields
npm run template -- --module MM --action CREATE_MATERIAL

# "check csv" -> validate field mapping before any conversion
npm run csv:check -- --input data.csv --module MM --action CREATE_MATERIAL

# "load csv" -> convert validated CSV to BAPI JSON for ZROUTER dispatch
npm run convert -- --input data.csv --module MM --action CREATE_MATERIAL
```

Always run `csv:check` before `convert` — the checker catches missing mandatory BAPI fields offline.

## Pitfalls

- **Macro fails with connection/auth errors** → Cause: macros assume a configured `.env`; healthcheck
  was never run. Solution: `npm run hc:prompt` first — it interactively fills missing vars, then re-run.
- **`spec run` on an ambiguous spec wastes a full pipeline pass** → Cause: 8 stages executed on a spec
  that needed clarification. Solution: `spec scan` first, then
  `python scripts/sap_router.py pipeline --mode dry-run --spec req.md` before any real run.
- **`fallback X` dies at Tier 3 (GUI)** → Cause: cascade reached GUI/BDC tiers but SAPGUI scripting is
  not installed/enabled on this machine. Solution: `npm run gui:check`; if red, enable SAPGUI scripting
  (RZ11 `sapgui/user_scripting = TRUE`) or accept Offline tier output.
- **Flags swallowed by npm** → Cause: missing `--` separator, e.g. `npm run router --action X`.
  Solution: always pass args after `--`: `npm run router -- --action X`.
- **`ship it` passes locally but transport is rejected** → Cause: only `abap:review` (lint) was run.
  Solution: `abap:review:transport` is the actual release gate; run it before every transport release.

## Verification

```bash
# Environment sane and every MCP reachable
npm run hc

# Macro expansion works end-to-end without touching SAP
npm run fallback:map -- MM_CREATE_MATERIAL     # prints tier plan, no execution
python scripts/sap_router.py pipeline --mode dry-run --spec req.md

# Full gate — healthcheck + lint CI + router status must all pass
npm run validate:all
```

## Related

- **sap-router-skill** — master dispatch table and routing decision tree these macros expand into
- **karpathy-guidelines** — mandatory wrapper (Think → Simplify → Surgical → Goal-Verify) around every macro
- **caveman:cavecrew** — decision guide for the delegation shortcuts in section 2
- **run-sap-router-skill** — smoke-testing the CLIs behind the macros
- **sap-self-learn** — how `learn:mcp` / `learn:route` telemetry adapts future routing
