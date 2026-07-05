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