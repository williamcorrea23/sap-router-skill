# Changelog

## [4.2.0] — 2026-07-01

### Added
- **abap-mcp** integration (DimiDR/ABAP-MCP) for advanced agentic ABAP development (method surgery, DDIC validation, Clean ABAP workflow).
- **mcp-calm-server** integration (fr0ster/mcp-calm-server) for SAP Cloud ALM services.
- **sap-transport-mcp** integration (Nidhideep/sap-transport-mcp) for Change and Transport System (CTS) management.
- **Intelligent Dynamic Routing**: updated `sap_router.py` to route requests dynamically to `abap-mcp`, `mcp-calm-server`, and `sap-transport-mcp` based on requested actions and keywords.
- Registered all new servers in `.mcp.json`, `.env.template`, and `healthcheck.py`.

## [4.1.0] — 2026-07-01

### Added
- **mcp-integration-suite** integration (1nbuc/mcp-integration-suite) for managing Integration Packages, iFlows, message mapping, and monitoring.
- **ci-mcp-server** integration (lemaiwo/ci-mcp-server) mapping the CPI OData V2 API to MCP tools.
- Registered new servers in `.mcp.json`, `.env.template`, and `healthcheck.py`.

## [4.0.0] — 2026-06-26

### Added
- **Karpathy command format** — 4-principle behavioral wrapper (Think→Simplify→Surgical→Verify)
- **SAP GUI Scripting support** — 3 MCP servers, 27 transaction fallbacks, BDC patterns
- **TieredFallback engine** — 6-tier cascading fallback: ADT→RFC→GUI→BDC→Offline→Manual
- **Self-learn engine** — Hermes-style context adaptation, MCP latency/reliability tracking
- **Healthcheck guardian** — probes all 22 MCPs + ZROUTER, .env verification, interactive prompts
- **ZROUTER Bootstrap** — probe, install (ADT/GUI/Offline), auto-repair, fallback routing
- **CSV BAPI mapping validator** — fuzzy header match, required field check, JSON payload generation
- **8-stage spec-to-transport pipeline** with peer review at stages 3 and 7
- **RAG connectors** — Pinecone, Supabase pgvector, Azure AI Search (pre-ready)
- **6 new skills**: `karpathy-guidelines`, `sap-gui-scripting`, `sap-gui-web-enrich`, `sap-self-learn`,
  `abap-code-review`, `sap-transport-gate`, `btp-cloud-foundry`, `sap-api-policy`, `sap-llm-engineering`,
  `sap-workflow-pipeline`
- **4 new Python CLIs**: `healthcheck.py`, `self_learn.py`, `fallback_engine.py`, `zrouter_bootstrap.py`
- **9 new MCP servers**: `mcp-sap-gui` (3 tiers), `sap-cpi`, `cf-cli-mcp`, `sap-api-management`,
  `sf-mcp`, `sap-rfc-mcp-server`, `pinecone-rag`, `supabase-rag`, `azure-ai-search`
- **36 npm scripts total** — update, install, healthcheck, learn, gui enrich, pipeline, CPI, CSV
- **abaplint watch mode** + pre-release transport gate
- **Caveman integration** — cavecrew-investigator/builder/reviewer wired into routing

### Changed
- `SKILL.md` — full Karpathy rewrite with 4-principle wrapper + decision tree
- `README.md` — 8 Mermaid diagrams, skill catalog, MCP reference, module BAPI map
- `sap_router.py` — ZROUTER state awareness, auto-probe, TieredFallback integration
- `.mcp.json` — 19→22 MCPs, immediate GUI fallback, self-learn enabled, RAG priority
- `package.json` — 40→60 npm scripts, v4.0 metadata
- `AGENTS.md` — 72→78 skills, v3.0 routing tree
- All Python scripts — f-string modernization, type hints (fallback_engine.py), dead code removal
- `COMPARISON.md` — 70 repos analyzed, 7 missed repos integrated, GUI reclassified as in-scope

### Fixed
- `_check_object_adt` dead stub in `zrouter_bootstrap.py` — now reads cached ZROUTER state
- `serialize` npm script missing subcommand — now defaults to `package`
- SKILL.md skills list deduplicated (was ~22 duplicates)
- All cross-file counts synchronized (78 skills, 22 MCPs, 10 CLIs)
- `healthcheck.py` docstring count corrected (22 MCPs + ZROUTER)
- Unicode characters replaced with ASCII in all scripts
- Broken `.format()` calls from f-string batch conversion repaired
- `_get_gui_fallback_for_action` orphan method removed from sap_router.py

## [3.0.0] — 2026-06-26
- SAP GUI MCP integration with immediate fallback
- Caveman sub-agent delegation in routing tree
- Spec-to-transport pipeline with abaplint peer review
- 75 skills, 19 MCPs, 8 CLIs

## [2.0.0] — 2026-06-26
- 54 Claude Code skills across all SAP domains
- 6 Python CLIs, 11 MCP servers, ABAP peer review pipeline
- COMPARISON.md with 62-repo analysis

## [1.0.0] — Initial Release
- 3 Python CLIs, 3 ABAP templates, 15 smoke tests
