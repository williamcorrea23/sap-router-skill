# HCM On-Premises Operations

## Overview
Handles SAP HR (HCM) on-premises execution using standard RFCs and infotype operations.

## Actions Reference

### `HCM_READ_EMPLOYEE`
- **Purpose**: Retrieve employee metadata (PA0001, PA0002).
- **Backend BAPI**: `BAPI_EMPLOYEE_GETDATA`
- **Fields**:
  - `employee_number`: PERNR (Employee Number)

### `HCM_CREATE_INFOTYPE`
- **Purpose**: Create/Insert an Infotype record.
- **Backend FM**: `HR_INFOTYPE_OPERATION`
- **Fields**:
  - `employee_number`: PERNR
  - `infotype`: Infotype code (e.g. 0001)
  - `subtype`: Subtype code
  - `begin_date`: Start Date
  - `end_date`: End Date (default: 99991231)
  - `record`: JSON formatted data representing the infotype structure

### `HCM_CHANGE_INFOTYPE`
- **Purpose**: Modify an Infotype record.
- **Backend FM**: `HR_INFOTYPE_OPERATION`
- **Fields**: Same as create (operation set to 'MOD').

### `HCM_CHECK_CONFIG`
- **Purpose**: Verify HR configuration tables.
- **Tables checked**:
  - `T500P` (personnel areas)
  - `T001P` (personnel subareas)
  - `T503` (employee groups)
  - `T510` (pay scale tables)
