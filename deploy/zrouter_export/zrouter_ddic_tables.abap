*&---------------------------------------------------------------------*
*& Report ZROUTER_DDIC_SETUP — Create ZROUTER DDIC tables
*& Execute via SE38 to create ZROUTER_CONFIG and ZROUTER_LOG tables
*&---------------------------------------------------------------------*
REPORT zrouter_ddic_setup.

TABLES: dd02l, dd03l, dd04t.

FORM create_table USING iv_table TYPE tabname iv_desc TYPE ddtext.
  DATA: ls_dd02l TYPE dd02l,
        lt_dd03l TYPE TABLE OF dd03l,
        ls_dd03l TYPE dd03l,
        lv_tabclass TYPE dd02l-tabclass.

  " Set table class based on delivery
  IF iv_table = 'ZROUTER_CONFIG' OR iv_table = 'ZROUTER_LOG' OR iv_table = 'ZROUTER_BATCH_RESULT'.
    lv_tabclass = 'TRANSP'.
  ELSE.
    lv_tabclass = 'TRANSP'.
  ENDIF.

  ls_dd02l-tabname    = iv_table.
  ls_dd02l-ddlanguage = 'E'.
  ls_dd02l-tabclass   = lv_tabclass.
  ls_dd02l-ddtext     = iv_desc.
  ls_dd02l-contflag   = 'A'.
  ls_dd02l-mainflag   = 'X'.
  ls_dd02l-masterlang = 'E'.

  CALL FUNCTION 'DDIF_TABL_PUT'
    EXPORTING
      name              = iv_table
      dd02v_wa          = ls_dd02l
    EXCEPTIONS
      tabl_not_found    = 1
      name_inconsistent = 2
      OTHERS            = 3.
  IF sy-subrc <> 0.
    WRITE: / 'Table', iv_table, 'creation failed. Subrc =', sy-subrc.
    RETURN.
  ENDIF.

  WRITE: / 'Table', iv_table, '- header created.'.
ENDFORM.

FORM add_field USING iv_table  TYPE tabname
                     iv_field  TYPE fieldname
                     iv_pos    TYPE tabfdpos
                     iv_role   TYPE rollname
                     iv_key    TYPE keyflag
                     iv_notnull TYPE notnull.

  DATA: ls_dd03l TYPE dd03l.
  ls_dd03l-tabname   = iv_table.
  ls_dd03l-fieldname = iv_field.
  ls_dd03l-position   = iv_pos.
  ls_dd03l-rollname   = iv_role.
  ls_dd03l-keyflag    = iv_key.
  ls_dd03l-notnull    = iv_notnull.
  ls_dd03l-ddlanguage = 'E'.

  CALL FUNCTION 'DDIF_FIELDINFO_GET'
    EXPORTING
      tabname   = iv_table
      fieldname = iv_field
    EXCEPTIONS
      OTHERS    = 1.
  IF sy-subrc <> 0.
    " Field doesn't exist, add it
    CALL FUNCTION 'DDIF_TABL_ACTIVATE'
      EXPORTING
        name        = iv_table
      EXCEPTIONS
        OTHERS      = 0.
  ENDIF.
ENDFORM.

START-OF-SELECTION.
  WRITE: / 'ZROUTER DDIC Setup - Creating tables...'.

  " Table 1: ZROUTER_CONFIG - Action configuration (module/action allowlist)
  PERFORM create_table USING 'ZROUTER_CONFIG' 'ZROUTER Action Configuration'.
  " Fields defined manually via SE11. Execute and then use SE11 to add fields.
  WRITE: / 'Use SE11 to add fields to ZROUTER_CONFIG:',
         / '  MANDT     MANDT    CLNT 3  KEY  Client',
         / '  MODULE    CHAR     CHAR 10 KEY  Module (MM/SD/FI/etc.)',
         / '  ACTION    CHAR     CHAR 30 KEY  Action name',
         / '  ACTIVE    CHAR     CHAR 1      Active flag (X=active)',
         / '  BATCHABLE CHAR     CHAR 1      Batchable flag',
         / '  TIMEOUT   INT4     INT4   0    Timeout in seconds'.

  SKIP.
  PERFORM create_table USING 'ZROUTER_LOG' 'ZROUTER Audit Log'.
  WRITE: / 'Use SE11 to add fields to ZROUTER_LOG:',
         / '  MANDT     MANDT    CLNT 3  KEY  Client',
         / '  GUID      SYSUUID  CHAR 32 KEY  GUID',
         / '  MODULE    CHAR     CHAR 10     Module',
         / '  ACTION    CHAR     CHAR 30     Action name',
         / '  STATUS    CHAR     CHAR 10     Status (SUCCESS/ERROR)',
         / '  MESSAGE   CHAR     CHAR 200    Message text',
         / '  PAYLOAD   STRING   STRING      JSON payload',
         / '  RESULT    STRING   STRING      JSON result',
         / '  USERNAME  UNAME    CHAR 12     User name',
         / '  TIMESTAMP TIMESTAMPL DEC 21 7  Timestamp'.

  SKIP.
  PERFORM create_table USING 'ZROUTER_BATCH_RESULT' 'ZROUTER Batch Results'.
  WRITE: / 'Use SE11 to add fields to ZROUTER_BATCH_RESULT:',
         / '  MANDT       MANDT    CLNT 3  KEY  Client',
         / '  BATCH_GUID  SYSUUID  CHAR 32 KEY  Batch GUID',
         / '  SEQNR       INT4     INT4   0 KEY  Sequence number',
         / '  MODULE      CHAR     CHAR 10     Module',
         / '  ACTION      CHAR     CHAR 30     Action name',
         / '  STATUS      CHAR     CHAR 10     Status',
         / '  MESSAGE     CHAR     CHAR 200    Message text',
         / '  PAYLOAD     STRING   STRING      JSON payload',
         / '  RESULT      STRING   STRING      JSON result',
         / '  TIMESTAMP   TIMESTAMPL DEC 21 7  Timestamp'.

  WRITE: / 'Done. Activate all tables via SE11 -> activate (Ctrl+F3).'.
