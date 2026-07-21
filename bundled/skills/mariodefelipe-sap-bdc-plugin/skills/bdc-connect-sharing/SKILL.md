---
name: bdc-connect-sharing
description: Use when the user is sharing data products into or out of SAP BDC via BDC Connect, working with the sap-bdc-connect-sdk Python library, using Delta Sharing to publish Databricks/Snowflake data into BDC, using the Data Product Generator to extract BW/BW4HANA InfoProviders as BDC data products, or dealing with ORD/CSN metadata. Trigger phrases include "BDC Connect", "BDC data product", "publish to BDC", "share into BDC", "Delta Sharing BDC", "ORD metadata", "CSN schema", "Data Product Generator", "DPG", "BW data product", "BDC Connect SDK", "zero-copy BDC".
---

# SAP BDC Connect & Data Product Sharing

## BDC Connect Overview

BDC Connect enables **zero-copy, bidirectional data product sharing** between SAP Business Data Cloud and external systems like Databricks and Snowflake. Instead of replicating data, BDC Connect uses **Delta Sharing** (an open protocol) to provide direct, secure access to a single source of truth.

**Key benefits:**
- Bidirectional: Share BDC catalog data OUT to Databricks/Snowflake, or publish external Databricks shares back INTO BDC
- Zero-copy: No data duplication; recipients access tables directly
- Rich metadata: ORD (Open Resource Discovery) and CSN (Core Schema Notation) describe what data means and how to work with it
- Full lifecycle control: Create, update, publish, unpublish data products

**Prerequisites:**
- SAP Business Data Cloud provisioned with Datasphere tenant
- For external partner shares: Databricks or Snowflake workspace configured
- BDC catalog asset access (requires `Catalog Asset –R––––––` and `Cloud Data Product -----S-` privileges)

---

## ORD Metadata Structure

**ORD (Open Resource Discovery)** provides human-discoverable metadata about a data product.

**Mandatory ORD fields** (required for all data products):
- `title`: Short, clear name (e.g., "Customer Order")
- `shortDescription`: One-sentence summary (e.g., "Offering access to all customer orders")
- `description`: Detailed explanation (must NOT contain shortDescription)

**Optional ORD fields** (include if you want them to appear):
- `labels`: Functional grouping (e.g., `["sales", "orders"]`)
- `tags`: Technical tags (e.g., `["storage", "high-availability"]`)
- `industry`: Applicable industries (e.g., `["Retail", "Public Sector"]`)
- `lineOfBusiness`: LOB scope (e.g., `["Sales"]`)
- `deprecationDate`: When data product will be retired (ISO 8601 timestamp)
- `sunsetDate`: Final removal date (ISO 8601 timestamp)
- `successors`: Array of replacement data product URIs
- `correlationIds`: Links to source systems (e.g., `["sap.s4:communicationScenario:SAP_COM_0008"]`)
- `dataProductLinks`: Relationships to other data products
- `links`: Documentation, support, terms URLs
- `documentationLabels`: Organized documentation links

**Always-overridable fields:**
- `visibility`: "public" (default), "interval", or "private"
- `releaseStatus`: "active" (default), "beta", or "deprecated"

ORD is provided as a JSON object with the `@openResourceDiscoveryV1` key when using the SDK.

---

## CSN Schema Definition

**CSN (Core Schema Notation)** defines the technical structure: tables, columns, data types, primary/foreign keys, and relationships.

CSN is the standardized format for specifying table schemas in Delta Sharing contexts. It includes:
- **Entity definitions**: Table names, column names, data types
- **Primary keys**: Unique row identifiers
- **Associations/References**: Foreign key relationships
- **Data type mappings**: SQL types mapped to compatible targets

The Python SDK provides `csn_generator.generate_csn_template()` to automatically generate CSN from a Databricks share, then you can manually edit it for accuracy.

CSN compliance is validated against the **CSN Interop Effective v1** specification. For full CSN examples, consult CSN Interop Effective v1 · Examples documentation.

---

## Python SDK: Installation & Usage

### Installation

```bash
pip install sap-bdc-connect-sdk
```

Requires Python ≥3.9. License: SAP Developer License Agreement.

