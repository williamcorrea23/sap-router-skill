# Checklist C5: Capacidade inexistente e estado terminal — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a C5.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [C5](../review-remediation.md#c5)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#c5)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos de resolução abrangem capacidade, servidor, perfil e alias inexistentes antes de qualquer uso operacional? [Completude, Spec §FR-003, Spec §FR-021]
- [ ] CHK002 O formato e o motivo do erro para capacidade desconhecida estão definidos na especificação? [Clareza, Spec §FR-017, Gap]

## Consistência e definição do escopo

- [ ] CHK003 As regras de falha estruturada são consistentes entre classificador, launcher e executor? [Consistência, Spec §FR-003, Spec §FR-017, Gap]
- [ ] CHK004 A especificação define o estado terminal e a persistência exigidos quando uma dependência canônica desaparece? [Completude, Spec §FR-012, Spec §FR-013, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação exigem zero chamadas externas, motivo identificável e ausência de registro abandonado em Running? [Mensurabilidade, Spec §FR-017, Spec §SC-002, Gap]
- [ ] CHK006 Os requisitos cobrem alias inválido, rota sem perfil, capacidade removida e retomada com catálogo incompatível? [Cobertura, Spec §FR-014, Spec §FR-021, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

