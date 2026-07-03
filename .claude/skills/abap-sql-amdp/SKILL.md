---
name: abap-sql-amdp
description: ABAP SQL and AMDP patterns — CDS table functions, AMDP class structure with IF_AMDP_MARKER_HDB, Open SQL vs Native SQL, HANA SQLScript procedures, parameter mapping, performance analysis, SQL Monitor (SQLM). Use when writing AMDP classes, implementing CDS table functions, optimizing ABAP SQL queries, or working with HANA SQLScript from ABAP.
trigger:
  keywords: [amdp, sql, cds-table-functions, hana, sqlscript, open-sql, native-sql, if-amdp-marker-hdb, sql-monitor, performance]
  intent: >-
    Write AMDP classes, CDS table functions, and optimize ABAP SQL queries for SAP HANA.
---

# ABAP SQL and AMDP

AMDP (ABAP Managed Database Procedures) and SQL patterns for SAP HANA.

## AMDP Class Structure

```abap
CLASS zcl_material_amdp DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.
    TYPES: BEGIN OF ty_material,
             matnr TYPE matnr,
             maktx TYPE maktx,
           END OF ty_material,
           ty_materials TYPE STANDARD TABLE OF ty_material WITH EMPTY KEY.
    CLASS-METHODS get_active_materials
      EXPORTING VALUE(et_materials) TYPE ty_materials.
ENDCLASS.

CLASS zcl_material_amdp IMPLEMENTATION.
  METHOD get_active_materials
    BY DATABASE PROCEDURE FOR HDB LANGUAGE SQLSCRIPT
    OPTIONS READ-ONLY
    USING mara makt.
    et_materials = SELECT
      mara.matnr,
      makt.maktx
    FROM mara
    INNER JOIN makt
      ON mara.matnr = makt.matnr
    WHERE mara.lvorm = ''
      AND makt.spras = 'E';
  ENDMETHOD.
ENDCLASS.
```

## CDS Table Function (uses AMDP behind the scenes)

```cds
@ClientDependent: true
define table function Z_TF_MATERIAL
  with parameters @Environment.systemField: #CLIENT
                  p_language : spras
  returns {
    mandt : mandt;
    matnr : matnr;
    maktx : maktx;
  }
implemented by method zcl_tf_material=>get_data;


" ABAP implementation class
CLASS zcl_tf_material DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.
    CLASS-METHODS get_data FOR TABLE FUNCTION z_tf_material.
ENDCLASS.

CLASS zcl_tf_material IMPLEMENTATION.
  METHOD get_data BY DATABASE FUNCTION
    FOR HDB LANGUAGE SQLSCRIPT OPTIONS READ-ONLY
    USING mara makt.
    RETURN SELECT
      mara.mandt,
      mara.matnr,
      makt.maktx
    FROM mara
    INNER JOIN makt
      ON mara.matnr = makt.matnr
      AND makt.spras = :p_language
    WHERE mara.lvorm = '';
  ENDMETHOD.
ENDCLASS.
```

## Open SQL vs Native SQL (HANA)

```abap
" Open SQL — portable across DBs
SELECT matnr, maktx FROM mara INTO TABLE @DATA(lt_mara).

" Native SQL — HANA-specific, via ADBC
DATA(lo_sql) = NEW cl_sql_statement( ).
DATA(lt_result) = lo_sql->execute_query(
  'SELECT "MATNR", "MAKTX" FROM "MARA" WHERE "LVORM" = '''' '
).
lo_sql->set_param( lo_sql->dba_stmt->get_db_connection( 'DEFAULT' ) ).
```

## SQLScript in HANA

```sql
-- HANA SQLScript stored procedure
PROCEDURE ZSP_MATERIAL_STOCK (
  IN iv_plant NVARCHAR(4),
  OUT et_result ZT_MATERIAL_STOCK
)
LANGUAGE SQLSCRIPT
SQL SECURITY INVOKER
AS
BEGIN
  et_result = SELECT
    m.mandt,
    m.matnr,
    m.maktx,
    COALESCE(s.labst, 0) AS labst
  FROM mara AS m
  LEFT JOIN mard AS s
    ON m.matnr = s.matnr
    AND s.werks = :iv_plant
  WHERE m.lvorm = '';
END;
```

## Performance Analysis

### SQL Monitor (SQLM) — ST05 replacement
```abap
" Start trace
CALL FUNCTION 'SQLM_START_TRACE'.

" Run code to analyze
PERFORM heavy_query.

" Stop and analyze
CALL FUNCTION 'SQLM_STOP_TRACE'.
" View results in SQLM transaction /SQLMD
```

### Explain Plan
```abap
SELECT matnr, maktx FROM mara INTO TABLE @DATA(lt_result)
  WHERE matnr IN @lt_materials
  %_HINTS ORACLE 'INDEX(MARA M~0)'.
```

## Gotchas

- **AMDP must implement IF_AMDP_MARKER_HDB** — compiler requirement
- **BY DATABASE PROCEDURE** keyword required for AMDP methods
- **OPTIONS READ-ONLY** prevents accidental writes
- **CDS table functions are read-only** — no DML allowed
- **SQLScript is case-sensitive** — table/column names must be UPPER with quotes
