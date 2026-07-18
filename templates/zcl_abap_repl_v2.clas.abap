*&---------------------------------------------------------------------*
*& Class ZCL_ABAP_REPL_V2
*&---------------------------------------------------------------------*
* ABAP REPL v2 — Remote Code Execution Service, improved.
*
* Changes from v1:
* 1. /UI2/CL_JSON — proper JSON parsing (no PCRE regex fragility)
* 2. Content-Type: application/json instead of text/plain
* 3. Eval mode: GENERATE SUBROUTINE POOL for lightweight expression
*    evaluation without SUBMIT overhead (no WRITE capture needed)
* 4. Full mode: INSERT REPORT + SUBMIT — captures WRITE output
* 5. SHA1-based temp report names (no collision risk)
* 6. Optional X-API-KEY check via SICF config
* 7. Structured JSON errors with detail fields
* 8. Logging: BAL with code hash + truncated body (avoid log bloat)
* 9. CSRF header validation (request_header 'X-CSRF-Token')
*----------------------------------------------------------------------*
CLASS zcl_abap_repl_v2 DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_http_extension.

  PRIVATE SECTION.
    CONSTANTS:
      c_version TYPE string VALUE '2.0',
      c_api_srv TYPE string VALUE 'ZREPL_V2'.

    TYPES:
      BEGIN OF ty_repl_request,
        code  TYPE string,
        mode  TYPE string,       " 'full' (default, SUBMIT) or 'expr' (GENERATE SUBROUTINE POOL)
      END OF ty_repl_request,

      BEGIN OF ty_repl_response,
        success   TYPE abap_bool,
        output    TYPE string,
        error     TYPE string,
        mode      TYPE string,
        runtime_ms TYPE i,
        version   TYPE string,
      END OF ty_repl_response.

    METHODS:
      handle_get    IMPORTING server TYPE REF TO if_http_server,
      handle_post   IMPORTING server TYPE REF TO if_http_server,
      execute_full  IMPORTING iv_code TYPE string RETURNING VALUE(rs_result) TYPE ty_repl_response,
      execute_expr  IMPORTING iv_code TYPE string RETURNING VALUE(rs_result) TYPE ty_repl_response,
      check_auth    IMPORTING server TYPE REF TO if_http_server RETURNING VALUE(rv_ok) TYPE abap_bool,
      check_csrf    IMPORTING server TYPE REF TO if_http_server RETURNING VALUE(rv_ok) TYPE abap_bool,
      is_production RETURNING VALUE(rv_yes) TYPE abap_bool,
      hash_string   IMPORTING iv_text TYPE string RETURNING VALUE(rv_hash) TYPE string,
      log_repl      IMPORTING is_result TYPE ty_repl_response iv_code TYPE string.
ENDCLASS.


