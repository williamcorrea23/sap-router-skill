CLASS zcl_zrouter_handler_co DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_internal_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS activity_alloc
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_co IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'CO' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_INTERNAL_ORDER'.
        rs_result = create_internal_order( iv_payload ).
      WHEN 'ACTIVITY_ALLOC'.
        rs_result = activity_alloc( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown CO action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_internal_order.
    DATA: ls_master_data TYPE bapi2075_7,
          ls_ret         TYPE bapiret2,
          lv_orderid     TYPE bapi2075_2-order.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_master_data ).

    CALL FUNCTION 'BAPI_INTERNALORDER_CREATE'
      EXPORTING
        i_master_data = ls_master_data
      IMPORTING
        orderid       = lv_orderid
        return        = ls_ret.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Internal order creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Internal order created' iv_data = lv_orderid ).
    ENDIF.
  ENDMETHOD.

  METHOD activity_alloc.
    DATA: ls_params TYPE zrouter_co_alloc_params,
          ls_ret    TYPE bapiret2.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'BAPI_CO_ALLOCACTUALS'
      EXPORTING
        controllingarea = ls_params-controlling_area
        sendercostcenter = ls_params-sender_cost_center
        receivercostcenter = ls_params-receiver_cost_center
        activitytype    = ls_params-activity_type
        quantity        = ls_params-quantity
        fiscalperiod    = ls_params-period
        fiscalyear      = ls_params-fiscal_year
      IMPORTING
        return          = ls_ret.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Activity allocation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Activity allocation posted' ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.