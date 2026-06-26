# Quality Management (QM) Operations

## Overview
Covers Inspection Lot generation, quality results recording, PDF inspections certificates generation, and QM configs.

## Actions Reference

### `QM_CREATE_INSPECTION`
- **Purpose**: Create an Inspection Lot.
- **Backend BAPI**: `BAPI_INSPLOT_CREATE`
- **Fields**:
  - `material`: Material number
  - `plant`: Plant
  - `insp_type`: Inspection type (TQ01)
  - `quantity`: Quantity

### `QM_RECORD_RESULTS`
- **Purpose**: Record characteristics inspection results.
- **Backend BAPI**: `BAPI_INSRES_RECORD`

### `QM_GENERATE_PDF`
- **Purpose**: Call RFC to generate inspection PDF certificate.
- **Backend FM**: `ZFM_QM_GENERATE_INSPECTION_PDF`
- **Fields**:
  - `insp_lot`: Inspection Lot Number

### `QM_CHECK_CONFIG`
- **Purpose**: Verify QM configuration tables.
- **Tables checked**:
  - `TQ01` (inspection types)
  - `TQ02` (inspection origins)
  - `T156Q` (QM material movement assignments)
