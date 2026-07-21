# Function Module Patterns
Parent skill: vaibe-sap-developer
Load when: user requests a Function Module, RFC-enabled FM, or an FM wrapper for an existing interface.

Clean Core guidance first: prefer a class + method over a new Function Module whenever there's a choice — FMs lack interfaces/inheritance and are harder to unit test in isolation. Generate a new FM only when the use case genuinely needs it: RFC-callable legacy interface, BAPI-style wrapper other systems already call by name, or extending an existing FM group's interface for compatibility.

## Skeleton — RFC-enabled FM as a thin wrapper over a class
```abap
FUNCTION z_get_sales_order_status.
*"----------------------------------------------------------------------
*"*"Local interface:
*"  IMPORTING
*"     VALUE(IV_VBELN) TYPE  VBELN_VA
*"  EXPORTING
*"     VALUE(EV_STATUS) TYPE  STRING
*"  EXCEPTIONS
*"      NOT_FOUND
*"----------------------------------------------------------------------
  TRY.
      ev_status = zcl_sales_order_status=>get_status( iv_vbeln = iv_vbeln ).
    CATCH zcx_sales_order_not_found.
      RAISE not_found.
  ENDTRY.
ENDFUNCTION.
```
Rule: the FM body only translates between the classic FM signature and a class method call — all logic lives in the class so it stays unit-testable (see `references/unit-test-patterns.md`). Never put branching business logic directly in the FM body.

## Classic EXCEPTIONS interface
FM signatures predate class-based exceptions — exceptions are declared as classic named exceptions (`NOT_FOUND` above), not exception classes. Map any internal class-based exception (`zcx_*`) to the right classic exception name in the wrapper; don't let a class-based exception propagate unhandled out of an FM.

## TABLES parameters
Avoid the legacy `TABLES` parameter type for new FMs — use `IMPORTING`/`EXPORTING` with typed table parameters instead. `TABLES` is only for extending an existing FM that already has one (compatibility), never for new development.

## BAPI conventions
A BAPI is a Function Module with extra naming/structural rules — `BAPI_<businessobject>_<operation>` (e.g. `BAPI_SALESORDER_CHANGE`), a `RETURN` table of type `BAPIRET2` for messages instead of classic `EXCEPTIONS`, and **no internal `COMMIT WORK`** — the caller is responsible for committing.
```abap
FUNCTION bapi_po_approval_set.
*"  IMPORTING
*"     VALUE(IV_VBELN) TYPE  VBELN_VA
*"  TABLES
*"      RETURN STRUCTURE  BAPIRET2
  TRY.
      zcl_po_approval=>approve( iv_vbeln = iv_vbeln ).
      APPEND VALUE bapiret2( type = 'S' id = 'ZPO' number = '001' ) TO return.
    CATCH zcx_po_approval_error INTO DATA(lx_error).
      APPEND VALUE bapiret2( type = 'E' id = 'ZPO' number = '002'
        message_v1 = lx_error->get_text( ) ) TO return.
  ENDTRY.
ENDFUNCTION.
```
Rule: never call `COMMIT WORK` inside a BAPI — the standard pattern is BAPI call, caller inspects `RETURN` for errors, caller explicitly calls `BAPI_TRANSACTION_COMMIT` (or rolls back). A BAPI that commits internally breaks LUW control for any caller batching multiple BAPI calls together.

## Anti-patterns
- Don't `SELECT` directly inside the FM body — delegate to a class that uses set-based Open SQL (see `references/anti-patterns.md`).
- Don't create a new FM at all if the request is really "I need a method on an existing/new class" — confirm an RFC-callable interface is genuinely required before defaulting here.
