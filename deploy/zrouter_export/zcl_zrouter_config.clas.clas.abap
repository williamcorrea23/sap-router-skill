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