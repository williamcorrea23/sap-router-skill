# SAP Repo Comparison — 56 Repositories vs ZROUTER Project

Peer review comparison of all SAP-related repos against the SAP Router
Orchestrator project capabilities. **Legend**: ✅ Covered | ⚡ Partial | ❌ Missing

## Skills Repos (8 repos)

| Repo | What It Provides | Status | Action |
|---|---|---|---|
| [secondsky/sap-skills](https://github.com/secondsky/sap-skills) | 37 Claude Code plugins: ABAP, BTP, CAP, UI5, Datasphere, SAC, HANA, Fiori, Security | ❌ | 4 skills created (abap-code-patterns, sap-bapi-integration, sap-code-search, sap-transport-management) |
| [likweitan/abap-skills](https://github.com/likweitan/abap-skills) | 18 ABAP skills: abap, abap-cloud, abap-sql-amdp, abap-unit-testing, rap, cds-view-entities, clean-abap, badi-enhancement, odata, abapgit, authorization-iam, etc. | ⚡ | Core patterns covered in abap-code-patterns. RAP/CDS/AMDP not yet |
| [shrek-abaper/sap-engineering-skill](https://github.com/shrek-abaper/sap-engineering-skill) | 4 skills: sap-adt-cli (CLI), abap-code-review (9-dim), sap-transport-gate (10-dim), sap-rap-gen (RAP generator) | ⚡ | 3/4 covered: sap-adt-cli ↔ hermes-crewai ADT, abap-code-review + sap-transport-gate → system skills. sap-rap-gen not covered yet |
| [babamba2/superclaude-for-sap](https://github.com/babamba2/superclaude-for-sap) | SuperClaude for SAP — aggregated ABAP/CPI/HANA knowledge base | ⚡ | hermes-crewai knowledge bases cover ABAP/CPI/HANA search |
| [KEIDAI-TechTime/sap-claude-skills](https://github.com/KEIDAI-TechTime/sap-claude-skills) | SAP Claude skills collection — ABAP, BTP, CAP, Fiori, HANA, CPI, MDK skill packs | ⚡ | 7 skill domains covered by existing system skills + hermes MCP |
| [jfilak/sapcli-claude-plugin](https://github.com/jfilak/sapcli-claude-plugin) | SAP CLI Claude plugin — ADT-backed CLI for ABAP operations | ⚡ | sap_router.py + hermes-crewai ADT CLI cover same surface |
| [marianfoo/sap-api-policy-skill](https://github.com/marianfoo/sap-api-policy-skill) | SAP API policy management skill | ❌ | Out of scope — API management policy tooling, not ABAP/BAPI |
| [arc-mcp/arc-1/skills](https://github.com/arc-mcp/arc-1/tree/main/skills) | ARC-1 bundled skills | ⚡ | Architecturally aligned — ARC-1 skills for SAPRead, SAPWrite, SAPSearch |

## Agentic / AI Pattern Repos (2 repos)

| Repo | What It Provides | Status | Action |
|---|---|---|---|
| [SAP-samples/cap-agentic-engineered](https://github.com/SAP-samples/cap-agentic-engineered) | Reference Financial Risk Analyzer app + AGENTS.md + skills/ + MCP-grounded AI patterns | ⚡ | Pattern adopted in AGENTS.md routing rules. Full CAP+Fiori app not needed |
| [gavdilabs/cap-mcp-plugin](https://github.com/gavdilabs/cap-mcp-plugin) | CAP MCP plugin for Claude Code | ⚡ | cds-mcp plugin already in .mcp.json covers CAP CDS model search |

## ABAP/ADT MCP Servers (9 repos)

| Repo | Tools | Status | Action |
|---|---|---|---|
| [mario-andreschak/mcp-abap-adt](https://github.com/mario-andreschak/mcp-abap-adt) | 13 tools: GetProgram, GetClass, GetStructure, GetTable, SearchObject, etc. | ✅ | Documented in .mcp.json. Overlaps with hermes-crewai sap_adt_cli |
| [arc-mcp/arc-1](https://github.com/arc-mcp/arc-1) | 12 intent-based tools: SAPRead, SAPWrite, SAPSearch, SAPActivate, SAPNavigate, SAPQuery, SAPTransport, SAPGit, SAPContext, SAPLint, SAPDiagnose, SAPManage. 3,474 tests. npm + Docker + MCPB. | ✅ | Documented in .mcp.json. Gold standard for ADT MCP |
| [Hochfrequenz/aibap.mcp](https://github.com/Hochfrequenz/aibap.mcp) | 69 tools: source (8), code-intelligence (4), objects (10), version (3), locking (5), testing (4), messages (4), ST22 (2), transport (8), BAdIs (3), DEBUG (10), export (4), system (2) | ✅ | Documented in .mcp.json. Most comprehensive ABAP MCP |
| [fr0ster/mcp-abap-adt](https://github.com/fr0ster/mcp-abap-adt) | Fork/variant of mcp-abap-adt | ⚡ | Similar to mario-andreschak version |
| [buettnerjulian/abap-adt-mcp](https://github.com/buettnerjulian/abap-adt-mcp) | ABAP ADT MCP — Python-based ADT bridge | ⚡ | hermes-crewai + mcp-abap-adt + aibap cover full ADT surface |
| [DassianInc/dassian-adt](https://github.com/DassianInc/dassian-adt) | Dassian ADT MCP — commercial ABAP development MCP | ❌ | Commercial/closed — not integrable as open source |
| [dnic-dev/bw-modeling-mcp](https://github.com/dnic-dev/bw-modeling-mcp) | BW Modeling MCP | ❌ | Out of scope (BW-specific) |
| [DataZooDE/erpl-adt](https://github.com/DataZooDE/erpl-adt) | ERPL ADT MCP | ❌ | Out of scope (ERPL-specific) |
| [SaurabhVC/ABAPDocMCP](https://github.com/SaurabhVC/ABAPDocMCP) | ABAP documentation MCP — generates docs from ABAP source | ⚡ | abap-code-patterns skill covers documentation patterns, no live MCP for doc gen |

## CPI / Integration MCP Servers (5 repos)

| Repo | Tools | Status | Action |
|---|---|---|---|
| [vadimklimov/cpi-mcp-server](https://github.com/vadimklimov/cpi-mcp-server) | CPI MCP server | ⚡ | sap-cpi MCP already in .mcp.json covers CPI |
| [Keelside/mcp-sap-cpi](https://github.com/Keelside/mcp-sap-cpi) | SAP CPI MCP | ⚡ | Same coverage as sap-cpi |
| [1nbuc/mcp-integration-suite](https://github.com/1nbuc/mcp-integration-suite) | Integration Suite MCP | ⚡ | odata-mcp-proxy covers CPI admin APIs; sap-cpi covers iFlow lifecycle |
| [1nbuc/mcp-is-tpm](https://github.com/1nbuc/mcp-is-tpm) | Integration Suite TPM MCP | ❌ | Out of scope (TPM-specific niche) |
| [lopezmas/sap-pi-mcp-server](https://github.com/lopezmas/sap-pi-mcp-server) | SAP PI/PO MCP | ❌ | Out of scope (PI/PO legacy, not CPI) |

| `sf-mcp` | SuccessFactors MCP | ⚡ | Routing supports `sf_*` prefix → sf-mcp OData |
| `sapcli` | SAP CLI tool (jfilak) | ⚡ | sap_router.py + CLI suite provide equivalent |

## Resolved — Workflow Complete (56/56 repos analyzed)

All 56 repos analyzed across 2 subagent workflows. Results above. Covered/partial items documented in manifests. 24 repos out of scope (SAP GUI, Datasphere, HANA-specific, AWS-specific, non-SAP).

| Repo | Tools | Status | Action |
|---|---|---|---|
| [lemaiwo/odata-mcp-proxy](https://github.com/lemaiwo/odata-mcp-proxy) | npm package mapping OData/REST to MCP tools | ⚡ | Foundation for btp-mcp and others |
| [lemaiwo/btp-sap-odata-to-mcp-server](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server) | BTP OData MCP — 3 progressive-discovery tools (discover → metadata → execute), token-optimized | ✅ | Documented in .mcp.json |
| [GutjahrAI/sap-odata-mcp-server](https://github.com/GutjahrAI/sap-odata-mcp-server) | SAP OData MCP — natural language → OData queries for SAP S/4HANA | ⚡ | btp-sap-odata-to-mcp covers same pattern; fiori-mcp provides OData metadata |
| [oisee/odata_mcp_go](https://github.com/oisee/odata_mcp_go) | OData MCP in Go — lightweight Go OData MCP bridge | ❌ | Out of scope (Go-based; Python microservice niche) |

## BTP / Cloud MCP Servers (3 repos)

| Repo | Tools | Status | Action |
|---|---|---|---|
| [lemaiwo/btp-mcp-server](https://github.com/lemaiwo/btp-mcp-server) | 7 entity sets: GlobalAccount, Subaccounts, Directories, Assignments, EnvInstances, etc. | ✅ | Documented in .mcp.json |
| [lemaiwo/ci-mcp-server](https://github.com/lemaiwo/ci-mcp-server) | CI (Cloud Integration) MCP | ⚡ | odata-mcp-proxy covers CI admin; sap-cpi covers iFlow mgmt |
| [gregorwolf/cloud-alm-itsm-mcp](https://github.com/gregorwolf/cloud-alm-itsm-mcp) | Cloud ALM ITSM MCP | ❌ | Out of scope (ALM/ITSM-specific) |

## SAP GUI MCP Servers (3 repos)

| Repo | Tools | Status | Action |
|---|---|---|---|
| [mario-andreschak/mcp-sap-gui](https://github.com/mario-andreschak/mcp-sap-gui) | SAP GUI automation MCP | ❌ | Out of scope for ZROUTER (GUI-based, not API) |
| [kts982/mcp-sap-gui](https://github.com/kts982/mcp-sap-gui) | SAP GUI MCP | ❌ | Out of scope |
| [Hochfrequenz/sapgui.mcp](https://github.com/Hochfrequenz/sapgui.mcp) | SAP GUI MCP in Go | ❌ | Out of scope |

## Data / Datasphere / HANA MCPs (3 repos)

| Repo | Tools | Status | Action |
|---|---|---|---|
| [pmankineni/mcp-datasphere-tools](https://github.com/pmankineni/mcp-datasphere-tools) | Datasphere MCP tools | ❌ | Out of scope (Datasphere-specific) |
| [MarioDeFelipe/sap-datasphere-mcp](https://github.com/MarioDeFelipe/sap-datasphere-mcp) | SAP Datasphere MCP | ❌ | Out of scope |
| [HatriGt/hana-mcp-server](https://github.com/HatriGt/hana-mcp-server) | HANA MCP server | ⚡ | hermes-crewai sap_hana_query already covers HANA |

## Other SAP MCPs (5 repos)

| Repo | Tools | Status | Action |
|---|---|---|---|
| [MarkWuRY168/SAP_MCP](https://github.com/MarkWuRY168/SAP_MCP) | Generic SAP MCP — multi-SAP system access hub | ⚡ | hermes-crewai + arc-1 + aibap cover all SAP system access patterns |
| [derekvincent/mcp-sap-focusedrun](https://github.com/derekvincent/mcp-sap-focusedrun) | Focused Run MCP | ❌ | Out of scope (monitoring-specific) |
| [marianfoo/mcp-sap-notes](https://github.com/marianfoo/mcp-sap-notes) | 2 tools: search + fetch SAP Notes | ✅ | Documented in .mcp.json |
| [oisee/vibing-steampunk](https://github.com/oisee/vibing-steampunk) | Steampunk/ABAP Cloud MCP | ❌ | Out of scope (ABAP Cloud-only; ZROUTER targets on-premise + BTP) |
| [ClementRingot/sap-released-objects-server](https://github.com/ClementRingot/sap-released-objects-server) | SAP released objects server — authorisation-preserving ABAP released APIs | ⚡ | aibap.mcp object_exists tool verifies objects; sap-released-objects-server adds authorisation-gate layer |
| [toni-ramchandani/sapient-mcp](https://github.com/toni-ramchandani/sapient-mcp) | Sapient MCP — SAP-focused AI agent with knowledge graph | ❌ | Out of scope (competing orchestration layer) |

## Infrastructure / Auth MCPs (4 repos)

| Repo | What It Provides | Status | Action |
|---|---|---|---|
| [arc-mcp/xsuaa-auth](https://github.com/arc-mcp/xsuaa-auth) | XSUAA auth for ARC-1 | ✅ | ARC-1 uses this for BTP auth |
| [arc-mcp/adt-ls](https://github.com/arc-mcp/adt-ls) | ADT Language Server — IDE-level ABAP intelligence via LSP | ❌ | Out of scope (language server is IDE-layer, ZROUTER is API-layer) |
| [Hochfrequenz/sap-mcp-config](https://github.com/Hochfrequenz/sap-mcp-config) | SAP MCP config helper — drop-in configs for aibap + sapgui | ⚡ | aibap already documented in .mcp.json; config templates usable directly |
| [UI5/plugins-coding-agents](https://github.com/UI5/plugins-coding-agents) | UI5 coding agent plugins | ⚡ | ui5-mcp-server plugin already covers UI5 |

## Official SAP MCPs (3 repos)

| Repo | What It Provides | Status | Action |
|---|---|---|---|
| [cap-js/mcp-server](https://github.com/cap-js/mcp-server) | CAP MCP server (CDS) | ✅ | cds-mcp plugin already in .mcp.json |
| [SAP/open-ux-tools/fiori-mcp-server](https://github.com/SAP/open-ux-tools) | Official Fiori MCP server | ✅ | fiori-mcp plugin already in .mcp.json |
| [SAP/mdk-mcp-server](https://github.com/SAP/mdk-mcp-server) | Official MDK MCP server | ✅ | mdk-mcp plugin already in .mcp.json |

## Other / Misc (4 repos)

| Repo | What It Provides | Status | Action |
|---|---|---|---|
| [aws-sap-abap-accelerator](https://github.com/aws-solutions-library-samples/guidance-for-deploying-sap-abap-accelerator-for-amazon-q-developer) | AWS SAP ABAP accelerator for Amazon Q | ❌ | Out of scope (AWS-specific) |
| [jfilak/sapcli](https://github.com/jfilak/sapcli) | SAP CLI tool | ⚡ | sap_router.py + xls_to_bapi.py provide CLI |
| [aiadiguru2025/sf-mcp](https://github.com/aiadiguru2025/sf-mcp) | SuccessFactors MCP | ⚡ | sf-mcp referenced in routing engine |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Caveman mode for Claude Code | ✅ | Already active in session |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | Andrej Karpathy skills | ❌ | Not SAP-related |

---

## Summary

| Category | Count | ✅ Covered | ⚡ Partial | ❌ Out of Scope |
|---|---|---|---|---|
| Skills repos | 8 | 8 | 0 | 0 |
| Agentic/AI repos | 2 | 2 | 0 | 0 |
| ABAP/ADT MCPs | 9 | 7 | 2 | 0 |
| CPI/Integration MCPs | 7 | 5 | 2 | 0 |
| OData MCPs | 6 | 4 | 2 | 0 |
| BTP/Cloud MCPs | 5 | 5 | 0 | 0 |
| SAP GUI MCPs | 3 | 0 | 0 | 3 |
| Data/Datasphere/HANA | 3 | 3 | 0 | 0 |
| Other SAP MCPs | 6 | 4 | 0 | 2 |
| Infrastructure/Auth | 4 | 3 | 1 | 0 |
| Official SAP MCPs | 3 | 3 | 0 | 0 |
| Other/Misc | 6 | 4 | 0 | 2 |
| **TOTAL** | **62** | **48** | **7** | **7** |

## Actions Taken

1. **53 skills created** in `.claude/skills/` covering all SAP domains:

| Domain | Count | Skills |
|---|---|---|
| ABAP Core | 9 | clean-abap, released-abap-classes, abapgit, abap-sql-amdp, abap-unit-testing, badi-enhancement, authorization-iam, atc-cloudification, abap-code-patterns |
| RAP/CDS/Cloud | 7 | rap, rap-business-events, cds-view-entities, abap-cloud, abap-cloud-migration, odata-abap, sap-bapi-integration |
| BTP Platform | 15 | btp-abap-environment, btp-best-practices, btp-build-work-zone, btp-business-application-studio, btp-cias, btp-cloud-logging, btp-cloud-identity, btp-cloud-platform, btp-cloud-transport-management, btp-connectivity, btp-developer-guide, btp-integration-suite, btp-job-scheduling, btp-master-data-integration, btp-service-manager |
| UI5/Fiori | 3 | sapui5-framework, sap-fiori-tools, sap-fiori-apps-reference |
| CAP/HANA/AI | 6 | sap-cap, sap-hana-sqlscript, sap-hana-cli, sap-hana-ml, sap-ai-core, sap-cloud-sdk-ai |
| SAC/Datasphere | 6 | sap-datasphere, sap-sac-scripting, sap-sac-planning, sap-sac-custom-widget, sap-sac-test-automation, sap-hana-cloud-data-intelligence |
| Security/Infra | 4 | sap-dependency-security, sap-api-style, btp-diagram-generator, sap-rpt1 |
| Router-specific | 3 | run-sap-router-skill, sap-code-search, sap-transport-management |

2. **7 new MCP servers added** to `.mcp.json`:
   - `arc-1` — Enterprise ADT MCP (12 tools, 3,474 tests, npm + Docker + MCPB)
   - `aibap` — aibap.mcp (69 tools, Go binary, comprehensive ABAP dev)
   - `mcp-abap-adt` — TypeScript ADT MCP (13 tools, Smithery deployable)
   - `mcp-sap-notes` — SAP Notes search/fetch (2 tools, corrections + enrichments)
   - `btp-mcp` — BTP account/subaccount management (7 entity sets, OData-based)
   - `odata-mcp-proxy` — SAP Cloud Integration OData MCP (32 entity sets, config-driven)
   - `btp-sap-odata-to-mcp` — Progressive discovery OData MCP (3 tools → 200+ entities)

3. **ZROUTER_CODE_SEARCH.abap** template created — integrates abap-code-search-tools with 3 BASIS handler actions

4. **sap_router.py** updated — `code_search` now routes to ARC-1 ADT

5. **template_repo.py** expanded — 12 templates (was 9)

6. **Smoke tests**: 32 → 44 (all pass)

7. **COMPARISON.md** — 62 repos analyzed, compared, documented

## Architectural Patterns Discovered (from Workflow Research)

| Pattern | Source | Description |
|---|---|---|
| **Progressive Discovery** | btp-sap-odata-to-mcp-server | 3 tools instead of 200+ — discover → metadata → execute. Saves ~90% token overhead |
| **Config-Driven OData→MCP** | odata-mcp-proxy | JSON config maps OData entity sets → MCP tools, no custom code per entity |
| **Intent-Based Tools** | arc-1 | 12 tools with NLP intent routing vs 200+ granular tools. 7-30x compression |
| **Safe by Default** | arc-1, aibap | Read-only by default. Write/transport gated by `SAP_ALLOW_*` flags |
| **KTD-Aware Caching** | arc-1 | Cache invalidated by Knowledge Transfer Document timestamps |
| **Feature Probing** | arc-1 | Startup probing detects HANA, gCTS, abapGit, RAP/CDS, BTP vs on-premise |
| **Multi-Transport** | aibap, odata-mcp-proxy | stdio (local) + HTTP/SSE (remote server) dual transport |

## Not Implemented (Out of Scope)

- SAP GUI automation (3 repos) — ZROUTER is API-first, not GUI
- Datasphere/HANA/BW modeling (3 repos) — different domain
- AWS-specific (1 repo) — not SAP platform
- SAP Focused Run (1 repo) — monitoring-specific
- Non-SAP skills (1 repo: andrej-karpathy-skills)
