# ZROUTER — revisão de código antes da instalação

Gerado em 2026-08-03 por revisão multi-agente (5 lentes independentes: segurança,
compilação, golden rules, encaixe no produto, modelagem de dados) sobre:

- `ZROUTER - ENTERPRISE ABAP TEMPLATE.txt`
- `ZCL_ABAP_REPL.txt`
- `ZROUTER_TECHNICAL_SPEC.md` (seção 8, código revisado)
- `model-library/src/*` (templates base)

**Ressalva de método:** a rodada de verificação adversarial não completou (limite de
sessão). Os achados abaixo são de primeira passada; os de compilação foram reconferidos
manualmente um a um. Os de arquitetura são julgamento de projeto, não fato verificável
sem sistema. Nada aqui foi executado contra um SAP real.

**62 achados** — critico: 18, alto: 20, medio: 18, baixo: 6


## Críticos — impedem instalação

### [DM-01] Log e batch_result gravam na mesma LUW dos dados de negócio: o ROLLBACK apaga a própria evidência

**Onde:** `§8 — zcl_zrouter_logger~log_action (linhas 408-424), zcl_zrouter_batch~save_batch_result (1071-1083) e ~execute_batch (1085-1129); zcl_zrouter_handler_fi~post_document (728-744)`

**Problema:** log_action faz INSERT zrouter_log e save_batch_result faz MODIFY zrouter_batch_result sem commit próprio, dentro da mesma LUW da BAPI. Em seguida execute_batch chama BAPI_TRANSACTION_ROLLBACK na primeira falha (linha 1114) e post_document também chama ROLLBACK (linha 738). O rollback do banco desfaz indistintamente os dados de negócio E as linhas de auditoria já inseridas. Nenhum sy-subrc é verificado no MODIFY. Para um gateway cujo único valor de controle é a trilha de auditoria de escrita, isso significa que exatamente o caso que precisa de prova (a falha) é o que não deixa registro.

**Falha concreta:** Batch com 3 ações; a ação 2 falha. save_batch_result já gravou a linha seqnr=1 (SUCCESS) e a seqnr=2 (ERROR); execute_batch chama BAPI_TRANSACTION_ROLLBACK e sai do loop. O rollback descarta as duas linhas de ZROUTER_BATCH_RESULT e o log de erro escrito por dispatch. Depois disso ZROUTER_BATCH_RESULT fica vazia para aquele batch_guid, o EV_RESULT retornado ao agente diz 'ERROR' com 2 itens, e não existe nenhuma linha no banco que comprove que o batch rodou ou o que ele tentou escrever.

**Correção:** Auditoria não pode compartilhar LUW com o dado auditado. Acumular as entradas de log/batch em tabela interna durante a execução; após o COMMIT ou o ROLLBACK do dado de negócio, executar INSERT ... FROM TABLE + COMMIT WORK próprio (ou gravar via FM chamada com IN BACKGROUND UNIT / task separada). Verificar sy-subrc de todo INSERT/MODIFY e escalar cx_zrouter (M400) quando falhar. Nunca reutilizar BAPI_TRANSACTION_ROLLBACK sem antes preservar o buffer de log.

### [DM-02] ZROUTER_CONFIG não modela leitura vs escrita nem exigência de aprovação — o invariante do produto não é representável

**Onde:** `§2.1 define table zrouter_config (linhas 86-100) vs §9 Registry de Actions (linhas 1163-1170)`

**Problema:** A §9 do próprio spec classifica cada ação com a coluna 'Modo Escrita' (MM_CREATE_MATERIAL=X, FI_POST_DOCUMENT=X). Essa coluna não existe na tabela: zrouter_config só tem active, batchable e timeout. Como o invariante do TheBug Desktop (desktop-shell/CLAUDE.md) é que escrita ABAP nunca entra no catálogo do agente e que a única exceção passa por aprovação humana por ação, o ponto natural de enforcement é o registry — e ele não tem campo nem para classificar a ação, nem para exigir aprovação, nem para registrar quem aprovou. validate_and_check (linhas 938-949) só consulta active + autorização, então o modelo de dados trata GET_MATERIAL e POST_DOCUMENT como idênticos.

**Falha concreta:** Um Basis cadastra a linha ('FI','POST_DOCUMENT', active='X') no cliente para 'habilitar consulta de razão'. O ZROUTER passa a aceitar lançamento contábil via HTTP sem qualquer aprovação humana e sem que nada no modelo de dados sinalize que aquela linha é uma ação de escrita. Auditoria posterior sobre ZROUTER_CONFIG não consegue nem listar quais ações habilitadas escrevem no ERP.

**Correção:** Acrescentar a ZROUTER_CONFIG: write_op : abap_boolean (leitura/escrita), approval_mode : abap.char(1) (N=none, H=human-approved), risk_class : abap.char(1), e opcionalmente auth_object/auth_value explícitos por linha. Fazer validate_and_check recusar por padrão qualquer linha com write_op = abap_true que não traga evidência de aprovação (correlacionada em ZROUTER_LOG, ver DM-11). Documentar em ADR que o default de uma linha nova é write_op='X' até prova em contrário (fail-closed), e que o registry viaja por transporte (ver DM-04), não por cadastro manual em PRD.

### [DM-03] get_logs não compila e, se compilasse, o range de data sobre timestampl retornaria zero linhas sempre

**Onde:** `§8 — zcl_zrouter_logger~get_logs (linhas 426-436), cláusula WHERE`

**Problema:** Três defeitos empilhados na mesma SELECT. (1) '( module = @iv_module OR @iv_module IS INITIAL )' e '@iv_date IS INITIAL' não são ABAP SQL válido: variável host só pode aparecer do lado direito de uma comparação; IS INITIAL exige coluna/expressão SQL como operando. (2) 'DATA(lv_date_to) = iv_date + 1' — em declaração inline, o tipo de cálculo de um campo de data em expressão aritmética é i, então lv_date_to vira o número do dia (~739105), enquanto lv_date_from continua TYPE d ('20260803'). Os dois limites do range estão em unidades diferentes. (3) A coluna timestamp é um timestamp (2.026e13 em timestampl), comparado contra 20260803 e 739105 — não há conversão implícita de DATS para timestamp; a semântica de dia não existe.

**Falha concreta:** Chamada get_logs( iv_date = '20260803' ). Se o sistema aceitar a sintaxe, a condição vira 'timestamp >= 20260803 AND timestamp < 739105': a primeira é verdadeira para toda linha, a segunda é falsa para toda linha (todo timestampl real é ~2e13). Resultado: rt_logs volta vazia, sy-subrc=4, sem exceção e sem mensagem. O operador conclui que não houve atividade do agente naquele dia — enquanto a tabela pode conter milhares de escritas.

**Correção:** Converter a data para os limites do timestamp e usar range table para o filtro opcional: DATA(lv_from) = CONV timestampl( |{ iv_date }000000| ). DATA(lv_to) = CONV timestampl( |{ CONV dats( iv_date + 1 ) }000000| ). Montar lr_module TYPE RANGE OF ... vazio quando iv_module for inicial e usar 'WHERE module IN @lr_module AND timestamp >= @lv_from AND timestamp < @lv_to'. Documentar que o timestamp é UTC e que iv_date é data local — converter o limite com cl_abap_tstmp/utclong e o fuso do usuário, senão a fronteira do dia fica deslocada.

### [DM-18] REPL: a persistência da auditoria guarda 50 caracteres do código arbitrário executado, e INSERT REPORT grava objeto de repositório com nome colidível

**Onde:** `log_execution linhas 298-339 (ls_msg-msgv1 = iv_code(lv_len), linhas 320-324) e execute_code linhas 176-190 (INSERT REPORT com nome derivado de sy-uname)`

**Problema:** A única persistência do que o REPL executou é uma mensagem BAL cujo msgv1 é CHAR(50) — o código é cortado em 50 caracteres antes de gravar (lv_len limitado a 50). Não há tabela de log com o código íntegro, nem hash, nem saída, nem correlação com ZROUTER_LOG. Em paralelo, execute_code persiste um objeto de repositório real (INSERT REPORT em REPOSRC/D010S) com nome 'ZR' + sy-uname(4) + sy-uzeit; o DELETE REPORT de limpeza apaga esse nome sem verificar quem o criou. E 'DATA(lv_user) = CONV string( sy-uname )' remove brancos à direita, então lv_user(4) estoura para nomes de usuário com menos de 4 caracteres.

**Falha concreta:** (a) Auditoria: alguém executa via REPL um bloco que faz UPDATE direto numa tabela de negócio. O BAL registra 'DATA lt TYPE TABLE OF bkpf. UPDATE bkpf SET bu' — 50 caracteres. Nada no sistema diz o que foi alterado, e o REPL não usa ZROUTER_LOG. (b) Colisão: duas sessões do mesmo usuário técnico executam no mesmo segundo; ambas geram o nome ZRWILL143022. O segundo INSERT REPORT sobrescreve o fonte que o primeiro está executando, e o primeiro DELETE REPORT apaga o report do segundo no meio da execução. (c) Dump: usuário 'BOB' (3 caracteres) dispara CX_SY_RANGE_OUT_OF_BOUNDS em lv_user(4).

**Correção:** Este artefato não deveria entrar na instalação do cliente — INSERT REPORT + GENERATE REPORT + SUBMIT de código recebido por HTTP é escrita ABAP arbitrária e viola tanto a golden rule 'no-eval-expression' quanto o invariante de desktop-shell/CLAUDE.md; a guarda is_production_system( ) (cccategory='P') não é suficiente porque cccategory é dado de T000 mantido manualmente. Se ele for mantido para uso interno de desenvolvimento, no mínimo: persistir o código completo (abap.string), a saída, o hash e o resultado numa tabela dedicada com dataMaintenance #NOT_ALLOWED, correlacionada ao mesmo guid de ZROUTER_LOG; gerar o nome do report com cl_system_uuid em vez de uname+uzeit; e trocar sy-uname(4) por substring( val = lv_user off = 0 len = nmin( val1 = 4 val2 = strlen( lv_user ) ) ).

### [F01] API inexistente cl_abap_authorization=>check_authorization e exceção cx_abap_not_authorized

**Onde:** `linhas 179-183 (spec) e 459-466 (classe ZCL_ZROUTER_AUTHORITY, método check_authority)`

**Problema:** Não existe no ABAP padrão (nem clássico nem ABAP Cloud) a classe CL_ABAP_AUTHORIZATION nem o método estático check_authorization( iv_object iv_field iv_value ). Checagem de autorização em ABAP se faz com o statement AUTHORITY-CHECK OBJECT (liberado para ABAP Cloud) ou com DCL/access controls em CDS. A exceção cx_abap_not_authorized capturada no CATCH também não é uma classe padrão. Ambos os símbolos são desconhecidos -> a classe inteira ZCL_ZROUTER_AUTHORITY não compila, e como ela é o núcleo de segurança do dispatcher (chamada em validate_and_check), derruba a ativação de ZCL_ZROUTER_DISPATCH também. O texto do spec ainda afirma que é 'a API padrão do ABAP Cloud', o que é falso.

**Falha concreta:** Ativar ZCL_ZROUTER_AUTHORITY -> erro de sintaxe 'CL_ABAP_AUTHORIZATION is unknown' / 'CX_ABAP_NOT_AUTHORIZED is unknown'. Nada relacionado a segurança compila.

**Correção:** Trocar por AUTHORITY-CHECK OBJECT 'ZROUTER' ID 'ACTIVITY' FIELD lv_activity. e avaliar sy-subrc (0 = autorizado), sem TRY/CATCH. Remover a menção falsa a cl_abap_authorization no §5. O objeto ZROUTER com campo ACTIVITY precisa existir em SU21.

### [F02] Tipo DDL embutido abap.syst_lo05 não existe -> tabelas não ativam

**Onde:** `ZROUTER_LOG campo timestamp linha 116 e ZROUTER_BATCH_RESULT campo timestamp linha 134: 'timestamp : abap.syst_lo05;'`

**Problema:** abap.syst_lo05 não é um tipo predefinido do dicionário. Os built-in DDL válidos para timestamp são abap.utclong, ou o data element timestampl / timestamp (dec 21,7 / dec 15,0). 'syst_lo05' é inventado. As duas tabelas transparentes não ativam, e por consequência qualquer objeto que declara TYPE zrouter_log / zrouter_batch_result (ZCL_ZROUTER_LOGGER, ZCL_ZROUTER_BATCH) fica sem tipo -> não compila em cascata.

**Falha concreta:** Ativar a DDL de ZROUTER_LOG -> 'Type abap.syst_lo05 is unknown'. GET TIME STAMP FIELD ls_log-timestamp (linha 419) e INSERT zrouter_log ficam inválidos.

**Correção:** Usar 'timestamp : timestampl;' (data element) ou 'timestamp : abap.dec(21,7);' ou abap.utclong, alinhando o tipo ABAP dos campos ty_log_entry-timestamp / ty_action_result-timestamp (que são timestampl).

