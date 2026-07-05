CLASS zcl_zrouter_batch DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_batch_action,
        seqnr   TYPE i,
        module  TYPE string,
        action  TYPE string,
        payload TYPE string,
      END OF ty_batch_action,
      ty_batch_actions TYPE STANDARD TABLE OF ty_batch_action,

      BEGIN OF ty_batch_item_result,
        seqnr   TYPE i,
        module  TYPE string,
        action  TYPE string,
        status  TYPE string,
        message TYPE string,
        data    TYPE string,
      END OF ty_batch_item_result,
      ty_batch_results TYPE STANDARD TABLE OF ty_batch_item_result,

      BEGIN OF ty_batch_result,
        batch_guid TYPE sysuuid_c32,
        status     TYPE string,
        results    TYPE ty_batch_results,
      END OF ty_batch_result.

    METHODS execute_batch
      IMPORTING it_actions       TYPE ty_batch_actions
      RETURNING VALUE(rs_result) TYPE ty_batch_result.

    METHODS constructor
      IMPORTING io_dispatch TYPE REF TO zcl_zrouter_dispatch OPTIONAL.

  PRIVATE SECTION.
    DATA mo_dispatch TYPE REF TO zcl_zrouter_dispatch.
    DATA mo_logger   TYPE REF TO zif_zrouter_logger.
    METHODS save_batch_result
      IMPORTING
        iv_batch_guid TYPE sysuuid_c32
        iv_seqnr      TYPE i
        iv_module     TYPE string
        iv_action     TYPE string
        iv_status     TYPE string
        iv_message    TYPE string
        iv_payload    TYPE string
        iv_result     TYPE string.
    METHODS generate_guid RETURNING VALUE(rv_guid) TYPE sysuuid_c32.
ENDCLASS.


CLASS zcl_zrouter_batch IMPLEMENTATION.
  METHOD constructor.
    IF io_dispatch IS SUPPLIED.
      mo_dispatch = io_dispatch.
    ELSE.
      mo_dispatch = NEW zcl_zrouter_dispatch( ).
    ENDIF.
    mo_logger = NEW zcl_zrouter_logger( ).
  ENDMETHOD.

  METHOD generate_guid.
    TRY.
        rv_guid = cl_system_uuid=>create_uuid_c32_static( ).
      CATCH cx_uuid_error.
        " sy-index is 0 outside of loops — use random fallback
        rv_guid = |{ cl_abap_random_int=>create(
          seed = cl_abap_random=>seed( )
          min  = 1000000000
          max  = 9999999999 )->get_next( ) }|.
    ENDTRY.
  ENDMETHOD.

  METHOD save_batch_result.
    DATA: ls_batch TYPE zrouter_batch_result.
    ls_batch-batch_guid = iv_batch_guid.
    ls_batch-seqnr      = iv_seqnr.
    ls_batch-module     = iv_module.
    ls_batch-action     = iv_action.
    ls_batch-status     = iv_status.
    ls_batch-message    = iv_message.
    ls_batch-payload    = iv_payload.
    ls_batch-result     = iv_result.
    GET TIME STAMP FIELD ls_batch-timestamp.
    MODIFY zrouter_batch_result FROM @ls_batch.
  ENDMETHOD.

  METHOD execute_batch.
    DATA(lv_overall_status) = 'SUCCESS'.
    rs_result-batch_guid = generate_guid( ).

    LOOP AT it_actions INTO DATA(ls_action).
      DATA(ls_dispatch) = mo_dispatch->dispatch(
        iv_module  = ls_action-module
        iv_action  = ls_action-action
        iv_payload = ls_action-payload ).

      APPEND VALUE #( seqnr   = ls_action-seqnr
                      module  = ls_action-module
                      action  = ls_action-action
                      status  = ls_dispatch-status
                      message = ls_dispatch-message
                      data    = ls_dispatch-data ) TO rs_result-results.

      save_batch_result(
        iv_batch_guid = rs_result-batch_guid
        iv_seqnr      = ls_action-seqnr
        iv_module     = ls_action-module
        iv_action     = ls_action-action
        iv_status     = ls_dispatch-status
        iv_message    = ls_dispatch-message
        iv_payload    = ls_action-payload
        iv_result     = ls_dispatch-data ).

      IF ls_dispatch-status = 'ERROR'.
        lv_overall_status = 'ERROR'.
        " Each handler already did BAPI_TRANSACTION_ROLLBACK for its own LUW.
        " Stop processing but do NOT rollback here — prior successful
        " actions are already committed by their own handlers.
        EXIT.
      ENDIF.
    ENDLOOP.

    IF lv_overall_status = 'SUCCESS'.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'.
    ENDIF.

    rs_result-status = lv_overall_status.
    mo_logger->log_action(
      iv_module  = 'BATCH'
      iv_action  = 'EXECUTE'
      iv_status  = rs_result-status
      iv_message = |Batch { rs_result-batch_guid } completed with { lines( rs_result-results ) } actions| ).
  ENDMETHOD.
ENDCLASS.