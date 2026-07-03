---
name: sap-hana-sqlscript
description: >
  SAP HANA SQLScript — stored procedures, table functions, AMDP, calculation views,
  declarative vs imperative logic, CE functions, performance profiling, HDI containers.
  Use when writing HANA SQLScript, creating AMDP classes, or optimizing database logic.
trigger:
  keywords:
    - SQLScript
    - AMDP
    - hdbprocedure
    - hdbtablefunction
    - calculation view
    - HANA stored procedure
    - HANA table function
    - CE function
    - plan visualizer
  intent: >-
    Write and optimize SAP HANA SQLScript procedures, table functions, AMDP classes, and calculation views.
  file_patterns:
    - "*.hdbprocedure"
    - "*.hdbtablefunction"
    - "*.hdbview"
    - "*amdp*"
---

# SAP HANA SQLScript

## Prerequisites

- SAP HANA 2.0 SPS05+ (or HANA Cloud) with SQLScript enabled
- HANA Database Explorer or HANA Studio for debugging/profiling
- HDI container access (for CAP/HDI deployments) or direct schema access
- ABAP 7.4 SP05+ on HANA for AMDP (requires `IF_AMDP_MARKER_HDB` interface)
- ADT (ABAP Development Tools) for AMDP class editing

## Stored Procedure

- Host variables use colon prefix (`:iv_matnr`) inside SQL statements
- `SELECT` assigns to variables via expression (`lv_count = SELECT COUNT(*)...`) — no `INTO` clause
- `SESSION_CONTEXT('CLIENT')` retrieves session variables

```sql
CREATE PROCEDURE ZSP_MATERIAL_STOCK (
  IN  iv_plant  NVARCHAR(4),
  OUT et_result TABLE(MATNR NVARCHAR(18), MAKTX NVARCHAR(40), LABST DECIMAL(13,3))
)
LANGUAGE SQLSCRIPT
SQL SECURITY INVOKER
AS
BEGIN
  et_result = SELECT
    m.MATNR, m.MAKTX, COALESCE(s.LABST, 0) AS LABST
  FROM "MARA" AS m
  LEFT JOIN "MARD" AS s ON m.MATNR = s.MATNR AND s.WERKS = :iv_plant
  WHERE m.LVORM = '';
END;
```

## Table Function

```sql
CREATE FUNCTION ZTF_PRODUCT_ACTIVE(p_plant NVARCHAR(4))
RETURNS TABLE(MATNR NVARCHAR(18), MAKTX NVARCHAR(40))
LANGUAGE SQLSCRIPT
SQL SECURITY INVOKER
AS
BEGIN
  RETURN SELECT m.MATNR, m.MAKTX
    FROM "MARA" AS m
    JOIN "MARD" AS s ON m.MATNR = s.MATNR
    WHERE s.WERKS = :p_plant AND m.LVORM = '';
END;
```

## Declarative vs Imperative

**Rule: prefer declarative.** The SQLScript optimizer rewrites declarative code at runtime for superior execution plans. Imperative logic (loops, cursors) bypasses the optimizer.

```sql
-- Declarative (preferred — optimizer can inline, push down, reorder)
CREATE PROCEDURE ZSP_DECLARATIVE(IN iv_year INT, OUT et_result TABLE(...))
AS BEGIN
  et_result = SELECT a.*, b.text
    FROM accounting AS a
    JOIN texts AS b ON a.id = b.id AND a.year = :iv_year;
END;

-- Imperative (only when logic truly requires row-by-row processing)
CREATE PROCEDURE ZSP_IMPERATIVE(IN iv_limit INT, OUT et_result TABLE(...))
AS BEGIN
  DECLARE CURSOR cur FOR SELECT * FROM mara LIMIT :iv_limit;
  FOR r AS cur DO
    IF r.LVORM = '' THEN
      -- row-level processing
    END IF;
  END FOR;
END;
```

## AMDP (ABAP-Managed Database Procedures)

AMDP wraps SQLScript inside ABAP class methods — lifecycle managed via transport, debuggable from ADT, extensible via SAP Notes.