> **By the way** — earlier versions of this skill pinned the SDK at `==1.1.13`. That hard pin is now **incorrect**. The SAP-published reference version (per *help.sap.com "Working with Data Products in SAP Databricks"*, May 2026) is **1.0.9**, and PyPI may publish higher 1.x versions. Use `>=1.0.9` as a floor, not a hard pin. The MCP server v0.5.0+ already does this.

### Serverless environment version

When running the SDK inside an SAP Databricks notebook, set the **Serverless environment version to 3** before installing the SDK:
1. Open the notebook
2. Sidebar → **Environment** button
3. **Environment version** dropdown → choose **3**
4. **Apply**

Source: *help.sap.com "Working with Data Products in SAP Databricks"*, May 2026, page 10.

### Creating a Client

```python
from bdc_connect_sdk.auth import BdcConnectClient, DatabricksClient

# Create Databricks client (requires Databricks notebook context)
databricks_client = DatabricksClient(dbutils, "<recipient-name>")

# Create BDC Connect client
bdc_connect_client = BdcConnectClient(databricks_client)
```

**Parameters:**
- `dbutils`: Databricks notebook utility object
- `<recipient-name>`: Name of the BDC recipient (usually the BDC tenant name or system identifier)


### Required Databricks privileges (NEW 2026-05-02)

To share data products to/from BDC, the executing principal must have these **6 metastore privileges**, granted via *Catalog → Manage → Metastore → Permissions → Grant*:

- `CREATE CATALOG`
- `CREATE SHARE`
- `SET SHARE PERMISSION`
- `USE PROVIDER`
- `USE RECIPIENT`
- `USE SHARE`

Use the MCP server's `validate_databricks_privileges` tool to pre-flight this check before any sharing operation.

### Reserved recipient name

When sharing Databricks Delta Shares **back** to BDC, the recipient name is fixed: `sap-business-data-cloud`. This recipient is auto-provisioned in the SAP Databricks tenant during the formation join. Do not create a different one.

### Unsupported asset types

**Materialized views are NOT supported** by SAP Databricks Delta Sharing. You can share schemas, tables, and regular views — but materialized views must be re-exposed as a regular view or persisted as a Delta table. Use the MCP server's `list_unsupported_share_assets` tool to scan a catalog/schema.

### Recommended properties for derived data products (Databricks → BDC)

When you create a Delta table in SAP Databricks that you intend to expose back to BDC as a derived data product, set both:

```python
df.write.format("delta") \
    .option("delta.enableChangeDataFeed", "true") \
    .option("delta.enableDeletionVectors", "true") \
    .saveAsTable("my_catalog.my_schema.my_derived_table")
```

```sql
CREATE TABLE my_catalog.my_schema.my_derived_table
  TBLPROPERTIES (
    delta.enableChangeDataFeed = true,
    delta.enableDeletionVectors = true
  )
  AS SELECT * FROM source.schema.table WHERE ...;
```

> **Deletion vectors clarification** — SAP Note 3706399 says deletion vectors break sharing. That note covers the **consume side** of an inbound share you don't own. The recommendation above covers the **produce side** of derived tables you create yourself. Both are correct in their own context.

Source: *help.sap.com "Working with Data Products in SAP Databricks"*, May 2026, pages 7–9.

### Create or Update Share

```python
from bdc_connect_sdk.auth import BdcConnectClient, DatabricksClient

bdc_connect_client = BdcConnectClient(DatabricksClient(dbutils, "<recipient-name>"))
share_name = "<share-name>"

open_resource_discovery_information = {
    "@openResourceDiscoveryV1": {
        "title": "<title>",
        "shortDescription": "<short-description>",
        "description": "<description>"
    }
}

response = bdc_connect_client.create_or_update_share(
    share_name,
    open_resource_discovery_information
)
print(f"Share created/updated: {response}")
```

**Key method:** `create_or_update_share(share_name, open_resource_discovery_information)`

---

### Create or Update Share CSN

```python
from bdc_connect_sdk.auth import BdcConnectClient, DatabricksClient
from bdc_connect_sdk.utils import csn_generator

bdc_connect_client = BdcConnectClient(DatabricksClient(dbutils, "<recipient-name>"))
share_name = "<share-name>"

# Auto-generate CSN from Databricks share
csn_schema = csn_generator.generate_csn_template(share_name)

# Update the share's CSN metadata
response = bdc_connect_client.create_or_update_share_csn(
    share_name,
    csn_schema
)
print(f"CSN updated: {response}")
```

