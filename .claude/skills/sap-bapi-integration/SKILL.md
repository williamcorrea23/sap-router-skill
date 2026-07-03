---
name: sap-bapi-integration
description: SAP BAPI/RFC integration — BAPI discovery, transaction handling, BAPIRET2 patterns, 29 BAPI mappings across 9 modules (MM/SD/FI/QM/PP/WM/CO/HCM/BASIS). Use for BAPI calls, CSV→BAPI conversion, ZROUTER handler creation, or BAPI debugging.
trigger: bapi, BAPI, rfc, RFC, transaction commit, BAPIRET2, BAPI_TRANSACTION, goods movement, sales order bapi, material bapi, purchase order bapi, criar material, criar pedido, posting document, ZROUTER handler
---

# SAP BAPI Integration — 9 Modules, 29 BAPIs

> **Prerequisites:** SAP RFC connection, ZROUTER_DISPATCH_FM (or direct BAPI), Python 3.8+.
> Full BAPI tables: [reference.md](reference.md)

## When to use

- Create/modify materials, orders, FI docs via BAPI
- Map CSV/XLS fields to BAPI parameters
- Debug BAPIRET2 -- the real error message is never in sy-subrc
- Create ZROUTER handler for a new functional module
- Replace batch input/BDC with BAPI (ex: MB01 → BAPI_GOODSMVT_CREATE)

## Golden Rule

```
1. BAPI_<OBJECT>_<ACTION> → call with parameters by VALUE
2. Check BAPIRET2-TYPE       → NEVER trust sy-subrc
3. E or A in TYPE?           → BAPI_TRANSACTION_ROLLBACK
4. Otherwise                 → BAPI_TRANSACTION_COMMIT EXPORTING wait = 'X'
```

## Step by step

### 1. Discover BAPI

```bash
python scripts/sap_router.py route --action CREATE_MATERIAL --module MM
# → "ZROUTER RFC"

# List BAPIs of a module
grep -A1 "CREATE_MATERIAL\|CREATE_PO\|CREATE_ORDER\|POST_DOCUMENT" scripts/xls_to_bapi.py
```

### 2. Convert CSV → BAPI payload

```bash
# Generate template
python scripts/xls_to_bapi.py template --output tmpl.csv --module MM --action CREATE_MATERIAL

# Convert data
python scripts/xls_to_bapi.py convert --input data.csv --module MM --action CREATE_MATERIAL
# Expected: JSON with BAPI_MATERIAL_SAVEDATA payload
```

### 3. Call BAPI (ABAP)

```abap
DATA: ls_header TYPE bapimathead, ls_ret TYPE bapiret2, lv_matnr TYPE matnr,
      lt_desc TYPE TABLE OF bapi_makt.

ls_header-material      = 'M-001'.
ls_header-matl_type     = 'FERT'.
ls_header-indust_sector = 'M'.

CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
  EXPORTING headdata = ls_header
  IMPORTING return   = ls_ret
            material = lv_matnr
  TABLES    materialdescription = lt_desc.

" Check TYPE, NOT sy-subrc
IF ls_ret-type CA 'EA'.
  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
ELSE.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
ENDIF.
```

### 4. Verify

```bash
python scripts/sap_router.py log-action \
  --action CREATE_MATERIAL --module MM --status OK --details "MATNR: 000000000000001234"
python scripts/memory_manager.py verify --input MEMORY.md
```

## BAPIRET2 — The Debug Key

| Campo | Meaning | Example |
|---|---|---|
| TYPE | S=OK, W=Warning, **E=Error, A=Abort**, I=Info | `E` |
| ID | Message class | `M3` |
| NUMBER | Message number | `001` |
| MESSAGE | Translated text | "Material M-001 created" |
| MESSAGE_V1..V4 | Message variables | M-001, FERT, ... |
| PARAMETER | Field that caused the error | `HEADDATA-MATERIAL` |
| ROW | Table row (if applicable) | `3` |

See [reference.md](reference.md) for production-grade BAPIRET2 loop code.

## 9 Modules — BAPI Quick Index

### MM — Materials Management
`BAPI_MATERIAL_SAVEDATA` (create/change material), `BAPI_MATERIAL_GETALL` (list), `BAPI_PO_CREATE1` (create PO), `BAPI_PO_CHANGE` (change PO), `BAPI_GOODSMVT_CREATE` (goods movement). Template: `xls_to_bapi.py template --module MM --action CREATE_PO`

