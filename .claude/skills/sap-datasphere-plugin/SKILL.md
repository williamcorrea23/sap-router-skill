---
name: sap-datasphere-plugin
description: >
  SAP Datasphere plugin for Claude Co-Work (MarioDeFelipe/sap-datasphere-plugin-for-claude-cowork).
  Reference for Datasphere spaces, views, and data federation — the MCP/plugin usage layer:
  connecting via datasphere-mcp, @sap/datasphere-cli operations, consuming views via
  OData/Open SQL, and monitoring task chains.
trigger:
  keywords: [datasphere plugin, datasphere mcp, datasphere cli, dsphere, spaces list, dbusers, view consumption, odata consumption, task chain, hana cloud federation]
  intent: Operating SAP Datasphere from Claude via the datasphere-mcp server or @sap/datasphere-cli — listing spaces, querying exposed views, managing database users, and running/monitoring task chains
prerequisites:
  - SAP Datasphere tenant URL (e.g. https://<tenant>.us10.hcs.cloud.sap)
  - OAuth client created in Datasphere → System → App Integration (Purpose "Interactive Usage")
  - DSPHERE_HOST / DSPHERE_USER / DSPHERE_PASSWORD set in .env (consumed by datasphere-mcp)
  - Technical user assigned as member of each target space (DW Integrator/Viewer role)
  - Node.js 18+ for @sap/datasphere-cli and the MCP server
---

# SAP Datasphere Plugin (MCP + CLI Usage Layer)

Operational layer for driving SAP Datasphere from Claude: the `datasphere-mcp` server
(MarioDeFelipe/sap-datasphere-mcp) plus `@sap/datasphere-cli`. For data-modeling concepts
(Data Builder, analytical models, replication flows) use the sibling `sap-datasphere` skill.

## 1. Plugin / MCP setup

The repo ships a `datasphere-mcp` entry in `.mcp.json` (stdio, `node dist/index.js`) reading:

```bash
# .env — required by datasphere-mcp
DSPHERE_HOST=https://<tenant>.us10.hcs.cloud.sap
DSPHERE_USER=<technical-user-or-oauth-client-id>
DSPHERE_PASSWORD=<password-or-oauth-client-secret>

# Verify the MCP is reachable (probes all 53 MCPs incl. datasphere-mcp)
npm run hc
```

OAuth prerequisite (one-time, in the Datasphere tenant):

1. System → Administration → App Integration → **Add a New OAuth Client**
2. Purpose: **Interactive Usage** (CLI login) — Authorization Grant: Authorization Code
3. Note the Client ID, Client Secret, Authorization URL, Token URL

## 2. CLI login and space discovery

```bash
# Install CLI
npm install -g @sap/datasphere-cli

# Point CLI at the tenant, then login via OAuth client (opens browser consent)
datasphere config host set "https://<tenant>.us10.hcs.cloud.sap"
datasphere login --client-id "<CLIENT_ID>" --client-secret "<CLIENT_SECRET>"

# List all spaces visible to the user
datasphere spaces list

# Read one space definition (members, objects) to a file
datasphere spaces read --space SALES --output sales_space.json

# List database users (Open SQL schema users) of a space
datasphere dbusers list --space SALES
```

## 3. Consume a view — OData

The view must have **Expose for Consumption = ON** in Data Builder (see Pitfall 4).

```bash
# Relational consumption endpoint (entity data as OData v4)
curl -H "Authorization: Bearer $TOKEN" \
  "https://<tenant>.us10.hcs.cloud.sap/api/v1/dwc/consumption/relational/SALES/V_SALES_KPI/V_SALES_KPI?\$top=10"

# Analytical consumption (aggregated, for analytical models)
curl -H "Authorization: Bearer $TOKEN" \
  "https://<tenant>.us10.hcs.cloud.sap/api/v1/dwc/consumption/analytical/SALES/AM_SALES/AM_SALES?\$select=Revenue"
```

## 4. Consume a view — SQL (Open SQL schema)

Database users unlock direct SQL access on HANA Cloud port 443.

```bash
# Create/list the space's database user first (schema name = SPACE#USER)
datasphere dbusers list --space SALES

# Connect with hdbsql (HANA client) and query the exposed view
hdbsql -n "<tenant-hana-host>:443" -e -u "SALES#TECH_USER" -p "<password>" \
  'SELECT TOP 10 * FROM "SALES"."V_SALES_KPI";'
```

## 5. Data federation basics

Federation = remote tables over a **connection** (S/4HANA via ODP/CDS, HANA Cloud via
SDA, Azure SQL, BW/4HANA). Queries execute at the source — no copy, always fresh.

```text
Connection (S4HANA_PRD) → Remote Table (federated, default) → View → Expose → OData/SQL
                                    └─ optional: switch to Replicated (snapshot/real-time)
```

- Check state: Data Integration Monitor → Remote Tables → Federation vs Replicated
- Heavy analytical reads on S/4? Switch the remote table to replicated (see Pitfall 3)
- Model federation details (virtual tables, VDM layers) live in the `sap-datasphere` skill

## 6. Task chains — run and monitor

```bash
# List task chains / tasks of a space
datasphere tasks list --space SALES

# Run a task chain and watch its status
datasphere tasks chains run --space SALES --object TC_DAILY_LOAD
datasphere tasks list --space SALES --status RUNNING

# UI equivalent: Data Integration Monitor → Task Chains → last run = COMPLETED
```

## Pitfalls

- **CLI login fails with invalid_client** → Cause: OAuth client created without Purpose "Interactive Usage" (e.g. API Access only). Solution: recreate the OAuth client in App Integration with Purpose = Interactive Usage, Authorization Grant = Authorization Code.
- **`spaces list` returns empty / 403 on space objects** → Cause: technical user authenticated but not a member of the space. Solution: Space Management → SPACE_ID → Members → add user with DW Viewer (read) or DW Integrator (run tasks).
- **"Fresh" data is stale or source is overloaded** → Cause: remote table replication vs federation confusion — replicated tables serve snapshots; federated tables push every query to the source. Solution: check Data Integration Monitor → Remote Tables; use federation for freshness, replication to offload heavy reads from S/4HANA.
- **View returns 404 on the consumption API** → Cause: view not exposed — "Expose for Consumption" toggle is OFF. Solution: Data Builder → open view → toggle Expose for Consumption ON → deploy, then retry the OData/SQL query.
- **hdbsql connection refused** → Cause: client IP not in the Datasphere IP allowlist. Solution: System → Configuration → IP Allowlist → add the client's public IP.

## Verification

```bash
# 1. MCP healthy + env vars present
npm run hc                          # datasphere-mcp must report OK; no missing DSPHERE_* vars

# 2. CLI authenticated and space visible
datasphere spaces list              # target space appears

# 3. View consumable end-to-end
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<tenant>.us10.hcs.cloud.sap/api/v1/dwc/consumption/relational/SALES/V_SALES_KPI/V_SALES_KPI?\$top=1"
# → returns one row of JSON, not 404/403

# 4. Task chain green
datasphere tasks list --space SALES   # last run status = COMPLETED
```

## Related

- **sap-datasphere** skill — modeling layer: spaces, Data Builder, analytical models, replication flows, VDM
- **datasphere-mcp** in `.mcp.json` — MarioDeFelipe/sap-datasphere-mcp (DSPHERE_HOST/USER/PASSWORD)
- **sap-hana-cli** skill — hdbsql and HANA Cloud client tooling for Open SQL schema access
- **sap-sac-*** skills — SAC consumes exposed Datasphere analytical models
