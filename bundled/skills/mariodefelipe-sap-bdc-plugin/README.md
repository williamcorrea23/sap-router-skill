# sap-bdc — Cowork plugin for SAP Business Data Cloud

Version 0.5.0 · MIT license · Mario de Felipe

A human-facing plugin for anyone working with **SAP Business Data Cloud (BDC)** — admins, support engineers, integration developers, Databricks platform teams. Paired with a narrow machine-facing MCP server for programmatic operations.

## Architecture

```
sap-bdc plugin
├── 7 human-facing skills              ← for people
│   ├── bdc-onboarding                 first-time tenant setup
│   ├── bdc-core-admin                 users, roles, IdP, capacity, monitoring
│   ├── bdc-governance-catalog         catalog, metadata, glossary, KPIs, lineage
│   ├── bdc-connect-sharing            BDC Connect / ORD / CSN / SDK / DPG
│   ├── bdc-intelligent-apps           intelligent apps, data packages, ingestion spaces
│   ├── sap-databricks                 front door for SAP Databricks
│   └── bdc-troubleshooter             symptom → SAP Note lookup (22 notes)
│
├── mcp-server (sap-bdc-mcp-server)    ← for machines
│   └── 14 MCP tools (stdio transport) Databricks / Snowflake / etc. call these
│
└── 3 slash commands
    ├── /bdc-status
    ├── /bdc-validate-share
    └── /bdc-diagnose
```

Clean split: **skills** answer human questions ("how do I…"); **MCP tools** do the plumbing ("create this share", "diagnose this error"). The `bdc-connect-sharing` skill and the MCP server overlap deliberately — the skill teaches, the MCP executes.

## MCP tools exposed

Core 7 (Delta Sharing / BDC Connect execution):
- `create_or_update_share`
- `create_or_update_share_csn`
- `publish_data_product`
- `delete_share`
- `generate_csn_template`
- `provision_share` (end-to-end orchestration)
- `validate_share_readiness`

Extended 7 (discovery & diagnostics):
- `list_shares`, `get_share_details`, `list_recipients`
- `validate_tenant_hostname` (SAP Notes 3652165, 3705747)
- `check_deletion_vectors` (SAP Note 3706399)
- `cleanup_orphaned_data_product` (SAP Note 3720724)
- `diagnose_share_error` (regex map to 10+ SAP Notes)

## Install

```
/plugin install sap-bdc
```

The MCP server auto-starts and expects these env vars:

- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `DATABRICKS_RECIPIENT_NAME`
- `DATABRICKS_WAREHOUSE_ID`

## SAP Notes indexed

22 unique Notes covering provisioning, Databricks login/identity, SCIM, Delta Sharing, CSN publish errors, Azure Storage firewall, BDC Connect, HANA Cloud, and support workflows. Full index inside the `bdc-troubleshooter` skill.

## Changelog

**0.4.0 (2026-04-15)**
- Split monolithic `bdc-troubleshooter` into 7 domain skills + narrow symptom-lookup skill
- Added 4 new SAP Notes (3600390, 3665741, 3718680, 3726123)
- Refreshed 3 notes with newer versions (3653192, 3678584, 3725086)
- Added Azure Storage firewall section to `bdc-connect-sharing`
- MCP server unchanged — keeps all 17 tools including diagnostics

**0.3.0 (2026-04-13)**
- Added 7 extended MCP tools (list_shares, diagnose_share_error, etc.)
- Bundled `bdc-troubleshooter` skill indexed against 18 SAP Notes
- Added slash commands

**0.2.0 (2026-01-10)**
- Initial PyPI release of `sap-bdc-mcp-server` (7 core tools)
