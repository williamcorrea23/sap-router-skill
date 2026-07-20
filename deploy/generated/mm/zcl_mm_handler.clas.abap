CLASS zcl_mm_handler DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES zif_mm_handler.
    ALIASES handle_action FOR zif_mm_handler~handle_action.

  PRIVATE SECTION.
    " MM lives inside a string literal, so this template compiles and lints
    " as-is; the generator replaces it at stamp time (e.g. MM).
    CONSTANTS co_module TYPE string VALUE 'MM'.

    METHODS create_entity
      IMPORTING
        iv_payload       TYPE string
      RETURNING
        VALUE(rs_result) TYPE zif_mm_handler=>ty_action_result.

    METHODS build_result
      IMPORTING
        iv_status        TYPE string
        iv_message       TYPE string
        iv_data          TYPE string OPTIONAL
      RETURNING
        VALUE(rs_result) TYPE zif_mm_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_mm_handler IMPLEMENTATION.

  METHOD zif_mm_handler~handle_action.
    CASE to_upper( iv_action ).
      WHEN 'PING'.
        rs_result = build_result(
          iv_status  = 'SUCCESS'
          iv_message = |{ co_module } handler alive|
          iv_data    = 'pong' ).
      WHEN 'CREATE_MATERIAL'.
        rs_result = create_entity( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_mm
          EXPORTING mv_text = |Unknown { co_module } action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_entity.
    DATA: lt_return TYPE STANDARD TABLE OF bapiret2,
          ls_return TYPE bapiret2.

    " -------------------------------------------------------------------------
    " GOLDEN PATTERN - do not reorder. See docs/model-library-design.md section 6.
    "  1. Deserialize iv_payload into a DDIC structure (nested-table-deser),
    "     never an inline TYPES, so /ui2/cl_json fills nested BAPI tables.
    "  2. Call the module BAPI. Slot BAPI_MATERIAL_SAVEDATA (e.g. BAPI_MATERIAL_SAVEDATA).
    "  3. Scan ALL BAPIRET2 rows for E/A (bapiret2-full-scan), not just row 1.
    "  4. COMMIT only after the error scan passes (commit-after-bapi-return).
    "     No COMMIT lives in the logger - the handler owns transactional state.
    " -------------------------------------------------------------------------

    CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
      TABLES
        return = lt_return.

    LOOP AT lt_return INTO ls_return WHERE type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result(
        iv_status  = 'ERROR'
        iv_message = ls_return-message ).
      RETURN.
    ENDLOOP.

    CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
      EXPORTING wait = abap_true.

    rs_result = build_result(
      iv_status  = 'SUCCESS'
      iv_message = |{ co_module } MATERIAL created| ).
  ENDMETHOD.

  METHOD build_result.
    rs_result-status  = iv_status.
    rs_result-message = iv_message.
    rs_result-data    = iv_data.
    rs_result-module  = co_module.
    GET TIME STAMP FIELD rs_result-timestamp.
  ENDMETHOD.

ENDCLASS.
