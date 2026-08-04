*&---------------------------------------------------------------------*
*& CLASS ZCL_ZROUTER_GW  —  gateway HTTP do ZROUTER v5
*&
*& FONTE CANÔNICO. O instalador (ZROUTER_V5_INSTALL.abap) carrega uma cópia
*& deste arquivo como tabela de strings; ela é GERADA por build_installer.py,
*& nunca editada à mão. Depois de mexer aqui:
*&     python deploy/zrouter-v5/build_installer.py
*&     python deploy/zrouter-v5/check_sync.py
*&
*& Sem backtick em nenhum ponto do fonte: o gerador delimita cada linha com
*& backtick ao embutir, e um backtick aqui encerraria a string no meio.
*&
*& PROTOCOLO — desenhado para consumo por modelo: poucos tokens, sem virar
*& charada.
*&
*&   POST /r   leitura   {"op":"TBL.READ","t":"MARA","f":"MATNR,MTART","n":50}
*&   POST /w   escrita   {"op":"SRC.WRITE","n":"ZFOO","s":"...","why":"..."}
*&                       -> 202 {"ok":1,"id":"..."}   NÃO executa
*&   GET  /q   fila      pendências aguardando decisão
*&   POST /d   decidir   {"id":"...","y":1}  -> aprova E executa
*&   GET  /healthz
*&
*&   ok escalar: {"ok":1,"d":"..."}
*&   ok tabela:  {"ok":1,"n":3,"h":"MATNR\tMTART","t":"1\tFERT\n2\tROH"}
*&   erro:       {"ok":0,"e":"no_auth"}
*&
*& Por que TSV dentro do JSON e não array de objetos: 50 linhas por 6 colunas
*& em JSON repete os 6 nomes de campo 50 vezes. Em TSV eles aparecem uma vez,
*& no cabeçalho. Medido numa leitura de MARA com 50 linhas e 6 campos:
*& 6.022 caracteres como array de objetos contra 2.674 em TSV — 2,3x menos.
*& A vantagem cresce com mais linhas e nomes de campo mais longos.
*&
*& Os parâmetros ficam no topo do objeto, não aninhados em "d": um nível a
*& menos de chaves em toda requisição.
*&---------------------------------------------------------------------*
CLASS zcl_zrouter_gw DEFINITION PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_http_extension.
    CONSTANTS co_max_body TYPE i VALUE 262144.
    CONSTANTS co_max_rows TYPE i VALUE 200.
    CONSTANTS co_ttl_secs TYPE i VALUE 900.

  PRIVATE SECTION.
    DATA mv_corr TYPE char32.

    METHODS handle_read   IMPORTING io_srv TYPE REF TO if_http_server.
    METHODS handle_write  IMPORTING io_srv TYPE REF TO if_http_server.
    METHODS handle_queue  IMPORTING io_srv TYPE REF TO if_http_server.
    METHODS handle_decide IMPORTING io_srv TYPE REF TO if_http_server.

    METHODS exec_read
      IMPORTING iv_op TYPE string iv_data TYPE string
      EXPORTING ev_head TYPE string ev_body TYPE string
                ev_rows TYPE i ev_scalar TYPE string ev_error TYPE string.

    METHODS exec_write
      IMPORTING iv_op TYPE string iv_data TYPE string
      EXPORTING ev_scalar TYPE string ev_error TYPE string.

    METHODS op_sysinfo EXPORTING ev_scalar TYPE string.
    METHODS op_table
      IMPORTING iv_data TYPE string
      EXPORTING ev_head TYPE string ev_body TYPE string
                ev_rows TYPE i ev_error TYPE string.
    METHODS op_describe
      IMPORTING iv_data TYPE string
      EXPORTING ev_head TYPE string ev_body TYPE string
                ev_rows TYPE i ev_error TYPE string.
    METHODS op_source_read
      IMPORTING iv_data TYPE string
      EXPORTING ev_scalar TYPE string ev_error TYPE string.
    METHODS op_find
      IMPORTING iv_data TYPE string
      EXPORTING ev_head TYPE string ev_body TYPE string
                ev_rows TYPE i ev_error TYPE string.
    METHODS op_source_write
      IMPORTING iv_data TYPE string
      EXPORTING ev_scalar TYPE string ev_error TYPE string.

    METHODS authorize IMPORTING iv_op TYPE string iv_mode TYPE char1
                      RETURNING VALUE(rv_ok) TYPE abap_bool.
    METHODS registry_ok IMPORTING iv_op TYPE string iv_mode TYPE char1
                        EXPORTING ev_error TYPE string
                        RETURNING VALUE(rv_ok) TYPE abap_bool.
    METHODS safe_where IMPORTING iv_where TYPE string
                       RETURNING VALUE(rv_ok) TYPE abap_bool.
    METHODS jstr IMPORTING iv_json TYPE string iv_key TYPE string
                 RETURNING VALUE(rv_val) TYPE string.
    METHODS ok_scalar IMPORTING io_srv TYPE REF TO if_http_server iv_data TYPE string.
    METHODS ok_table IMPORTING io_srv TYPE REF TO if_http_server
                               iv_head TYPE string iv_body TYPE string iv_rows TYPE i.
    METHODS fail IMPORTING io_srv TYPE REF TO if_http_server
                           iv_code TYPE i iv_error TYPE string.
    METHODS send IMPORTING io_srv TYPE REF TO if_http_server
                           iv_code TYPE i iv_json TYPE string.
    METHODS audit IMPORTING iv_op TYPE string iv_mode TYPE char1
                            iv_status TYPE string iv_msg TYPE string
                            iv_payload TYPE string iv_result TYPE string.
    METHODS new_id RETURNING VALUE(rv_id) TYPE char32.
    METHODS esc IMPORTING iv_in TYPE string RETURNING VALUE(rv_out) TYPE string.
    METHODS tab RETURNING VALUE(rv_c) TYPE c.
    METHODS nl RETURNING VALUE(rv_c) TYPE c.

