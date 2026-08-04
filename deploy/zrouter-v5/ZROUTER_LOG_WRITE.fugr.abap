*&---------------------------------------------------------------------*
*& Function group ZROUTER_LOG — gravação de auditoria em LUW separada
*&
*& POR QUE ISTO É UM MÓDULO DE FUNÇÃO RFC E NÃO UM MÉTODO
*&
*& No ZROUTER v4 o log era gravado com INSERT direto, na mesma LUW da BAPI
*& de negócio. Em seguida `execute_batch` chamava BAPI_TRANSACTION_ROLLBACK
*& no primeiro erro — e o rollback apagava as linhas de log junto com os
*& dados. O resultado é que a trilha de auditoria existia exatamente nos
*& casos em que não era necessária (sucesso) e desaparecia exatamente
*& naquele em que era (falha).
*&
*& Chamar este módulo com DESTINATION 'NONE' abre uma LUW separada no mesmo
*& sistema. O rollback da transação de negócio não a alcança. É o padrão
*& clássico para log que precisa sobreviver ao fracasso do que ele audita.
*&
*& CRIAR ASSIM (SE37):
*&   1. SE80 -> grupo de funções ZROUTER_LOG -> criar
*&   2. Criar módulo ZROUTER_LOG_WRITE
*&   3. Aba Atributos -> marcar "Módulo habilitado para acesso remoto"
*&      (RFC-enabled é obrigatório: DESTINATION 'NONE' exige)
*&   4. Aba Importação: IS_LOG  TYPE ZROUTER_LOG  (marcar "Valor de passagem")
*&   5. Colar o corpo abaixo em Código-fonte
*&---------------------------------------------------------------------*
FUNCTION zrouter_log_write.
*"----------------------------------------------------------------------
*"*"Interface local:
*"  IMPORTING
*"     VALUE(IS_LOG) TYPE  ZROUTER_LOG
*"----------------------------------------------------------------------

  DATA ls_log TYPE zrouter_log.
  ls_log = is_log.

  " O chamador pode não ter preenchido; a auditoria nunca fica sem quando.
  IF ls_log-tstamp IS INITIAL.
    GET TIME STAMP FIELD ls_log-tstamp.
  ENDIF.
  IF ls_log-uname IS INITIAL.
    ls_log-uname = sy-uname.
  ENDIF.

  " INSERT e não MODIFY: log é append-only. Um MODIFY permitiria que uma
  " segunda gravação com o mesmo id sobrescrevesse o registro anterior, e
  " auditoria que pode ser reescrita não é auditoria.
  INSERT zrouter_log FROM @ls_log.

  IF sy-subrc <> 0.
    " Colisão de GUID é a única causa realista aqui. Não relançamos: este
    " módulo roda numa LUW que ninguém está observando, e um dump aqui não
    " informa ninguém — só derruba a LUW de log sem tocar a de negócio.
    " O syslog é o lugar onde isso fica visível (SM21).
    DATA(lv_msg) = |ZROUTER: log { ls_log-log_id } nao gravado (subrc { sy-subrc })|.
    CALL FUNCTION 'RSLG_WRITE_SYSLOG_ENTRY'
      EXPORTING
        sl_message_area  = 'ZR'
        sl_message_subid = '1'
        sl_variable_data = lv_msg
      EXCEPTIONS
        OTHERS           = 0.
    RETURN.
  ENDIF.

  " COMMIT explícito: esta LUW é nossa e ninguém mais vai fechá-la.
  COMMIT WORK.

ENDFUNCTION.
