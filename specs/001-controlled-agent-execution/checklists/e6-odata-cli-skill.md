# Checklist E6: Skill e CLI SAP OData — Controlled Agent Execution

**Purpose**: Avaliar clareza, completude e critérios de aceitação dos requisitos associados a E6.
**Created**: 2026-10-02
**Feature**: [spec.md](../spec.md)
**Finding**: [E6](../review-remediation.md#e6)
**Loop**: [Procedimento de verificação](../verification/peer-review-loop.md#e6)
**Depth**: Standard; foco nos riscos identificados; uso por reviewer antes de implementar ou promover.

**Note**: Gerado com `speckit-checklist` a partir do pedido do usuário, da especificação e da revisão.
**Review Ownership**: Este checklist pertence ao reviewer e avalia a qualidade dos requisitos.
**Marker Semantics**: `[x]` significa requisito revisado e suficientemente definido; não significa correção implementada. Os itens são criados em `[ ]` e só podem ser marcados pelo reviewer ou por agente explicitamente autorizado a avaliar os requisitos.

## Completude e clareza dos requisitos

- [ ] CHK001 Os requisitos identificam a fonte como skill e CLI, explicitando qualquer adapter necessário para o harness? [Completude, Spec §FR-015, Revisão §E6, Gap]
- [ ] CHK002 O escopo distingue leitura SAP de alterações locais em perfis e biblioteca offline? [Clareza, Revisão §E6, Gap]

## Consistência e definição do escopo

- [ ] CHK003 As regras de credenciais preservam keyring ou referências de ambiente sem valores em argumentos ou prompts? [Consistência, Spec §FR-005, Revisão §E6]
- [ ] CHK004 Os requisitos de binário fixado, saída estruturada, erros e perfis de conexão estão documentados? [Completude, Spec §FR-018, Revisão §E6, Gap]

## Critérios de aceitação e cobertura

- [ ] CHK005 Os critérios de aceitação distinguem metadata/lint offline de consultas reais e exigem falha identificável quando não há autenticação? [Mensurabilidade, Spec §FR-016, Spec §FR-022, Revisão §E6, Gap]
- [ ] CHK006 Os requisitos cobrem OData v2/v4, SSO vencido, keyring indisponível e alterações locais destrutivas solicitadas explicitamente? [Cobertura, Revisão §E6, Gap]

## Notes

- Os IDs CHK001–CHK006 são únicos dentro deste arquivo; a referência completa inclui o caminho do checklist.
- `speckit-implement` lê o estado destes critérios como gate e não deve modificar os marcadores.
- As verificações de implementação e suas evidências ficam no loop; a revisão dos requisitos permanece responsabilidade do reviewer.
- Marcadores `Gap`, `Ambiguidade` e `Conflito` indicam decisões ou ajustes documentais ainda necessários.
- Os itens E1–E7 representam adequações condicionadas à adoção; não ampliam automaticamente os nove candidatos de FR-020/SC-005.

