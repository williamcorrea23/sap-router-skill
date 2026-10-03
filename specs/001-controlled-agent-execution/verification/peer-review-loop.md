# Loop de correção e adequação do peer-review

## 1. Metadata

- **Trigger**: execução manual de um item C1–C5/U1/D1 ou de uma adequação E1–E7 escolhida dentro do escopo autorizado.
- **Goal**: cumprir o objetivo do item com requisitos suficientemente definidos e evidência observável da correção ou adequação.
- **Target**: correções locais/offline; candidatos ficam desabilitados. Qualquer aceitação SAP precisa declarar sistema/tenant/cliente e operação.
- **Verification Level**: 1/2 para checks locais e fixtures; 3 somente para resposta SAP efetivamente observada; 4 exige checker em processo/contexto independente; 5 registra autorização ou aceitação humana.
- **Worklist**: [índice e achados](../review-remediation.md).
- **Durable Memory**: [peer-review-state.json](peer-review-state.json). Este é um estado de acompanhamento da revisão, distinto do RunRecord consumido por `sap_harness.py status/resume`.

## 2. Anatomy

### Execution: protocolos e gate de requisitos

Ler os `execution_protocols` do perfil selecionado e os procedimentos canônicos `karpathy-guidelines`, `loop-specification` e `verification-loop`. Ler também o checklist do item em `checklists/` e sua evidência de base no índice.

O reviewer avalia a qualidade dos requisitos. Marcadores customizados não são alterados pelo executor nem inferidos de testes verdes. Registrar aprovação de requisitos somente após avaliação do reviewer ou por agente que ele autorizou explicitamente. Pendências de requisitos impeditivas ficam registradas antes da implementação.

Cada run trabalha um item, com uma alteração aceita por iteração. E1–E7 exigem uma decisão de adoção e atualização dos artefatos Spec Kit relevantes antes da integração; pesquisar ou gerar documentos não promove um provedor.

### Limites e controle de progresso

- Até 8 iterações por run de um item.
- Até 900 segundos no total por run, incluindo negociação, execução e verificação.
- Até 120 segundos por chamada; limites menores do perfil/harness continuam valendo.
- 3 iterações consecutivas sem progresso aceito encerram em `Stalled`.
- Um prazo esgotado não permite reservar aprovação, iniciar chamada ou renovar implicitamente o limite.
- Salvar objetivo, plano, iteração, tempo acumulado/restante, fingerprint da ação, referência de aprovação quando aplicável, evidência e próximo passo.
- Se o tempo total do run não foi instrumentado, registrar `elapsed_seconds` e `remaining_limits.max_seconds` como `null`, com uma nota explícita; não estimar duração total somando somente tempos de comandos.
- Tokens/custo por alteração ficam `NOT_RUN` quando não medidos; não inventar métricas.
- Estes limites se aplicam a cada run de correção, não tornam a geração dos documentos uma execução de correção concluída.

### Stopping Rules & Terminal States

| Estado | Condição obrigatória |
|---|---|
| `Success` | Objetivo do item atingido, requisitos impeditivos resolvidos e todos os verificadores obrigatórios PASS com evidência. |
| `No-Op` | Comparação ou leitura determinística prova que o objetivo do item já estava cumprido. |
| `Blocked` | Contrato, licença, autorização, requisito, dependência ou evidência obrigatória indisponível. |
| `Stalled` | Três iterações consecutivas sem alteração aceita ou novo passo justificável. |
| `Exhausted` | Limite de tempo, iteração, chamada ou orçamento declarado impede continuar. |
| `PENDING_APPROVAL` | Checkpoint para ação externa concreta aguardando validação do broker; não executar a mutação. |

Estado `PLANNED` no arquivo de acompanhamento significa que o run ainda não começou; `execution_state` permanece nulo. Não representa um terminal nem uma autorização.

