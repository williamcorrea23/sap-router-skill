" ZCL_ZROUTER_HTTP - REST/HTTP Gateway for ZROUTER v5
" Implements IF_HTTP_EXTENSION, registered via SICF at /sap/zrouter
" Endpoints: POST /dispatch, GET /actions, GET /health, POST /batch
" Version 5.0.0 - Auto-deployed via ADT
CLASS zcl_zrouter_http DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_http_extension.

  PRIVATE SECTION.
    TYPES:
      BEGIN OF ty_dispatch_request,
        module  TYPE string,
        action  TYPE string,
        payload TYPE string,
      END OF ty_dispatch_request,
      BEGIN OF ty_batch_request,
        actions TYPE STANDARD TABLE OF ty_dispatch_request WITH NON-UNIQUE DEFAULT KEY,
      END OF ty_batch_request,
      BEGIN OF ty_dispatch_response,
        status    TYPE string,
        message   TYPE string,
        data      TYPE string,
        module    TYPE string,
        action    TYPE string,
        timestamp TYPE string,
      END OF ty_dispatch_response,
      BEGIN OF ty_batch_response,
        status   TYPE string,
        message  TYPE string,
        results  TYPE STANDARD TABLE OF ty_dispatch_response WITH NON-UNIQUE DEFAULT KEY,
        total    TYPE i,
        success  TYPE i,
        failures TYPE i,
      END OF ty_batch_response,
      BEGIN OF ty_action_info,
        module    TYPE string,
        action    TYPE string,
        active    TYPE string,
        batchable TYPE string,
        timeout   TYPE i,
      END OF ty_action_info,
      BEGIN OF ty_action_info_tab,
        actions TYPE STANDARD TABLE OF ty_action_info WITH NON-UNIQUE DEFAULT KEY,
      END OF ty_action_info_tab,
      BEGIN OF ty_health_response,
        status    TYPE string,
        version   TYPE string,
        timestamp TYPE string,
        system_id TYPE string,
        client    TYPE string,
        actions   TYPE i,
      END OF ty_health_response.

    CONSTANTS:
      co_version        TYPE string VALUE '5.0.0',
      co_content_json   TYPE string VALUE 'application/json; charset=utf-8',
      co_max_batch_size TYPE i VALUE 100.

    METHODS handle_post
      IMPORTING io_server TYPE REF TO if_http_server.

    METHODS handle_get
      IMPORTING io_server TYPE REF TO if_http_server.

    METHODS handle_options
      IMPORTING io_server TYPE REF TO if_http_server.

    METHODS dispatch_action
      IMPORTING iv_module     TYPE string
                iv_action     TYPE string
                iv_payload    TYPE string
      RETURNING VALUE(rs_res) TYPE ty_dispatch_response.

    METHODS send_json_response
      IMPORTING io_server TYPE REF TO if_http_server
                iv_status  TYPE i
                iv_body    TYPE string.

    METHODS send_error
      IMPORTING io_server TYPE REF TO if_http_server
                iv_status  TYPE i
                iv_message TYPE string.

    METHODS parse_path
      IMPORTING iv_path        TYPE string
      RETURNING VALUE(rv_rest) TYPE string.

ENDCLASS.

