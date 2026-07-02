---
name: sap-workflow-pipeline
description: >-
  Pipeline automatizado spec → transport para ABAP com Business Workflow.
  Lê especificação, identifica módulo SAP, gera proposta técnica, implementa,
  roda abaplint, peer review com 9 dimensões, e produz transporte pronto.
  Incorpora conceitos de BOR (Business Object Repository), eventos, receivers
  e gestão de status do SAP Business Workflow.
trigger:
  - "implement specification"
  - "build from spec"
  - "ABAP pipeline"
  - "full workflow"
  - "spec to code"
  - "automated development"
  - "business workflow"
---

# SAP Workflow Pipeline — Spec → Transport

Pipeline de 8 estágios: spec → análise → proposta → review → implementação →
lint → crew analysis → transport gate. Integrado ao SAP Business Workflow:
BOR object types, eventos, receivers e gestão de status.

## Pré-requisitos

- Python 3.8+ (`scripts/sap_router.py`)
- Node.js 18+ com `@abaplint/cli` instalado
- ADT MCP conectado (arc-1 / aibap / mcp-abap-adt)
- SAP system acessível (DEV) para deploy e activation
- `openpyxl` se usando XLSX: `pip install openpyxl`
- Conhecimento de BOR: object types, eventos, methods (ver Referência RAG abaixo)

## Pipeline — Comandos Copiáveis

```bash
# Pipeline completo (8 estágios, ~50K tokens, 3-5 min)
python scripts/sap_router.py pipeline --spec requirements.md --module auto

# Fast mode: análise → implementação → lint (pula crew analysis, ~15K tokens)
python scripts/sap_router.py pipeline --spec requirements.md --mode fast

# Dry run: analisa spec, gera proposta, não escreve código
python scripts/sap_router.py pipeline --spec requirements.md --dry-run

# Resume a partir de estágio específico (após corrigir issues)
python scripts/sap_router.py pipeline --spec requirements.md --resume-from stage4
```

## Estágios do Pipeline

```
SPEC → 1.Análise → 2.Proposta → 3.Review1 → 4.Implementação
     → 5.Lint → 6.CrewAnalysis → 7.Review2 → 8.TransportGate → DONE
```

- **Estágio 1 — Análise**: parseia spec, identifica módulo (MM/SD/FI/QM/PP/...),
  extrai BAPIs, tabelas, autorizações. Output: `MODULE_ANALYSIS.md`
- **Estágio 2 — Proposta**: 7-agent crew gera design técnico (classes, DDIC,
  BAPIs, auth, test strategy, risks). Output: `TECHNICAL_PROPOSAL.md`
- **Estágio 3 — Review 1**: 9 dimensões (SEC|AUTH|DATA|PERF|STD|INTERFACE|
  CHANGE|COMP|FUNC). GO/NO-GO. NO-GO → volta ao Estágio 2.
- **Estágio 4 — Implementação**: cavecrew-builder + ADT escreve código no SAP,
  syntax check, unit tests.
- **Estágio 5 — Lint**: `abaplint` + security gate + clean code gate.
- **Estágio 6 — Crew Analysis**: 7-agent full mode, 9 dimensões no código
  implementado. Roda em background, paralelo ao Estágio 5.
- **Estágio 7 — Review 2**: compara implementação com Review 1. GO/NO-GO.
  NO-GO → volta ao Estágio 4.
- **Estágio 8 — Transport Gate**: risk assessment 10 dimensões, cria transport
  request, verifica inclusão de objetos.

## Integração com SAP Business Workflow (RAG)

Conceitos de BOR e Workflow incorporados ao pipeline:

### BOR Object Types e Eventos

Eventos comunicam entre aplicação e workflow system. Usados para sincronizar
processos (ex: "Wait until document is released"). O object type é definido no
Business Object Repository (transação `SWO1`).

```python
# Detecção de workflow events no spec analyzer
WORKFLOW_KEYWORDS = {
    'event': ['event', 'trigger', 'BOR', 'object type', 'SWO1'],
    'receiver': ['receiver', 'event receiver', 'linkage', 'SWE2'],
    'status': ['status management', 'work item', 'SWI1', 'SWI2_FREQ'],
    'decision': ['user decision', 'approval', 'reject', 'SBWP'],
}
```

### Transações-Chave de Workflow

