# Checklist C1: Credenciais em respostas MCP — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a C1.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [C1](../review-remediation.md#c1)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#c1)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos de proteção abrangem todos os canais das respostas MCP, inclusive texto e conteúdo estruturado duplicado? [Completude, Spec §FR-005, Spec §FR-013]
- [ ] CHK002 Os requisitos identificam quais valores e campos são sensíveis mesmo quando não vieram do ambiente do subprocesso? [Clareza, Spec §FR-005, Gap]

## Consistência e definição do escopo

- [ ] CHK003 As regras documentadas exigem proteção equivalente para representações textuais e estruturadas da mesma resposta? [Consistência, Spec §FR-005, Gap]
- [ ] CHK004 A especificação delimita o tratamento de JSON malformado e respostas de erro sem permitir exposição de credenciais? [Cobertura, Spec §FR-005, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação definem ausência mensurável de credenciais no contexto dos modelos, nas observações e nos arquivos persistidos? [Mensurabilidade, Spec §FR-005, Spec §FR-013, Spec §FR-016]
- [ ] CHK006 Os requisitos cobrem conteúdo somente textual, estruturas aninhadas, caracteres escapados e valores sensíveis desconhecidos previamente? [Cobertura, Spec §FR-005, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