Se o objetivo escolhido incluir promoção de MCP ou comportamento SAP, ausência do resultado real mantém o run `Blocked`, mesmo com fixtures verdes. Se o objetivo for apenas gerar checklists, a evidência de geração fecha somente essa entrega documental.

## 3. Surgical Run Turn Steps

1. Resolver `SAP_ROUTER_ROOT`, entrar no diretório e exigir `scripts/source_catalog.py`.
2. Ler o estado do item, seu checklist, objetivos, limitações, perfil e autorizações já existentes.
3. Resolver os requisitos impeditivos no spec/plano; registrar o resultado da revisão de qualidade sem autoaprovar marcadores.
4. Para C1–C5, acrescentar o verificador independente e demonstrar falha antes de corrigir. Para U1/D1, definir o contrato documental e os checks aplicáveis antes da alteração.
5. Registrar exatamente a hipótese, os objetos selecionados e o próximo passo. Para uma nova verificação, provar que um caso inválido falha.
6. Aplicar a menor correção relacionada ao item. Evitar alterações em código, perfis, skills ou candidatos de outros itens.
7. Rodar o teste focado existente listado abaixo depois de incluir a regressão necessária. O teste existente sozinho não fecha um caso ainda não coberto.
8. Registrar command/tool, exit code, resultado sanitizado, fingerprint, PASS/FAIL/NOT_RUN e nível da evidência.
9. Se FAIL, identificar a causa e registrar a próxima ação; não mudar teste ou requisito apenas para obter verde.
10. Depois de PASS focado, executar somente gates mais amplos que sejam afetados. Repetir gate amplo apenas com nova mudança, falha ou preocupação não resolvida.
11. Se houver ação externa mutante autorizada, salvar antes/depois, usar broker para os argumentos/destino exatos e reconciliar resultado incerto antes de repetir.
12. Atualizar o estado durável e emitir terminal com motivo e checks restantes. Nunca fechar todos os itens por contagens gerais verdes.

## 4. Verificadores por item

Os procedimentos abaixo governam cada item. C1–C5/U1/D1 já receberam regressões e correções locais nesta execução; E1–E7 seguem `PLANNED` até haver decisão de adoção. O [estado durável](peer-review-state.json) e o [relatório de implementação](remediation-implementation-report.json) registram os resultados. Checklists de qualidade continuam sob revisão independente.

### C1

- **Requisitos**: [c1-credential-json.md](../checklists/c1-credential-json.md).
- **Goal**: Nenhuma credencial das respostas MCP chega ao contexto de modelos ou aos registros persistidos.
- **Verificador executado**: Regressão cobre structuredContent e content textual, JSON aninhado, caracteres escapados e valor ausente do ambiente; ausência do valor nos prompts e arquivos é obrigatória.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_harness_executor.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; verificações operacionais `PASS`; revisão do checklist `NOT_RUN`.

### C2

- **Requisitos**: [c2-mcp-transport-deadline.md](../checklists/c2-mcp-transport-deadline.md).
- **Goal**: Uma operação MCP inteira termina dentro do prazo documentado, inclusive quando o servidor deixa de consumir a entrada.
- **Verificador executado**: Processo MCP falso negocia e para de ler stdin; uma carga limitada mede o prazo e verifica o encerramento da árvore de processos. No Windows, o teste aguarda a terminação do processo filho por handle.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_harness_transport.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; verificações operacionais `PASS`; revisão do checklist `NOT_RUN`.

### C3

- **Requisitos**: [c3-strict-tool-contracts.md](../checklists/c3-strict-tool-contracts.md).
- **Goal**: O catálogo estrito rejeita qualquer contrato incompatível com esquema, servidor, capacidade, efeito ou política.
- **Verificador executado**: Casos negativos em cópias temporárias cobrem hash, efeito, capacidade, servidor, contrato duplicado e política; cada inconsistência é rejeitada pelo validador.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_consistency_regressions.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; regressões e catálogo estrito `PASS`; revisão do checklist `NOT_RUN`.

### C4

