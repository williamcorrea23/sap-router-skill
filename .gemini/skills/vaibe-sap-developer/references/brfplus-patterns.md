# BRFplus (Business Rules Framework plus)
Parent skill: vaibe-sap-developer
Load when: the user needs a decision table, rule set, or expression authored in BRFplus, or the ABAP-side call into an existing BRFplus application/function.

BRFplus applications/rule sets are built in the BRFplus workbench (transaction `BRF+`), not generated as ABAP — describe the structure precisely (decision table columns, expression types) so it's a direct copy-in, and generate only the ABAP call-side code.

## Availability by edition
- On-Premise / Private Edition / BTP ABAP Environment — full custom BRFplus application development.
- Cloud Public Edition — ⚠ custom BRFplus application development is generally **not** part of standard developer/key-user extensibility; BRFplus mostly appears there pre-built inside specific scenarios (e.g. Flexible Workflow's condition steps, output parameter determination), which the key user configures through the owning app rather than the BRFplus workbench directly. Confirm with the user whether they actually have BRFplus workbench access on a Public Edition tenant before designing a new custom application — don't assume it.

## Calling a BRFplus function from ABAP
```abap
DATA(lv_function_id) = '0123456789ABCDEF...'.   " from BRFplus workbench

CALL FUNCTION 'FDT_FUNCTION_PROCESS'
  EXPORTING
    iv_function_id     = lv_function_id
  IMPORTING
    eo_event_publisher = lo_event_publisher
  CHANGING
    ct_context_data    = lt_context.
```
Or the newer typed API via `CL_FDT_FUNCTION_PROCESS=>FACTORY` / `IF_FDT_FUNCTION~PROCESS` when typed access generation is enabled in BRFplus — prefer this for new development, it gives typed result structures instead of generic context tables.

## Decision table design notes (for the workbench, not ABAP)
```
Decision table: Z_PO_APPROVAL_LEVEL
Condition columns: Company Code, Order Value (range)
Result column: Required Approval Level
```
Rule: keep condition columns to fields the calling ABAP can actually supply at call time — a decision table referencing a field the caller never populates will silently fail to match any row and fall through to the default result.

## Anti-patterns
- Don't generate ABAP that re-implements decision-table logic inline "to save a step" — if a decision table already exists or is requested, the rule belongs there, not duplicated in the calling class.
- Don't assume custom BRFplus workbench access exists on Cloud Public Edition without the user confirming it.
