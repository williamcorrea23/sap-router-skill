# Forms (Smart Forms / Adobe Forms / SAPscript)
Parent skill: vaibe-sap-developer
Load when: user requests print/PDF output for documents (PO, invoice, delivery note, etc.) via Smart Forms, Adobe Forms, or legacy SAPscript.

Edition check first — per `references/edition-legality.md`, classic form technology is **❌ not available** in Cloud Public Edition or BTP ABAP Environment (no released API for SSF/Adobe form processing). Only generate this for On-Premise or Cloud Private Edition. If the declared environment is Public Edition or BTP, say so and point to a modern alternative (e.g. Adobe Document Server output via a released API, or a Fiori-based output preview) instead of generating SAPscript/Smart Form driver code.

## Smart Forms driver pattern
```abap
CALL FUNCTION 'SSF_FUNCTION_MODULE_NAME'
  EXPORTING
    formname           = 'ZSF_PURCHASE_ORDER'
  IMPORTING
    fm_name             = lv_fm_name
  EXCEPTIONS
    no_form             = 1
    no_function_module  = 2
    OTHERS              = 3.
IF sy-subrc <> 0.
  " handle via message class, see references/exception-patterns.md
ENDIF.

CALL FUNCTION lv_fm_name
  EXPORTING
    is_header  = ls_header
  TABLES
    it_items   = lt_items
  EXCEPTIONS
    formatting_error = 1
    internal_error   = 2
    send_error       = 3
    user_canceled    = 4
    OTHERS           = 5.
```
Rule: always resolve the generated FM name dynamically via `SSF_FUNCTION_MODULE_NAME` — never hardcode a `/1BCDWB/SF...` generated name, it changes per form version/transport.

## Adobe Forms driver pattern
```abap
CALL FUNCTION 'FP_FUNCTION_MODULE_NAME'
  EXPORTING
    i_name     = 'ZADOBE_INVOICE'
  IMPORTING
    e_funcname = lv_fm_name.

CALL FUNCTION 'FP_JOB_OPEN'
  CHANGING
    ie_outputparams = ls_output_params.

CALL FUNCTION lv_fm_name
  EXPORTING
    /1bcdwb/docparams = ls_doc_params
    is_header         = ls_header.

CALL FUNCTION 'FP_JOB_CLOSE'.
```
Rule: `FP_JOB_OPEN`/`FP_JOB_CLOSE` always bracket the call — never call the generated form FM standalone without an open job, output is undefined.

## SAPscript (legacy fallback only)
Only generate SAPscript driver logic (`OPEN_FORM`/`WRITE_FORM`/`CLOSE_FORM`) when the user explicitly says an existing SAPscript form must be extended — never propose new SAPscript development; Smart Forms or Adobe Forms are the baseline for any new on-premise form work.

## Anti-patterns
- Don't build layout logic (column widths, page breaks) in ABAP string concatenation — that belongs in the form layout/template, not the driver program.
- Don't skip device-type resolution (`SSF_GET_DEVICE_TYPE`) when output device varies (printer vs PDF preview vs archive).