- **Requisitos**: [c4-total-run-budget.md](../checklists/c4-total-run-budget.md).
- **Goal**: Não ocorre reserva de aprovação nem despacho depois de esgotado o orçamento total da execução.
- **Verificador executado**: Fixture deixa `tools/list` consumir o orçamento antes de ação mutante; estado final é `Exhausted`, com nenhuma reserva nem despacho.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_harness_executor.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; regressão de orçamento `PASS`; revisão do checklist `NOT_RUN`.

### C5

- **Requisitos**: [c5-unknown-capability.md](../checklists/c5-unknown-capability.md).
- **Goal**: Capacidade inexistente produz erro estruturado e estado Blocked sem chamar ferramentas.
- **Verificador executado**: Caso de capacidade ausente comprova resultado bloqueado persistido, zero chamadas e nenhuma substituição silenciosa.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_harness_executor.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; regressão de capacidade desconhecida `PASS`; revisão do checklist `NOT_RUN`.

### U1

- **Requisitos**: [u1-run-state-expiry.md](../checklists/u1-run-state-expiry.md).
- **Goal**: Expiração do estado tem regra definida e status/resume recusam registros expirados sem ações externas.
- **Verificador executado**: TTL de 24 horas e fronteira exata são testados com relógio controlado, incluindo aprovação pendente, consulta histórica e retomada sem ação externa.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_harness_executor.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; regressões de expiração e retomada `PASS`; revisão do checklist `NOT_RUN`.

### D1

- **Requisitos**: [d1-python-support.md](../checklists/d1-python-support.md).
- **Goal**: As instruções de instalação e execução declaram o piso Python compatível com o harness e seu plano.
- **Verificador executado**: Documentação dos pontos de entrada foi alinhada, a regressão conferiu as declarações e Python 3.11.15 foi usado para a suíte.
- **Comando focado existente**: `python -m unittest discover -s tests -p 'test_harness_cli.py' -q`.
- **Evidência esperada**: nível 1/2; fixture ou análise documental identifica a falha e depois comprova sua resolução.
- **Estado deste run**: `COMPLETED` local; regressão Python e paridade IDE `PASS`; revisão do checklist `NOT_RUN`.

### E1

- **Requisitos**: [e1-abapilot.md](../checklists/e1-abapilot.md).
- **Goal**: Preparar o candidato selecionado para DEV sem abrir execução antes de identificar e validar o backend, o sistema e os contratos MCP.
- **Verificador executado**: Perfil específico DEV pinado; candidato continua disabled e sem runtime/rota ativa. Validação estrita e 21 regressões de consistência passaram, incluindo rejeição de política para ferramentas mutantes e instalação.
- **Comandos focados**: `rtk proxy python scripts/validate_catalog.py --strict --json`; `rtk proxy python -m unittest discover -s tests -p test_consistency_regressions.py -q`.
- **Evidência**: nível 1 local PASS; backend licenciado, sistema/cliente, endpoint, credenciais externas, `tools/list`, autorização/auditoria SAP e teste de campo permanecem `NOT_RUN`/bloqueados. Ver [relatório de implementação](external-candidate-implementation-report.json) e `.agents/registries/mcp-target-profiles.json`.
- **Estado deste run**: implementação local `COMPLETED`; terminal `Blocked` para execução no DEV; checklist independente `NOT_RUN` e seus critérios permanecem desmarcados.

### E2

- **Requisitos**: [e2-odata-go.md](../checklists/e2-odata-go.md).
- **Goal**: Uma eventual ponte OData Go possui versão e destino fixados, leitura estrita e operação efetiva validada pelo contrato.
- **Verificador a preparar**: Revisar binário e serviço, iniciar em stdio com --read-only e testar metadata OData v2/v4 em fixture. Negativas devem cobrir escrita e function/action na ferramenta universal e no catálogo por entidade.
- **Comando focado existente**: `python scripts/mcp_launcher.py search --query "OData Go"`.
- **Evidência esperada**: proveniência e catálogo local em nível 1/2; negociação ou build não substitui aceitação SAP em nível 3 quando a promoção for o objetivo.
- **Estado inicial**: `PLANNED`; verificações da correção/integração `NOT_RUN`. Busca no catálogo prova descoberta apenas.

