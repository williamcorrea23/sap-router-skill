# ZROUTER v5 — instalação

Gateway HTTP para o SAP, pensado para ser consumido pelo TheBug Desktop quando
o ADT não cobre a operação. Sem RFC SDK, sem SAPlink, sem transporte prévio.

## Instalação em 4 passos

**1. Instalador** — SE38, criar programa executável `ZROUTER_V5_INSTALL`, colar
[`ZROUTER_V5_INSTALL.abap`](ZROUTER_V5_INSTALL.abap), ativar, executar.

Deixe **Simulação** marcada na primeira vez. Ele lista o que faria sem gravar
nada. Depois desmarque e rode de novo.

Cria: `ZROUTER_CFG`, `ZROUTER_LOG`, `ZROUTER_PEND`, a classe `ZCL_ZROUTER_GW`,
e semeia o registry.

**2. Objeto de autorização** — SU21, objeto `ZROUTER`, classe a seu critério:

| Campo | Tipo | Valores |
|---|---|---|
| `ZRMODULE` | CHAR30 | `BASIS`, `MM`, `FI`, … ou `*` |
| `ZRACTION` | CHAR60 | `PING`, `CREATE_MATERIAL`, … ou `*` |
| `ACTVT` | ACTVT | `03` ler · `02` escrever e decidir |

Sem esse objeto **toda chamada responde 403**. É o modo correto de falhar: o
serviço no ar recusando tudo é melhor que o serviço no ar liberando tudo.

**3. Grupo de funções** — SE80, grupo `ZROUTER_LOG`, módulo `ZROUTER_LOG_WRITE`
marcado como **habilitado para RFC**. Corpo e assinatura em
[`ZROUTER_LOG_WRITE.fugr.abap`](ZROUTER_LOG_WRITE.fugr.abap).

O RFC não é capricho: o log é gravado com `DESTINATION 'NONE'` para cair numa
LUW separada. Sem isso, o `ROLLBACK` de uma operação que falhou apaga o registro
de que ela falhou.

**4. Nó SICF** — SICF, `default_host/sap/bc`, novo subelemento `zrouter`,
tratador `ZCL_ZROUTER_GW`, logon exigido, ativar.

**Não configure usuário de serviço fixo.** O `AUTHORITY-CHECK` testa quem chama;
com usuário fixo, ele passa a testar sempre a mesma pessoa e o gate vira enfeite.

Verificação: `GET /sap/bc/zrouter/healthz` deve responder
`{"ok":true,"version":"5.0.0",...}`.

## O contrato HTTP

| Rota | Verbo | O que faz |
|---|---|---|
| `/healthz` | GET | versão, SID, mandante |
| `/r` | POST | **lê**. Executa operação marcada `R`; recusa `W` com 409 |
| `/w` | POST | **pede escrita**. Não executa: cria pendência, devolve 202 + id |
| `/q` | GET | fila de pendências não expiradas |
| `/d` | POST | decide — e, se aprovado, **executa na mesma viagem** |

### Formato, e por que ele é assim

Toda requisição é um objeto plano. Os parâmetros ficam no topo, não aninhados,
para poupar um nível de chaves em cada chamada:

```json
{"op":"TBL.READ","t":"MARA","f":"MATNR,MTART","w":"MTART = 'FERT'","n":50}
```

Resposta escalar:

```json
{"ok":1,"d":"sid=DS4 cli=110 usr=WCORREA lang=P cat=T"}
```

Resposta tabular — TSV dentro do JSON:

```json
{"ok":1,"n":3,"h":"MATNR\tMTART","t":"100\tFERT\n101\tHALB\n102\tROH"}
```

Erro:

```json
{"ok":0,"e":"tbl_not_allowed"}
```

O TSV é a decisão que mais economiza. Um resultado de 50 linhas × 6 colunas como
array de objetos repete os 6 nomes de campo 50 vezes; em TSV eles aparecem uma
vez, no cabeçalho.