**To edit CSN manually:**

```python
import json

csn_schema = csn_generator.generate_csn_template(share_name)
file_path = f"csn_{share_name}.json"

# Write to file for editing
with open(file_path, "w") as f:
    f.write(json.dumps(csn_schema, indent=2))

# Later, read edited CSN
with open(file_path, "r") as f:
    edited_csn = json.load(f)

response = bdc_connect_client.create_or_update_share_csn(share_name, edited_csn)
```

**Key methods:**
- `csn_generator.generate_csn_template(share_name)`: Auto-generates CSN from Databricks share tables
- `create_or_update_share_csn(share_name, csn_schema)`: Pushes CSN to BDC Connect

---

### Publish a Data Product

```python
from bdc_connect_sdk.auth import BdcConnectClient, DatabricksClient

bdc_connect_client = BdcConnectClient(DatabricksClient(dbutils, "<recipient-name>"))
share_name = "<share-name>"

response = bdc_connect_client.publish_data_product(share_name)
print(f"Data product published: {response}")
```

**What happens:**
- The share (with ORD + CSN metadata) becomes a discoverable data product in BDC Catalog
- Recipients can see title, description, and schema
- Zero-copy access is provisioned

**Key method:** `publish_data_product(share_name)`

---

### Unpublish a Data Product

```python
from bdc_connect_sdk.auth import BdcConnectClient, DatabricksClient

bdc_connect_client = BdcConnectClient(DatabricksClient(dbutils, "<recipient-name>"))
share_name = "<share-name>"

response = bdc_connect_client.delete_share(share_name)
print(f"Share deleted: {response}")
```

Unpublishing removes the data product from catalog and revokes access. Use when data is no longer needed or to enforce data governance.

**Key method:** `delete_share(share_name)`

---

## Data Product Generator: BW/BW4HANA Extraction

The **Data Product Generator (DPG)** automates extraction of BW/BW4HANA InfoProviders into BDC local tables, enabling legacy BW data to be published as modern data products.

### Prerequisites

- **Minimum versions:**
  - SAP BW 7.5 SP24 or higher
  - SAP BW/4HANA 2021 SP04 or higher
  - SAP BW/4HANA 2023 SP00 or higher
- BW system must be in **private cloud edition** (lifted into SAP BDC)
- SAP Datasphere tenant configured within BDC formation
- Object Store enabled in Datasphere: `Configuration > Tenant Configuration > Object Store` (set Storage in TB, Compute in block-hours, API Requests/month)
- Support case opened on component **BDC-BW** for authorization and initial configuration (SAP Note 3590400)

### Data Subscriptions Concept

A **data subscription** is a new BW object type (TLOGO **DSUB** or legacy **SUBS**) that defines:
- **Source**: Which InfoProvider to extract from (ODP-based)
- **Target**: Which Datasphere space/tenant to send data to
- **Scope**: Which fields and filters to apply
- **Mode**: Full (snapshot) or Delta (incremental) extraction

Data subscriptions are **NOT** the extracted data itself—they are metadata definitions of extraction operations.

**Data subscription types:**
- **DSUB**: Transportable type (can move between DEV/QA/PROD via transport requests)
- **SUBS**: Local type (legacy, non-transportable; can be migrated to DSUB)

All new subscriptions are created as **DSUB** by default.

### InfoProviders & Delta Extraction Support

**Delta extraction available on:**
- Standard DataStore objects (aDSO) — **Yes (both BW 7.5 & BW/4HANA)**
- Staging aDSO with Inbound Queue Only, Compress Data, or Reporting-Enabled — **Yes**
- InfoCubes — **Yes (both systems)**
- MultiProviders (MPRO) — **Only if containing InfoCubes only**
- CompositeProviders (HCPR) — **Only if containing InfoCubes/aDSOs of same type (not mixed)**

**Full extraction only:**
- Classic DataStore objects (ODSO)
- DataStore objects (advanced) of type data mart
- Write-Optimized aDSO
- InfoObjects with Enhanced Master Data Update

