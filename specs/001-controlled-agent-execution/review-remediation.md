# Checklists e adequações do peer-review

**Criado**: 2026-10-02  
**Feature**: [Controlled Agent Execution](spec.md)  
**Escopo desta execução**: implementação e verificação local de C1–C5/U1/D1 em 2026-10-03, além dos procedimentos e checklists criados antes. E1–E7 continuam condicionados à decisão de adoção; nenhum candidato foi importado ou promovido.

São 14 checklists customizados, com seis critérios cada: sete achados C1–C5/U1/D1 e sete adequações de candidatos E1–E7. Todos os 84 critérios são criados desmarcados.

`speckit-checklist` avalia requisitos escritos. O [loop](verification/peer-review-loop.md) contém os verificadores de implementação; o [estado durável](verification/peer-review-state.json) acompanha cada item sem transformar um checklist em evidência de funcionamento.

**Evidência da geração documental**: [relatório da geração](verification/checklist-generation-report.json). **Evidência da implementação**: [relatório de remediação](verification/remediation-implementation-report.json) e [estado durável](verification/peer-review-state.json).

## Uso pelos agentes e reviewers

1. Ler o item, seu checklist e a seção correspondente do loop antes de trabalhar.
2. Revisar os requisitos e resolver lacunas documentais antes de uma correção ou promoção. O reviewer decide sobre os marcadores customizados; um agente só os avalia quando explicitamente autorizado.
3. Usar Karpathy, loop-specification e verification-loop canônicos, além do perfil selecionado. Fazer uma correção aceita por iteração e registrar a evidência do verificador.
4. Ler o estado anterior, executar somente o trabalho escolhido e atualizar seu resultado. Um item pendente não é fechado pelo sucesso de outro item.
5. Manter candidatos desabilitados até os gates de adoção aplicáveis. Solicitações de escrita seguem as autorizações existentes e o broker; checklist ou revisão de modelo não substituem aprovação.

## Rastreabilidade e estados

Os requisitos FR-020/SC-005 e T010–T013 cobrem nove repositórios do escopo original. E1–E7 são uma avaliação complementar: uma decisão de integração exige atualizar spec, plano e tarefas com os requisitos necessários antes da implementação. Não se assume cobertura dessa nova adoção pelo número nove.

T001–T034 permanecem como histórico da implementação original. T035–T048 registram e fecham as remediações locais executadas. A avaliação de qualidade dos requisitos permanece `NOT_RUN`; os checklists customizados continuam sem alterações, sob responsabilidade do reviewer.

