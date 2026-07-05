

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