- `SWO1` — BOR object type maintenance
- `SWE2` — Event linkage configuration
- `PFTC` — General task maintenance (PFTC_DIS=display, PFTC_CHG=change)
- `SWI1` — Workflow log (overview of steps, container, agents)
- `SBWP` — Business workspace (workitem inbox)
- `SWI2_FREQ` — Work items per task frequency analysis

### APIs de Workflow (Runtime)

```abap
" Obter objetos do work item (leading object como POR)
CALL FUNCTION 'SAP_WAPI_GET_OBJECTS'
  EXPORTING
    workitem_id = lv_wi_id
  IMPORTING
    leading_object = ls_por.

" Converter POR para runtime handle (BOR macro)
" Requer include <cntn01>
SWC_OBJECT_FROM_PERSISTENT ls_por lv_obj.
```

### Status Management

Work item status: `WAITING` → `READY` → `IN_PROGRESS` → `COMPLETED`/`CANCELLED`.
O pipeline valida status em Stage 3 (Review) e Stage 7 (Review 2).

## Template de Proposta Técnica (resumo)

Proposta inclui: Architecture (module, approach, object count), Classes
(`ZCL_{MODULE}_HANDLER/HELPER`), DDIC (`Z{MODULE}_LOG` audit table), Error
Handling (`ZCX_{MODULE}` + BAL + BAPIRET2 TABLES RETURN check), Authorization
(check at method entry + before BAPI), Test Strategy (ABAP Unit + risk level).

## Pitfalls

- **Spec vago** → proposta vaga. Sinalizar seções subespecificadas no Estágio 1.
- **Module misdetection** → specs cross-module (MM+FI) precisam dual routing.
- **BAPIRET2 incompleto** → sempre checar `TABLES RETURN`, nunca só `IMPORTING`.
- **Event linkage esquecido** → se spec menciona eventos BOR, incluir SWE2 config.
- **Token budget** → pipeline completo ~50K tokens. Fast mode ~15K.
- **abaplint version drift** → pinar `@abaplint/cli` no CI. Rule changes flip gates.
- **Crew analysis paralelo** → roda em background. Pipeline continua ao Estágio 5.
- **Transport risk** → gate bloqueia só em CRITICAL security findings. MEDIUM = warning.
- **BOR macro include** → `<cntn01>` obrigatório para `SWC_*` macros. Sem ele = dump.
- **Workitem status race** → validar status antes de operar. `SAP_WAPI_GET_OBJECTS`
  pode retornar POR de work item já CANCELLED.

## Verificação

```bash
# 1. Verificar driver do skill (50 checks, exit 0 = pass)
python .claude/skills/run-sap-router-skill/driver.py

# 2. Verificar MEMORY.md após pipeline
python scripts/memory_manager.py verify --input MEMORY.md

# 3. Verificar objetos deployados via ADT
# (via ADT MCP: read_source + syntax_check em cada objeto)

# 4. Verificar workflow log (se BOR events envolvidos)
# Transação SWI1 no SAP: filtrar por task/template ID

# 5. Verificar event linkage ativo
# Transação SWE2: confirmar linkage ENABLED para o object type/event

# 6. Verificar workitem inbox
# Transação SBWP: confirmar work items criados e assigned corretamente

# 7. Verificar transport
python scripts/sap_router.py transport-status --tr DEVK900043
```

## MEMORY.md — Registro de Pipeline

Cada estágio escreve um bloco em MEMORY.md (máx 20 blocos, 100 linhas):

```
### [14:32] WORKFLOW/MM-CreateMaterial-Spec
status:OK | stage:1 | module:MM | bapi:BAPI_MATERIAL_SAVEDATA

### [14:50] WORKFLOW/MM-CreateMaterial-Transport
status:GO | stage:8 | tr:DEVK900043 | release:APPROVED
```

## Anti-Padrões a Evitar

- ❌ Pular Review 1 (Estágio 3) mesmo em fast mode
- ❌ Ignorar BAPIRET2 com múltiplas linhas de erro
- ❌ Hardcoded work item IDs — sempre obter via `SAP_WAPI_*`
- ❌ Deploy sem syntax check prévio no ADT
- ❌ Release transport sem GO do Estágio 7 e Estágio 8
- ❌ Usar `SWC_*` macros sem include `<cntn01>`
- ❌ Assumir status de work item sem validar em runtime
