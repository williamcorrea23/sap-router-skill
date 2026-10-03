# External SAP skills and MCP integrations

This repository keeps `.agents/` as the canonical source. External repositories are
checked out under `bundled/` with a pinned revision, indexed by
`scripts/source_catalog.py`, and never become executable merely by being discovered.

## Imported skills

The current canonical catalog contains 203 skills. The additions and refreshes in this
release come from:

| Source | Scope | License observed | Status |
|---|---|---|---|
| `likweitan/abap-skills` | ABAP, RAP, CDS, OData, Clean Core | MIT | Imported and refreshed |
| `adam0thman/sap-basis-ops` | Basis, DB, SAPRouter and operational runbooks | MIT | Pinned at `6ae551f6ec2ef4c554b606fcdef5a04599e4ab11`; 21 new skills and 12 refreshed |
| `kts982/sap-odata-explorer` | SAP OData CLI usage guidance | MIT | `sap-odata-cli` imported as skill-only; CLI and MCP runtime are not installed |
| `SAP/ai-skills-library` | SAP Fiori guidance | Apache-2.0 | Imported |
| `UI5/plugins-coding-agents` | UI5 best practices, modernization and fixes | Apache-2.0 | Imported |
| `SAP/ui-theme-designer-plugins-for-coding-agents` | Theme Designer and design tokens | Apache-2.0 | Imported |
| `SAP/automation-pilot-agent-skills` | Automation Pilot command lifecycle | Apache-2.0 | Imported |
| `capire/skills` | CAP development and upgrades | Apache-2.0 | Imported |
| `jfilak/sapcli-claude-plugin` | ABAP system information and snippets | Repository license | Imported |
| `Gixsy95/abap_wiki` | ABAP knowledge-base ingestion and querying | MIT | Imported |

Use the catalog to search the merged set:

```powershell
python scripts/source_catalog.py search "SAP Basis health triage"
python scripts/source_catalog.py search "UI5 table modernization"
```

## MCPs and libraries

The following requested MCP projects are registered as fail-closed candidates. Some have pointer-only snapshots and no runnable source; registry status does not imply that a runtime can be started:

| ID | Repository | Classification | Default |
|---|---|---|---|
| `lemaiwo-btp-mcp-server` | `lemaiwo/btp-mcp-server` | BTP administration MCP | Disabled candidate |
| `aiadiguru2025-sf-mcp` | `aiadiguru2025/sf-mcp` | SuccessFactors OData MCP | Disabled candidate |
| `kts982-mcp-sap-gui` | `kts982/mcp-sap-gui` | Windows SAP GUI MCP | Disabled candidate |
| `hochfrequenz-sapgui-mcp` | `Hochfrequenz/sapgui.mcp` | SAP GUI/WebGUI MCP | Disabled candidate |
| `gavdilabs-cap-mcp-plugin` | `gavdilabs/cap-mcp-plugin` | CAP plugin that exposes services as MCP | Disabled candidate |
| `arc-mcp-xsuaa-auth` | `arc-mcp/xsuaa-auth` | XSUAA auth library for HTTP MCP hosts | Library only |
| `odata-mcp-go` | `oisee/odata_mcp_go` | Go SAP OData MCP | Disabled candidate; runtime and safety review required |
| `gutjahrai-sap-odata-mcp-py` | `GutjahrAI/sap-odata-mcp-py` | Python SAP OData MCP | Disabled candidate; pointer-only snapshot, no runtime |
| `nicohern-abapilot-mcp` | `NicoHern/abapilot-mcp` | ABAP development MCP | Disabled candidate; selected target profile is blocked DEV |

Candidates are searchable with:

```powershell
python scripts/mcp_launcher.py search --query "BTP administration"
python scripts/mcp_launcher.py search --query "SuccessFactors employee data"
```

Promotion requires a reviewed entry in `.agents/registries/mcps.json`, a runtime
probe, declared environment references, and approval semantics for writes. Do not put
credentials in this repository or enable all candidates at once.

### ABAPilot DEV trial profile

`.agents/registries/mcp-target-profiles.json` records the requested `nicohern-abapilot-mcp-dev`
target. The connector is pinned to upstream commit `25639b76f6d3f53ae029af73913370af56a1e980`
and package `abapilot@1.0.6`; its runtime is not installed or fetched. The profile remains
`blocked`, and the MCP candidate remains disabled and absent from active server configuration.
Its proposed default-deny read allowlist is restricted to code/object metadata and syntax
checks; write, program execution, transaction, variant, translation, and note-upload tools
are explicitly denied. This client-side filter does not replace server-side SAP authorization.

Activation still requires the licensed ABAPilot backend installed on the exact DEV system,
system ID/client/release and HTTPS endpoint, credentials held outside the repository, a
captured `tools/list` schema review, and verified DEV authorization/audit behavior. No live
SAP check has run. See `.agents/registries/mcp-target-profiles.json` for machine-readable gates.

## Global availability

Regenerate repository assets and copy the canonical skills to the user-level Claude,
Gemini/Antigravity and Codex directories:

```powershell
python scripts/generate_ide_assets.py generate --targets all --global
```

This updates `~/.claude/skills`, `~/.gemini/config/skills`, and `~/.codex/skills`,
plus the global Codex `AGENTS.md`. MCPs remain globally discoverable through the
repository registry; client-specific MCP configuration should be enabled one server
at a time after promotion and local dependency installation.

Validate parity after synchronization:

```powershell
python scripts/generate_ide_assets.py check
python scripts/source_catalog.py status
```
