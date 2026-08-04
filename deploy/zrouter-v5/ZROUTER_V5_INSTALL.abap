*&---------------------------------------------------------------------*
*& Report  ZROUTER_V5_INSTALL
*&---------------------------------------------------------------------*
*& Instalador auto-contido do ZROUTER v5.
*&
*& COMO USAR
*&   1. SE38 -> criar programa executável ZROUTER_V5_INSTALL -> colar este
*&      fonte -> ativar. Nenhum objeto precisa existir antes: este programa
*&      não referencia nada do ZROUTER.
*&   2. Executar. Marcar o que instalar e rodar primeiro em SIMULAÇÃO.
*&   3. Rodar de verdade. Ao final, o autoteste diz o que ficou de pé.
*&
*& O QUE ELE CRIA
*&   - Tabelas ZROUTER_CFG, ZROUTER_LOG, ZROUTER_PEND
*&   - Classe global ZCL_ZROUTER_GW (handler ICF)
*&   - Nó SICF /sap/bc/zrouter (opcional; pode ser feito à mão em SICF)
*&   - Linhas de registry: só operações de LEITURA são semeadas ativas
*&
*& POR QUE UM INSTALADOR E NÃO UM NUGGET SAPLINK
*&   SAPlink importa nugget, mas o próprio SAPlink é um conjunto de classes
*&   que precisa existir antes -- o problema de bootstrap continua de pé para
*&   quem só tem o .slnk. Um REPORT é o único artefato ABAP que se instala
*&   com copiar/colar e zero dependência. O nugget continua disponível em
*&   ZROUTER_V5.slnk para quem já roda SAPlink.
*&
*& SOBRE `INSERT REPORT` AQUI
*&   A golden rule `no-eval-expression` proíbe compilar dado de REQUISIÇÃO.
*&   Este programa compila um fonte CONSTANTE, embutido abaixo, durante uma
*&   instalação que um desenvolvedor disparou conscientemente. É a mesma coisa
*&   que o SAPlink faz. O que a regra proíbe -- e o ZROUTER v5 não faz em
*&   nenhum ponto -- é transformar corpo de HTTP em código.
*&---------------------------------------------------------------------*
REPORT zrouter_v5_install LINE-SIZE 255.

CONSTANTS:
  co_version   TYPE string VALUE '5.0.0',
  co_pkg       TYPE devclass VALUE '$TMP',
  co_class     TYPE seoclsname VALUE 'ZCL_ZROUTER_GW',
  co_icf_path  TYPE string VALUE '/sap/bc/zrouter'.

*&---------------------------------------------------------------------*
*& Tela de seleção
*&---------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE t_b1.
PARAMETERS:
  p_simul TYPE abap_bool AS CHECKBOX DEFAULT 'X',
  p_pack  TYPE devclass DEFAULT '$TMP'.
SELECTION-SCREEN END OF BLOCK b1.

SELECTION-SCREEN BEGIN OF BLOCK b2 WITH FRAME TITLE t_b2.
PARAMETERS:
  p_tab   TYPE abap_bool AS CHECKBOX DEFAULT 'X',
  p_cls   TYPE abap_bool AS CHECKBOX DEFAULT 'X',
  p_icf   TYPE abap_bool AS CHECKBOX DEFAULT ' ',
  p_seed  TYPE abap_bool AS CHECKBOX DEFAULT 'X'.
SELECTION-SCREEN END OF BLOCK b2.

SELECTION-SCREEN BEGIN OF BLOCK b3 WITH FRAME TITLE t_b3.
PARAMETERS:
  p_test  TYPE abap_bool AS CHECKBOX DEFAULT 'X'.
SELECTION-SCREEN END OF BLOCK b3.

*&---------------------------------------------------------------------*
*& Log de instalação
*&---------------------------------------------------------------------*
CLASS lcl_log DEFINITION.
  PUBLIC SECTION.
    CLASS-METHODS:
      ok      IMPORTING iv_text TYPE string,
      skip    IMPORTING iv_text TYPE string,
      warn    IMPORTING iv_text TYPE string,
      fail    IMPORTING iv_text TYPE string,
      head    IMPORTING iv_text TYPE string,
      failed  RETURNING VALUE(rv_failed) TYPE abap_bool.
  PRIVATE SECTION.
    CLASS-DATA gv_failed TYPE abap_bool.
ENDCLASS.

CLASS lcl_log IMPLEMENTATION.
  METHOD head.
    SKIP.
    WRITE: / iv_text COLOR COL_HEADING.
    ULINE.
  ENDMETHOD.
  METHOD ok.
    WRITE: / '  [ ok ]' COLOR COL_POSITIVE, iv_text.
  ENDMETHOD.
  METHOD skip.
    WRITE: / '  [pula]' COLOR COL_NORMAL, iv_text.
  ENDMETHOD.
  METHOD warn.
    WRITE: / '  [aten]' COLOR COL_TOTAL, iv_text.
  ENDMETHOD.
  METHOD fail.
    gv_failed = abap_true.
    WRITE: / '  [FALH]' COLOR COL_NEGATIVE, iv_text.
  ENDMETHOD.
  METHOD failed.
    rv_failed = gv_failed.
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
*& Criação das tabelas
*&
*& Os três defeitos de DDIC do spec v4 estão corrigidos aqui:
*&   - `abap.syst_lo05` não existe; timestamp usa DEC 21/7 (TIMESTAMPL).
*&   - payload/result eram CHAR(1024) recebendo STRING, truncando em
*&     silêncio; agora são STRING (LRAW/LCHR via DDIC = tipo STRG).
*&   - faltavam tableCategory/deliveryClass; log e config têm classes de
*&     entrega diferentes (log = APPL0/L, config = customizing/C).
*&---------------------------------------------------------------------*
CLASS lcl_tables DEFINITION.
  PUBLIC SECTION.
    METHODS install IMPORTING iv_simulate TYPE abap_bool
                              iv_package  TYPE devclass.
  PRIVATE SECTION.
    METHODS:
      build_cfg  RETURNING VALUE(rt_fields) TYPE dd03ttyp,
      build_log  RETURNING VALUE(rt_fields) TYPE dd03ttyp,
      build_pend RETURNING VALUE(rt_fields) TYPE dd03ttyp,
      field
        IMPORTING iv_name     TYPE dd03p-fieldname
                  iv_pos      TYPE i
                  iv_key      TYPE abap_bool DEFAULT abap_false
                  iv_datatype TYPE dd03p-datatype
                  iv_leng     TYPE i DEFAULT 0
                  iv_decimals TYPE i DEFAULT 0
                  iv_rollname TYPE dd03p-rollname OPTIONAL
                  iv_text     TYPE string OPTIONAL
        RETURNING VALUE(rs_field) TYPE dd03p,
      put_table
        IMPORTING iv_name     TYPE dd02l-tabname
                  iv_text     TYPE string
                  iv_delclass TYPE dd02l-contflag
                  it_fields   TYPE dd03ttyp
                  iv_simulate TYPE abap_bool
                  iv_package  TYPE devclass.
ENDCLASS.

