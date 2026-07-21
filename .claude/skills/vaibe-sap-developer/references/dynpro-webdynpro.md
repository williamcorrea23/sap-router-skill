# Classic Dynpro & WebDynpro ABAP
Parent skill: vaibe-sap-developer
Load when: user explicitly requests a classic screen (Dynpro) or a WebDynpro ABAP component — almost always a legacy-maintenance request on an existing app, not new development.

Edition check first — per `references/edition-legality.md`, both are **❌ not available** in Cloud Public Edition or BTP ABAP Environment (no classic UI runtime there). On-Premise and Private Edition only.

**Clean Core flag, every time:** even on On-Premise/Private Edition, surface a note that Fiori Elements on RAP/OData (`references/rap-patterns.md` + `references/odata-fiori.md`) is the modern path for any *new* UI — only generate Dynpro/WebDynpro code when the user is explicitly maintaining/extending an existing screen or component, not for greenfield UI work.

## Classic Dynpro — PBO/PAI skeleton
```abap
MODULE status_0100 OUTPUT.
  SET PF-STATUS 'MAIN0100'.
  SET TITLEBAR 'TIT0100'.
ENDMODULE.

MODULE user_command_0100 INPUT.
  CASE sy-ucomm.
    WHEN 'SAVE'.
      zcl_my_logic=>save( is_data = gs_screen_data ).
    WHEN 'BACK' OR 'EXIT' OR 'CANC'.
      LEAVE TO SCREEN 0.
  ENDCASE.
ENDMODULE.
```
Rule: PAI modules dispatch to a class method (same thin-adapter principle as elsewhere in this skill) — don't write business logic directly inside the `MODULE ... INPUT` block; it can't be unit tested there.

## WebDynpro ABAP — lifecycle + context skeleton
```abap
METHOD wddoinit.
  DATA(lo_node) = wd_context->get_child_node( 'SALES_ORDER' ).
  lo_node->bind_table( zcl_sales_order_reader=>get_open_orders( ) ).
ENDMETHOD.

METHOD onactionapprove.
  DATA(lo_node) = wd_context->get_child_node( 'SALES_ORDER' ).
  DATA(ls_order) = lo_node->get_element( )->get_static_attributes( ).
  zcl_sales_order_approval=>approve( iv_vbeln = ls_order-vbeln ).
ENDMETHOD.
```
Rule: bind context nodes to data already produced by a class method — don't run direct `SELECT`s inside `WDDOINIT` or an action handler.

## Anti-patterns
- Don't generate either of these for Cloud Public Edition or BTP ABAP Environment — flag the edition mismatch instead of producing dead-on-arrival code.
- Don't propose new Dynpro/WebDynpro development when the request is "build a new screen for X" with no existing legacy app to maintain — ask whether Fiori/RAP is acceptable first.
