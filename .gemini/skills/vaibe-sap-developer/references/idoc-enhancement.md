# IDoc, BAdI & Enhancement Patterns
Parent skill: vaibe-sap-developer
Load when: user requests IDoc processing/retrigger, BAdI implementation, enhancement spots, error-status reprocessing.

## IDoc Retrigger — Clean-Core Pattern
Avoid direct `EDIDC`/`EDID4` table manipulation. Use released APIs:
```abap
CLASS zcl_idoc_retrigger DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    METHODS retrigger
      IMPORTING iv_docnum TYPE edidc-docnum
      RAISING   zcx_idoc_processing.
ENDCLASS.

CLASS zcl_idoc_retrigger IMPLEMENTATION.
  METHOD retrigger.
    DATA: lt_docnum TYPE STANDARD TABLE OF bdidocnum.

    APPEND iv_docnum TO lt_docnum.

    CALL FUNCTION 'EDI_DOCUMENT_RESEND_LIST'
      TABLES
        docnum_tab = lt_docnum
      EXCEPTIONS
        OTHERS     = 1.

    IF sy-subrc <> 0.
      RAISE EXCEPTION NEW zcx_idoc_processing(
        textid = zcx_idoc_processing=>retrigger_failed ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```
Rule: only retrigger IDocs in error status (51, 56, 64). Always log docnum + old status + retrigger timestamp before calling resend — needed for audit trail and idempotency checks (don't retrigger same doc twice within a debounce window).

## RAP Wrapping for IDoc Monitor (Clean-Core consumption)
Expose retrigger as a RAP **action**, not a raw RFC-callable function module:
```abap
action ( features : instance ) retriggerIdoc result [1] $self;
```
```abap
METHOD retriggerIdoc.
  LOOP AT keys INTO DATA(key).
    TRY.
        zcl_idoc_retrigger=>retrigger( iv_docnum = key-IdocNumber ).
      CATCH zcx_idoc_processing INTO DATA(lx).
        APPEND VALUE #( %tky = key-%tky %msg = lx ) TO reported-idocmonitor.
        APPEND VALUE #( %tky = key-%tky ) TO failed-idocmonitor.
    ENDTRY.
  ENDLOOP.
ENDMETHOD.
```

## BAdI Implementation Skeleton
```abap
CLASS zcl_im_idoc_inbound DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_ex_idoc_inbound.   " or relevant std BAdI interface
ENDCLASS.

CLASS zcl_im_idoc_inbound IMPLEMENTATION.
  METHOD if_ex_idoc_inbound~inbound_processing.
    " single-responsibility: delegate to a Z-class, never inline logic in BAdI impl
    zcl_idoc_inbound_handler=>process( it_idoc_data = idoc_data ).
  ENDMETHOD.
ENDCLASS.
```
Rule: BAdI implementation class is a thin adapter — delegate to a standalone class so the logic is unit-testable without the enhancement framework in the loop.

## Enhancement Spot vs Key User Extensibility
- **S/4HANA Cloud Public Edition**: only key-user/in-app extensibility allowed (custom fields, custom logic via released BAdIs in the extensibility catalog). No classic enhancement spots, no implicit/explicit enhancements outside catalog.
- **S/4HANA Cloud Private Edition / On-Premise**: classic BAdIs, user-exits, implicit enhancements available — still prefer released BAdIs over implicit enhancements for upgrade stability.
- Always confirm which edition before generating enhancement code — wrong assumption breaks upgrade compatibility.

## Idempotency Note
Mass retrigger jobs must check last-retrigger-timestamp before resending — prevents duplicate postings if scheduled job overlaps manual retrigger.
