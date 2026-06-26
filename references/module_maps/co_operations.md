# Controlling (CO) Operations

## Overview
Covers Internal Orders creation, cost allocation, profit center structures check, and CO configurations.

## Actions Reference

### `CO_CREATE_ORDER`
- **Purpose**: Create a Controlling Internal Order.
- **Backend BAPI**: `BAPI_INTERNALORDER_CREATE`
- **Fields**:
  - `order_name`: Name/description of internal order
  - `order_type`: Internal order type (COAS)
  - `controlling_area`: Controlling Area (TKA01)

### `CO_ACTIVITY_ALLOC`
- **Purpose**: Post direct activity allocation.
- **Backend BAPI**: `BAPI_ACC_ACTIVITY_ALLOC_POST`

### `CO_CHECK_CONFIG`
- **Purpose**: Verify CO configuration tables.
- **Tables checked**:
  - `TKA01` (controlling areas)
  - `CSKS` (cost centers list)
  - `CSKA` (cost elements catalog)
  - `TKA02` (CO assignment company code mappings)