### [F03] Construção de tipo tabela inline na assinatura de método (proibida)

**Onde:** `método get_logs, linhas 329-330: 'RETURNING VALUE(rt_logs) TYPE STANDARD TABLE OF ty_log_entry WITH EMPTY KEY.'`

**Problema:** O tipo de um parâmetro (após TYPE) deve referenciar um tipo nomeado; não é permitido construir 'STANDARD TABLE OF ... WITH EMPTY KEY' inline na declaração de parâmetro. Repare que a própria interface zif_zrouter_config faz o certo: define TYPES ty_config_entries (linha 275) e usa TYPE ty_config_entries. Já get_logs não define tipo tabela nomeado. Isso é erro de sintaxe -> a interface zif_zrouter_logger não ativa.

**Falha concreta:** Ativar zif_zrouter_logger -> erro de sintaxe na cláusula RETURNING de get_logs. Toda a cadeia logger/dispatch/batch quebra.

**Correção:** Declarar na interface: TYPES ty_log_entries TYPE STANDARD TABLE OF ty_log_entry WITH EMPTY KEY. e usar RETURNING VALUE(rt_logs) TYPE ty_log_entries.

### [F04] Campo de cliente citado em WHERE sem CLIENT SPECIFIED (Open SQL strict)

**Onde:** `linha 353 'WHERE client = @sy-mandt' (load_config) e linha 431 'WHERE client = @sy-mandt' (get_logs)`

**Problema:** O código usa Open SQL strict (lista de colunas com vírgula e host vars com @). Em modo strict, referenciar explicitamente a coluna de cliente (aqui chamada 'client', tipo abap.clnt) na condição WHERE sem a adição CLIENT SPECIFIED é erro de sintaxe: o cliente é tratado automaticamente. Ocorre nos dois SELECTs.

**Falha concreta:** Verificação de sintaxe do SELECT -> 'A coluna de cliente CLIENT não pode ser usada na condição WHERE sem CLIENT SPECIFIED'. Os dois métodos não compilam.

**Correção:** Remover 'client = @sy-mandt' (o cliente já é implícito) ou, se for realmente necessário, usar '... USING CLIENT ...' / 'CLIENT SPECIFIED'. Em ABAP Cloud, sy-mandt também não é liberado.

### [F05] Exceção verificada cx_zrouter não capturada nem declarada

**Onde:** `execute_batch chama mo_logger->log_action linhas 1124-1128 (assinatura sem RAISING, linha 1030); dispatch chama mo_logger->log_action dentro do CATCH linhas 989-994 (assinatura sem RAISING, linha 905)`

**Problema:** log_action é declarado RAISING cx_zrouter (cx_static_check = exceção verificada). Em execute_batch a chamada final a log_action não está em TRY/CATCH e o método não declara RAISING -> erro de sintaxe 'CX_ZROUTER não é capturada nem declarada'. Em dispatch, a chamada a log_action está DENTRO do bloco CATCH; uma exceção lançada dentro do CATCH não é capturada pelo mesmo TRY, e dispatch também não declara RAISING -> mesmo erro.

**Falha concreta:** Ativar ZCL_ZROUTER_BATCH e ZCL_ZROUTER_DISPATCH -> erro de sintaxe de exceção não tratada em ambos.

**Correção:** Envolver as chamadas de log_action em TRY. ... CATCH cx_zrouter. ENDTRY. (log de auditoria não deve derrubar o fluxo), ou declarar RAISING cx_zrouter nas assinaturas de execute_batch/dispatch.

### [F1] Endpoint unico de dispatch entrega escrita ao catalogo do agente

**Onde:** `dispatch() ~L976-996 e validate_and_check() L938-949`

**Problema:** dispatch(iv_module, iv_action, iv_payload) nao tem parametro de modo/escopo read-only. validate_and_check so checa is_action_allowed (flag active) + cl_abap_authorization. Um unico tool cobre leitura e escrita. Registrar esse endpoint como ferramenta de escopo mcp coloca CREATE_MATERIAL, POST_DOCUMENT, CREATE_SALES_ORDER e o batch no catalogo do agente; os handlers dao BAPI_TRANSACTION_COMMIT. Viola diretamente o invariante #1 (desktop-shell/CLAUDE.md L6-23) e exige um ADR proprio, que nao existe. Resposta a pergunta central: com o desenho atual o invariante NAO se mantem.

**Falha concreta:** Agente emite {module:'FI', action:'POST_DOCUMENT', payload:{...}} -> zcl_zrouter_handler_fi chama BAPI_ACC_DOCUMENT_POST + BAPI_TRANSACTION_COMMIT (spec L732-742) sem gate humano -> documento contabil lancado a partir de um turno do modelo.

**Correção:** Dividir a superficie na fronteira do tool: expor ao agente apenas um tool read-only (enum fechado de GET_*); acoes de escrita nunca entram no catalogo e sao roteadas pelo gate do bridge (ver F8). O dispatcher/ICF deve recusar acoes de escrita fora do caminho gated.

### [F2] ZROUTER comita dentro do handler, sem pendencia/aprovacao - contorna o gate por construcao

**Onde:** `zcl_zrouter_handler_fi=>post_document L728-744; handler_mm create_material L586-601; ausencia de estado pendente no dispatch`

**Problema:** Nao existe etapa que mantenha a acao pendente para decisao humana: o COMMIT acontece dentro do proprio handler no mesmo request. E exatamente o motivo pelo qual o ADR-0001 rejeitou os MCPs de GUI de terceiros ('contornam o gate por construcao - dirigem COM internamente, sem ponto onde interpor a confirmacao', ADR-0001 L49-52). Nao ha separacao requester/approver como no thebug-sap-gui (/gui/action escopo mcp bloqueia; /gui/pending e /gui/decide escopo ui). O gate de aprovacao humana do ADR-0001 nao se encaixa em nenhuma acao mutavel do ZROUTER como esta.

**Falha concreta:** Qualquer acao de escrita executa e comita no mesmo POST; nao ha equivalente a /gui/pending nem /gui/decide -> impossivel interpor a confirmacao humana por acao que o ADR-0001 exige.

**Correção:** Se alguma acao mutavel do ZROUTER for realmente desejada, replicar o padrao ADR-0001: MCP registra pendencia no bridge (escopo mcp), long-poll ate aprovacao humana na UI (escopo ui) exibindo o payload literal, allowlist de acao, auditoria por acao aprovada, desligado por default, e um ADR novo. Sem isso, manter escrita fora do catalogo.

### [F4] O template HTTP nao tem gate de autorizacao e instancia classe dinamica a partir de string do banco

**Onde:** `process_request L151-189 (sem authority-check) + zcl_execution_engine=>run L44-45 (CREATE OBJECT lo_exec TYPE (iv_class))`

**Problema:** O handler ICF que a tarefa pretende expor por HTTP nao chama nenhuma checagem de autorizacao: deserializa intent, faz SELECT handler_class FROM zai_skills e executa zcl_execution_engine=>run, que faz CREATE OBJECT lo_exec TYPE (iv_class) - um motor de execucao generico dirigido por string do banco. A versao OO da secao 8 (com cl_abap_authorization) e um Function Module RFC, NAO este handler HTTP. Portanto o artefato realmente exposto por HTTP e o mais fraco dos dois, e os dois discordam sobre se auth e sequer checada.

**Falha concreta:** POST com intent mapeado a uma classe arbitraria cadastrada em zai_skills -> execucao da classe sem authority-check; se zai_skills for populavel/seedada de forma ampla, vira execucao de classe arbitraria via HTTP.

**Correção:** Nao expor este template. Se houver ICF, envolver o dispatcher da secao 8 com authority-check obrigatorio e sem instanciacao dinamica por string (factory com allowlist fechada de handlers), e ainda assim so para acoes read-only no catalogo do agente.

### [F5] REPL e execucao remota de codigo arbitrario - nunca pode chegar perto do catalogo do agente

**Onde:** `execute_code L168-274 (INSERT REPORT/GENERATE REPORT/SUBMIT); check_authorization L277-286 (ACTVT '03'); is_production_system L289-295`

**Problema:** O ZCL_ABAP_REPL aceita ABAP arbitrario via HTTP POST e executa com INSERT REPORT + GENERATE REPORT + SUBMIT. Viola a golden rule no-eval-expression (model-library-design.md secao 6, L166: 'No GENERATE SUBROUTINE POOL / dynamic exec of request data'). O unico gate e AUTHORITY-CHECK S_DEVELOP com ACTVT '03' (display) para o que e, na pratica, escrita/execucao ilimitada, mais um bloqueio que so vale em produtivo (cccategory='P'). Em DEV/QAS nao-produtivo executa tudo.

**Falha concreta:** POST /repl {"code":"... UPDATE dbtab ..."} num cliente nao-produtivo, usuario com S_DEVELOP display -> efeitos colaterais arbitrarios (escrita, chamada de BAPI, DELETE) rodam server-side.

**Correção:** Manter o REPL inteiramente fora de qualquer superficie consumida pelo agente; nao e candidato a tool sob nenhum escopo (mcp nem ui). Se precisar existir para dev humano, fica atras de rota manual autenticada, nunca registrada no catalogo.

### [SEC-01] RCE por design: corpo HTTP vira programa ABAP via INSERT REPORT + GENERATE REPORT + SUBMIT

**Onde:** `zcl_abap_repl=>execute_code, linhas 168-274 (INSERT REPORT ~190, GENERATE REPORT ~196, SUBMIT ~216)`

**Problema:** O corpo da requisição é extraído com FIND PCRE, montado como fonte de um REPORT, gravado no repositório com INSERT REPORT, compilado com GENERATE REPORT e executado com SUBMIT (lv_repname). Isso é a violação máxima da regra no-eval-expression: não há sandbox, não há allowlist de statements, não há AUTHORITY-CHECK dentro do código gerado. Programas criados por INSERT REPORT não têm grupo de autorização em TRDIR, portanto o SUBMIT também não dispara S_PROGRAM — não existe segunda barreira. Além disso, cada requisição cria um objeto de repositório real (ZR*), o que viola diretamente o invariante 2 do desktop-shell/CLAUDE.md ('Nunca crie objetos técnicos ABAP via RFC. Tabela, classe, interface: criação apenas por transporte/abapGit').

**Falha concreta:** POST /sap/bc/zabap_repl com corpo {"code":"SELECT bname, bcode, passcode FROM usr02 INTO TABLE @DATA(lt). LOOP AT lt INTO DATA(ls). WRITE / ls-bname. ENDLOOP."} feito por qualquer usuário que passe no check da linha 278. O servidor grava o programa, compila e executa. O atacante obtém leitura arbitrária (USR02, RFCDES, T000 com CLIENT SPECIFIED), escrita arbitrária (UPDATE/DELETE em qualquer tabela sem AUTHORITY-CHECK), CALL FUNCTION ... DESTINATION para pivotar para sistemas vizinhos e CALL 'SYSTEM' para comandos de SO. Consequência: comprometimento total do sistema ABAP e de tudo que ele alcança.

**Correção:** Não instalar ZCL_ABAP_REPL no sistema do cliente sob nenhuma configuração. Se for necessária execução de código em DEV, isso é papel do ADT/SE38 com transporte, não de um endpoint ICF. Para o objetivo de cobrir lacunas do ADT, o ZROUTER deve expor um conjunto fechado e nomeado de operações (registry estático em código, não tabela editável), sem nenhuma forma de execução dinâmica de fonte.

### [SEC-02] S_DEVELOP com ACTVT '03' (exibir) usado para autorizar EXECUÇÃO de código arbitrário

**Onde:** `zcl_abap_repl=>check_authorization, linhas 277-286`

**Problema:** O único gate de autorização do POST é AUTHORITY-CHECK OBJECT 'S_DEVELOP' ... ID 'ACTVT' FIELD '03'. ACTVT 03 é 'exibir' — é a autorização que se concede a consultores funcionais, auditores, analistas de suporte e usuários de leitura para abrirem código em SE80/SE38. Ela está sendo usada para autorizar criação de programa (ACTVT 01), alteração (02) e execução (16). Agravantes: DEVCLASS, OBJNAME e P_GROUP estão como DUMMY, ou seja, qualquer pacote/nome/grupo passa; e se o nó SICF do serviço tiver logon data fixo (usuário de serviço), o check roda contra o usuário de serviço e não contra o chamador, transformando o endpoint em RCE efetivamente anônimo.

**Falha concreta:** Usuário CONSULTOR_FI, cujo perfil só tem S_DEVELOP ACTVT 03 para ler código, envia POST /sap/bc/zabap_repl com {"code":"UPDATE usr02 SET uflag = 0 WHERE bname = 'SAP*'. COMMIT WORK."}. check_authorization retorna abap_true, o código roda com todas as autorizações desse usuário e sem nenhum AUTHORITY-CHECK subsequente. O usuário de leitura vira executor arbitrário. Variante pior: com logon data no SICF, um cliente HTTP sem credencial nenhuma alcança o mesmo resultado com as autorizações do usuário de serviço.

