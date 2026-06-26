# Sales & Distribution (SD) Operations

## Overview
Covers Sales Order management, Delivery notes creation, Billing documents, and functional configurations checks.

## Actions Reference

### `SD_CREATE_ORDER`
- **Purpose**: Create a Sales Order.
- **Backend BAPI**: `BAPI_SALESORDER_CREATEFROMDAT2`
- **Fields**:
  - `doc_type`: Sales doc type (TVAK)
  - `sales_org`: Sales Org
  - `distr_chan`: Distribution Channel
  - `division`: Division
  - `sold_to`: Sold-to Party
  - `ship_to`: Ship-to Party
  - `material`: Material number
  - `quantity`: Order quantity

### `SD_CHANGE_ORDER`
- **Purpose**: Modify an existing Sales Order.
- **Backend BAPI**: `BAPI_SALESORDER_CHANGE`

### `SD_CREATE_DELIVERY`
- **Purpose**: Create Outbound Delivery from Sales Order.
- **Backend BAPI**: `BAPI_OUTB_DELIVERY_CREATE_SLS`

### `SD_CREATE_INVOICE`
- **Purpose**: Post Billing Document (Invoice).
- **Backend BAPI**: `BAPI_BILLINGDOC_CREATEMULTIPLE`

### `SD_CHECK_CONFIG`
- **Purpose**: Verify SD configuration tables.
- **Tables checked**:
  - `TVAK` (sales document types)
  - `TVKO` (sales organizations)
  - `TVSB` (shipping conditions)
  - `TVFK` (billing types)
  - `KNVV` (customer sales data status)