### E3

- **Requisitos**: [e3-odata-python.md](../checklists/e3-odata-python.md).
- **Goal**: Antes de qualquer adoção, a fonte OData Python tem licença esclarecida, snapshot real e efeitos de todas as ferramentas classificados.
- **Verificador a preparar**: Esclarecer licença antes de importar código; obter snapshot real, inventariar ferramentas e fechar escrita por política/contrato. Testar protocolo e resultados com fixture sem SAP ou credenciais reais.
- **Comando focado existente**: `python scripts/source_catalog.py search "GutjahrAI OData Python"`.
- **Evidência esperada**: proveniência e catálogo local em nível 1/2; negociação ou build não substitui aceitação SAP em nível 3 quando a promoção for o objetivo.
- **Estado inicial**: `PLANNED`; verificações da correção/integração `NOT_RUN`. Busca no catálogo prova descoberta apenas.

### E4

- **Requisitos**: [e4-sapgui-provider.md](../checklists/e4-sapgui-provider.md).
- **Goal**: Os candidatos SAP GUI identificam o runtime selecionado e a política de ações antes de qualquer promoção.
- **Verificador a preparar**: Revisar delta e runtime escolhido, testar negociação com backend simulado e política das ações; promoção exige prova no ambiente GUI/WebGUI identificado e reconciliação de mutações incertas.
- **Comando focado existente**: `python scripts/mcp_launcher.py search --query "Hochfrequenz SAP GUI"`.
- **Evidência esperada**: proveniência e catálogo local em nível 1/2; negociação ou build não substitui aceitação SAP em nível 3 quando a promoção for o objetivo.
- **Estado inicial**: `PLANNED`; verificações da correção/integração `NOT_RUN`. Busca no catálogo prova descoberta apenas.

### E5

- **Requisitos**: [e5-successfactors-credentials.md](../checklists/e5-successfactors-credentials.md).
- **Goal**: A integração SuccessFactors mantém credenciais no provedor e fornece ao modelo somente argumentos de negócio autorizados.
- **Verificador a preparar**: Revisar/adaptar o provedor para injetar credenciais fora do modelo; schemas públicos e snapshots não podem exigir senha. Testar configuração por data center/instance, isolamento, erros e autorização antes de qualquer tenant.
- **Comando focado existente**: `python scripts/mcp_launcher.py search --query "SuccessFactors"`.
- **Evidência esperada**: proveniência e catálogo local em nível 1/2; negociação ou build não substitui aceitação SAP em nível 3 quando a promoção for o objetivo.
- **Estado inicial**: `PLANNED`; verificações da correção/integração `NOT_RUN`. Busca no catálogo prova descoberta apenas.

### E6

- **Requisitos**: [e6-odata-cli-skill.md](../checklists/e6-odata-cli-skill.md).
- **Goal**: A skill SAP OData CLI é classificada como skill/CLI e suas operações são controladas sem inventar um servidor MCP nativo.
- **Verificador executado**: Skill e licença MIT importadas do SHA fixado; strict catalog, 21 regressões e validação do empacotador passaram. Nenhum binário CLI, dependência ou registro MCP foi instalado.
- **Comandos focados**: `rtk proxy python scripts/validate_catalog.py --strict --json`; `rtk proxy python scripts/skill_packager.py validate --skill sap-odata-cli --validate-only`; `rtk proxy python -m unittest discover -s tests -p test_consistency_regressions.py -q`.
- **Evidência**: nível 1/2 local PASS; habilidade classificada `skill_only`, sem chamada OData nem autenticação SAP. Ver [relatório de implementação](external-candidate-implementation-report.json) e `.agents/registries/skill-imports.json`.
- **Estado deste run**: `COMPLETED` como orientação local; runtime/MCP não promovidos; validação SAP `NOT_RUN`; checklist independente permanece desmarcado.

