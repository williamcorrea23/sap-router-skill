---
name: bdc-intelligent-apps
description: Use when the user is working with SAP BDC Intelligent Applications — installing, reviewing, extending, or partitioning them — or managing Data Packages, Data Products, or Ingestion Spaces within BDC. Trigger phrases include "intelligent application", "intelligent app", "BDC data package", "install data product", "ingestion space", "extending intelligent app", "partitioning local tables", "RLS intelligent app".
---

# SAP BDC Intelligent Applications

## Intelligent Applications Lifecycle

### Installing Intelligent Applications

An SAP BDC administrator installs intelligent applications into SAP Datasphere and SAP Analytics Cloud tenants. Installation automatically creates three SAP-managed spaces:

- **Ingestion space**: Contains data products as local tables and replication flows that load data from source systems.
- **Preparation space**: Contains views built on data products for consumption preparation.
- **App space**: Contains analytic models exposed to SAP Analytics Cloud (named after the intelligent application).

These spaces are **read-only and SAP-managed**—objects cannot be created, shared, or imported/exported manually. Data flows from source system → SAP Datasphere → combined/prepared for analytics → exposed in SAP Analytics Cloud as stories.

#### Multiple Installations & Shared Ingestion Spaces

Multiple instances of a single intelligent application can be installed for different source systems:
- Each instance gets its own set of three spaces, distinguished by a system alias assigned during installation.
- Multiple intelligent applications can be installed for the same source system, **reusing the shared ingestion space**.
- When uninstalling, only relevant spaces are removed; the shared ingestion space is retained until the final application is removed.

### Reviewing Installed Intelligent Applications

Users with appropriate space access can:
- View objects in standard editors (read-only).
- Monitor data flow from source to SAC stories.
- If task chains exist, DW Integrator-role users must run each chain at least once and create a schedule for regular runs.

## Row-Level Security for Intelligent Application Data

By default, **no user can view data** in delivered SAP Analytics Cloud stories. Row-level security uses data access controls:

1. **Identify** fact views and permissions table in the preparation space.
2. **Prepare** permissions records in operator/values format for row-level access:
   - Use `ALL` or `*` operator to show all records to selected user.
   - Avoid more than 5,000 permissions records per user for performance.
3. **Upload** permissions data as CSV file (see Load or Delete Local Table Data).
4. **Optionally review** accessible data using View as User dialog.
5. **Maintain** permissions table as necessary.

**Important**: Source system authorizations are not automatically imported; permissions must be manually configured in SAP Datasphere.

## Extending Intelligent Applications

Data products from SAP BDC do not include custom field extensions from source systems. To extend:

1. **Identify** all relevant spaces containing the data product.
2. **Request DW Administrator** to copy preparation and application spaces:
   - Copying removes objects from protective namespace.
   - Technical names transformed from `sap.s4.entity` → `sap_s4_entity`.
3. **Request DW Administrator** to add Modeler users to copied spaces and authorize for data product installation.
4. **DW Modeler** installs data products in copied preparation space, updating with custom fields.
5. **DW Modeler** adjusts view sources and analytic models in copied application space to use copied preparation space as source.
6. **Modify** objects in both spaces for extension fields.
7. **Verify** data access controls still protect data appropriately.
8. **Communicate** new models and fields to SAC business analysts.

**Note**: Always copy both preparation and application spaces; independent copied spaces are required. If SAP updates data products, updates are not auto-applied to copied spaces.

## Partitioning Local Tables for Intelligent Applications

Partition local tables installed via SAP BDC to break data into chunks and manage large-volume read-only tables:

1. In **Data Builder**, select the SAP-managed space.
2. **Open** the local table (marked with SAP Business Data Cloud label).
3. **Add partitions** (partitioning is the only permitted change to SAP-managed read-only tables).
4. **Reset** to default partitioning if needed via Reset button.

## Data Packages & Data Products

### Activating Data Packages and Installing Data Products

An SAP BDC administrator activates data packages in SAP BDC to make data products available for installation:

- DW Datasphere administrator chooses spaces where products can be installed and selects access method (remote tables or replication flows).
- DW Datasphere modelers install products to modeling spaces.
- SAP BDC Catalog administrators share products to SAP Databricks.

### Creating Data Products

Create data products from SAP BW, SAP IBP, or other connected sources:

1. **Prepare** source data (tables containing product data).
2. **Identify** a file space to stage data product tables (products can only contain data from file spaces).
3. **Navigate** to Data Sharing Cockpit and create data product.
4. **List** product becomes available in Catalog & Marketplace (SAP Datasphere and BDC Cockpit).
5. **Install** product in modeling spaces or share with other BDC formation consumers.

### Data Product Generator for SAP BW/4HANA

The Data Product Generator for SAP BDC works with SAP BW and SAP BW/4HANA systems:

- Generates data products from BW/4HANA objects and structures.
- Data products pass through a single "local" ingestion space derived from SAP Datasphere tenant URL.
- **Supported systems**: SAP BW 7.5 and SAP BW/4HANA.

### SAP Integrated Business Planning (IBP) Integration

SAP IBP data can be pushed to SAP Datasphere object store for further modeling:

- **Status**: Currently limited to early adopters; contact SAP with component **SCM-IBP-INT-BDC**.
- **Setup**: Connection established using communication scenarios **SAP_COM_1260** and **SAP_COM_1263**.
- **Scheduling**: Data push scheduled via application job templates (use templates starting with "Business Data Cloud").
- **Process**: Application job collects data → pushes through communication scenario → creates read-only local table (file).

#### Working with IBP-Generated Local Tables

- **Read-only** but support data management tasks (e.g., deletion).
- Can be **shared** to other spaces for views and analytic models.
- **No property changes** permitted; delta capture status is fixed.
- **Restoring** previous versions not supported; only display available.
- **Partitions** defined at creation are viewable but not modifiable.
- **Updates** pushed to inbound buffer; merge tasks must be manually scheduled or via task chains to update actual table.

## Special Ingestion Spaces & BDC Space Types

SAP BDC formations include special space types, automatically created and managed by the platform:

### Ingestion Spaces

- **Created** automatically when data product installed from connection; named after connection.
- **Each connection** with data products has its own ingestion space.
- **Data Product Generator**: Data products from SAP BW via Data Product Generator and other products pass through single "local" ingestion space (name derived from tenant URL).
- **Restrictions**: Administrators modify only space quota; assigned users can monitor tables.
- **Storage**: SAP HANA Database (Disk and In-Memory).

### SAP BW Spaces

- **Auto-created** and populated with data from Data Product Generator.
- **Restrictions**: Modify quota only; users can monitor tables and create task chains for merge tasks.
- **Storage**: SAP HANA Data Lake Files.
- **Related**: Data Product Generator for SAP BW/4HANA.

### SAP IBP Spaces

- **Auto-created** and populated with IBP-pushed data.
- **Restrictions**: Modify quota only; users can monitor tables and create task chains for merge tasks.
- **Storage**: SAP HANA Data Lake Files.
- **Related**: SAP Integrated Business Planning integration.

### SAP-Managed Prep/App Spaces

- **Auto-created** alongside intelligent application installation.
- **No users** granted by default; DW administrator can add users.
- **No object creation** permitted; content is SAP-managed and read-only.
- **Protected** by namespace; copy to modify (see Extending Intelligent Applications).

## References
- `references/chunk-02-intelligent-apps.md` — distilled chapter 2 reference
