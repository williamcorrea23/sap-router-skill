---
name: abap-code-patterns
description: >-
  ABAP development patterns and best practices — BAPI/RFC calls, GENERATE
  SUBROUTINE POOL dynamic evaluation, INSERT REPORT + SUBMIT, Clean ABAP
  patterns, DDIC design, exception handling with CX_STATIC_CHECK, BAL
  application logging, and ABAP OO design patterns. Use when writing,
  reviewing, or refactoring ABAP code; when asked about ABAP patterns,
  BAPI integration, dynamic programming, or Clean ABAP rules; when
  implementing ZROUTER handlers or SAP ABAP classes.
---

# ABAP Code Patterns

Reference for ABAP development patterns used in ZROUTER_DISPATCH and
related SAP projects. Based on Clean ABAP, SAP Community best practices,
and patterns validated via abaplint.

## BAPI/RFC Pattern

```abap
" Always use BAPI_TRANSACTION_COMMIT with WAIT = 'X' for BAPI calls
" Never use COMMIT WORK — doesn't trigger BAPI update task
CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
  EXPORTING
    headdata = ls_header
  IMPORTING
    return   = ls_ret.
IF ls_ret-type = 'E' OR ls_ret-type = 'A'.
  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
  " Handle error
ELSE.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING wait = 'X'.
ENDIF.
```

## GENERATE SUBROUTINE POOL (Dynamic Eval)

```abap
" Compiles ABAP source at runtime, lighter than INSERT REPORT + SUBMIT
" Use for config-driven transformations, expression evaluation
DATA: lt_source TYPE TABLE OF string,
      lv_pool   TYPE string.

APPEND |PROGRAM.| TO lt_source.
APPEND |FORM eval CHANGING cv_result TYPE string.| TO lt_source.
SPLIT iv_expression AT cl_abap_char_utilities=>newline INTO TABLE DATA(lt_lines).
APPEND LINES OF lt_lines TO lt_source.
APPEND |ENDFORM.| TO lt_source.

GENERATE SUBROUTINE POOL lt_source
  NAME lv_pool
  MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).

IF sy-subrc <> 0.
  " Handle syntax error — lv_line is offset from FORM start (+2)
  RAISE EXCEPTION TYPE cx_zrouter
    EXPORTING mv_text = |Syntax error line { lv_line - 2 }: { lv_msg }|.
ENDIF.

PERFORM ('EVAL') IN PROGRAM (lv_pool) IF FOUND CHANGING cv_result.
```

## INSERT REPORT + SUBMIT (Full Dynamic)

```abap
" Full dynamic ABAP — creates temp program, SUBMITs, captures WRITE output
" Heavier than GENERATE SUBROUTINE POOL, use when you need WRITE capture
DATA: lv_report TYPE syrepid,
      lt_source TYPE TABLE OF string.

APPEND |REPORT ztemp.| TO lt_source.
APPEND LINES OF lt_dynamic_code TO lt_source.

INSERT REPORT lv_report FROM lt_source.
SUBMIT (lv_report) VIA SELECTION-SCREEN AND RETURN.
" Capture output via LIST_FROM_MEMORY + LIST_TO_ASCI
```

## DDIC Table Design

```abap
" Header + Item pattern with client-dependency
" Always include MANDT as first key field
" Use CHAR for flags (X = true), NUMC for version numbers
" TIMESTAMPL for UTC timestamps

" Header: ZROUTER_TMPL_HD
"   MANDT (key), TEMPLATE_ID (key), MODULE, ACTION, VERSION,
"   TITLE, DESCRIPTION, CATEGORY, CREATED_BY, CREATED_AT, ACTIVE_FLAG

" Items: ZROUTER_TMPL_CD
"   MANDT (key), TEMPLATE_ID (key), LINE_NUM (key), CODE_LINE
```

## Clean ABAP Rules

1. **No SELECT * — use field lists**: `SELECT matnr, maktx FROM mara INTO TABLE @lt_mara`
2. **Inline declarations**: `DATA(lv_matnr) = 'MAT001'` not `DATA lv_matnr TYPE matnr`
3. **NEW constructor**: `mo_logger = NEW zcl_zrouter_logger( )` not `CREATE OBJECT`
4. **VALUE operator**: `lt_data = VALUE #( ( a = 1 ) ( a = 2 ) )`
5. **COND / SWITCH**: `lv_status = COND #( WHEN sy-subrc = 0 THEN 'OK' ELSE 'ERROR' )`
6. **FOR loops**: `LOOP AT lt_materials ASSIGNING FIELD-SYMBOL(<ls_mat>)`
7. **No COMMIT WORK / ROLLBACK WORK**: Use BAPI_TRANSACTION_COMMIT/ROLLBACK
8. **Exception classes**: Inherit from CX_STATIC_CHECK, not CX_ROOT
9. **/UI2/CL_JSON**: Use standard JSON class, never manual PCRE parsing
10. **BAL logging**: BAL_LOG_CREATE → BAL_LOG_MSG_ADD → BAL_DB_SAVE

## ABAP OO Patterns

```abap
" Abstract handler + subclass per module
CLASS zcl_handler_abstract DEFINITION PUBLIC ABSTRACT.
  PUBLIC SECTION.
    INTERFACES zif_handler.
  PROTECTED SECTION.
    METHODS handle_custom_action ABSTRACT.
ENDCLASS.

CLASS zcl_handler_mm DEFINITION PUBLIC FINAL
  INHERITING FROM zcl_handler_abstract.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
ENDCLASS.

" Factory dispatch
CASE to_upper( iv_module ).
  WHEN 'MM'.
    ro_handler = NEW zcl_handler_mm( ).
  WHEN 'SD'.
    ro_handler = NEW zcl_handler_sd( ).
ENDCASE.
```

## Gotchas

- **GENERATE SUBROUTINE POOL error line offset**: line numbers start at FORM, not PROGRAM. Subtract 2 to get user expression line.
- **BAPI_TRANSACTION_COMMIT WAIT = 'X'**: Without WAIT, update task runs async — next BAPI may see stale data.
- **RFC_READ_TABLE max 512 chars**: Field value truncated. Use ADT SQL or HANA query for long fields.
- **sy-subrc after BAPI call**: Check BAPIRET2-TYPE, not sy-subrc. Some BAPIs return sy-subrc=0 with TYPE='E'.