CLASS zcl_zrouter_http IMPLEMENTATION.

  METHOD if_http_extension~handle_request.
    DATA: lv_method TYPE string,
          lo_server TYPE REF TO if_http_server.

    lo_server = server.
    lv_method = lo_server->request->get_method( ).

    " ICF authorization check
    AUTHORITY-CHECK OBJECT 'ZROUTER'
      ID 'ACTIVITY' FIELD 'HTTP_ACCESS'.
    IF sy-subrc <> 0.
      lo_server->response->set_status( code = 401 reason = 'Unauthorized' ).
      lo_server->response->set_cdata( data = '{"status":"ERROR","message":"Not authorized"}' ).
      RETURN.
    ENDIF.

    " Path validation — prevent traversal
    DATA(lv_path) = lo_server->request->get_header_field( '~request_uri' ).
    IF lv_path CS '..' OR lv_path CS '//'.
      send_error( io_server = lo_server iv_status = 400
                  iv_message = 'Invalid path.' ).
      RETURN.
    ENDIF.

    " CORS with origin reflection (safer than wildcard for non-browser clients)
    DATA(lv_origin) = lo_server->request->get_header_field( 'Origin' ).
    IF lv_origin IS NOT INITIAL.
      lo_server->response->set_header_field(
        name  = 'Access-Control-Allow-Origin'
        value = lv_origin ).
    ELSE.
      lo_server->response->set_header_field(
        name  = 'Access-Control-Allow-Origin'
        value = '*' ).
    ENDIF.
    lo_server->response->set_header_field(
      name  = 'Access-Control-Allow-Methods'
      value = 'GET, POST, OPTIONS' ).
    lo_server->response->set_header_field(
      name  = 'Access-Control-Allow-Headers'
      value = 'Content-Type, Authorization, Accept' ).

    CASE lv_method.
      WHEN 'POST'.
        handle_post( lo_server ).
      WHEN 'GET'.
        handle_get( lo_server ).
      WHEN 'OPTIONS'.
        handle_options( lo_server ).
      WHEN OTHERS.
        send_error(
          io_server  = lo_server
          iv_status  = 405
          iv_message = 'Method Not Allowed. Use GET, POST, or OPTIONS.' ).
    ENDCASE.
  ENDMETHOD.

  METHOD handle_post.
    DATA: lv_path  TYPE string,
          lv_body  TYPE string,
          ls_req   TYPE ty_dispatch_request,
          ls_batch TYPE ty_batch_request,
          ls_res   TYPE ty_dispatch_response,
          ls_batch_res TYPE ty_batch_response.

    lv_path = io_server->request->get_header_field( '~request_uri' ).
    lv_body = io_server->request->get_cdata( ).

    IF lv_body IS INITIAL.
      send_error( io_server = io_server iv_status = 400 iv_message = 'Empty request body.' ).
      RETURN.
    ENDIF.

    " Route by path
    IF lv_path CS '/batch'.
      " Batch dispatch with size limit
      /ui2/cl_json=>deserialize(
        EXPORTING json = lv_body
        CHANGING  data = ls_batch ).
      IF lines( ls_batch-actions ) > co_max_batch_size.
        send_error( io_server = io_server iv_status = 413
                    iv_message = |Batch too large. Max { co_max_batch_size } actions.| ).
        RETURN.
      ENDIF.
      ls_batch_res-status = 'SUCCESS'.
      ls_batch_res-total  = lines( ls_batch-actions ).
      ls_batch_res-success = 0.
      ls_batch_res-failures = 0.
      LOOP AT ls_batch-actions INTO ls_req.
        ls_res = dispatch_action(
          iv_module  = ls_req-module
          iv_action  = ls_req-action
          iv_payload = ls_req-payload ).
        APPEND ls_res TO ls_batch_res-results.
        IF ls_res-status = 'SUCCESS'.
          ls_batch_res-success = ls_batch_res-success + 1.
        ELSE.
          ls_batch_res-failures = ls_batch_res-failures + 1.
        ENDIF.
      ENDLOOP.
      ls_batch_res-message = |Batch: { ls_batch_res-success } OK, { ls_batch_res-failures } failed, { ls_batch_res-total } total|.
      send_json_response(
        io_server = io_server
        iv_status = 200
        iv_body   = /ui2/cl_json=>serialize(
          data        = ls_batch_res
          compress    = abap_true
          pretty_name = /ui2/cl_json=>pretty_mode-camel_case ) ).
    ELSE.
      " Single dispatch
      /ui2/cl_json=>deserialize(
        EXPORTING json = lv_body
        CHANGING  data = ls_req ).
      ls_res = dispatch_action(
        iv_module  = ls_req-module
        iv_action  = ls_req-action
        iv_payload = ls_req-payload ).
      send_json_response(
        io_server = io_server
        iv_status = 200
        iv_body   = /ui2/cl_json=>serialize(
          data        = ls_res
          compress    = abap_true
          pretty_name = /ui2/cl_json=>pretty_mode-camel_case ) ).
    ENDIF.
  ENDMETHOD.

  METHOD handle_get.
    DATA: lv_path        TYPE string,
          lv_module      TYPE string,
          lt_config      TYPE zif_zrouter_config=>ty_config_entries,
          ls_actions     TYPE ty_action_info_tab,
          ls_info        TYPE ty_action_info,
          ls_health      TYPE ty_health_response,
          lv_timestamp   TYPE timestampl,
          ls_date        TYPE string,
          ls_time        TYPE string,
          lv_action      TYPE string,
          lv_template_json TYPE string.

    lv_path = io_server->request->get_header_field( '~request_uri' ).

    " Healthcheck
    IF lv_path CS '/health'.
      GET TIME STAMP FIELD lv_timestamp.
      ls_date = |{ lv_timestamp+0(4) }-{ lv_timestamp+4(2) }-{ lv_timestamp+6(2) }|.
      ls_time = |{ lv_timestamp+8(2) }:{ lv_timestamp+10(2) }:{ lv_timestamp+12(2) }|.
      ls_health-status    = 'OK'.
      ls_health-version   = co_version.
      ls_health-timestamp = |{ ls_date }T{ ls_time }Z|.
      ls_health-system_id = COND #( WHEN sy-sysid IS NOT INITIAL THEN sy-sysid ELSE 'LOCAL' ).
      ls_health-client    = sy-mandt.
      TRY.
          DATA(lo_config) = NEW zcl_zrouter_config( ).
          lt_config = lo_config->zif_zrouter_config~get_all_config( ).
          ls_health-actions = lines( lt_config ).
        CATCH cx_root.
          ls_health-actions = 0.
      ENDTRY.
      send_json_response(
        io_server = io_server
        iv_status = 200
        iv_body   = /ui2/cl_json=>serialize(
          data        = ls_health
          compress    = abap_true
          pretty_name = /ui2/cl_json=>pretty_mode-camel_case ) ).
      RETURN.
    ENDIF.

    " Templates: /templates/{module}/{action}
    IF lv_path CS '/templates/'.
      SPLIT lv_path AT '/' INTO TABLE DATA(lt_path_parts).
      IF lines( lt_path_parts ) >= 2.
        lv_module = lt_path_parts[ lines( lt_path_parts ) - 1 ].
        lv_action = lt_path_parts[ lines( lt_path_parts ) ].
        " Template lookup -- queries ZROUTER_TEMPLATE DB table
        SELECT SINGLE template_json FROM zrouter_template
          INTO lv_template_json
          WHERE module = lv_module
            AND action = lv_action.
        IF sy-subrc = 0.
          send_json_response(
            io_server = io_server
            iv_status = 200
            iv_body   = lv_template_json ).
        ELSE.
          send_error(
            io_server  = io_server
            iv_status  = 404
            iv_message = |Template not found: { lv_module }/{ lv_action }| ).
        ENDIF.
        RETURN.
      ENDIF.
    ENDIF.

    " Actions list: /actions or /actions/{module}
    TRY.
        DATA(lo_cfg) = NEW zcl_zrouter_config( ).
        lt_config = lo_cfg->zif_zrouter_config~get_all_config( ).
      CATCH cx_root INTO DATA(lx_cfg).
        send_error(
          io_server  = io_server
          iv_status  = 500
          iv_message = |Config error: { lx_cfg->get_text( ) }| ).
        RETURN.
    ENDTRY.

    " Filter by module if path contains /actions/xxx
    IF lv_path CS '/actions/' AND lv_path <> '/actions'.
      SPLIT lv_path AT '/' INTO TABLE DATA(lt_parts).
      lv_module = lt_parts[ lines( lt_parts ) ].
    ENDIF.

    LOOP AT lt_config INTO DATA(ls_cfg).
      IF lv_module IS NOT INITIAL AND ls_cfg-module <> lv_module.
        CONTINUE.
      ENDIF.
      ls_info-module    = ls_cfg-module.
      ls_info-action    = ls_cfg-action.
      ls_info-active    = COND #( WHEN ls_cfg-active = abap_true THEN 'true' ELSE 'false' ).
      ls_info-batchable = COND #( WHEN ls_cfg-batchable = abap_true THEN 'true' ELSE 'false' ).
      ls_info-timeout   = ls_cfg-timeout.
      APPEND ls_info TO ls_actions-actions.
    ENDLOOP.

    send_json_response(
      io_server = io_server
      iv_status = 200
      iv_body   = /ui2/cl_json=>serialize(
        data        = ls_actions
        compress    = abap_true
        pretty_name = /ui2/cl_json=>pretty_mode-camel_case ) ).
  ENDMETHOD.
  METHOD handle_options.
    io_server->response->set_status( code = 204 reason = 'No Content' ).
  ENDMETHOD.
  METHOD dispatch_action.
    DATA: lv_timestamp TYPE timestampl,
          ls_date      TYPE string,
          ls_time      TYPE string.

    TRY.
        DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).
        DATA(ls_dispatch_result) = lo_dispatch->dispatch(
          iv_module  = iv_module
          iv_action  = iv_action
          iv_payload = iv_payload ).
        rs_res-status  = ls_dispatch_result-status.
        rs_res-message = ls_dispatch_result-message.
        rs_res-data    = ls_dispatch_result-data.
        rs_res-module  = iv_module.
        rs_res-action  = iv_action.
      CATCH cx_root INTO DATA(lx).
        rs_res-status  = 'ERROR'.
        rs_res-message = lx->get_text( ).
        rs_res-data    = ''.
        rs_res-module  = iv_module.
        rs_res-action  = iv_action.
    ENDTRY.

    " ISO 8601 timestamp
    GET TIME STAMP FIELD lv_timestamp.
    ls_date = |{ lv_timestamp+0(4) }-{ lv_timestamp+4(2) }-{ lv_timestamp+6(2) }|.
    ls_time = |{ lv_timestamp+8(2) }:{ lv_timestamp+10(2) }:{ lv_timestamp+12(2) }|.
    rs_res-timestamp = |{ ls_date }T{ ls_time }Z|.
  ENDMETHOD.
  METHOD send_json_response.
    io_server->response->set_status( code = iv_status reason = COND #( WHEN iv_status = 200 THEN 'OK' ELSE '' ) ).
    io_server->response->set_content_type( co_content_json ).
    io_server->response->set_cdata( data = iv_body ).
  ENDMETHOD.

  METHOD send_error.
    DATA: BEGIN OF ls_error,
            status  TYPE string,
            message TYPE string,
          END OF ls_error.
    ls_error-status  = 'ERROR'.
    ls_error-message = iv_message.
    io_server->response->set_status( code = iv_status reason = '' ).
    io_server->response->set_content_type( co_content_json ).
    io_server->response->set_cdata( data = /ui2/cl_json=>serialize(
      data        = ls_error
      compress    = abap_true
      pretty_name = /ui2/cl_json=>pretty_mode-camel_case ) ).
  ENDMETHOD.

  METHOD parse_path.
    " Remove /sap/zrouter prefix, return rest
    rv_rest = iv_path.
    REPLACE ALL OCCURRENCES OF REGEX '^.*/sap/zrouter' IN rv_rest WITH ''.
  ENDMETHOD.

ENDCLASS.
