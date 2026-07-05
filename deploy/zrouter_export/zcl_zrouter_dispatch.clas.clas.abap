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
      RAISING   zcx_zrouter.
    METHODS validate_and_check
      IMPORTING
        iv_module  TYPE string
        iv_action  TYPE string
      RAISING
        zcx_zrouter.
ENDCLASS.


CLASS zcl_zrouter_dispatch IMPLEMENTATION.
  METHOD constructor.
    mo_config = NEW zcl_zrouter_config( ).
    mo_logger = NEW zcl_zrouter_logger( ).
    mo_auth   = NEW zcl_zrouter_authority( ).
  ENDMETHOD.

  METHOD validate_and_check.
    IF mo_config->is_action_allowed( iv_module = iv_module iv_action = iv_action ) = abap_bool.
      " Ação permitida na configuração
    ELSE.
      RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Action { iv_action } for { iv_module } not allowed|.
    ENDIF.

    DATA(ls_auth) = mo_auth->check_authority( iv_module = iv_module iv_action = iv_action ).
    IF ls_auth-authorized = abap_false.
      RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = ls_auth-message.
    ENDIF.
  ENDMETHOD.

  METHOD get_handler_for_module.
    CASE to_upper( iv_module ).
      WHEN 'MM'.
        ro_handler = NEW zcl_zrouter_handler_mm( io_logger = mo_logger io_config = mo_config ).
      WHEN 'SD'.
        ro_handler = NEW zcl_zrouter_handler_sd( io_logger = mo_logger io_config = mo_config ).
      WHEN 'FI'.
        ro_handler = NEW zcl_zrouter_handler_fi( io_logger = mo_logger io_config = mo_config ).
      WHEN 'QM'.
        ro_handler = NEW zcl_zrouter_handler_qm( io_logger = mo_logger io_config = mo_config ).
      WHEN 'PP'.
        ro_handler = NEW zcl_zrouter_handler_pp( io_logger = mo_logger io_config = mo_config ).
      WHEN 'WM'.
        ro_handler = NEW zcl_zrouter_handler_wm( io_logger = mo_logger io_config = mo_config ).
      WHEN 'CO'.
        ro_handler = NEW zcl_zrouter_handler_co( io_logger = mo_logger io_config = mo_config ).
      WHEN 'HCM'.
        ro_handler = NEW zcl_zrouter_handler_hcm( io_logger = mo_logger io_config = mo_config ).
      WHEN 'BASIS'.
        ro_handler = NEW zcl_zrouter_handler_basis( io_logger = mo_logger io_config = mo_config ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown module: { iv_module }|.
    ENDCASE.
  ENDMETHOD.

  METHOD dispatch.
    TRY.
        validate_and_check( iv_module = iv_module iv_action = iv_action ).
        DATA(lo_handler) = get_handler_for_module( iv_module ).
        DATA(ls_handler_result) = lo_handler->handle_action( iv_action = iv_action iv_payload = iv_payload ).
        rs_result-module  = ls_handler_result-module.
        rs_result-action  = ls_handler_result-action.
        rs_result-status  = ls_handler_result-status.
        rs_result-message = ls_handler_result-message.
        rs_result-data    = ls_handler_result-data.
      CATCH zcx_zrouter INTO DATA(lx_zrouter).
        rs_result-status  = 'ERROR'.
        rs_result-message = lx_zrouter->mv_text.
        mo_logger->log_action(
          iv_module  = iv_module
          iv_action  = iv_action
          iv_status  = 'ERROR'
          iv_message = lx_zrouter->mv_text
          iv_payload = iv_payload ).
    ENDTRY.
  ENDMETHOD.
ENDCLASS.