### SD — Sales & Distribution
`BAPI_SALESORDER_CREATEFROMDAT2` (create order), `BAPI_SALESORDER_CHANGE` (change), `BAPI_BILLINGDOC_CREATEMULTIPLE` (VF01 billing), `BAPI_OUTB_DELIVERY_CREATE_SLS` (VL01N delivery). Flow: TA (VA01) → LF (VL01N) → F2 (VF01).

### FI — Financial Accounting
`BAPI_ACC_DOCUMENT_POST` (post document), `BAPI_ACC_DOCUMENT_REV_POST` (reverse), `BAPI_GL_GETACCOUNTSALDO` (account balance).

### QM — Quality Management
`CO_QM_INSPECTION_LOT_CREATE` (inspection lot), `BAPI_INSPOPER_RECORDRESULTS` (record results).

### PP — Production Planning
`BAPI_PRODORD_CREATE` (production order), `BAPI_PRODORDCONF_CREATE_TT` (confirm), `CS_BOM_EXPL_MAT_V2` (explode BOM), `BAPI_ROUTING_GETDETAIL` (routing details).

### WM — Warehouse Management
`BAPI_GOODSMVT_CREATE` (goods movement), `L_TO_CREATE_SINGLE` (transfer order).

### CO — Controlling
`BAPI_INTERNALORDER_CREATE` (internal order), `BAPI_CO_ALLOCACTUALS` (allocate costs).

### HCM — Human Capital Management
`BAPI_EMPLOYEE_GETDATA` (employee data), `PA_INFOTYPE_INSERT` (create infotype -- requires ENQUEUE).

### BASIS — System Administration
`TR_INSERT_REQUEST_WITH_TASKS` (create transport), `TR_RELEASE_REQUEST` (release), `TRINT_INSPECT_OBJECTS` (analyze objects).

## Pitfalls

- **sy-subrc != BAPIRET2-TYPE**: BAPI always returns 0, the error is in BAPIRET2. **NEVER** `IF sy-subrc <> 0` to validate BAPI.
  - Cause: BAPIs wrap all errors in BAPIRET2-TYPE. Solution: always check `ls_ret-type CA 'EA'`.
- **COMMIT vs COMMIT WORK**: Always use `BAPI_TRANSACTION_COMMIT`, never `COMMIT WORK` directly. BAPI commit ensures synchronous update.
  - Cause: `COMMIT WORK` skips update task processing. Solution: `BAPI_TRANSACTION_COMMIT EXPORTING wait = 'X'`.
- **Parameters by value**: BAPIs do not support pass-by-reference. All parameters must be passed by value.
  - Cause: RFC marshalling limitation. Solution: check FM signature in SE37 -- import=by value, changing=by ref (avoid).
- **Lock before update**: For HCM/PA_INFOTYPE_INSERT always ENQUEUE first. MM uses BAPI_MATERIAL_SAVEDATA which auto-locks.
  - Cause: Infotype requires PA lock. Solution: `CALL FUNCTION 'ENQUEUE_EPA'` before insert.
- **QM uses prefix CO_**: QM BAPIs use `CO_QM_*`, not `BAPI_QM_*`.
  - Cause: Historical naming from CO module. Solution: search `CO_QM_*` for quality BAPIs.
- **L_TO_CREATE_SINGLE is RFC not BAPI**: No BAPIRET2, check specific return structure.
  - Cause: WM transfer order predates BAPI standard. Solution: check `LTAP-VSOLA` and `LTAP-NLPLA` fields.
- **Implicit commits**: Dialog step, RFC calls, CALL TRANSACTION, SUBMIT, WAIT -- all trigger implicit commit. Careful with long SAP LUWs.
  - Cause: SAP kernel auto-commits at dialog boundaries. Solution: batch all BAPIs within one LUW before final commit.
- **Implicit rollback**: Runtime error (dump), message type A or X, PBO with error -- resets everything.
  - Cause: SAP transaction integrity. Solution: handle exceptions, check message types before calling BAPI.

## Verification

```bash
# Validate via sap_router
python scripts/sap_router.py log-action --action CREATE_MATERIAL --module MM --status OK

# Check memory
python scripts/memory_manager.py verify --input MEMORY.md

# ABAP: check BAPIRET2 after call
" LOOP AT lt_bapiret INTO ls_ret WHERE type CA 'EA'. → error found
" SE37 → BAPI_MATERIAL_SAVEDATA → Test → execute with test data
```

## Related

- ZROUTER handler: `python scripts/template_repo.py resolve --template MM_CREATE_MATERIAL ...`
- Field mapping: `python scripts/xls_to_bapi.py template --module <MOD> --action <ACT>`
- Full BAPI tables and production code: [reference.md](reference.md)