### E7

- **Requisitos**: [e7-basis-skill-refresh.md](../checklists/e7-basis-skill-refresh.md).
- **Goal**: Uma atualização Basis preserva a fonte canônica, revisa 21 novas skills e atualiza as 12 existentes com paridade e políticas.
- **Verificador executado**: Revisão da fonte pinada, comparação dos 76 arquivos do snapshot, catálogo com 76/76 fontes e 759 assets indexados sem faltas, além de paridade IDE para 203 skills. Comandos operacionais foram inspecionados como documentação e não executados.
- **Comandos focados**: `rtk proxy python scripts/source_catalog.py status`; `rtk proxy python scripts/generate_ide_assets.py check`.
- **Evidência**: nível 1/2 local PASS; nenhuma operação SAP, SO ou banco executada. Qualquer capacidade operacional permanece sujeita a target, autorização e aprovação próprios. Ver [relatório de implementação](external-candidate-implementation-report.json).
- **Estado deste run**: `COMPLETED` para importação e paridade locais; teste de campo `NOT_RUN`; checklist independente permanece desmarcado.

## 5. Verification Commands

Preparar o ambiente PowerShell a partir do checkout canônico, sem instalar dependências implicitamente:

```powershell
$env:SAP_ROUTER_ROOT = (Get-Location).Path
Set-Location -LiteralPath $env:SAP_ROUTER_ROOT
if (-not (Test-Path -LiteralPath 'scripts/source_catalog.py')) { throw 'Canonical router root absent' }
$env:PYTHONDONTWRITEBYTECODE = '1'
```

| Gate | Comando existente | Quando aplicar |
|---|---|---|
| Executor | `rtk proxy python -X utf8 -B -m unittest discover -s tests -p 'test_harness_executor.py' -q` | C1/C4/C5/U1; regressões dedicadas foram incluídas. |
| Transporte | `rtk proxy python -X utf8 -B -m unittest discover -s tests -p 'test_harness_transport.py' -q` | C2; inclui escrita bloqueada e término da árvore de processos. |
| Consistência | `rtk proxy python -X utf8 -B -m unittest discover -s tests -p 'test_consistency_regressions.py' -q` | C3; inclui contratos negativos do catálogo estrito. |
| CLI | `rtk proxy python -X utf8 -B -m unittest discover -s tests -p 'test_harness_cli.py' -q` | D1 e contratos de inicialização. |
| Catálogo | `rtk proxy python -X utf8 -B scripts/validate_catalog.py --strict` | Valida contratos, registros, perfis e importações, incluindo os contratos MCP revisados. |
| Mirrors | `rtk proxy python -X utf8 -B scripts/generate_ide_assets.py check` | Alterações canônicas; gerar antes pelo gerador do repositório quando necessário. |
| Segurança | `rtk proxy python -X utf8 -B scripts/secret_audit.py --strict --json` | Artefatos/código alterados; reportar só diagnóstico sanitizado. |
| Regressão ampla | `rtk proxy python -X utf8 -B -m unittest discover -s tests -q` | Quando mudanças do executor/registro afetarem o conjunto do repositório. |
| Avaliação offline | `rtk proxy python -X utf8 -B scripts/sap_harness.py eval --suite all` | Alterações de harness; manter live SAP NOT_RUN. |
| ABAP/artifacts | `rtk proxy npm run abap:review` | Somente alterações ABAP ou de seus artefatos. |
| Diff | `rtk proxy git diff -- <paths>` | Revisar apenas paths do item; arquivos novos também precisam ser inspecionados diretamente. |

Sem alvo de build/types aplicável, registrar `NOT_RUN` com motivo; não instalar ferramentas para criar um PASS artificial. Um intérprete mais novo não prova automaticamente suporte ao piso Python documentado.

