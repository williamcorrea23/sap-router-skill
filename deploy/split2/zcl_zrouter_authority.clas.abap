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


CLASS zcl_zrouter_authority IMPLEMENTATION.
  METHOD check_authority.
    DATA(lv_activity) = |ZROUTER_{ iv_module }_{ iv_action }|.
    TRY.
        cl_abap_authorization=>check_authorization(
          EXPORTING
            iv_object = 'ZROUTER'
            iv_field  = 'ACTIVITY'
            iv_value  = lv_activity ).
        rs_result-authorized = abap_true.
        rs_result-message    = 'Authorized'.
      CATCH cx_abap_not_authorized.
        rs_result-authorized = abap_false.
        rs_result-message    = |Not authorized for { iv_module }/{ iv_action }|.
    ENDTRY.
  ENDMETHOD.
ENDCLASS.