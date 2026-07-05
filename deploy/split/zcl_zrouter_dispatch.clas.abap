
CLASS zcl_zrouter_dispatch DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_dispatch_result,
        module  TYPE string,
        action  TYPE string,
        status  TYPE string,
        message TYPE string,
        data    TYPE string,
      END OF ty_dispatch_result.

    METHODS dispatch
      IMPORTING
        iv_module        TYPE string
        iv_action        TYPE string
        iv_payload       TYPE string
      RETURNING
        VALUE(rs_result) TYPE ty_dispatch_result.

    METHODS constructor.

  PRIVATE SECTION.
    DATA mo_config TYPE REF TO zif_zrouter_config.
    DATA mo_logger TYPE REF TO zif_zrouter_logger.
    DATA mo_auth   TYPE REF TO zcl_zrouter_authority.
    METHODS get_handler_for_module
      IMPORTING iv_module         TYPE string
      RETURNING VALUE(ro_handler) TYPE REF TO zif_zrouter_handler
      RAISING   cx_zrouter.
    METHODS validate_and_check
      IMPORTING
        iv_module  TYPE string
        iv_action  TYPE string
      RAISING
        cx_zrouter.
ENDCLASS.