ENDCLASS.


CLASS zcl_zrouter_gw IMPLEMENTATION.

  METHOD tab.
    rv_c = cl_abap_char_utilities=>horizontal_tab.
  ENDMETHOD.

  METHOD nl.
    rv_c = cl_abap_char_utilities=>newline.
  ENDMETHOD.

  METHOD new_id.
    TRY.
        rv_id = cl_system_uuid=>create_uuid_c32_static( ).
      CATCH cx_uuid_error.
        GET TIME STAMP FIELD DATA(lv_ts).
        rv_id = |{ sy-uname }{ lv_ts }|.
    ENDTRY.
  ENDMETHOD.

  METHOD esc.
    rv_out = escape( val = iv_in format = cl_abap_format=>e_json_string ).
  ENDMETHOD.

  METHOD if_http_extension~handle_request.
    mv_corr = new_id( ).
    DATA(lv_path) = to_lower( server->request->get_header_field( '~path_info' ) ).
    DATA(lv_meth) = to_upper( server->request->get_method( ) ).

    " Teto antes de qualquer parse: POST sem limite derruba o work process.
    DATA(lv_len) = CONV i( server->request->get_header_field( 'content-length' ) ).
    IF lv_len > co_max_body.
      fail( io_srv = server iv_code = 413 iv_error = 'too_big' ).
      RETURN.
    ENDIF.

    CASE lv_path.
      WHEN '/r'.
        IF lv_meth <> 'POST'.
          fail( io_srv = server iv_code = 405 iv_error = 'post_only' ).
          RETURN.
        ENDIF.
        handle_read( server ).
      WHEN '/w'.
        IF lv_meth <> 'POST'.
          fail( io_srv = server iv_code = 405 iv_error = 'post_only' ).
          RETURN.
        ENDIF.
        handle_write( server ).
      WHEN '/q'.
        handle_queue( server ).
      WHEN '/d'.
        IF lv_meth <> 'POST'.
          fail( io_srv = server iv_code = 405 iv_error = 'post_only' ).
          RETURN.
        ENDIF.
        handle_decide( server ).
      WHEN '/healthz'.
        send( io_srv = server iv_code = 200
              iv_json = |\{"ok":1,"v":"5.0.0","sid":"{ sy-sysid }","cli":"{ sy-mandt }"\}| ).
      WHEN OTHERS.
        " 404 explícito. Nunca 200 com corpo vazio: silêncio lido como
        " sucesso é o defeito que o consumidor registrou como P1-7.
        fail( io_srv = server iv_code = 404 iv_error = 'no_route' ).
    ENDCASE.
  ENDMETHOD.

  METHOD jstr.
    " Extrator para chaves de topo. O corpo já passou pelo teto de tamanho;
    " aqui só se busca o valor de uma chave conhecida, nunca se avalia nada.
    DATA lv_val TYPE string.
    FIND REGEX |"{ iv_key }"\\s*:\\s*"([^"\\\\]*(\\\\.[^"\\\\]*)*)"|
      IN iv_json SUBMATCHES lv_val.
    IF sy-subrc <> 0.
      " Aceita também número sem aspas: {"n":50}
      FIND REGEX |"{ iv_key }"\\s*:\\s*(-?[0-9]+)| IN iv_json SUBMATCHES lv_val.
      IF sy-subrc <> 0.
        CLEAR rv_val.
        RETURN.
      ENDIF.
      rv_val = lv_val.
      RETURN.
    ENDIF.
    REPLACE ALL OCCURRENCES OF '\"' IN lv_val WITH '"'.
    REPLACE ALL OCCURRENCES OF '\n' IN lv_val WITH cl_abap_char_utilities=>newline.
    REPLACE ALL OCCURRENCES OF '\t' IN lv_val WITH cl_abap_char_utilities=>horizontal_tab.
    REPLACE ALL OCCURRENCES OF '\\' IN lv_val WITH '\'.
    rv_val = lv_val.
  ENDMETHOD.

  METHOD authorize.
    " auth-check-first: nada acontece antes disto.
    DATA(lv_actvt) = COND char2( WHEN iv_mode = 'W' THEN '02' ELSE '03' ).
    DATA(lv_mod) = substring_before( val = iv_op sub = '.' ).
    DATA(lv_act) = substring_after( val = iv_op sub = '.' ).
    IF lv_mod IS INITIAL.
      lv_mod = iv_op.
    ENDIF.
    AUTHORITY-CHECK OBJECT 'ZROUTER'
      ID 'ZRMODULE' FIELD lv_mod
      ID 'ZRACTION' FIELD lv_act
      ID 'ACTVT'    FIELD lv_actvt.
    rv_ok = xsdbool( sy-subrc = 0 ).
  ENDMETHOD.

  METHOD registry_ok.
    DATA(lv_mod) = substring_before( val = iv_op sub = '.' ).
    DATA(lv_act) = substring_after( val = iv_op sub = '.' ).
    SELECT SINGLE op_mode, active FROM zrouter_cfg
      INTO @DATA(ls_cfg)
      WHERE module = @lv_mod AND action = @lv_act.
    IF sy-subrc <> 0.
      ev_error = 'no_op'.
      RETURN.
    ENDIF.
    IF ls_cfg-active <> 'X'.
      ev_error = 'off'.
      RETURN.
    ENDIF.
    " O ponto que sustenta o invariante do consumidor: a rota de leitura
    " recusa linha marcada como escrita mesmo com o usuário autorizado, e a
    " de escrita recusa linha de leitura — para que /w não vire atalho de /r
    " sem gate.
    IF iv_mode = 'R' AND ls_cfg-op_mode <> 'R'.
      ev_error = 'write_op'.
      RETURN.
    ENDIF.
    IF iv_mode = 'W' AND ls_cfg-op_mode <> 'W'.
      ev_error = 'read_op'.
      RETURN.
    ENDIF.
    rv_ok = abap_true.
  ENDMETHOD.

  METHOD handle_read.
    DATA(lv_body) = io_srv->request->get_cdata( ).
    DATA(lv_op) = to_upper( jstr( iv_json = lv_body iv_key = 'op' ) ).
    IF lv_op IS INITIAL.
      fail( io_srv = io_srv iv_code = 400 iv_error = 'no_op' ).
      RETURN.
    ENDIF.
    IF authorize( iv_op = lv_op iv_mode = 'R' ) = abap_false.
      audit( iv_op = lv_op iv_mode = 'R' iv_status = 'DENIED'
             iv_msg = 'sem autorizacao' iv_payload = lv_body iv_result = '' ).
      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).
      RETURN.
    ENDIF.
    DATA lv_reg_err TYPE string.
    IF registry_ok( EXPORTING iv_op = lv_op iv_mode = 'R'
                    IMPORTING ev_error = lv_reg_err ) = abap_false.
      fail( io_srv = io_srv iv_code = 409 iv_error = lv_reg_err ).
      RETURN.
    ENDIF.

    DATA: lv_head TYPE string, lv_tsv TYPE string, lv_rows TYPE i,
          lv_scalar TYPE string, lv_err TYPE string.
    exec_read( EXPORTING iv_op = lv_op iv_data = lv_body
               IMPORTING ev_head = lv_head ev_body = lv_tsv ev_rows = lv_rows
                         ev_scalar = lv_scalar ev_error = lv_err ).
    IF lv_err IS NOT INITIAL.
      audit( iv_op = lv_op iv_mode = 'R' iv_status = 'ERROR'
             iv_msg = lv_err iv_payload = lv_body iv_result = '' ).
      fail( io_srv = io_srv iv_code = 422 iv_error = lv_err ).
      RETURN.
    ENDIF.
    audit( iv_op = lv_op iv_mode = 'R' iv_status = 'OK' iv_msg = ''
           iv_payload = lv_body iv_result = |rows={ lv_rows }| ).
    IF lv_head IS NOT INITIAL.
      ok_table( io_srv = io_srv iv_head = lv_head iv_body = lv_tsv iv_rows = lv_rows ).
    ELSE.
      ok_scalar( io_srv = io_srv iv_data = lv_scalar ).
    ENDIF.
  ENDMETHOD.

  METHOD handle_write.
    " Escrita NÃO executa aqui. Vira pendência e devolve o id. É a diferença
    " entre um gate e um adorno: o modelo pede, um humano lê em /q o que vai
    " acontecer, e decide em /d.
    DATA(lv_body) = io_srv->request->get_cdata( ).
    DATA(lv_op)  = to_upper( jstr( iv_json = lv_body iv_key = 'op' ) ).
    DATA(lv_why) = jstr( iv_json = lv_body iv_key = 'why' ).
    IF lv_op IS INITIAL.
      fail( io_srv = io_srv iv_code = 400 iv_error = 'no_op' ).
      RETURN.
    ENDIF.
    IF authorize( iv_op = lv_op iv_mode = 'W' ) = abap_false.
      audit( iv_op = lv_op iv_mode = 'W' iv_status = 'DENIED'
             iv_msg = 'sem autorizacao' iv_payload = lv_body iv_result = '' ).
      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).
      RETURN.
    ENDIF.
    DATA lv_reg_err TYPE string.
    IF registry_ok( EXPORTING iv_op = lv_op iv_mode = 'W'
                    IMPORTING ev_error = lv_reg_err ) = abap_false.
      fail( io_srv = io_srv iv_code = 409 iv_error = lv_reg_err ).
      RETURN.
    ENDIF.
    IF lv_why IS INITIAL.
      " Sem texto literal não há o que aprovar. Um diálogo genérico
      " (executar acao?) anula o gate — por isso é recusa, não default.
      fail( io_srv = io_srv iv_code = 400 iv_error = 'why_required' ).
      RETURN.
    ENDIF.

    DATA ls_p TYPE zrouter_pend.
    ls_p-pend_id      = new_id( ).
    ls_p-module       = substring_before( val = lv_op sub = '.' ).
    ls_p-action       = substring_after( val = lv_op sub = '.' ).
    ls_p-payload      = lv_body.
    ls_p-description  = lv_why.
    ls_p-status       = 'PENDING'.
    ls_p-requested_by = sy-uname.
    GET TIME STAMP FIELD ls_p-created_at.
    ls_p-expires_at = cl_abap_tstmp=>add( tstmp = ls_p-created_at secs = co_ttl_secs ).
    INSERT zrouter_pend FROM @ls_p.
    IF sy-subrc <> 0.
      fail( io_srv = io_srv iv_code = 500 iv_error = 'pend_failed' ).
      RETURN.
    ENDIF.
    COMMIT WORK.
    audit( iv_op = lv_op iv_mode = 'W' iv_status = 'PENDING'
           iv_msg = lv_why iv_payload = lv_body iv_result = '' ).
    send( io_srv = io_srv iv_code = 202
          iv_json = |\{"ok":1,"id":"{ ls_p-pend_id }"\}| ).
  ENDMETHOD.

  METHOD handle_queue.
    AUTHORITY-CHECK OBJECT 'ZROUTER'
      ID 'ZRMODULE' DUMMY ID 'ZRACTION' DUMMY ID 'ACTVT' FIELD '03'.
    IF sy-subrc <> 0.
      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).
      RETURN.
    ENDIF.
    GET TIME STAMP FIELD DATA(lv_now).
    SELECT pend_id, module, action, requested_by, description
      FROM zrouter_pend INTO TABLE @DATA(lt_p)
      WHERE status = 'PENDING' AND expires_at > @lv_now
      ORDER BY created_at ASCENDING.
    DATA lv_tsv TYPE string.
    LOOP AT lt_p INTO DATA(ls_p).
      DATA(lv_desc) = CONV string( ls_p-description ).
      REPLACE ALL OCCURRENCES OF nl( ) IN lv_desc WITH ' '.
      REPLACE ALL OCCURRENCES OF tab( ) IN lv_desc WITH ' '.
      IF lv_tsv IS NOT INITIAL.
        lv_tsv = lv_tsv && nl( ).
      ENDIF.
      lv_tsv = lv_tsv && |{ ls_p-pend_id }| && tab( )
                      && |{ ls_p-module }.{ ls_p-action }| && tab( )
                      && |{ ls_p-requested_by }| && tab( ) && lv_desc.
    ENDLOOP.
    ok_table( io_srv = io_srv
              iv_head = |ID{ tab( ) }OP{ tab( ) }BY{ tab( ) }WHY|
              iv_body = lv_tsv iv_rows = lines( lt_p ) ).
  ENDMETHOD.

  METHOD handle_decide.
    " Aprovar e executar na mesma viagem. Separar em duas chamadas só criaria
    " uma janela entre a decisão e o efeito, em que o estado aprovado muda.
    DATA(lv_body) = io_srv->request->get_cdata( ).
    DATA(lv_id)  = jstr( iv_json = lv_body iv_key = 'id' ).
    DATA(lv_yes) = jstr( iv_json = lv_body iv_key = 'y' ).
    IF lv_yes IS INITIAL.
      FIND REGEX '"y"\s*:\s*true' IN lv_body.
      lv_yes = COND #( WHEN sy-subrc = 0 THEN '1' ELSE '0' ).
    ENDIF.

    AUTHORITY-CHECK OBJECT 'ZROUTER'
      ID 'ZRMODULE' DUMMY ID 'ZRACTION' DUMMY ID 'ACTVT' FIELD '02'.
    IF sy-subrc <> 0.
      fail( io_srv = io_srv iv_code = 403 iv_error = 'no_auth' ).
      RETURN.
    ENDIF.

    GET TIME STAMP FIELD DATA(lv_now).
    SELECT SINGLE * FROM zrouter_pend INTO @DATA(ls_p)
      WHERE pend_id = @lv_id AND status = 'PENDING'.
    IF sy-subrc <> 0.
      fail( io_srv = io_srv iv_code = 404 iv_error = 'no_pend' ).
      RETURN.
    ENDIF.
    IF ls_p-expires_at <= lv_now.
      ls_p-status = 'EXPIRED'.
      UPDATE zrouter_pend FROM @ls_p.
      COMMIT WORK.
      " Aprovação velha aprova um contexto que já mudou.
      fail( io_srv = io_srv iv_code = 409 iv_error = 'expired' ).
      RETURN.
    ENDIF.

    DATA(lv_op) = |{ ls_p-module }.{ ls_p-action }|.

    IF lv_yes <> '1'.
      ls_p-status = 'DENIED'.
      ls_p-decided_by = sy-uname.
      UPDATE zrouter_pend FROM @ls_p.
      COMMIT WORK.
      audit( iv_op = lv_op iv_mode = 'W' iv_status = 'DENIED'
             iv_msg = CONV string( ls_p-description )
             iv_payload = CONV string( ls_p-payload ) iv_result = '' ).
      send( io_srv = io_srv iv_code = 200 iv_json = '{"ok":1,"d":"denied"}' ).
      RETURN.
    ENDIF.

    " Marca aprovada ANTES de executar. Se a execução dumpar, fica registrado
    " que foi autorizada; o inverso deixaria efeito sem autorização visível.
    ls_p-status = 'APPROVED'.
    ls_p-decided_by = sy-uname.
    UPDATE zrouter_pend FROM @ls_p.
    COMMIT WORK.
    audit( iv_op = lv_op iv_mode = 'W' iv_status = 'APPROVED'
           iv_msg = CONV string( ls_p-description )
           iv_payload = CONV string( ls_p-payload ) iv_result = '' ).

    DATA: lv_scalar TYPE string, lv_err TYPE string.
    exec_write( EXPORTING iv_op = lv_op iv_data = CONV string( ls_p-payload )
                IMPORTING ev_scalar = lv_scalar ev_error = lv_err ).

    ls_p-status = COND #( WHEN lv_err IS INITIAL THEN 'DONE' ELSE 'FAILED' ).
    UPDATE zrouter_pend FROM @ls_p.
    COMMIT WORK.

    IF lv_err IS NOT INITIAL.
      audit( iv_op = lv_op iv_mode = 'W' iv_status = 'FAILED'
             iv_msg = lv_err iv_payload = CONV string( ls_p-payload ) iv_result = '' ).
      fail( io_srv = io_srv iv_code = 422 iv_error = lv_err ).
      RETURN.
    ENDIF.
    audit( iv_op = lv_op iv_mode = 'W' iv_status = 'DONE' iv_msg = ''
           iv_payload = CONV string( ls_p-payload ) iv_result = lv_scalar ).
    ok_scalar( io_srv = io_srv iv_data = lv_scalar ).
  ENDMETHOD.

  METHOD exec_read.
    " Factory FECHADA. O v4 fazia CREATE OBJECT TYPE (nome vindo de tabela):
    " quem escrevesse no registry escolhia a classe executada. Aqui a tabela
    " só pode DESLIGAR uma operação, nunca criar uma.
    CASE iv_op.
      WHEN 'SYS.INFO'.
        op_sysinfo( IMPORTING ev_scalar = ev_scalar ).
      WHEN 'TBL.READ'.
        op_table( EXPORTING iv_data = iv_data
                  IMPORTING ev_head = ev_head ev_body = ev_body
                            ev_rows = ev_rows ev_error = ev_error ).
      WHEN 'TBL.DESC'.
        op_describe( EXPORTING iv_data = iv_data
                     IMPORTING ev_head = ev_head ev_body = ev_body
                               ev_rows = ev_rows ev_error = ev_error ).
      WHEN 'SRC.READ'.
        op_source_read( EXPORTING iv_data = iv_data
                        IMPORTING ev_scalar = ev_scalar ev_error = ev_error ).
      WHEN 'OBJ.FIND'.
        op_find( EXPORTING iv_data = iv_data
                 IMPORTING ev_head = ev_head ev_body = ev_body
                           ev_rows = ev_rows ev_error = ev_error ).
      WHEN OTHERS.
        ev_error = 'not_impl'.
    ENDCASE.
  ENDMETHOD.

  METHOD exec_write.
    CASE iv_op.
      WHEN 'SRC.WRITE'.
        op_source_write( EXPORTING iv_data = iv_data
                         IMPORTING ev_scalar = ev_scalar ev_error = ev_error ).
      WHEN OTHERS.
        ev_error = 'not_impl'.
    ENDCASE.
  ENDMETHOD.

  METHOD op_sysinfo.
    SELECT SINGLE cccategory FROM t000 INTO @DATA(lv_cat) WHERE mandt = @sy-mandt.
    ev_scalar = |sid={ sy-sysid } cli={ sy-mandt } usr={ sy-uname } | &&
                |lang={ sy-langu } cat={ lv_cat }|.
  ENDMETHOD.

  METHOD safe_where.
    " O WHERE é dinâmico, então tudo que permitiria sair de um SELECT simples
    " é recusado. É lista de negação sobre entrada JÁ autorizada e JÁ limitada
    " às tabelas do registry — soma-se à allowlist, não a substitui.
    DATA(lv_w) = to_upper( iv_where ).
    IF lv_w CS ';' OR lv_w CS '--' OR lv_w CS '/*'
       OR lv_w CS 'SELECT' OR lv_w CS 'INSERT' OR lv_w CS 'UPDATE'
       OR lv_w CS 'DELETE' OR lv_w CS 'MODIFY' OR lv_w CS 'JOIN'
       OR lv_w CS 'UNION' OR lv_w CS 'CALL' OR lv_w CS 'CLIENT'.
      RETURN.
    ENDIF.
    IF strlen( iv_where ) > 512.
      RETURN.
    ENDIF.
    rv_ok = abap_true.
  ENDMETHOD.

  METHOD op_table.
    DATA(lv_tab)   = to_upper( jstr( iv_json = iv_data iv_key = 't' ) ).
    DATA(lv_flds)  = to_upper( jstr( iv_json = iv_data iv_key = 'f' ) ).
    DATA(lv_where) = jstr( iv_json = iv_data iv_key = 'w' ).
    DATA(lv_nstr)  = jstr( iv_json = iv_data iv_key = 'n' ).

    IF lv_tab IS INITIAL.
      ev_error = 'no_table'.
      RETURN.
    ENDIF.

    " A tabela precisa estar liberada no registry como TBL.<NOME>. Sem isso,
    " uma leitura genérica viraria leitura de qualquer tabela do sistema —
    " inclusive as de usuário e de autorização.
    SELECT SINGLE active FROM zrouter_cfg INTO @DATA(lv_act)
      WHERE module = 'TBL' AND action = @lv_tab.
    IF sy-subrc <> 0 OR lv_act <> 'X'.
      ev_error = 'tbl_not_allowed'.
      RETURN.
    ENDIF.

    SELECT SINGLE tabname FROM dd02l INTO @DATA(lv_chk)
      WHERE tabname = @lv_tab AND as4local = 'A'.
    IF sy-subrc <> 0.
      ev_error = 'no_table'.
      RETURN.
    ENDIF.

    IF lv_where IS NOT INITIAL AND safe_where( lv_where ) = abap_false.
      ev_error = 'bad_where'.
      RETURN.
    ENDIF.

    DATA(lv_n) = COND i( WHEN lv_nstr IS INITIAL THEN 50 ELSE CONV i( lv_nstr ) ).
    IF lv_n <= 0 OR lv_n > co_max_rows.
      lv_n = co_max_rows.
    ENDIF.
    IF lv_flds IS INITIAL.
      lv_flds = '*'.
    ENDIF.

    DATA lr_tab TYPE REF TO data.
    FIELD-SYMBOLS <lt> TYPE STANDARD TABLE.
    TRY.
        CREATE DATA lr_tab TYPE STANDARD TABLE OF (lv_tab).
        ASSIGN lr_tab->* TO <lt>.
      CATCH cx_sy_create_data_error.
        ev_error = 'no_table'.
        RETURN.
    ENDTRY.

    TRY.
        SELECT (lv_flds) FROM (lv_tab)
          INTO CORRESPONDING FIELDS OF TABLE @<lt>
          UP TO @lv_n ROWS
          WHERE (lv_where).
      CATCH cx_sy_dynamic_osql_error.
        ev_error = 'bad_query'.
        RETURN.
    ENDTRY.

    DATA(lo_line) = CAST cl_abap_tabledescr(
      cl_abap_typedescr=>describe_by_data( <lt> ) )->get_table_line_type( ).
    DATA(lt_comp) = CAST cl_abap_structdescr( lo_line )->get_components( ).

    DATA lt_use TYPE stringtab.
    IF lv_flds = '*'.
      LOOP AT lt_comp INTO DATA(ls_comp).
        APPEND CONV string( ls_comp-name ) TO lt_use.
      ENDLOOP.
    ELSE.
      SPLIT lv_flds AT ',' INTO TABLE lt_use.
    ENDIF.

    LOOP AT lt_use INTO DATA(lv_f).
      CONDENSE lv_f.
      IF ev_head IS NOT INITIAL.
        ev_head = ev_head && tab( ).
      ENDIF.
      ev_head = ev_head && lv_f.
    ENDLOOP.

    FIELD-SYMBOLS <ls> TYPE any.
    FIELD-SYMBOLS <lv> TYPE any.
    LOOP AT <lt> ASSIGNING <ls>.
      DATA lv_line TYPE string.
      CLEAR lv_line.
      LOOP AT lt_use INTO lv_f.
        CONDENSE lv_f.
        ASSIGN COMPONENT lv_f OF STRUCTURE <ls> TO <lv>.
        DATA lv_cell TYPE string.
        IF sy-subrc = 0.
          lv_cell = |{ <lv> }|.
        ELSE.
          CLEAR lv_cell.
        ENDIF.
        " Tabulação ou quebra dentro do dado destruiria o TSV.
        REPLACE ALL OCCURRENCES OF tab( ) IN lv_cell WITH ' '.
        REPLACE ALL OCCURRENCES OF nl( ) IN lv_cell WITH ' '.
        IF lv_line IS NOT INITIAL.
          lv_line = lv_line && tab( ).
        ENDIF.
        lv_line = lv_line && lv_cell.
      ENDLOOP.
      IF ev_body IS NOT INITIAL.
        ev_body = ev_body && nl( ).
      ENDIF.
      ev_body = ev_body && lv_line.
    ENDLOOP.
    ev_rows = lines( <lt> ).
  ENDMETHOD.

  METHOD op_describe.
    DATA(lv_tab) = to_upper( jstr( iv_json = iv_data iv_key = 't' ) ).
    IF lv_tab IS INITIAL.
      ev_error = 'no_table'.
      RETURN.
    ENDIF.
    SELECT fieldname, keyflag, datatype, leng
      FROM dd03l INTO TABLE @DATA(lt_f)
      WHERE tabname = @lv_tab AND as4local = 'A' AND fieldname <> '.INCLUDE'
      ORDER BY position ASCENDING.
    IF lines( lt_f ) = 0.
      ev_error = 'no_table'.
      RETURN.
    ENDIF.
    ev_head = |FIELD{ tab( ) }KEY{ tab( ) }TYPE{ tab( ) }LEN|.
    LOOP AT lt_f INTO DATA(ls_f).
      IF ev_body IS NOT INITIAL.
        ev_body = ev_body && nl( ).
      ENDIF.
      ev_body = ev_body && |{ ls_f-fieldname }| && tab( )
                        && |{ ls_f-keyflag }| && tab( )
                        && |{ ls_f-datatype }| && tab( )
                        && |{ ls_f-leng }|.
    ENDLOOP.
    ev_rows = lines( lt_f ).
  ENDMETHOD.

  METHOD op_source_read.
    DATA(lv_name) = to_upper( jstr( iv_json = iv_data iv_key = 'n' ) ).
    IF lv_name IS INITIAL.
      ev_error = 'no_name'.
      RETURN.
    ENDIF.
    " Só objetos do cliente. Ler fonte SAP standard por aqui não serve ao
    " produto e amplia a superfície sem ganho.
    IF NOT ( lv_name(1) = 'Z' OR lv_name(1) = 'Y' ).
      ev_error = 'not_custom'.
      RETURN.
    ENDIF.
    SELECT SINGLE name FROM trdir INTO @DATA(lv_chk) WHERE name = @lv_name.
    IF sy-subrc <> 0.
      ev_error = 'no_object'.
      RETURN.
    ENDIF.
    DATA lt_src TYPE TABLE OF string.
    READ REPORT lv_name INTO lt_src.
    IF sy-subrc <> 0.
      ev_error = 'read_failed'.
      RETURN.
    ENDIF.
    LOOP AT lt_src INTO DATA(lv_l).
      IF ev_scalar IS NOT INITIAL.
        ev_scalar = ev_scalar && nl( ).
      ENDIF.
      ev_scalar = ev_scalar && lv_l.
    ENDLOOP.
  ENDMETHOD.

  METHOD op_find.
    DATA(lv_q) = to_upper( jstr( iv_json = iv_data iv_key = 'q' ) ).
    IF lv_q IS INITIAL.
      ev_error = 'no_query'.
      RETURN.
    ENDIF.
    REPLACE ALL OCCURRENCES OF '*' IN lv_q WITH '%'.
    IF lv_q NS '%'.
      lv_q = lv_q && '%'.
    ENDIF.
    SELECT obj_name, object, devclass FROM tadir
      INTO TABLE @DATA(lt_o)
      UP TO @co_max_rows ROWS
      WHERE obj_name LIKE @lv_q
        AND ( object = 'PROG' OR object = 'CLAS' OR object = 'INTF'
              OR object = 'FUGR' OR object = 'TABL' )
        AND delflag = @abap_false
      ORDER BY obj_name ASCENDING.
    ev_head = |NAME{ tab( ) }TYPE{ tab( ) }PKG|.
    LOOP AT lt_o INTO DATA(ls_o).
      IF ev_body IS NOT INITIAL.
        ev_body = ev_body && nl( ).
      ENDIF.
      ev_body = ev_body && |{ ls_o-obj_name }| && tab( )
                        && |{ ls_o-object }| && tab( ) && |{ ls_o-devclass }|.
    ENDLOOP.
    ev_rows = lines( lt_o ).
  ENDMETHOD.

  METHOD op_source_write.
    " Grava fonte de programa do cliente. Só chega aqui por /d, isto é,
    " depois de um humano ter lido em /q o texto do que seria feito.
    DATA(lv_name) = to_upper( jstr( iv_json = iv_data iv_key = 'n' ) ).
    DATA(lv_src)  = jstr( iv_json = iv_data iv_key = 's' ).
    IF lv_name IS INITIAL OR lv_src IS INITIAL.
      ev_error = 'no_name_or_src'.
      RETURN.
    ENDIF.
    IF NOT ( lv_name(1) = 'Z' OR lv_name(1) = 'Y' ).
      ev_error = 'not_custom'.
      RETURN.
    ENDIF.
    SELECT SINGLE cccategory FROM t000 INTO @DATA(lv_cat) WHERE mandt = @sy-mandt.
    IF lv_cat = 'P'.
      " Escrita de fonte em mandante produtivo é transporte, não HTTP.
      ev_error = 'prod_client'.
      RETURN.
    ENDIF.

    DATA lt_new TYPE TABLE OF string.
    SPLIT lv_src AT nl( ) INTO TABLE lt_new.
    IF lines( lt_new ) = 0.
      ev_error = 'empty_src'.
      RETURN.
    ENDIF.

    SELECT SINGLE name FROM trdir INTO @DATA(lv_exists) WHERE name = @lv_name.
    DATA(lv_is_new) = xsdbool( sy-subrc <> 0 ).

    INSERT REPORT lv_name FROM lt_new.
    IF sy-subrc <> 0.
      ev_error = 'insert_failed'.
      RETURN.
    ENDIF.

    " Sintaxe conferida DEPOIS de gravar: o objetivo é reportar, não impedir.
    " Um fonte que não compila continua sendo o que o humano aprovou gravar,
    " e devolver o erro é mais útil que recusar em silêncio.
    SYNTAX-CHECK FOR lt_new PROGRAM lv_name
      MESSAGE DATA(lv_msg) LINE DATA(lv_line) WORD DATA(lv_word).
    IF sy-subrc <> 0.
      ev_scalar = |saved={ lv_name } new={ lv_is_new } syntax=ERR | &&
                  |line={ lv_line } msg={ lv_msg }|.
      RETURN.
    ENDIF.
    ev_scalar = |saved={ lv_name } new={ lv_is_new } syntax=OK n={ lines( lt_new ) }|.
  ENDMETHOD.

  METHOD audit.
    " LUW separada, de propósito. No v4 o log ia na mesma LUW da BAPI e o
    " ROLLBACK apagava a própria evidência — justamente no caso em que ela
    " importa. DESTINATION NONE abre uma LUW nova no mesmo sistema.
    DATA ls_log TYPE zrouter_log.
    ls_log-log_id  = new_id( ).
    ls_log-corr_id = mv_corr.
    ls_log-module  = substring_before( val = iv_op sub = '.' ).
    ls_log-action  = substring_after( val = iv_op sub = '.' ).
    ls_log-op_mode = iv_mode.
    ls_log-status  = iv_status.
    ls_log-message = iv_msg.
    ls_log-payload = iv_payload.
    ls_log-result  = iv_result.
    ls_log-uname   = sy-uname.
    GET TIME STAMP FIELD ls_log-tstamp.
    CALL FUNCTION 'ZROUTER_LOG_WRITE'
      DESTINATION 'NONE'
      EXPORTING is_log = ls_log
      EXCEPTIONS communication_failure = 1 system_failure = 2 OTHERS = 3.
    IF sy-subrc <> 0.
      " A LUW separada não subiu. Auditoria indisponível não derruba a
      " resposta, mas sumir em silêncio seria pior: grava-se local como
      " último recurso, MARCADO, porque esta linha não sobrevive a um
      " rollback — que é o defeito que a LUW separada existe para corrigir.
      ls_log-status = |{ ls_log-status }/LOCAL|.
      INSERT zrouter_log FROM @ls_log.
    ENDIF.
  ENDMETHOD.

  METHOD ok_scalar.
    send( io_srv = io_srv iv_code = 200
          iv_json = |\{"ok":1,"d":"{ esc( iv_data ) }"\}| ).
  ENDMETHOD.

  METHOD ok_table.
    send( io_srv = io_srv iv_code = 200
          iv_json = |\{"ok":1,"n":{ iv_rows },"h":"{ esc( iv_head ) }","t":"{ esc( iv_body ) }"\}| ).
  ENDMETHOD.

  METHOD fail.
    send( io_srv = io_srv iv_code = iv_code
          iv_json = |\{"ok":0,"e":"{ esc( iv_error ) }"\}| ).
  ENDMETHOD.

  METHOD send.
    io_srv->response->set_status( code = iv_code reason = '' ).
    io_srv->response->set_content_type( 'application/json; charset=utf-8' ).
    io_srv->response->set_cdata( iv_json ).
  ENDMETHOD.

ENDCLASS.
