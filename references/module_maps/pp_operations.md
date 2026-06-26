# Production Planning (PP) Operations

## Overview
Covers Production Order creation, order confirmations, BOM explosions, routing retrievals, and configuration checks.

## Actions Reference

### `PP_CREATE_ORDER`
- **Purpose**: Create a Production Order.
- **Backend BAPI**: `BAPI_PRODORD_CREATE`
- **Fields**:
  - `material`: Material number
  - `plant`: Production plant
  - `quantity`: Target quantity
  - `order_type`: Order type (T003O)
  - `start_date`: Scheduled start date

### `PP_CONFIRM_ORDER`
- **Purpose**: Confirm Production Order operations.
- **Backend BAPI**: `BAPI_PRODORDCONF_CREATE_HDR`

### `PP_READ_BOM`
- **Purpose**: Explode a Bill of Materials.
- **Backend BAPI/FM**: `CS_BOM_EXPL_MAT_V2`
- **Fields**:
  - `material`: Material
  - `plant`: Plant
  - `bom_usage`: BOM usage (T011)

### `PP_READ_ROUTING`
- **Purpose**: Read task list / routing for a material.
- **Backend BAPI**: `BAPI_ROUTING_GET`

### `PP_CHECK_CONFIG`
- **Purpose**: Verify PP configuration tables.
- **Tables checked**:
  - `T003O` (order types)
  - `T399D` (MRP plant parameters)
  - `T024F` (MRP controllers)
