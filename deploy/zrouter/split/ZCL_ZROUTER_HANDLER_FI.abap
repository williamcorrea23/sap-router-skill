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