**Archived data:** DPG can extract from NLS (Near-Line Storage) but NOT from ADK-based Data Archiving Process (DAP).

### Configuration Workflow

1. **Open support case** on BDC-BW to authorize DPG usage and register BW system
2. **Enable Object Store** in Datasphere tenant configuration
3. **Follow SAP Note 3590400** configuration guide (manual setup required)
4. **Create targets** in RSDPS transaction (or Data Subscriptions app in BW/4HANA Cockpit):
   - Target Type: **HDLFS** (SAP HANA Cloud, data lake Files)
   - Set Target Name, description, connection details to Datasphere
   - Mark as "Preferred System" if desired
   - Test connectivity via "Check Connectivity" button

### Target Management (RSDPS Transaction)

In RSDPS transaction, navigate to **Goto > Maintain Target System**:

| Action | Steps |
|--------|-------|
| View target details | Select target name; properties populate |
| Check connectivity | Click `[Check Connectivity]` icon |
| Edit target | Click `[Display ↔ Change]` then modify; click `[Save]` |
| Delete target | Click `[Display ↔ Change]` then `[Delete Target System]`; confirm |
| Create new target | Click `[Display ↔ Change]` then `[Create Target System]`; enter Target Name, set type to HDLFS |

**Important:** Target Type **MUST** be **HDLFS** (only supported type).

### Data Subscription Properties

When you create or maintain a data subscription, these properties are managed:

| Property | Description | Editable After First Run? |
|----------|-------------|--------------------------|
| Technical Name | Auto-generated | No |
| Description | Manual entry | Yes |
| Source Name | InfoProvider selected | No |
| Source Type | Always ODP (Operational Data Provisioning) | No |
| Target Name | Datasphere space/tenant | **No** (fixed at creation) |
| Target Type | Always HDLFS | No |
| Subscription Type | DSUB or SUBS | No |
| Status | Active/Inactive | Yes |
| Extraction Mode | Full or Delta | **No** (locked after first run) |
| Scheduling | None, Direct Execution, or Process Chain | Yes |
| Last Run | Success/failure status | Auto-generated |
| Created At / By | Timestamp + user | Auto-generated |
| Last Changed At / By | Timestamp + user | Auto-generated |

### Creating Data Subscriptions

**In Data Subscriptions App (BW/4HANA Cockpit):**
1. Navigate to **Data Product Generator for SAP Business Data Cloud** tab
2. Click **Create**
3. Enter Description
4. Select Source Name (InfoProvider) — text/dropdown search
5. Toggle Target Name arrow; select from available targets
6. Switch to **Settings** tab
7. Select **Extraction Mode**: Full or Delta (if supported)
8. Save

**In RSDPS Transaction (SAP GUI):**
1. Execute RSDPS
2. Enter Description
3. Enter Source Name (InfoProvider)
4. Click file icon next to Target Name; select target
5. Set **Extraction Mode**: Full or Delta
6. Configure field selection, filters, projection as needed
7. Save

**Target selection (CRITICAL):**
- If user-preferred target exists, it pre-fills; otherwise system-preferred fills in
- Target **CANNOT be changed after creation**
- Invalid or missing target prevents save

### Data Subscription Execution

After creating a subscription, **run it manually or schedule it**:
- **Manual run**: Execute immediately from app/transaction
- **Scheduled run**: Configure in **Scheduling** field (None, Direct Execution, or Process Chain)

**Execution flow:**
1. Data flows to **inbound buffer** in Datasphere object store
2. **Merge task** must be manually scheduled or run via task chain to merge snapshot/delta into local table
3. Local table becomes read-only; data can be previewed, exported, deleted
4. **Share to other spaces** for consumption in views and analytic models

### Creating Data Products from Local Tables

Once extracted, local tables can be published as data products via **Data Sharing Cockpit** in Datasphere:
1. Locate local table in BW file space
2. Create data product with ORD metadata (title, shortDescription, description)
3. Optionally publish to Databricks via Delta Share (if SAP Databricks capability enabled)

### Integration with BW Modeling Tools (BWMT)

Available in BWMT 1.27+:

