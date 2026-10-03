# Checklist U1: Expiração do estado de execução — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a U1.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [U1](../review-remediation.md#u1)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#u1)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 A especificação define prazo, referência temporal e estados sujeitos à expiração do registro de execução? [Completude, Spec §FR-014, Gap]
- [ ] CHK002 A regra de expiração diferencia tempo desde a criação, inatividade e possíveis renovações autorizadas? [Clareza, Spec §FR-014, Ambiguidade]

## Consistência e definição do escopo

- [ ] CHK003 As regras de expiração do registro, da aprovação e do orçamento total são independentes e consistentes? [Consistência, Spec §FR-010, Spec §FR-012, Spec §FR-014]
- [ ] CHK004 O comportamento de status e resume para registros expirados está definido com motivo e estado observáveis? [Clareza, Spec §FR-014, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação definem o limite temporal exato e zero ações externas após a expiração? [Mensurabilidade, Spec §FR-014, Spec §SC-002, Gap]
- [ ] CHK006 Os requisitos cobrem aprovação pendente, mudança de relógio, migração de versão e retomada sem renovação implícita? [Cobertura, Spec §FR-014, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

