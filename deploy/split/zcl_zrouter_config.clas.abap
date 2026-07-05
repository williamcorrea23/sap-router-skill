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