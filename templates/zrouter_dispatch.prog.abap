*&---------------------------------------------------------------------*
*& Function Group ZROUTER - Implementation Template (ABAP OO / Clean Core)
*&---------------------------------------------------------------------*

*&---------------------------------------------------------------------*
*& 1. Classe de Exceção - ZCX_ZROUTER
*&---------------------------------------------------------------------*
CLASS zcx_zrouter DEFINITION
  INHERITING FROM cx_static_check
  PUBLIC
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_t100_message.
    METHODS constructor
      IMPORTING
        textid   LIKE if_t100_message=>t100key OPTIONAL
        previous LIKE previous OPTIONAL
        mv_text  TYPE string OPTIONAL.
    DATA mv_text TYPE string READ-ONLY.
ENDCLASS.

CLASS zcx_zrouter IMPLEMENTATION.
  METHOD constructor.
    super->constructor( previous = previous ).
    if_t100_message~t100key = textid.
    me->mv_text = mv_text.
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
*& 2. Interfaces
*&---------------------------------------------------------------------*

INTERFACE zif_zrouter_handler PUBLIC.
  TYPES:
    BEGIN OF ty_action_result,
      status    TYPE string,
      message   TYPE string,
      data      TYPE string,
      module    TYPE string,
      action    TYPE string,
      timestamp TYPE timestampl,
    END OF ty_action_result.

  METHODS handle_action
    IMPORTING
      iv_action        TYPE string
      iv_payload       TYPE string
    RETURNING
      VALUE(rs_result) TYPE ty_action_result
    RAISING
      zcx_zrouter.
ENDINTERFACE.

INTERFACE zif_zrouter_config PUBLIC.
  TYPES:
    BEGIN OF ty_config_entry,
      module    TYPE string,
      action    TYPE string,
      active    TYPE abap_bool,
      batchable TYPE abap_bool,
      timeout   TYPE i,
    END OF ty_config_entry,
    ty_config_entries TYPE STANDARD TABLE OF ty_config_entry.

  METHODS get_config
    IMPORTING
      iv_module        TYPE string
      iv_action        TYPE string
    RETURNING
      VALUE(rs_config) TYPE ty_config_entry
    RAISING
      zcx_zrouter.

  METHODS is_action_allowed
    IMPORTING
      iv_module         TYPE string
      iv_action         TYPE string
    RETURNING
      VALUE(rv_allowed) TYPE abap_bool.

  METHODS get_all_config
    RETURNING
      VALUE(rt_config) TYPE ty_config_entries.
ENDINTERFACE.

INTERFACE zif_zrouter_logger PUBLIC.
  TYPES:
    BEGIN OF ty_log_entry,
      guid      TYPE sysuuid_c32,
      module    TYPE string,
      action    TYPE string,
      status    TYPE string,
      message   TYPE string,
      payload   TYPE string,
      result    TYPE string,
      username  TYPE syuname,
      timestamp TYPE timestampl,
    END OF ty_log_entry.

  METHODS log_action
    IMPORTING
      iv_module      TYPE string
      iv_action      TYPE string
      iv_status      TYPE string
      iv_message     TYPE string
      iv_payload     TYPE string OPTIONAL
      iv_result      TYPE string OPTIONAL
    RETURNING
      VALUE(rv_guid) TYPE sysuuid_c32
    RAISING
      zcx_zrouter.

  METHODS get_logs
    IMPORTING
      iv_module      TYPE string OPTIONAL
      iv_date        TYPE dats OPTIONAL
    RETURNING
      VALUE(rt_logs) TYPE STANDARD TABLE OF ty_log_entry.
ENDINTERFACE.

*&---------------------------------------------------------------------*
*& 3. Classes de Infraestrutura
*&---------------------------------------------------------------------*

*&---------------------------------------------------------------------*
*& 3a. DDIC Structures for BAPI Payload Deserialization
*&---------------------------------------------------------------------*
" These types are used by /ui2/cl_json=>deserialize to parse JSON payloads
" into typed BAPI parameters. Create as DDIC structures via SE11 or
" define inline in handler methods for ABAP Cloud compatibility.

TYPES:
  BEGIN OF zrouter_qm_insp_params,
    material     TYPE matnr,
    plant        TYPE werks_d,
    insp_type    TYPE qmart,
    lot_quantity TYPE qlos_menge,
  END OF zrouter_qm_insp_params,

  BEGIN OF zrouter_wm_gm_params,
    material   TYPE matnr,
    plant      TYPE werks_d,
    stor_loc   TYPE lgort_d,
    move_type  TYPE bwart,
    quantity   TYPE bpmng,
    gm_code    TYPE bapi2017_gm_code,
    pstng_date TYPE budat,
    doc_date   TYPE bldat,
  END OF zrouter_wm_gm_params,

  BEGIN OF zrouter_wm_to_params,
    warehouse        TYPE lgnum,
    move_type        TYPE bwlvs,
    material         TYPE matnr,
    plant            TYPE werks_d,
    source_stor_type TYPE lgtp_vl,
    source_stor_bin  TYPE lgpla_vl,
    dest_stor_type   TYPE lgtp_nl,
    dest_stor_bin    TYPE lgpla_nl,
    quantity         TYPE anfme,
    base_uom         TYPE altme,
  END OF zrouter_wm_to_params,

  BEGIN OF zrouter_co_alloc_params,
    controlling_area     TYPE kokrs,
    sender_cost_center   TYPE kostl,
    receiver_cost_center TYPE kostl,
    activity_type        TYPE lstar,
    quantity             TYPE lstxx,
    period               TYPE co_perio,
    fiscal_year          TYPE gjahr,
  END OF zrouter_co_alloc_params,

  BEGIN OF zrouter_hcm_infotype_params,
    employee_id TYPE pernr_d,
    infotype    TYPE infty,
    subtype     TYPE subty,
    begin_date  TYPE begda,
    end_date    TYPE endda,
    data_json   TYPE string,
  END OF zrouter_hcm_infotype_params,

  BEGIN OF zrouter_basis_tr_params,
    request_type  TYPE trfunction,
    owner_text    TYPE as4text,
    target_system TYPE tarsystem,
  END OF zrouter_basis_tr_params.

