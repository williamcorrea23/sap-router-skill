CLASS zcl_zrouter_logger DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES zif_zrouter_logger.
  PRIVATE SECTION.
    METHODS generate_guid RETURNING VALUE(rv_guid) TYPE sysuuid_c32.
ENDCLASS.


CLASS zcl_zrouter_logger IMPLEMENTATION.
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

  METHOD zif_zrouter_logger~log_action.
    DATA: ls_log TYPE zrouter_log.
    rv_guid = generate_guid( ).
    ls_log-guid      = rv_guid.
    ls_log-module    = iv_module.
    ls_log-action    = iv_action.
    ls_log-status    = iv_status.
    ls_log-message   = iv_message.
    ls_log-payload   = iv_payload.
    ls_log-result    = iv_result.
    ls_log-username  = sy-uname.
    GET TIME STAMP FIELD ls_log-timestamp.
    INSERT zrouter_log FROM @ls_log.
    IF sy-subrc <> 0.
      RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = 'Failed to write log entry'.
    ENDIF.
    " Note: No COMMIT WORK here. Caller (handler/dispatcher) controls LUW.
    " Log entry is persisted when handler calls BAPI_TRANSACTION_COMMIT.
  ENDMETHOD.

  METHOD zif_zrouter_logger~get_logs.
    DATA(lv_date_from) = iv_date.
    DATA(lv_date_to)   = iv_date + 1.
    SELECT guid, module, action, status, message, payload, result, username, timestamp
      FROM zrouter_log
      WHERE client = @sy-mandt
        AND ( module = @iv_module OR @iv_module IS INITIAL )
        AND ( timestamp >= @lv_date_from AND timestamp < @lv_date_to OR @iv_date IS INITIAL )
      ORDER BY timestamp DESCENDING
      INTO CORRESPONDING FIELDS OF TABLE @rt_logs.
  ENDMETHOD.
ENDCLASS.