# TM — Transportation Management Operations Map

## Overview
Covers TM operations including Freight Orders, vehicle planning, carrier tendering, and charges calculation.

## Actions Reference

### `TM_FREIGHT_PLAN`
- **Purpose**: Interactive planning for transportation.
- **Backend BAPI**: /SCMTMS/PLN planning
- **Fields**:
  - `planning_profile`: TM Planning profile
  - `freight_unit`: Freight Unit ID

### `TM_CARRIER_SELECT`
- **Purpose**: Carrier selection and tendering.
- **Backend BAPI**: /SCMTMS/TSPStend
- **Fields**:
  - `freight_order`: Freight Order ID

## T-codes
/SCMTMS/PLN, /SCMTMS/TOR, /SCMTMS/TEN

## Tables
/SCMTMS/D_TORROT, /SCMTMS/D_TORITE, /SCMTMS/D_TCLROT