*&---------------------------------------------------------------------*
*& 3b. Classes de Infraestrutura
*&---------------------------------------------------------------------*

" Config — reads action config from DB table ZROUTER_CONFIG
CLASS zcl_zrouter_config DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES zif_zrouter_config.
  PRIVATE SECTION.
    DATA lt_config_cache TYPE zif_zrouter_config=>ty_config_entries.
    METHODS load_config.
    METHODS db_to_config_entry
      IMPORTING is_db     TYPE zrouter_config
      RETURNING VALUE(rs) TYPE zif_zrouter_config=>ty_config_entry.
ENDCLASS.

CLASS zcl_zrouter_config IMPLEMENTATION.
  METHOD load_config.
    IF lt_config_cache IS INITIAL.
      SELECT module, action, active, batchable, timeout
        FROM zrouter_config
        WHERE client = @sy-mandt
        INTO CORRESPONDING FIELDS OF TABLE @lt_config_cache.
    ENDIF.
  ENDMETHOD.

  METHOD db_to_config_entry.
    rs-module    = is_db-module.
    rs-action    = is_db-action.
    rs-active    = COND #( WHEN is_db-active = 'X' THEN abap_true ELSE abap_false ).
    rs-batchable = COND #( WHEN is_db-batchable = 'X' THEN abap_true ELSE abap_false ).
    rs-timeout   = is_db-timeout.
  ENDMETHOD.

  METHOD zif_zrouter_config~get_config.
    load_config( ).
    TRY.
        rs_config = lt_config_cache[ module = iv_module action = iv_action ].
      CATCH cx_sy_itab_line_not_found.
        RAISE EXCEPTION TYPE zcx_zrouter
          EXPORTING mv_text = |Config for { iv_module }/{ iv_action } not found|.
    ENDTRY.
  ENDMETHOD.

  METHOD zif_zrouter_config~is_action_allowed.
    TRY.
        DATA(ls_config) = zif_zrouter_config~get_config( iv_module = iv_module iv_action = iv_action ).
        rv_allowed = ls_config-active.
      CATCH zcx_zrouter.
        rv_allowed = abap_false.
    ENDTRY.
  ENDMETHOD.

  METHOD zif_zrouter_config~get_all_config.
    load_config( ).
    rt_config = lt_config_cache.
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_logger DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES zif_zrouter_logger.
  PRIVATE SECTION.
    METHODS generate_guid RETURNING VALUE(rv_guid) TYPE sysuuid_c32.
ENDCLASS.

CLASS zcl_zrouter_logger IMPLEMENTATION.
  METHOD generate_guid.
    TRY.
        rv_guid = cl_system_uuid=>create_uuid_c32_static( ).
      CATCH cx_uuid_error.
        " sy-index is 0 outside of loops — use random fallback
        rv_guid = |{ cl_abap_random_int=>create(
          seed = cl_abap_random=>seed( )
          min  = 1000000000
          max  = 9999999999 )->get_next( ) }|.
    ENDTRY.
  ENDMETHOD.

  METHOD zif_zrouter_logger~log_action.
    DATA: ls_log TYPE zrouter_log.
    rv_guid = generate_guid( ).
    ls_log-guid      = rv_guid.
    ls_log-module    = iv_module.
    ls_log-action    = iv_action.
    ls_log-status    = iv_status.
    ls_log-message   = iv_message.
    ls_log-payload   = iv_payload.
    ls_log-result    = iv_result.
    ls_log-username  = sy-uname.
    GET TIME STAMP FIELD ls_log-timestamp.
    INSERT zrouter_log FROM @ls_log.
    IF sy-subrc <> 0.
      RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = 'Failed to write log entry'.
    ELSE.
      COMMIT WORK AND WAIT.
    ENDIF.
  ENDMETHOD.

  METHOD zif_zrouter_logger~get_logs.
    DATA(lv_date_from) = iv_date.
    DATA(lv_date_to)   = iv_date + 1.
    SELECT guid, module, action, status, message, payload, result, username, timestamp
      FROM zrouter_log
      WHERE client = @sy-mandt
        AND ( module = @iv_module OR @iv_module IS INITIAL )
        AND ( timestamp >= @lv_date_from AND timestamp < @lv_date_to OR @iv_date IS INITIAL )
      ORDER BY timestamp DESCENDING
      INTO CORRESPONDING FIELDS OF TABLE @rt_logs.
  ENDMETHOD.
ENDCLASS.


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

*&---------------------------------------------------------------------*
*& 4. Classes de Handler (Base Abstrata e Implementações)
*&---------------------------------------------------------------------*

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
        zcx_zrouter.

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
        zcx_zrouter.
ENDCLASS.

