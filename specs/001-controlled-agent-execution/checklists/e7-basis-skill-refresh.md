# Checklist E7: Atualização das skills Basis — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a E7.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [E7](../review-remediation.md#e7)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#e7)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos de atualização inventariam as 21 novas skills e as alterações das 12 já importadas por revisão imutável? [Completude, Revisão §E7, Gap]
- [ ] CHK002 O escopo de conhecimento operacional e o escopo de execução OS/DB/SAP estão claramente delimitados? [Clareza, Revisão §E7, Gap]

## Consistência e definição do escopo

- [ ] CHK003 As regras de importação preservam uma fonte canônica e geração de mirrors sem duplicar corpos ou aliases conflitantes? [Consistência, Spec §FR-015, Spec §SC-004, Revisão §E7]
- [ ] CHK004 Os requisitos mantêm protocolos Karpathy, loop e verificação, além de destino, pré-condições e aprovação para efeitos operacionais? [Completude, Spec §FR-009, Spec §FR-015, Revisão §E7, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação exigem catálogo e paridade derivados do conteúdo aprovado, com evidência e contagens atualizadas? [Mensurabilidade, Spec §FR-016, Spec §SC-004, Revisão §E7]
- [ ] CHK006 Os requisitos cobrem skill rejeitada, conflito de atualização, documentação de dependência externa e cenário destrutivo em produção? [Cobertura, Revisão §E7, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

