# Checklist C3: Contratos no catálogo estrito — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a C3.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [C3](../review-remediation.md#c3)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#c3)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos declaram todos os contratos de ferramentas como parte do catálogo sujeito à validação estrita? [Completude, Spec §FR-006, Spec §FR-017]
- [ ] CHK002 As condições de compatibilidade entre contrato, capacidade, servidor, efeito e política estão explicitamente definidas? [Clareza, Spec §FR-006, Spec §FR-007, Spec §FR-017]

## Consistência e definição do escopo

- [ ] CHK003 As regras de consistência do catálogo e as regras anteriores ao despacho exigem os mesmos vínculos e fingerprints? [Consistência, Spec §FR-006, Spec §FR-017]
- [ ] CHK004 As exceções para contratos exclusivos de fixtures estão delimitadas sem autorizar seu uso como provedores reais? [Cobertura, Spec §FR-022, Tarefas §T025, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação exigem falha e diagnóstico identificável para hash ou efeito incompatível, em vez de apenas uma contagem de entradas? [Mensurabilidade, Spec §FR-017, Spec §SC-002, Gap]
- [ ] CHK006 Os requisitos cobrem contratos duplicados, capacidade inexistente, servidor desabilitado e mudanças de esquema? [Cobertura, Spec §FR-006, Spec §FR-017, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

