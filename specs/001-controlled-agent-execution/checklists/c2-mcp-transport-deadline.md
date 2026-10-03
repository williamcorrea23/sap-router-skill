# Checklist C2: Prazo de todo o transporte MCP — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a C2.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [C2](../review-remediation.md#c2)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#c2)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos de prazo abrangem envio, espera da resposta, negociação e encerramento da operação MCP? [Completude, Spec §FR-004, Spec §FR-012, Gap]
- [ ] CHK002 O limite de uma chamada MCP e sua relação com o orçamento total estão quantificados na especificação? [Clareza, Spec §FR-012, Gap]

## Consistência e definição do escopo

- [ ] CHK003 As regras de prazo permanecem consistentes entre a inicialização do transporte, a descoberta de ferramentas e a chamada selecionada? [Consistência, Spec §FR-012, Gap]
- [ ] CHK004 O comportamento exigido quando o servidor deixa de consumir a entrada ou encerra parcialmente a comunicação está documentado? [Cobertura, Spec §FR-022, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação definem prazo máximo, tolerância de medição e ausência de processos descendentes após o encerramento? [Mensurabilidade, Spec §FR-012, Spec §FR-022, Gap]
- [ ] CHK006 Os requisitos cobrem comunicação bloqueada, resposta tardia, interrupção e diferenças de plataforma Windows/POSIX? [Cobertura, Spec §FR-004, Spec §FR-022, Plano §Technical Context, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

