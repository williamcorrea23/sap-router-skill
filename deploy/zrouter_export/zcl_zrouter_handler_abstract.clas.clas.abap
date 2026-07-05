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

    " evaluate_expression — GENERATE SUBROUTINE POOL dynamic eval
    " Wraps iv_expression in FORM/ENDFORM, compiles as subroutine pool,
    " PERFORMs it passing optional CHANGING parameter.
    " Use for dynamic field mapping / config-driven transformations.
    METHODS evaluate_expression
      IMPORTING
        iv_expression   TYPE string
      CHANGING
        cv_result       TYPE string
      RAISING
        zcx_zrouter.
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

  METHOD evaluate_expression.
    " Wrap expression in a FORM that sets cv_result
    DATA: lt_source TYPE TABLE OF string,
          lv_pool   TYPE string.

    APPEND |PROGRAM.| TO lt_source.
    APPEND |FORM eval CHANGING cv_result TYPE string.| TO lt_source.
    SPLIT iv_expression AT cl_abap_char_utilities=>newline INTO TABLE DATA(lt_lines).

    " Security blocklist — prevent dangerous ABAP in dynamic expressions
    DATA(lt_dangerous) = VALUE string_table(
      ( |DELETE | )   ( |INSERT | )   ( |MODIFY | )        ( |UPDATE | )
      ( |CALL TRANSACTION| )  ( |SUBMIT | )
      ( |COMMIT WORK| )       ( |ROLLBACK WORK| )
      ( |OPEN DATASET| )      ( |DELETE DATASET| )
      ( |GENERATE SUBROUTINE| )( |INSERT REPORT| )
      ( |SYSTEM-CALL| )       ( |BREAK-POINT| )
      ( |EDITOR-CALL| )
    ).
    LOOP AT lt_lines INTO DATA(lv_line).
      LOOP AT lt_dangerous INTO DATA(lv_dangerous).
        IF to_upper( lv_line ) CS lv_dangerous.
          RAISE EXCEPTION TYPE zcx_zrouter
            EXPORTING mv_text = |Forbidden statement in expression: "{ lv_dangerous }"|.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    APPEND LINES OF lt_lines TO lt_source.
    APPEND |ENDFORM.| TO lt_source.

    GENERATE SUBROUTINE POOL lt_source
      NAME lv_pool
      MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).

    IF sy-subrc <> 0 OR lv_pool IS INITIAL.
      RAISE EXCEPTION TYPE zcx_zrouter
        EXPORTING mv_text = |Expression syntax error line { lv_line - 2 }: { lv_msg }{ COND #( WHEN lv_word IS NOT INITIAL THEN | near "{ lv_word }"| ) }|.
    ENDIF.

    " Define a FORM name inside pool — always 'eval'
    PERFORM ('EVAL') IN PROGRAM (lv_pool) IF FOUND
      CHANGING cv_result.

    " Pool released when internal session ends — no explicit cleanup needed
    FREE lt_source.
  ENDMETHOD.
ENDCLASS.