```abap
CLASS zcl_amdp_material DEFINITION PUBLIC FINAL.
  PUBLIC SECTION.
    INTERFACES if_amdp_marker_hdb.
    METHODS get_stock
      IMPORTING VALUE(iv_plant) TYPE werks_d
      EXPORTING VALUE(et_result) TYPE ANY TABLE.
ENDCLASS.

CLASS zcl_amdp_material IMPLEMENTATION.
  METHOD get_stock
    BY DATABASE PROCEDURE FOR HDB LANGUAGE SQLSCRIPT
    OPTIONS READ-ONLY
    USING mara mard.

    et_result = SELECT m.matnr, COALESCE(s.labst, 0) AS labst
      FROM mara AS m
      LEFT JOIN mard AS s ON m.matnr = s.matnr
      WHERE s.werks = :iv_plant;
  ENDMETHOD.
ENDCLASS.
```

- `BY DATABASE PROCEDURE FOR HDB` — declares AMDP method
- `OPTIONS READ-ONLY` — marks method as read-only (recommended when no DML)
- `USING` — **mandatory** when referencing ABAP dictionary objects (tables, views, other AMDPs)

## CE Functions (Calculation Engine)

```sql
-- CE functions bypass SQL optimizer — use only for proven hot paths
SELECT ce_aggregation(:lt_data, [SUM("AMOUNT")], ["REGION"]) AS result
FROM dummy;
```

## Performance Analysis

### Plan Visualizer

```sql
EXPLAIN PLAN FOR SELECT matnr, maktx FROM mara WHERE matnr = 'MAT001';
-- HANA Database Explorer → Plan Visualizer tab
-- Look for: TABLE SCAN (missing index), high join cardinality, materialization
```

### AMDP Profiler

1. Window → Preferences → ABAP Development → Profiling → Enable AMDP trace
2. Execute AMDP method via ADT or ABAP program
3. Right-click result → Profile As → ABAP Profiling
4. Inspect per-statement execution time and row counts

**Profiler limitations:** does not track CE functions, loops, or ABAP CDS table functions called via ABAP SQL.

## HDI Container Deployment

```
db/src/
├── procedures/
│   └── get_material_stock.hdbprocedure
├── functions/
│   └── get_active_products.hdbtablefunction
└── .hdinamespace
```

Deploy via `cds deploy` (CAP) or `hdi-deploy` (standalone HDI).

## Pitfalls

- **Imperative loops kill performance** — the SQLScript optimizer cannot rewrite cursor-based logic. Always try declarative first.
- **Missing `USING` clause** in AMDP causes runtime dump `CX_AMDP_NO_ABAP_TABLE_IN_DBPROC` — list every referenced DDIC object.
- **Table variables consume default memory pool** — large intermediate results can exhaust `$TMPTABLES`. Filter early with WHERE before materializing.
- **`SELECT` without `LIMIT` in cursors** materializes the full result set into memory — add `LIMIT` or paginate.
- **CE functions are not optimizer-friendly** — they bypass the SQL plan. Benchmark against declarative SQL before adopting.
- **`SQL SECURITY DEFINER`** grants procedure the owner's privileges — prefer `INVOKER` for least-privilege unless explicitly required.
- **AMDP Profiler gaps** — no profiling data for CE functions, fine-grained SQLScript elements (loops, IF), or CDS table functions consumed via ABAP SQL.
- **Quoted identifiers** — use `"MARA"` (double quotes) for schema objects in native HANA; unquoted identifiers are uppercased implicitly.

## Verification

```bash
# Validate HDI artefact syntax (local, from skill root)
python scripts/hdi_lint.py --path db/src/procedures/get_material_stock.hdbprocedure
# or: npm run hana:hdi-lint -- db/src/procedures/

# Check AMDP activation in ABAP (requires ADT CLI)
python scripts/sap_router.py adt activate ZCL_AMDP_MATERIAL
```

```sql
-- Verify procedure/function exist and are valid
SELECT PROCEDURE_NAME, STATUS FROM SYS.PROCEDURES WHERE PROCEDURE_NAME = 'ZSP_MATERIAL_STOCK';
SELECT FUNCTION_NAME, STATUS FROM SYS.FUNCTIONS WHERE FUNCTION_NAME = 'ZTF_PRODUCT_ACTIVE';
```