CLASS zcl_zrouter_handler_abstract IMPLEMENTATION.
  METHOD constructor.
    mo_logger = io_logger.
    mo_config = io_config.
    mv_module = iv_module.
  ENDMETHOD.

  METHOD build_result.
    rs_result-status = iv_status.
    rs_result-message = iv_message.
    rs_result-data = iv_data.
    rs_result-module = mv_module.
    rs_result-timestamp = utclong_current( ).
  ENDMETHOD.

  METHOD before_action.
  ENDMETHOD.

  METHOD after_action.
  ENDMETHOD.

  METHOD handle_custom_action.
    RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown action { iv_action } for { mv_module }|.
  ENDMETHOD.

  METHOD zif_zrouter_handler~handle_action.
    DATA(lv_action_upper) = to_upper( iv_action ).
    before_action( ).
    IF lv_action_upper = 'PING'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = |{ mv_module } handler alive| iv_data = 'pong' ).
    ELSE.
      rs_result = handle_custom_action( iv_action = iv_action iv_payload = iv_payload ).
    ENDIF.
    after_action( ).
    mo_logger->log_action(
      iv_module  = mv_module
      iv_action  = lv_action_upper
      iv_status  = rs_result-status
      iv_message = rs_result-message ).
  ENDMETHOD.

  METHOD evaluate_expression.
    " Wrap expression in a FORM that sets cv_result
    DATA: lt_source TYPE TABLE OF string,
          lv_pool   TYPE string.

    APPEND |PROGRAM.| TO lt_source.
    APPEND |FORM eval CHANGING cv_result TYPE string.| TO lt_source.
    SPLIT iv_expression AT cl_abap_char_utilities=>newline INTO TABLE DATA(lt_lines).

    " Security blocklist — prevent dangerous ABAP in dynamic expressions
    DATA(lt_dangerous) = VALUE string_table(
      ( |DELETE | )   ( |INSERT | )   ( |MODIFY | )        ( |UPDATE | )
      ( |CALL TRANSACTION| )  ( |SUBMIT | )
      ( |COMMIT WORK| )       ( |ROLLBACK WORK| )
      ( |OPEN DATASET| )      ( |DELETE DATASET| )
      ( |GENERATE SUBROUTINE| )( |INSERT REPORT| )
      ( |SYSTEM-CALL| )       ( |BREAK-POINT| )
      ( |EDITOR-CALL| )
    ).
    LOOP AT lt_lines INTO DATA(lv_line).
      LOOP AT lt_dangerous INTO DATA(lv_dangerous).
        IF to_upper( lv_line ) CS lv_dangerous.
          RAISE EXCEPTION TYPE zcx_zrouter
            EXPORTING mv_text = |Forbidden statement in expression: "{ lv_dangerous }"|.
        ENDIF.
      ENDLOOP.
    ENDLOOP.

    APPEND LINES OF lt_lines TO lt_source.
    APPEND |ENDFORM.| TO lt_source.

    GENERATE SUBROUTINE POOL lt_source
      NAME lv_pool
      MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).

    IF sy-subrc <> 0 OR lv_pool IS INITIAL.
      RAISE EXCEPTION TYPE zcx_zrouter
        EXPORTING mv_text = |Expression syntax error line { lv_line - 2 }: { lv_msg }{ COND #( WHEN lv_word IS NOT INITIAL THEN | near "{ lv_word }"| ) }|.
    ENDIF.

    " Define a FORM name inside pool — always 'eval'
    PERFORM ('EVAL') IN PROGRAM (lv_pool) IF FOUND
      CHANGING cv_result.

    " Pool released when internal session ends — no explicit cleanup needed
    FREE lt_source.
  ENDMETHOD.
ENDCLASS.


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

CLASS zcl_zrouter_handler_mm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'MM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_MATERIAL'.
        rs_result = create_material( iv_payload ).
      WHEN 'CHANGE_MATERIAL'.
        rs_result = change_material( iv_payload ).
      WHEN 'GET_MATERIAL'.
        rs_result = get_material( iv_payload ).
      WHEN 'CREATE_PO'.
        rs_result = create_po( iv_payload ).
      WHEN 'CHANGE_PO'.
        rs_result = change_po( iv_payload ).
      WHEN 'CHECK_CONFIG'.
        rs_result = check_config( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown MM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_material.
    DATA: ls_header  TYPE bapimathead,
          lt_desc    TYPE TABLE OF bapi_makt,
          ls_ret     TYPE bapiret2,
          lt_ret     TYPE TABLE OF bapiret2,
          lv_material TYPE matnr.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CLEAR lt_ret.
    CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
      EXPORTING headdata = ls_header
      IMPORTING return   = ls_ret material = lv_material
      TABLES   returnmessages = lt_ret materialdescription = lt_desc.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] )
                             OR line_exists( lt_ret[ type = 'A' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      DATA(lv_msg) = ls_ret-message.
      READ TABLE lt_ret INTO DATA(ls_table_ret) WITH KEY type = 'E'.
      IF sy-subrc = 0. lv_msg = ls_table_ret-message. ENDIF.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Material creation failed: { lv_msg }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Material created' iv_data = lv_material ).
    ENDIF.
  ENDMETHOD.

  METHOD change_material.
    DATA: ls_header TYPE bapimathead,
          ls_ret    TYPE bapiret2,
          lt_ret    TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
      EXPORTING headdata = ls_header
      IMPORTING return   = ls_ret
      TABLES   returnmessages = lt_ret.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Material change failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Material changed' ).
    ENDIF.
  ENDMETHOD.

  METHOD get_material.
    DATA: ls_material TYPE bapi_material_getall_data, ls_ret TYPE bapiret2.
    CALL FUNCTION 'BAPI_MATERIAL_GETALL'
      EXPORTING material = iv_payload
      IMPORTING data = ls_material return = ls_ret.
    IF ls_ret-type = 'E' OR ls_ret-type = 'A'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Material retrieval failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Material retrieved' iv_data = |{ ls_material-material } - { ls_material-matl_desc }| ).
    ENDIF.
  ENDMETHOD.

  METHOD create_po.
    DATA: ls_header TYPE bapimeoutheader,
          lt_items  TYPE TABLE OF bapimeoutitem,
          lt_ret    TYPE TABLE OF bapiret2,
          lv_po     TYPE ebeln.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CALL FUNCTION 'BAPI_PO_CREATE1'
      EXPORTING poheader   = ls_header
      IMPORTING exppurchaseorder = lv_po
      TABLES   return      = lt_ret poitem = lt_items.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |PO creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Purchase order created' iv_data = lv_po ).
    ENDIF.
  ENDMETHOD.

  METHOD change_po.
    DATA: ls_header TYPE bapimeoutheader,
          lt_ret    TYPE TABLE OF bapiret2,
          lv_po     TYPE ebeln.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header ).
    CALL FUNCTION 'BAPI_PO_CHANGE'
      EXPORTING purchaseorder = lv_po poheader = ls_header
      TABLES   return = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |PO change failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Purchase order changed' iv_data = lv_po ).
    ENDIF.
  ENDMETHOD.

  METHOD check_config.
    DATA: lt_t161  TYPE TABLE OF t161,
          lt_t024  TYPE TABLE OF t024,
          lt_t001w TYPE TABLE OF t001w,
          lv_tables TYPE string.
    SELECT * FROM t161 INTO TABLE @lt_t161 UP TO 10 ROWS.
    SELECT * FROM t024 INTO TABLE @lt_t024 UP TO 10 ROWS.
    SELECT * FROM t001w INTO TABLE @lt_t001w UP TO 10 ROWS.
    lv_tables = |T161:{ lines( lt_t161 ) }, T024:{ lines( lt_t024 ) }, T001W:{ lines( lt_t001w ) }|.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'MM config tables checked' iv_data = lv_tables ).
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_sd DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS change_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_delivery
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_invoice
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS check_config
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_sd IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'SD' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_ORDER'.
        rs_result = create_order( iv_payload ).
      WHEN 'CHANGE_ORDER'.
        rs_result = change_order( iv_payload ).
      WHEN 'CREATE_DELIVERY'.
        rs_result = create_delivery( iv_payload ).
      WHEN 'CREATE_INVOICE'.
        rs_result = create_invoice( iv_payload ).
      WHEN 'CHECK_CONFIG'.
        rs_result = check_config( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown SD action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_order.
    DATA: ls_header_in  TYPE bapisdhd1, ls_header_inx TYPE bapisdhd1x,
          lt_items      TYPE TABLE OF bapisditm, lt_partners TYPE TABLE OF bapiparnr,
          lv_sales_doc  TYPE vbeln_va, ls_ret TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header_in ).
    CLEAR lt_ret.
    CALL FUNCTION 'BAPI_SALESORDER_CREATEFROMDAT2'
      EXPORTING order_header_in = ls_header_in order_header_inx = ls_header_inx
      IMPORTING salesdocument = lv_sales_doc return = ls_ret
      TABLES   return = lt_ret order_items_in = lt_items order_partners = lt_partners.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] )
                             OR line_exists( lt_ret[ type = 'A' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Sales order creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Sales order created' iv_data = lv_sales_doc ).
    ENDIF.
  ENDMETHOD.

  METHOD change_order.
    DATA: ls_header_in TYPE bapisdhd1, ls_header_inx TYPE bapisdhd1x,
          ls_ret       TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_header_in ).
    CALL FUNCTION 'BAPI_SALESORDER_CHANGE'
      EXPORTING salesdocument = ls_header_in-salesdocument
                order_header_in = ls_header_in order_header_inx = ls_header_inx
      TABLES   return = lt_ret.
    READ TABLE lt_ret INTO ls_ret INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Sales order change failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Sales order changed' ).
    ENDIF.
  ENDMETHOD.

  METHOD create_delivery.
    DATA: lt_items     TYPE TABLE OF bapidlvitem,
          lv_delivery  TYPE vbeln_vl, ls_ret TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = lt_items ).
    CALL FUNCTION 'BAPI_OUTB_DELIVERY_CREATE_SLS'
      IMPORTING delivery = lv_delivery return = ls_ret
      TABLES   return   = lt_ret items = lt_items.
    IF ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Delivery creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Delivery created' iv_data = lv_delivery ).
    ENDIF.
  ENDMETHOD.

  METHOD create_invoice.
    DATA: lt_billing  TYPE TABLE OF bapivbrk, ls_ret TYPE bapiret2, lt_ret TYPE TABLE OF bapiret2.
    /ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = lt_billing ).
    CALL FUNCTION 'BAPI_BILLINGDOC_CREATEMULTIPLE'
      EXPORTING testrun = abap_false
      TABLES   billingdatain = lt_billing return = lt_ret.
    READ TABLE lt_ret INTO ls_ret INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Billing doc creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Billing document created' ).
    ENDIF.
  ENDMETHOD.

  METHOD check_config.
    DATA: lt_tvak  TYPE TABLE OF tvak, lt_tvko  TYPE TABLE OF tvko,
          lt_tvfk  TYPE TABLE OF tvfk, lv_tables TYPE string.
    SELECT * FROM tvak INTO TABLE @lt_tvak UP TO 10 ROWS.
    SELECT * FROM tvko INTO TABLE @lt_tvko UP TO 10 ROWS.
    SELECT * FROM tvfk INTO TABLE @lt_tvfk UP TO 10 ROWS.
    lv_tables = |TVAK:{ lines( lt_tvak ) }, TVKO:{ lines( lt_tvko ) }, TVFK:{ lines( lt_tvfk ) }|.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'SD config tables checked' iv_data = lv_tables ).
  ENDMETHOD.
