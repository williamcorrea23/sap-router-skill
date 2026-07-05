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
        cx_zrouter.

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
        cx_zrouter.
ENDCLASS.