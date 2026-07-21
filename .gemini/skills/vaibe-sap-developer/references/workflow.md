# Workflow (Flexible Workflow / Classic Business Workflow)
Parent skill: vaibe-sap-developer
Load when: user requests a workflow trigger, approval routing, or workflow-related ABAP logic.

Two distinct technologies — confirm which one before generating anything, they're not interchangeable:

| | Flexible Workflow | Classic Business Workflow (SWF) |
|---|---|---|
| Tooling | Manage Workflows Fiori app, BRFplus/Decision tables | Workflow Builder (SWDD), PFTC, BOR objects |
| Availability | On-Premise, Private Edition, Public Edition (standard scenarios only — key user adapts via app, no custom ABAP step logic) | On-Premise, Private Edition only — **❌ not available** in Public Edition or BTP ABAP Environment per `references/edition-legality.md` |
| ABAP touchpoint | Raise a Business Event; no direct workflow-engine API calls from custom code | `SAP_WAPI_*` function modules, BOR method calls |

If environment = Public Edition or BTP and the request implies classic SWF (Workflow Builder, BOR objects, `SWW_WI_START`), say so explicitly and redirect to event-based triggering for Flexible Workflow instead — don't generate classic-SWF code against a cloud edition.

## Flexible Workflow — triggering pattern (event-based, edition-safe)
```abap
CALL FUNCTION 'SWE_EVENT_CREATE'
  EXPORTING
    objtype          = 'BUS2105'        " business object type for the trigger object
    objkey           = lv_objkey
    event            = 'APPROVALNEEDED'
  EXCEPTIONS
    OTHERS = 1.
```
Rule: prefer raising the business event over any direct call into the workflow engine — this keeps the triggering class decoupled from how the receiving workflow template is configured, and is the only legal pattern for Public Edition's standard Flexible Workflow scenarios.

## Classic Business Workflow — starting a workflow (On-Premise / Private Edition only)
```abap
DATA: lv_wi_id TYPE sww_wiid.

CALL FUNCTION 'SAP_WAPI_START_WORKFLOW'
  EXPORTING
    workflow_id        = 'WS90000123'
    actual_agent       = sy-uname
    object_type        = 'BUS2105'
    object_key         = lv_objkey
  IMPORTING
    return_code        = lv_subrc
    workflow_item_id   = lv_wi_id.
```
Rule: don't hand-roll the container population — pass typed object key/type and let the workflow template's own binding handle the rest; mismatched container element names are the most common cause of a workflow starting with no data.

## Anti-patterns
- Don't embed approval-step decision logic inside the triggering ABAP class — that belongs in the workflow template/BRFplus, not the calling code.
- Don't poll for workflow completion in a tight loop from application code — workflows are async by design; use a status callback/event instead.
