# Plano de Integração Revisado: sapstack + sc4sap → sap-router-orchestrator

> **Correção importante**: Os agentes do sapstack **SIM têm** YAML frontmatter Claude-native
> (`name:`, `description:`, `tools:`, `model:`). Ambas as fontes são compatíveis e adaptáveis.

---

## Comparação Real dos Formatos

### sapstack (BoxLogoDev) — formato real encontrado:
```yaml
---
name: sap-qm-consultant
description: SAP QM(품질관리) 한국어 전문가. 검사계획(QP01), 검사로트(QA01)...
tools: Read, Grep, Glob
model: sonnet
---
```
**Conteúdo**: Prompt completo em coreano com seções estruturadas (핵심 원칙, 응답 형식, T-codes, regras por indústria)

### sc4sap (babamba2) — formato real encontrado:
```yaml
---
name: sap-fi-consultant
description: SAP Financial Accounting consultant — general ledger, AP/AR, asset...
model: claude-opus-4-7
tools: [Read, Grep, Glob, Bash, WebFetch, mcp__plugin_sc4sap_sap__GetTable, ...]
disallowedTools: [Write, Edit]
---
```
**Conteúdo**: Prompt em inglês com carregamento de contexto em tiers, referências a `configs/`, MCP tools do ADT

---

## O Que Adaptar (apenas 3 mudanças mínimas)

Para qualquer agente de qualquer fonte, a adaptação tem **3 passos simples**:

### 1. Ajustar `description:` para roteamento correto em PT-BR
```yaml
# Antes (sapstack — coreano):
description: SAP TR(자금관리) 한국어 컨설턴트. 유동성 계획(FF7A/FF7B)...

# Depois (adaptado — PT-BR + inglês):
description: >
  SAP Treasury (TR) specialist — liquidity planning (FF7A/FF7B), cash management,
  house banks (FI12), payment run (F110), bank statements (FF_5), DMEE, MT940.
  Trigger on: treasury, cash management, bank reconciliation, liquidity questions.
```

### 2. Remover/ajustar `tools:` para MCPs disponíveis localmente
```yaml
# Antes (sc4sap — com MCPs proprietários):
tools: [Read, Grep, mcp__plugin_sc4sap_sap__GetTable, mcp__plugin_sc4sap_sap__SearchObject]

# Depois (sem MCPs sc4sap):
tools: [Read, Grep, Glob]
```

### 3. Ajustar paths internos (referências a `plugins/` → paths do sap-router-skill)
```
# Antes (sapstack):
SKILL.md 참조 — `plugins/sap-tr/skills/sap-tr/SKILL.md`

# Depois:
Referir-se a: `references/module_maps/tr_operations.md`
```

**O corpo do prompt (conhecimento SAP) não precisa de alteração — está correto e rico.**

---

## Inventário Completo dos Agentes Disponíveis

### sapstack — 19 agentes com YAML frontmatter
| Arquivo | Módulo | Idioma | Cobertura |
|---|---|---|---|
| `sap-fi-consultant.md` | FI | 🇰🇷 KO | G/L, AP, AR, Asset, F110 |
| `sap-co-consultant.md` | CO | 🇰🇷 KO | Cost centers, orders, PA |
| `sap-mm-consultant.md` | MM | 🇰🇷 KO | Procurement, GR/GI, inventory |
| `sap-sd-consultant.md` | SD | 🇰🇷 KO | Sales orders, delivery, billing |
| `sap-pp-consultant.md` | PP | 🇰🇷 KO | Production orders, MRP, routing |
| `sap-qm-consultant.md` | QM | 🇰🇷 KO | Inspection, AQL, QM01, SPC |
| `sap-hcm-consultant.md` | HCM | 🇰🇷 KO | HR master, payroll, time |
| `sap-tr-consultant.md` | **TR** ⭐ | 🇰🇷 KO | Liquidity, F110, DMEE, MT940 |
| `sap-pm-consultant.md` | **PM** ⭐ | 🇰🇷 KO | Work orders, maintenance plans |
| `sap-ewm-consultant.md` | **EWM** ⭐ | 🇰🇷 KO | Extended WM, putaway, wave picking |
| `sap-abap-developer.md` | ABAP | 🇰🇷 KO | Code, ALV, BAdI, FM |
| `sap-basis-consultant.md` | BASIS | 🇰🇷 KO | System admin, transport |
| `sap-ariba-consultant.md` | Ariba | 🇰🇷 KO | Procurement cloud |
| `sap-ibp-consultant.md` | IBP | 🇰🇷 KO | Demand planning, supply |
| `sap-integration-cloud-consultant.md` | CPI | 🇰🇷 KO | Integration Suite, iFlow |
| `sap-cloud-consultant.md` | BTP/Cloud | 🇰🇷 KO | BTP, RISE, Cloud PE |
| `sap-s4-migration-advisor.md` | S4Mig | 🇰🇷 KO | ECC→S/4 migration |
| `sap-sac-consultant.md` | SAC | 🇰🇷 KO | Analytics Cloud, stories |
| `sap-tutor.md` | Router | 🇰🇷 KO | Classifier/delegator agent |
| `sap-integration-advisor.md` | Integration | 🇰🇷 KO | CPI, RFC, OData, IDoc |

