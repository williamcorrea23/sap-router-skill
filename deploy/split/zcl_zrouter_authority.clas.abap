

CLASS zcl_zrouter_authority DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_auth_result,
        authorized TYPE abap_bool,
        message    TYPE string,
      END OF ty_auth_result.
    METHODS check_authority
      IMPORTING
        iv_module        TYPE string
        iv_action        TYPE string
      RETURNING
        VALUE(rs_result) TYPE ty_auth_result.
ENDCLASS.