**Correção:** Remover o endpoint (ver SEC-01). Regra geral para o ZROUTER: nunca autorizar execução com ACTVT 03. Para o handler ICF do ZROUTER, usar objeto de autorização próprio com atividade explícita de execução, verificado antes de qualquer trabalho, e documentar no SICF que o serviço não deve ter logon data fixo — a identidade tem que ser a do chamador.

### [SEC-03] Sem validação de CSRF e sem limite de tamanho de corpo no POST que executa código

**Onde:** `zcl_abap_repl=>if_http_extension~handle_request linha 61 e handle_post linhas 91-165`

**Problema:** handle_post não lê nem valida X-CSRF-Token, não checa Origin/Referer, e o serviço ICF customizado não tem proteção XSRF habilitada por padrão. A extração do código é feita por FIND PCRE '"code"\s*:\s*"...' sobre o corpo bruto, ou seja, o corpo nem precisa ser JSON válido nem ter Content-Type application/json — um form HTML com enctype=text/plain produz um corpo que casa com o regex, e requisição simples de formulário não dispara preflight CORS. get_cdata( ) também lê o corpo inteiro para memória sem checar content-length.

**Falha concreta:** Um desenvolvedor com sessão SAP ativa (cookie MYSAPSSO2 ou SAP_SESSIONID no navegador, situação normal com Fiori/WebGUI aberto) visita uma página maliciosa que contém <form action="https://sap-dev:44300/sap/bc/zabap_repl" method="POST" enctype="text/plain"> com um campo cujo name é {"code":"...payload..." e submit automático. O navegador anexa o cookie, o handler extrai o código e o executa com as autorizações do desenvolvedor. Nenhuma interação além de visitar a página. Secundariamente, um POST de 500 MB de corpo é materializado em string e derruba o work process.

**Correção:** Além de remover este endpoint: para o handler ICF do ZROUTER, exigir o token XSRF do framework ICF (habilitar a proteção no nó SICF e validar o header no handler), rejeitar requisições cujo Content-Type não seja exatamente application/json, e verificar server->request->get_header_field('content-length') contra um teto explícito antes de chamar get_cdata( ).

### [SEC-08] Handler ICF do ZROUTER sem nenhum AUTHORITY-CHECK antes de despachar a intent

**Onde:** `zcl_zrouter=>if_http_extension~handle_request, linhas 143-149, e process_request, linhas 151-189`

**Problema:** handle_request lê o corpo e chama process_request imediatamente. Não existe AUTHORITY-CHECK em nenhum ponto do arquivo — nem no router, nem em zcl_execution_engine=>run, nem no exemplo zcl_mm_service. Violação direta da regra auth-check-first. O único controle de acesso é o logon do nó SICF, que é binário: quem consegue autenticar no serviço executa qualquer intent registrada em ZAI_SKILLS, inclusive as de escrita. Se o nó SICF for configurado com logon data (prática comum para integrações), a autorização efetiva passa a ser a do usuário de serviço para todos os chamadores, e o handler não tem como distinguir quem chamou.

**Falha concreta:** CONSULTOR_MM, que só tem papéis de exibição, envia POST /sap/bc/zrouter com {"intent":"FI_POST_DOCUMENT","user":"X","parameters":"{...}"}. O router resolve a classe na ZAI_SKILLS e executa. Para handlers que fazem SELECT direto (o exemplo zcl_mm_service não faz nenhum check), ele lê dados de MM/FI/HCM aos quais não teria acesso por transação. Para handlers com BAPI padrão, as checagens internas da BAPI ainda valem, mas não existe controle nenhum sobre QUAIS intents aquele chamador pode acionar — o gate de granularidade do ZROUTER simplesmente não existe. Com logon data no SICF, qualquer chamador HTTP herda as autorizações do usuário de serviço.

**Correção:** AUTHORITY-CHECK como primeira instrução de handle_request, sobre objeto de autorização próprio, com o valor derivado da intent, antes de ler o corpo e antes de qualquer SELECT. Falha do check retorna 403 e grava log. Documentar no runbook de instalação que o nó SICF do ZROUTER não pode ter logon data fixo.

### [SEC-17] O único template concreto aprovado executa BAPI de escrita e COMMIT sem AUTHORITY-CHECK, e o template de handler HTTP que deveria carregar a regra não existe

**Onde:** `zcl_tmpl_handler=>create_entity, linhas 48-80 (CALL FUNCTION '{{BAPI_NAME}}' linha 62, BAPI_TRANSACTION_COMMIT linha 74); regra auth-check-first em docs/model-library-design.md seção 6`

**Problema:** zcl_tmpl_handler é o modelo do qual todos os handlers de módulo serão gerados. Ele chama uma BAPI de escrita e faz BAPI_TRANSACTION_COMMIT sem uma única AUTHORITY-CHECK. A seção 6 do model-library-design atribui a regra auth-check-first exclusivamente a http_handler, e src/ contém apenas package.devc.xml, zcl_tmpl_handler, zcx_tmpl, zif_tmpl_handler e ztmpl_table.tabl.ddl — zcl_tmpl_http_handler.clas.abap não existe. Ou seja: a única regra de autorização da biblioteca está atribuída a um artefato inexistente, e o artefato que existe e escreve não a aplica. handle_action é público em classe CREATE PUBLIC, então vale o mesmo que SEC-13: não há como restringir o chamador. O gate de CI descrito na seção 6 roda abap:lint e ATC sobre src/**, e nenhum dos dois detecta ausência de AUTHORITY-CHECK.

**Falha concreta:** Gera-se ZCL_MM_HANDLER a partir do template, conforme o workflow da seção 7. Quem implementar o ponto de entrada ICF vai usar o template do artefato 1 (que também não tem check, SEC-08) ou instanciar o handler direto. Resultado: POST /sap/bc/zrouter por qualquer usuário que autentique no serviço chega a BAPI_MATERIAL_SAVEDATA + COMMIT sem que nenhuma linha de código do ZROUTER tenha verificado se aquele chamador podia acionar aquela ação. Todo handler gerado a partir da biblioteca herda o defeito, que é exatamente o oposto do propósito declarado da biblioteca ('golden templates carry the fixes').

**Correção:** Antes de qualquer geração: (1) adicionar AUTHORITY-CHECK como primeira instrução de zif_tmpl_handler~handle_action no template, sobre objeto de autorização dedicado, com valor derivado de co_module + iv_action, retornando erro sem executar nada em caso de falha; (2) mover a regra auth-check-first da linha de http_handler para 'all' na tabela da seção 6, junto com no-eval-expression; (3) criar de fato src/http/zcl_tmpl_http_handler.clas.abap com AUTHORITY-CHECK, validação de token XSRF, verificação de método e teto de content-length; (4) acrescentar ao gate de CI uma verificação que reprove qualquer template que chame BAPI/COMMIT/MODIFY sem AUTHORITY-CHECK precedente, já que abap:lint e ATC não cobrem isso.


## Altos — corrigir antes de expor

### [DM-04] Faltam as annotations obrigatórias tableCategory/deliveryClass/dataMaintenance; e a classe de entrega correta difere entre config e log

**Onde:** `§2.1 — cabeçalho de annotations das três tabelas (linhas 86-88, 104-106, 121-124); comparar com model-library/src/ztmpl_table.tabl.ddl linhas 7-11`

**Problema:** O padrão aprovado (ztmpl_table.tabl.ddl) declara cinco annotations: EndUserText.label, enhancement.category, tableCategory #TRANSPARENT, deliveryClass #A e dataMaintenance #RESTRICTED. As três tabelas do spec declaram apenas as duas primeiras. Em DDL de tabela, tableCategory e deliveryClass são obrigatórias — a ativação falha. Além disso, copiar o #A do template para as três seria errado: ZROUTER_CONFIG é um allowlist de segurança que precisa viajar por transporte para PRD (classe C), enquanto ZROUTER_LOG e ZROUTER_BATCH_RESULT são trilha de auditoria que jamais pode ser editável (dataMaintenance #NOT_ALLOWED) nem transportada com conteúdo.

**Falha concreta:** Deploy via deploy_all.py (ADT /ddic/tables/.../source/main): a ativação de zrouter_config retorna erro de ativação por annotation obrigatória ausente e nenhuma das três tabelas existe no sistema. Se as annotations forem completadas às cegas com o #A/#RESTRICTED do template, o allowlist passa a ser cadastrado manualmente em cada cliente (DEV, QAS, PRD divergem silenciosamente) e a tabela de log fica manutenível por SE16/SM30 para quem tiver S_TABU_DIS — auditoria editável não é auditoria.

**Correção:** ZROUTER_CONFIG: @AbapCatalog.tableCategory:#TRANSPARENT, @AbapCatalog.deliveryClass:#C, @AbapCatalog.dataMaintenance:#RESTRICTED (com view de manutenção e objeto de autorização próprio). ZROUTER_LOG e ZROUTER_BATCH_RESULT: #TRANSPARENT, deliveryClass #A (ou #L se o conteúdo deve sumir em cópia de cliente) e @AbapCatalog.dataMaintenance:#NOT_ALLOWED. Registrar essa diferença explicitamente como regra na §6 do docs/model-library-design.md, já que o template único não cobre os dois casos.

### [DM-05] abap.syst_lo05 não é tipo built-in do DDIC; e o código mistura utclong com timestampl no mesmo campo conceitual

**Onde:** `§2.1 zrouter_log linha 116 e zrouter_batch_result linha 134 ('timestamp : abap.syst_lo05'); §8 linhas 419, 521, 1081`

**Problema:** O prefixo 'abap.' referencia tipos embutidos do dicionário (char, clnt, dats, dec, int4, string, utclong...). 'syst_lo05' não está nessa lista — parece nome de elemento de dados, e mesmo assim seria escrito sem o prefixo. A tabela não ativa. Em paralelo, o código usa três representações diferentes de tempo: GET TIME STAMP FIELD ls_log-timestamp (linha 419) exige timestamp/timestampl/utclong; build_result faz 'rs_result-timestamp = utclong_current( )' (linha 521) atribuindo utclong a um campo declarado TYPE timestampl na interface (linha 309) — utclong só é conversível com utclong e tipos caracteres, então isso é erro de sintaxe ou lixo; e o template aprovado usa 'created_at : abap.timestampl'.

**Falha concreta:** Ativação da DDL de zrouter_log falha com 'tipo abap.syst_lo05 desconhecido'. Após alguém trocar por um tipo qualquer que ative (ex.: abap.char(20)), o GET TIME STAMP FIELD passa a gravar um valor numérico em campo caractere e get_logs ordena/filtra lexicograficamente — a ordenação DESCENDING deixa de refletir a ordem cronológica.

**Correção:** Padronizar um único tipo de tempo em todo o stack. Recomendo abap.utclong nas três tabelas (moderno, sem ambiguidade de fuso, alinhado com ABAP Cloud) e timestamp TYPE utclong nas estruturas ty_action_result/ty_log_entry, usando utclong_current( ) em todos os pontos. Alternativa conservadora: 'timestamp : timestampl' (elemento de dados) nas tabelas + GET TIME STAMP FIELD em todos os pontos, eliminando utclong_current( ). Corrigir o template ztmpl_table.tabl.ddl no mesmo movimento e fixar a escolha como golden rule.

### [DM-06] Truncamento silencioso de payload, result e message: char(1024)/char(255) recebendo STRING

**Onde:** `§2.1 zrouter_log linhas 113-115 e zrouter_batch_result linhas 131-133; §8 linhas 414-416 e 1078-1080. Comparar com model-library/src/ztmpl_table.tabl.ddl linha 18`

**Problema:** payload e result são abap.char(1024) e message abap.char(255), mas log_action e save_batch_result recebem iv_payload/iv_result/iv_message TYPE string e fazem atribuição direta. Em ABAP, string -> char(n) trunca sem erro, sem sy-subrc, sem exceção. O template já aprovado usa 'payload : abap.string' exatamente para evitar isso. Além do truncamento, char(1024) preenche com brancos até 1024 em toda linha e os brancos finais somem na leitura, o que corrompe JSON terminado em espaço.

**Falha concreta:** Agente envia CREATE_MATERIAL com o header BAPI_MATERIAL_SAVEDATA serializado (facilmente 2-4 KB de JSON). ZROUTER_LOG.payload guarda os primeiros 1024 caracteres — um JSON sintaticamente inválido, cortado no meio de um campo. Numa investigação sobre um material criado errado, ninguém consegue reconstruir o que foi pedido nem reprocessar o payload; o mesmo vale para result. As mensagens montadas por string template ('Material creation failed: ' + BAPIRET2-message, até 220 chars) estouram os 255 e perdem o final justamente da mensagem de erro do SAP.

**Correção:** payload, result e message como abap.string nas duas tabelas (padrão do ztmpl_table.tabl.ddl). Se houver exigência de limitar o volume, o truncamento tem que ser explícito e auditável: manter payload_full como string, ou gravar payload_len TYPE abap.int4, payload_hash TYPE abap.char(64) (SHA-256 do payload íntegro) e um flag truncated TYPE abap_boolean, com o corte feito no código e registrado. Nunca deixar o DDIC truncar por conta própria.

### [DM-07] Coluna de cliente referenciada explicitamente no WHERE — erro de sintaxe no modo estrito e em ABAP Cloud

**Onde:** `§8 — zcl_zrouter_config~load_config linha 353 e zcl_zrouter_logger~get_logs linha 431 ('WHERE client = @sy-mandt')`

**Problema:** Ambas as SELECTs filtram explicitamente pela coluna de cliente. Em tabela cliente-dependente o ABAP SQL já adiciona o cliente automaticamente, e a partir do modo estrito da checagem de sintaxe (7.40+) referenciar a coluna de cliente sem CLIENT SPECIFIED / USING CLIENT é erro. O spec declara alvo ABAP Cloud Tier 2 (§5, uso de cl_abap_authorization), onde a restrição é ainda mais dura. Somado ao fato de a coluna se chamar 'client' (e não 'mandt'), essa cláusula é ao mesmo tempo redundante e bloqueante.

**Falha concreta:** Ativação de zcl_zrouter_config e zcl_zrouter_logger falha na checagem de sintaxe com erro sobre uso da coluna de cliente; o ZROUTER não ativa em nenhum sistema com modo estrito. Se o desenvolvedor 'resolver' adicionando CLIENT SPECIFIED sem entender, a SELECT passa a ler todos os mandantes: get_logs de um cliente devolve log de escrita de outro mandante do mesmo sistema.

**Correção:** Remover a cláusula de cliente das duas SELECTs e deixar o handling implícito. Se algum caso exigir leitura cross-client (não é o caso aqui), usar explicitamente USING CLIENT / CLIENT SPECIFIED, documentar em ADR e proteger por autorização própria. Acrescentar esse ponto como golden rule ('no-explicit-client-in-where') na §6 do model-library-design.md, já que é padrão que se propaga por cópia.

### [DM-08] Nenhum índice secundário existe de fato; get_logs faz full scan + sort e materializa a tabela inteira em memória

**Onde:** `§2.1 zrouter_log chave (linhas 107-108); §8 get_logs (429-435); §11 recomendação 2 (linha 1190)`

**Problema:** A chave primária é (client, guid) com guid aleatório de cl_system_uuid — inútil para a consulta que o código realmente faz, que filtra por module e faixa de tempo e ordena por timestamp. Nenhum objeto de índice é definido em nenhum artefato: a §11 apenas 'recomenda' criar um índice (client, timestamp, module), o que não é entregável. Além disso get_logs não tem UP TO n ROWS nem paginação, e devolve uma tabela interna de campos STRING; e o ORDER BY timestamp sozinho não é determinístico (timestamps repetem), então paginação futura embaralha resultados.

**Falha concreta:** ZROUTER_LOG cresce uma linha por dispatch. Com 5 milhões de linhas, uma chamada get_logs sem filtro (iv_module e iv_date iniciais, que é o caminho que a condição OR habilita) faz full table scan, ordena tudo e tenta materializar 5 milhões de estruturas de strings no work process: TSV_TNEW_PAGE_ALLOC_FAILED derruba o work process, e a chamada HTTP do desktop expira. Repetido pelo agente, tira o sistema do ar.

**Correção:** Criar objeto de índice secundário (client, timestamp) e (client, module, timestamp) — e (client, batch_guid) junto com DM-11. Adicionar UP TO @iv_max_rows ROWS com default sensato (ex.: 200) e paginação por (timestamp, guid) como cursor; incluir guid no ORDER BY para desempate determinístico. Definir política de retenção/arquivamento da tabela de log (expurgo por data, job de housekeeping) antes do go-live: hoje o crescimento é ilimitado e nada no modelo prevê expurgo.

### [DM-09] seqnr vem do payload do chamador e é chave do MODIFY — linhas de resultado do batch se sobrescrevem

**Onde:** `§2.1 zrouter_batch_result chave (linhas 125-127); §8 save_batch_result (1071-1083) e execute_batch (1089-1110)`

**Problema:** A chave é (client, batch_guid, seqnr) e save_batch_result recebe iv_seqnr = ls_action-seqnr, ou seja, o número de sequência é fornecido pelo cliente HTTP/RFC dentro do JSON (ty_batch_action-seqnr TYPE i). O loop nunca deriva a sequência de sy-tabix. Como a gravação é MODIFY (upsert por chave), duas ações com o mesmo seqnr colapsam em uma única linha. Não há validação de unicidade nem de valor positivo.

**Falha concreta:** Agente envia batch com 3 ações e omite seqnr (campo ausente no JSON, /ui2/cl_json deixa 0 nas três). O MODIFY grava a linha (batch_guid, 0) três vezes, cada uma sobrescrevendo a anterior. ZROUTER_BATCH_RESULT fica com 1 linha — a da última ação — enquanto rs_result-results em memória tem 3 itens. A persistência do batch diverge do retorno, e uma escrita bem-sucedida no meio do lote desaparece do registro. Um chamador malicioso consegue apagar deliberadamente o rastro de uma ação anterior reenviando o mesmo seqnr.

**Correção:** Derivar seqnr no servidor: 'DATA(lv_seq) = sy-tabix.' dentro do LOOP (ou contador próprio), ignorando o valor recebido; manter o seqnr do chamador, se útil, num campo não-chave 'client_seqnr'. Trocar MODIFY por INSERT e tratar sy-subrc <> 0 como cx_zrouter (M400) — em tabela de auditoria, colisão de chave é incidente, não upsert silencioso.

### [DM-10] Handler comita por conta própria dentro do batch: a atomicidade prometida pelo spec não existe

**Onde:** `§8 — zcl_zrouter_handler_fi~post_document linhas 738/741 vs zcl_zrouter_batch~execute_batch linhas 1114/1120`

**Problema:** post_document chama BAPI_TRANSACTION_COMMIT ao final de cada item. execute_batch, ao detectar erro num item posterior, chama BAPI_TRANSACTION_ROLLBACK esperando desfazer o lote (comentário na linha 1115: 'garantir atomicidade'). Um COMMIT já executado encerrou a LUW — o rollback subsequente não alcança nada. É exatamente a golden rule 'no-batch-double-commit' da §6 do model-library-design.md invertida, e contradiz a promessa da §1.2 do spec ('rollback automático em caso de falha').

**Falha concreta:** Batch = [FI POST_DOCUMENT (ok, comita), MM CREATE_MATERIAL (falha)]. execute_batch marca ERROR, chama ROLLBACK e retorna status 'ERROR' com results contendo o item 1 como SUCCESS. O documento contábil ficou lançado em produção; o agente e o operador recebem 'ERROR' no batch inteiro e assumem que nada foi gravado. Divergência contábil silenciosa, sem estorno.

**Correção:** Nenhum handler de item pode comitar ou rolar back: mover BAPI_TRANSACTION_COMMIT/ROLLBACK exclusivamente para o orquestrador (execute_batch para lote; dispatch para chamada isolada), como já prescreve o zcl_tmpl_handler.clas.abap aprovado (comentário do GOLDEN PATTERN). Se atomicidade multi-BAPI real for requisito, declarar explicitamente quais ações são elegíveis a lote via o campo batchable (hoje nunca lido — ver DM-13) e recusar o batch quando qualquer item não for batchable.

### [DM-11] Não há campo de correlação entre ZROUTER_LOG e ZROUTER_BATCH_RESULT; e o batch_result não registra usuário

**Onde:** `§2.1 zrouter_log (104-117) e zrouter_batch_result (121-135); §8 execute_batch linha 1128 (batch_guid dentro do texto da mensagem)`

**Problema:** ZROUTER_LOG tem guid próprio mas nenhum batch_guid/parent_guid; ZROUTER_BATCH_RESULT tem batch_guid mas nenhum log_guid. A única ligação existente é o batch_guid interpolado no texto livre da mensagem de resumo ('Batch { guid } completed with N actions'), campo char(255) sujeito a truncamento (DM-06) e não pesquisável por índice. Pior: log_action devolve rv_guid e execute_batch descarta o retorno, então nem seria difícil gravar o vínculo. Além disso ZROUTER_BATCH_RESULT não tem username — a tabela que registra escrituras em lote não guarda quem as executou.

**Falha concreta:** Auditoria pergunta 'quais chamadas o agente fez no batch 5F3A...?'. Não existe SELECT que responda: é preciso varrer ZROUTER_LOG com LIKE '%5F3A%' sobre message (full scan, sem índice) e ainda assim só encontrar a linha de resumo, nunca as linhas por item — que foram gravadas por log_action sem qualquer referência ao batch. E, ao olhar ZROUTER_BATCH_RESULT, não há como dizer sob qual usuário o lote rodou.

**Correção:** Em ZROUTER_LOG acrescentar 'batch_guid : sysuuid_c32;' (inicial para chamadas isoladas) e 'seqnr : abap.int4;', com índice secundário (client, batch_guid, seqnr). Em ZROUTER_BATCH_RESULT acrescentar 'log_guid : sysuuid_c32;' preenchido com o retorno de log_action, mais 'username : syuname;'. Propagar o batch_guid pelo dispatch (parâmetro opcional iv_batch_guid) até o logger, em vez de mantê-lo apenas na classe de batch.

### [DM-17] Registry zai_skills não tem DDL em artefato nenhum e seu conteúdo é usado como nome de classe em instanciação dinâmica

**Onde:** `zcl_zrouter~process_request linhas 167-169 (SELECT SINGLE handler_class FROM zai_skills) e zcl_execution_engine~run linha 45 (CREATE OBJECT lo_exec TYPE (iv_class))`

**Problema:** O template do ICF handler resolve o intent lendo handler_class de zai_skills e passa o valor direto para CREATE OBJECT ... TYPE (iv_class). A tabela zai_skills não está definida em nenhum dos artefatos: não há DDL, não há chave, não se sabe se é cliente-dependente, não há campo active, não há classe de entrega, não há coluna que diga se o handler escreve. Além disso ela concorre com ZROUTER_CONFIG — dois registries divergentes para o mesmo conceito, um em cada artefato. E o SELECT não filtra por cliente nem por flag de ativação.

**Falha concreta:** Qualquer usuário com autorização de manutenção sobre zai_skills (uma tabela Z sem classe de entrega definida, portanto provavelmente #A com manutenção permitida por S_TABU_DIS genérico) altera handler_class de um intent de leitura para o nome de uma classe qualquer do sistema. O ZROUTER passa a instanciar essa classe e a chamar execute( ) nela sob o usuário de serviço do ICF, sem passar por ZROUTER_CONFIG, sem AUTHORITY-CHECK e sem log em ZROUTER_LOG — o handler HTTP não chama nada de zcl_zrouter_authority. Escrita arbitrária a partir de uma linha de tabela, exatamente o que o invariante do produto proíbe.

**Correção:** Ou eliminar zai_skills e unificar tudo em ZROUTER_CONFIG (recomendado, uma fonte só), ou modelá-la formalmente: DDL com key client, key intent_id, handler_class, active, write_op, deliveryClass #C, dataMaintenance #RESTRICTED com view de manutenção protegida por objeto de autorização próprio. Em qualquer caso, substituir a instanciação dinâmica por um factory com CASE fechado sobre um conjunto de classes conhecidas em tempo de compilação (o padrão que get_handler_for_module já usa na §8 do spec) — nome de classe vindo de tabela é execução de dado, e viola a golden rule 'no-eval-expression'.

### [F06] DOCUMENTHEADER passado como TABLES em BAPI_ACC_DOCUMENT_POST

**Onde:** `linhas 732-735: CALL FUNCTION 'BAPI_ACC_DOCUMENT_POST' TABLES documentheader = lt_doc_header return = lt_ret`

**Problema:** Em BAPI_ACC_DOCUMENT_POST, DOCUMENTHEADER é parâmetro IMPORTING do FM (estrutura única BAPIACHE09), não parâmetro TABLES. Passá-lo sob a cláusula TABLES (e como tabela lt_doc_header TYPE TABLE OF bapiache09) é incompatibilidade de categoria de parâmetro -> erro de sintaxe no CALL FUNCTION. Além disso OBJ_KEY (EXPORTING) nunca é capturado, então lv_obj_key fica sempre inicial.

**Falha concreta:** Verificação de sintaxe do CALL FUNCTION -> 'DOCUMENTHEADER não é um parâmetro TABLES do módulo de função'. Não compila.

**Correção:** Usar EXPORTING documentheader = ls_doc_header (estrutura BAPIACHE09) e TABLES accountgl/accountpayable/currencyamount/return = ...; capturar IMPORTING obj_key = lv_obj_key. Verificar a interface real do BAPI no sistema alvo.

### [F3] A coluna 'Modo Escrita' so existe na doc; o schema de runtime nao distingue leitura de escrita

**Onde:** `ZROUTER_CONFIG L84-100; ty_config_entry L267-275; tabela 'Modo Escrita' L1163-1170`

**Problema:** A coluna 'Modo Escrita' da secao 9 e decorativa - nao aparece em ZROUTER_CONFIG (client/module/action/active/batchable/timeout) nem em ty_config_entry (module/action/active/batchable/timeout). O dispatcher nao tem como saber em runtime se uma acao grava. O flag active so diz 'habilitada', nao 'somente leitura'. Ou seja: o registry mistura leitura e escrita e a unica marcacao read/write vive em prosa, nunca chega ao codigo.

**Falha concreta:** Para construir um filtro read-only nao ha campo a consultar: is_action_allowed devolve true tanto para GET_MATERIAL quanto para CREATE_MATERIAL; nada no config permite recusar so as de escrita.

**Correção:** Adicionar um flag read_only/write em ZROUTER_CONFIG e em ty_config_entry, e nao confiar apenas nele - a classificacao read/write tambem tem que ser reforcada na fronteira do desktop (enum fechado proprio), porque a config SAP e controlada pelo cliente (ver F6).

### [F6] Superficie de tool definida por linhas de ZROUTER_CONFIG no SAP, nao por enum fechado revisado

**Onde:** `is_action_allowed L376-383 e check_authority L455-471 vs tool-ops.schema.json (enum fechado das 9 ops)`

**Problema:** Em TheBug o catalogo e um enum fechado (tool-ops.schema.json), versionado e coberto por scan-secrets/contract-review; e a fronteira ui vs mcp que e o gate (desktop-shell/CLAUDE.md L284-288: 'quem esta sendo verificado nao pode ler nem escrever o veredito'). No ZROUTER a allowlist sao linhas em ZROUTER_CONFIG e roles SU21/PFCG - controle do cliente, fora do desktop. Alem disso is_action_allowed e cl_abap_authorization autorizam a identidade tecnica com que o desktop conecta, que e a MESMA que o agente dirige; logo config/role SAP nao substitui o gate de fronteira do desktop. Falta a separacao de escopo equivalente a do bridge (ui vs mcp).

**Falha concreta:** Cliente adiciona linha active='X' para FI_POST_DOCUMENT e concede ZROUTER_FI_POST_DOCUMENT a conta de servico -> escrita habilitada sem passar pelo review do desktop nem por ADR; o desktop nem sabe que a superficie mudou.

**Correção:** O desktop declara sua propria allowlist read-only fechada (contrato v1 espelhando tool-ops.schema.json) e nunca deriva a superficie de tool da config SAP. A config/role SAP vira defesa em profundidade, nao o gate. Separar escopos: o token do agente so alcanca o subconjunto read-only.

### [F8] Caminho para preservar o invariante ao consumir o ZROUTER por HTTP

**Onde:** `catalogo mcp do agente + escopos ui/mcp do bridge (desktop-shell/CLAUDE.md L269-291) + ADR-0001`

**Problema:** Resposta a pergunta central, consolidada: como desenhado, o invariante 'escrita nunca entra no catalogo' NAO se mantem. Para mante-lo: (1) so handlers read-only de dados de negocio (GET_*) entram no catalogo mcp, declarados por um enum fechado proprio do desktop, nao pela config SAP; (2) o dispatcher/ICF recusa acoes de escrita salvo pelo caminho gated; (3) acoes mutaveis, se desejadas, seguem exatamente o ADR-0001 (pendencia no bridge escopo mcp, aprovacao humana por acao com payload literal na UI escopo ui, allowlist, auditoria, off por default) e exigem ADR novo; (4) flag read/write em ZROUTER_CONFIG como defesa em profundidade, sem confiar nela como gate unico; (5) nunca expor o template HTTP generico (F4) nem o REPL (F5).

**Falha concreta:** Sem esses cortes, expor o endpoint unico de dispatch como tool = CREATE_MATERIAL/POST_DOCUMENT/batch no catalogo, comitando sem gate -> regressao direta do P0-8 que o invariante #1 existe para impedir.

**Correção:** Implementar (1)-(5). Regra pratica: tratar qualquer acao mutavel do ZROUTER como o thebug-sap-gui (gated, com ADR), e nunca como o thebug-sap-adt (read-only no catalogo).

### [SEC-04] Detecção de sistema produtivo contornável pelo parâmetro sap-client da URL

**Onde:** `zcl_abap_repl=>is_production_system, linhas 289-295; uso em handle_post linha 128`

**Problema:** O guard lê SELECT SINGLE cccategory FROM t000 WHERE mandt = @sy-mandt e só considera produtivo cccategory = 'P'. Isso avalia o cliente da sessão, não o sistema. Um serviço ICF aceita ?sap-client=NNN, então o chamador escolhe em qual cliente a sessão roda. Todo sistema produtivo tem clientes não-'P' (000 e 001 saem de fábrica com categoria 'C' ou em branco; cópias de teste e clientes de customizing também). Além disso cccategory é atributo de cliente mantido em SCC4 e alterável por quem tenha S_TABU_DIS em T000, e o próprio código executado pelo REPL pode alterá-lo.

**Falha concreta:** POST https://sap-prd:44300/sap/bc/zabap_repl?sap-client=000 com credencial de um usuário técnico do cliente 000. sy-mandt = 000, T000 devolve cccategory 'C', is_production_system retorna abap_false e o REPL executa — no hardware produtivo, com as destinations RFC produtivas, o sistema de arquivos produtivo, e com acesso aos dados do cliente produtivo via SELECT ... FROM bkpf CLIENT SPECIFIED WHERE mandt = '100'. O guard de produção não protegeu nada.

**Correção:** Nunca derivar 'é produção' de um atributo de cliente. Usar o indicador de sistema: cl_abap_system_check / a flag de alterabilidade do sistema (TADIR/TRESE via BAPI ou T000 do cliente + SCC4 combinados), e complementar com uma allowlist explícita de SYSID/instalação (sy-sysid + LICENSE_NUMBER) configurada fora do alcance da aplicação. Como o guard controla RCE, ele deve falhar fechado: qualquer erro na determinação bloqueia.

### [SEC-05] Nome do report temporário colide entre usuários: substituição de código e execução sob identidade alheia

**Onde:** `zcl_abap_repl=>execute_code, linhas 176-179 e 190-216`

**Problema:** lv_short = 'ZR' && lv_user(4) && sy-uzeit gera um nome de 12 caracteres cuja unicidade depende apenas dos 4 primeiros caracteres do usuário e do segundo do relógio. Dois usuários cujos nomes compartilham o prefixo de 4 caracteres, atendidos no mesmo segundo, produzem o mesmo lv_repname. Entre o INSERT REPORT (190) e o SUBMIT (216) existe uma janela TOCTOU sem ENQUEUE. O DELETE REPORT (211/268) também apaga o report do outro. Adicionalmente, lv_user(4) sobre CONV string( sy-uname ) provoca CX_SY_RANGE_OUT_OF_BOUNDS para nomes de usuário com menos de 4 caracteres, e como log_execution só roda depois de execute_code, o dump não deixa registro no log da aplicação.

**Falha concreta:** Atacante DEVE_ATK e vítima DEVELOPER compartilham o prefixo 'DEVE'. O atacante dispara POSTs em laço com {"code":"...payload..."} enquanto a vítima usa o REPL. Numa iteração o INSERT REPORT do atacante grava ZRDEVE143012 depois do INSERT/GENERATE da vítima e antes do SUBMIT dela: a vítima executa o código do atacante, na sessão dela, com as autorizações dela. Se a vítima for um usuário de basis, o atacante escala de desenvolvedor para administrador sem tocar em nenhuma senha. Variante de DoS: um usuário chamado 'ADM' derruba o work process a cada requisição.

**Correção:** Nome derivado de identificador realmente único por requisição (cl_system_uuid=>create_uuid_c22_static) ou, no mínimo, ENQUEUE exclusivo sobre o nome antes do INSERT REPORT e liberação só após o SUBMIT. Substituir lv_user(4) por substring( val = lv_user off = 0 len = nmin( val1 = 4 val2 = strlen( lv_user ) ) ). Na prática, a correção correta é eliminar a geração dinâmica de programas.

### [SEC-09] Instanciação dinâmica de classe escolhida por dado da requisição (no-eval-expression)

**Onde:** `zcl_execution_engine=>run, linha 45 (CREATE OBJECT lo_exec TYPE (iv_class)); origem do valor em zcl_zrouter=>process_request linhas 167-169`

**Problema:** O campo intent do JSON do atacante seleciona a linha de ZAI_SKILLS e o valor handler_class é usado em CREATE OBJECT lo_exec TYPE (iv_class). A tipagem de lo_exec como REF TO zif_ai_skill_executor limita o alvo a classes que implementam a interface (o runtime dispara CX_SY_CREATE_OBJECT_ERROR caso contrário), mas continua sendo execução dirigida por dado externo com três consequências reais: qualquer classe do sistema que implemente a interface é alcançável, o construtor da classe alvo roda como efeito colateral, e a superfície de ataque migra para quem consegue gravar em ZAI_SKILLS. ZAI_SKILLS é uma tabela Z sem grupo de autorização definido no template, portanto mantível por SE16N/SM30 por quem tenha S_TABU_DIS em &NC&. O CATCH cx_root da linha 61 engole tudo, então a sondagem é silenciosa.

**Falha concreta:** Usuário com SE16N e S_TABU_DIS &NC& (perfil comum de analista) insere em ZAI_SKILLS a linha intent_id='PWN', handler_class='<classe existente que implementa zif_ai_skill_executor>'. Em seguida, ou o próprio atacante ou o agente TheBug, envia POST /sap/bc/zrouter com {"intent":"PWN","parameters":"..."} e a classe é instanciada e executada pelo caminho HTTP, sem AUTHORITY-CHECK (SEC-08) e sem registro. O registry vira um canal de execução persistente controlado por quem só tinha acesso de manutenção de tabela.

**Correção:** Substituir o registry em tabela por um CASE estático sobre intents conhecidas no código do dispatcher (como faz zcl_zrouter_dispatch=>get_handler_for_module da spec), de modo que o conjunto de classes executáveis seja fixado em tempo de transporte. Se o registry em tabela for mesmo necessário, validar o nome contra uma allowlist compilada, atribuir grupo de autorização à ZAI_SKILLS e exigir AUTHORITY-CHECK de manutenção, e nunca capturar cx_root sem registrar.

### [SEC-10] Identidade do chamador vem do corpo JSON e é repassada aos executores como usuário autor da ação

**Onde:** `zcl_zrouter=>process_request linha 160 (deserialize preenche ls_input-user) e zcl_execution_engine=>run linhas 47-50 (iv_user = is_input-user)`

**Problema:** O campo user do JSON é totalmente controlado pelo cliente e é entregue a zif_ai_skill_executor~execute como iv_user. A interface documenta esse parâmetro como a identidade do usuário, então implementações de skill vão usá-lo para decidir escopo, montar log e atribuir autoria. A identidade real da sessão é sy-uname e nunca é consultada em lugar nenhum do arquivo.

**Falha concreta:** Qualquer chamador do endpoint envia POST /sap/bc/zrouter com {"intent":"FI_POST_DOCUMENT","user":"BASIS_ADMIN","parameters":"..."}. Toda a trilha de auditoria produzida pelos handlers atribui a ação a BASIS_ADMIN. Se algum handler usar iv_user para escopar dados (por exemplo, 'mostre os pedidos do usuário X'), o atacante lê os dados de outro usuário simplesmente trocando a string. Repúdio garantido e escalonamento horizontal sem nenhuma exploração técnica.

**Correção:** Remover o campo user do contrato de entrada. Derivar a identidade exclusivamente de sy-uname dentro do handler ICF e propagá-la como parâmetro read-only para os executores. Se o agente precisar declarar um 'on behalf of', isso é um campo separado, sempre logado junto com sy-uname, e nunca usado para decisão de autorização.

### [SEC-11] Handler ICF de escrita sem token CSRF, sem verificação de método e sem limite de corpo

**Onde:** `zcl_zrouter=>if_http_extension~handle_request, linhas 143-149`

**Problema:** handle_request não valida X-CSRF-Token, não verifica Origin/Referer, não distingue GET de POST (o mesmo caminho processa qualquer método) e chama get_cdata( ) sem consultar content-length. O serviço ICF customizado não tem proteção XSRF ativa por padrão. Como /ui2/cl_json=>deserialize não levanta exceção para JSON inválido, o TRY/CATCH das linhas 157-164 é código morto e não serve de filtro.

**Falha concreta:** Usuário SAP com sessão de navegador ativa (Fiori/WebGUI aberto, cookie SAP_SESSIONID válido) visita página maliciosa contendo <form action="https://sap:44300/sap/bc/zrouter" method="POST" enctype="text/plain"> cujo campo produz o corpo {"intent":"SD_CREATE_SALES_ORDER","parameters":"{...}"}. Requisição simples de formulário não dispara preflight, o cookie viaja junto e a intent de escrita é executada com as autorizações da vítima, sem que ela clique em nada. Em paralelo, um POST com corpo de centenas de MB é materializado inteiro em string e esgota a memória do work process.

**Correção:** Validar o token XSRF do ICF (habilitar a proteção no nó SICF e checar o header no handler) em toda requisição que não seja idempotente; rejeitar métodos fora de POST; exigir Content-Type application/json exato; e ler content-length e abortar com 413 acima de um teto explícito antes de chamar get_cdata( ).

### [SEC-13] O AUTHORITY-CHECK está no orquestrador e não na operação privilegiada, e os handlers são públicos e instanciáveis

**Onde:** `Seção 8: zcl_zrouter_handler_abstract (linhas 477-549, ALIASES handle_action público) e zcl_zrouter_handler_mm/sd/fi (CREATE PUBLIC); gate em zcl_zrouter_dispatch=>validate_and_check linhas 938-949`

**Problema:** validate_and_check é o único ponto que chama zcl_zrouter_authority. Ele vive em zcl_zrouter_dispatch=>dispatch. Todos os handlers, porém, são PUBLIC ... CREATE PUBLIC, com construtor público e handle_action exposto por ALIASES e pela interface pública zif_zrouter_handler. Em ABAP não existe forma de restringir quem chama um método público de uma classe pública, então a barreira de autorização é contornável por construção: basta não passar pelo dispatcher. Nenhum handler faz AUTHORITY-CHECK próprio antes de chamar BAPI_ACC_DOCUMENT_POST, BAPI_MATERIAL_SAVEDATA ou BAPI_SALESORDER_CREATEFROMDAT2.

**Falha concreta:** Qualquer código no sistema — inclusive o futuro handler ICF do ZROUTER, que a spec não define e que quem implementar vai modelar pelo template do artefato 1 — faz NEW zcl_zrouter_handler_fi( io_logger = ... io_config = ... )->handle_action( iv_action = 'POST_DOCUMENT' iv_payload = <payload> ). Nenhum check de ZROUTER roda, nenhuma linha entra em ZROUTER_LOG pelo caminho de erro do dispatch, e a BAPI de lançamento contábil é chamada. O mesmo vale para um segundo FM RFC, um BSP ou um job que instancie o handler diretamente.

**Correção:** Mover o AUTHORITY-CHECK para dentro de handle_action da classe abstrata, como primeira instrução, antes de before_action e antes de qualquer despacho — é o padrão auth-check-first aplicado no lugar certo. O dispatcher pode manter o check como filtro rápido, mas ele não pode ser o único. Complementarmente, tornar os construtores dos handlers CREATE PRIVATE/CREATE PROTECTED com friend do dispatcher, para que a única rota de instanciação seja a auditada.

### [SEC-18] Endpoint único sem separação leitura/escrita torna o invariante read-only inaplicável fora do código ABAP

**Onde:** `zcl_zrouter=>process_request, linhas 151-189 (endpoint único, registry único em ZAI_SKILLS)`

**Problema:** Todas as intents — leitura e escrita — chegam pelo mesmo POST, no mesmo caminho ICF, com a mesma tabela de registry e o mesmo método HTTP. Não existe nenhuma dimensão (path, método, serviço SICF, objeto de autorização) sobre a qual se possa restringir o ZROUTER a leitura. O invariante do desktop-shell exige que escrita ABAP nunca entre no catálogo do agente, e a única exceção registrada (ADR-0001, thebug-sap-gui) só é aceitável porque cada ação passa por aprovação humana no bridge. O ZROUTER como desenhado não tem nem separação de superfície nem ponto de aprovação por ação: registrar o endpoint no catálogo do agente registra simultaneamente FI_POST_DOCUMENT e MM_GET_MATERIAL.

**Falha concreta:** O ZROUTER é registrado como ferramenta MCP do agente para 'cobrir o que o ADT não cobre'. O agente, seguindo instrução injetada num artefato que ele leu no SAP (um texto de item, um comentário de código, um log), emite POST /sap/bc/zrouter com {"intent":"FI_POST_DOCUMENT",...}. O basis não tem como bloquear apenas essa intent no SICF, porque o caminho e o método são os mesmos da leitura; e não há confirmação humana vinculada. O invariante cai sem que nenhuma linha do desktop-shell tenha sido alterada.

**Correção:** Separar em dois nós SICF distintos com dois handlers distintos e dois objetos de autorização distintos: um caminho estritamente de leitura (registry compilado, apenas intents sem escrita, verificado em código) e outro de escrita. Só o caminho de leitura pode ser considerado para o catálogo do agente. Qualquer intent de escrita exige ADR próprio e o mesmo mecanismo de aprovação por ação do ADR-0001, materializado no bridge e não no ABAP — e nenhuma escrita entra no catálogo antes disso.


## Médios

### [DM-12] Parâmetro RETURNING declara tipo tabela inline — a interface não ativa

**Onde:** `§8 — interface zif_zrouter_logger, método get_logs, linhas 325-330`

**Problema:** 'RETURNING VALUE(rt_logs) TYPE STANDARD TABLE OF ty_log_entry WITH EMPTY KEY' não é sintaxe válida em assinatura de método: parâmetros só podem referenciar um tipo já nomeado, a construção STANDARD TABLE OF é exclusiva de TYPES/DATA. A interface irmã zif_zrouter_config faz certo (declara ty_config_entries e referencia), o que evidencia que foi descuido e não decisão.

**Falha concreta:** Ativação de zif_zrouter_logger falha; por dependência, zcl_zrouter_logger, zcl_zrouter_dispatch, zcl_zrouter_batch e todos os handlers não ativam. O deploy inteiro para no primeiro objeto e nenhuma das camadas de persistência chega ao sistema.

**Correção:** Declarar no bloco TYPES da interface: 'ty_log_entries TYPE STANDARD TABLE OF ty_log_entry WITH EMPTY KEY.' e usar 'RETURNING VALUE(rt_logs) TYPE ty_log_entries'. Rodar abap:lint sobre a §8 antes de promover o código ao model-library (ver DM-16).

### [DM-13] batchable e timeout são persistidos e nunca lidos: controles que existem no modelo e não existem no runtime

**Onde:** `§2.1 zrouter_config linhas 93-94 (batchable, timeout); §8 db_to_config_entry 358-364, validate_and_check 938-949, execute_batch 1085-1129`

**Problema:** O registry armazena batchable e timeout, get_config os devolve, e nenhum ponto do código os consulta. validate_and_check checa apenas active + autorização; execute_batch nunca verifica batchable; nada aplica timeout. O método db_to_config_entry, que faria a conversão char->abap_bool, é código morto — load_config usa INTO CORRESPONDING FIELDS e o ignora.

**Falha concreta:** Basis marca ('FI','POST_DOCUMENT', batchable=' ') acreditando ter impedido que lançamentos contábeis entrem em lote. O agente envia um batch com 20 POST_DOCUMENT; execute_batch executa os 20 sem consultar o flag. O controle configurado não teve efeito algum e não há sinal disso em lugar nenhum — nem log, nem erro.

**Correção:** Ou implementar o enforcement (execute_batch consulta batchable de cada item e recusa o lote inteiro antes de executar qualquer ação; dispatch aplica timeout via cl_abap_*timeout/ SET RUN TIME ANALYZER equivalente), ou remover as colunas do modelo. Coluna de controle não aplicada é pior que coluna ausente, porque cria falsa sensação de contenção. Remover db_to_config_entry ou fazer load_config usá-lo explicitamente em vez de INTO CORRESPONDING FIELDS.

### [DM-14] Tipos primitivos soltos onde deveriam existir elementos de dados/domínios; e abap.datn perde a hora na auditoria do allowlist

**Onde:** `§2.1 zrouter_config linhas 92-98 (active, batchable char(1); created_at/changed_at abap.datn); zrouter_log linha 111 (status char(20)) e 115 (username char(12))`

**Problema:** active e batchable são abap.char(1) cru, sem domínio de valores fixos: qualquer valor entrável ('Y','1','n') é aceito pelo DDIC e db_to_config_entry mapeia tudo que não seja 'X' para false. status é abap.char(20) livre embora só existam SUCCESS|ERROR. username é abap.char(12) em vez de syuname/xubname. created_at/changed_at são abap.datn — só data, sem hora — numa tabela cuja auditoria de alteração é relevante para segurança; e datn é tipo recente com restrições de suporte em stacks mais antigos, o que é risco para uma instalação nova no sistema do cliente.

**Falha concreta:** Administrador ativa uma ação digitando 'Y' no campo active (não há checagem de domínio, não há checkbox). A leitura mapeia 'Y' -> abap_false e a ação continua bloqueada; o administrador vê 'Y' na tabela, conclui que está ativo e abre chamado. Separadamente, duas alterações no allowlist no mesmo dia (habilitar POST_DOCUMENT às 09h, desabilitar às 17h) ficam ambas com changed_at = 20260803: é impossível ordenar os eventos e determinar qual valia no momento de uma escrita investigada.

**Correção:** active/batchable/write_op como abap_boolean (ou xfeld) para herdar o domínio 'X'/' '; status com domínio de valores fixos próprio (ZROUTER_STATUS) ou elemento de dados dedicado; username como syuname; created_at/changed_at como timestampl ou abap.utclong (mesmo tipo escolhido em DM-05). Manter created_by/changed_by como syuname e torná-los not null para o registro de auditoria.

### [DM-15] O 'cache' de config não cacheia e não tem invalidação: full read do registry a cada requisição, e desativação sem efeito garantido

**Onde:** `§8 — zcl_zrouter_config (lt_config_cache, linha 341), load_config (349-356), zcl_zrouter_dispatch~constructor (932-936)`

**Problema:** lt_config_cache é atributo de instância; zcl_zrouter_dispatch instancia zcl_zrouter_config no construtor e o FM instancia um dispatch novo por chamada — o cache é reconstruído a cada requisição. load_config lê TODAS as linhas do registry (sem WHERE por module/action) para responder a uma única consulta. E o carregamento é 'IF lt_config_cache IS INITIAL', sem qualquer invalidação explícita — exatamente a golden rule 'config-cache-refresh' da §6 do model-library-design.md violada.

**Falha concreta:** Com 2.000 linhas no registry, cada chamada HTTP do desktop dispara um SELECT completo de zrouter_config antes de qualquer trabalho útil. Pior no cenário oposto: se alguém 'otimizar' tornando lt_config_cache estático (é a correção óbvia e errada), desativar uma ação de escrita (active=' ') deixa de ter efeito nos work processes que já carregaram o cache — a ação continua sendo executada até o próximo restart, sem nenhum indicador. Um kill-switch de segurança que não desliga.

**Correção:** Buscar apenas a linha necessária ('SELECT SINGLE ... WHERE module = @iv_module AND action = @iv_action') para is_action_allowed/get_config, e reservar o carregamento completo para get_all_config. Se buffer for necessário, usar buffer de tabela do DDIC (single-record buffering na chave) em vez de cache em memória de aplicação, ou implementar invalidação explícita por timestamp de alteração do registry, com TTL curto documentado.

### [DM-16] As três tabelas só existem dentro de um markdown, fora de model-library/src — logo, fora do gate de CI — e divergem do padrão aprovado

**Onde:** `§2.1 completo vs src/ztmpl_table.tabl.ddl; docs/model-library-design.md §6 (gate de CI) e §8 item 5`

**Problema:** O design (§6 e §11) estabelece que abap:lint + ATC rodam contra model-library/src/**, e a §8 item 5 registra que os templates DDIC ztmpl_config/ztmpl_log estão faltando ('no copy currently defines them'). As três tabelas do ZROUTER continuam existindo apenas como bloco de código em ZROUTER_TECHNICAL_SPEC.md — nenhum linter, nenhum ATC, nenhuma revisão automatizada as alcança. Isso explica por que os defeitos DM-04, DM-05 e DM-06 sobreviveram a uma revisão que o próprio spec descreve como '100% de conformidade com Clean ABAP'. Divergências concretas em relação ao ztmpl_table.tabl.ddl aprovado: guid como abap.char(32) em vez do elemento sysuuid_c32; payload como abap.char(1024) em vez de abap.string; larguras arbitrárias (module 30 vs 10, action 60 vs 40, status 20 vs 10) sem justificativa registrada.

**Falha concreta:** Alguém gera a instalação do cliente a partir do spec (copiar/colar do markdown para o ADT). Nenhum passo do pipeline detecta o abap.syst_lo05 inválido nem as annotations ausentes; o erro só aparece no sistema do cliente, na janela de instalação, com o consultor na frente do usuário. E como não há arquivo versionado, a correção feita no cliente nunca volta para o repositório — a próxima instalação repete o mesmo erro.

**Correção:** Materializar model-library/src/ddic/ztmpl_config.tabl.ddl e ztmpl_log.tabl.ddl (mais ztmpl_batch_result) com o token TMPL, registrá-los em manifest.json com golden_rules próprias, e passar a gerar ZROUTER_CONFIG/LOG/BATCH_RESULT a partir deles. Fazer do spec um consumidor da biblioteca, não uma segunda fonte de verdade. Alinhar guid a sysuuid_c32 e payload a abap.string; onde a largura divergir do template, documentar o motivo na entrada do manifest.

### [F07] Comparação de coluna timestamp (timestampl) com host vars de data (dats)

**Onde:** `linha 428 'DATA(lv_date_to) = iv_date + 1.' e linha 433 'timestamp >= @lv_date_from AND timestamp < @lv_date_to'`

**Problema:** iv_date é TYPE dats (AAAAMMDD, 8 dígitos). A coluna timestamp é um timestamp (14+ dígitos, AAAAMMDDHHMMSS...). Comparar timestamp >= 20260803 e timestamp < 20260804 nunca casa um timestamp real daquele dia (ex.: 20260803120000 é > 20260804). Além disso, 'iv_date + 1' num inline DATA infere tipo i (contagem de dias interna), diferente de lv_date_from (dats) -> tipos divergentes e filtro quebrado. Em Open SQL strict a comparação timestamp(dec) x dats ainda pode ser recusada por incompatibilidade de tipo.

**Falha concreta:** get_logs com iv_date preenchido -> retorna 0 linhas para qualquer registro do próprio dia (filtro logicamente impossível), ou erro de tipo na verificação de sintaxe.

**Correção:** Converter a data em faixa de timestamps: lv_ts_from = |{ iv_date }000000|, lv_ts_to = |{ iv_date }235959| tipados como timestampl, ou usar cl_abap_tstmp. Tipar explicitamente lv_date_to como dats se optar por aritmética de data.

### [F08] Atribuição de utclong (utclong_current) a campo timestampl

**Onde:** `linha 521 'rs_result-timestamp = utclong_current( ).' (campo timestamp é TYPE timestampl, interface linha 253)`

**Problema:** utclong_current( ) retorna tipo utclong (timestamp UTC de 8 bytes), enquanto rs_result-timestamp é timestampl (packed dec 21,7). São tipos distintos; a atribuição direta utclong -> p não é conversão definida e é rejeitada pela verificação de sintaxe (ou produz valor sem sentido). Note que o template dourado zcl_tmpl_handler usa GET TIME STAMP FIELD rs_result-timestamp para o mesmo campo, ou seja, o padrão correto foi divergido aqui.

**Falha concreta:** Ativar ZCL_ZROUTER_HANDLER_ABSTRACT -> erro/aviso de conversão utclong para tipo P, ou timestamp inválido em runtime.

**Correção:** Usar GET TIME STAMP FIELD rs_result-timestamp. (como no golden template) ou mudar o tipo do campo para utclong e usar utclong_current( ). Verificar a rejeição exata da conversão no sistema alvo.

### [F09] Método db_to_config_entry declarado e nunca chamado (código morto)

**Onde:** `método db_to_config_entry declarado linhas 343-345, implementado 358-364; load_config (349-356) usa INTO CORRESPONDING FIELDS e nunca chama db_to_config_entry`

**Problema:** db_to_config_entry faz a conversão 'X'/' ' -> abap_bool via COND, mas load_config popula lt_config_cache diretamente com SELECT ... INTO CORRESPONDING FIELDS, sem passar pelo mapeador. O método fica morto. Funciona por coincidência (DB active char1 'X'/' ' bate com abap_true/abap_false), mas o mapeamento previsto foi abandonado. Sinaliza que a intenção de design não foi implementada.

**Falha concreta:** Manutenção futura muda a semântica de 'active' esperando o mapeador -> não tem efeito, pois o método nunca roda.

**Correção:** Ou remover db_to_config_entry, ou fazer load_config selecionar em estrutura DB e chamar db_to_config_entry por linha para preencher o cache.

### [F10] Acesso lv_user(4) dá dump quando o usuário tem menos de 4 caracteres

**Onde:** `linha 176 'DATA(lv_user) = CONV string( sy-uname ).' e linha 177 'DATA(lv_short) = 'ZR' && lv_user(4) && sy-uzeit.' (fora do TRY, que só começa na linha 189)`

**Problema:** CONV string( sy-uname ) remove espaços à direita, então lv_user tem o comprimento do nome sem padding. lv_user(4) faz offset/length 4 sobre uma string; se strlen < 4 lança CX_SY_RANGE_OUT_OF_BOUNDS. Está antes do TRY (linha 189), portanto não é capturado -> short dump. Usuários com nome curto (ex.: 'ABC', usuários técnicos de 3 letras) disparam.

**Falha concreta:** POST no REPL autenticado como usuário 'ABC' -> dump CX_SY_RANGE_OUT_OF_BOUNDS na montagem do nome de report temporário, antes de qualquer proteção.

**Correção:** Usar padding/substring seguro, ex.: DATA(lv_u4) = substring( val = lv_user && '0000' off = 0 len = 4 ). ou CONV syuname( sy-uname ) mantendo char12 antes do offset.

### [F11] Dupla-commit e rollback quebrando atomicidade e apagando logs do batch

**Onde:** `handler FI faz COMMIT interno (linha 741 CALL FUNCTION 'BAPI_TRANSACTION_COMMIT') dentro de um batch que também dá COMMIT (1120) / ROLLBACK (1114); save_batch_result faz MODIFY (1082)`

**Problema:** Viola a golden rule no-batch-double-commit. Se a ação FI (post_document) já dá BAPI_TRANSACTION_COMMIT e uma ação seguinte falha, o batch chama BAPI_TRANSACTION_ROLLBACK esperando desfazer tudo, mas o documento FI já foi commitado (não desfaz). Pior: o ROLLBACK do batch também desfaz os MODIFY zrouter_batch_result e os logs ainda não commitados, perdendo a trilha de auditoria da falha.

**Falha concreta:** Batch [FI_POST_DOCUMENT ok, MM_CREATE_MATERIAL erro] -> documento FI persiste (commit interno), rollback do batch apaga os resultados/logs de batch gravados até ali; estado inconsistente e sem rastro.

**Correção:** Handlers de item não devem commitar; centralizar COMMIT/ROLLBACK único no batch (padrão handler_abstract/batch das golden rules). Persistir logs de auditoria em LUW separada (ex.: função UPDATE TASK / após o commit final).

### [F7] Ganho real = leituras de dados de negocio; risco de duplicar o ADT sem ganho

**Onde:** `tool-ops.schema.json (9 ops de repositorio) vs handlers GET_MATERIAL/GET_SALES_ORDER/GET_BALANCE spec L603-761`

**Problema:** O ADT cobre metadados de repositorio/dev (ADT_READ_SOURCE, ADT_READ_PROPERTIES, ADT_SEARCH_OBJECT, ADT_DISCOVERY, ADT_LIST_INACTIVE_OBJECTS, ADT_READ_TRANSPORT[_CONTENTS], ADT_SYNTAX_CHECK, ADT_WHERE_USED) - nao le dados de negocio nem chama BAPI. As leituras do ZROUTER (GET_MATERIAL, GET_SALES_ORDER, GET_BALANCE) sao territorio novo e sao o ganho legitimo e compativel com o invariante. Nao ha ganho nenhum em o ZROUTER reexpor leitura de source/estrutura/objeto que o ADT ja faz read-only: duplicaria uma superficie ja controlada por uma pior controlada.

**Falha concreta:** Adicionar handlers 'read source' ou 'search object' ao ZROUTER -> duplica ADT_READ_SOURCE/ADT_SEARCH_OBJECT com menos governanca e zero capacidade nova, ampliando a superficie de ataque sem beneficio.

**Correção:** Escopar o ZROUTER a leituras de dados de negocio (GET_* via BAPI) que o ADT nao cobre; nao reimplementar leituras de repositorio do ADT. Esse subconjunto read-only e o unico que deveria ser considerado para o catalogo mcp.

### [F9] O 'rollback automatico' do batch nao e atomico - handlers ja comitaram

**Onde:** `execute_batch L1085-1129; handler_fi post_document comita internamente L741`

**Problema:** execute_batch faz BAPI_TRANSACTION_ROLLBACK na primeira falha (L1114), mas os handlers de escrita ja chamaram BAPI_TRANSACTION_COMMIT dentro do item anterior (ex.: post_document L741). O rollback so afeta a LUW corrente, nao desfaz itens ja comitados. Viola a golden rule no-batch-double-commit (model-library-design.md secao 6). A promessa de atomicidade que a spec usa para 'justificar' deixar o agente disparar lotes (secao 1.2, 'Rollback & Logs Consolidados') e falsa.

**Falha concreta:** Batch [POST_DOCUMENT ok, CREATE_MATERIAL falha] -> o documento FI ja foi comitado e permanece; o rollback nao o remove -> estado parcial persistido, exatamente o oposto da atomicidade anunciada.

**Correção:** Nenhum handler de item deve comitar; commit/rollback unico no orquestrador ao fim do lote. Secundario porem: a correcao primaria e nao deixar escrita/batch no catalogo (F1/F8) - atomicidade correta nao torna o batch elegivel ao catalogo do agente.

### [SEC-06] Trilha de auditoria truncada em 50 caracteres, gravada só após a execução e com falhas silenciadas

**Onde:** `zcl_abap_repl=>log_execution, linhas 298-339 (truncamento em 320-324); chamada em handle_post linha 148`

**Problema:** ls_msg-msgv1 = iv_code(lv_len) com lv_len limitado a 50 registra apenas os 50 primeiros caracteres do código submetido; o restante nunca é persistido. log_execution é chamado depois de execute_code, então qualquer dump, timeout ou rollback durante a execução deixa a requisição sem registro nenhum. As três chamadas BAL (BAL_LOG_CREATE, BAL_LOG_MSG_ADD, BAL_DB_SAVE) usam EXCEPTIONS OTHERS = 1 e o sy-subrc só é testado na primeira, de modo que falha de gravação passa despercebida. Como consequência inversa, se os 50 primeiros caracteres contiverem literal de senha (padrão comum em snippet que abre cl_http_client), a credencial vai para BALDAT, legível por qualquer usuário com SLG1.

**Falha concreta:** O atacante envia {"code":"\" padding inofensivo para encher o log de auditoria\n<payload real>"}. O SLG1 do objeto ZREPL/EXEC mostra apenas o comentário de padding; o que foi realmente executado não existe em lugar nenhum. Investigação pós-incidente não consegue reconstruir a ação. Se em vez disso o atacante provocar um dump (SEC-05), nem essa linha existe.

**Correção:** Persistir o hash SHA-256 do código completo mais o código integral em um campo string de tabela de log própria (não em msgv1), gravar a linha ANTES da execução com status 'STARTED' e atualizá-la depois, e tratar sy-subrc de cada chamada BAL — falha de auditoria deve abortar a operação, não ser ignorada.

### [SEC-07] GET sem AUTHORITY-CHECK expõe SYSID, mandante, usuário e o estado do guard de produção

**Onde:** `zcl_abap_repl=>handle_get, linhas 79-88 (chamada em handle_request linha 66, sem check_authorization)`

**Problema:** handle_request roteia GET direto para handle_get sem passar por check_authorization( ). O JSON devolvido contém sy-uname, sy-sysid, sy-mandt e o resultado de is_production_system( ). Viola auth-check-first e entrega ao atacante exatamente o reconhecimento de que ele precisa para explorar SEC-04.

**Falha concreta:** GET /sap/bc/zabap_repl?sap-client=000 com qualquer credencial válida (ou nenhuma, se o nó SICF tiver logon data). A resposta informa o SYSID, o mandante e 'production':false. O atacante descobre, sem tentar nada destrutivo e sem gerar log (handle_get não chama log_execution), qual combinação sistema+mandante desliga o guard de produção, e em seguida executa SEC-01 por lá.

**Correção:** Aplicar o mesmo gate de autorização em todos os métodos HTTP antes de qualquer trabalho ou resposta, e não devolver identidade de sistema em endpoint de health check. Se um endpoint de status for necessário, ele responde apenas {"status":"ready"}.

### [SEC-14] Mensagens de erro distinguem 'ação não configurada' de 'não autorizado': oráculo de enumeração do registry e das autorizações

**Onde:** `Seção 8: zcl_zrouter_dispatch=>validate_and_check linhas 938-949 e dispatch linhas 986-995; propagado por ZROUTER_DISPATCH_FM linha 1155`

**Problema:** validate_and_check produz dois textos distintos: 'Action X for Y not allowed' quando não há linha em ZROUTER_CONFIG, e 'Not authorized for Y/X' (vindo de zcl_zrouter_authority) quando a linha existe mas o usuário não tem a autorização. Ambos são devolvidos verbatim em EV_RETURN_MESSAGE. Um terceiro estado, 'Unknown module', diferencia módulos existentes. Isso entrega ao chamador não autorizado o mapa completo do que existe e do que ele quase pode fazer.

**Falha concreta:** Usuário técnico com S_RFC amplo (situação comum em usuários de interface: S_RFC com FUGR = *) mas sem nenhuma autorização no objeto ZROUTER chama ZROUTER_DISPATCH_FM em laço variando IV_MODULE e IV_ACTION. Pelas mensagens ele reconstrói todo o registry ZROUTER_CONFIG, descobre quais ações de escrita estão ativas em produção e, ao repetir o teste com contas diferentes, mapeia quais contas possuem quais valores de ZROUTER. É reconhecimento completo antes do ataque, e o custo é zero.

**Correção:** Um único texto genérico para o chamador em todos os casos de recusa ('operation not permitted') mais um id de correlação. A distinção entre inexistente, inativo e não autorizado fica apenas no ZROUTER_LOG. Adicionalmente, registrar as recusas em log — hoje 'not allowed'/'not authorized' geram linha via dispatch, mas ela pode ser desfeita (ver SEC-15).

### [SEC-15] Rollback do batch apaga as linhas de auditoria do item que falhou enquanto os COMMITs internos dos handlers preservam as escritas anteriores

**Onde:** `Seção 8: zcl_zrouter_batch=>execute_batch linhas 1085-1129 (BAPI_TRANSACTION_ROLLBACK linha 1114) combinado com zcl_zrouter_handler_fi=>post_document linhas 728-744 (COMMIT interno linha 741)`

**Problema:** O handler FI chama BAPI_TRANSACTION_COMMIT dentro do próprio post_document, violando no-batch-double-commit. Já execute_batch chama BAPI_TRANSACTION_ROLLBACK ao primeiro erro. Como INSERT zrouter_log (zcl_zrouter_logger, linha 420) e MODIFY zrouter_batch_result (save_batch_result, linha 1082) são gravações de banco na mesma LUW e não são comitadas separadamente, o ROLLBACK do batch descarta exatamente as linhas de auditoria escritas após o último COMMIT — isto é, as do item que falhou. As escritas de negócio já comitadas por handlers anteriores permanecem. Auditoria e dado de negócio ficam desalinhados na direção errada.

**Falha concreta:** O atacante monta um batch com um único item, ou com o item de sondagem na última posição: [{module:'FI',action:'POST_DOCUMENT',...}]. A ação é recusada, dispatch grava a linha de erro em ZROUTER_LOG, save_batch_result grava a linha em ZROUTER_BATCH_RESULT, e em seguida execute_batch executa BAPI_TRANSACTION_ROLLBACK, desfazendo as duas. Repetindo isso, ele varre todo o registry testando quais ações consegue executar e não deixa nenhuma linha de log de tentativa negada. Quando encontra uma que passa, a escrita de negócio ocorre e é comitada pelo handler. Sondagem silenciosa com trilha limpa.

**Correção:** Auditoria não pode compartilhar LUW com o dado de negócio: gravar log em unidade de trabalho separada (função em UPDATE TASK dedicada ou COMMIT WORK próprio antes do rollback do negócio, ou ainda BAL com BAL_DB_SAVE que já usa LUW própria). E retirar os COMMIT/ROLLBACK de dentro dos handlers: o dono do estado transacional é o batch, conforme a regra no-batch-double-commit da seção 6 do model-library-design.

### [SEC-16] Tabelas de log persistem o payload bruto das requisições sem restrição de manutenção nem grupo de autorização de tabela

**Onde:** `Seção 2.1: DDL de zrouter_log (linhas 106-117) e zrouter_batch_result (linhas 124-135); gravação em zcl_zrouter_logger=>log_action linha 416 e save_batch_result linha 1079`

**Problema:** zrouter_log.payload e zrouter_batch_result.payload guardam char(1024) do JSON enviado pelo agente, e result guarda a resposta. As definições DDL não declaram @AbapCatalog.dataMaintenance : #RESTRICTED (que o template aprovado ztmpl_table.tabl.ddl declara) e não há menção a grupo de autorização de tabela em TDDAT. Sem entrada em TDDAT, a tabela cai no grupo &NC&, que é concedido de forma ampla na maioria das instalações. Os payloads de FI e HCM contêm dados de folha, dados bancários e dados pessoais; payloads de integração frequentemente contêm segredos.

**Falha concreta:** Analista com SE16N e S_TABU_DIS para &NC& — combinação corriqueira — executa SE16N sobre ZROUTER_LOG e lê o histórico completo de tudo que o copiloto TheBug enviou ao SAP, incluindo os payloads de HCM_* e FI_*. Ele nunca teve autorização para as transações correspondentes, mas o log do gateway entrega os dados já extraídos e concentrados num único lugar.

**Correção:** Declarar @AbapCatalog.dataMaintenance : #RESTRICTED nas três tabelas, criar entrada em TDDAT com grupo de autorização dedicado (ex.: ZROU) e exigir S_TABU_DIS nesse grupo. Não persistir payload bruto: gravar apenas os campos necessários, com mascaramento explícito dos campos sensíveis, ou apenas o hash do payload. O mesmo endurecimento vale para ztmpl_table.tabl.ddl, que tem #RESTRICTED mas segue sem grupo de autorização e guarda payload como abap.string sem limite.

### [SEC-19] Valor de autorização montado por concatenação ilimitada num campo SU20 de tamanho fixo: ações distintas colapsam no mesmo valor

**Onde:** `Seção 5.1/5.2 (linhas 170-184) e zcl_zrouter_authority=>check_authority linha 457`

**Problema:** O desenho usa um único campo de autorização (ACTIVITY) cujo valor é |ZROUTER_{ iv_module }_{ iv_action }|. Módulo é char(30) e ação é char(60) na ZROUTER_CONFIG, então o valor construído chega a quase 100 caracteres, enquanto um campo de autorização SU20 tem no máximo 40 caracteres e os valores em AGR_1251 são CHAR40. O que exceder é truncado, e o AUTHORITY-CHECK compara valores truncados. Além disso, o separador '_' é ambíguo porque ambos os componentes podem contê-lo. Modelar módulo e ação como um único campo concatenado, em vez de dois campos de autorização independentes, é o erro de base.

**Falha concreta:** O papel concede ZROUTER ACTIVITY = 'ZROUTER_FI_GET_DOCUMENT_HEADER_DETAIL' a um perfil de leitura. Uma segunda ação cujo nome compartilhe o mesmo prefixo até o limite do campo — por exemplo ZROUTER_FI_GET_DOCUMENT_HEADER_DETAIL_AND_POST — é truncada para o mesmo valor e passa no check. O usuário de leitura executa a ação de escrita. Como o valor é montado em runtime e nunca validado contra o comprimento do campo, o basis não tem como perceber a colisão no PFCG.

**Correção:** Definir o objeto ZROUTER com dois campos de autorização separados (ZROU_MOD e ZROU_ACT) e verificar ambos no mesmo AUTHORITY-CHECK, mais um campo ACTVT padrão distinguindo leitura (03) de execução/escrita (16/01/02). Nunca concatenar. Validar em tempo de cadastro que os nomes de módulo e ação cabem nos respectivos campos e normalizar para maiúsculas antes do check, coerente com o to_upper usado no despacho.


## Baixos

### [F12] Campo exportado 'action' nunca é preenchido

**Onde:** `build_result (516-522) não seta rs_result-action; handle_action (534-548) idem; dispatch copia rs_result-action = ls_handler_result-action (982)`

**Problema:** ty_action_result tem o campo action, mas nenhum ponto o preenche (build_result seta status/message/data/module/timestamp; handle_action não seta). dispatch e o FM RFC propagam sempre action vazio. Campo exportado que nunca recebe valor.

**Falha concreta:** Cliente MCP recebe result com 'action' sempre em branco, perdendo correlação da ação executada.

**Correção:** Passar iv_action para build_result e atribuir rs_result-action, ou setar rs_result-action = iv_action em handle_action antes de retornar.

### [F13] Cálculo de runtime com sy-uzeit fica negativo ao cruzar a meia-noite

**Onde:** `linhas 169 e 272-273: lv_start = sy-uzeit; lv_end = sy-uzeit; ev_runtime = ( lv_end - lv_start ) * 1000.`

**Problema:** sy-uzeit é hora do dia (T). Se a execução atravessa 00:00, lv_end < lv_start e o runtime vira negativo. Também a resolução é só de segundos (o *1000 sempre dá múltiplos de 1000, 'runtime_ms' enganoso).

**Falha concreta:** Execução iniciada 23:59:59 e terminada 00:00:01 -> ev_runtime negativo (~ -86398000 ms) reportado no JSON.

**Correção:** Usar GET RUN TIME FIELD / timestamps (GET TIME STAMP + cl_abap_tstmp=>subtract) para medir duração monotônica em vez de sy-uzeit.

### [F14] Atribuição string(JSON) -> matnr semanticamente incorreta

**Onde:** `linha 590 'lv_material = iv_payload.' (iv_payload TYPE string, lv_material TYPE matnr)`

**Problema:** iv_payload é o payload JSON inteiro (string). A conversão string -> matnr (char) compila, mas trunca/preenche e coloca o JSON bruto como número de material. Nada desserializa o payload para preencher ls_header (BAPIMATHEAD fica vazio) antes do BAPI. Não dá dump, mas o material 'criado' é lixo e o BAPI receberá header vazio.

**Falha concreta:** CREATE_MATERIAL com payload {'material':'X'} -> lv_material recebe a string JSON truncada; BAPI_MATERIAL_SAVEDATA roda com headdata inicial e retorna erro (ou cria nada).

**Correção:** Desserializar iv_payload em estrutura DDIC (nested-table-deser) para preencher ls_header e derivar o material corretamente, conforme golden rule. Verificar também a existência real de BAPI_MATERIAL_GETALL / bapi_material_getall_data usados em get_material.

### [F15] cx_zrouter seta t100key inicial e não redefine get_text (diverge do golden zcx_tmpl)

**Onde:** `constructor linhas 234-238: 'if_t100_message~t100key = textid.' sem fallback default_textid; get_text não redefinido`

**Problema:** Todos os callers usam RAISE ... EXPORTING mv_text = ... sem textid, então textid é inicial e if_t100_message~t100key fica em branco. O golden zcx_tmpl trata isso com if_t100_message=>default_textid e redefine get_text para devolver mv_text. Aqui get_text( ) devolve texto T100 vazio; só funciona porque o dispatch lê lx_zrouter->mv_text direto. Não dá dump, mas qualquer consumidor que chame get_text( ) recebe string vazia e a mensagem se perde.

**Falha concreta:** Exceção cx_zrouter logada via get_text( ) por código futuro -> mensagem vazia em vez do texto de erro.

**Correção:** Replicar o padrão de zcx_tmpl: IF textid IS INITIAL. if_t100_message~t100key = if_t100_message=>default_textid. ELSE ... e METHODS get_text REDEFINITION retornando mv_text quando preenchido.

### [F16] TRY/CATCH cx_root em volta de SUBMIT não captura dumps do programa submetido

**Onde:** `linhas 215-220: TRY. SUBMIT (lv_repname) AND RETURN EXPORTING LIST TO MEMORY. CATCH cx_root INTO DATA(lx_submit). ...`

**Problema:** Um erro de runtime no programa submetido (código arbitrário do usuário) gera short dump na execução daquele report; não é uma exceção catchable que retorne ao chamador via TRY/CATCH. O handler CATCH cx_root aqui é praticamente morto para a maioria dos erros de runtime do código gerado, dando falsa sensação de proteção.

**Falha concreta:** Código submetido faz divisão por zero -> dump CX_SY_ZERODIVIDE no report gerado, não capturado pelo TRY; o REPL não retorna o JSON de erro esperado.

**Correção:** Não é possível capturar dumps de outro programa por TRY/CATCH; para isolar, validar/gerar com salvaguardas ou capturar via mecanismo de log de dumps. Idealmente remover o design de execução de código arbitrário (ver observação de invariante abaixo).

### [SEC-12] Texto de exceção interna devolvido literalmente ao chamador HTTP

**Onde:** `zcl_execution_engine=>run, linhas 61-64 (es_output-error = lx->get_text( )); serializado ao cliente em process_request linhas 185-187`

**Problema:** CATCH cx_root captura qualquer exceção e devolve lx->get_text( ) no JSON de resposta. Textos de exceção ABAP carregam nomes de classe, nomes de tabela, nomes de campo e mensagens de banco. Combinado com SEC-09, isso é o oráculo que permite ao atacante mapear o registry e o repositório sem tentativa e erro cego.

**Falha concreta:** O atacante itera POST /sap/bc/zrouter variando intent e lê as respostas: 'Intent not found' distingue intent inexistente de intent existente cuja classe falhou, e o texto de CX_SY_CREATE_OBJECT_ERROR revela o nome exato da classe configurada em ZAI_SKILLS. Ele enumera todo o registry e a estrutura interna sem nenhuma autorização adicional.

**Correção:** Devolver ao cliente um identificador de correlação e uma mensagem genérica; gravar o texto completo da exceção apenas no log da aplicação. Distinguir com granularidade fina 'não existe' de 'existe mas falhou' também não deve chegar ao chamador.