ENDCLASS.


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

CLASS zcl_zrouter_handler_fi IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'FI' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'POST_DOCUMENT'.
        rs_result = post_document( iv_payload ).
      WHEN 'GET_BALANCE'.
        rs_result = get_balance( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown FI action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD post_document.
    DATA: ls_doc_header TYPE bapiache09,
          lt_gl         TYPE TABLE OF bapiacgl09,
          lt_ap         TYPE TABLE OF bapiacap09,
          lt_ar         TYPE TABLE OF bapiacar09,
          lt_ret        TYPE TABLE OF bapiret2,
          lv_obj_type   TYPE bapiache09-obj_type,
          lv_obj_key    TYPE bapiache09-obj_key.

    " Parse JSON payload into BAPI structures
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_doc_header ).

    CALL FUNCTION 'BAPI_ACC_DOCUMENT_POST'
      EXPORTING
        documentheader = ls_doc_header
      IMPORTING
        obj_type       = lv_obj_type
        obj_key        = lv_obj_key
      TABLES
        accountgl      = lt_gl
        accountpayable = lt_ap
        accountreceivable = lt_ar
        return         = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Accounting doc posting failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Document posted' iv_data = lv_obj_key ).
    ENDIF.
  ENDMETHOD.

  METHOD get_balance.
    DATA: lt_balance TYPE TABLE OF bapiaccr09,
          lt_ret     TYPE TABLE OF bapiret2.
    CALL FUNCTION 'BAPI_GL_GETACCOUNTSALDO'
      EXPORTING
        account = iv_payload
      TABLES
        balance = lt_balance
        return  = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type = 'E'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Balance retrieval failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Balance retrieved' iv_data = |Account { iv_payload }| ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_qm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_inspection_lot
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS record_results
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_qm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'QM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_INSPECTION'.
        rs_result = create_inspection_lot( iv_payload ).
      WHEN 'RECORD_RESULTS'.
        rs_result = record_results( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown QM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_inspection_lot.
    DATA: ls_params   TYPE zrouter_qm_insp_params,
          lt_ret      TYPE TABLE OF bapiret2,
          lv_insp_lot TYPE qplos.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'CO_QM_INSPECTION_LOT_CREATE'
      EXPORTING
        i_material   = ls_params-material
        i_werk       = ls_params-plant
        i_insp_type  = ls_params-insp_type
        i_insp_qty   = ls_params-lot_quantity
      IMPORTING
        e_inspection = lv_insp_lot
      TABLES
        t_return     = lt_ret.
    IF sy-subrc <> 0 OR line_exists( lt_ret[ type = 'E' ] )
                       OR line_exists( lt_ret[ type = 'A' ] ).
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      READ TABLE lt_ret WITH KEY type = 'E' INTO DATA(ls_qm_ret).
      rs_result = build_result( iv_status = 'ERROR'
          iv_message = |Inspection lot creation failed: { ls_qm_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Inspection lot created' iv_data = |{ lv_insp_lot }| ).
    ENDIF.
  ENDMETHOD.

  METHOD record_results.
    DATA: ls_ret TYPE bapiret2.
    CALL FUNCTION 'BAPI_INSPOPER_RECORDRESULTS'
      EXPORTING
        insplot  = iv_payload
      IMPORTING
        return   = ls_ret.
    IF ls_ret-type = 'E'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Results recording failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Results recorded' ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_pp DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_prod_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS confirm_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS read_bom
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS read_routing
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_pp IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'PP' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_ORDER'.
        rs_result = create_prod_order( iv_payload ).
      WHEN 'CONFIRM_ORDER'.
        rs_result = confirm_order( iv_payload ).
      WHEN 'READ_BOM'.
        rs_result = read_bom( iv_payload ).
      WHEN 'READ_ROUTING'.
        rs_result = read_routing( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown PP action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_prod_order.
    DATA: ls_orderdata TYPE bapi_pp_order_create,
          ls_ret       TYPE bapiret2,
          lv_order_num TYPE bapi_order_key-order_number.

    " Parse JSON payload into BAPI structure
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_orderdata ).

    CALL FUNCTION 'BAPI_PRODORD_CREATE'
      EXPORTING
        orderdata    = ls_orderdata
      IMPORTING
        return       = ls_ret
        order_number = lv_order_num.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Prod order creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Prod order created' iv_data = lv_order_num ).
    ENDIF.
  ENDMETHOD.

  METHOD confirm_order.
    DATA: lt_timetickets TYPE TABLE OF bapi_pp_timeticket,
          lt_ret         TYPE TABLE OF bapiret2.
    APPEND INITIAL LINE TO lt_timetickets ASSIGNING FIELD-SYMBOL(<ls_ticket>).
    <ls_ticket>-order = iv_payload.
    CALL FUNCTION 'BAPI_PRODORDCONF_CREATE_TT'
      TABLES
        timetickets   = lt_timetickets
        detail_return = lt_ret.
    READ TABLE lt_ret INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type = 'E'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Confirmation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Order confirmed' ).
    ENDIF.
  ENDMETHOD.

  METHOD read_bom.
    DATA: lt_stpov TYPE TABLE OF stpo_vb,
          lt_ret   TYPE TABLE OF bapiret2.
    CALL FUNCTION 'CS_BOM_EXPL_MAT_V2'
      EXPORTING
        matnr = iv_payload
      TABLES
        stb   = lt_stpov.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'BOM read' iv_data = |{ lines( lt_stpov ) } components| ).
  ENDMETHOD.

  METHOD read_routing.
    rs_result = build_result( iv_status = 'INFO' iv_message = 'Routing read requires material + plant from payload' ).
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_wm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS goods_movement
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_to
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_wm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'WM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'GOODS_MOVEMENT'.
        rs_result = goods_movement( iv_payload ).
      WHEN 'CREATE_TO'.
        rs_result = create_to( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown WM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD goods_movement.
    DATA: ls_header TYPE bapi2017_gm_head_01,
          ls_params TYPE zrouter_wm_gm_params,
          lt_item   TYPE TABLE OF bapi2017_gm_item_create,
          lt_ret    TYPE TABLE OF bapiret2,
          ls_ret    TYPE bapiret2,
          lv_mdoc   TYPE bapi2017_gm_head_01-mat_doc.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).
    ls_header = CORRESPONDING #( ls_params ).
    IF ls_header-pstng_date IS INITIAL.
      ls_header-pstng_date = sy-datum.
      ls_header-doc_date   = sy-datum.
    ENDIF.

    APPEND INITIAL LINE TO lt_item ASSIGNING FIELD-SYMBOL(<ls_item>).
    IF <ls_item> IS ASSIGNED.
      <ls_item>-material = ls_params-material.
      <ls_item>-plant    = ls_params-plant.
      <ls_item>-stge_loc = ls_params-stor_loc.
      <ls_item>-move_type = ls_params-move_type.
      <ls_item>-entry_qnt = ls_params-quantity.
    ENDIF.

    CALL FUNCTION 'BAPI_GOODSMVT_CREATE'
      EXPORTING
        goodsmvt_header  = ls_header
        goodsmvt_code    = ls_params-gm_code
      IMPORTING
        materialdocument = lv_mdoc
      TABLES
        goodsmvt_item    = lt_item
        return           = lt_ret.
    READ TABLE lt_ret INTO ls_ret INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Goods movement failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Goods movement posted' iv_data = |{ lv_mdoc }| ).
    ENDIF.
  ENDMETHOD.

  METHOD create_to.
    DATA: ls_params TYPE zrouter_wm_to_params,
          lv_tanum  TYPE ltak-tanum.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'L_TO_CREATE_SINGLE'
      EXPORTING
        i_lgnum       = ls_params-warehouse
        i_bwlvs       = ls_params-move_type
        i_matnr       = ls_params-material
        i_werks       = ls_params-plant
        i_vltyp       = ls_params-source_stor_type
        i_vlpla       = ls_params-source_stor_bin
        i_nltyp       = ls_params-dest_stor_type
        i_nlpla       = ls_params-dest_stor_bin
        i_anfme       = ls_params-quantity
        i_altme       = ls_params-base_uom
        i_commit_work = 'X'
      IMPORTING
        e_tanum       = lv_tanum
      EXCEPTIONS
        OTHERS        = 99.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Transfer order creation failed, subrc={ sy-subrc }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Transfer order created' iv_data = |{ lv_tanum }| ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_co DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_internal_order
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS activity_alloc
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_co IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'CO' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_INTERNAL_ORDER'.
        rs_result = create_internal_order( iv_payload ).
      WHEN 'ACTIVITY_ALLOC'.
        rs_result = activity_alloc( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown CO action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_internal_order.
    DATA: ls_master_data TYPE bapi2075_7,
          ls_ret         TYPE bapiret2,
          lv_orderid     TYPE bapi2075_2-order.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_master_data ).

    CALL FUNCTION 'BAPI_INTERNALORDER_CREATE'
      EXPORTING
        i_master_data = ls_master_data
      IMPORTING
        orderid       = lv_orderid
        return        = ls_ret.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Internal order creation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Internal order created' iv_data = lv_orderid ).
    ENDIF.
  ENDMETHOD.

  METHOD activity_alloc.
    DATA: ls_params TYPE zrouter_co_alloc_params,
          ls_ret    TYPE bapiret2.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'BAPI_CO_ALLOCACTUALS'
      EXPORTING
        controllingarea = ls_params-controlling_area
        sendercostcenter = ls_params-sender_cost_center
        receivercostcenter = ls_params-receiver_cost_center
        activitytype    = ls_params-activity_type
        quantity        = ls_params-quantity
        fiscalperiod    = ls_params-period
        fiscalyear      = ls_params-fiscal_year
      IMPORTING
        return          = ls_ret.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Activity allocation failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Activity allocation posted' ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_hcm DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS read_employee
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS create_infotype
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_hcm IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'HCM' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'READ_EMPLOYEE'.
        rs_result = read_employee( iv_payload ).
      WHEN 'CREATE_INFOTYPE'.
        rs_result = create_infotype( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown HCM action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD read_employee.
    DATA: lt_return TYPE TABLE OF bapiret2.
    CALL FUNCTION 'BAPI_EMPLOYEE_GETDATA'
      EXPORTING
        employee_id = iv_payload
      TABLES
        return      = lt_return.
    READ TABLE lt_return INTO DATA(ls_ret) INDEX 1.
    IF sy-subrc = 0 AND ls_ret-type = 'E'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Employee read failed: { ls_ret-message }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Employee data retrieved' ).
    ENDIF.
  ENDMETHOD.

  METHOD create_infotype.
    DATA: ls_params TYPE zrouter_hcm_infotype_params,
          ls_ret    TYPE bapiret2.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'BAPI_EMPLOYEE_ENQUEUE'
      EXPORTING
        employee_id = ls_params-employee_id.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Employee enqueue failed| ).
      RETURN.
    ENDIF.

    CALL FUNCTION 'PA_INFOTYPE_INSERT'
      EXPORTING
        employee_id  = ls_params-employee_id
        infotype     = ls_params-infotype
        subtype      = ls_params-subtype
        begda        = ls_params-begin_date
        endda        = ls_params-end_date
      IMPORTING
        return       = ls_ret.
    IF ls_ret-type CA 'EA'.
      CALL FUNCTION 'BAPI_TRANSACTION_ROLLBACK'.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Infotype insert failed: { ls_ret-message }| ).
    ELSE.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT' EXPORTING wait = 'X'.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Infotype record created' ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.


CLASS zcl_zrouter_handler_basis DEFINITION PUBLIC FINAL CREATE PUBLIC
  INHERITING FROM zcl_zrouter_handler_abstract.
  PUBLIC SECTION.
    METHODS constructor
      IMPORTING
        io_logger TYPE REF TO zif_zrouter_logger
        io_config TYPE REF TO zif_zrouter_config.
  PROTECTED SECTION.
    METHODS handle_custom_action REDEFINITION.
  PRIVATE SECTION.
    METHODS create_request
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS release_request
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS st22_scan
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
    METHODS code_analysis
      IMPORTING iv_payload     TYPE string
      RETURNING VALUE(rs_result) TYPE zif_zrouter_handler=>ty_action_result.
ENDCLASS.

CLASS zcl_zrouter_handler_basis IMPLEMENTATION.
  METHOD constructor.
    super->constructor( io_logger = io_logger io_config = io_config iv_module = 'BASIS' ).
  ENDMETHOD.

  METHOD handle_custom_action.
    CASE to_upper( iv_action ).
      WHEN 'CREATE_REQUEST'.
        rs_result = create_request( iv_payload ).
      WHEN 'RELEASE_REQUEST'.
        rs_result = release_request( iv_payload ).
      WHEN 'ST22_SCAN'.
        rs_result = st22_scan( iv_payload ).
      WHEN 'CODE_ANALYSIS'.
        rs_result = code_analysis( iv_payload ).
      WHEN OTHERS.
        RAISE EXCEPTION TYPE zcx_zrouter EXPORTING mv_text = |Unknown BASIS action: { iv_action }|.
    ENDCASE.
  ENDMETHOD.

  METHOD create_request.
    DATA: ls_params TYPE zrouter_basis_tr_params,
          lv_request TYPE trkorr.

    " Parse JSON payload
    /ui2/cl_json=>deserialize(
      EXPORTING json = iv_payload
      CHANGING  data = ls_params ).

    CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'
      EXPORTING
        iv_type     = ls_params-request_type
        iv_text     = ls_params-owner_text
        iv_target   = ls_params-target_system
      IMPORTING
        ev_request  = lv_request
      EXCEPTIONS
        OTHERS      = 99.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Transport request creation failed, subrc={ sy-subrc }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Transport request created' iv_data = lv_request ).
    ENDIF.
  ENDMETHOD.

  METHOD release_request.
    CALL FUNCTION 'TR_RELEASE_REQUEST'
      EXPORTING
        iv_trkorr = iv_payload
      EXCEPTIONS
        OTHERS    = 99.
    IF sy-subrc <> 0.
      rs_result = build_result( iv_status = 'ERROR' iv_message = |Release failed, subrc={ sy-subrc }| ).
    ELSE.
      rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Transport request released' ).
    ENDIF.
  ENDMETHOD.

  METHOD st22_scan.
    DATA: lt_snap TYPE TABLE OF snap,
          lv_count TYPE i.
    SELECT COUNT(*) INTO @lv_count
      FROM snap
      WHERE datum BETWEEN @iv_payload AND @sy-datum
      UP TO 1 ROWS.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'ST22 scan complete' iv_data = |{ lv_count } dumps found| ).
  ENDMETHOD.

  METHOD code_analysis.
    DATA: lt_ret TYPE TABLE OF bapiret2.
    CALL FUNCTION 'TRINT_INSPECT_OBJECTS'
      EXPORTING
        iv_mode = 'N'.
    rs_result = build_result( iv_status = 'SUCCESS' iv_message = 'Code analysis triggered' ).
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
*& 5. Classe Central Dispatcher - ZCL_ZROUTER_DISPATCH
*&---------------------------------------------------------------------*

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

