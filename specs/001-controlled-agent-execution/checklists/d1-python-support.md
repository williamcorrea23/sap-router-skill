# Checklist D1: Versão mínima e suporte Python — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a D1.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [D1](../review-remediation.md#d1)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#d1)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos documentam a versão mínima para o harness e para os comandos apresentados ao usuário? [Completude, Plano §Technical Context, Gap]
- [ ] CHK002 O alcance do suporte de scripts legados e do novo executor está definido sem uma promessa geral incompatível? [Clareza, Plano §Technical Context, Ambiguidade]

## Consistência e definição do escopo

- [ ] CHK003 As versões anunciadas em AGENTS, README, plano e instruções geradas estão consistentes? [Consistência, Plano §Technical Context, Conflito]
- [ ] CHK004 As dependências de linguagem e dos CLIs externos estão documentadas como requisitos distintos? [Completude, Plano §Technical Context, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação identificam a versão efetivamente validada e mantêm NOT_RUN para plataformas ou intérpretes indisponíveis? [Mensurabilidade, Spec §FR-016, Spec §SC-006]
- [ ] CHK006 Os requisitos cobrem inicialização com versão insuficiente e preservação de documentação específica de comandos legados? [Cobertura, Plano §Technical Context, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