Medido com uma leitura de `MARA` (50 linhas, 6 campos, valores realistas):

| Formato | Caracteres |
|---|---|
| `{"ok":true,"rows":[{...},…]}` | 6.022 |
| `{"ok":1,"n":50,"h":"…","t":"…"}` | 2.674 |

**56% a menos, 2,3x.** A vantagem cresce com nomes de campo mais longos e com
mais linhas, e encolhe em resultados de uma linha só — onde o cabeçalho não se
dilui. Para resposta escalar o formato nem usa tabela.

O mesmo raciocínio explica o resto do protocolo, com ganhos menores mas
gratuitos: `ok` em vez de `success`, `e` em vez de `error`, código de erro sem
mensagem redundante (`no_auth` já diz o que houve), e nenhum eco do request na
resposta.

### Operações

| `op` | Modo | Parâmetros | Devolve |
|---|---|---|---|
| `SYS.INFO` | R | — | escalar com SID, mandante, usuário, categoria |
| `OBJ.FIND` | R | `q` (aceita `*`) | tabela NAME/TYPE/PKG |
| `TBL.DESC` | R | `t` | tabela FIELD/KEY/TYPE/LEN |
| `TBL.READ` | R | `t`, `f`, `w`, `n` | tabela com as colunas pedidas |
| `SRC.READ` | R | `n` | fonte do programa, escalar |
| `SRC.WRITE` | W | `n`, `s`, `why` | `saved=… syntax=OK n=…` |

`TBL.READ` só alcança tabela liberada no registry como `TBL.<NOME>`. Sem essa
linha, a operação existe e não lê nada — inclusive não lê as tabelas de usuário e
de autorização, que é o ponto. O instalador semeia cinco (as três do próprio
ZROUTER, mais `TADIR` e `TRDIR`); acrescente as suas em `ZROUTER_CFG`.

`SRC.WRITE` recusa mandante produtivo: gravar fonte lá é transporte, não HTTP.

### O gate

A separação `/r` × `/w` é o que faz este gateway ser consumível pelo TheBug sem
quebrar o invariante do produto: o catálogo do agente recebe apenas `/r`, e essa
rota recusa por construção qualquer linha marcada como escrita — mesmo com o
usuário autorizado a escrever.

O gate de `/w` é o mesmo do
[ADR-0001](../../../../thebug-desktop/docs/adr/0001-sap-gui-scripting-com-confirmacao-por-acao.md):
o modelo pede, um humano lê o texto literal do efeito em `/q` e decide em `/d`.

- **`why` é obrigatório.** Um diálogo genérico ("executar ação?") anula o gate,
  então a ausência do texto é 400, não um default.
- **A pendência expira em 15 minutos.** Aprovação velha aprova um contexto que já
  mudou.
- **`/d` aprova e executa numa viagem só.** Separar em duas criaria uma janela
  entre a decisão e o efeito, em que o estado aprovado muda.
- **O gate é entre o modelo e o efeito, não entre duas pessoas.** Uma versão
  anterior recusava auto-aprovação (`requested_by = sy-uname`); isso travava o
  caso real, em que o TheBug chama o SAP com o seu usuário e você é quem aprova.
  Se o seu cenário exigir segregação de funções, ela vem de papéis distintos em
  `ZROUTER` (`ACTVT 02` só para quem aprova), não de comparar nomes.

## O que mudou do v4, e por quê

A revisão completa está em
[`docs/zrouter-v5-code-review.md`](../../docs/zrouter-v5-code-review.md) — 62
achados. O que motivou reescrever em vez de corrigir:

**Não compilava.** `cl_abap_authorization=>check_authorization( )` não existe no
ABAP. Toda a seção 5 do spec ("segurança centralizada") apoiava-se numa classe
inventada. Junto: `abap.syst_lo05` não é tipo DDIC, então as tabelas não ativam;
`RETURNING VALUE(rt_logs) TYPE STANDARD TABLE OF … WITH EMPTY KEY` não é
assinatura válida; `WHERE client = @sy-mandt` é erro em Open SQL estrito; e
`log_action` era chamado sem tratar a exceção verificada que declara.

