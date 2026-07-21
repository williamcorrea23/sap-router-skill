CLASS zcl_zrouter_handler_abstract DEFINITION PUBLIC ABSTRACT CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES zif_zrouter_handler.
    ALIASES handle_action FOR zif_zrouter_handler~handle_action.
  PROTECTED SECTION.
    DATA mo_logger TYPE REF TO zif_zrouter_logger.
    DATA mo_config TYPE REF TO zif_zrouter_config.
    DATA mv_module TYPE string.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config
        iv_module TYPE string.
    METHODS build_result
      IMPORTING
        iv_status        TYPE string
        iv_message       TYPE string
        iv_data          TYPE string OPTIONAL
      RETURNING
        VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS before_action.
    METHODS after_action.
    METHODS handle_custom_action
      IMPORTING
        iv_action        TYPE string
        iv_payload       TYPE string
      RETURNING
        VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result
      RAISING
        zcx_zrouter.

    " SECURITY: the former runtime evaluator over request-derived text was
    " removed. Dynamic execution of caller input is a
    " code-injection risk a blocklist cannot close. Config-driven transforms must
    " use explicit ABAP mapping, never runtime code generation.
ENDCLASS.


CLASS zcl_zrouter_handler_abstract IMPLEMENTATION.
  METHOD constructor.
    mo_logger = io_logger.
    mo_config = io_config.
    mv_module = iv_module.
  ENDMETHOD.

  METHOD build_result.
    rs_result-status = iv_status.
    rs_result-message = iv_message.
    rs_result-data = iv_data.
    rs_result-module = mv_module.
    rs_result-timestamp = utclong_current( ).
  ENDMETHOD.

  METHOD before_action.
  ENDMETHOD.

  METHOD after_action.
  ENDMETHOD.

  METHOD handle_custom_action.
    RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown action { iv_action } for { mv_module }|.
  ENDMETHOD.

  METHOD zif_zrouter_handler~handle_action.
    DATA(lv_action_upper) = to_upper( iv_action ).
    before_action( ).
    IF lv_action_upper = 'PING'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = |{ mv_module } handler alive| iv_data = 'pong' ).
    ELSE.
      rs_result = handle_custom_action( iv_action = iv_action iv_payload = iv_payload ).
    ENDIF.
    after_action( ).
    mo_logger->log_action(
      iv_module  = mv_module
      iv_action  = lv_action_upper
      iv_status  = rs_result-status
      iv_message = rs_result-message ).
  ENDMETHOD.
ENDCLASS.