**BW Data Product Generator Perspective:**
- Dedicated view with Scenario Generator and Data Subscriptions tabs
- Welcome screen with DPG overview
- Quick access to both capabilities

**Scenario Generator:**
- Mass-create data subscriptions from BW model dependencies
- Pre-define target and extraction mode at scenario level
- Prevents duplicate subscription creation
- Individual data subscriptions editable before generation
- Target check available before scenario execution
- Multi-replace function for bulk subscription updates

**Use case:** Map entire BW analytical model into BDC with one scenario, respecting dependencies.

### Transport of Data Subscriptions

DSUB data subscriptions are transportable objects (TLOGO type **DSUB**):
- Can be moved between DEV, QA, PROD systems via standard transport requests
- Activate in RSDPS/Data Subscriptions app before transport
- Configure transport request and package during activation
- Legacy SUBS objects can be migrated to DSUB via dedicated ABAP report

**Process Chain Integration:**
- New process type added to include Datasphere task chains in BW process chains
- Enables end-to-end scheduling (e.g., extract via subscription, then run transformation flow)

### BW Metadata Extraction & Catalog Integration

**Available on BW/4HANA 2023 SP04+:**
- Implement SAP Note 3601550 to enable metadata extraction
- Data subscriptions appear in Datasphere Catalog alongside tables, views, analytic models
- Visible to modelers (Datasphere) and administrators (BDC Cockpit)
- Search and discover data subscriptions across all catalog entry points

---

## BDC Connect Workflow: Sharing Data From Databricks to BDC

**Step-by-step with Python SDK:**

1. **Create Delta Share in Databricks** (native; consult Databricks docs for AWS/GCP/Azure)
   - Example: `CREATE SHARE my_sales_data;` in Databricks SQL

2. **Add tables to share** (Databricks side)
   - Grant SELECT access on tables to the share

3. **Create share metadata in BDC Connect** (Python SDK)
   ```python
   open_resource_discovery = {
       "@openResourceDiscoveryV1": {
           "title": "Sales Analytics Data",
           "shortDescription": "Shared sales transactions and metrics",
           "description": "Real-time sales data for analytics and ML workflows..."
       }
   }
   response = bdc_client.create_or_update_share("my_sales_data", open_resource_discovery)
   ```

4. **Generate & update CSN schema** (Python SDK)
   ```python
   csn = csn_generator.generate_csn_template("my_sales_data")
   # Optionally edit CSN for accuracy (data types, keys, references)
   response = bdc_client.create_or_update_share_csn("my_sales_data", csn)
   ```

5. **Publish as data product** (Python SDK)
   ```python
   response = bdc_client.publish_data_product("my_sales_data")
   ```

6. **Discover in BDC Catalog** (BDC Cockpit)
   - Navigate to Catalog & Marketplace > Search
   - Filter by Data Products collection
   - Find "Sales Analytics Data" with full metadata

7. **Consume in Datasphere or downstream** (recipient side)
   - Zero-copy access; no data duplication
   - Create views, analytic models, or ML pipelines on top

---

## BDC Connect Workflow: Sharing BDC Data to Databricks

1. **In BDC Catalog**: Catalog & Marketplace > Search
2. **Find & open data product** to be shared
3. **Select Share button** (Overview Details tab)
4. **Add target**: Select Databricks workspace
5. **Confirm share**
   - Notification confirms share process start/end
   - Databricks now has access to data product
6. **In Databricks**: Use shared data for analytics, enrichment, or ML

---

## Metering & Capacity Planning

BDC Connect metering measures cloud subscription usage. Reference **SAP Cloud Subscription Usage** page or **SAP Business Data Cloud Capacity Unit Estimator**:
- Look for **Capacity Units – SAP Business Data Cloud Connect (CY555)**
- Available in cloud services documents under **ATTACHMENT A**, **Table 5: SAP Business Data Cloud Connect Capacity Services**

---

## Troubleshooting & Support

**Common issues:**
- **Target connectivity fails**: Verify Datasphere connection details in RSDPS; use "Check Connectivity" button
- **CSN generation errors**: Ensure share exists in Databricks and has tables; inspect `generate_csn_template()` output
- **Data product not published**: Check ORD mandatory fields (title, shortDescription, description); confirm SDK response for errors
- **Extraction stalls**: Verify InfoProvider is ODP-compatible and not archived via ADK-DAP; check target space quotas in Datasphere