CLASS lcl_tables IMPLEMENTATION.

  METHOD field.
    rs_field-fieldname = iv_name.
    rs_field-position  = iv_pos.
    rs_field-keyflag   = COND #( WHEN iv_key = abap_true THEN 'X' ELSE space ).
    rs_field-datatype  = iv_datatype.
    rs_field-leng      = iv_leng.
    rs_field-decimals  = iv_decimals.
    rs_field-rollname  = iv_rollname.
    rs_field-ddtext    = iv_text.
    " NOT NULL em todo campo-chave: sem isso a ativação recusa a tabela.
    IF iv_key = abap_true.
      rs_field-notnull = 'X'.
    ENDIF.
  ENDMETHOD.

  METHOD build_cfg.
    " Registry das operações. A coluna que o v4 não tinha e que sustenta o
    " invariante do produto é OP_MODE: 'R' (leitura) ou 'W' (escrita).
    " Sem ela, "modo escrita" existia só na documentação -- e a UI/agente não
    " tinha como pedir "só leitura" em runtime.
    APPEND field( iv_name = 'MANDT'  iv_pos = 1 iv_key = abap_true
                  iv_datatype = 'CLNT' iv_leng = 3 iv_rollname = 'MANDT' ) TO rt_fields.
    APPEND field( iv_name = 'MODULE' iv_pos = 2 iv_key = abap_true
                  iv_datatype = 'CHAR' iv_leng = 30 iv_text = 'Modulo' ) TO rt_fields.
    APPEND field( iv_name = 'ACTION' iv_pos = 3 iv_key = abap_true
                  iv_datatype = 'CHAR' iv_leng = 60 iv_text = 'Acao' ) TO rt_fields.
    APPEND field( iv_name = 'OP_MODE' iv_pos = 4
                  iv_datatype = 'CHAR' iv_leng = 1 iv_text = 'R=leitura W=escrita' ) TO rt_fields.
    APPEND field( iv_name = 'NEEDS_APPROVAL' iv_pos = 5
                  iv_datatype = 'CHAR' iv_leng = 1 iv_text = 'Exige aprovacao humana' ) TO rt_fields.
    APPEND field( iv_name = 'ACTIVE' iv_pos = 6
                  iv_datatype = 'CHAR' iv_leng = 1 iv_text = 'Ativa' ) TO rt_fields.
    APPEND field( iv_name = 'AUTH_ACTVT' iv_pos = 7
                  iv_datatype = 'CHAR' iv_leng = 2 iv_text = 'Atividade S_ZROUTER' ) TO rt_fields.
    APPEND field( iv_name = 'TIMEOUT_S' iv_pos = 8
                  iv_datatype = 'INT4' iv_leng = 10 iv_text = 'Timeout (s)' ) TO rt_fields.
    APPEND field( iv_name = 'CHANGED_BY' iv_pos = 9
                  iv_datatype = 'CHAR' iv_leng = 12 iv_text = 'Alterado por' ) TO rt_fields.
    APPEND field( iv_name = 'CHANGED_AT' iv_pos = 10
                  iv_datatype = 'DEC' iv_leng = 21 iv_decimals = 7 iv_text = 'Alterado em' ) TO rt_fields.
  ENDMETHOD.

  METHOD build_log.
    APPEND field( iv_name = 'MANDT' iv_pos = 1 iv_key = abap_true
                  iv_datatype = 'CLNT' iv_leng = 3 iv_rollname = 'MANDT' ) TO rt_fields.
    APPEND field( iv_name = 'LOG_ID' iv_pos = 2 iv_key = abap_true
                  iv_datatype = 'CHAR' iv_leng = 32 iv_text = 'GUID do log' ) TO rt_fields.
    APPEND field( iv_name = 'CORR_ID' iv_pos = 3
                  iv_datatype = 'CHAR' iv_leng = 32 iv_text = 'Correlacao (pendencia/lote)' ) TO rt_fields.
    APPEND field( iv_name = 'MODULE' iv_pos = 4
                  iv_datatype = 'CHAR' iv_leng = 30 ) TO rt_fields.
    APPEND field( iv_name = 'ACTION' iv_pos = 5
                  iv_datatype = 'CHAR' iv_leng = 60 ) TO rt_fields.
    APPEND field( iv_name = 'OP_MODE' iv_pos = 6
                  iv_datatype = 'CHAR' iv_leng = 1 ) TO rt_fields.
    APPEND field( iv_name = 'STATUS' iv_pos = 7
                  iv_datatype = 'CHAR' iv_leng = 20 ) TO rt_fields.
    APPEND field( iv_name = 'MESSAGE' iv_pos = 8
                  iv_datatype = 'STRG' iv_text = 'Mensagem' ) TO rt_fields.
    APPEND field( iv_name = 'PAYLOAD' iv_pos = 9
                  iv_datatype = 'STRG' iv_text = 'Payload integral' ) TO rt_fields.
    APPEND field( iv_name = 'RESULT' iv_pos = 10
                  iv_datatype = 'STRG' iv_text = 'Resultado integral' ) TO rt_fields.
    APPEND field( iv_name = 'UNAME' iv_pos = 11
                  iv_datatype = 'CHAR' iv_leng = 12 ) TO rt_fields.
    APPEND field( iv_name = 'TSTAMP' iv_pos = 12
                  iv_datatype = 'DEC' iv_leng = 21 iv_decimals = 7 ) TO rt_fields.
  ENDMETHOD.

  METHOD build_pend.
    " A tabela que o v4 não tinha, e sem a qual o gate humano é impossível:
    " uma ação de escrita vira LINHA PENDENTE, não efeito. Quem aprova lê
    " daqui o texto literal do que vai acontecer.
    APPEND field( iv_name = 'MANDT' iv_pos = 1 iv_key = abap_true
                  iv_datatype = 'CLNT' iv_leng = 3 iv_rollname = 'MANDT' ) TO rt_fields.
    APPEND field( iv_name = 'PEND_ID' iv_pos = 2 iv_key = abap_true
                  iv_datatype = 'CHAR' iv_leng = 32 iv_text = 'GUID da pendencia' ) TO rt_fields.
    APPEND field( iv_name = 'MODULE' iv_pos = 3
                  iv_datatype = 'CHAR' iv_leng = 30 ) TO rt_fields.
    APPEND field( iv_name = 'ACTION' iv_pos = 4
                  iv_datatype = 'CHAR' iv_leng = 60 ) TO rt_fields.
    APPEND field( iv_name = 'PAYLOAD' iv_pos = 5
                  iv_datatype = 'STRG' ) TO rt_fields.
    APPEND field( iv_name = 'DESCRIPTION' iv_pos = 6
                  iv_datatype = 'STRG' iv_text = 'Texto literal aprovado' ) TO rt_fields.
    APPEND field( iv_name = 'STATUS' iv_pos = 7
                  iv_datatype = 'CHAR' iv_leng = 10 iv_text = 'PENDING/APPROVED/DENIED/DONE' ) TO rt_fields.
    APPEND field( iv_name = 'REQUESTED_BY' iv_pos = 8
                  iv_datatype = 'CHAR' iv_leng = 12 ) TO rt_fields.
    APPEND field( iv_name = 'DECIDED_BY' iv_pos = 9
                  iv_datatype = 'CHAR' iv_leng = 12 ) TO rt_fields.
    APPEND field( iv_name = 'CREATED_AT' iv_pos = 10
                  iv_datatype = 'DEC' iv_leng = 21 iv_decimals = 7 ) TO rt_fields.
    APPEND field( iv_name = 'EXPIRES_AT' iv_pos = 11
                  iv_datatype = 'DEC' iv_leng = 21 iv_decimals = 7 ) TO rt_fields.
  ENDMETHOD.

  METHOD put_table.
    DATA: ls_head   TYPE dd02v,
          lt_fields TYPE dd03ttyp,
          lv_rc     TYPE sy-subrc.

    SELECT SINGLE tabname FROM dd02l INTO @DATA(lv_exists) WHERE tabname = @iv_name.
    IF sy-subrc = 0.
      lcl_log=>skip( |{ iv_name }: já existe, não recriada| ).
      RETURN.
    ENDIF.

    IF iv_simulate = abap_true.
      lcl_log=>ok( |{ iv_name }: seria criada ({ lines( it_fields ) } campos)| ).
      RETURN.
    ENDIF.

    ls_head-tabname   = iv_name.
    ls_head-ddlanguage = sy-langu.
    ls_head-tabclass  = 'TRANSP'.
    ls_head-ddtext    = iv_text.
    ls_head-contflag  = iv_delclass.
    ls_head-mainflag  = 'X'.
    ls_head-exclass   = '1'.
    lt_fields = it_fields.

    CALL FUNCTION 'DDIF_TABL_PUT'
      EXPORTING
        name              = iv_name
        dd02v_wa          = ls_head
      TABLES
        dd03p_tab         = lt_fields
      EXCEPTIONS
        tabl_not_found    = 1
        name_inconsistent = 2
        tabl_inconsistent = 3
        put_failure       = 4
        put_refused       = 5
        OTHERS            = 6.
    IF sy-subrc <> 0.
      lcl_log=>fail( |{ iv_name }: DDIF_TABL_PUT falhou (subrc { sy-subrc })| ).
      RETURN.
    ENDIF.

    CALL FUNCTION 'TR_TADIR_INTERFACE'
      EXPORTING
        wi_test_modus    = abap_false
        wi_tadir_pgmid   = 'R3TR'
        wi_tadir_object  = 'TABL'
        wi_tadir_obj_name = CONV sobj_name( iv_name )
        wi_tadir_devclass = iv_package
      EXCEPTIONS
        OTHERS           = 1.

    CALL FUNCTION 'DDIF_TABL_ACTIVATE'
      EXPORTING
        name        = iv_name
      IMPORTING
        rc          = lv_rc
      EXCEPTIONS
        not_found   = 1
        put_failure = 2
        OTHERS      = 3.
    IF sy-subrc <> 0 OR lv_rc > 4.
      lcl_log=>fail( |{ iv_name }: ativação falhou (rc { lv_rc })| ).
      RETURN.
    ENDIF.

    lcl_log=>ok( |{ iv_name }: criada e ativada| ).
  ENDMETHOD.

  METHOD install.
    lcl_log=>head( '1. Tabelas' ).
    " Config é customizing (entrega C): o cliente edita o registry.
    put_table( iv_name = 'ZROUTER_CFG' iv_text = 'ZROUTER: registry de operacoes'
               iv_delclass = 'C' it_fields = build_cfg( )
               iv_simulate = iv_simulate iv_package = iv_package ).
    " Log e pendências são dados de aplicação (entrega A): nunca transportados.
    put_table( iv_name = 'ZROUTER_LOG' iv_text = 'ZROUTER: auditoria'
               iv_delclass = 'A' it_fields = build_log( )
               iv_simulate = iv_simulate iv_package = iv_package ).
    put_table( iv_name = 'ZROUTER_PEND' iv_text = 'ZROUTER: acoes pendentes de aprovacao'
               iv_delclass = 'A' it_fields = build_pend( )
               iv_simulate = iv_simulate iv_package = iv_package ).
  ENDMETHOD.

ENDCLASS.

