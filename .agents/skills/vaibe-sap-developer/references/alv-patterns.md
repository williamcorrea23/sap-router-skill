# ALV Reporting (Classic FM-based and OO)
Parent skill: vaibe-sap-developer
Load when: the user requests an ALV report/list display — classic `REUSE_ALV_GRID_DISPLAY` or object-oriented `CL_GUI_ALV_GRID`/`CL_SALV_TABLE`.

Edition check first — per `references/edition-legality.md`, both ALV flavors render via the classic SAP GUI control framework, which is **❌ not available** in Cloud Public Edition or BTP ABAP Environment. For those editions, redirect to a Fiori Elements List Report on a RAP BO (`references/rap-patterns.md` + `references/odata-fiori.md`) instead of generating ALV code.

## Prefer `CL_SALV_TABLE` over `REUSE_ALV_GRID_DISPLAY` for new On-Premise/Private Edition work
`CL_SALV_TABLE` is the modern OO wrapper — simpler API, same rendering engine underneath. Only use the classic function module when extending an existing classic-ALV report.

```abap
DATA(lo_salv) = NEW cl_salv_table( ).
cl_salv_table=>factory(
  IMPORTING r_salv_table = lo_salv
  CHANGING  t_table      = lt_results ).

lo_salv->get_columns( )->get_column( 'NETWR' )->set_short_text( 'Net Value' ).
lo_salv->get_functions( )->set_all( ).
lo_salv->display( ).
```
Rule: build `lt_results` via a separate, testable class method — don't run the `SELECT` inline before the ALV call; keep data retrieval and display assembly separate (see `references/anti-patterns.md`).

## Classic function-module ALV (legacy-extension only)
```abap
CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
  EXPORTING
    i_callback_program = sy-repid
    is_layout          = ls_layout
    it_fieldcat        = lt_fieldcat
  TABLES
    t_outtab           = lt_results.
```
Rule: only generate this form when the user is maintaining an existing classic-ALV report that already uses it — never propose it for new development.

## Interactive ALV (drill-down)
Use `CL_SALV_TABLE` event handlers (`HANDLE_DOUBLE_CLICK`, `HANDLE_LINK_CLICK`) rather than the classic `AT LINE-SELECTION`/`user_command` callback pattern for any new interactive list — keeps the handler logic in a class, testable in isolation from the list framework.

## Anti-patterns
- Don't generate ALV code at all for Cloud Public Edition or BTP ABAP Environment — flag the edition mismatch and offer the Fiori/RAP alternative instead.
- Don't build the field catalog by hand when the structure is already DDIC-registered — derive it (`cl_salv_table=>factory` does this automatically from a typed internal table).
