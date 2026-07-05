
INTERFACE zif_zrouter_config PUBLIC.
  TYPES:
    BEGIN OF ty_config_entry,
      module    TYPE string,
      action    TYPE string,
      active    TYPE abap_bool,
      batchable TYPE abap_bool,
      timeout   TYPE i,
    END OF ty_config_entry,
    ty_config_entries TYPE STANDARD TABLE OF ty_config_entry WITH EMPTY KEY.

  METHODS get_config
    IMPORTING
      iv_module        TYPE string
      iv_action        TYPE string
    RETURNING
      VALUE(rs_config) TYPE ty_config_entry
    RAISING
      cx_zrouter.

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
      cx_zrouter.

  METHODS get_logs
    IMPORTING
      iv_module      TYPE string OPTIONAL
      iv_date        TYPE dats OPTIONAL
    RETURNING
      VALUE(rt_logs) TYPE STANDARD TABLE OF ty_log_entry WITH EMPTY KEY.
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