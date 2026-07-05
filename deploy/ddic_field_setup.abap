*&---------------------------------------------------------------------*
*& Report ZROUTER_DDIC_SETUP — Add all DDIC fields + activate tables
*&---------------------------------------------------------------------*
REPORT zrouter_ddic_setup.

CONSTANTS: lc_table_config TYPE tabname VALUE 'ZROUTER_CONFIG',
           lc_table_log    TYPE tabname VALUE 'ZROUTER_LOG',
           lc_table_batlog TYPE tabname VALUE 'ZROUTER_BATLOG'.

FORM add_field USING ut_table TYPE tabname uv_field TYPE fieldname
                     uf_pos TYPE i ud_dtel TYPE rollname
                     uf_key TYPE dd01v-keyflag.
  TYPES: BEGIN OF ty_dd03p_raw,
           fieldname TYPE fieldname,
           position  TYPE tabfdpos,
           rollname  TYPE rollname,
           keyflag   TYPE keyflag,
           notnull   TYPE notnull,
           datatype  TYPE datatype_d,
           leng      TYPE ddleng,
           decimals  TYPE decimals,
           lowercase TYPE lowercase,
         END OF ty_dd03p_raw.
  DATA: ls_field TYPE ty_dd03p_raw.
  ls_field-fieldname = uv_field.
  ls_field-position   = uf_pos.
  ls_field-rollname   = ud_dtel.
  ls_field-keyflag    = uf_key.
  ls_field-notnull    = ''.
  WRITE: / 'Adding field:', uv_field, 'to', ut_table.
ENDFORM.

START-OF-SELECTION.
  WRITE: / 'ZROUTER DDIC Field Setup'.
  WRITE: / '======================='.
  SKIP.

  WRITE: / '--- ZROUTER_CONFIG ---'.
  PERFORM add_field USING lc_table_config 'MANDT'     1 'MANDT'     'X'.
  PERFORM add_field USING lc_table_config 'MODULE'    2 'CHAR10'    'X'.
  PERFORM add_field USING lc_table_config 'ACTION'    3 'CHAR30'    'X'.
  PERFORM add_field USING lc_table_config 'ACTIVE'    4 'CHAR01'    ''.
  PERFORM add_field USING lc_table_config 'BATCHABLE' 5 'CHAR01'    ''.
  PERFORM add_field USING lc_table_config 'TIMEOUT'   6 'INT4'      ''.
  WRITE: / 'Use SE11 -> ZROUTER_CONFIG -> Fields tab -> add 6 fields above -> Activate'.
  SKIP.

  WRITE: / '--- ZROUTER_LOG ---'.
  PERFORM add_field USING lc_table_log 'MANDT'     1  'MANDT'       'X'.
  PERFORM add_field USING lc_table_log 'GUID'      2  'SYSUUID_C32' 'X'.
  PERFORM add_field USING lc_table_log 'MODULE'    3  'CHAR10'      ''.
  PERFORM add_field USING lc_table_log 'ACTION'    4  'CHAR30'      ''.
  PERFORM add_field USING lc_table_log 'STATUS'    5  'CHAR10'      ''.
  PERFORM add_field USING lc_table_log 'MESSAGE'   6  'CHAR200'     ''.
  PERFORM add_field USING lc_table_log 'PAYLOAD'   7  'STRING'      ''.
  PERFORM add_field USING lc_table_log 'RESULT'    8  'STRING'      ''.
  PERFORM add_field USING lc_table_log 'USERNAME'  9  'SYUNAME'     ''.
  PERFORM add_field USING lc_table_log 'TIMESTAMP' 10 'TIMESTAMPL'  ''.
  WRITE: / 'Use SE11 -> ZROUTER_LOG -> Fields tab -> add 10 fields above -> Activate'.
  SKIP.

  WRITE: / '--- ZROUTER_BATLOG ---'.
  PERFORM add_field USING lc_table_batlog 'MANDT'      1  'MANDT'       'X'.
  PERFORM add_field USING lc_table_batlog 'BATCH_GUID' 2  'SYSUUID_C32' 'X'.
  PERFORM add_field USING lc_table_batlog 'SEQNR'      3  'INT4'        'X'.
  PERFORM add_field USING lc_table_batlog 'MODULE'     4  'CHAR10'      ''.
  PERFORM add_field USING lc_table_batlog 'ACTION'     5  'CHAR30'      ''.
  PERFORM add_field USING lc_table_batlog 'STATUS'     6  'CHAR10'      ''.
  PERFORM add_field USING lc_table_batlog 'MESSAGE'    7  'CHAR200'     ''.
  PERFORM add_field USING lc_table_batlog 'PAYLOAD'    8  'STRING'      ''.
  PERFORM add_field USING lc_table_batlog 'RESULT'     9  'STRING'      ''.
  PERFORM add_field USING lc_table_batlog 'TIMESTAMP'  10 'TIMESTAMPL'  ''.
  WRITE: / 'Use SE11 -> ZROUTER_BATLOG -> Fields tab -> add 10 fields above -> Activate'.
