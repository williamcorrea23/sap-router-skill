# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Healthcheck — probes 35 MCPs (+18 planned) + .env completeness (run first)
npm run hc
npm run hc:prompt       # Interactive setup for missing .env vars

# Routing
npm run router -- --action MM_CREATE_MATERIAL
npm run router:gui -- --action SPRO_CONFIG   # Force GUI fallback

# Pipeline — spec to transport (8 stages)
npm run pipeline -- requirements.md
npm run pipeline:fast -- requirements.md

# ABAP quality
npm run abap:lint                 # abaplint static analysis
npm run abap:review               # lint + security + clean
npm run abap:review:transport     # Pre-release gate

# Self-learn
npm run learn:mcp -- --mcp arc-1 --latency 245 --success true
npm run learn:route -- --action MM_CREATE_MATERIAL --success true

# ZROUTER bootstrap
npm run zrouter:probe             # Check if ZROUTER installed on SAP
npm run zrouter:install:force     # Install via ADT

# Data
npm run template -- --module MM --action CREATE_MATERIAL
npm run csv:check -- --input data.csv --module MM --action CREATE_MATERIAL

# Update
npm run update          # git pull + npm install + healthcheck
```

## Architecture

**Skill orchestration is model-driven, not code-driven.** 85 skill files in `.claude/skills/*/SKILL.md` contain YAML frontmatter (`name`, `description` with trigger keywords) and markdown instructions. Claude Code activates matching skills by scanning the frontmatter descriptions. There is no programmatic skill dispatcher — the LLM reads the SKILL.md instructions and decides what to call.

**karpathy-guidelines** is the mandatory behavioral wrapper. Every SAP operation follows Think (surface assumptions) → Simplify (shortest path) → Surgical (touch only what's needed) → Goal-Verify (loop until criteria met). Output defaults to caveman compression.

**Routing decision tree** lives in `scripts/sap_router.py` (`SapRouter.get_route()`) and SKILL.md:
1. Caveman scope? → cavecrew-investigator/builder/reviewer
2. ADT operation? → arc-1 (primary) or aibap (secondary)
3. GUI required? → mcp-sap-gui (immediate, no ADT attempt)
4. BAPI batch? → ZROUTER RFC via sap-rfc-mcp-server
5. Spec→code? → 8-stage pipeline
6. Fallback: TieredFallback engine in `scripts/fallback_engine.py` (6 tiers: ADT→RFC→GUI→BDC→Offline→Manual)

**ZROUTER availability** is cached in `_zrouter_state` (None=not checked, True=installed, False=missing). `sap_router.py` auto-probes on first route. When ZROUTER is missing, the router cascades through fallback tiers.

## Key files

| File | Purpose |
|---|---|
| `SKILL.md` | Master dispatch table, 4-principle Karpathy wrapper, routing decision tree |
| `scripts/sap_router.py` | Routing engine with ADT-first/GUI-fallback/caveman delegation/pipeline orchestration |
| `scripts/fallback_engine.py` | 6-tier cascading fallback with retry, verification, 36 mapped actions |
| `scripts/healthcheck.py` | Probes 35 MCPs (+18 planned), validates .env, generates interactive prompts |
| `scripts/self_learn.py` | Hermes-style context adaptation — tracks MCP latency/reliability, adapts routing |
| `scripts/zrouter_bootstrap.py` | ZROUTER probe + install (ADT/GUI/Offline) + fallback mapping |
| `scripts/xls_to_bapi.py` | CSV/XLSX → BAPI JSON with field mapping validation |
| `scripts/memory_manager.py` | MEMORY.md session lifecycle + ABAPLINT section |
| `.mcp.json` | 35 MCP server configs (+18 planned) — ADT, GUI (3 tiers), RFC, CPI, CF, APIM, RAG (3), PI/PO, BW, Datasphere, Steampunk, Sapient, Integration Suite, CPI OData Proxy, ABAP-MCP, Cloud ALM, CTS Transport + 4 plugins |
| `README.md` | GitHub landing page — 8 Mermaid diagrams, skill catalog, MCP reference, 130 topic tags, SEO footer |

## Cross-file consistency rules

When adding skills, MCPs, CLIs, or npm scripts, update ALL of these:
- `SKILL.md` — skills list, MCPs section, CLIs section
- `README.md` — badges, counts, Mermaid diagrams, skill categories
- `.mcp.json` — `mcpServers` object, `routing` config, `notes`
- `.env.template` — env vars for new MCPs
- `scripts/healthcheck.py` — `MCP_HEALTHCHECK_SPEC`, `OPTIONAL_ENV_FILE_VARS`, thresholds
- `package.json` — `description` with accurate counts, npm scripts
- `AGENTS.md` — skill count, routing table

## Python script constraints

- Windows cp1252 codec issues: use `.format()` or f-strings with ASCII-only characters. Avoid Unicode in print() output (arrows, emojis, curly quotes).
- All imports from sibling scripts must handle `ModuleNotFoundError` with `sys.path.insert(0, str(SKILL_DIR))` fallback.
- Count thresholds in `healthcheck.py` must match actual disk counts (skills >= 85, scripts >= 15).

## Mermaid diagrams (README.md only)

All 8 Mermaid blocks must avoid subgraph/node ID collisions. When a subgraph name matches any node within it, Mermaid rejects with a cycle error. Use distinct subgraph IDs.
