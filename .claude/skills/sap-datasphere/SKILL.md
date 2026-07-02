---
name: sap-datasphere
description: >
  SAP Datasphere — cloud data warehouse on BTP for semantic data modeling, federation,
  analytical models, spaces, remote/local tables, data flows, replication flows, catalog,
  role-based access, SAC integration. Use when building Datasphere data models, federating
  SAP and non-SAP data, creating analytical datasets for SAP Analytics Cloud, or managing
  Open SQL schemas and Data Builder artifacts.
trigger:
  keywords:
    - datasphere
    - data builder
    - analytical model
    - remote table
    - data flow
    - replication flow
    - open sql schema
    - federation
    - semantic layer
    - SAC integration
  file_patterns:
    - "*.hdbsynonym"
    - "*.hdbview"
    - "datasphere/**"
---

# SAP Datasphere

Cloud data warehouse on SAP BTP — semantic data modeling, federation, and catalog.
Built on SAP HANA Cloud; consumes CDS views from S/4HANA and external sources alike.

## Pré-requisitos

- SAP BTP global account with Datasphere entitlement (Cloud Foundry)
- Space assignment (e.g. `Finance`, `Sales`) — content isolation boundary
- Source connection configured: S/4HANA (CDS views via ODP), Azure SQL, CSV, etc.
- Database user with Open SQL schema if pushing data from external systems
- IP allowlist updated for any external source system
- SAP Analytics Cloud (SAC) instance for consumption (optional but typical)

## Architecture

```
Sources                          Datasphere                       Consumers
────────                          ──────────                       ─────────
SAP S/4HANA (CDS/ODP) ──┐
SAP SuccessFactors ────────┤     Spaces
Non-SAP (SQL Server) ──────┤     ├── Connections
CSV / Parquet files ───────┘     ├── Remote Tables (federation)
                                 ├── Local Tables (replicated/Open SQL)
                                 ├── Views (SQL / graphical)
                                 ├── Data Flows (ETL)
                                 ├── Replication Flows (CDC / batch)
                                 └── Analytical Models (star schema)
                                          ↓
                                   SAC / Data Lake / API
```

## Spaces

```
Space: Finance (content isolation)
├── Connections   — S4HANA_PRD, AZURE_SQL, CONCUR_API
├── Tables        — remote (federated) + local (replicated/pushed)
├── Views         — SQL views, graphical views
├── Data Flows    — ETL transformations (max 30 steps)
└── Analytical Models — star schema with measures + dimensions
```

## Remote Tables (Federation)

Federated queries execute on the source — no data copy, always fresh.

```sql
-- Create remote table from S/4HANA CDS view
CREATE REMOTE TABLE ZRT_MATERIALS
ON ZS4_CONNECTION
AS SELECT * FROM Z_I_PRODUCT;

-- Federated join: Datasphere local + S/4HANA remote
SELECT ds.sales_amount, s4.product_desc
FROM ZDS_SALES      AS ds
JOIN ZRT_PRODUCTS   AS s4 ON ds.material = s4.material;

-- Federation on federation (HANA Cloud → Data Lake via virtual table)
CREATE VIRTUAL TABLE VT_DL_SALES
  AT "REMOTE_SOURCE_DL"."<NULL>"."DL_SCHEMA"."SALES_FACT";
```

## Open SQL Schema (External Push)

External systems push data directly into Datasphere via database users.

```sql
-- Admin creates Open SQL schema + database user
-- External system writes via standard SQL INSERT/UPSERT
-- Then import in Data Builder → deployed as local table
```

## Data Flows

```
Source Table → Join → Filter → Aggregation → Target Table
  MARA (remote) → +MAKT → active only → count by type → Z_MATERIAL_STATS
```

- Max 30 transformation steps per flow
- Schedule: manual, timer, or event-based

## Replication Flows

```
S/4HANA CDS View → CDC (near-real-time) → Datasphere Remote Table
                  → Batch (scheduled)   → Local Table (snapshot)
```

## Analytical Model (Star Schema)

```
Fact: SalesFacts
├── Dimension: ProductDim  (ProductID, Material, Description)
├── Dimension: TimeDim     (Date, Month, Quarter, Year)
├── Dimension: CustomerDim (CustomerID, Name, Region)
└── Measures: Revenue, Quantity, Margin
```

Expose as OData service → consumed by SAC stories and dashboards.

## VDM Connection (CDS Views from S/4HANA)

SAP S/4HANA exposes a Virtual Data Model (VDM) via CDS views with layers:

```
Basic (F)  → Composite (I)  → Consumption (C)  → Query
  raw data    reused joins    ready-to-consume   analytics
```

- Datasphere imports `I_*` or `C_*` views via ODP (Operational Data Provisioning)
- Associations in CDS become navigation paths in Datasphere views
- Annotations (e.g. `@AnalyticsDetails`) carry through to SAC

## ACLs and Data Access Controls

```
Space: Finance
├── Role: Finance_Analyst    → Read access to all Finance views
└── Role: Finance_Restricted → Read access with row-level filter (region = 'EU')
```

## Pitfalls

1. **Remote table performance** — queries execute on source system; large scans can overload S/4HANA. Use replication for heavy reads.
2. **Federation on federation** — virtual table over virtual table adds latency; validate before production.
3. **Data flow step limit** — 30 steps max per flow. Split complex pipelines into chained flows.
4. **Federated queries bypass cache** — always fresh but potentially slower than replicated local tables.
5. **Open SQL schema isolation** — pushed data is local to the schema; must be imported in Data Builder to appear in views.
6. **CDC replication lag** — near-real-time ≠ real-time; verify SLA requirements for dashboards.
7. **IP allowlist** — external push systems must be registered in Datasphere IP allowlist before connection works.
8. **Space deletion cascades** — deleting a space removes all contained objects. Export content first.
9. **VDM layer selection** — consuming `F_*` (basic) views is discouraged; prefer `I_*` or `C_*` for stability.

## Verificação

```bash
# 1. Check space connectivity (Datasphere CLI or web UI)
#    Space → Connections → verify green status on each connection

# 2. Validate remote table freshness
SELECT COUNT(*), MAX(last_loaded_at) FROM ZRT_MATERIALS;

# 3. Test analytical model exposure
#    Open model in Data Builder → Preview → verify rows return

# 4. Verify SAC connection
#    SAC → Connection → Datasphere → Test → green

# 5. Check replication flow status
#    Data Integration Monitor → flow name → Last Run = Success

# 6. Confirm ACL enforcement
#    Log in as restricted user → verify row-level filter applied
```
