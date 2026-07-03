---
name: clean-abap
description: Clean ABAP Style Guide — naming conventions, formatting rules, method length limits, error handling patterns, OO best practices, modern ABAP conventions based on SAP Clean ABAP Style Guide (CC BY 4.0). Use when writing ABAP code, reviewing ABAP code quality, refactoring ABAP, or applying clean code rules to ABAP programs.
trigger:
  keywords: [Clean ABAP, style guide, naming convention, formatting, method length, error handling, OO best practice, modern ABAP, refactoring, code quality]
  intent: >-
    Apply Clean ABAP style guide rules for naming, formatting, error handling, and modern ABAP conventions when writing or reviewing ABAP code.
---

# Clean ABAP Style Guide

Clean ABAP patterns derived from SAP Clean ABAP Style Guide (CC BY 4.0).

## Naming Conventions

| Rule | Good | Bad |
|---|---|---|
| Variables descriptive | `lv_material_description` | `lv_md` |
| Classes prefixed ZCL_ | `zcl_material_handler` | `material_class` |
| Methods verb-first | `create_material()` | `material_create()` |
| Booleans with is/has | `is_active`, `has_errors` | `active_flag` |
| Constants UPPER case | `gc_max_retries` | `max_retries` |

## Formatting

```abap
" Good
METHOD create_material.
  DATA(ls_header) = prepare_header( iv_payload ).
  DATA(ls_return) = call_bapi( ls_header ).
  check_result( ls_return ).
ENDMETHOD.

" Bad
METHOD create_material.
data(ls_header)=prepare_header(iv_payload).
data(ls_return)=call_bapi(ls_header).
check_result(ls_return).
ENDMETHOD.
```

## Method Rules

- Max 50 lines per method (not counting declarations block)
- Single responsibility — one method, one purpose
- Extract conditions into self-documenting methods:
  ```abap
  " Good
  IF is_material_locked( lv_matnr ).
    RETURN.
  ENDIF.

  " Bad
  IF lt_lock[] IS NOT INITIAL AND lv_matnr IN lt_lock.
    RETURN.
  ENDIF.
  ```

## Error Handling

```abap
" Prefer class-based exceptions
TRY.
    DATA(lo_handler) = get_handler( iv_module ).
    lo_handler->handle_action( iv_action = iv_action iv_payload = iv_payload ).
  CATCH cx_zrouter INTO DATA(lx).
    mo_logger->log_action( iv_status = 'ERROR' iv_message = lx->mv_text ).
ENDTRY.

" Not:
" CALL FUNCTION ... EXCEPTIONS OTHERS = 99.
```

## Inline Declarations

```abap
" Good (ABAP 7.40+)
DATA(lv_matnr) = 'MAT001'.
DATA(lt_materials) = VALUE string_table( ( 'MAT001' ) ( 'MAT002' ) ).

" Not
DATA lv_matnr TYPE matnr.
lv_matnr = 'MAT001'.
```

## SELECT Optimization

```abap
" Good
SELECT matnr, maktx FROM mara WHERE matnr = @lv_matnr INTO TABLE @DATA(lt_mara).

" Not
SELECT * FROM mara INTO TABLE lt_mara WHERE matnr = lv_matnr.
```

## Modern Constructors

```abap
" Good
mo_logger = NEW zcl_zrouter_logger( ).
DATA(lt_data) = VALUE #( ( a = 1 b = 2 ) ( a = 3 b = 4 ) ).

" Not
CREATE OBJECT mo_logger.
APPEND INITIAL LINE TO lt_data ASSIGNING FIELD-SYMBOL(<ls>).
<ls>-a = 1.
<ls>-b = 2.
```

## COND / SWITCH

```abap
lv_status = COND #(
  WHEN sy-subrc = 0 THEN 'SUCCESS'
  WHEN sy-subrc = 4 THEN 'NOT_FOUND'
  ELSE 'ERROR'
).

lv_handler_type = SWITCH #( iv_module
  WHEN 'MM'  THEN 'MATERIAL'
  WHEN 'SD'  THEN 'SALES'
  WHEN 'FI'  THEN 'FINANCE'
  ELSE THROW cx_zrouter( mv_text = |Unknown: { iv_module }| )
).
```

## Gotchas

- **COMMIT WORK / ROLLBACK WORK** — deprecated in BAPI context. Use BAPI_TRANSACTION_COMMIT/ROLLBACK
- **SELECT * in loops** — largest performance killer in ABAP
- **Long methods** — extract; code review catches methods > 50 lines
- **Missing inline declarations** — DATA(lv_x) cleaner than DATA lv_x TYPE ...

## Integration with ZROUTER

All ZROUTER_DISPATCH handler classes follow Clean ABAP conventions:
- `zcl_zrouter_handler_abstract` — template method pattern
- `evaluate_expression` — single-method, inline declared
- BAPI calls use BAPI_TRANSACTION_COMMIT with WAIT = 'X'
