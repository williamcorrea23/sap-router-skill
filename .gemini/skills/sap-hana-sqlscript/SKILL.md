---
name: sap-hana-sqlscript
description: SAP HANA SQLScript — stored procedures, table functions, declarative logic, imperative logic, CE functions, SQLScript debugger, performance analysis with plan visualizer, SQLScript in HDI containers, migration from ABAP AMDP to HANA procedures. Use when writing HANA SQLScript procedures, creating HANA table functions, or optimizing HANA database logic.
---

# SAP HANA SQLScript

HANA database programming language — SQL + procedural logic in the database layer.

## Stored Procedure

```sql
CREATE PROCEDURE ZSP_MATERIAL_STOCK (
  IN iv_plant NVARCHAR(4),
  OUT et_result TABLE(MATNR NVARCHAR(18), MAKTX NVARCHAR(40), LABST DECIMAL(13,3))
)
LANGUAGE SQLSCRIPT
SQL SECURITY INVOKER
AS
BEGIN
  et_result = SELECT
    m.MATNR, m.MAKTX, COALESCE(s.LABST, 0) AS LABST
  FROM MARA AS m
  LEFT JOIN MARD AS s ON m.MATNR = s.MATNR AND s.WERKS = :iv_plant
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
    FROM MARA AS m JOIN MARD AS s ON m.MATNR = s.MATNR
    WHERE s.WERKS = :p_plant AND m.LVORM = '';
END;
```

## Declarative vs Imperative

```sql
-- Declarative (preferred — optimizer-friendly)
CREATE PROCEDURE ZSP_DECLARATIVE(IN iv_year INT, OUT et_result TABLE(...))
AS BEGIN
  et_result = SELECT a.*, b.text
    FROM accounting AS a JOIN texts AS b
    ON a.id = b.id AND a.year = :iv_year;
END;

-- Imperative (when logic requires it)
CREATE PROCEDURE ZSP_IMPERATIVE(IN iv_limit INT, OUT et_result TABLE(...))
AS BEGIN
  DECLARE CURSOR cur FOR SELECT * FROM mara LIMIT :iv_limit;
  FOR r AS cur DO
    IF r.LVORM = '' THEN
      -- process row
    END IF;
  END FOR;
END;
```

## CE Functions (Calculation Engine)

```sql
-- CE functions for high-performance aggregation
SELECT
  ce_aggregation(:lt_data, [SUM("AMOUNT")], ["REGION"]) AS result
FROM dummy;
```

## SQLScript Debugger

1. HANA Database Explorer → SQL Console
2. Debug → Start Debugging
3. Set breakpoints in procedure body
4. Watch variables, step through code

## Plan Visualizer

```sql
EXPLAIN PLAN FOR SELECT * FROM mara WHERE MATNR = 'MAT001';
-- View in HANA Database Explorer → Plan Visualizer
-- Identifies bottlenecks: table scans, missing indexes, join cardinality
```

## HDI Container Integration

HANA Deployment Infrastructure (HDI) — containerized database logic in CAP projects:

```
db/src/
├── procedures/
│   └── ZSP_MATERIAL.hdbprocedure
├── functions/
│   └── ZTF_PRODUCT.hdbtablefunction
└── src/
    └── .hdinamespace
```

## Gotchas
- Use **declarative logic** whenever possible — imperative cursors are slower
- Table variables use DEFAULT memory pool — watch memory consumption
- CURSOR with ORDER BY: use LIMIT or the entire result set is materialized
- CE functions: undocumented but extremely performant for aggregations