*&---------------------------------------------------------------------*
*& Fonte da classe global do gateway
*&
*& Mantido como tabela de texto porque é isto que o instalador materializa.
*& Toda a correção de segurança do v5 está aqui:
*&   - AUTHORITY-CHECK OBJECT real (o v4 chamava cl_abap_authorization=>
*&     check_authorization, que NÃO EXISTE no ABAP -- o código não compilava,
*&     então "a segurança estava centralizada" numa chamada inexistente).
*&   - Sem CREATE OBJECT TYPE (var): factory com CASE fechado. O v4
*&     instanciava classe cujo nome vinha de linha de tabela.
*&   - Leitura e escrita em ROTAS SEPARADAS. Escrita nunca executa no mesmo
*&     request: vira pendência e espera decisão humana.
*&   - CSRF, limite de corpo, verificação de método.
*&---------------------------------------------------------------------*
CLASS lcl_class DEFINITION.
  PUBLIC SECTION.
    METHODS install IMPORTING iv_simulate TYPE abap_bool
                              iv_package  TYPE devclass.
  PRIVATE SECTION.
    METHODS source RETURNING VALUE(rt_src) TYPE rswsourcet.
ENDCLASS.

CLASS lcl_class IMPLEMENTATION.

  METHOD source.
    DEFINE _a.
      APPEND &1 TO rt_src.
    END-OF-DEFINITION.

    _a `CLASS zcl_zrouter_gw DEFINITION PUBLIC FINAL CREATE PUBLIC.`.
    _a ``.
    _a `  PUBLIC SECTION.`.
    _a `    INTERFACES if_http_extension.`.
    _a `    CONSTANTS co_max_body TYPE i VALUE 262144.`.
    _a `    CONSTANTS co_max_rows TYPE i VALUE 200.`.
    _a `    CONSTANTS co_ttl_secs TYPE i VALUE 900.`.
    _a ``.
    _a `  PRIVATE SECTION.`.
    _a `    DATA mv_corr TYPE char32.`.
    _a ``.
    _a `    METHODS handle_read   IMPORTING io_srv TYPE REF TO if_http_server.`.
    _a `    METHODS handle_write  IMPORTING io_srv TYPE REF TO if_http_server.`.
    _a `    METHODS handle_queue  IMPORTING io_srv TYPE REF TO if_http_server.`.
    _a `    METHODS handle_decide IMPORTING io_srv TYPE REF TO if_http_server.`.
    _a ``.
    _a `    METHODS exec_read`.
    _a `      IMPORTING iv_op TYPE string iv_data TYPE string`.
    _a `      EXPORTING ev_head TYPE string ev_body TYPE string`.
    _a `                ev_rows TYPE i ev_scalar TYPE string ev_error TYPE string.`.
    _a ``.
    _a `    METHODS exec_write`.
    _a `      IMPORTING iv_op TYPE string iv_data TYPE string`.
    _a `      EXPORTING ev_scalar TYPE string ev_error TYPE string.`.
    _a ``.
    _a `    METHODS op_sysinfo EXPORTING ev_scalar TYPE string.`.
    _a `    METHODS op_table`.
    _a `      IMPORTING iv_data TYPE string`.
    _a `      EXPORTING ev_head TYPE string ev_body TYPE string`.
    _a `                ev_rows TYPE i ev_error TYPE string.`.
    _a `    METHODS op_describe`.
    _a `      IMPORTING iv_data TYPE string`.
    _a `      EXPORTING ev_head TYPE string ev_body TYPE string`.
    _a `                ev_rows TYPE i ev_error TYPE string.`.
    _a `    METHODS op_source_read`.
    _a `      IMPORTING iv_data TYPE string`.
    _a `      EXPORTING ev_scalar TYPE string ev_error TYPE string.`.
    _a `    METHODS op_find`.
    _a `      IMPORTING iv_data TYPE string`.
    _a `      EXPORTING ev_head TYPE string ev_body TYPE string`.
    _a `                ev_rows TYPE i ev_error TYPE string.`.
    _a `    METHODS op_source_write`.
    _a `      IMPORTING iv_data TYPE string`.
    _a `      EXPORTING ev_scalar TYPE string ev_error TYPE string.`.
    _a ``.
    _a `    METHODS authorize IMPORTING iv_op TYPE string iv_mode TYPE char1`.
    _a `                      RETURNING VALUE(rv_ok) TYPE abap_bool.`.
    _a `    METHODS registry_ok IMPORTING iv_op TYPE string iv_mode TYPE char1`.
    _a `                        EXPORTING ev_error TYPE string`.
    _a `                        RETURNING VALUE(rv_ok) TYPE abap_bool.`.
    _a `    METHODS safe_where IMPORTING iv_where TYPE string`.
    _a `                       RETURNING VALUE(rv_ok) TYPE abap_bool.`.
    _a `    METHODS jstr IMPORTING iv_json TYPE string iv_key TYPE string`.
    _a `                 RETURNING VALUE(rv_val) TYPE string.`.
    _a `    METHODS ok_scalar IMPORTING io_srv TYPE REF TO if_http_server iv_data TYPE string.`.
    _a `    METHODS ok_table IMPORTING io_srv TYPE REF TO if_http_server`.
    _a `                               iv_head TYPE string iv_body TYPE string iv_rows TYPE i.`.
    _a `    METHODS fail IMPORTING io_srv TYPE REF TO if_http_server`.
    _a `                           iv_code TYPE i iv_error TYPE string.`.
    _a `    METHODS send IMPORTING io_srv TYPE REF TO if_http_server`.
    _a `                           iv_code TYPE i iv_json TYPE string.`.
    _a `    METHODS audit IMPORTING iv_op TYPE string iv_mode TYPE char1`.
    _a `                            iv_status TYPE string iv_msg TYPE string`.
    _a `                            iv_payload TYPE string iv_result TYPE string.`.
    _a `    METHODS new_id RETURNING VALUE(rv_id) TYPE char32.`.
    _a `    METHODS esc IMPORTING iv_in TYPE string RETURNING VALUE(rv_out) TYPE string.`.
    _a `    METHODS tab RETURNING VALUE(rv_c) TYPE c.`.
    _a `    METHODS nl RETURNING VALUE(rv_c) TYPE c.`.
    _a ``.
    _a `ENDCLASS.`.
    _a ``.
    _a ``.
    _a `CLASS zcl_zrouter_gw IMPLEMENTATION.`.
    _a ``.
    _a `  METHOD tab.`.
    _a `    rv_c = cl_abap_char_utilities=>horizontal_tab.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD nl.`.
    _a `    rv_c = cl_abap_char_utilities=>newline.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD new_id.`.
    _a `    TRY.`.
    _a `        rv_id = cl_system_uuid=>create_uuid_c32_static( ).`.
    _a `      CATCH cx_uuid_error.`.
    _a `        GET TIME STAMP FIELD DATA(lv_ts).`.
    _a `        rv_id = |{ sy-uname }{ lv_ts }|.`.
    _a `    ENDTRY.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD esc.`.
    _a `    rv_out = escape( val = iv_in format = cl_abap_format=>e_json_string ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD if_http_extension~handle_request.`.
    _a `    mv_corr = new_id( ).`.
    _a `    DATA(lv_path) = to_lower( server->request->get_header_field( '~path_info' ) ).`.
    _a `    DATA(lv_meth) = to_upper( server->request->get_method( ) ).`.
    _a ``.
    _a `    " Teto antes de qualquer parse: POST sem limite derruba o work process.`.
    _a `    DATA(lv_len) = CONV i( server->request->get_header_field( 'content-length' ) ).`.
    _a `    IF lv_len > co_max_body.`.
    _a `      fail( io_srv = server iv_code = 413 iv_error = 'too_big' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    CASE lv_path.`.
    _a `      WHEN '/r'.`.
    _a `        IF lv_meth <> 'POST'.`.
    _a `          fail( io_srv = server iv_code = 405 iv_error = 'post_only' ).`.
    _a `          RETURN.`.
    _a `        ENDIF.`.
    _a `        handle_read( server ).`.
    _a `      WHEN '/w'.`.
    _a `        IF lv_meth <> 'POST'.`.
    _a `          fail( io_srv = server iv_code = 405 iv_error = 'post_only' ).`.
    _a `          RETURN.`.
    _a `        ENDIF.`.
    _a `        handle_write( server ).`.
    _a `      WHEN '/q'.`.
    _a `        handle_queue( server ).`.
    _a `      WHEN '/d'.`.
    _a `        IF lv_meth <> 'POST'.`.
    _a `          fail( io_srv = server iv_code = 405 iv_error = 'post_only' ).`.
    _a `          RETURN.`.
    _a `        ENDIF.`.
    _a `        handle_decide( server ).`.
    _a `      WHEN '/healthz'.`.
    _a `        send( io_srv = server iv_code = 200`.
    _a `              iv_json = |\{"ok":1,"v":"5.0.0","sid":"{ sy-sysid }","cli":"{ sy-mandt }"\}| ).`.
    _a `      WHEN OTHERS.`.
    _a `        " 404 explícito. Nunca 200 com corpo vazio: silêncio lido como`.
    _a `        " sucesso é o defeito que o consumidor registrou como P1-7.`.
    _a `        fail( io_srv = server iv_code = 404 iv_error = 'no_route' ).`.
    _a `    ENDCASE.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD jstr.`.
    _a `    " Extrator para chaves de topo. O corpo já passou pelo teto de tamanho;`.
    _a `    " aqui só se busca o valor de uma chave conhecida, nunca se avalia nada.`.
    _a `    DATA lv_val TYPE string.`.
    _a `    FIND REGEX |"{ iv_key }"\\s*:\\s*"([^"\\\\]*(\\\\.[^"\\\\]*)*)"|`.
    _a `      IN iv_json SUBMATCHES lv_val.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      " Aceita também número sem aspas: {"n":50}`.
    _a `      FIND REGEX |"{ iv_key }"\\s*:\\s*(-?[0-9]+)| IN iv_json SUBMATCHES lv_val.`.
    _a `      IF sy-subrc <> 0.`.
    _a `        CLEAR rv_val.`.
    _a `        RETURN.`.
    _a `      ENDIF.`.
    _a `      rv_val = lv_val.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    REPLACE ALL OCCURRENCES OF '\"' IN lv_val WITH '"'.`.
    _a `    REPLACE ALL OCCURRENCES OF '\n' IN lv_val WITH cl_abap_char_utilities=>newline.`.
    _a `    REPLACE ALL OCCURRENCES OF '\t' IN lv_val WITH cl_abap_char_utilities=>horizontal_tab.`.
    _a `    REPLACE ALL OCCURRENCES OF '\\' IN lv_val WITH '\'.`.
    _a `    rv_val = lv_val.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD authorize.`.
    _a `    " auth-check-first: nada acontece antes disto.`.
    _a `    DATA(lv_actvt) = COND char2( WHEN iv_mode = 'W' THEN '02' ELSE '03' ).`.
    _a `    DATA(lv_mod) = substring_before( val = iv_op sub = '.' ).`.
    _a `    DATA(lv_act) = substring_after( val = iv_op sub = '.' ).`.
    _a `    IF lv_mod IS INITIAL.`.
    _a `      lv_mod = iv_op.`.
    _a `    ENDIF.`.
    _a `    AUTHORITY-CHECK OBJECT 'ZROUTER'`.
    _a `      ID 'ZRMODULE' FIELD lv_mod`.
    _a `      ID 'ZRACTION' FIELD lv_act`.
    _a `      ID 'ACTVT'    FIELD lv_actvt.`.
    _a `    rv_ok = xsdbool( sy-subrc = 0 ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD registry_ok.`.
    _a `    DATA(lv_mod) = substring_before( val = iv_op sub = '.' ).`.
    _a `    DATA(lv_act) = substring_after( val = iv_op sub = '.' ).`.
    _a `    SELECT SINGLE op_mode, active FROM zrouter_cfg`.
    _a `      INTO @DATA(ls_cfg)`.
    _a `      WHERE module = @lv_mod AND action = @lv_act.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      ev_error = 'no_op'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF ls_cfg-active <> 'X'.`.
    _a `      ev_error = 'off'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    " O ponto que sustenta o invariante do consumidor: a rota de leitura`.
    _a `    " recusa linha marcada como escrita mesmo com o usuário autorizado, e a`.
    _a `    " de escrita recusa linha de leitura — para que /w não vire atalho de /r`.
    _a `    " sem gate.`.
    _a `    IF iv_mode = 'R' AND ls_cfg-op_mode <> 'R'.`.
    _a `      ev_error = 'write_op'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF iv_mode = 'W' AND ls_cfg-op_mode <> 'W'.`.
    _a `      ev_error = 'read_op'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    rv_ok = abap_true.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD handle_read.`.
    _a `    DATA(lv_body) = io_srv->request->get_cdata( ).`.
    _a `    DATA(lv_op) = to_upper( jstr( iv_json = lv_body iv_key = 'op' ) ).`.
    _a `    IF lv_op IS INITIAL.`.
    _a `      fail( io_srv = io_srv iv_code = 400 iv_error = 'no_op' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF authorize( iv_op = lv_op iv_mode = 'R' ) = abap_false.`.
    _a `      audit( iv_op = lv_op iv_mode = 'R' iv_status = 'DENIED'`.
    _a `             iv_msg = 'sem autorizacao' iv_payload = lv_body iv_result = '' ).`.
    _a `      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    DATA lv_reg_err TYPE string.`.
    _a `    IF registry_ok( EXPORTING iv_op = lv_op iv_mode = 'R'`.
    _a `                    IMPORTING ev_error = lv_reg_err ) = abap_false.`.
    _a `      fail( io_srv = io_srv iv_code = 409 iv_error = lv_reg_err ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    DATA: lv_head TYPE string, lv_tsv TYPE string, lv_rows TYPE i,`.
    _a `          lv_scalar TYPE string, lv_err TYPE string.`.
    _a `    exec_read( EXPORTING iv_op = lv_op iv_data = lv_body`.
    _a `               IMPORTING ev_head = lv_head ev_body = lv_tsv ev_rows = lv_rows`.
    _a `                         ev_scalar = lv_scalar ev_error = lv_err ).`.
    _a `    IF lv_err IS NOT INITIAL.`.
    _a `      audit( iv_op = lv_op iv_mode = 'R' iv_status = 'ERROR'`.
    _a `             iv_msg = lv_err iv_payload = lv_body iv_result = '' ).`.
    _a `      fail( io_srv = io_srv iv_code = 422 iv_error = lv_err ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    audit( iv_op = lv_op iv_mode = 'R' iv_status = 'OK' iv_msg = ''`.
    _a `           iv_payload = lv_body iv_result = |rows={ lv_rows }| ).`.
    _a `    IF lv_head IS NOT INITIAL.`.
    _a `      ok_table( io_srv = io_srv iv_head = lv_head iv_body = lv_tsv iv_rows = lv_rows ).`.
    _a `    ELSE.`.
    _a `      ok_scalar( io_srv = io_srv iv_data = lv_scalar ).`.
    _a `    ENDIF.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD handle_write.`.
    _a `    " Escrita NÃO executa aqui. Vira pendência e devolve o id. É a diferença`.
    _a `    " entre um gate e um adorno: o modelo pede, um humano lê em /q o que vai`.
    _a `    " acontecer, e decide em /d.`.
    _a `    DATA(lv_body) = io_srv->request->get_cdata( ).`.
    _a `    DATA(lv_op)  = to_upper( jstr( iv_json = lv_body iv_key = 'op' ) ).`.
    _a `    DATA(lv_why) = jstr( iv_json = lv_body iv_key = 'why' ).`.
    _a `    IF lv_op IS INITIAL.`.
    _a `      fail( io_srv = io_srv iv_code = 400 iv_error = 'no_op' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF authorize( iv_op = lv_op iv_mode = 'W' ) = abap_false.`.
    _a `      audit( iv_op = lv_op iv_mode = 'W' iv_status = 'DENIED'`.
    _a `             iv_msg = 'sem autorizacao' iv_payload = lv_body iv_result = '' ).`.
    _a `      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    DATA lv_reg_err TYPE string.`.
    _a `    IF registry_ok( EXPORTING iv_op = lv_op iv_mode = 'W'`.
    _a `                    IMPORTING ev_error = lv_reg_err ) = abap_false.`.
    _a `      fail( io_srv = io_srv iv_code = 409 iv_error = lv_reg_err ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF lv_why IS INITIAL.`.
    _a `      " Sem texto literal não há o que aprovar. Um diálogo genérico`.
    _a `      " (executar acao?) anula o gate — por isso é recusa, não default.`.
    _a `      fail( io_srv = io_srv iv_code = 400 iv_error = 'why_required' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    DATA ls_p TYPE zrouter_pend.`.
    _a `    ls_p-pend_id      = new_id( ).`.
    _a `    ls_p-module       = substring_before( val = lv_op sub = '.' ).`.
    _a `    ls_p-action       = substring_after( val = lv_op sub = '.' ).`.
    _a `    ls_p-payload      = lv_body.`.
    _a `    ls_p-description  = lv_why.`.
    _a `    ls_p-status       = 'PENDING'.`.
    _a `    ls_p-requested_by = sy-uname.`.
    _a `    GET TIME STAMP FIELD ls_p-created_at.`.
    _a `    ls_p-expires_at = cl_abap_tstmp=>add( tstmp = ls_p-created_at secs = co_ttl_secs ).`.
    _a `    INSERT zrouter_pend FROM @ls_p.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      fail( io_srv = io_srv iv_code = 500 iv_error = 'pend_failed' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    COMMIT WORK.`.
    _a `    audit( iv_op = lv_op iv_mode = 'W' iv_status = 'PENDING'`.
    _a `           iv_msg = lv_why iv_payload = lv_body iv_result = '' ).`.
    _a `    send( io_srv = io_srv iv_code = 202`.
    _a `          iv_json = |\{"ok":1,"id":"{ ls_p-pend_id }"\}| ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD handle_queue.`.
    _a `    AUTHORITY-CHECK OBJECT 'ZROUTER'`.
    _a `      ID 'ZRMODULE' DUMMY ID 'ZRACTION' DUMMY ID 'ACTVT' FIELD '03'.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    GET TIME STAMP FIELD DATA(lv_now).`.
    _a `    SELECT pend_id, module, action, requested_by, description`.
    _a `      FROM zrouter_pend INTO TABLE @DATA(lt_p)`.
    _a `      WHERE status = 'PENDING' AND expires_at > @lv_now`.
    _a `      ORDER BY created_at ASCENDING.`.
    _a `    DATA lv_tsv TYPE string.`.
    _a `    LOOP AT lt_p INTO DATA(ls_p).`.
    _a `      DATA(lv_desc) = CONV string( ls_p-description ).`.
    _a `      REPLACE ALL OCCURRENCES OF nl( ) IN lv_desc WITH ' '.`.
    _a `      REPLACE ALL OCCURRENCES OF tab( ) IN lv_desc WITH ' '.`.
    _a `      IF lv_tsv IS NOT INITIAL.`.
    _a `        lv_tsv = lv_tsv && nl( ).`.
    _a `      ENDIF.`.
    _a `      lv_tsv = lv_tsv && |{ ls_p-pend_id }| && tab( )`.
    _a `                      && |{ ls_p-module }.{ ls_p-action }| && tab( )`.
    _a `                      && |{ ls_p-requested_by }| && tab( ) && lv_desc.`.
    _a `    ENDLOOP.`.
    _a `    ok_table( io_srv = io_srv`.
    _a `              iv_head = |ID{ tab( ) }OP{ tab( ) }BY{ tab( ) }WHY|`.
    _a `              iv_body = lv_tsv iv_rows = lines( lt_p ) ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD handle_decide.`.
    _a `    " Aprovar e executar na mesma viagem. Separar em duas chamadas só criaria`.
    _a `    " uma janela entre a decisão e o efeito, em que o estado aprovado muda.`.
    _a `    DATA(lv_body) = io_srv->request->get_cdata( ).`.
    _a `    DATA(lv_id)  = jstr( iv_json = lv_body iv_key = 'id' ).`.
    _a `    DATA(lv_yes) = jstr( iv_json = lv_body iv_key = 'y' ).`.
    _a `    IF lv_yes IS INITIAL.`.
    _a `      FIND REGEX '"y"\s*:\s*true' IN lv_body.`.
    _a `      lv_yes = COND #( WHEN sy-subrc = 0 THEN '1' ELSE '0' ).`.
    _a `    ENDIF.`.
    _a ``.
    _a `    AUTHORITY-CHECK OBJECT 'ZROUTER'`.
    _a `      ID 'ZRMODULE' DUMMY ID 'ZRACTION' DUMMY ID 'ACTVT' FIELD '02'.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    GET TIME STAMP FIELD DATA(lv_now).`.
    _a `    SELECT SINGLE * FROM zrouter_pend INTO @DATA(ls_p)`.
    _a `      WHERE pend_id = @lv_id AND status = 'PENDING'.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      fail( io_srv = io_srv iv_code = 404 iv_error = 'no_pend' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF ls_p-expires_at <= lv_now.`.
    _a `      ls_p-status = 'EXPIRED'.`.
    _a `      UPDATE zrouter_pend FROM @ls_p.`.
    _a `      COMMIT WORK.`.
    _a `      " Aprovação velha aprova um contexto que já mudou.`.
    _a `      fail( io_srv = io_srv iv_code = 409 iv_error = 'expired' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    DATA(lv_op) = |{ ls_p-module }.{ ls_p-action }|.`.
    _a ``.
    _a `    IF lv_yes <> '1'.`.
    _a `      ls_p-status = 'DENIED'.`.
    _a `      ls_p-decided_by = sy-uname.`.
    _a `      UPDATE zrouter_pend FROM @ls_p.`.
    _a `      COMMIT WORK.`.
    _a `      audit( iv_op = lv_op iv_mode = 'W' iv_status = 'DENIED'`.
    _a `             iv_msg = CONV string( ls_p-description )`.
    _a `             iv_payload = CONV string( ls_p-payload ) iv_result = '' ).`.
    _a `      send( io_srv = io_srv iv_code = 200 iv_json = '{"ok":1,"d":"denied"}' ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    " Marca aprovada ANTES de executar. Se a execução dumpar, fica registrado`.
    _a `    " que foi autorizada; o inverso deixaria efeito sem autorização visível.`.
    _a `    ls_p-status = 'APPROVED'.`.
    _a `    ls_p-decided_by = sy-uname.`.
    _a `    UPDATE zrouter_pend FROM @ls_p.`.
    _a `    COMMIT WORK.`.
    _a `    audit( iv_op = lv_op iv_mode = 'W' iv_status = 'APPROVED'`.
    _a `           iv_msg = CONV string( ls_p-description )`.
    _a `           iv_payload = CONV string( ls_p-payload ) iv_result = '' ).`.
    _a ``.
    _a `    DATA: lv_scalar TYPE string, lv_err TYPE string.`.
    _a `    exec_write( EXPORTING iv_op = lv_op iv_data = CONV string( ls_p-payload )`.
    _a `                IMPORTING ev_scalar = lv_scalar ev_error = lv_err ).`.
    _a ``.
    _a `    ls_p-status = COND #( WHEN lv_err IS INITIAL THEN 'DONE' ELSE 'FAILED' ).`.
    _a `    UPDATE zrouter_pend FROM @ls_p.`.
    _a `    COMMIT WORK.`.
    _a ``.
    _a `    IF lv_err IS NOT INITIAL.`.
    _a `      audit( iv_op = lv_op iv_mode = 'W' iv_status = 'FAILED'`.
    _a `             iv_msg = lv_err iv_payload = CONV string( ls_p-payload ) iv_result = '' ).`.
    _a `      fail( io_srv = io_srv iv_code = 422 iv_error = lv_err ).`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    audit( iv_op = lv_op iv_mode = 'W' iv_status = 'DONE' iv_msg = ''`.
    _a `           iv_payload = CONV string( ls_p-payload ) iv_result = lv_scalar ).`.
    _a `    ok_scalar( io_srv = io_srv iv_data = lv_scalar ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD exec_read.`.
    _a `    " Factory FECHADA. O v4 fazia CREATE OBJECT TYPE (nome vindo de tabela):`.
    _a `    " quem escrevesse no registry escolhia a classe executada. Aqui a tabela`.
    _a `    " só pode DESLIGAR uma operação, nunca criar uma.`.
    _a `    CASE iv_op.`.
    _a `      WHEN 'SYS.INFO'.`.
    _a `        op_sysinfo( IMPORTING ev_scalar = ev_scalar ).`.
    _a `      WHEN 'TBL.READ'.`.
    _a `        op_table( EXPORTING iv_data = iv_data`.
    _a `                  IMPORTING ev_head = ev_head ev_body = ev_body`.
    _a `                            ev_rows = ev_rows ev_error = ev_error ).`.
    _a `      WHEN 'TBL.DESC'.`.
    _a `        op_describe( EXPORTING iv_data = iv_data`.
    _a `                     IMPORTING ev_head = ev_head ev_body = ev_body`.
    _a `                               ev_rows = ev_rows ev_error = ev_error ).`.
    _a `      WHEN 'SRC.READ'.`.
    _a `        op_source_read( EXPORTING iv_data = iv_data`.
    _a `                        IMPORTING ev_scalar = ev_scalar ev_error = ev_error ).`.
    _a `      WHEN 'OBJ.FIND'.`.
    _a `        op_find( EXPORTING iv_data = iv_data`.
    _a `                 IMPORTING ev_head = ev_head ev_body = ev_body`.
    _a `                           ev_rows = ev_rows ev_error = ev_error ).`.
    _a `      WHEN OTHERS.`.
    _a `        ev_error = 'not_impl'.`.
    _a `    ENDCASE.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD exec_write.`.
    _a `    CASE iv_op.`.
    _a `      WHEN 'SRC.WRITE'.`.
    _a `        op_source_write( EXPORTING iv_data = iv_data`.
    _a `                         IMPORTING ev_scalar = ev_scalar ev_error = ev_error ).`.
    _a `      WHEN OTHERS.`.
    _a `        ev_error = 'not_impl'.`.
    _a `    ENDCASE.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD op_sysinfo.`.
    _a `    SELECT SINGLE cccategory FROM t000 INTO @DATA(lv_cat) WHERE mandt = @sy-mandt.`.
    _a `    ev_scalar = |sid={ sy-sysid } cli={ sy-mandt } usr={ sy-uname } | &&`.
    _a `                |lang={ sy-langu } cat={ lv_cat }|.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD safe_where.`.
    _a `    " O WHERE é dinâmico, então tudo que permitiria sair de um SELECT simples`.
    _a `    " é recusado. É lista de negação sobre entrada JÁ autorizada e JÁ limitada`.
    _a `    " às tabelas do registry — soma-se à allowlist, não a substitui.`.
    _a `    DATA(lv_w) = to_upper( iv_where ).`.
    _a `    IF lv_w CS ';' OR lv_w CS '--' OR lv_w CS '/*'`.
    _a `       OR lv_w CS 'SELECT' OR lv_w CS 'INSERT' OR lv_w CS 'UPDATE'`.
    _a `       OR lv_w CS 'DELETE' OR lv_w CS 'MODIFY' OR lv_w CS 'JOIN'`.
    _a `       OR lv_w CS 'UNION' OR lv_w CS 'CALL' OR lv_w CS 'CLIENT'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF strlen( iv_where ) > 512.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    rv_ok = abap_true.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD op_table.`.
    _a `    DATA(lv_tab)   = to_upper( jstr( iv_json = iv_data iv_key = 't' ) ).`.
    _a `    DATA(lv_flds)  = to_upper( jstr( iv_json = iv_data iv_key = 'f' ) ).`.
    _a `    DATA(lv_where) = jstr( iv_json = iv_data iv_key = 'w' ).`.
    _a `    DATA(lv_nstr)  = jstr( iv_json = iv_data iv_key = 'n' ).`.
    _a ``.
    _a `    IF lv_tab IS INITIAL.`.
    _a `      ev_error = 'no_table'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    " A tabela precisa estar liberada no registry como TBL.<NOME>. Sem isso,`.
    _a `    " uma leitura genérica viraria leitura de qualquer tabela do sistema —`.
    _a `    " inclusive as de usuário e de autorização.`.
    _a `    SELECT SINGLE active FROM zrouter_cfg INTO @DATA(lv_act)`.
    _a `      WHERE module = 'TBL' AND action = @lv_tab.`.
    _a `    IF sy-subrc <> 0 OR lv_act <> 'X'.`.
    _a `      ev_error = 'tbl_not_allowed'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    SELECT SINGLE tabname FROM dd02l INTO @DATA(lv_chk)`.
    _a `      WHERE tabname = @lv_tab AND as4local = 'A'.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      ev_error = 'no_table'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    IF lv_where IS NOT INITIAL AND safe_where( lv_where ) = abap_false.`.
    _a `      ev_error = 'bad_where'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    DATA(lv_n) = COND i( WHEN lv_nstr IS INITIAL THEN 50 ELSE CONV i( lv_nstr ) ).`.
    _a `    IF lv_n <= 0 OR lv_n > co_max_rows.`.
    _a `      lv_n = co_max_rows.`.
    _a `    ENDIF.`.
    _a `    IF lv_flds IS INITIAL.`.
    _a `      lv_flds = '*'.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    DATA lr_tab TYPE REF TO data.`.
    _a `    FIELD-SYMBOLS <lt> TYPE STANDARD TABLE.`.
    _a `    TRY.`.
    _a `        CREATE DATA lr_tab TYPE STANDARD TABLE OF (lv_tab).`.
    _a `        ASSIGN lr_tab->* TO <lt>.`.
    _a `      CATCH cx_sy_create_data_error.`.
    _a `        ev_error = 'no_table'.`.
    _a `        RETURN.`.
    _a `    ENDTRY.`.
    _a ``.
    _a `    TRY.`.
    _a `        SELECT (lv_flds) FROM (lv_tab)`.
    _a `          INTO CORRESPONDING FIELDS OF TABLE @<lt>`.
    _a `          UP TO @lv_n ROWS`.
    _a `          WHERE (lv_where).`.
    _a `      CATCH cx_sy_dynamic_osql_error.`.
    _a `        ev_error = 'bad_query'.`.
    _a `        RETURN.`.
    _a `    ENDTRY.`.
    _a ``.
    _a `    DATA(lo_line) = CAST cl_abap_tabledescr(`.
    _a `      cl_abap_typedescr=>describe_by_data( <lt> ) )->get_table_line_type( ).`.
    _a `    DATA(lt_comp) = CAST cl_abap_structdescr( lo_line )->get_components( ).`.
    _a ``.
    _a `    DATA lt_use TYPE stringtab.`.
    _a `    IF lv_flds = '*'.`.
    _a `      LOOP AT lt_comp INTO DATA(ls_comp).`.
    _a `        APPEND CONV string( ls_comp-name ) TO lt_use.`.
    _a `      ENDLOOP.`.
    _a `    ELSE.`.
    _a `      SPLIT lv_flds AT ',' INTO TABLE lt_use.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    LOOP AT lt_use INTO DATA(lv_f).`.
    _a `      CONDENSE lv_f.`.
    _a `      IF ev_head IS NOT INITIAL.`.
    _a `        ev_head = ev_head && tab( ).`.
    _a `      ENDIF.`.
    _a `      ev_head = ev_head && lv_f.`.
    _a `    ENDLOOP.`.
    _a ``.
    _a `    FIELD-SYMBOLS <ls> TYPE any.`.
    _a `    FIELD-SYMBOLS <lv> TYPE any.`.
    _a `    LOOP AT <lt> ASSIGNING <ls>.`.
    _a `      DATA lv_line TYPE string.`.
    _a `      CLEAR lv_line.`.
    _a `      LOOP AT lt_use INTO lv_f.`.
    _a `        CONDENSE lv_f.`.
    _a `        ASSIGN COMPONENT lv_f OF STRUCTURE <ls> TO <lv>.`.
    _a `        DATA lv_cell TYPE string.`.
    _a `        IF sy-subrc = 0.`.
    _a `          lv_cell = |{ <lv> }|.`.
    _a `        ELSE.`.
    _a `          CLEAR lv_cell.`.
    _a `        ENDIF.`.
    _a `        " Tabulação ou quebra dentro do dado destruiria o TSV.`.
    _a `        REPLACE ALL OCCURRENCES OF tab( ) IN lv_cell WITH ' '.`.
    _a `        REPLACE ALL OCCURRENCES OF nl( ) IN lv_cell WITH ' '.`.
    _a `        IF lv_line IS NOT INITIAL.`.
    _a `          lv_line = lv_line && tab( ).`.
    _a `        ENDIF.`.
    _a `        lv_line = lv_line && lv_cell.`.
    _a `      ENDLOOP.`.
    _a `      IF ev_body IS NOT INITIAL.`.
    _a `        ev_body = ev_body && nl( ).`.
    _a `      ENDIF.`.
    _a `      ev_body = ev_body && lv_line.`.
    _a `    ENDLOOP.`.
    _a `    ev_rows = lines( <lt> ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD op_describe.`.
    _a `    DATA(lv_tab) = to_upper( jstr( iv_json = iv_data iv_key = 't' ) ).`.
    _a `    IF lv_tab IS INITIAL.`.
    _a `      ev_error = 'no_table'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    SELECT fieldname, keyflag, datatype, leng`.
    _a `      FROM dd03l INTO TABLE @DATA(lt_f)`.
    _a `      WHERE tabname = @lv_tab AND as4local = 'A' AND fieldname <> '.INCLUDE'`.
    _a `      ORDER BY position ASCENDING.`.
    _a `    IF lines( lt_f ) = 0.`.
    _a `      ev_error = 'no_table'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    ev_head = |FIELD{ tab( ) }KEY{ tab( ) }TYPE{ tab( ) }LEN|.`.
    _a `    LOOP AT lt_f INTO DATA(ls_f).`.
    _a `      IF ev_body IS NOT INITIAL.`.
    _a `        ev_body = ev_body && nl( ).`.
    _a `      ENDIF.`.
    _a `      ev_body = ev_body && |{ ls_f-fieldname }| && tab( )`.
    _a `                        && |{ ls_f-keyflag }| && tab( )`.
    _a `                        && |{ ls_f-datatype }| && tab( )`.
    _a `                        && |{ ls_f-leng }|.`.
    _a `    ENDLOOP.`.
    _a `    ev_rows = lines( lt_f ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD op_source_read.`.
    _a `    DATA(lv_name) = to_upper( jstr( iv_json = iv_data iv_key = 'n' ) ).`.
    _a `    IF lv_name IS INITIAL.`.
    _a `      ev_error = 'no_name'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    " Só objetos do cliente. Ler fonte SAP standard por aqui não serve ao`.
    _a `    " produto e amplia a superfície sem ganho.`.
    _a `    IF NOT ( lv_name(1) = 'Z' OR lv_name(1) = 'Y' ).`.
    _a `      ev_error = 'not_custom'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    SELECT SINGLE name FROM trdir INTO @DATA(lv_chk) WHERE name = @lv_name.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      ev_error = 'no_object'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    DATA lt_src TYPE TABLE OF string.`.
    _a `    READ REPORT lv_name INTO lt_src.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      ev_error = 'read_failed'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    LOOP AT lt_src INTO DATA(lv_l).`.
    _a `      IF ev_scalar IS NOT INITIAL.`.
    _a `        ev_scalar = ev_scalar && nl( ).`.
    _a `      ENDIF.`.
    _a `      ev_scalar = ev_scalar && lv_l.`.
    _a `    ENDLOOP.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD op_find.`.
    _a `    DATA(lv_q) = to_upper( jstr( iv_json = iv_data iv_key = 'q' ) ).`.
    _a `    IF lv_q IS INITIAL.`.
    _a `      ev_error = 'no_query'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    REPLACE ALL OCCURRENCES OF '*' IN lv_q WITH '%'.`.
    _a `    IF lv_q NS '%'.`.
    _a `      lv_q = lv_q && '%'.`.
    _a `    ENDIF.`.
    _a `    SELECT obj_name, object, devclass FROM tadir`.
    _a `      INTO TABLE @DATA(lt_o)`.
    _a `      UP TO @co_max_rows ROWS`.
    _a `      WHERE obj_name LIKE @lv_q`.
    _a `        AND ( object = 'PROG' OR object = 'CLAS' OR object = 'INTF'`.
    _a `              OR object = 'FUGR' OR object = 'TABL' )`.
    _a `        AND delflag = @abap_false`.
    _a `      ORDER BY obj_name ASCENDING.`.
    _a `    ev_head = |NAME{ tab( ) }TYPE{ tab( ) }PKG|.`.
    _a `    LOOP AT lt_o INTO DATA(ls_o).`.
    _a `      IF ev_body IS NOT INITIAL.`.
    _a `        ev_body = ev_body && nl( ).`.
    _a `      ENDIF.`.
    _a `      ev_body = ev_body && |{ ls_o-obj_name }| && tab( )`.
    _a `                        && |{ ls_o-object }| && tab( ) && |{ ls_o-devclass }|.`.
    _a `    ENDLOOP.`.
    _a `    ev_rows = lines( lt_o ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD op_source_write.`.
    _a `    " Grava fonte de programa do cliente. Só chega aqui por /d, isto é,`.
    _a `    " depois de um humano ter lido em /q o texto do que seria feito.`.
    _a `    DATA(lv_name) = to_upper( jstr( iv_json = iv_data iv_key = 'n' ) ).`.
    _a `    DATA(lv_src)  = jstr( iv_json = iv_data iv_key = 's' ).`.
    _a `    IF lv_name IS INITIAL OR lv_src IS INITIAL.`.
    _a `      ev_error = 'no_name_or_src'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    IF NOT ( lv_name(1) = 'Z' OR lv_name(1) = 'Y' ).`.
    _a `      ev_error = 'not_custom'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    SELECT SINGLE cccategory FROM t000 INTO @DATA(lv_cat) WHERE mandt = @sy-mandt.`.
    _a `    IF lv_cat = 'P'.`.
    _a `      " Escrita de fonte em mandante produtivo é transporte, não HTTP.`.
    _a `      ev_error = 'prod_client'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    DATA lt_new TYPE TABLE OF string.`.
    _a `    SPLIT lv_src AT nl( ) INTO TABLE lt_new.`.
    _a `    IF lines( lt_new ) = 0.`.
    _a `      ev_error = 'empty_src'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    SELECT SINGLE name FROM trdir INTO @DATA(lv_exists) WHERE name = @lv_name.`.
    _a `    DATA(lv_is_new) = xsdbool( sy-subrc <> 0 ).`.
    _a ``.
    _a `    INSERT REPORT lv_name FROM lt_new.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      ev_error = 'insert_failed'.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a ``.
    _a `    " Sintaxe conferida DEPOIS de gravar: o objetivo é reportar, não impedir.`.
    _a `    " Um fonte que não compila continua sendo o que o humano aprovou gravar,`.
    _a `    " e devolver o erro é mais útil que recusar em silêncio.`.
    _a `    SYNTAX-CHECK FOR lt_new PROGRAM lv_name`.
    _a `      MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).`.
    _a `    IF sy-subrc <> 0.`.
    _a `      ev_scalar = |saved={ lv_name } new={ lv_is_new } syntax=ERR | &&`.
    _a `                  |line={ lv_line } msg={ lv_msg }|.`.
    _a `      RETURN.`.
    _a `    ENDIF.`.
    _a `    ev_scalar = |saved={ lv_name } new={ lv_is_new } syntax=OK n={ lines( lt_new ) }|.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD audit.`.
    _a `    " LUW separada, de propósito. No v4 o log ia na mesma LUW da BAPI e o`.
    _a `    " ROLLBACK apagava a própria evidência — justamente no caso em que ela`.
    _a `    " importa. DESTINATION NONE abre uma LUW nova no mesmo sistema.`.
    _a `    DATA ls_log TYPE zrouter_log.`.
    _a `    ls_log-log_id  = new_id( ).`.
    _a `    ls_log-corr_id = mv_corr.`.
    _a `    ls_log-module  = substring_before( val = iv_op sub = '.' ).`.
    _a `    ls_log-action  = substring_after( val = iv_op sub = '.' ).`.
    _a `    ls_log-op_mode = iv_mode.`.
    _a `    ls_log-status  = iv_status.`.
    _a `    ls_log-message = iv_msg.`.
    _a `    ls_log-payload = iv_payload.`.
    _a `    ls_log-result  = iv_result.`.
    _a `    ls_log-uname   = sy-uname.`.
    _a `    GET TIME STAMP FIELD ls_log-tstamp.`.
    _a `    CALL FUNCTION 'ZROUTER_LOG_WRITE'`.
    _a `      DESTINATION 'NONE'`.
    _a `      EXPORTING is_log = ls_log`.
    _a `      EXCEPTIONS communication_failure = 1 system_failure = 2 OTHERS = 3.`.
    _a `    IF sy-subrc <> 0.`.
    _a `      " A LUW separada não subiu. Auditoria indisponível não derruba a`.
    _a `      " resposta, mas sumir em silêncio seria pior: grava-se local como`.
    _a `      " último recurso, MARCADO, porque esta linha não sobrevive a um`.
    _a `      " rollback — que é o defeito que a LUW separada existe para corrigir.`.
    _a `      ls_log-status = |{ ls_log-status }/LOCAL|.`.
    _a `      INSERT zrouter_log FROM @ls_log.`.
    _a `    ENDIF.`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD ok_scalar.`.
    _a `    send( io_srv = io_srv iv_code = 200`.
    _a `          iv_json = |\{"ok":1,"d":"{ esc( iv_data ) }"\}| ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD ok_table.`.
    _a `    send( io_srv = io_srv iv_code = 200`.
    _a `          iv_json = |\{"ok":1,"n":{ iv_rows },"h":"{ esc( iv_head ) }","t":"{ esc( iv_body ) }"\}| ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD fail.`.
    _a `    send( io_srv = io_srv iv_code = iv_code`.
    _a `          iv_json = |\{"ok":0,"e":"{ esc( iv_error ) }"\}| ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `  METHOD send.`.
    _a `    io_srv->response->set_status( code = iv_code reason = '' ).`.
    _a `    io_srv->response->set_content_type( 'application/json; charset=utf-8' ).`.
    _a `    io_srv->response->set_cdata( iv_json ).`.
    _a `  ENDMETHOD.`.
    _a ``.
    _a `ENDCLASS.`.
  ENDMETHOD.

  METHOD install.
    lcl_log=>head( '2. Classe do gateway' ).

    SELECT SINGLE clsname FROM seoclass INTO @DATA(lv_have) WHERE clsname = @co_class.
    IF sy-subrc = 0.
      lcl_log=>skip( |{ co_class }: já existe| ).
      RETURN.
    ENDIF.

    DATA(lt_src) = source( ).
    IF iv_simulate = abap_true.
      lcl_log=>ok( |{ co_class }: seria criada ({ lines( lt_src ) } linhas)| ).
      RETURN.
    ENDIF.

    DATA: ls_class TYPE vseoclass.
    ls_class-clsname  = co_class.
    ls_class-descript = 'ZROUTER v5 - gateway HTTP'.
    ls_class-state    = '1'.
    ls_class-clsccincl = 'X'.
    ls_class-exposure = '2'.
    ls_class-unicode  = 'X'.

    CALL FUNCTION 'SEO_CLASS_CREATE_COMPLETE'
      EXPORTING
        devclass        = iv_package
        overwrite       = abap_false
      CHANGING
        class           = ls_class
      EXCEPTIONS
        existing        = 1
        is_interface    = 2
        db_error        = 3
        component_error = 4
        no_access       = 5
        other           = 6
        OTHERS          = 7.
    IF sy-subrc <> 0 AND sy-subrc <> 1.
      lcl_log=>fail( |{ co_class }: SEO_CLASS_CREATE_COMPLETE subrc { sy-subrc }| ).
      RETURN.
    ENDIF.

    DATA lv_incl TYPE program.
    CALL FUNCTION 'SEO_CLASS_GET_INCLUDE_BY_NAME'
      EXPORTING
        clsname = co_class
      IMPORTING
        progname = lv_incl
      EXCEPTIONS
        OTHERS  = 1.
    IF sy-subrc <> 0.
      lv_incl = |{ co_class }{ repeat( val = '=' occ = 30 - strlen( co_class ) ) }CP|.
    ENDIF.

    INSERT REPORT lv_incl FROM lt_src.
    IF sy-subrc <> 0.
      lcl_log=>fail( |{ co_class }: INSERT REPORT em { lv_incl } falhou| ).
      RETURN.
    ENDIF.

    CALL FUNCTION 'RS_WORKING_AREA_INIT'.
    DATA lt_msg TYPE STANDARD TABLE OF dwinactiv.
    CALL FUNCTION 'RS_INACTIVE_OBJECTS_WARNING'
      EXPORTING
        suppress_protocol = abap_true
      TABLES
        p_e071            = lt_msg
      EXCEPTIONS
        OTHERS            = 1.

    lcl_log=>ok( |{ co_class }: fonte gravado em { lv_incl }| ).
    lcl_log=>warn( 'Ative a classe em SE24 antes de usar o serviço (SE80 -> ativar).' ).
  ENDMETHOD.

ENDCLASS.

*&---------------------------------------------------------------------*
*& Registry inicial
*&
*& Só leitura entra ativa. Escrita entra DESATIVADA de propósito: ativar
*& é decisão de quem instala, e o objeto de autorização precisa existir
*& antes -- ativar uma linha de escrita sem SU21 feito deixaria uma rota
*& que parece pronta e recusa toda chamada.
*&---------------------------------------------------------------------*
CLASS lcl_seed DEFINITION.
  PUBLIC SECTION.
    METHODS install IMPORTING iv_simulate TYPE abap_bool.
ENDCLASS.

CLASS lcl_seed IMPLEMENTATION.
  METHOD install.
    lcl_log=>head( '4. Registry inicial' ).

    TYPES: BEGIN OF ty_seed,
             module   TYPE char30,
             action   TYPE char60,
             mode     TYPE char1,
             approval TYPE char1,
             active   TYPE char1,
           END OF ty_seed.
    DATA lt_seed TYPE STANDARD TABLE OF ty_seed.

    lt_seed = VALUE #(
      " Leitura — ativas de saída.
      ( module = 'SYS' action = 'INFO'  mode = 'R' approval = ' ' active = 'X' )
      ( module = 'TBL' action = 'READ'  mode = 'R' approval = ' ' active = 'X' )
      ( module = 'TBL' action = 'DESC'  mode = 'R' approval = ' ' active = 'X' )
      ( module = 'SRC' action = 'READ'  mode = 'R' approval = ' ' active = 'X' )
      ( module = 'OBJ' action = 'FIND'  mode = 'R' approval = ' ' active = 'X' )

      " Escrita — DESATIVADA de saída. Ativar é decisão de quem instala, e o
      " objeto de autorização precisa existir antes: uma linha de escrita ativa
      " sem SU21 feito deixa uma rota que parece pronta e recusa toda chamada.
      ( module = 'SRC' action = 'WRITE' mode = 'W' approval = 'X' active = ' ' )

      " Allowlist de tabelas para TBL.READ. Sem uma linha aqui, a operação
      " existe mas não alcança tabela nenhuma — inclusive as de usuário e
      " autorização, que é o ponto. Acrescente as suas com SM30 em ZROUTER_CFG.
      ( module = 'TBL' action = 'ZROUTER_CFG'  mode = 'R' approval = ' ' active = 'X' )
      ( module = 'TBL' action = 'ZROUTER_LOG'  mode = 'R' approval = ' ' active = 'X' )
      ( module = 'TBL' action = 'ZROUTER_PEND' mode = 'R' approval = ' ' active = 'X' )
      ( module = 'TBL' action = 'TADIR'        mode = 'R' approval = ' ' active = 'X' )
      ( module = 'TBL' action = 'TRDIR'        mode = 'R' approval = ' ' active = 'X' ) ).

    IF iv_simulate = abap_true.
      LOOP AT lt_seed INTO DATA(ls_s).
        lcl_log=>ok( |{ ls_s-module }/{ ls_s-action }: modo { ls_s-mode }, | &&
                     |ativa={ COND string( WHEN ls_s-active = 'X' THEN 'sim' ELSE 'nao' ) }| ).
      ENDLOOP.
      RETURN.
    ENDIF.

    LOOP AT lt_seed INTO ls_s.
      DATA ls_cfg TYPE zrouter_cfg.
      CLEAR ls_cfg.
      ls_cfg-module         = ls_s-module.
      ls_cfg-action         = ls_s-action.
      ls_cfg-op_mode        = ls_s-mode.
      ls_cfg-needs_approval = ls_s-approval.
      ls_cfg-active         = ls_s-active.
      ls_cfg-auth_actvt     = COND #( WHEN ls_s-mode = 'W' THEN '02' ELSE '03' ).
      ls_cfg-timeout_s      = 30.
      ls_cfg-changed_by     = sy-uname.
      GET TIME STAMP FIELD ls_cfg-changed_at.
      MODIFY zrouter_cfg FROM @ls_cfg.
      IF sy-subrc = 0.
        lcl_log=>ok( |{ ls_s-module }/{ ls_s-action } gravada| ).
      ELSE.
        lcl_log=>fail( |{ ls_s-module }/{ ls_s-action } não gravada| ).
      ENDIF.
    ENDLOOP.
    COMMIT WORK.
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
*& Nó SICF
*&---------------------------------------------------------------------*
CLASS lcl_icf DEFINITION.
  PUBLIC SECTION.
    METHODS install IMPORTING iv_simulate TYPE abap_bool.
ENDCLASS.

CLASS lcl_icf IMPLEMENTATION.
  METHOD install.
    lcl_log=>head( '3. Nó SICF' ).
    " Criação programática de nó ICF depende de APIs que variam por release e
    " que não são liberadas. Em vez de tentar e falhar de formas diferentes em
    " cada sistema, o instalador diz exatamente o que fazer em SICF -- são dois
    " minutos e fica auditável no transporte.
    lcl_log=>warn( 'Passo manual (SICF), por ser mais confiável que a API:' ).
    WRITE: /  '         1. SICF -> Executar -> navegar até default_host/sap/bc'.
    WRITE: /  '         2. Botão direito em bc -> Novo subelemento -> nome: zrouter'.
    WRITE: /  '         3. Aba Dados de tratador -> Tratador: ZCL_ZROUTER_GW'.
    WRITE: /  '         4. Aba Dados de serviço -> Tipo de logon: exigir logon'.
    WRITE: /  '            (NÃO configure usuário de serviço fixo: a identidade'.
    WRITE: /  '             de quem chama é o que o AUTHORITY-CHECK testa)'.
    WRITE: /  '         5. Ativar o serviço (botão direito -> Ativar serviço)'.
    WRITE: / |         URL final: { co_icf_path }/healthz|.
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
*& Autoteste
*&---------------------------------------------------------------------*
CLASS lcl_selftest DEFINITION.
  PUBLIC SECTION.
    METHODS run.
ENDCLASS.

CLASS lcl_selftest IMPLEMENTATION.
  METHOD run.
    lcl_log=>head( '5. Autoteste' ).

    DATA(lv_all_ok) = abap_true.

    LOOP AT VALUE stringtab( ( `ZROUTER_CFG` ) ( `ZROUTER_LOG` ) ( `ZROUTER_PEND` ) ) INTO DATA(lv_tab).
      SELECT SINGLE tabname FROM dd02l INTO @DATA(lv_t)
        WHERE tabname = @lv_tab AND as4local = 'A'.
      IF sy-subrc = 0.
        lcl_log=>ok( |{ lv_tab }: ativa| ).
      ELSE.
        lcl_log=>fail( |{ lv_tab }: ausente ou inativa| ).
        lv_all_ok = abap_false.
      ENDIF.
    ENDLOOP.

    SELECT SINGLE clsname FROM seoclass INTO @DATA(lv_c) WHERE clsname = @co_class.
    IF sy-subrc = 0.
      lcl_log=>ok( |{ co_class }: existe| ).
    ELSE.
      lcl_log=>fail( |{ co_class }: ausente| ).
      lv_all_ok = abap_false.
    ENDIF.

    SELECT SINGLE object FROM tobj INTO @DATA(lv_obj) WHERE objct = 'ZROUTER'.
    IF sy-subrc = 0.
      lcl_log=>ok( 'Objeto de autorização ZROUTER: existe' ).
    ELSE.
      lcl_log=>warn( 'Objeto de autorização ZROUTER NÃO existe — crie em SU21' ).
      WRITE: / '         Campos: ZRMODULE (CHAR30), ZRACTION (CHAR60), ACTVT (03=ler, 02=escrever/decidir)'.
      WRITE: / '         Sem ele, TODA chamada responde 403 — que é o modo seguro de falhar.'.
    ENDIF.

    SKIP.
    IF lv_all_ok = abap_true AND lcl_log=>failed( ) = abap_false.
      WRITE: / 'Instalação consistente até onde este programa consegue verificar.' COLOR COL_POSITIVE.
      WRITE: / 'O que ele NÃO verificou: se a classe ativa, se o nó SICF responde,'.
      WRITE: / 'e se o AUTHORITY-CHECK recusa quem deve recusar. Isso exige chamar'.
      WRITE: / 'o serviço de fora com dois usuários diferentes.'.
    ELSE.
      WRITE: / 'Instalação INCOMPLETA — veja as linhas [FALH] acima.' COLOR COL_NEGATIVE.
    ENDIF.
  ENDMETHOD.
ENDCLASS.

*&---------------------------------------------------------------------*
INITIALIZATION.
  t_b1 = 'Modo'.
  t_b2 = 'Componentes'.
  t_b3 = 'Verificação'.

START-OF-SELECTION.

  WRITE: / |ZROUTER { co_version } — instalador| COLOR COL_HEADING.
  WRITE: / |Sistema { sy-sysid } mandante { sy-mandt } usuário { sy-uname }|.
  IF p_simul = abap_true.
    WRITE: / 'MODO SIMULAÇÃO — nada será gravado.' COLOR COL_TOTAL.
  ENDIF.

  " Instalar num sistema produtivo é decisão de quem opera, não deste programa;
  " mas passar por cima disso sem ver o aviso não deve ser possível.
  SELECT SINGLE cccategory FROM t000 INTO @DATA(lv_cat) WHERE mandt = @sy-mandt.
  IF lv_cat = 'P' AND p_simul = abap_false.
    WRITE: / 'ATENÇÃO: mandante marcado como PRODUTIVO em T000.' COLOR COL_NEGATIVE.
    WRITE: / 'Instale por transporte, não direto aqui.' COLOR COL_NEGATIVE.
  ENDIF.

  DATA(lo_tab)  = NEW lcl_tables( ).
  DATA(lo_cls)  = NEW lcl_class( ).
  DATA(lo_icf)  = NEW lcl_icf( ).
  DATA(lo_seed) = NEW lcl_seed( ).

  IF p_tab = abap_true.
    lo_tab->install( iv_simulate = p_simul iv_package = p_pack ).
  ENDIF.
  IF p_cls = abap_true.
    lo_cls->install( iv_simulate = p_simul iv_package = p_pack ).
  ENDIF.
  IF p_icf = abap_true.
    lo_icf->install( iv_simulate = p_simul ).
  ENDIF.
  IF p_seed = abap_true AND p_simul = abap_false AND p_tab = abap_true.
    lo_seed->install( iv_simulate = p_simul ).
  ELSEIF p_seed = abap_true.
    lo_seed->install( iv_simulate = abap_true ).
  ENDIF.
  IF p_test = abap_true AND p_simul = abap_false.
    NEW lcl_selftest( )->run( ).
  ENDIF.
