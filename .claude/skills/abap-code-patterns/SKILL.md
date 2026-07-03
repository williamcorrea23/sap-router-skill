---
name: abap-code-patterns
description: >-
  ABAP development patterns and best practices — BAPI/RFC, dynamic programming,
  Clean ABAP, DDIC design, exception handling, BAL logging, ABAP OO. Use when
  writing, reviewing, or refactoring ABAP code; implementing ZROUTER handlers.
trigger:
  - "ABAP pattern"
  - "ABAP best practice"
  - "Clean ABAP"
  - "BAPI pattern"
  - "dynamic ABAP"
  - "ABAP OO design"
  - "ZROUTER handler"
  - "refactor ABAP"
  - "ABAP exception handling"
  - "BAL logging"
---

# ABAP Code Patterns

Reference for ABAP development in ZROUTER_DISPATCH and related SAP projects.
Validated against Clean ABAP guidelines and abaplint rules.

## Prerequisites

- SAP NetWeaver 7.40+ (inline declarations, VALUE, COND, FOR)
- abaplint configured (config in `package.json` `abaplint` key, or root `abaplint.json`)
- Access to SE80/ADT for object creation

## 1. BAPI/RFC Pattern

```abap
" BAPI call with proper commit/rollback
CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
  EXPORTING headdata = ls_header
  IMPORTING return   = ls_ret.

IF ls_ret-type = 'E' OR ls_ret-type = 'A'.
  CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
  RAISE EXCEPTION TYPE cx_zrouter EXPORTING mv_text = ls_ret-message.
ELSE.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
ENDIF.
```

## 2. GENERATE SUBROUTINE POOL (Dynamic Eval)

```abap
" Compile ABAP at runtime — lighter than INSERT REPORT + SUBMIT
DATA: lt_source TYPE TABLE OF string,
      lv_pool   TYPE string.

APPEND |PROGRAM.| TO lt_source.
APPEND |FORM eval CHANGING cv_result TYPE string.| TO lt_source.
APPEND LINES OF lt_lines TO lt_source.
APPEND |ENDFORM.| TO lt_source.

GENERATE SUBROUTINE POOL lt_source NAME lv_pool
  MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).

IF sy-subrc <> 0.
  RAISE EXCEPTION TYPE cx_zrouter
    EXPORTING mv_text = |Syntax error line { lv_line - 2 }: { lv_msg }|.
ENDIF.

PERFORM ('EVAL') IN PROGRAM (lv_pool) IF FOUND CHANGING cv_result.
```

## 3. Clean ABAP Quick Rules

1. **Field lists**: `SELECT matnr, maktx FROM mara` — never `SELECT *`
2. **Inline declarations**: `DATA(lv_matnr) = 'MAT001'`
3. **NEW operator**: `mo_log = NEW zcl_logger( )` — not `CREATE OBJECT`
4. **VALUE**: `lt_data = VALUE #( ( a = 1 ) ( a = 2 ) )`
5. **COND/SWITCH**: `lv_st = COND #( WHEN sy-subrc = 0 THEN 'OK' ELSE 'ERR' )`
6. **Field symbols**: `LOOP AT lt_tab ASSIGNING FIELD-SYMBOL(<ls>)`
7. **No COMMIT WORK**: Use `BAPI_TRANSACTION_COMMIT` with `wait = 'X'`
8. **Exceptions**: Inherit `CX_STATIC_CHECK`, never `CX_ROOT`
9. **JSON**: Use `/UI2/CL_JSON` — never manual PCRE parsing
10. **BAL logging**: `BAL_LOG_CREATE` → `BAL_LOG_MSG_ADD` → `BAL_DB_SAVE`

## 4. ABAP OO Pattern — Abstract Handler + Factory

```abap
CLASS zcl_handler_abstract DEFINITION PUBLIC ABSTRACT.
  PUBLIC SECTION.
    INTERFACES zif_handler.
  PROTECTED SECTION.
    METHODS handle_action ABSTRACT.
ENDCLASS.

CLASS zcl_handler_mm DEFINITION PUBLIC FINAL
  INHERITING FROM zcl_handler_abstract.
  PROTECTED SECTION.
    METHODS handle_action REDEFINITION.
ENDCLASS.

" Factory dispatch
CASE to_upper( iv_module ).
  WHEN 'MM'. ro_handler = NEW zcl_handler_mm( ).
  WHEN 'SD'. ro_handler = NEW zcl_handler_sd( ).
ENDCASE.
```

## 5. DDIC Table Design — Header + Item

- **Header** (`ZROUTER_TMPL_HD`): `MANDT` (key), `TEMPLATE_ID` (key), `MODULE`,
  `ACTION`, `VERSION`, `TITLE`, `CREATED_BY`, `CREATED_AT`, `ACTIVE_FLAG`
- **Items** (`ZROUTER_TMPL_CD`): `MANDT` (key), `TEMPLATE_ID` (key),
  `LINE_NUM` (key), `CODE_LINE`
- Use `CHAR1` for flags (`X` = true), `NUMC4` for version, `TIMESTAMPL` for UTC

## 6. INSERT REPORT + SUBMIT (Full Dynamic)

```abap
" Heavier — use only when you need WRITE output capture
INSERT REPORT lv_report FROM lt_source.
SUBMIT (lv_report) VIA SELECTION-SCREEN AND RETURN.
" Capture via LIST_FROM_MEMORY + LIST_TO_ASCI
```

## Pitfalls

- **GENERATE SUBROUTINE POOL line offset**:
  - Cause: Error line numbers start at FORM, not PROGRAM.
  - Solution: Subtract 2 to map back to user expression line.
- **BAPI_TRANSACTION_COMMIT without WAIT**:
  - Cause: Update task runs async; next BAPI may read stale data.
  - Solution: Always pass `wait = 'X'`.
- **RFC_READ_TABLE 512-char truncation**:
  - Cause: Field values silently truncated beyond 512 chars.
  - Solution: Use ADT SQL or HANA query for long text fields.
- **sy-subrc after BAPI call**:
  - Cause: Some BAPIs return `sy-subrc = 0` with `BAPIRET2-TYPE = 'E'`.
  - Solution: Always check `BAPIRET2-TYPE`, not `sy-subrc`.

## Verification

```bash
# Lint the ABAP source
npx abaplint templates/**/*.abap

# Verify BAPI commit pattern present
grep -rn "BAPI_TRANSACTION_COMMIT" src/ | grep -c "wait.*X"

# Verify no COMMIT WORK in source
grep -rn "COMMIT WORK" src/ && echo "FAIL: found COMMIT WORK" || echo "OK"
```
