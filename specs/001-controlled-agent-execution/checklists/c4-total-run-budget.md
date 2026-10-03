# Checklist C4: Orçamento total antes do despacho — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a C4.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [C4](../review-remediation.md#c4)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#c4)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos incluem negociação, descoberta de ferramentas, verificação e despacho no mesmo orçamento total? [Completude, Spec §FR-012, Gap]
- [ ] CHK002 O início, a contabilização e a persistência do tempo disponível estão definidos de forma mensurável? [Clareza, Spec §FR-012, Spec §FR-013, Gap]

## Consistência e definição do escopo

- [ ] CHK003 A expiração do orçamento é consistente com a proibição de reservar aprovação ou iniciar ações externas após o limite? [Consistência, Spec §FR-009, Spec §FR-012, Gap]
- [ ] CHK004 A especificação distingue esgotamento do orçamento, timeout de uma chamada e expiração do estado de execução? [Clareza, Spec §FR-012, Spec §FR-014, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação exigem zero despachos e zero reservas tardias quando fases anteriores consomem o tempo restante? [Mensurabilidade, Spec §FR-009, Spec §FR-012, Gap]
- [ ] CHK006 Os requisitos cobrem orçamento reduzido, aprovação pendente, retomada e expiração durante a negociação? [Cobertura, Spec §FR-012, Spec §FR-014, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

