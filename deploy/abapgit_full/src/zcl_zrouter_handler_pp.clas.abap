CLASS zcl_zrouter_handler_pp DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_prod_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS confirm_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS read_bom
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS read_routing
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_pp IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'PP' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_ORDER'.
        rs_result = create_prod_order( iv_payload ).
      WHEN 'CONFIRM_ORDER'.
        rs_result = confirm_order( iv_payload ).
      WHEN 'READ_BOM'.
        rs_result = read_bom( iv_payload ).
      WHEN 'READ_ROUTING'.
        rs_result = read_routing( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown PP action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_prod_order.
    DATA: ls_orderdata TYPE bapi_pp_order_create,
          ls_ret       TYPE bapiret2,
          lv_order_num TYPE bapi_order_key-order_number.

    " Parse JSON payload into BAPI structure
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_orderdata ).

    CALL FUNCTION 'BAPI_PRODORD_CREATE'
      EXPORTING
        orderdata    = ls_orderdata
      IMPORTING
        return       = ls_ret
        order_number = lv_order_num.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Prod order creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Prod order created' iv_data = lv_order_num ).
    ENDIF.
  ENDMETHOD.

  METHOD confirm_order.
    DATA: lt_timetickets TYPE TABLE OF bapi_pp_timeticket,
          lt_ret         TYPE TABLE OF bapiret2.
    APPEND INITIAL LINE TO lt_timetickets ASSIGNING FIELD-SYMBOL(<ls_ticket>).
    <ls_ticket>-order = iv_payload.
    CALL FUNCTION 'BAPI_PRODORDCONF_CREATE_TT'
      TABLES
        timetickets   = lt_timetickets
        detail_return = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type = 'E'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Confirmation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Order confirmed' ).
    ENDIF.
  ENDMETHOD.

  METHOD read_bom.
    DATA: lt_stpov TYPE TABLE OF stpo_vb,
          lt_ret   TYPE TABLE OF bapiret2.
    CALL FUNCTION 'CS_BOM_EXPL_MAT_V2'
      EXPORTING
        matnr = iv_payload
      TABLES
        stb   = lt_stpov.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'BOM read' iv_data = |{ lines( lt_stpov ) } components| ).
  ENDMETHOD.

  METHOD read_routing.
    rs_result = build_result( iv_status = 'INFO' iv_message = 'Routing read requires material + plant from payload' ).
  ENDMETHOD.
ENDCLASS.