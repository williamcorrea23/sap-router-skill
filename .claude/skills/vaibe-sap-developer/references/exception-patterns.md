# Exception & Error-Handling Patterns
Parent skill: vaibe-sap-developer
Load when: generating any class/method that can fail — DB ops, external calls, RAP validations.

## Message class (SE91) — created once, referenced by every exception below
Every `msgid` used below must already exist as an SE91 message class with its message numbers defined — this is Customizing, not generatable ABAP:
1. SE91 → create message class (e.g. `ZSALES`) if one doesn't already exist for the functional area.
2. Add a message number per distinct error text, with `&`-placeholders for variable parts (e.g. `001`: `Order amount & exceeds approval limit &`).
3. Reference the exact class + number in the exception constant below — never invent a `msgid`/`msgno` pair the user hasn't confirmed exists; ask for the message class name (or whether a new one should be created) if it's not given.

## Custom Exception Class Skeleton
```abap
CLASS zcx_sales_order DEFINITION
  INHERITING FROM cx_static_check.
  PUBLIC SECTION.
    CONSTANTS:
      BEGIN OF amount_invalid,
        msgid TYPE symsgid VALUE 'ZSALES',
        msgno TYPE symsgno VALUE '001',
        attr1 TYPE scx_attrname VALUE '',
      END OF amount_invalid.

    METHODS constructor
      IMPORTING
        textid   LIKE if_t100_message=>t100key OPTIONAL
        previous LIKE previous OPTIONAL.
ENDCLASS.

CLASS zcx_sales_order IMPLEMENTATION.
  METHOD constructor.
    super->constructor( previous = previous ).
    CLASS me->textid = textid.
  ENDMETHOD.
ENDCLASS.
```

## Rules
- Inherit `cx_static_check` for catchable/expected errors (business rule violations). Use `cx_no_check` only for truly unrecoverable programming errors.
- Always bind to a message class (`msgid`/`msgno`) — never construct exception text by string concatenation. Keeps i18n intact.
- One exception class per bounded context (e.g. `zcx_sales_order`, not one giant `zcx_app_error` for everything) — keeps `CATCH` blocks precise.

## Raising
```abap
RAISE EXCEPTION TYPE zcx_sales_order
  EXPORTING
    textid = zcx_sales_order=>amount_invalid.
```

## Catching — Never Swallow Silently
```abap
TRY.
    lo_processor->execute( it_data = lt_data ).
  CATCH zcx_sales_order INTO DATA(lx_order).
    " log + re-raise or surface to caller — never empty CATCH block
    RAISE EXCEPTION NEW zcx_application(
      previous = lx_order ).
ENDTRY.
```

## RAP-Specific Error Reporting
Inside behavior implementation, errors go through `failed`/`reported` structures, not `RAISE EXCEPTION`:
```abap
APPEND VALUE #( %tky = keys[ 1 ]-%tky ) TO failed-salesorder.
APPEND VALUE #( %tky = keys[ 1 ]-%tky
                 %msg = NEW zcx_sales_order( textid = zcx_sales_order=>amount_invalid ) )
  TO reported-salesorder.
```
Reject any RAP validation/determination method that uses bare `RAISE EXCEPTION` — framework expects `failed`/`reported`, not a thrown exception, inside these handler methods.
