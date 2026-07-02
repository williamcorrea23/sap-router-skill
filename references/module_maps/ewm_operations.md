# EWM — Extended Warehouse Management Operations Map

## Overview
Covers Extended Warehouse Management operations: Warehouse Tasks/Orders, Wave management, Packing, RF Framework, and Physical Inventory.

## Actions Reference

### `EWM_PICKING`
- **Purpose**: Execute picking wave processing.
- **Backend BAPI**: /SCWM/MON (Monitor) / /SCWM/WAVE wave release.
- **Fields**:
  - `warehouse_no`: Warehouse Number
  - `wave_no`: Wave number

### `EWM_PUTAWAY`
- **Purpose**: Create putaway warehouse task.
- **Backend BAPI**: /SCWM/TO_CREATE (Task creation)
- **Fields**:
  - `warehouse_no`: Warehouse Number
  - `item_no`: Item number

### `EWM_PHYS_INV`
- **Purpose**: Create Physical Inventory document.
- **Backend BAPI**: /SCWM/PI_CREATE
- **Fields**:
  - `warehouse_no`: Warehouse Number
  - `bin`: Storage bin

## T-codes
/SCWM/MON, /SCWM/WAVE, /SCWM/PACK, /SCWM/RFUI, /SCWM/PI, LT01, LB01

## Tables
/SCWM/TOHR, /SCWM/TOIT, /SCWM/WAVEHDR, /SCWM/LAGP
