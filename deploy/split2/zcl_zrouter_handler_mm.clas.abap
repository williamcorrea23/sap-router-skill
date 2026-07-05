CLASS zcl_zrouter_handler_mm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_material
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS change_material
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS get_material
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_po
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS change_po
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS check_config
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_mm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'MM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_MATERIAL'.
        rs_result = create_material( iv_payload ).
      WHEN 'CHANGE_MATERIAL'.
        rs_result = change_material( iv_payload ).
      WHEN 'GET_MATERIAL'.
        rs_result = get_material( iv_payload ).
      WHEN 'CREATE_PO'.
        rs_result = create_po( iv_payload ).
      WHEN 'CHANGE_PO'.
        rs_result = change_po( iv_payload ).
      WHEN 'CHECK_CONFIG'.
        rs_result = check_config( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown MM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_material.
    DATA: ls_header  TYPE bapimathead,
          lt_desc    TYPE TABLE OF bapi_makt,
          ls_ret     TYPE bapiret2,
          lt_ret     TYPE TABLE OF bapiret2,
          lv_material TYPE matnr.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CLEAR lt_ret.
    CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
      EXPORTING headdata = ls_header
      IMPORTING return   = ls_ret material = lv_material
      TABLES   returnmessages = lt_ret materialdescription = lt_desc.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] )
                             OR line_exists( lt_ret[ type = 'A' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      DATA(lv_msg) = ls_ret-message.
      READ TABLE lt_ret INTO DATA(ls_table_ret) WITH KEY type = 'E'.
      IF sy-subrc = 0. lv_msg = ls_table_ret-message. ENDIF.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Material creation failed: { lv_msg }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Material created' iv_data = lv_material ).
    ENDIF.
  ENDMETHOD.

  METHOD change_material.
    DATA: ls_header TYPE bapimathead,
          ls_ret    TYPE bapiret2,
          lt_ret    TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
      EXPORTING headdata = ls_header
      IMPORTING return   = ls_ret
      TABLES   returnmessages = lt_ret.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Material change failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Material changed' ).
    ENDIF.
  ENDMETHOD.

  METHOD get_material.
    DATA: ls_material TYPE bapi_material_getall_data, ls_ret TYPE bapiret2.
    CALL FUNCTION 'BAPI_MATERIAL_GETALL'
      EXPORTING material = iv_payload
      IMPORTING data = ls_material return = ls_ret.
    IF ls_ret-type = 'E' OR ls_ret-type = 'A'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Material retrieval failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Material retrieved' iv_data = |{ ls_material-material } - { ls_material-matl_desc }| ).
    ENDIF.
  ENDMETHOD.

  METHOD create_po.
    DATA: ls_header TYPE bapimeoutheader,
          lt_items  TYPE TABLE OF bapimeoutitem,
          lt_ret    TYPE TABLE OF bapiret2,
          lv_po     TYPE ebeln.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CALL FUNCTION 'BAPI_PO_CREATE1'
      EXPORTING poheader   = ls_header
      IMPORTING exppurchaseorder = lv_po
      TABLES   return      = lt_ret poitem = lt_items.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |PO creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Purchase order created' iv_data = lv_po ).
    ENDIF.
  ENDMETHOD.

  METHOD change_po.
    DATA: ls_header TYPE bapimeoutheader,
          lt_ret    TYPE TABLE OF bapiret2,
          lv_po     TYPE ebeln.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CALL FUNCTION 'BAPI_PO_CHANGE'
      EXPORTING purchaseorder = lv_po poheader = ls_header
      TABLES   return = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |PO change failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Purchase order changed' iv_data = lv_po ).
    ENDIF.
  ENDMETHOD.

  METHOD check_config.
    DATA: lt_t161  TYPE TABLE OF t161,
          lt_t024  TYPE TABLE OF t024,
          lt_t001w TYPE TABLE OF t001w,
          lv_tables TYPE string.
    SELECT * FROM t161 INTO TABLE @lt_t161 UP TO 10 ROWS.
    SELECT * FROM t024 INTO TABLE @lt_t024 UP TO 10 ROWS.
    SELECT * FROM t001w INTO TABLE @lt_t001w UP TO 10 ROWS.
    lv_tables = |T161:{ lines( lt_t161 ) }, T024:{ lines( lt_t024 ) }, T001W:{ lines( lt_t001w ) }|.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'MM config tables checked' iv_data = lv_tables ).
  ENDMETHOD.
ENDCLASS.