**Getting help:**
- Check **SAP Trust Center** for service/region availability
- Review **SAP Notes & KBAs** via SAP Support Portal
- Open **SAP for Me** case on **BDC-BW** for DPG issues; other component-specific cases as needed
- See **SAP Note 3568017** for BDC support case prerequisites

---

## References

- **bdcConnect.pdf** — BDC Connect overview, Delta Sharing fundamentals, ORD/CSN metadata specification
- **sap-bdc-connect-sdk-pypi.pdf** — Python SDK API reference (BdcConnectClient/DatabricksClient classes, method signatures). *By the way*: the v1.1.13 version cited in the previous version of this skill is no longer the canonical reference — SAP help.sap.com (May 2026) cites **1.0.9** and PyPI may have higher 1.x versions.
- **dataproductgenerator.pdf** — Data Product Generator configuration, data subscriptions, RSDPS/Cockpit UI, BWMT integration, BW extraction workflows
- **workingwithdataproductsindatabricks.pdf** *(NEW 2026-05-02)* — End-to-end BDC↔Databricks data product procedure: privileges, ingress (BDC → Databricks via *Catalog Explorer → Manage → Delta Sharing → Shared with me → Create catalog*), egress (Databricks → BDC via sap-bdc-connect-sdk), derived data product table properties, ORD field reference

---

## Azure Storage firewall — common 403 gotcha

When sharing data from Enterprise Databricks on Azure into BDC, if the underlying Azure Storage account has its firewall enabled (default posture for production), the consumer side hits `AuthorizationFailure` 403 on the parquet reads behind the share.

**Fix (from SAP Notes 3718680 + 3726123):**

1. Identify the SAP Datasphere HANA Database VNet subnet or public IP for your region. The authoritative region-specific subnet table lives in SAP Note 3726123 (refresh periodically — subnets get added).
2. In the Azure portal → Storage account → Networking → Firewalls and virtual networks → allowlist that subnet ID (or the public IP range).
3. Re-run the share. The 403s stop immediately.

Notes:
- 3718680 is the consumer-side diagnostic; 3726123 is the authoritative subnet table. Reference both.
- Applies to any Azure Storage account backing a Databricks Unity Catalog external location that a BDC-Connect share targets.
- Not relevant on AWS/GCP.

For the raw error-code → note mapping, delegate to the `bdc-troubleshooter` skill.

## Paired MCP Tools

The `sap-bdc-mcp-server` MCP (v0.5.0) provides programmatic execution of BDC Connect operations.

**SDK wrappers (core):**
- `create_or_update_share` — wraps SDK; in v0.5.0+, automatically pre-validates ORD JSON via `validate_ord_metadata` (bypass with `skip_validation=true`)
- `create_or_update_share_csn` — wraps SDK
- `publish_data_product` — wraps SDK
- `delete_share` — wraps SDK
- `provision_share` — sets up recipient access end-to-end
- `generate_csn_template` — wraps csn_generator utility
- `validate_share_readiness` — pre-flight before BDC registration

**Discovery & diagnostics (v0.3.0):**
- `list_shares`, `get_share_details`, `list_recipients`
- `validate_tenant_hostname` (SAP Notes 3652165 / 3705747)
- `check_deletion_vectors` (SAP Note 3706399)
- `cleanup_orphaned_data_product` (SAP Note 3720724)
- `diagnose_share_error` — regex-based mapping to indexed SAP Notes

**New in v0.5.0** (driven by SAP help.sap.com 2026-05-02 batch):
- `validate_databricks_privileges` — confirm CREATE CATALOG / CREATE SHARE / SET SHARE PERMISSION / USE PROVIDER / USE RECIPIENT / USE SHARE on the metastore
- `validate_ord_metadata` — local ORD JSON validation (required fields, description ≠ shortDescription, visibility/releaseStatus enums, ISO 8601 dates)
- `list_unsupported_share_assets` — flag materialized views and other unsupported types in a catalog/schema

This skill covers the **concepts and manual workflows**; the MCP handles **automated/scripted execution** in Databricks notebooks or orchestration tools.
