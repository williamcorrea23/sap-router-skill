# PM — Plant Maintenance Operations Map

## Overview
Covers Work Order creation/modification, Maintenance Notifications, Equipment Master records, and preventive maintenance scheduling.

## Actions Reference

### `PM_CREATE_ORDER`
- **Purpose**: Create a new Plant Maintenance Work Order.
- **Backend BAPI**: `BAPI_ALM_ORDER_MAINTAIN`
- **Fields**:
  - `order_type`: Maintenance Order type (AUART)
  - `equipment`: Equipment Number (EQUNR)
  - `description`: Short description
  - `plant`: Maintenance Plant (WERKS)

### `PM_CREATE_NOTIFICATION`
- **Purpose**: Create a Plant Maintenance Notification.
- **Backend BAPI**: `BAPI_ALM_NOTIF_CREATE`
- **Fields**:
  - `notif_type`: Notification type (QMART)
  - `equipment`: Equipment Number
  - `description`: Short description

### `PM_CREATE_EQUIPMENT`
- **Purpose**: Create a new Equipment Master record.
- **Backend BAPI**: `BAPI_EQUI_CREATE`
- **Fields**:
  - `description`: Equipment name/desc
  - `category`: Equipment category (EQTYP)
  - `plant`: Plant

### `PM_CHECK_CONFIG`
- **Purpose**: Verify PM configuration tables.
- **Tables checked**: AUFK, AFIH, QMEL, EQUI, IFLOT

## T-codes
IW31, IW32, IW33, IW21, IW22, IW23, IP41, IP42, IP10, IP30, IE01, IE02, IE03, IL01, IL02, IL03

## Tables
AUFK, AFIH, QMEL, EQUI, IFLOT, MPLA, MPOS
