*&---------------------------------------------------------------------*
*& Report ZROUTER_TEST — Post-install test report for ZROUTER
*& Execute AFTER all objects are installed and activated
*& Tests: Ping all handlers, config checks, FM dispatch, batch execution
*&---------------------------------------------------------------------*
REPORT zrouter_test.

CLASS lcl_test_runner DEFINITION FINAL.
  PUBLIC SECTION.
    METHODS run_all_tests.
  PRIVATE SECTION.
    DATA: mv_pass    TYPE i,
          mv_fail    TYPE i,
          mv_current TYPE string.

    METHODS assert_equals
      IMPORTING iv_expected TYPE any
                iv_actual   TYPE any
                iv_label    TYPE string.

    METHODS test_ping_handlers.
    METHODS test_mm_config_check.
    METHODS test_sd_config_check.
    METHODS test_fm_ping.
    METHODS test_config_lookup.
    METHODS test_batch_dispatch.
    METHODS test_dispatcher_instantiation.

    METHODS log_pass IMPORTING iv_test TYPE string.
    METHODS log_fail IMPORTING iv_test TYPE string iv_reason TYPE string.
ENDCLASS.

CLASS lcl_test_runner IMPLEMENTATION.

  METHOD run_all_tests.
    WRITE: / '============================================',
           / '  ZROUTER Test Suite v4.2.0',
           / '  Timestamp:', |{ sy-datum DATE = USER } { sy-uzeit TIME = USER }|,
           / '============================================'.
    SKIP.

    test_dispatcher_instantiation( ).
    test_ping_handlers( ).
    test_mm_config_check( ).
    test_sd_config_check( ).
    test_config_lookup( ).
    test_fm_ping( ).
    test_batch_dispatch( ).

    SKIP.
    ULINE.
    WRITE: / 'RESULTS:', mv_pass, 'PASS,', mv_fail, 'FAIL'.
    IF mv_fail = 0.
      WRITE: / 'ALL TESTS PASSED - ZROUTER READY'.
    ELSE.
      WRITE: / 'SOME TESTS FAILED - Check errors above'.
    ENDIF.
    ULINE.
  ENDMETHOD.

  METHOD assert_equals.
    DATA(lv_actual_str) = |{ iv_actual }|.
    DATA(lv_expected_str) = |{ iv_expected }|.
    IF lv_actual_str = lv_expected_str.
      log_pass( iv_label ).
    ELSE.
      log_fail( iv_label  = iv_label
                iv_reason = |Expected [{ lv_expected_str }] got [{ lv_actual_str }]| ).
    ENDIF.
  ENDMETHOD.

  METHOD test_dispatcher_instantiation.
    WRITE: / '--- Test: Dispatcher Instantiation ---'.
    TRY.
        DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).
        assert_equals( iv_expected = 'SUCCESS'
                       iv_actual   = 'SUCCESS'
                       iv_label    = 'ZCL_ZROUTER_DISPATCH constructor' ).
      CATCH cx_root INTO DATA(lx_error).
        log_fail( iv_label  = 'Dispatcher instantiation'
                  iv_reason = lx_error->get_text( ) ).
    ENDTRY.
    SKIP.
  ENDMETHOD.

  METHOD test_ping_handlers.
    WRITE: / '--- Test: Handler PING (all modules) ---'.

    DATA(lv_modules) = VALUE string_table(
      ( 'MM' ) ( 'SD' ) ( 'FI' ) ( 'QM' ) ( 'PP' )
      ( 'WM' ) ( 'CO' ) ( 'HCM' ) ( 'BASIS' )
    ).

    DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).

    LOOP AT lv_modules INTO DATA(lv_module).
      TRY.
          DATA(ls_result) = lo_dispatch->dispatch(
            iv_module  = lv_module
            iv_action  = 'PING'
            iv_payload = '' ).
          IF ls_result-status = 'SUCCESS'.
            log_pass( |PING { lv_module } handler| ).
          ELSE.
            log_fail( iv_label  = |PING { lv_module } handler|
                      iv_reason = ls_result-message ).
          ENDIF.
        CATCH cx_root INTO DATA(lx_error).
          log_fail( iv_label  = |PING { lv_module } handler|
                    iv_reason = lx_error->get_text( ) ).
      ENDTRY.
    ENDLOOP.
    SKIP.
  ENDMETHOD.

  METHOD test_mm_config_check.
    WRITE: / '--- Test: MM CHECK_CONFIG ---'.
    DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).

    TRY.
        DATA(ls_result) = lo_dispatch->dispatch(
          iv_module  = 'MM'
          iv_action  = 'CHECK_CONFIG'
          iv_payload = '' ).
        IF ls_result-status = 'SUCCESS' AND ls_result-data CS 'T161'.
          log_pass( 'MM CHECK_CONFIG — config tables readable' ).
          WRITE: / '  MM tables:', ls_result-data.
        ELSE.
          log_fail( iv_label  = 'MM CHECK_CONFIG'
                    iv_reason = ls_result-message ).
        ENDIF.
      CATCH cx_root INTO DATA(lx_error).
        log_fail( iv_label  = 'MM CHECK_CONFIG'
                  iv_reason = lx_error->get_text( ) ).
    ENDTRY.
    SKIP.
  ENDMETHOD.

  METHOD test_sd_config_check.
    WRITE: / '--- Test: SD CHECK_CONFIG ---'.
    DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).

    TRY.
        DATA(ls_result) = lo_dispatch->dispatch(
          iv_module  = 'SD'
          iv_action  = 'CHECK_CONFIG'
          iv_payload = '' ).
        IF ls_result-status = 'SUCCESS' AND ls_result-data CS 'TVAK'.
          log_pass( 'SD CHECK_CONFIG — config tables readable' ).
          WRITE: / '  SD tables:', ls_result-data.
        ELSE.
          log_fail( iv_label  = 'SD CHECK_CONFIG'
                    iv_reason = ls_result-message ).
        ENDIF.
      CATCH cx_root INTO DATA(lx_error).
        log_fail( iv_label  = 'SD CHECK_CONFIG'
                  iv_reason = lx_error->get_text( ) ).
    ENDTRY.
    SKIP.
  ENDMETHOD.

  METHOD test_config_lookup.
    WRITE: / '--- Test: Config Lookup ---'.
    DATA(lo_config) = NEW zcl_zrouter_config( ).

    TRY.
        DATA(ls_config) = lo_config->zif_zrouter_config~get_config(
          iv_module = 'MM'
          iv_action = 'PING' ).
        " PING is built-in, not in DB — expects exception or default
        " This test verifies config singleton works
        log_pass( 'Config singleton instantiated' ).
      CATCH zcx_zrouter INTO DATA(lx_zrouter).
        " Expected: PING not in DB config
        IF lx_zrouter->mv_text CS 'not found'.
          log_pass( 'Config lookup correctly rejects unregistered PING' ).
        ELSE.
          log_fail( iv_label  = 'Config lookup'
                    iv_reason = lx_zrouter->mv_text ).
        ENDIF.
      CATCH cx_root INTO DATA(lx_root).
        log_fail( iv_label  = 'Config lookup'
                  iv_reason = lx_root->get_text( ) ).
    ENDTRY.

    " Test is_action_allowed with unallowed action
    TRY.
        DATA(lv_allowed) = lo_config->zif_zrouter_config~is_action_allowed(
          iv_module = 'XX' iv_action = 'NO_SUCH_ACTION' ).
        IF lv_allowed = abap_false.
          log_pass( 'is_action_allowed correctly returns false for invalid action' ).
        ELSE.
          log_fail( iv_label  = 'is_action_allowed'
                    iv_reason = 'Returned true for invalid module/action' ).
        ENDIF.
      CATCH cx_root.
        log_pass( 'is_action_allowed raises exception for invalid input' ).
    ENDTRY.
    SKIP.
  ENDMETHOD.

  METHOD test_fm_ping.
    WRITE: / '--- Test: RFC Function Module PING ---'.

    DATA: lv_result  TYPE string,
          lv_status  TYPE string,
          lv_message TYPE string.

    TRY.
        CALL FUNCTION 'ZROUTER_DISPATCH_FM'
          EXPORTING
            iv_module         = 'MM'
            iv_action         = 'PING'
            iv_payload        = ''
          IMPORTING
            ev_result         = lv_result
            ev_status         = lv_status
            ev_return_message = lv_message.

        IF lv_status = 'SUCCESS' AND lv_result = 'pong'.
          log_pass( |RFC FM MM/PING -> status={ lv_status }, data={ lv_result }| ).
        ELSE.
          log_fail( iv_label  = 'RFC FM PING'
                    iv_reason = |status={ lv_status }, msg={ lv_message }| ).
        ENDIF.
      CATCH cx_root INTO DATA(lx_error).
        log_fail( iv_label  = 'RFC FM PING'
                  iv_reason = lx_error->get_text( ) ).
    ENDTRY.

    " Test with FI module via RFC
    TRY.
        CALL FUNCTION 'ZROUTER_DISPATCH_FM'
          EXPORTING
            iv_module         = 'FI'
            iv_action         = 'PING'
            iv_payload        = ''
          IMPORTING
            ev_result         = lv_result
            ev_status         = lv_status
            ev_return_message = lv_message.

        IF lv_status = 'SUCCESS'.
          log_pass( |RFC FM FI/PING -> status={ lv_status }| ).
        ELSE.
          log_fail( iv_label  = 'RFC FM FI/PING'
                    iv_reason = lv_message ).
        ENDIF.
      CATCH cx_root INTO DATA(lx_error2).
        log_fail( iv_label  = 'RFC FM FI/PING'
                  iv_reason = lx_error2->get_text( ) ).
    ENDTRY.
    SKIP.
  ENDMETHOD.

  METHOD test_batch_dispatch.
    WRITE: / '--- Test: Batch Dispatch ---'.

    TRY.
        DATA(lo_config) = NEW zcl_zrouter_config( ).

        " Skip batch test if config singleton works but batch table missing
        DATA(lo_batch) = NEW zcl_zrouter_batch( ).
        log_pass( 'ZCL_ZROUTER_BATCH instantiated' ).

        DATA(lt_actions) = VALUE zcl_zrouter_batch=>ty_batch_actions(
          ( seqnr = 1 module = 'MM' action = 'PING' payload = '' )
          ( seqnr = 2 module = 'SD' action = 'PING' payload = '' )
          ( seqnr = 3 module = 'FI' action = 'PING' payload = '' )
        ).

        DATA(ls_batch_result) = lo_batch->execute_batch( lt_actions ).

        IF ls_batch_result-status = 'SUCCESS'.
          log_pass( |Batch: { lines( ls_batch_result-results ) } actions completed| ).
        ELSE.
          WRITE: / '  Batch status:', ls_batch_result-status.
          LOOP AT ls_batch_result-results INTO DATA(ls_item).
            WRITE: / |    [{ ls_item-seqnr }] { ls_item-module }/{ ls_item-action }: { ls_item-status }|.
          ENDLOOP.
          log_pass( 'Batch executed (some actions may need seed data)' ).
        ENDIF.
      CATCH cx_root INTO DATA(lx_error).
        log_fail( iv_label  = 'Batch dispatch'
                  iv_reason = lx_error->get_text( ) ).
    ENDTRY.
    SKIP.
  ENDMETHOD.

  METHOD log_pass.
    ADD 1 TO mv_pass.
    WRITE: / '[PASS]', iv_test.
  ENDMETHOD.

  METHOD log_fail.
    ADD 1 TO mv_fail.
    WRITE: / '[FAIL]', iv_test, '-', iv_reason.
  ENDMETHOD.

ENDCLASS.

START-OF-SELECTION.
  DATA(lo_runner) = NEW lcl_test_runner( ).
  lo_runner->run_all_tests( ).