| Item | Tipo | Foco | Checklist | Estado atual |
|---|---|---|---|---|
| C1 | Correção | Credenciais em respostas MCP | [c1-credential-json.md](checklists/c1-credential-json.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| C2 | Correção | Prazo de todo o transporte MCP | [c2-mcp-transport-deadline.md](checklists/c2-mcp-transport-deadline.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| C3 | Correção | Contratos no catálogo estrito | [c3-strict-tool-contracts.md](checklists/c3-strict-tool-contracts.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| C4 | Correção | Orçamento total antes do despacho | [c4-total-run-budget.md](checklists/c4-total-run-budget.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| C5 | Correção | Capacidade inexistente e estado terminal | [c5-unknown-capability.md](checklists/c5-unknown-capability.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| U1 | Correção | Expiração do estado de execução | [u1-run-state-expiry.md](checklists/u1-run-state-expiry.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| D1 | Correção | Versão mínima e suporte Python | [d1-python-support.md](checklists/d1-python-support.md) | Implementado; verificações locais PASS; revisão do checklist `NOT_RUN` |
| E1 | Adequação condicionada à adoção | Adequação do ABAPilot MCP | [e1-abapilot.md](checklists/e1-abapilot.md) | Pendente |
| E2 | Adequação condicionada à adoção | Adequação da ponte OData em Go | [e2-odata-go.md](checklists/e2-odata-go.md) | Pendente |
| E3 | Adequação condicionada à adoção | Proveniência e efeitos do OData Python | [e3-odata-python.md](checklists/e3-odata-python.md) | Pendente |
| E4 | Adequação condicionada à adoção | Runtime e efeitos do SAP GUI MCP | [e4-sapgui-provider.md](checklists/e4-sapgui-provider.md) | Pendente |
| E5 | Adequação condicionada à adoção | Credenciais e adequação do SuccessFactors MCP | [e5-successfactors-credentials.md](checklists/e5-successfactors-credentials.md) | Pendente |
| E6 | Adequação condicionada à adoção | Skill e CLI SAP OData | [e6-odata-cli-skill.md](checklists/e6-odata-cli-skill.md) | Pendente |
| E7 | Adequação condicionada à adoção | Atualização das skills Basis | [e7-basis-skill-refresh.md](checklists/e7-basis-skill-refresh.md) | Pendente |

## Evidência da revisão

Os casos C1–C5, U1 e D1 tiveram regressões red-before-green. A suíte final executou 143 testes com Python 3.11.15 e passou. O catálogo estrito passou com gaps planejados e fail-closed; os assets de IDE passaram em paridade (181 skills e 38 perfis); a auditoria de segredos nos arquivos afetados passou com zero achados. Diff hygiene também foi verificada. Nenhuma verificação em sistema SAP foi feita. Os checklists de qualidade continuam sob avaliação independente.

A leitura dos sete upstreams desta rodada foi feita pelo plugin GitHub e pelo navegador em revisões imutáveis. Não houve instalação, execução de código desses projetos, importação ou ativação de MCP.

## C1

**Credenciais em respostas MCP**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: FR-005, FR-013, FR-016; T020, T021, T033  
**Ponto local**: `scripts/harness_executor.py:84`  

**Verificação desta execução**: PASS; regressão de credenciais JSON estruturadas/textuais e suíte integral registrada em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: Fixture do peer-review: segredo em JSON textual chegou ao checker e ao arquivo da execução; o valor estruturado foi mascarado.

**Objetivo de correção**: Nenhuma credencial das respostas MCP chega ao contexto de modelos ou aos registros persistidos.

**Checklist de requisitos**: [c1-credential-json.md](checklists/c1-credential-json.md)  
**Verificação operacional**: [seção C1 do loop](verification/peer-review-loop.md#c1)

## C2

**Prazo de todo o transporte MCP**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: FR-004, FR-012, FR-022; T018, T019, T033  
**Ponto local**: `scripts/harness_mcp_client.py:174`  

**Verificação desta execução**: PASS; escrita bloqueada, prazo e encerramento do processo filho cobertos em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: Fixture do peer-review: timeout interno de 1 segundo não encerrou a escrita; um watchdog externo interrompeu o processo após 5 segundos.

**Objetivo de correção**: Uma operação MCP inteira termina dentro do prazo documentado, inclusive quando o servidor deixa de consumir a entrada.

**Checklist de requisitos**: [c2-mcp-transport-deadline.md](checklists/c2-mcp-transport-deadline.md)  
**Verificação operacional**: [seção C2 do loop](verification/peer-review-loop.md#c2)

## C3

**Contratos no catálogo estrito**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: FR-006, FR-007, FR-017; T006, T019, T025  
**Ponto local**: `python/sap_router_core/registry.py:559`  

**Verificação desta execução**: PASS; regressões negativas e validação `--strict` registradas em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: Cópia temporária do catálogo recebeu contrato com efeito incompatível e hash inválido; o validador estrito retornou PASS.

**Objetivo de correção**: O catálogo estrito rejeita qualquer contrato incompatível com esquema, servidor, capacidade, efeito ou política.

**Checklist de requisitos**: [c3-strict-tool-contracts.md](checklists/c3-strict-tool-contracts.md)  
**Verificação operacional**: [seção C3 do loop](verification/peer-review-loop.md#c3)

## C4

**Orçamento total antes do despacho**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: FR-009, FR-012, FR-013; T018, T019, T024  
**Ponto local**: `scripts/harness_executor.py:426`  

**Verificação desta execução**: PASS; orçamento total cobre reserva e despacho, com evidência em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: Fixture com orçamento de 1 segundo iniciou a ferramenta aproximadamente 1,75 segundo após o início.

**Objetivo de correção**: Não ocorre reserva de aprovação nem despacho depois de esgotado o orçamento total da execução.

**Checklist de requisitos**: [c4-total-run-budget.md](checklists/c4-total-run-budget.md)  
**Verificação operacional**: [seção C4 do loop](verification/peer-review-loop.md#c4)

## C5

**Capacidade inexistente e estado terminal**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: FR-003, FR-017, FR-021; T005, T006, T019, T021  
**Ponto local**: `scripts/harness_executor.py:343`  

**Verificação desta execução**: PASS; capacidade desconhecida resulta em estado bloqueado persistido sem despacho, com evidência em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: Fixture com capacidade ausente lançou AttributeError, manteve o registro em Running e realizou zero chamadas de ferramenta.

**Objetivo de correção**: Capacidade inexistente produz erro estruturado e estado Blocked sem chamar ferramentas.

**Checklist de requisitos**: [c5-unknown-capability.md](checklists/c5-unknown-capability.md)  
**Verificação operacional**: [seção C5 do loop](verification/peer-review-loop.md#c5)

## U1

**Expiração do estado de execução**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: FR-010, FR-012, FR-014; T021, T024, T033  
**Ponto local**: `specs/001-controlled-agent-execution/spec.md:88`  

**Verificação desta execução**: PASS; TTL, limite exato e retomada local foram verificados com relógio controlado; evidência em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: FR-014 exige estado expirado fail-closed, mas não define TTL, marco inicial ou comportamento de status/resume; a aprovação possui expiração própria.

**Objetivo de correção**: Expiração do estado tem regra definida e status/resume recusam registros expirados sem ações externas.

**Checklist de requisitos**: [u1-run-state-expiry.md](checklists/u1-run-state-expiry.md)  
**Verificação operacional**: [seção U1 do loop](verification/peer-review-loop.md#u1)

## D1

**Versão mínima e suporte Python**  
**Situação**: correção implementada e verificada localmente; checklist de requisitos permanece sob revisão independente  
**Rastreabilidade**: SC-006; T003, T029, T032  
**Ponto local**: `AGENTS.md:135`  

**Verificação desta execução**: PASS; entradas afetadas declaram Python 3.11+, intérprete 3.11.15 foi usado e assets gerados estão em paridade; evidência em [remediation-implementation-report.json](verification/remediation-implementation-report.json).

**Evidência de base**: AGENTS.md anuncia Python 3.8+, enquanto o plano especifica 3.11+ e o harness utiliza APIs compatíveis com esse piso.

**Objetivo de correção**: As instruções de instalação e execução declaram o piso Python compatível com o harness e seu plano.

**Checklist de requisitos**: [d1-python-support.md](checklists/d1-python-support.md)  
**Verificação operacional**: [seção D1 do loop](verification/peer-review-loop.md#d1)

## E1

**Adequação do ABAPilot MCP**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-005, FR-006, FR-009, FR-018; extensão de escopo a definir  
**Ponto local**: `.agents/registries/mcp-candidates.json:1123`  

**Fonte**: [NicoHern/abapilot-mcp](https://github.com/NicoHern/abapilot-mcp/tree/25639b76f6d3f53ae029af73913370af56a1e980)  
**Revisão consultada**: `25639b76f6d3f53ae029af73913370af56a1e980`  
**Licença observada**: MIT (conector); backend requer licença própria  
**Situação local**: Candidato desabilitado com runtime nulo; fonte não consta no lock local.

**Valor para o router**: Alternativa condicionada para ECC e S/4HANA on-premise com contexto ABAP/DDIC e sintaxe, quando houver backend ABAPilot instalado.

**Adequações necessárias**: Backend SAP licenciado; schema incompleto de sap_write_code_safe e salvaguardas dependentes do backend; pacote e execução precisam ser fixados e revisados.

**Objetivo se adotado**: Uma eventual integração ABAPilot possui backend identificado, runtime fixado e contratos restritos às ferramentas autorizadas.

**Checklist de requisitos**: [e1-abapilot.md](checklists/e1-abapilot.md)  
**Verificação operacional**: [seção E1 do loop](verification/peer-review-loop.md#e1)

## E2

**Adequação da ponte OData em Go**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-006, FR-007, FR-008, FR-018; extensão de escopo a definir  
**Ponto local**: `.agents/registries/mcp-candidates.json:361`  

**Fonte**: [oisee/odata_mcp_go](https://github.com/oisee/odata_mcp_go/tree/9fd9d0f06746c228c5e56a7e61061ad83e525aaa)  
**Revisão consultada**: `9fd9d0f06746c228c5e56a7e61061ad83e525aaa`  
**Licença observada**: MIT  
**Situação local**: Candidato odata-mcp-go desabilitado; não consta como snapshot fixado no lock local.

**Valor para o router**: Ponte OData v2/v4; stdio, modo somente leitura e opção de ferramenta universal para reduzir catálogo de ferramentas.

**Adequações necessárias**: Runtime local usa nome odata-mcp-go sem destino configurado; upstream documenta odata-mcp e exige serviço. Modo universal e functions precisam de efeitos controlados.

**Objetivo se adotado**: Uma eventual ponte OData Go possui versão e destino fixados, leitura estrita e operação efetiva validada pelo contrato.

**Checklist de requisitos**: [e2-odata-go.md](checklists/e2-odata-go.md)  
**Verificação operacional**: [seção E2 do loop](verification/peer-review-loop.md#e2)

## E3

**Proveniência e efeitos do OData Python**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-005, FR-006, FR-008, FR-009; extensão de escopo a definir  
**Ponto local**: `.agents/registries/mcp-candidates.json:867`  

**Fonte**: [GutjahrAI/sap-odata-mcp-py](https://github.com/GutjahrAI/sap-odata-mcp-py/tree/5e2cce5978bcdf0b9dc8ba58456b08293a430780)  
**Revisão consultada**: `5e2cce5978bcdf0b9dc8ba58456b08293a430780`  
**Licença observada**: Não foi encontrada declaração explícita de licença no commit consultado.  
**Situação local**: Apenas README ponteiro; revision bundled-candidate, sem código ou licença vendorizados; runtime nulo e desabilitado.

**Valor para o router**: Referência compacta de descoberta/metadata SAP OData e implementação Python; utilidade operacional depende das adequações.

**Adequações necessárias**: Fonte pública tem quatro arquivos e expõe criação/exclusão/ações; candidato local declara apenas query. Licença ausente e integração não possui provas locais.

**Objetivo se adotado**: Antes de qualquer adoção, a fonte OData Python tem licença esclarecida, snapshot real e efeitos de todas as ferramentas classificados.

**Checklist de requisitos**: [e3-odata-python.md](checklists/e3-odata-python.md)  
**Verificação operacional**: [seção E3 do loop](verification/peer-review-loop.md#e3)

## E4

**Runtime e efeitos do SAP GUI MCP**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-006, FR-009, FR-012, FR-018; extensão de escopo a definir  
**Ponto local**: `.agents/registries/mcp-candidates.json:749`  

**Fonte**: [Hochfrequenz/sapgui.mcp](https://github.com/Hochfrequenz/sapgui.mcp/tree/95b0226dfa4d36647f993e64627dfc416c85127d)  
**Revisão consultada**: `95b0226dfa4d36647f993e64627dfc416c85127d`  
**Licença observada**: MIT  
**Situação local**: Snapshot 83c0bb4, desabilitado; há entradas Go/WebGUI e entrada sapgui_mcp. Upstream atual tem entrypoint Python run-sapgui-mcp-server.

**Valor para o router**: Fallback GUI/WebGUI, validação visual, testes de ponta a ponta e captura de evidências em cenários sem API adequada.

**Adequações necessárias**: 65 commits após o snapshot; alinhar entrypoint, dependências e candidatos legados. Sessão GUI, transações e ações de tela exigem classificação/controle.

**Objetivo se adotado**: Os candidatos SAP GUI identificam o runtime selecionado e a política de ações antes de qualquer promoção.

**Checklist de requisitos**: [e4-sapgui-provider.md](checklists/e4-sapgui-provider.md)  
**Verificação operacional**: [seção E4 do loop](verification/peer-review-loop.md#e4)

## E5

**Credenciais e adequação do SuccessFactors MCP**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-005, FR-006, FR-007, FR-022; extensão de escopo a definir  
**Ponto local**: `.agents/registries/mcp-candidates.json:726`  

**Fonte**: [aiadiguru2025/sf-mcp](https://github.com/aiadiguru2025/sf-mcp/tree/b17ada8caf81b2edc1014a15353a6522a71657b5)  
**Revisão consultada**: `b17ada8caf81b2edc1014a15353a6522a71657b5`  
**Licença observada**: MIT  
**Situação local**: Snapshot local corresponde ao upstream, mas permanece desabilitado.

**Valor para o router**: Ferramentas especializadas de HR, RBP, auditoria e compliance; possível provedor para a lacuna SuccessFactors.

**Adequações necessárias**: resolve_credentials devolve credenciais fornecidas em cada chamada; client rejeita sua ausência. Metadados locais que pressupõem configuração OAuth por ambiente não descrevem essa implementação.

**Objetivo se adotado**: A integração SuccessFactors mantém credenciais no provedor e fornece ao modelo somente argumentos de negócio autorizados.

**Checklist de requisitos**: [e5-successfactors-credentials.md](checklists/e5-successfactors-credentials.md)  
**Verificação operacional**: [seção E5 do loop](verification/peer-review-loop.md#e5)

## E6

**Skill e CLI SAP OData**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-005, FR-015, FR-018; extensão de escopo a definir  
**Ponto local**: `.agents/registries/mcp-candidates.json:1105`  

**Fonte**: [kts982/sap-odata-explorer](https://github.com/kts982/sap-odata-explorer/tree/146e3b8de0764e4cfecc5cba1643fe61b40cb4ee)  
**Revisão consultada**: `146e3b8de0764e4cfecc5cba1643fe61b40cb4ee`  
**Licença observada**: MIT  
**Situação local**: Catalogado como candidato MCP com runtime nulo; a skill sap-odata-cli ainda não é canônica.

**Valor para o router**: Descoberta Gateway, metadata/annotations, consultas, lint Fiori e EDMX offline; alta utilidade para desenvolvimento OData/Fiori.

**Adequações necessárias**: É CLI Rust e aplicação desktop, sem servidor MCP nativo. O harness precisa de integração CLI controlada ou adapter revisado; perfis e biblioteca offline possuem mutações locais.

**Objetivo se adotado**: A skill SAP OData CLI é classificada como skill/CLI e suas operações são controladas sem inventar um servidor MCP nativo.

**Checklist de requisitos**: [e6-odata-cli-skill.md](checklists/e6-odata-cli-skill.md)  
**Verificação operacional**: [seção E6 do loop](verification/peer-review-loop.md#e6)

## E7

**Atualização das skills Basis**  
**Situação**: adequação antes de adoção; nenhuma promoção autorizada por este documento  
**Rastreabilidade**: FR-015, FR-016, SC-004; extensão de escopo a definir  
**Ponto local**: `.agents/registries/bundled-sources.lock.json:196`  

**Fonte**: [adam0thman/sap-basis-ops](https://github.com/adam0thman/sap-basis-ops/tree/6ae551f6ec2ef4c554b606fcdef5a04599e4ab11)  
**Revisão consultada**: `6ae551f6ec2ef4c554b606fcdef5a04599e4ab11`  
**Licença observada**: MIT  
**Situação local**: 12 skills importadas no snapshot f23d0ca; upstream possui 33 e está 49 commits à frente.

**Valor para o router**: 21 novas skills para HA/DR de bancos, BTP CLI, criptografia/PSE, ferramentas de sistema, troubleshooting e operações Basis.

**Adequações necessárias**: Há 21 novas skills ainda ausentes da árvore canônica e alterações nas 12 existentes; comandos operacionais e pré-condições precisam de revisão antes de uso.

**Objetivo se adotado**: Uma atualização Basis preserva a fonte canônica, revisa 21 novas skills e atualiza as 12 existentes com paridade e políticas.

**Checklist de requisitos**: [e7-basis-skill-refresh.md](checklists/e7-basis-skill-refresh.md)  
**Verificação operacional**: [seção E7 do loop](verification/peer-review-loop.md#e7)

## Ordem recomendada

C1–C5/U1/D1 já estão corrigidos e verificados localmente. O reviewer pode avaliar os sete checklists sem alterar seus marcadores por inferência. Para trabalho futuro de adoção, priorizar E6 e a revisão Basis E7; E2 é o candidato principal para ponte OData genérica. E5 pode cobrir SuccessFactors após resolver o fluxo de credenciais. E4 serve como fallback GUI. E1 depende do backend licenciado. E3 fica em espera enquanto licença e proveniência não forem resolvidas. Qualquer adoção precisa de escopo Spec Kit próprio antes da importação ou promoção.

## Procedimentos usados

- `speckit-checklist`: skill solicitada em `C:/Users/William Correa/.codex/skills/speckit-checklist/SKILL.md`; template local em `.specify/templates/checklist-template.md`.
- [verification-loop canônico](../../.agents/skills/verification-loop/SKILL.md) e [loop-specification canônico](../../.agents/skills/loop-specification/SKILL.md).
- Perfil de referência: [sap-code-reviewer](../../.agents/profiles/sap-code-reviewer.json), com 8 iterações, 900 segundos, 120 segundos/chamada e parada por 3 iterações sem progresso.

