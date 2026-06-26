---
name: sap-hana-cloud-data-intelligence
description: SAP HANA Cloud Data Intelligence — data integration pipelines, data quality rules, metadata catalog, data lineage, SAP Data Intelligence Cloud, data governance, ETL orchestration, connection management. Use when building data pipelines with SAP DI Cloud, implementing data quality checks, managing metadata catalogs, or integrating S/4HANA data with HANA Cloud analytics.
---

# SAP HANA Cloud Data Intelligence

Data integration, quality, and catalog on SAP BTP — formerly SAP Data Intelligence Cloud.

## Core Capabilities

| Capability | Description | S/4HANA Relevance |
|---|---|---|
| Data Integration | ETL/ELT pipelines, 200+ connectors | Extract S/4HANA data for analytics |
| Data Quality | Rules-based validation, cleansing, dedup | Clean master data before migration |
| Metadata Catalog | Searchable catalog of all data assets | Discover S/4HANA CDS views, tables |
| Data Lineage | Track data from source to consumption | Impact analysis for S/4HANA changes |
| Connection Management | SAP + non-SAP source connectivity | ABAP, HANA, ODP, SLT connections |

## Data Pipeline

```
Source (S/4HANA CDS View) → Read → Transform → Quality Check → Write → Target (HANA Cloud)
```

## Pipeline Operators

| Operator | Function | Example |
|---|---|---|
| CDS Reader | Read SAP CDS views | Extract I_Product view |
| ODP Extractor | ODP framework extraction | Extract from S/4HANA extractors |
| SLT Connector | Real-time replication | Replicate MARA table changes |
| SQL Transform | SQL-based transformation | Join, filter, aggregate |
| Python Operator | Custom Python logic | ML preprocessing |
| Data Quality | Validate and cleanse | Check mandatory fields |
| HANA Client | Write to HANA Cloud | Load into HDI container |

## Connection Types

```json
// ABAP connection to S/4HANA
{
  "type": "ABAP",
  "host": "s4hana.internal.corp",
  "client": "100",
  "authentication": "BASIC",
  "protocol": "RFC"
}

// HANA connection
{
  "type": "HANA_DB",
  "host": "hana-cloud.cfapps.us10.hana.ondemand.com",
  "port": 443,
  "authentication": "DB_USER",
  "encrypt": true
}
```

## Data Quality Rules

```sql
-- Mandatory field check
SELECT COUNT(*) FROM input_data WHERE material IS NULL;

-- Duplicate detection
SELECT material, COUNT(*) FROM input_data GROUP BY material HAVING COUNT(*) > 1;

-- Value range validation
SELECT * FROM input_data WHERE quantity < 0 OR quantity > 1000000;
```

## Data Lineage

Lineage tracks how data flows through pipelines:
```
S/4HANA table MARA
  → CDS View Z_I_PRODUCT
    → DI Pipeline "Product Enrichment"
      → HANA Cloud table Z_PRODUCT_ENRICHED
        → SAC Story "Product Dashboard"
```

Impact: changing MARA field length → alerts Z_I_PRODUCT consumers.

## S/4HANA CDS Integration

```
S/4HANA CDS View → ODP Extraction → DI Pipeline → HANA Cloud
  (I_Product)     (delta-enabled)   (transform)    (analytical dataset)
```

## ABAP Trigger

```abap
" Trigger DI pipeline from ABAP Cloud
DATA(lo_http) = cl_web_http_client_manager=>create_by_http_destination(
  i_destination = cl_http_destination_provider=>create_by_cloud_destination(
    i_name = 'DI_CLOUD' ) ).
lo_http->get_http_request( )->set_text( '{ "pipeline": "Product_Load" }' ).
DATA(lo_response) = lo_http->execute( i_method = 'POST' ).
```

## Gotchas

- DI Cloud is a separate BTP service subscription (not bundled with HANA Cloud)
- ODP extraction requires S/4HANA ODP framework active (transaction ODQMON)
- Data lineage tracked at column level in S/4HANA CDS views
- Metadata catalog auto-discovers HANA Cloud assets; non-HANA sources need manual registration
- Pipeline scheduling via Job Scheduling service or REST API trigger
