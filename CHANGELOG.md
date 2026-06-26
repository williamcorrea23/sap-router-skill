# Changelog

## [2.0.0] — 2026-06-26

### Added
- **54 Claude Code skills** covering all SAP domains (ABAP, RAP, CDS, BTP, CAP, UI5, Fiori, HANA, SAC, CPI, AI)
- **6 Python CLIs**: `sap_router.py`, `memory_manager.py`, `xls_to_bapi.py`, `template_repo.py`, `abap_serializer.py`, `cpi_iflow_packager.py`
- **16 MCP server** configurations in `.mcp.json` (arc-1, aibap, mcp-abap-adt, mcp-sap-notes, btp-mcp, odata-mcp-proxy, btp-sap-odata-to-mcp, hermes-crewai, sap-cpi, UI5, Fiori, MDK, CDS, Azure, Desktop Commander, mobile-webapp-crew)
- **ABAP peer review pipeline**: abaplint via npm scripts (`npm run abap:lint`, `npm run abap:review`, `npm run abap:review:ci`)
- **ZROUTER_CODE_SEARCH.abap**: integration with DevEpos/abap-code-search-tools (3 BASIS handler actions)
- **CPI iFlow development**: full Groovy pattern library, `cpi_iflow_packager.py` ZIP tool
- **Installation guide**: 6-step ZROUTER deployment via ADT MCP tools
- **50 smoke tests**: covering routing, memory, XLS/BAPI, template repo, ABAP serializer, CPI packager
- **12 template seeds** in `template_repo.py` (was 9)
- **29 xls_to_bapi actions** (was 26) — added CODE_SEARCH, CODE_SEARCH_STATS, CODE_SEARCH_ADT
- **COMPARISON.md**: 62-repository cross-reference analysis
- `README.md`, `LICENSE`, `.gitignore`, `CHANGELOG.md`, `.abaplint.json`
- `references/` — 14 trench knowledge files + 10 module operation maps

### Changed
- `sap_router.py`: added `code_search` routing to ARC-1 ADT
- `xls_to_bapi.py`: expanded to 29 actions across 9 modules
- `template_repo.py`: 12 seed templates
- `abap_serializer.py`: fixed INTERFACE regex bug in `_split_abap_objects()`
- `ZROUTER_DISPATCH.abap`: added `evaluate_expression` method to abstract handler

### Fixed
- `abap_serializer.py`: INTERFACE regex `\s+` requirement broke on `INTERFACE zif_foo.` — fixed to no trailing requirement
- 8 BAPI name corrections (QM, PP, WM, CO, SD, FI, BASIS)
- `template_repo.py`: `cmd_init()` and `cmd_list()` signatures fixed (added `_args` parameter)

## [1.0.0] — Initial Release

- 3 Python CLIs: `sap_router.py`, `memory_manager.py`, `xls_to_bapi.py`
- 3 ABAP templates: `ZROUTER_DISPATCH.abap`, `ZCL_ABAP_REPL_V2.abap`, `ZROUTER_DB_TABLES.abap`
- 15 smoke tests
- 26 BAPI actions in `xls_to_bapi.py`
- 9 template seeds
- Basic AGENTS.md routing table
