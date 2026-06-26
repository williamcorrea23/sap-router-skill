# Materials Management (MM) Operations

## Overview
Covers Material Master creation/modification, Purchase Order processes, Goods Movements, configuration checks, and active enhancements scan.

## Actions Reference

### `MM_CREATE_MATERIAL`
- **Purpose**: Create a new Material Master.
- **Backend BAPI**: `BAPI_MATERIAL_SAVEDATA`
- **Fields**:
  - `material`: Material Number (external)
  - `material_type`: Material Type (T134)
  - `industry`: Industry Sector (T137)
  - `description`: Text
  - `base_uom`: Base UoM
  - `plant`: Plant
  - `stor_loc`: Storage Location

### `MM_CHANGE_MATERIAL`
- **Purpose**: Modify an existing Material Master.
- **Backend BAPI**: `BAPI_MATERIAL_SAVEDATA`
- **Fields**: Same as create (delta fields).

### `MM_CREATE_PO`
- **Purpose**: Create a Purchase Order.
- **Backend BAPI**: `BAPI_PO_CREATE1`
- **Fields**:
  - `doc_type`: PO type (T161)
  - `purch_org`: Purchasing Org
  - `pur_group`: Purchasing Group
  - `vendor`: Vendor code
  - `material`: Material number
  - `plant`: Plant
  - `quantity`: Quantity
  - `price`: Price

### `MM_CHECK_CONFIG`
- **Purpose**: Verify MM configuration tables.
- **Tables checked**:
  - `T161` (document types)
  - `T024` (purchasing groups)
  - `T001W` (plants)
  - `T156` (movement types)

### `MM_CHECK_ENHANCEMENTS`
- **Purpose**: Scan for active BAdIs and User Exits in MM.
- **T-Codes mapped**: `ME21N`, `MIGO`, `MM01`
- **Tables**: `MODACT`, `SXS_ATTR`
