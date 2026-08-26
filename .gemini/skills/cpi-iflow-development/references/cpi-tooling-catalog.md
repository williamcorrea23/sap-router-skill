# CPI community tooling catalog

Snapshot: 2026-08-12. Revisions are the latest default-branch commit observed through
the GitHub API. Star counts are discovery signals only, never trust or quality gates.
No source code is vendored by this catalog.

## Reuse policy

- Reimplement useful patterns natively and retain attribution for MIT/Apache-2.0 sources.
- Invoke GPL-3.0 tools only as separately installed external processes; never copy,
  link, bundle, or auto-install them.
- Treat repositories without a detected license as ideas/documentation only.
- Keep every community MCP disabled until its revision, runtime, authentication,
  tool effects, and tests are reviewed and promoted in the canonical registry.

## Assessed repositories

| Repository | Revision / commit date | Stars | License | Useful area | Decision |
|---|---:|---:|---|---|---|
| [mwittrock/cpilint](https://github.com/mwittrock/cpilint) | `cf4a966ad44c` / 2025-05-13 | 77 | MIT | iFlow lint/governance | Optional `CPILINT_CMD`; structural validator remains built in |
| [outoftheboxea/SAPCPI](https://github.com/outoftheboxea/SAPCPI) | `6b2ba6f34e6c` / 2026-06-08 | 44 | none detected | Groovy examples | Ideas only; no code reuse |
| [codebude/cpi-dashboard](https://github.com/codebude/cpi-dashboard) | `269c701af1ad` / 2020-11-24 | 32 | MIT | Monitoring dashboard | Adapt concise overview/failed-message presentation |
| [vadimklimov/cpi-navigator](https://github.com/vadimklimov/cpi-navigator) | `97440581ae98` / 2026-06-30 | 24 | MIT | Read-only content navigation | Adapt API-first, bounded read workflows |
| [vadimklimov/cpi-mcp-server](https://github.com/vadimklimov/cpi-mcp-server) | `6f53566b4098` / 2026-06-30 | 23 | MIT | Content/runtime MCP | Adapt tool coverage; retain disabled candidate |
| [pizug/cpi-sync](https://github.com/pizug/cpi-sync) | `ac85228ed88e` / 2022-02-17 | 20 | GPL-3.0 | CPI/Git synchronization | Optional external `CPI_SYNC_CMD` only |
| [pizug/cpi-mapping-test](https://github.com/pizug/cpi-mapping-test) | `fec658d65add` / 2020-09-20 | 13 | GPL-3.0 | Mapping tests | Optional external `CPI_MAPPING_TEST_CMD` only |
| [fatihpense/JavaMappingExampleCPI](https://github.com/fatihpense/JavaMappingExampleCPI) | `604a9c48c090` / 2018-03-19 | 10 | MIT | Java mapping example | Reference/test-fixture patterns only |
| [codebude/iflow-plotter](https://github.com/codebude/iflow-plotter) | `2ef55aa385ee` / 2021-04-26 | 8 | MIT | iFlow visualization | Optional `CPI_IFLOW_PLOTTER_CMD` with approved output write |
| [contiva/cloud-connector-helper](https://github.com/contiva/cloud-connector-helper) | `3f8f314a3621` / 2026-07-09 | 7 | MIT | Cloud Connector diagnostics | Reference for connectivity diagnostics; not a CPI runtime dependency |
| [vadimklimov/steampipe-plugin-cpi](https://github.com/vadimklimov/steampipe-plugin-cpi) | `5a3dc6207fa2` / 2026-06-30 | 6 | Apache-2.0 | SQL reads over CPI | Optional `CPI_STEAMPIPE_CMD`; allow one SELECT only |
| [Manojkh/ConVista-CPI-Helper-Chrome-Extension](https://github.com/Manojkh/ConVista-CPI-Helper-Chrome-Extension) | `7e992ccc8379` / 2020-03-03 | 6 | none detected | Browser helper | Ideas only; Web UI fallback stays canonical |
| [MartinPankraz/SAPCPI-Az-DevOps](https://github.com/MartinPankraz/SAPCPI-Az-DevOps) | `6f823358350e` / 2020-07-29 | 6 | Apache-2.0 | Azure DevOps lifecycle | Adapt plan-before-deploy concepts |
| [rsugio/cpi](https://github.com/rsugio/cpi) | `b4ecc344718c` / 2021-02-09 | 5 | Apache-2.0 | CPI examples | Reference patterns only |
| [fatihpense/supereasy-partnerui-for-cpi](https://github.com/fatihpense/supereasy-partnerui-for-cpi) | `d4764ee798c5` / 2019-11-29 | 5 | none detected | Partner Directory UI | Ideas only |
| [outoftheboxea/academySAPCPI](https://github.com/outoftheboxea/academySAPCPI) | `bf8a99993adc` / 2026-02-15 | 5 | none detected | Learning content | Documentation reference only |
| [MartinPankraz/SAP-CPI-Azure-Monitor](https://github.com/MartinPankraz/SAP-CPI-Azure-Monitor) | `f29e054a04da` / 2022-08-05 | 5 | Apache-2.0 | Failed MPL monitoring | Adapt filter/status/alert concepts |
| [asbrucon/CPIops](https://github.com/asbrucon/CPIops) | `b5fe9f3c0d70` / 2026-07-28 | 5 | Apache-2.0 | CAP portal, sync state, quality gate | Adapt overview and quality/sync status UX |
| [nageshwarrao19/XSLTmappings](https://github.com/nageshwarrao19/XSLTmappings) | `3d1530effef2` / 2019-01-31 | 4 | none detected | XSLT samples | Ideas/test inputs only |
| [santhoshvellingiri/SAP-CPI-Tool](https://github.com/santhoshvellingiri/SAP-CPI-Tool) | `ead2679b03bf` / 2023-01-08 | 4 | MIT | Desktop CPI utility | Reference patterns only |
| [karthickshiva-png/sap-cpi-mcp-server](https://github.com/karthickshiva-png/sap-cpi-mcp-server) | `651d9dce3fcf` / 2026-08-10 | 4 | MIT | Native CPI/OpenAPI MCP | Concepts only; very new disabled candidate |
| [Asutosh-Integration/SAP-CPI](https://github.com/Asutosh-Integration/SAP-CPI) | `b200467f2092` / 2020-12-28 | 2 | MIT | JavaScript CPI examples | Reference patterns only |
| [Youssef-Sa3d/procurement-request-approval-portal](https://github.com/Youssef-Sa3d/procurement-request-approval-portal) | `350d5a8eb44f` / 2026-05-12 | 2 | none detected | Approval portal | Ideas only; approval broker remains authoritative |
| [habilaltin/cpi_tools](https://github.com/habilaltin/cpi_tools) | `856a39d60b38` / 2023-03-18 | 1 | none detected | CPI helper scripts | Ideas only |
| [crsrikanth-07/sap-cpi-iflow-generator](https://github.com/crsrikanth-07/sap-cpi-iflow-generator) | `83cde6150715` / 2026-03-31 | 1 | Apache-2.0 | Template-driven iFlow generation | Adapt local generation workflow through existing packager |
| [SunitG72/SAP_CPI_iFlows](https://github.com/SunitG72/SAP_CPI_iFlows) | `9ececce67d41` / 2026-04-04 | 1 | none detected | iFlow examples | Documentation ideas only |
| [Pavan-29/All-in-one-tools-for-CPI](https://github.com/Pavan-29/All-in-one-tools-for-CPI) | `26d751b51348` / 2026-05-30 | 1 | none detected | Multi-tool UI | Ideas only |
| [ManojAdhithya/sap-ci-html-to-pdf](https://github.com/ManojAdhithya/sap-ci-html-to-pdf) | `90a0a1f01cc8` / 2025-10-19 | 1 | MIT | HTML/PDF iFlow example | Reference pattern only |
| [sahil-sachdev/SAP-CI-CPI-iFlow-Technical-Specification-Generator-using-Generative-AI](https://github.com/sahil-sachdev/SAP-CI-CPI-iFlow-Technical-Specification-Generator-using-Generative-AI) | `181a2d858ae6` / 2025-09-19 | 1 | none detected | Technical specification generation | Ideas only |
| [DrAlgoStrange/Tenant-Management-Tool-SAP-BTP-Integration-Suite](https://github.com/DrAlgoStrange/Tenant-Management-Tool-SAP-BTP-Integration-Suite) | `041259438189` / 2025-08-26 | 1 | none detected | Tenant management | Ideas only; out of runtime scope |
| [rameshvaranganti/SAPCPI](https://github.com/rameshvaranganti/SAPCPI) | `c8d32f31e723` / 2026-01-24 | 0 | none detected | CPI examples | Documentation ideas only |
| [kumarprem886/sap-cpi-assistant](https://github.com/kumarprem886/sap-cpi-assistant) | `5f2dc11931bd` / 2026-06-21 | 0 | none detected | CPI assistant | Ideas only; no runtime dependency |

## Runtime promotion gate

Before promoting any candidate: pin an immutable revision, verify license, install
outside this workflow, enumerate tools, classify effects, validate auth/roles, test
timeouts and redaction, add it to `mcps.json`, then update capability routing. Until
all steps pass, keep it in `mcp-candidates.json` and `.mcp.json/plannedServers`.
