# DDIC Objects (Tables, Structures, Domains, Search Helps, Lock Objects, Number Ranges)
Parent skill: vaibe-sap-developer
Load when: the user needs a new database table, structure, data element/domain, search help, lock object, or number range object — the Data Dictionary primitives underneath any RAP/CDS/class-based development.

These are mostly DDIC metadata, not executable ABAP — describe the object's structure precisely (field list, types, keys) rather than generating "code" for it; the actual creation happens in SE11/SNRO, but get the field-level spec right so it's a direct copy-in.

## Custom database table
```
Table: ZPO_APPROVAL
Delivery class: A (application table)
Fields:
  MANDT     CLNT  3   (key, client)
  VBELN     CHAR 10   (key, sales document)
  APPR_STAT CHAR  1   (approval status: blank/A/R)
  APPR_BY   CHAR 12   (approver user ID)
  APPR_AT   TIMS  6   (approval timestamp)
Technical settings: data class APPL1, size category 0, buffering off (transactional data — never buffer a table that's updated per-transaction).
```
Rule: never recommend table buffering for a table that gets written frequently (status/transactional tables) — only for slow-changing master/customizing data.

## Lock object (SE11 → lock object, generates ENQUEUE_/DEQUEUE_ FMs)
```
Lock object: EZPO_APPROVAL
Lock mode: E (exclusive)
Primary table: ZPO_APPROVAL
Lock fields: VBELN
```
Usage in code:
```abap
CALL FUNCTION 'ENQUEUE_EZPO_APPROVAL'
  EXPORTING
    vbeln = lv_vbeln
  EXCEPTIONS
    foreign_lock = 1
    OTHERS       = 2.
IF sy-subrc <> 0.
  " someone else is editing this record — see references/exception-patterns.md
ENDIF.
" ... do the update ...
CALL FUNCTION 'DEQUEUE_EZPO_APPROVAL'
  EXPORTING
    vbeln = lv_vbeln.
```
Rule: always pair ENQUEUE with DEQUEUE in the same method, including in every exception path — a forgotten DEQUEUE on an error branch leaves the record locked until the session ends.

## Number range object (SNRO)
Advisory, not generatable code: object name (≤10 char), number length, whether it's numeric/alpha, and at least one interval (from/to/current) — this is Customizing done in SNRO, not ABAP. Once created, draw the next number with:
```abap
CALL FUNCTION 'NUMBER_GET_NEXT'
  EXPORTING
    nr_range_nr = '01'
    object      = 'ZPO_APPR'
  IMPORTING
    number      = lv_number.
```

## Search help
Only needed when a field's value-help can't be satisfied by an existing one — confirm no standard/existing search help already covers the field before proposing a new one.

## Anti-patterns
- Don't propose buffering for a table that's written per-document/per-transaction.
- Don't generate ENQUEUE without a matching DEQUEUE on every exit path, including exceptions.
- Don't invent field lengths/types — if the user hasn't given them, ask rather than guessing a plausible-looking type.
