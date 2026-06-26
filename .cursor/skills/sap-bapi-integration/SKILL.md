---
name: sap-bapi-integration
description: >-
  SAP BAPI/RFC integration guide — BAPI discovery, BAPI_TRANSACTION_COMMIT
  patterns, BAPIRET2 error handling, RFC_READ_TABLE alternatives, xls_to_bapi
  field mapping, and BAPI parameter structures for MM/SD/FI/QM/PP/WM/CO/HCM/BASIS.
  Use when implementing BAPI calls, troubleshooting BAPI errors, mapping CSV
  fields to BAPI parameters, or creating new ZROUTER handler methods.
---

# SAP BAPI Integration

Integration patterns for SAP BAPI/RFC calls used in ZROUTER_DISPATCH
and the xls_to_bapi.py converter.

## BAPI Discovery

```bash
# Use Hermes MCP for BAPI documentation
# Or SE37 in SAP GUI → search BAPI_*

# Common BAPI naming conventions:
#   BAPI_<OBJECT>_GETDETAIL     — read single object
#   BAPI_<OBJECT>_GETLIST       — read multiple objects
#   BAPI_<OBJECT>_CREATE        — create object
#   BAPI_<OBJECT>_CHANGE        — modify object
#   BAPI_<OBJECT>_DELETE        — delete object
#   BAPI_<OBJECT>_<ACTION>      — specific action
#   BAPI_<OBJECT>_SAVEDATA      — create or change (upsert)
```

## Standard BAPI Pattern

```abap
" 1. Prepare input structures
DATA: ls_header  TYPE bapimathead,
      ls_ret     TYPE bapiret2,
      lt_ret     TYPE TABLE OF bapiret2,
      lv_matnr   TYPE matnr.

" 2. Call BAPI
CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
  EXPORTING
    headdata = ls_header
  IMPORTING
    return   = ls_ret
    material = lv_matnr
  TABLES
    materialdescription = lt_desc.

" 3. Check BAPIRET2, not sy-subrc
IF ls_ret-type = 'E' OR ls_ret-type = 'A'
   OR line_exists( lt_ret[ type = 'E' ] ).
  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
  " Error path
ELSE.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING wait = 'X'.
  " Success path
ENDIF.
```

## BAPIRET2 Structure

| Field | Meaning |
|---|---|
| TYPE | S=Success, W=Warning, E=Error, A=Abort, I=Info |
| ID | Message class (e.g. M3) |
| NUMBER | Message number |
| MESSAGE | Message text |
| MESSAGE_V1-V4 | Message variables |
| PARAMETER | Field name causing error |
| ROW | Table row causing error |

## Field Mapping: CSV → BAPI

Fields in `xls_to_bapi.py` ACTION_FIELDS map to BAPI parameters:

```
CSV column "material"      → BAPI_MATERIAL_SAVEDATA HEADDATA-MATERIAL
CSV column "material_type" → BAPI_MATERIAL_SAVEDATA HEADDATA-MATERIAL_TYPE
CSV column "description"   → BAPI_MATERIAL_SAVEDATA MAKT-MAKTX
```

## BAPI Transaction Safety

| DO | DON'T |
|---|---|
| `BAPI_TRANSACTION_COMMIT EXPORTING wait = 'X'` | `COMMIT WORK` |
| `BAPI_TRANSACTION_ROLLBACK` | `ROLLBACK WORK` |
| Check BAPIRET2-TYPE | Check only sy-subrc |
| Use LT_BAK for batch operations | Call BAPI in tight loops |
| Lock before BAPI (ENQUEUE) | BAPI without locking |

## 9 SAP Modules Supported

| Module | Key BAPIs | Notes |
|---|---|---|
| MM | BAPI_MATERIAL_SAVEDATA, BAPI_PO_CREATE1 | HEADDATA + CLIENTDATA for material |
| SD | BAPI_SALESORDER_CREATEFROMDAT2, BAPI_BILLINGDOC_CREATEMULTIPLE | ORDER_HEADER_IN + ITEMS_IN |
| FI | BAPI_ACC_DOCUMENT_POST, BAPI_ACC_DOCUMENT_REV_POST | ACCOUNTGL + ACCOUNTPAYABLE tables |
| QM | CO_QM_INSPECTION_LOT_CREATE, BAPI_INSPOPER_RECORDRESULTS | Uses CO_ not BAPI_ prefix |
| PP | BAPI_PRODORD_CREATE, BAPI_PRODORDCONF_CREATE_TT | TIMETICKETS for confirmations |
| WM | BAPI_GOODSMVT_CREATE, L_TO_CREATE_SINGLE | L_TO is RFC, not BAPI |
| CO | BAPI_INTERNALORDER_CREATE, BAPI_CO_ALLOCACTUALS | Controlling area required |
| HCM | BAPI_EMPLOYEE_GETDATA, PA_INFOTYPE_INSERT | Enqueue before infotype insert |
| BASIS | TR_INSERT_REQUEST_WITH_TASKS, TRINT_INSPECT_OBJECTS | Function modules, not BAPIs |

## BAPI Call via Python

```bash
# Convert CSV to BAPI payload
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL
python scripts/xls_to_bapi.py convert  --input data.csv  --module MM --action CREATE_MATERIAL

# Route to ZROUTER RFC
python scripts/sap_router.py route --action MM_CREATE_MATERIAL
# → "ZROUTER RFC"

# Use template_repo for ABAP code generation
python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL \
  --values '{"HEADER":"ls_header","DESCRIPTION":"ls_desc","RETURN_STRUCT":"ls_ret","MATERIAL_NUMBER":"lv_matnr","DESCRIPTION_TABLE":"lt_desc"}'
```