**O gate era impossível.** O v4 executava a BAPI e comitava dentro do mesmo
request. Não havia estado pendente — logo, não havia onde interpor um humano. É
exatamente o motivo pelo qual o ADR-0001 recusou os MCPs de GUI de terceiros:
contornam o gate por construção.

**O invariante não era representável.** A seção 9 do spec classifica cada ação
com "Modo Escrita", mas essa coluna não existia em `ZROUTER_CONFIG`. Em runtime
não havia como pedir "só leitura", então expor o endpoint ao agente entregaria
`CREATE_MATERIAL` e `POST_DOCUMENT` ao modelo.

**A auditoria sumia na falha.** Log e resultado de lote gravavam na LUW da BAPI;
o `ROLLBACK` do primeiro erro apagava as duas coisas.

**Instanciação dinâmica.** `CREATE OBJECT lo_exec TYPE (iv_class)` com o nome
vindo de linha de tabela: quem escrevesse no registry escolhia a classe
executada. No v5 a factory é um `CASE` fechado.

## Sobre o ZCL_ABAP_REPL

**Não instale.** Ele aceita ABAP arbitrário por HTTP e executa com
`INSERT REPORT` + `GENERATE REPORT` + `SUBMIT`. A autorização é `S_DEVELOP` com
`ACTVT '03'` — *exibir* — para liberar execução; quem pode olhar código passa a
poder executar qualquer coisa. A guarda de produção lê `T000-CCCATEGORY`, que é
convenção e não garantia, e o nome do report temporário
(`'ZR' && sy-uname(4) && sy-uzeit`) colide entre usuários no mesmo segundo.

É útil como ferramenta de desenvolvimento pessoal num sandbox isolado. Não tem
lugar num caminho alcançável por um agente.

## Estender o registry

Uma operação nova precisa de duas coisas: uma linha em `ZROUTER_CFG` e um ramo
no `CASE` de `exec_read` (leitura) ou `exec_write` (escrita).

A linha sozinha não faz nada — de propósito. No v4, a superfície de ferramentas
era definida por linhas de tabela, então quem tivesse acesso à SM30 ampliava o
que o agente podia fazer sem passar por revisão de código. No v5 a tabela só
*restringe*: ela pode desligar uma operação, nunca criar uma.

A exceção é a allowlist `TBL.<NOME>`, que é dados por natureza — liberar a
leitura de uma tabela nova é decisão de configuração, não de código.

## Editar o código

`ZCL_ZROUTER_GW.clas.abap` é o fonte canônico. O instalador carrega uma cópia
como tabela de strings, e essa cópia é **gerada**:

```bash
python deploy/zrouter-v5/build_installer.py && python deploy/zrouter-v5/check_sync.py
```

Duas cópias mantidas à mão divergem, e a que ninguém executa é justamente a que é
revisada — a revisão passaria a atestar um código que não é o instalado. O
gerador também recusa backtick no fonte, porque ele delimita cada linha embutida
com backtick e um no meio encerraria a string ABAP.

## O que não foi verificado

Nada aqui rodou contra um SAP real. O instalador tem modo simulação e um
autoteste, e o autoteste é explícito sobre o próprio limite: confere se tabelas
e classe existem, e não confere se a classe ativa, se o nó SICF responde, nem se
o `AUTHORITY-CHECK` recusa quem deve recusar. Isso exige chamar o serviço de
fora com dois usuários diferentes — um autorizado e um não.

Rode o canário do TheBug (`npm run canary:adt`) depois de subir, e teste
`/read` com uma ação marcada `W` no registry: a resposta correta é 409, e se vier
200 o invariante caiu.
