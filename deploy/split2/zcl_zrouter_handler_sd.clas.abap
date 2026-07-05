CLASS zcl_zrouter_handler_sd DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS change_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_delivery
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_invoice
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS check_config
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_sd IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'SD' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_ORDER'.
        rs_result = create_order( iv_payload ).
      WHEN 'CHANGE_ORDER'.
        rs_result = change_order( iv_payload ).
      WHEN 'CREATE_DELIVERY'.
        rs_result = create_delivery( iv_payload ).
      WHEN 'CREATE_INVOICE'.
        rs_result = create_invoice( iv_payload ).
      WHEN 'CHECK_CONFIG'.
        rs_result = check_config( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown SD action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_order.
    DATA: ls_header_in  TYPE bapisdhd1, ls_header_inx TYPE bapisdhd1x,
          lt_items      TYPE TABLE OF bapisditm, lt_partners TYPE TABLE OF bapiparnr,
          lv_sales_doc  TYPE vbeln_va, ls_ret TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header_in ).
    CLEAR lt_ret.
    CALL FUNCTION 'BAPI_SALESORDER_CREATEFROMDAT2'
      EXPORTING order_header_in = ls_header_in order_header_inx = ls_header_inx
      IMPORTING salesdocument = lv_sales_doc return = ls_ret
      TABLES   return = lt_ret order_items_in = lt_items order_partners = lt_partners.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] )
                             OR line_exists( lt_ret[ type = 'A' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Sales order creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Sales order created' iv_data = lv_sales_doc ).
    ENDIF.
  ENDMETHOD.

  METHOD change_order.
    DATA: ls_header_in TYPE bapisdhd1, ls_header_inx TYPE bapisdhd1x,
          ls_ret       TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header_in ).
    CALL FUNCTION 'BAPI_SALESORDER_CHANGE'
      EXPORTING salesdocument = ls_header_in-salesdocument
                order_header_in = ls_header_in order_header_inx = ls_header_inx
      TABLES   return = lt_ret.
    READ TABLE lt_ret INTO ls_ret INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Sales order change failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Sales order changed' ).
    ENDIF.
  ENDMETHOD.

  METHOD create_delivery.
    DATA: lt_items     TYPE TABLE OF bapidlvitem,
          lv_delivery  TYPE vbeln_vl, ls_ret TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = lt_items ).
    CALL FUNCTION 'BAPI_OUTB_DELIVERY_CREATE_SLS'
      IMPORTING delivery = lv_delivery return = ls_ret
      TABLES   return   = lt_ret items = lt_items.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Delivery creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Delivery created' iv_data = lv_delivery ).
    ENDIF.
  ENDMETHOD.

  METHOD create_invoice.
    DATA: lt_billing  TYPE TABLE OF bapivbrk, ls_ret TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = lt_billing ).
    CALL FUNCTION 'BAPI_BILLINGDOC_CREATEMULTIPLE'
      EXPORTING testrun = abap_false
      TABLES   billingdatain = lt_billing return = lt_ret.
    READ TABLE lt_ret INTO ls_ret INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Billing doc creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Billing document created' ).
    ENDIF.
  ENDMETHOD.

  METHOD check_config.
    DATA: lt_tvak  TYPE TABLE OF tvak, lt_tvko  TYPE TABLE OF tvko,
          lt_tvfk  TYPE TABLE OF tvfk, lv_tables TYPE string.
    SELECT * FROM tvak INTO TABLE @lt_tvak UP TO 10 ROWS.
    SELECT * FROM tvko INTO TABLE @lt_tvko UP TO 10 ROWS.
    SELECT * FROM tvfk INTO TABLE @lt_tvfk UP TO 10 ROWS.
    lv_tables = |TVAK:{ lines( lt_tvak ) }, TVKO:{ lines( lt_tvko ) }, TVFK:{ lines( lt_tvfk ) }|.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'SD config tables checked' iv_data = lv_tables ).
  ENDMETHOD.
ENDCLASS.