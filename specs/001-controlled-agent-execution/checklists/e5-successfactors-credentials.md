# Checklist E5: Credenciais e adequação do SuccessFactors MCP — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a E5.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [E5](../review-remediation.md#e5)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#e5)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos definem como o provedor recebe credenciais sem incluí-las em argumentos apresentados ao modelo? [Completude, Spec §FR-005, Revisão §E5, Gap]
- [ ] CHK002 A autenticação real, data center, instance e endpoint selecionados estão documentados sem pressupor suporte OAuth inexistente na versão revisada? [Clareza, Spec §FR-007, Revisão §E5, Gap]

## Consistência e definição do escopo

- [ ] CHK003 As regras de schemas, prompts e registros são consistentes com a proibição de auth_password ou valores secretos no contexto do modelo? [Consistência, Spec §FR-005, Spec §FR-006, Revisão §E5, Gap]
- [ ] CHK004 Os requisitos delimitam permissões HR, campos autorizados, paginação, cache e volume de resultados por objetivo? [Completude, Spec §FR-007, Spec §FR-012, Revisão §E5, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação exigem funcionamento com segredos mantidos no provedor e falha controlada por ausência de credencial ou permissão? [Mensurabilidade, Spec §FR-005, Spec §SC-002, Revisão §E5, Gap]
- [ ] CHK006 Os requisitos cobrem expiração de autenticação, erro de tenant/data center e verificação real necessária antes da promoção? [Cobertura, Spec §FR-022, Revisão §E5, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

