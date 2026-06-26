# SAP Router Orchestrator v4.0 — Implementation Plan

## Current State (v4.0 — Complete)

| Metric | Value |
|---|---|
| Skills | 78 domain skills across 13 categories |
| MCP Servers | 30 configured (ADT, GUI 3-tier, RFC, CPI, CF, APIM, HCM, BTP/OData, RAG 3, PI/PO, BW, Datasphere, Steampunk, Sapient, 4 plugins) |
| Python CLIs | 10 scripts |
| npm Scripts | 60 |
| ABAP Templates | 4 |
| Routing Tiers | 6 (ADT → RFC → GUI → BDC → Offline → Manual) |
| Code Review | abaplint (60 rules) + 9-dimension review + 10-dim transport gate |
| Self-Learning | MCP latency/reliability tracking, route adaptation, decay-weighted stats |
| RAG | Pinecone, Supabase pgvector, Azure AI Search (pre-ready, activate via .env) |

## Implementation Decisions (Consolidated)

| # | Decision | Choice | Status |
|---|---|---|---|
| 1 | Skill base | **sc4sap patterns** + ZROUTER modules | Built |
| 2 | ADT backend | **ARC-1** (12 intent tools) primary, aibap (69 tools) secondary | Built |
| 3 | HCM | **Both**: SuccessFactors (sf-mcp OData) + HCM on-prem (RFC/BAPI) | Built |
| 4 | Orchestration | **LLM-driven** via SKILL.md dispatch — no code-level orchestrator | Built |
| 5 | MCPs | **30 total** (was 7 core + 6 lazy → now 22 core + 8 domain-specific) | Built |
| 6 | Context | **MEMORY.md** with block compaction + ABAPLINT section + ## LEARN section | Built |
| 7 | GUI fallback | **Immediate** — skip ADT attempt for SPRO/SM30/SU01/MM01 etc. | Built |
| 8 | Karpathy wrapper | **Mandatory** — Think→Simplify→Surgical→Verify on every operation | Built |
| 9 | Output format | **Caveman compression** default (60% token savings) | Built |
| 10 | Self-learning | **EMA stats** per MCP, route confidence tracking, 24h half-life decay | Built |
| 11 | Data ingestion | **CSV/XLS → BAPI JSON** with fuzzy field mapping + validation | Built |
| 12 | RAG connectors | **Pre-ready** — Pinecone, Supabase, Azure AI Search in .mcp.json + .env.template | Built |

## Architecture Layers

```
Layer 0 — Invocation: User types request in VS Code chat
Layer 1 — Karpathy Wrapper: 4-principle behavioral filter (karpathy-guidelines skill)
Layer 2 — Master Dispatch: SKILL.md routing decision tree → LLM picks action
Layer 3 — Routing Engine: sap_router.py get_route() — 6-tier decision tree
Layer 4 — Execution: MCP calls (arc-1, aibap, mcp-sap-gui, sap-rfc-mcp-server, etc.)
Layer 5 — Verification: abaplint → abap-code-review → sap-crew-analysis → transport-gate
Layer 6 — Self-Learn: self_learn.py records outcomes → adapts routing → MEMORY.md ## LEARN
```

## Key Extension Points

### Adding a New MCP Server
1. Add to `.mcp.json` → `mcpServers` object
2. Add env vars to `.env.template`
3. Add probe entry to `scripts/healthcheck.py` → `MCP_HEALTHCHECK_SPEC`
4. Add env vars to `scripts/healthcheck.py` → `OPTIONAL_ENV_FILE_VARS`
5. Update MCP count in SKILL.md, README.md, AGENTS.md, package.json
6. Add routing logic to `scripts/sap_router.py` if needed

### Adding a New Skill
1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter
2. Add skill name to SKILL.md skills list (sorted alphabetically)
3. Update README.md skill categories table
4. Update healthcheck threshold if count changes

### Adding a New CLI
1. Create `scripts/<name>.py` with argparse subcommands
2. Add npm scripts to `package.json`
3. Add to SKILL.md CLI list
4. Update healthcheck threshold (>= N scripts)

### Adding a New SAP Module
1. Create `references/module_maps/<module>_operations.md`
2. Add to fallback_engine.py → `DETAILED_GUI_MAP` (tcode + BDC + alt method)
3. Add to sap_router.py → `GUI_FALLBACK_MAP`
4. Add BAPIs to references/trench_knowledge/
5. Add to SKILL.md ZROUTER RFC Commands section

## Files That Must Stay Consistent

When any of the above changes, ALL of these must be updated:

- `SKILL.md` — skills list, MCP list, CLI list, routing table
- `README.md` — badges, skill categories, MCP details, module reference
- `AGENTS.md` — skill count, routing rules
- `.mcp.json` — server entries, routing config, notes
- `.env.template` — env vars for new services
- `scripts/healthcheck.py` — MCP probes, env vars, thresholds
- `package.json` — description counts, npm scripts
- `CHANGELOG.md` — version history
- `COMPARISON.md` — repo analysis updates

## Verification Checklist

```bash
# Pre-commit
python scripts/healthcheck.py          # All MCPs probed, .env valid
npm run abap:review:ci                 # abaplint clean
for f in scripts/*.py; do python -c "import py_compile; py_compile.compile('$f', doraise=True)"; done  # All compile
python -c "import json; json.load(open('.mcp.json'))"  # JSON valid

# Cross-file consistency
# Skills: disk == SKILL.md == README == AGENTS.md == 78
# MCPs: .mcp.json == healthcheck probes - 1 (ZROUTER) == 30
# CLIs: disk == SKILL.md == 10
# npm scripts: package.json == 60
```
