---
name: sap-hana-cloud-data-intelligence
description: SAP HANA Cloud Data Intelligence — data integration pipelines, data quality rules, metadata catalog, data lineage, SAP Data Intelligence Cloud integration. Use when building data pipelines with SAP DI Cloud, implementing data quality checks, or managing metadata catalogs.
---

# SAP HANA Cloud Data Intelligence

Data integration, quality, and catalog on SAP BTP.

## Core Capabilities

| Capability | Description |
|---|---|
| Data Integration | ETL/ELT pipelines, connectivity to SAP + non-SAP sources |
| Data Quality | Rules-based data validation, cleansing, deduplication |
| Metadata Catalog | Searchable catalog of all data assets |
| Data Lineage | Track data from source to consumption (impact analysis) |

## Data Pipeline

```
Source (S/4HANA table) → Read → Transform → Quality Check → Write → Target (HANA Cloud)
```

## Integration with ZROUTER

ZROUTER BASIS handler ST22_SCAN action queries SNAP table for dump analysis — relevant for pipeline monitoring. CODE_SEARCH action finds data objects across the system.

## Gotchas
- DI Cloud is a separate BTP service subscription (not bundled with HANA Cloud)
- Data lineage tracked at column level in S/4HANA CDS views
- Metadata catalog auto-discovers HANA Cloud assets; non-HANA sources need manual registration
