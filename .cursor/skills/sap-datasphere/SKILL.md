---
name: sap-datasphere
description: SAP Datasphere — data modeling, data federation, analytical models, spaces, views, remote tables, data flows, replication flows, catalog, role-based access, SAC integration. Use when building Datasphere data models, federating SAP and non-SAP data, or creating analytical datasets for SAP Analytics Cloud.
---

# SAP Datasphere

Cloud data warehouse on SAP BTP — semantic data modeling, federation, and catalog.

## Architecture

```
Sources                          Datasphere                 Consumers
────────                          ──────────                 ─────────
SAP S/4HANA (CDS views)  ──┐
SAP SuccessFactors ────────┤      Data    ──→  Analytical  ──→ SAC
Non-SAP (SQL Server, etc.)─┤     Models        Datasets
CSV/Parquet files ─────────┘                       └──→ Data Lake
```

## Spaces

```
Space: Finance (content isolation)
├── Connections (S4HANA source, Azure SQL, etc.)
├── Tables (remote tables, local tables)
├── Views (SQL views, graphical views)
├── Data Flows (ETL transformations)
└── Analytical Models (star schema)
```

## Remote Tables (Federation)

```sql
-- Federated query — no data copy, live access to S/4HANA
CREATE REMOTE TABLE ZRT_MATERIALS
ON ZS4_CONNECTION
AS SELECT * FROM Z_I_PRODUCT;

-- Federated query joining Datasphere + S/4HANA
SELECT ds.sales_amount, s4.product_desc
FROM ZDS_SALES AS ds
JOIN ZRT_PRODUCTS AS s4 ON ds.material = s4.material;
```

## Data Flows

```
Source Table → Join → Filter → Aggregation → Target Table
  MARA (remote) → + MAKT → active only → count by type → Z_MATERIAL_STATS
```

## Replication Flows

```
S/4HANA CDS View → Real-time Replication (CDC) → Datasphere Remote Table
                                                 → Local Table (snapshot)
```

## Analytical Model

```
Fact: SalesFacts
├── Dimension: ProductDim (ProductID, Material, Description)
├── Dimension: TimeDim (Date, Month, Quarter, Year)
├── Dimension: CustomerDim (CustomerID, Name, Region)
└── Measures: Revenue, Quantity, Margin
```

## ACLs and Data Access Controls

```
Space: Finance
├── Role: Finance_Analyst → Read access to all Finance views
└── Role: Finance_Restricted → Read access with row-level filter (region = 'EU')
```

## Gotchas
- Remote table queries execute on source system — performance depends on source
- Replication flow latency: near-real-time (CDC) or scheduled (batch)
- Data flow transformation steps limited to 30 per flow
- Federated queries bypass Datasphere cache — may be slower but always fresh
