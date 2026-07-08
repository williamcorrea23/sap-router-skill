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
    " Safe dynamic expression evaluator — ALLOWLIST based
    " Only permits: math operations (+ - * / **), comparisons (= < > <= >= <>),
    " string operations (&&, CONCATENATE, STRLEN), bool ops (AND OR NOT),
    " and assignment to cv_result.
    " All other statements are rejected.

    DATA: lt_source TYPE TABLE OF string,
          lv_pool   TYPE string,
          lt_lines  TYPE TABLE OF string.

    SPLIT iv_expression AT cl_abap_char_utilities=>newline INTO TABLE lt_lines.

    " Step 1: Allowlist check
    LOOP AT lt_lines ASSIGNING FIELD-SYMBOL(<lv_line_raw>).
      DATA(lv_upper) = to_upper( <lv_line_raw> ).

      " Block dangerous patterns
      IF lv_upper CS 'CALL ' OR lv_upper CS 'EXEC ' OR lv_upper CS 'SELECT '
      OR lv_upper CS 'INSERT ' OR lv_upper CS 'UPDATE ' OR lv_upper CS 'DELETE '
      OR lv_upper CS 'MODIFY ' OR lv_upper CS 'COMMIT ' OR lv_upper CS 'ROLLBACK '
      OR lv_upper CS 'GENERATE ' OR lv_upper CS 'SUBMIT ' OR lv_upper CS 'LEAVE '
      OR lv_upper CS 'CREATE ' OR lv_upper CS 'ASSIGN ' OR lv_upper CS 'OPEN '
      OR lv_upper CS 'CLOSE ' OR lv_upper CS 'READ ' OR lv_upper CS 'LOOP '
      OR lv_upper CS 'DO ' OR lv_upper CS 'WHILE ' OR lv_upper CS 'BREAK'
      OR lv_upper CS 'SYSTEM-' OR lv_upper CS 'EDITOR-'
      OR lv_upper CS 'FIELD-SYMBOL' OR lv_upper CS 'IMPORT '
      OR lv_upper CS 'EXPORT ' OR lv_upper CS 'GET ' OR lv_upper CS 'SET '
      OR lv_upper CS 'TRANSACTION' OR lv_upper CS 'PROGRAM'
      OR lv_upper CS 'CLASS ' OR lv_upper CS 'INTERFACE '
      OR lv_upper CS 'METHOD ' OR lv_upper CS 'FUNCTION '.
        RAISE EXCEPTION TYPE zcx_zrouter
          EXPORTING mv_text = |Forbidden statement: "{ <lv_line_raw> }"|.
      ENDIF.
    ENDLOOP.

    " Step 2: Build subroutine pool
    APPEND |PROGRAM.| TO lt_source.
    APPEND |FORM eval CHANGING cv_result TYPE string.| TO lt_source.
    APPEND LINES OF lt_lines TO lt_source.
    APPEND |ENDFORM.| TO lt_source.

    " Step 3: Generate and execute
    GENERATE SUBROUTINE POOL lt_source
      NAME lv_pool
      MESSAGE DATA(lv_msg) LINE DATA(lv_line_num) WORD DATA(lv_word).

    IF sy-subrc <> 0 OR lv_pool IS INITIAL.
      RAISE EXCEPTION TYPE zcx_zrouter
        EXPORTING mv_text = |Expression syntax error line { lv_line_num - 2 }: { lv_msg }{ COND #( WHEN lv_word IS NOT INITIAL THEN | near "{ lv_word }"| ) }|.
    ENDIF.

    PERFORM ('EVAL') IN PROGRAM (lv_pool) IF FOUND
      CHANGING cv_result.

    FREE lt_source.
  ENDMETHOD.
ENDCLASS.