## 6. Durable Memory and Evidence

Em `peer-review-state.json`, cada item tem checklist, goal, plano de verificação, limites, checkpoint, estado de execução, progresso e próximo passo. Atualizar somente o item escolhido e preservar os demais.

Para cada check, preencher:

```json
{
  "check": "identificador estável",
  "status": "PASS | FAIL | NOT_RUN",
  "verification_level": 1,
  "command_or_tool": "comando exato ou ferramenta",
  "target": "local/offline ou destino SAP exato",
  "observed_result": "resultado sanitizado e exit code quando disponível",
  "artifact_or_reference": "evidência ou referência legível",
  "reason": "obrigatório para NOT_RUN"
}
```

Fixtures e inspeção de fontes não são evidência SAP nível 3. Review de modelo nível 4 exige contexto/processo independente e não substitui checks determinísticos. A autorização humana nível 5 permite a ação concreta, sem comprovar o resultado.

Não gravar credenciais, cookies, tokens, headers sensíveis ou payloads brutos. O estado de revisão não funciona como plano de aprovação nem como RunRecord do harness.

## 7. Guardrails and Reporting

Preservar o gate de contexto funcional, permissões do perfil, contratos `(server, capability, tool, effect)`, fingerprint do schema, alvo exato e broker. Usar descoberta local; pesquisa GitHub desta avaliação não se torna lookup de runtime.

Para escrever em SAP ou promover provedores, cumprir as autorizações existentes e os controles aplicáveis. Em resultado incerto, registrar reconciliação e parar antes de replay/fallback. Desabilitar um candidato não elimina a necessidade de descrevê-lo corretamente.

Relatório de cada run:

```text
VERIFICATION REPORT
Item/Goal: <ID e condição observável>
Target: <local/offline ou sistema/tenant/cliente>
Requirements review: <referência do reviewer; pendências>
Build/artifact: PASS / FAIL / NOT_RUN — referência ou motivo
Types/syntax: PASS / FAIL / NOT_RUN — referência ou motivo
Catalog/lint: PASS / FAIL / NOT_RUN — referência ou motivo
Tests: PASS / FAIL / NOT_RUN — casos realmente presentes e contagem
Security: PASS / FAIL / NOT_RUN — evidência sanitizada
Diff: PASS / FAIL / NOT_RUN — escopo inspecionado
SAP field outcome: PASS / FAIL / NOT_RUN — nível e resultado
Run state: Success / No-Op / Blocked / Stalled / Exhausted / PENDING_APPROVAL
Remaining checks/Next action: <pendências concretas>
```

A conclusão da geração está em `checklist-generation-report.json`. Os resultados posteriores da implementação local estão na seção abaixo e em `remediation-implementation-report.json`; eles não representam avaliação dos checklists nem aprovação de adoção ou execução dos candidatos.

## 8. Resultado da implementação local (2026-10-03)

C1–C5/U1/D1 foram implementados após regressões red-before-green. A suíte integral executou **143 testes com Python 3.11.15 e passou**. A avaliação offline do harness passou em **5/5 cenários e 33/33 checks**. A validação `--strict` do catálogo passou (`181 skills`, `12 MCPs`, `70 planejados`, `55 capacidades`, `4 perfis`); gaps planejados permanecem fail-closed. A checagem de assets passou sem diferenças para Claude, Gemini, Codex, Cursor e Kiro (`181 skills`, `38 perfis`). A auditoria de segredos nos arquivos afetados passou com zero achados e `git diff --check` passou.

O teste C2 usa MCP fixture que deixa de consumir `stdin`, verifica o limite de tempo e aguarda a saída do filho. O transporte agora encerra o job do Windows explicitamente, além do encerramento por fechamento do job. Nenhuma conexão ou operação em SAP foi executada. As avaliações independentes de qualidade continuam `NOT_RUN`; E1–E7 permanecem `PLANNED` e sem promoção.