*&---------------------------------------------------------------------*
*& 6. Classe de Controle Batch - ZCL_ZROUTER_BATCH
*&---------------------------------------------------------------------*

CLASS zcl_zrouter_batch DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    TYPES:
      BEGIN OF ty_batch_action,
        seqnr   TYPE i,
        module  TYPE string,
        action  TYPE string,
        payload TYPE string,
      END OF ty_batch_action,
      ty_batch_actions TYPE STANDARD TABLE OF ty_batch_action,

      BEGIN OF ty_batch_item_result,
        seqnr   TYPE i,
        module  TYPE string,
        action  TYPE string,
        status  TYPE string,
        message TYPE string,
        data    TYPE string,
      END OF ty_batch_item_result,
      ty_batch_results TYPE STANDARD TABLE OF ty_batch_item_result,

      BEGIN OF ty_batch_result,
        batch_guid TYPE sysuuid_c32,
        status     TYPE string,
        results    TYPE ty_batch_results,
      END OF ty_batch_result.

    METHODS execute_batch
      IMPORTING it_actions       TYPE ty_batch_actions
      RETURNING VALUE(rs_result) TYPE ty_batch_result.

    METHODS constructor
      IMPORTING io_dispatch TYPE REF TO zcl_zrouter_dispatch OPTIONAL.

  PRIVATE SECTION.
    DATA mo_dispatch TYPE REF TO zcl_zrouter_dispatch.
    DATA mo_logger   TYPE REF TO zif_zrouter_logger.
    METHODS save_batch_result
      IMPORTING
        iv_batch_guid TYPE sysuuid_c32
        iv_seqnr      TYPE i
        iv_module     TYPE string
        iv_action     TYPE string
        iv_status     TYPE string
        iv_message    TYPE string
        iv_payload    TYPE string
        iv_result     TYPE string.
    METHODS generate_guid RETURNING VALUE(rv_guid) TYPE sysuuid_c32.
