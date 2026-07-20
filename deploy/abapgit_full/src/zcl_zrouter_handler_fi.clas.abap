CLASS zcl_zrouter_handler_fi DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS post_document
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS get_balance
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.


CLASS zcl_zrouter_handler_fi IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'FI' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'POST_DOCUMENT'.
        rs_result = post_document( iv_payload ).
      WHEN 'GET_BALANCE'.
        rs_result = get_balance( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown FI action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD post_document.
    DATA: ls_doc_header TYPE bapiache09,
          lt_gl         TYPE TABLE OF bapiacgl09,
          lt_ap         TYPE TABLE OF bapiacap09,
          lt_ar         TYPE TABLE OF bapiacar09,
          lt_ret        TYPE TABLE OF bapiret2,
          lv_obj_type   TYPE bapiache09-obj_type,
          lv_obj_key    TYPE bapiache09-obj_key.

    " Parse JSON payload into BAPI structures
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_doc_header ).

    CALL FUNCTION 'BAPI_ACC_DOCUMENT_POST'
      EXPORTING
        documentheader = ls_doc_header
      IMPORTING
        obj_type       = lv_obj_type
        obj_key        = lv_obj_key
      TABLES
        accountgl      = lt_gl
        accountpayable = lt_ap
        accountreceivable = lt_ar
        return         = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Accounting doc posting failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Document posted' iv_data = lv_obj_key ).
    ENDIF.
  ENDMETHOD.

  METHOD get_balance.
    DATA: lt_balance TYPE TABLE OF bapiaccr09,
          lt_ret     TYPE TABLE OF bapiret2.
    CALL FUNCTION 'BAPI_GL_GETACCOUNTSALDO'
      EXPORTING
        account = iv_payload
      TABLES
        balance = lt_balance
        return  = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type = 'E'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Balance retrieval failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Balance retrieved' iv_data = |Account { iv_payload }| ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.