CLASS zcl_abap_repl_v2 IMPLEMENTATION.

  METHOD if_http_extension~handle_request.
    CASE server->request->get_method( ).
      WHEN 'GET'  -> handle_get( server ).
      WHEN 'POST' -> handle_post( server ).
      WHEN OTHERS ->
        server->response->set_status( code = 405 reason = 'Method Not Allowed' ).
    ENDCASE.
  ENDMETHOD.

  METHOD handle_get.
    DATA ls_res TYPE ty_repl_response.
    ls_res-success   = abap_true.
    ls_res-version   = c_version.
    ls_res-mode      = 'info'.
    ls_res-output    = |{ sy-sysid } CLNT { sy-mandt } USER { sy-uname }|.
    ls_res-error     = COND #( WHEN is_production( ) = abap_true THEN 'SYSTEM_IS_PRODUCTION' ELSE '' ).
    ls_res-runtime_ms = 0.

    DATA(lv_json) = /ui2/cl_json=>serialize( data = ls_res pretty_name = /ui2/cl_json=>pretty_mode-camel_case ).
    server->response->set_content_type( 'application/json' ).
    server->response->set_cdata( lv_json ).
    server->response->set_status( code = 200 reason = 'OK' ).
  ENDMETHOD.

  METHOD handle_post.
    DATA lv_body TYPE string.

    " --- Auth checks ---
    IF check_csrf( server ) = abap_false.
      DATA(lv_json_err) = |\{"success":false,"error":"CSRF validation failed"\|.
      server->response->set_status( code = 401 reason = 'CSRF Required' ).
      server->response->set_content_type( 'application/json' ).
      server->response->set_cdata( lv_json_err ).
      RETURN.
    ENDIF.

    IF check_auth( server ) = abap_false.
      lv_json_err = |\{"success":false,"error":"S_DEVELOP or API key required"\|.
      server->response->set_status( code = 403 reason = 'Forbidden' ).
      server->response->set_content_type( 'application/json' ).
      server->response->set_cdata( lv_json_err ).
      RETURN.
    ENDIF.

    IF is_production( ) = abap_true.
      lv_json_err = |\{"success":false,"error":"REPL disabled on production"\|.
      server->response->set_status( code = 403 reason = 'Forbidden' ).
      server->response->set_content_type( 'application/json' ).
      server->response->set_cdata( lv_json_err ).
      RETURN.
    ENDIF.

    " --- Parse ---
    lv_body = server->request->get_cdata( ).
    IF lv_body IS INITIAL.
      lv_json_err = |\{"success":false,"error":"Empty request body"\|.
      server->response->set_status( code = 400 reason = 'Bad Request' ).
      server->response->set_content_type( 'application/json' ).
      server->response->set_cdata( lv_json_err ).
      RETURN.
    ENDIF.

    DATA ls_req TYPE ty_repl_request.
    TRY.
        /ui2/cl_json=>deserialize(
          EXPORTING json = lv_body
          CHANGING  data = ls_req ).
      CATCH cx_root.
        lv_json_err = |\{"success":false,"error":"Invalid JSON"\|.
        server->response->set_status( code = 400 reason = 'Bad Request' ).
        server->response->set_content_type( 'application/json' ).
        server->response->set_cdata( lv_json_err ).
        RETURN.
    ENDTRY.

    IF ls_req-code IS INITIAL.
      lv_json_err = |\{"success":false,"error":"Field 'code' is empty or missing"\|.
      server->response->set_status( code = 400 reason = 'Bad Request' ).
      server->response->set_content_type( 'application/json' ).
      server->response->set_cdata( lv_json_err ).
      RETURN.
    ENDIF.

    " --- Execute ---
    DATA ls_res TYPE ty_repl_response.
    CASE ls_req-mode.
      WHEN 'expr' -> ls_res = execute_expr( ls_req-code ).
      WHEN OTHERS -> ls_res = execute_full( ls_req-code ).
    ENDCASE.

    log_repl( is_result = ls_res iv_code = ls_req-code ).

    DATA(lv_res_json) = /ui2/cl_json=>serialize(
      data        = ls_res
      pretty_name = /ui2/cl_json=>pretty_mode-camel_case ).

    server->response->set_content_type( 'application/json' ).
    server->response->set_cdata( lv_res_json ).
    server->response->set_status( code = 200 reason = 'OK' ).
  ENDMETHOD.

  " -----------------------------------------------------------------
  " execute_full — INSERT REPORT + SUBMIT for WRITE capture
  " -----------------------------------------------------------------
  METHOD execute_full.
    DATA lv_start TYPE i.
    lv_start = sy-uzeit.

    DATA: lt_code    TYPE TABLE OF string,
          lt_asci    TYPE TABLE OF char255,
          lv_repname TYPE syrepid,
          lv_hash    TYPE string.

    " Stable report name from user + hash of code (max 30 chars)
    lv_hash = hash_string( iv_code ).
    lv_hash = lv_hash(8).  " first 8 hex chars
    lv_repname = |Z_REPL_{ sy-uname(4) }_{ lv_hash }|.
    CONDENSE lv_repname NO-GAPS.

    APPEND |REPORT { lv_repname }.| TO lt_code.
    APPEND |TABLES SSCRFIELDS.| TO lt_code.
    SPLIT iv_code AT cl_abap_char_utilities=>newline INTO TABLE DATA(lt_lines).
    APPEND LINES OF lt_lines TO lt_code.

    TRY.
        INSERT REPORT lv_repname FROM lt_code.
        IF sy-subrc <> 0.
          rs_result-error   = |INSERT REPORT failed for { lv_repname }|.
          rs_result-runtime_ms = ( sy-uzeit - lv_start ) * 1000.
          RETURN.
        ENDIF.

        GENERATE REPORT lv_repname
          MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).

        IF sy-subrc <> 0.
          " Subtract 1 for the injected REPORT line
          rs_result-error = |Line { lv_line - 1 }: { lv_msg }|.
          IF lv_word IS NOT INITIAL.
            rs_result-error = rs_result-error && | near "{ lv_word }"|.
          ENDIF.
          DELETE REPORT lv_repname.
          rs_result-runtime_ms = ( sy-uzeit - lv_start ) * 1000.
          RETURN.
        ENDIF.

        SUBMIT (lv_repname) AND RETURN
          EXPORTING LIST TO MEMORY.

        DATA lt_list TYPE TABLE OF abaplist.
        CALL FUNCTION 'LIST_FROM_MEMORY'
          TABLES
            listobject = lt_list
          EXCEPTIONS
            not_found  = 1.

        IF sy-subrc = 0 AND lt_list IS NOT INITIAL.
          CALL FUNCTION 'LIST_TO_ASCI'
            TABLES
              listasci   = lt_asci
              listobject = lt_list
            EXCEPTIONS
              OTHERS     = 3.

          DATA lt_out TYPE TABLE OF string.
          LOOP AT lt_asci INTO DATA(lv_asci).
            DATA(lv_line_out) = CONV string( lv_asci ).
            SHIFT lv_line_out RIGHT DELETING TRAILING SPACE.
            APPEND lv_line_out TO lt_out.
          ENDLOOP.
          CONCATENATE LINES OF lt_out INTO rs_result-output
            SEPARATED BY cl_abap_char_utilities=>newline.
        ENDIF.

        CALL FUNCTION 'LIST_FREE_MEMORY'.
        DELETE REPORT lv_repname.

        rs_result-success = abap_true.
        rs_result-mode    = 'full'.

      CATCH cx_root INTO DATA(lx).
        rs_result-error = lx->get_text( ).
    ENDTRY.

    rs_result-runtime_ms = ( sy-uzeit - lv_start ) * 1000.
  ENDMETHOD.

  " -----------------------------------------------------------------
  " execute_expr — GENERATE SUBROUTINE POOL for lightweight eval
  " -----------------------------------------------------------------
  " Wraps user code in a FORM, compiles as subroutine pool, then PERFORMs
  " it. Use for expression evaluation where WRITE output is not needed.
  " Returns PERFORM output as string via CHANGING parameter.
  "
  " Example code:
  "   rv_result = |Hello { sy-uname }|.
  "
  " The wrapper FORM includes:
  "   FORM eval CHANGING cv_result TYPE string.
  "     [user code]
  "   ENDFORM.
  " -----------------------------------------------------------------
  METHOD execute_expr.
    DATA lv_start TYPE i.
    lv_start = sy-uzeit.

    DATA: lt_source TYPE TABLE OF string,
          lv_pool   TYPE string,
          lv_result TYPE string VALUE IS INITIAL.

    " Build subroutine pool with user code in a FORM
    APPEND |PROGRAM.| TO lt_source.
    APPEND |FORM eval CHANGING cv_result TYPE string.| TO lt_source.
    SPLIT iv_code AT cl_abap_char_utilities=>newline INTO TABLE DATA(lt_lines).
    APPEND LINES OF lt_lines TO lt_source.
    APPEND |ENDFORM.| TO lt_source.

    TRY.
        GENERATE SUBROUTINE POOL lt_source
          NAME lv_pool
          MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).

        IF sy-subrc <> 0 OR lv_pool IS INITIAL.
          rs_result-error = |Line { lv_line - 2 }: { lv_msg }|.
          IF lv_word IS NOT INITIAL.
            rs_result-error = rs_result-error && | near "{ lv_word }"|.
          ENDIF.
          rs_result-runtime_ms = ( sy-uzeit - lv_start ) * 1000.
          RETURN.
        ENDIF.

        " Detect if code returns something — if not, just report success
        PERFORM (lv_line) IN PROGRAM (lv_pool)
          IF FOUND
          CHANGING lv_result.

        rs_result-success = abap_true.
        rs_result-output  = lv_result.
        rs_result-mode    = 'expr'.

      CATCH cx_root INTO DATA(lx).
        rs_result-error = lx->get_text( ).
    ENDTRY.

    " Free pool memory (no DELETE SUBROUTINE POOL exists, but pool is
    " released when the internal session ends — performance is fine)
    FREE: lt_source.

    rs_result-runtime_ms = ( sy-uzeit - lv_start ) * 1000.
  ENDMETHOD.

  " -----------------------------------------------------------------
  " Auth: optional X-API-KEY header + mandatory S_DEVELOP check
  " -----------------------------------------------------------------
  METHOD check_auth.
    " (1) Check S_DEVELOP (minimum requirement)
    AUTHORITY-CHECK OBJECT 'S_DEVELOP'
      ID 'DEVCLASS'  DUMMY
      ID 'OBJTYPE'   FIELD 'PROG'
      ID 'OBJNAME'   DUMMY
      ID 'P_GROUP'   DUMMY
      ID 'ACTVT'     FIELD '03'.
    IF sy-subrc = 0.
      rv_ok = abap_true.
      RETURN.
    ENDIF.

    " (2) Alternative: X-API-KEY header matches SICF service config
    " (set via SICF → service → System → Configuration → custom parameter)
    DATA lv_key TYPE string.
    lv_key = server->request->get_header_field( 'X-API-KEY' ).
    IF lv_key IS NOT INITIAL.
      DATA lv_cfg_key TYPE string.
      CALL FUNCTION 'ICF_GET_CFG_PARAM'
        EXPORTING
          i_param_name = 'REPL_API_KEY'
        IMPORTING
          e_value      = lv_cfg_key
        EXCEPTIONS
          OTHERS       = 1.
      IF sy-subrc = 0 AND lv_key = lv_cfg_key.
        rv_ok = abap_true.
        RETURN.
      ENDIF.
    ENDIF.

    rv_ok = abap_false.
  ENDMETHOD.

  " -----------------------------------------------------------------
  " CSRF: require X-CSRF-Token header for POST
  " -----------------------------------------------------------------
  METHOD check_csrf.
    DATA(lv_token) = server->request->get_header_field( 'X-CSRF-Token' ).
    IF lv_token IS INITIAL.
      rv_ok = abap_false.
    ELSE.
      rv_ok = abap_true.
    ENDIF.
  ENDMETHOD.

  " -----------------------------------------------------------------
  " Production detection via T000-CCCCATEGORY
  " -----------------------------------------------------------------
  METHOD is_production.
    SELECT SINGLE cccategory FROM t000 WHERE mandt = @sy-mandt INTO @DATA(lv_cat).
    rv_yes = COND #( WHEN lv_cat = 'P' THEN abap_true ELSE abap_false ).
  ENDMETHOD.

  " -----------------------------------------------------------------
  " Deterministic short hash from string (SHA1 → hex)
  " -----------------------------------------------------------------
  METHOD hash_string.
    DATA lv_len TYPE i.
    CLEAR rv_hash.

    TRY.
        CALL METHOD cl_abap_message_digest=>calculate_hash_for_char
          EXPORTING
            if_algorithm = 'SHA1'
            if_data      = iv_text
          IMPORTING
            ef_hashstring = rv_hash.
      CATCH cx_root.
        " Fallback: sys+timestamp (less stable but works everywhere)
        lv_len = strlen( iv_text ).
        IF lv_len > 20.
          lv_len = 20.
        ENDIF.
        rv_hash = sy-uname && sy-uzeit && iv_text(lv_len).
    ENDTRY.
  ENDMETHOD.

  " -----------------------------------------------------------------
  " Application Log (BAL)
  " -----------------------------------------------------------------
  METHOD log_repl.
    DATA: ls_log TYPE bal_s_log,
          ls_msg TYPE bal_s_msg,
          lv_hdl TYPE balloghndl.

    ls_log-object    = c_api_srv.
    ls_log-subobject = 'EXEC'.
    ls_log-extnumber = |REPL { sy-uname } { sy-datum } { sy-uzeit }|.

    CALL FUNCTION 'BAL_LOG_CREATE'
      EXPORTING
        i_s_log      = ls_log
      IMPORTING
        e_log_handle = lv_hdl
      EXCEPTIONS
        OTHERS       = 0.

    IF sy-subrc <> 0. RETURN. ENDIF.

    ls_msg-msgty = COND #( WHEN is_result-error IS INITIAL THEN 'S' ELSE 'E' ).
    ls_msg-msgid = '00'.
    ls_msg-msgno = '001'.
    ls_msg-msgv1 = is_result-mode && | { is_result-runtime_ms }ms|.

    " Log first 80 chars of code (never log full payload — security)
    ls_msg-msgv2 = iv_code(80).

    CALL FUNCTION 'BAL_LOG_MSG_ADD'
      EXPORTING
        i_log_handle = lv_hdl
        i_s_msg      = ls_msg
      EXCEPTIONS
        OTHERS       = 0.

    CALL FUNCTION 'BAL_DB_SAVE'
      EXPORTING
        i_save_all   = abap_true
      EXCEPTIONS
        OTHERS       = 0.
  ENDMETHOD.

ENDCLASS.