ENDCLASS.

CLASS zcl_zrouter_batch IMPLEMENTATION.
  METHOD constructor.
    IF io_dispatch IS SUPPLIED.
      mo_dispatch = io_dispatch.
    ELSE.
      mo_dispatch = NEW zcl_zrouter_dispatch( ).
    ENDIF.
    mo_logger = NEW zcl_zrouter_logger( ).
  ENDMETHOD.

  METHOD generate_guid.
    TRY.
        rv_guid = cl_system_uuid=>create_uuid_c32_static( ).
      CATCH cx_uuid_error.
        " sy-index is 0 outside of loops — use random fallback
        rv_guid = |{ cl_abap_random_int=>create(
          seed = cl_abap_random=>seed( )
          min  = 1000000000
          max  = 9999999999 )->get_next( ) }|.
    ENDTRY.
  ENDMETHOD.

  METHOD save_batch_result.
    DATA: ls_batch TYPE zrouter_batlog.
    ls_batch-batch_guid = iv_batch_guid.
    ls_batch-seqnr      = iv_seqnr.
    ls_batch-module     = iv_module.
    ls_batch-action     = iv_action.
    ls_batch-status     = iv_status.
    ls_batch-message    = iv_message.
    ls_batch-payload    = iv_payload.
    ls_batch-result     = iv_result.
    GET TIME STAMP FIELD ls_batch-timestamp.
    MODIFY zrouter_batlog FROM @ls_batch.
  ENDMETHOD.

  METHOD execute_batch.
    DATA(lv_overall_status) = 'SUCCESS'.
    rs_result-batch_guid = generate_guid( ).

    LOOP AT it_actions INTO DATA(ls_action).
      DATA(ls_dispatch) = mo_dispatch->dispatch(
        iv_module  = ls_action-module
        iv_action  = ls_action-action
        iv_payload = ls_action-payload ).

      APPEND VALUE #( seqnr   = ls_action-seqnr
                      module  = ls_action-module
                      action  = ls_action-action
                      status  = ls_dispatch-status
                      message = ls_dispatch-message
                      data    = ls_dispatch-data ) TO rs_result-results.

      save_batch_result(
        iv_batch_guid = rs_result-batch_guid
        iv_seqnr      = ls_action-seqnr
        iv_module     = ls_action-module
        iv_action     = ls_action-action
        iv_status     = ls_dispatch-status
        iv_message    = ls_dispatch-message
        iv_payload    = ls_action-payload
        iv_result     = ls_dispatch-data ).

      IF ls_dispatch-status = 'ERROR'.
        lv_overall_status = 'ERROR'.
        " Each handler already did BAPI_TRANSACTION_ROLLBACK for its own LUW.
        " Stop processing but do NOT rollback here — prior successful
        " actions are already committed by their own handlers.
        EXIT.
      ENDIF.
    ENDLOOP.

    IF lv_overall_status = 'SUCCESS'.
      CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'.
    ENDIF.

    rs_result-status = lv_overall_status.
    mo_logger->log_action(
      iv_module  = 'BATCH'
      iv_action  = 'EXECUTE'
      iv_status  = rs_result-status
      iv_message = |Batch { rs_result-batch_guid } completed with { lines( rs_result-results ) } actions| ).
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
*& 7. Function Module RFC - ZROUTER_DISPATCH_FM
*&---------------------------------------------------------------------*
FUNCTION ZROUTER_DISPATCH_FM.
*"----------------------------------------------------------------------
*"*"Interface Local:
*"  IMPORTING
*"     VALUE(IV_MODULE) TYPE STRING
*"     VALUE(IV_ACTION) TYPE STRING
*"     VALUE(IV_PAYLOAD) TYPE STRING
*"  EXPORTING
*"     VALUE(EV_RESULT) TYPE STRING
*"     VALUE(EV_STATUS) TYPE STRING
*"     VALUE(EV_RETURN_MESSAGE) TYPE STRING
*"----------------------------------------------------------------------
  DATA(lo_dispatch) = NEW zcl_zrouter_dispatch( ).
  DATA(ls_result) = lo_dispatch->dispatch(
    iv_module  = iv_module
    iv_action  = iv_action
    iv_payload = iv_payload
  ).
  ev_status         = ls_result-status.
  ev_result         = ls_result-data.
  ev_return_message = ls_result-message.
ENDFUNCTION.
