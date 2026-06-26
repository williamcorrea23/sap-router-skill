# Warehouse Management (WM) Operations

## Overview
Covers inventory movements, Transfer Orders (TO) creation, storage bins status, and warehouse configurations.

## Actions Reference

### `WM_GOODS_MOVEMENT`
- **Purpose**: Post a goods movement at MIGO level affecting warehouse storage.
- **Backend BAPI**: `BAPI_GOODSMVT_CREATE`

### `WM_CREATE_TO`
- **Purpose**: Create a Transfer Order.
- **Backend FM**: `L_TO_CREATE_MOVE_SU` (or standard L_TO_CREATE_SINGLE)
- **Fields**:
  - `lgnum`: Warehouse number (T300)
  - `tanum`: Transfer order number
  - `su_id`: Storage unit ID

### `WM_CHECK_CONFIG`
- **Purpose**: Verify WM configuration tables.
- **Tables checked**:
  - `T300` (warehouse numbers)
  - `T311` (WM movement types)
  - `T301` (storage types definitions)