### sc4sap — 21 agentes com YAML frontmatter (inglês, MCPs ADT)
| Arquivo | Módulo | Diferencial vs sapstack |
|---|---|---|
| `sap-fi-consultant.md` | FI | + configs/FI/ (bapi, spro, tables) |
| `sap-co-consultant.md` | CO | + configs/CO/ |
| `sap-mm-consultant.md` | MM | + configs/MM/ |
| `sap-sd-consultant.md` | SD | + configs/SD/ |
| `sap-hcm-consultant.md` | HCM | + configs/HCM/ |
| `sap-pm-consultant.md` | PM | + configs/PM/ |
| `sap-pp-consultant.md` | PP | + configs/PP/ |
| `sap-qm-consultant.md` | QM | + configs/QM/ |
| `sap-tm-consultant.md` | TM | único: Transport Management |
| `sap-tr-consultant.md` | TR | + configs/TR/ |
| `sap-wm-consultant.md` | WM | + configs/WM/ |
| `sap-bw-consultant.md` | BW | + configs/BW/ |
| `sap-ariba-consultant.md` | Ariba | + configs/Ariba/ |
| `sap-bc-consultant.md` | BC | Basis/BC |
| `sap-code-reviewer.md` | ABAP | Clean ABAP, security, performance |
| `sap-debugger.md` | ABAP | ST22, SM02, profiler |
| `sap-executor.md` | ABAP | Cria/edita objetos via MCP ADT |
| `sap-planner.md` | Orchestrator | Planejador de tarefas |
| `sap-analyst.md` | Analysis | Análise de dados/specs |
| `sap-architect.md` | Architecture | Design de solução |
| `sap-writer.md` | Documentation | Specs, documentação |

---

## Estratégia de Adoção: Melhor dos Dois Mundos

**Para módulos em ambos** (FI, CO, MM, SD, PP, QM, HCM, TR, PM, Ariba):
- **Usar sapstack como base** (conteúdo operacional mais rico, Evidence Loop integrado)
- **Complementar com configs/ do sc4sap** (dados estruturados: bapi, spro, tcodes por módulo)

**Para módulos só no sapstack** (EWM, IBP, SAC, CPI, S4Mig, Cloud, Tutor, Integration Advisor):
- Adaptar diretamente do sapstack

**Para módulos só no sc4sap** (TM, Code Reviewer, Debugger, Executor, Architect, Writer):
- Adaptar do sc4sap removendo MCPs ADT

---

## Estrutura de Destino no sap-router-skill

```
sap-router-skill/
├── packages/
│   └── agents/                          ← NOVO: sub-agentes invocáveis
│       ├── sap-tr-consultant.md         (sapstack adaptado — lacuna crítica)
│       ├── sap-pm-consultant.md         (sapstack adaptado — lacuna crítica)
│       ├── sap-ewm-consultant.md        (sapstack adaptado — único no sapstack)
│       ├── sap-tm-consultant.md         (sc4sap adaptado — único no sc4sap)
│       ├── sap-bw-consultant.md         (sc4sap adaptado)
│       ├── sap-ariba-consultant.md      (sapstack adaptado)
│       ├── sap-ibp-consultant.md        (sapstack adaptado)
│       ├── sap-sac-consultant.md        (sapstack adaptado)
│       ├── sap-s4-migration-advisor.md  (sapstack adaptado)
│       ├── sap-code-reviewer.md         (sc4sap adaptado — lacuna crítica)
│       ├── sap-abap-developer.md        (sapstack adaptado)
│       ├── sap-basis-consultant.md      (sapstack adaptado)
│       ├── sap-cloud-consultant.md      (sapstack adaptado)
│       ├── sap-integration-advisor.md   (sapstack adaptado)
│       └── sap-tutor.md                 (sapstack — classificador/roteador)
│
├── references/
│   ├── module_maps/                     ← EXISTENTE + expandir
│   │   ├── tr_operations.md             NOVO
│   │   ├── pm_operations.md             NOVO
│   │   └── ewm_operations.md            NOVO
│   └── data/                            ← NOVO: dados operacionais
│       ├── symptom-index.yaml           (sapstack — 106KB, 1000+ sintomas)
│       ├── tcodes.yaml                  (sapstack — 46KB)
│       └── sap-notes.yaml               (sapstack — 42KB)
│
└── templates/
    └── commands/                        ← NOVO: 22 comandos operacionais
        ├── sap-fi-closing.md
        ├── sap-migo-debug.md
        ├── sap-payment-run-debug.md
        ├── sap-transport-debug.md
        └── ...
```

---

## Plano de Execução (4 Fases)

### Fase 1 — Criar agentes das lacunas críticas (agora)
- [ ] `sap-tr-consultant.md` → copiar do sapstack + ajustar description/paths
- [ ] `sap-pm-consultant.md` → copiar do sapstack + ajustar description/paths
- [ ] `sap-code-reviewer.md` → copiar do sc4sap + remover MCPs ADT
- [ ] `tr_operations.md` e `pm_operations.md` em `references/module_maps/`

### Fase 2 — Importar dados para enriquecer o roteador
- [ ] `symptom-index.yaml` → fonte direta para roteamento semântico por sintoma
- [ ] `tcodes.yaml` → mapa de T-codes para classify por módulo
- [ ] Atualizar `sap_router.py` para usar esses índices

### Fase 3 — Agentes de módulos faltantes
- [ ] EWM, TM, BW, Ariba, IBP, SAC, S4Mig, Cloud, Integration Advisor

### Fase 4 — Comandos operacionais
- [ ] Adaptar os 22 `commands/` do sapstack como slash-commands do orquestrador

---

> **Próximo passo sugerido**: Executar a Fase 1 agora — criar os 3 agentes críticos (TR, PM, Code Reviewer)
> dentro de `sap-router-skill/packages/agents/` usando o sapstack como base.
