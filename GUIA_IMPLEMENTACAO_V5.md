# Guia de Implementação Técnica — SAP Router Orchestrator v5.0

> **Público-alvo**: IDE agêntica (Claude Code, Cursor, Antigravity) executando de forma autônoma.
> **Formato**: Fases sequenciais P0→P3. Cada tarefa tem: contexto, arquivos, código, critério de aceite, comando de verificação.
> **Regras Karpathy**: mudanças cirúrgicas; não tocar arquivos fora do escopo da tarefa; verificar cada fase antes da próxima.
> **Diretório raiz**: `C:\Users\William Correa\Downloads\sap-router-orchestrator-files\`

---

## Estado Atual (baseline verificado em 2026-07-01)

| Componente | Estado | Referência |
|---|---|---|
| `sap-router-skill/scripts/sap_router.py` | v4.2.0, ~950 linhas, monolítico. Mapas hardcoded (BAPI, GUI, pipeline, caveman) | linhas 73-172 |
| `sap-router-skill/scripts/self_learn.py` | Completo (~370 linhas) mas **nunca chamado pelo router** | — |
| `sap-router-skill/scripts/healthcheck.py` | Completo (35 MCPs) mas **desconectado do routing** | — |
| `sap-router-skill/scripts/fallback_engine.py` | Tiers 1-6 são stubs simulados, não executam MCP real | — |
| `.claude/agents/` | **NÃO EXISTE** | — |
| `packages/agents/` | **NÃO EXISTE** (plano integracao_subagentes_sap.md 0% executado) | — |
| Skills duplicadas | `.claude/` + `.codex/` + `.cursor/` + `.gemini/` = 4 cópias de ~73 skills | ~48k arquivos |
| `references/module_maps/` | 10 mapas existem (Basis, MM, SD, FI, QM, PP, WM, CO, HCM×2). **Faltam TR, PM, EWM** | — |
| Dados sapstack (`symptom-index.yaml`, `tcodes.yaml`, `sap-notes.yaml`) | **Não importados** | fontes externas |

**Fontes externas** (necessárias para P0.2 e P2.2 — verificar disponibilidade antes de começar):
- sapstack (BoxLogoDev): 19 agentes KO + dados YAML — `https://github.com/BoxLogoDev/sapstack`
- sc4sap (babamba2): 21 agentes EN + configs/ — `https://github.com/babamba2/sc4sap`
- Se repositórios inacessíveis: criar agentes do zero usando module_maps locais como base (fallback documentado em cada tarefa).

---

# FASE P0 — Fundação (executar primeiro, ~2h)

## P0.1 — Deduplicar skills (5 min)

**Contexto**: 73 skills × 4 plataformas = 292 SKILL.md idênticas. `.claude/skills/` é a cópia canônica.

**Ação**:
```powershell
# ANTES de deletar: comparar POR NOME (não por contagem) — garante superset real
$claude = (Get-ChildItem "sap-router-skill\.claude\skills" -Directory).Name
foreach ($dir in @(".codex", ".cursor", ".gemini")) {
    $other = (Get-ChildItem "sap-router-skill\$dir\skills" -Directory -ErrorAction SilentlyContinue).Name
    $missing = $other | Where-Object { $_ -notin $claude }
    if ($missing) {
        Write-Host "MOVER antes de deletar ($dir): $($missing -join ', ')"
        foreach ($m in $missing) {
            Move-Item "sap-router-skill\$dir\skills\$m" "sap-router-skill\.claude\skills\$m"
        }
    }
}

# Só depois do move (ou se $missing vazio em todos):
Remove-Item -Recurse -Force "sap-router-skill\.codex"
Remove-Item -Recurse -Force "sap-router-skill\.cursor"
Remove-Item -Recurse -Force "sap-router-skill\.gemini"
```

**Aceite**: `.claude/skills/` intacto com ≥73 skills; outros 3 diretórios removidos; contagem total de arquivos do repo cai ~75%.

---

## P0.2 — Criar `.claude/agents/` + 3 agentes críticos (1h)

**Contexto**: Fase 1 do `integracao_subagentes_sap.md`. Lacunas críticas: TR, PM, Code Reviewer.

**Estrutura a criar**:
```
sap-router-skill/
└── .claude/
    └── agents/
        ├── sap-tr-consultant.md
        ├── sap-pm-consultant.md
        └── sap-code-reviewer.md
```

**Template obrigatório** (frontmatter Claude-native — validar com parser YAML):

```markdown
---
name: sap-tr-consultant
description: >
  SAP Treasury (TR) specialist — liquidity planning (FF7A/FF7B), cash management,
  house banks (FI12), payment run (F110), bank statements (FF_5), DMEE, MT940/MT942,
  in-house cash, exposure management. Trigger on: treasury, cash management,
  bank reconciliation, liquidity, payment run, DMEE tree, extrato bancário,
  conciliação bancária, tesouraria, fluxo de caixa.
tools: [Read, Grep, Glob]
model: sonnet
---

# SAP Treasury (TR) Consultant

## Escopo
- Liquidity planning: FF7A (cash position), FF7B (liquidity forecast)
- House banks: FI12, tabelas T012, T012K
- Payment run F110: parâmetros, proposta, execução, DME
- Bank statements: FF_5 (import MT940), FEBAN (pós-processamento), FEBA
- DMEE: árvores de formato para pagamento (DMEE tcode)
- Config: OBVCU (métodos pagamento), FBZP (config F110 completa)

## Tabelas-chave
| Tabela | Conteúdo |
|---|---|
| T012/T012K | House banks / contas bancárias |
| REGUH/REGUP | Dados de pagamento F110 (header/item) |
| FEBKO/FEBEP | Extrato bancário header/item |
| PAYR | Cheques emitidos |
| TCURR | Taxas de câmbio |

## BAPIs/FMs principais
- BAPI_ACC_DOCUMENT_POST (lançamentos)
- FF_5 via RFBIDE00 / batch input
- FI_PAYMENT_PROPOSAL_* (F110 programático)

## Regras de resposta
1. Sempre citar T-code + tabela + BAPI quando aplicável.
2. Config F110 → apontar FBZP seção específica (banco pagador, métodos, formas).
3. Erro em extrato → verificar FEBKO status + algoritmo de interpretação (OT83).
4. Responder no idioma do usuário (PT-BR default).
```

**Agente 2 — `sap-pm-consultant.md`** (mesma estrutura):
```yaml
---
name: sap-pm-consultant
description: >
  SAP Plant Maintenance (PM) specialist — work orders (IW31/IW32), notifications
  (IW21), maintenance plans (IP41/IP42), task lists (IA05), equipment (IE01),
  functional locations (IL01), preventive maintenance scheduling (IP10/IP30).
  Trigger on: manutenção, ordem de manutenção, work order, equipment, notification,
  maintenance plan, plano de manutenção, apontamento manutenção.
tools: [Read, Grep, Glob]
model: sonnet
---
```
Corpo: escopo IW21-IW67, IP10-IP42, IE01-IE03, IL01-IL03; tabelas AUFK/AFIH/QMEL/EQUI/IFLOT/MPLA/MPOS; BAPIs `BAPI_ALM_ORDER_MAINTAIN`, `BAPI_ALM_NOTIF_CREATE`, `BAPI_EQUI_CREATE`.

**Agente 3 — `sap-code-reviewer.md`**:
```yaml
---
name: sap-code-reviewer
description: >
  ABAP code reviewer — Clean ABAP compliance, security audit (AUTHORITY-CHECK,
  SQL injection, hardcoded credentials), performance analysis (SELECT in loops,
  nested loops, FOR ALL ENTRIES sem check), 9-dimension release gate scoring.
  Trigger on: review ABAP, code review, revisar código, auditar código, quality gate.
tools: [Read, Grep, Glob, Bash]
model: sonnet
disallowedTools: [Write, Edit]
---
```
Corpo: 9 dimensões (SEC, AUTH, DATA, PERF, STD, INTERFACE, CHANGE, COMP, FUNC) com score 0-100 cada; threshold ≥70 = GO; formato de saída: 1 finding por linha `path:line: SEVERITY: problema. fix.`; referenciar `references/trench_knowledge/abap.md` local.

**Fallback se sapstack/sc4sap inacessíveis**: corpos acima já são autossuficientes — expandir usando `references/module_maps/*.md` e `references/trench_knowledge/*.md` locais.

**Aceite**:
1. 3 arquivos existem em `sap-router-skill/.claude/agents/`.
2. Frontmatter parseia: `python -c "import yaml,io; [yaml.safe_load(io.open(f,encoding='utf-8').read().split('---')[1]) for f in ['sap-router-skill/.claude/agents/sap-tr-consultant.md','sap-router-skill/.claude/agents/sap-pm-consultant.md','sap-router-skill/.claude/agents/sap-code-reviewer.md']]"` sem erro.
3. Cada `description` contém trigger keywords PT-BR + EN.

---

## P0.3 — Module maps faltantes: TR + PM (30 min)

**Criar**: `sap-router-skill/references/module_maps/tr_operations.md` e `pm_operations.md`.

**Formato**: idêntico aos 10 existentes (ver `mm_operations.md` como referência de estilo). Estrutura mínima:

```markdown
# TR — Treasury Operations Map

## Operações × BAPIs × Config
| Operação | ZROUTER Action | BAPI/FM | Config Tables |
|----------|---------------|---------|---------------|
| Payment run | TR_PAYMENT_RUN | F110 via batch/FI_PAYMENT_* | T042* (FBZP) |
| Import extrato | TR_IMPORT_STATEMENT | FF_5 / RFEBKA00 | T028G (algoritmos) |
| Cash position | TR_CASH_POSITION | FF7A read | T036/T037 |
| Check config | TR_CHECK_CONFIG | SQL | T012, T012K, T042, T028G |

## T-codes
F110, FF_5, FF7A, FF7B, FI12, FBZP, FEBAN, DMEE, OT83
```

PM análogo: IW31/IW21/IP10 etc., tabelas AUFK/QMEL/EQUI/MPLA, BAPI_ALM_*.

**Aceite**: 12 arquivos em `references/module_maps/` (10 existentes + 2 novos).

---

## P0.4 — Config externa: extrair mapas hardcoded para YAML (1h)

**Contexto**: Gap #2. `sap_router.py` linhas 73-172 têm 5 mapas hardcoded. Extrair para `config/` → plugin architecture.

**Criar diretório**: `sap-router-skill/config/`

**Arquivo 1 — `config/routing_maps.yaml`** (conteúdo migrado 1:1 do código atual):
```yaml
# SAP Router v5.0 — routing configuration (externalized from sap_router.py v4.2)
adt_actions:
  - read_source
  - search_object
  - syntax_check
  - where_used
  - get_deps
  - code_search

functional_write_keywords:
  [CREATE, CHANGE, POST, MOVEMENT, RECEIPT, DELIVERY, BILLING,
   INVOICE, CONFIRM, RELEASE, REVERSE, SAVE, UPDATE, CANCEL,
   PAYMENT]  # v5: sem PAYMENT, ação PAYMENT_RUN nunca passa pelo functional gate

functional_read_keywords:
  [READ, DISPLAY, OVERVIEW, CHECK, GET, LIST, SEARCH]

functional_bapi_map:
  CREATE_MATERIAL:       BAPI_MATERIAL_SAVEDATA
  CHANGE_MATERIAL:       BAPI_MATERIAL_SAVEDATA
  CREATE_PO:             BAPI_PO_CREATE1
  CHANGE_PO:             BAPI_PO_CHANGE
  GOODS_MOVEMENT:        BAPI_GOODSMVT_CREATE
  GOODS_RECEIPT:         BAPI_GOODSMVT_CREATE
  CREATE_DELIVERY:       BAPI_OUTB_DELIVERY_CREATE_SLS
  CREATE_INVOICE:        BAPI_BILLINGDOC_CREATEMULTIPLE
  CREATE_SALES_ORDER:    BAPI_SALESORDER_CREATEFROMDAT2
  CHANGE_SALES_ORDER:    BAPI_SALESORDER_CHANGE
  POST_DOCUMENT:         BAPI_ACC_DOCUMENT_POST
  REVERSE_DOCUMENT:      BAPI_ACC_DOCUMENT_REV_POST
  CREATE_INSPECTION:     BAPI_INSPLOT_CREATE
  CREATE_RN:             ZFM_QM_CREATE_RN
  CREATE_INTERNAL_ORDER: BAPI_INTERNALORDER_CREATE
  CREATE_PROD_ORDER:     BAPI_PRODORD_CREATE
  # NOVOS (P0.3): TR + PM
  PAYMENT_RUN:           F110_BATCH
  CREATE_MAINT_ORDER:    BAPI_ALM_ORDER_MAINTAIN
  CREATE_NOTIFICATION:   BAPI_ALM_NOTIF_CREATE

gui_fallback_map:
  SPRO_CONFIG:           {tcode: SPRO,  description: IMG Customizing}
  TABLE_MAINTENANCE:     {tcode: SM30,  description: Table View Maintenance}
  USER_MAINTENANCE:      {tcode: SU01,  description: User Maintenance}
  AUTH_CHECK:            {tcode: SU53,  description: Authorization Check}
  ROLE_EDITOR:           {tcode: PFCG,  description: Role Maintenance}
  NOTE_APPLY:            {tcode: SNOTE, description: SAP Note Application}
  MATERIAL_GUI:          {tcode: MM01,  description: Create Material (GUI)}
  MATERIAL_CHANGE_GUI:   {tcode: MM02,  description: Change Material (GUI)}
  PO_CREATE_GUI:         {tcode: ME21N, description: Create Purchase Order}
  GOODS_RECEIPT:         {tcode: MIGO,  description: Goods Movement}
  STOCK_OVERVIEW:        {tcode: MMBE,  description: Stock Overview}
  ORDER_CREATE_GUI:      {tcode: VA01,  description: Create Sales Order}
  ORDER_CHANGE_GUI:      {tcode: VA02,  description: Change Sales Order}
  DELIVERY_CREATE_GUI:   {tcode: VL01N, description: Create Delivery}
  BILLING_CREATE_GUI:    {tcode: VF01,  description: Create Billing Document}
  FI_POST_GUI:           {tcode: FB01,  description: Post Document (GUI)}
  GL_MASTER_GUI:         {tcode: FS00,  description: GL Account Master}
  INSPECTION_CREATE_GUI: {tcode: QA01,  description: Create Inspection Lot}
  PROD_ORDER_CREATE_GUI: {tcode: CO01,  description: Create Production Order}
  INTERNAL_ORDER_GUI:    {tcode: KO01,  description: Create Internal Order}
  EMPLOYEE_DISPLAY_GUI:  {tcode: PA20,  description: Display HR Master Data}
  SE16_DATA:             {tcode: SE16,  description: Data Browser}
  SE80_NAVIGATE:         {tcode: SE80,  description: Object Navigator}
  SA38_EXECUTE:          {tcode: SA38,  description: Program Execution}
  ST22_SCAN_GUI:         {tcode: ST22,  description: Dump Analysis}
  SM37_JOB_MONITOR:      {tcode: SM37,  description: Job Monitor}
  SM50_PROCESS_LIST:     {tcode: SM50,  description: Process Overview}
  # NOVOS TR + PM
  PAYMENT_RUN_GUI:       {tcode: F110,  description: Payment Run}
  BANK_STATEMENT_GUI:    {tcode: FF_5,  description: Import Bank Statement}
  MAINT_ORDER_GUI:       {tcode: IW31,  description: Create Maintenance Order}
  NOTIFICATION_GUI:      {tcode: IW21,  description: Create PM Notification}

tcode_derive:
  - [CREATE_MATERIAL, MM01]
  - [CHANGE_MATERIAL, MM02]
  - [CREATE_PO, ME21N]
  - [GOODS, MIGO]
  - [STOCK, MMBE]
  - [SALES_ORDER, VA01]
  - [DELIVERY, VL01N]
  - [BILLING, VF01]
  - [INSPECTION, QA01]
  - [CREATE_RN, QM01]
  - [PROD_ORDER, CO01]
  - [INTERNAL_ORDER, KO01]
  - [FI_POST, FB01]
  - [GL_MASTER, FS00]
  - [PAYMENT_RUN, F110]
  - [MAINT_ORDER, IW31]
```

**Arquivo 2 — `config/pipeline_stages.yaml`**:
```yaml
pipeline_stages:
  - {id: stage1, name: Spec Analysis,             skill: sap-router-skill,       avg_time: 10s,    wave: 0}
  - {id: stage2, name: Technical Proposal,        skill: sap-crew-analysis,      avg_time: 3min,   wave: 1}
  - {id: stage3, name: Peer Review 1,             skill: abap-code-review,       avg_time: 1min,   wave: 2}
  - {id: stage4, name: Implementation,            skill: cavecrew-builder + ADT, avg_time: varied, wave: 3, fan_out: per-object}
  - {id: stage5, name: Static Analysis (abaplint), tool: npm run abap:review,    avg_time: 30s,    wave: 4}
  - {id: stage6, name: Deep Analysis (Crew),      skill: sap-crew-analysis,      avg_time: 5min,   wave: 4}
  - {id: stage7, name: Peer Review 2,             skill: abap-code-review,       avg_time: 1min,   wave: 5}
  - {id: stage8, name: Transport Gate,            skill: sap-transport-gate,     avg_time: 2min,   wave: 6}
```

**Modificar `sap_router.py`** — adicionar loader no topo, manter mapas hardcoded como fallback:
```python
# === v5.0: CONFIG LOADER (YAML external, hardcoded fallback) ===
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")

def _load_yaml_config(filename, fallback):
    """Load routing map from config/*.yaml. Fallback to hardcoded on any error."""
    path = os.path.join(CONFIG_DIR, filename)
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return fallback

_cfg = _load_yaml_config("routing_maps.yaml", None)
if _cfg:
    ADT_ACTIONS = _cfg.get("adt_actions", ADT_ACTIONS)
    FUNCTIONAL_WRITE_KEYWORDS = _cfg.get("functional_write_keywords", FUNCTIONAL_WRITE_KEYWORDS)
    FUNCTIONAL_READ_KEYWORDS = _cfg.get("functional_read_keywords", FUNCTIONAL_READ_KEYWORDS)
    FUNCTIONAL_BAPI_MAP = _cfg.get("functional_bapi_map", FUNCTIONAL_BAPI_MAP)
    GUI_FALLBACK_MAP = _cfg.get("gui_fallback_map", GUI_FALLBACK_MAP)
```
Inserir APÓS as definições hardcoded existentes (linha ~172), ANTES de `class SapRouter`. Não deletar os mapas hardcoded — são o fallback.

Dependência: `pip install pyyaml` (verificar: `python -c "import yaml"`).

**Aceite**:
1. `python sap-router-skill/scripts/sap_router.py route --action CREATE_MATERIAL --functional` → retorna `BAPI_MATERIAL_SAVEDATA` (comportamento inalterado).
2. `python sap-router-skill/scripts/sap_router.py route --action CREATE_MAINT_ORDER --functional` → retorna `BAPI_ALM_ORDER_MAINTAIN` (novo, prova que YAML carregou; CREATE já é write keyword).
3. `python sap-router-skill/scripts/sap_router.py route --action PAYMENT_RUN --functional` → retorna `F110_BATCH` (prova que a keyword PAYMENT nova do YAML também carregou — este teste FALHA se apenas o BAPI map carregar mas as keywords não).
4. Renomear `config/routing_maps.yaml` temporariamente → router ainda funciona via fallback (PAYMENT_RUN volta a cair no GUI fallback — esperado) → restaurar.

---

# FASE P1 — Inteligência (semana 1, ~4h)

## P1.1 — Agent registry dinâmico no router (1h)

**Contexto**: Gap #1. Router deve descobrir agentes de `.claude/agents/` em runtime.

**Adicionar em `sap_router.py`** (novo método na classe `SapRouter` + novo passo no `get_route`):

```python
def scan_agent_registry(self):
    """v5.0: Discover agents from .claude/agents/*.md YAML frontmatter.
    Returns {name: {description, tools, model, keywords}}."""
    agents = {}
    agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", ".claude", "agents")
    if not os.path.isdir(agents_dir):
        return agents
    import glob as _glob
    for path in _glob.glob(os.path.join(agents_dir, "*.md")):
        try:
            text = open(path, encoding="utf-8").read()
            if not text.startswith("---"):
                continue
            fm_raw = text.split("---")[1]
            import yaml
            fm = yaml.safe_load(fm_raw)
            desc = str(fm.get("description", ""))
            # Trigger keywords = palavras significativas da description
            keywords = [w.strip(".,()").lower() for w in desc.split()
                        if len(w) > 4 and w.lower() not in ("specialist", "trigger")]
            agents[fm["name"]] = {
                "description": desc,
                "tools": fm.get("tools", []),
                "model": fm.get("model", "sonnet"),
                "keywords": keywords,
                "path": path,
            }
        except Exception:
            continue
    return agents

def match_agent(self, task_text):
    """v5.0: Return best-matching agent for a task, or None.
    Scoring: keyword hits in description. Threshold: >= 2 hits."""
    agents = self.scan_agent_registry()
    task_lower = task_text.lower()
    best, best_score = None, 0
    for name, info in agents.items():
        score = sum(1 for kw in info["keywords"] if kw in task_lower)
        if score > best_score:
            best, best_score = name, score
    if best_score >= 2:
        return {"agent": best, "score": best_score,
                "model": agents[best]["model"],
                "strategy": "agent-dispatch"}
    return None
```

**Novo subcomando CLI**:
```python
# em main(), adicionar:
agents_parser = subparsers.add_parser('agents', help='List/match dynamic agent registry')
agents_parser.add_argument('agents_action', choices=['list', 'match'])
agents_parser.add_argument('--task', help='Task text for match')
agents_parser.add_argument('--memory-file', default='MEMORY.md')

# handler:
elif args.command == 'agents':
    if args.agents_action == 'list':
        registry = router.scan_agent_registry()
        print(json.dumps({name: {k: v for k, v in info.items() if k != 'keywords'}
                          for name, info in registry.items()}, indent=2, ensure_ascii=False))
    elif args.agents_action == 'match':
        if not args.task:
            print("error: --task required", file=sys.stderr); sys.exit(1)
        m = router.match_agent(args.task)
        print(json.dumps(m or {"agent": None, "note": "no match >= threshold"}, indent=2))
```

**Integrar no `get_route`** — inserir como Step 3.5 (após functional gate, antes de caveman).

⚠️ **Restrição crítica**: `get_route` normalmente recebe TOKENS de ação (`MM_CREATE_MATERIAL`, `read_source`), não texto livre. Keyword matching contra token nunca atinge threshold ou, pior, dispara falso positivo. Gate obrigatório: só tentar match quando o input é texto livre (contém espaço):

```python
        # Step 3.5 (v5.0): dynamic agent registry match — SÓ para texto livre.
        # Tokens de ação (sem espaço) nunca entram aqui; preserva rotas v4.2.
        if " " in action:
            agent_match = self.match_agent(action_lower)
            if agent_match:
                return {
                    "destination": agent_match["agent"],
                    "strategy": "agent-dispatch",
                    "model": agent_match["model"],
                    "details": f"Dynamic agent registry match (score {agent_match['score']})",
                }
```

Além do `get_route`, chamar `match_agent` também em `crew-dispatch` (task é texto livre por natureza) — se um agente especialista pontuar mais alto que os cavemen genéricos, incluí-lo no plano.

**Aceite**:
1. `python scripts/sap_router.py agents list` → JSON com 3 agentes.
2. `python scripts/sap_router.py agents match --task "conciliação bancária extrato MT940"` → `sap-tr-consultant`.
3. `python scripts/sap_router.py agents match --task "ordem de manutenção equipamento parado"` → `sap-pm-consultant`.
4. Rotas antigas inalteradas: `route --action read_source` ainda → arc-1; `route --action MM_CREATE_MATERIAL --functional` ainda → BAPI (tokens sem espaço NUNCA entram no agent match).
5. Falso-positivo check: `route --action EMPLOYEE_DISPLAY_GUI` → GUI PA20 (não agente).

---

## P1.2 — Conectar self_learn ao router (2h)

**Contexto**: Gap #5/Lacuna #1. `self_learn.py` completo mas fantasma.

### P1.2a — PRÉ-REQUISITO: corrigir round-trip do memory_manager (30 min)

**Bug latente confirmado** (`memory_manager.py:84-118`): `parse()` só reconhece `## BLOCKS`, `## PENDING`, `## ARCHIVE`, `## ENV`, `## ACTIVE`. As seções `## LEARN` (escrita por `self_learn.persist()`) e `## ABAPLINT` **não resetam** `current_section` — suas linhas `- ...` vazam para a seção anterior (tipicamente ARCHIVE). Consequência: qualquer ciclo `add → parse → write` do memory_manager **absorve o LEARN no ARCHIVE e destrói os dados de aprendizado**. Conectar self_learn sem este fix = aprendizado corrompido no primeiro `log-action`.

**Fix em `memory_manager.py`**:
```python
# 1. No __init__: self.learn_lines = []
# 2. No parse(), adicionar ao elif chain (antes do elif '## ENV'):
            elif line_strip.startswith('## LEARN'):
                current_section = 'LEARN'
                continue
            elif line_strip.startswith('## ABAPLINT'):
                current_section = None  # já parseado via regex dedicado
                continue
# 3. No loop de seções, adicionar:
            elif current_section == 'LEARN':
                if line_strip.startswith('- '):
                    self.learn_lines.append(line_strip)
# 4. No write(), re-emitir ANTES do PENDING:
        if self.learn_lines:
            content.append("## LEARN")
            content.extend(self.learn_lines)
            content.append("")
```

**Aceite P1.2a**: criar MEMORY.md de teste com seção `## LEARN` de 3 linhas → `memory_manager.py add ...` → arquivo resultante ainda contém `## LEARN` com as 3 linhas (não migradas para ARCHIVE).

**Limite de 100 linhas**: LEARN cresce sem bound (35 MCPs + N rotas). Regra: `self_learn.persist()` deve emitir no máximo top-10 MCPs (por decay weight) + top-10 rotas + top-5 patterns = ≤25 linhas. Adicionar truncamento no `persist()` do `self_learn.py`.

### P1.2b — Wrapper no router

**Modificar `sap_router.py`**:

```python
# topo do arquivo, após imports:
def _get_learn_engine(memory_file):
    """Lazy-load SelfLearnEngine. Returns None if unavailable (non-fatal)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from self_learn import SelfLearnEngine
        engine = SelfLearnEngine(memory_file)
        engine.load_history()
        return engine
    except Exception:
        return None
```

**No `get_route`** — envolver retorno final com adaptação. Assinatura EXATA (copiar da definição atual em `sap_router.py:181` — não usar ellipsis):
```python
    def get_route(self, action, try_adt=True, allow_gui_fallback=True,
                  functional_context=False, use_zrouter=False):
        route = self._get_route_inner(action, try_adt=try_adt,
                                      allow_gui_fallback=allow_gui_fallback,
                                      functional_context=functional_context,
                                      use_zrouter=use_zrouter)
        learn = _get_learn_engine(self.memory_file)
        if learn:
            route = learn.adapt_route(action, route)  # adiciona confidence + warning
            # Se rota tem candidatos MCP, escolher o melhor por histórico:
            if "mcp_servers" in route and len(route.get("mcp_servers", [])) > 1:
                best = learn.get_best_mcp(route["mcp_servers"])
                if best and best != route.get("mcp_server"):
                    route["mcp_server"] = best
                    route["mcp_reranked"] = True
        return route
```
Refactor: renomear corpo atual de `get_route` para `_get_route_inner` (mesma assinatura) e criar wrapper acima. Mudança cirúrgica — sem tocar na lógica interna.

⚠️ **Path do MEMORY.md**: `self_learn.SelfLearnEngine` default = `<skill>/MEMORY.md`; router default = `MEMORY.md` relativo ao CWD. São arquivos DIFERENTES dependendo de onde o comando roda. Padronizar: router deve resolver `memory_file` para absoluto na `__init__` (`os.path.abspath`) e passar o MESMO path para self_learn e memory_manager. Documentar no SKILL.md: "sempre executar da raiz do sap-router-skill OU passar --memory-file absoluto".

**Novo subcomando de feedback** (a IDE chama após executar a rota):
```python
feedback_parser = subparsers.add_parser('feedback', help='Record route outcome for self-learning')
feedback_parser.add_argument('--action', required=True)
feedback_parser.add_argument('--success', choices=['true', 'false'], required=True)
feedback_parser.add_argument('--mcp', help='MCP that served the route')
feedback_parser.add_argument('--latency', type=int, default=0)
feedback_parser.add_argument('--memory-file', default='MEMORY.md')

elif args.command == 'feedback':
    # GOTCHA: self_learn.persist() retorna silenciosamente se MEMORY.md não
    # existe (early return). Auto-init antes para nunca perder feedback:
    if not os.path.exists(args.memory_file):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run([sys.executable, os.path.join(script_dir, "memory_manager.py"),
                        "init", "--input", args.memory_file,
                        "--sys", "S4H", "--client", "100", "--env", "DEV",
                        "--usr", os.environ.get("USERNAME", "DEVELOPER")],
                       capture_output=True, text=True)
    learn = _get_learn_engine(args.memory_file)
    if not learn:
        print("self_learn unavailable", file=sys.stderr); sys.exit(1)
    learn.record_route_outcome(args.action, args.success == 'true')
    if args.mcp:
        learn.record_mcp_call(args.mcp, args.latency, args.success == 'true')
    learn.persist()
    conf = learn.get_route_confidence(args.action)
    print(json.dumps({"recorded": True, "action": args.action, "confidence": round(conf, 2)}))
```

**Protocolo para a IDE** (documentar no SKILL.md do sap-router-skill):
```
Após CADA execução de rota:
python scripts/sap_router.py feedback --action <ACTION> --success true|false --mcp <MCP> --latency <MS>
```

**Aceite** (rodar da raiz do sap-router-skill):
1. P1.2a primeiro: round-trip LEARN sobrevive a `memory_manager.py add`.
2. `route --action MM_CREATE_MATERIAL --functional` → resposta agora contém campo `confidence`.
3. `feedback --action MM_CREATE_MATERIAL --success false` ×3 → próximo `route` da mesma ação contém `warning` de baixa confiança (adapt_route exige total ≥3; com 3 falhas confidence=0.0 < 0.3 → warning dispara).
4. `MEMORY.md` ganha seção `## LEARN` com `- route:MM_CREATE_MATERIAL ...` E permanece ≤100 linhas.
5. `log-action --action X --module MM --status OK` após feedback → `## LEARN` ainda presente (prova P1.2a).

---

## P1.3 — Conectar healthcheck ao routing (1h)

**Contexto**: Gap/Lacuna #4. Router roteia para MCP morto.

**Modificar `healthcheck.py`** — adicionar cache de resultado:
```python
# em run_full_check(), antes do return:
        cache_path = self.project_root / ".healthcheck_cache.json"
        try:
            cache_path.write_text(json.dumps(self.results, indent=2), encoding="utf-8")
        except OSError:
            pass
```

**Modificar `sap_router.py`** — consultar cache (TTL 15 min):
```python
def _load_health_cache(max_age_s=900):
    """Read last healthcheck result. None if stale/missing."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".healthcheck_cache.json")
    try:
        import time
        if time.time() - os.path.getmtime(path) > max_age_s:
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None

def _mcp_is_healthy(health, mcp_name):
    """True unless healthcheck explicitly marked this MCP as broken."""
    if not health:
        return True  # No data = assume OK (fail-open)
    check = health.get("mcp_checks", {}).get(mcp_name)
    if not check:
        return True
    env_st = check.get("env", {}).get("status", "")
    bin_st = check.get("binary", {}).get("status", "")
    return env_st not in ("NONE_SET",) and bin_st not in ("NOT_INSTALLED", "TIMEOUT")
```

No wrapper `get_route` (após self_learn):
```python
        health = _load_health_cache()
        if health and "mcp_servers" in route:
            healthy = [m for m in route["mcp_servers"] if _mcp_is_healthy(health, m)]
            if healthy and route.get("mcp_server") not in healthy:
                route["mcp_server_original"] = route.get("mcp_server")
                route["mcp_server"] = healthy[0]
                route["health_rerouted"] = True
            route["mcp_servers_healthy"] = healthy
```

⚠️ **Gotcha do env check**: `healthcheck.check_mcp_env_vars()` consulta `os.environ`, mas as credenciais vivem no arquivo `.env` (não exportadas ao processo). Resultado: quase todo MCP reporta `NONE_SET` → lista `healthy` fica vazia → nenhum reroute acontece (fail-open salva, mas o recurso vira no-op). **Fix obrigatório junto**: em `check_mcp_env_vars`, além de `os.environ`, consultar o conteúdo do `.env` (mesmo regex já usado em `check_env_file`). Sem esse fix, P1.3 não agrega valor.

**Aceite**:
1. `python scripts/healthcheck.py --quiet` → gera `.healthcheck_cache.json`.
2. Com `.env` contendo `ARC_SAP_URL=...` etc. (sem export): cache marca `arc-1` env como `ALL_SET` (prova do fix do gotcha).
3. `route --action read_source` → resposta contém `mcp_servers_healthy` não-vazio.
4. Cache ausente ou stale (>15 min) → routing funciona normal (fail-open).

---

## P1.4 — Enriquecer agentes com web search + docs (30 min)

**Contexto**: Q1 da análise. MCP hermes-crewai expõe `sap_web_search`, `sap_docs_search`, `sap_abap_docs_search`, `sap_knowledge_base_search`, `sap_tcodes`.

**Ação**: atualizar `tools:` dos 3 agentes criados em P0.2:

```yaml
# sap-tr-consultant.md e sap-pm-consultant.md:
tools: [Read, Grep, Glob,
        mcp__hermes-crewai__sap_web_search,
        mcp__hermes-crewai__sap_docs_search,
        mcp__hermes-crewai__sap_tcodes,
        mcp__hermes-crewai__sap_knowledge_base_search]

# sap-code-reviewer.md:
tools: [Read, Grep, Glob, Bash,
        mcp__hermes-crewai__abap_lint,
        mcp__hermes-crewai__sap_abap_docs_search]
```

**Adicionar seção no corpo de cada agente**:
```markdown
## Enriquecimento externo
Quando conhecimento local insuficiente:
1. `sap_docs_search` — SAP Help Portal (autoritativo, primeiro).
2. `sap_web_search` — tutoriais SAP Community/blogs (segundo).
3. `sap_tcodes` — validar T-code antes de citar.
Nunca inventar T-code/BAPI/tabela — validar antes de responder.
```

**Aceite**: frontmatter re-parseia OK; tools referenciam MCPs existentes (validar contra `hermes_mcp_list`).

---

# FASE P2 — Dados e Execução (semana 2, ~6h)

## P2.1 — Importar índices sapstack (2h)

**Fontes**: repositório sapstack — `symptom-index.yaml` (106KB), `tcodes.yaml` (46KB), `sap-notes.yaml` (42KB).

**Destino**: `sap-router-skill/references/data/`

**Passo 1 — obter arquivos**:
```powershell
# Opção A: clone raso
git clone --depth 1 https://github.com/BoxLogoDev/sapstack "$env:TEMP\sapstack"
New-Item -ItemType Directory -Force "sap-router-skill\references\data"
Copy-Item "$env:TEMP\sapstack\**\symptom-index.yaml" "sap-router-skill\references\data\" 
Copy-Item "$env:TEMP\sapstack\**\tcodes.yaml" "sap-router-skill\references\data\"
Copy-Item "$env:TEMP\sapstack\**\sap-notes.yaml" "sap-router-skill\references\data\"
```
**Fallback se repo inacessível**: gerar `tcodes.yaml` mínimo dos module_maps locais (extrair todas as linhas "Transações" dos 12 maps → ~120 T-codes com módulo). `symptom-index.yaml` fica pendente e P2.1 é parcial — registrar em PENDING do MEMORY.md.

**Passo 2 — VERIFICAR estrutura antes de codar o loader**: o schema real do `tcodes.yaml` do sapstack é desconhecido até o download (pode ser `{tcode: {module,...}}`, lista de objetos, ou agrupado por módulo). Obrigatório: `head -50 tcodes.yaml` primeiro, depois adaptar o loader para normalizar ao formato canônico `{tcode: {module, description}}`:
```python
def _load_tcode_index():
    """Load tcodes.yaml normalized to {TCODE: {module, description}}.
    Empty dict if missing. ADAPT the normalizer to the real sapstack schema."""
    path = os.path.join(CONFIG_DIR, "..", "references", "data", "tcodes.yaml")
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        # Normalizador — ajustar após inspecionar o arquivo real:
        if isinstance(raw, dict) and raw and isinstance(next(iter(raw.values())), dict):
            return {k.upper(): v for k, v in raw.items()}       # já canônico
        if isinstance(raw, list):                                # lista de objetos
            return {e["tcode"].upper(): e for e in raw if "tcode" in e}
        return {}
    except Exception:
        return {}
```

**Passo 3 — usar no `_identify_modules`** (upgrade, não substituição):
```python
    def _identify_modules(self, text):
        detected = []  # lógica keyword atual permanece
        # ... código existente ...
        # v5.0: T-code index lookup (mais preciso que keywords)
        tcode_index = _load_tcode_index()
        if tcode_index:
            for match in re.finditer(r'\b([A-Z]{2}\d{2}[A-Z]?|[A-Z]{4,5}\d?)\b', text.upper()):
                tc = match.group(1)
                if tc in tcode_index:
                    mod = tcode_index[tc].get("module")
                    if mod and mod not in detected:
                        detected.insert(0, mod)  # T-code match = prioridade
        return detected
```

**Aceite**:
1. `analyze-spec --spec-text "usuário reclama erro na IW31"` → módulo PM detectado (hoje falha — PM nem existe no keyword map).
2. Specs antigas: `analyze-spec --spec-text "create material FERT"` → MM (regressão zero).

---

## P2.2 — Agentes Fase 3: 9 módulos faltantes (3h)

**Criar em `.claude/agents/`** (mesmo template P0.2, um por vez):

| Arquivo | Fonte | Triggers principais |
|---|---|---|
| `sap-ewm-consultant.md` | sapstack | EWM, putaway, wave picking, /SCWM/*, warehouse task |
| `sap-tm-consultant.md` | sc4sap | Transportation Management, freight order, carrier |
| `sap-bw-consultant.md` | sc4sap | BW, DSO, InfoCube, DTP, transformation, query |
| `sap-ariba-consultant.md` | sapstack | Ariba, sourcing, procurement cloud, SLP |
| `sap-ibp-consultant.md` | sapstack | IBP, demand planning, supply review, S&OP |
| `sap-sac-consultant.md` | sapstack | SAC, Analytics Cloud, story, planning model |
| `sap-s4-migration-advisor.md` | sapstack | ECC to S/4, migration, conversion, readiness check |
| `sap-cloud-consultant.md` | sapstack | BTP, RISE, Cloud PE, subaccount |
| `sap-integration-advisor.md` | sapstack | CPI, RFC, OData, IDoc, interface decision |

Regras de adaptação (do integracao_subagentes_sap.md):
1. `description:` → PT-BR + EN com trigger keywords.
2. `tools:` → remover MCPs proprietários sc4sap; usar `[Read, Grep, Glob]` + hermes tools de P1.4.
3. Paths internos → apontar para `references/module_maps/` e `references/trench_knowledge/` locais.
4. Corpo (conhecimento SAP) → traduzir/manter conteúdo técnico.

**Fallback sem repos**: corpo mínimo de 60-100 linhas por agente usando conhecimento do modelo: escopo, T-codes, tabelas, BAPIs, regras de resposta.

**Module maps correspondentes** (senão os agentes referenciam paths inexistentes): criar junto `ewm_operations.md`, `tm_operations.md`, `bw_operations.md` em `references/module_maps/` (formato P0.3; Ariba/IBP/SAC/Cloud são cloud-first — sem module map, o corpo do agente é a fonte). Agentes que não têm map: remover a referência a `references/module_maps/` do corpo.

**Aceite**: `agents list` → 12 agentes; `agents match --task "criar freight order"` → `sap-tm-consultant`; 15 module maps (12 + EWM/TM/BW); nenhum agente cita path inexistente (verificar: `grep -o 'references/[a-z_/]*\.md' .claude/agents/*.md` → todos os paths existem).

---

## P2.3 — Fallback engine: execução real tier 1-3 (2h)

**Contexto**: Lacuna #2. Tiers simulados.

**Estratégia**: fallback_engine devolve **instrução MCP executável** em formato padronizado que a IDE consome. Não chamar MCP de dentro do Python (Python não tem acesso às tools MCP da sessão) — devolver contrato claro:

```python
# _attempt_adt v5.0 — retornar contrato executável:
def _attempt_adt(self, action, payload, module):
    adt_actions = ["read_source", "search_object", "syntax_check",
                   "where_used", "get_deps", "code_search"]
    matched = next((a for a in adt_actions if a in action.lower()), None)
    if matched:
        return {
            "success": True,
            "data": {
                "method": "ADT direct",
                "executable": True,
                # CONTRATO v5: a IDE executa este tool call
                "tool_call": {
                    "tool": "mcp__hermes-crewai__sap_adt_cli",
                    "args": {"operation": matched, "payload": payload or {}},
                },
                "verify": "response.status == 200",
            }
        }
    return {"success": False, "error": f"'{action}' not an ADT operation"}
```

Analogamente `_attempt_rfc` → `tool_call: {"tool": "mcp__hermes-crewai__sap_bapi_call", args: {...}}`; `_attempt_gui_transaction` → tool_call para mcp-sap-gui com tcode.

**Documentar contrato no SKILL.md**:
```
Fallback tier retorna data.tool_call quando executable=true.
IDE DEVE: executar tool_call → reportar resultado via
python scripts/sap_router.py feedback --action X --success true|false
```

**Aceite**: `python scripts/fallback_engine.py execute --action read_source_ZCL_TEST --json` → JSON contém `tool_call` com tool name válido.

---

# FASE P3 — Plataforma (semanas 3-4, ~12h)

## P3.1 — Multi-model routing (2h)

**Criar `config/model_routing.yaml`**:
```yaml
# Complexity → model tier
model_tiers:
  SIMPLE:       haiku      # T-code lookup, table read, display
  MODERATE:     sonnet     # BAPI single-call, config check, report
  COMPLEX:      sonnet     # enhancement, BADI, interface
  VERY_COMPLEX: opus       # multi-module, migration, architecture
```

**No router** — `analyze_spec` já retorna `complexity`; adicionar ao route:
```python
def decide_model(self, complexity):
    cfg = _load_yaml_config("model_routing.yaml", None) or {}
    tiers = cfg.get("model_tiers", {})
    return tiers.get(complexity, "sonnet")
```
Adicionar `"model": self.decide_model(...)` no dict de retorno das rotas que despacham agentes.

⚠️ **Nota de ambiente**: `.claude/settings.local.json` mapeia apenas haiku→deepseek-v4-flash e sonnet→deepseek-v4-pro. Tier `opus` não tem override — cairia no Opus real da Anthropic (custo alto/inesperado). Decisão: ou mapear `ANTHROPIC_DEFAULT_OPUS_MODEL` no settings, ou usar `sonnet` como tier máximo em `model_routing.yaml` neste ambiente.

**Aceite**: spec simples → `model: haiku`; spec multi-módulo → tier máximo configurado; nenhum tier aponta para modelo sem override no ambiente ativo.

## P3.2 — Pipeline via CrewAI MCP (4h)

`crew-dispatch` e `pipeline` ganham flag `--use-crewai`: em vez de emitir JSON estático, gerar payload para `mcp__hermes-crewai__crewai_orchestrate` com stages waves. Contrato igual P2.3: router devolve `tool_call`, IDE executa.

**Aceite**: `pipeline --spec-text "..." --use-crewai` → JSON com `tool_call.tool == "mcp__hermes-crewai__crewai_orchestrate"`.

## P3.3 — RAG pipeline: ingestão de arquivos base (6h)

**Criar `scripts/rag_ingest.py`**:
```
Subcomandos:
  ingest  --input <file.pdf|.md|.docx|.xlsx> --collection sap-knowledge
          → chunk (800 tokens, overlap 100) → embed → upsert
  query   --text "sintoma/pergunta" --top-k 5
          → retorna chunks relevantes p/ injetar no contexto
  status  → contagem de docs/chunks por collection

Backends (por env var, primeiro disponível):
  SUPABASE_URL + SUPABASE_SERVICE_KEY  → pgvector (recomendado: free tier)
  PINECONE_API_KEY                     → Pinecone
  AZURE_SEARCH_ENDPOINT                → Azure AI Search
  Nenhum                               → SQLite local + embeddings via API
```

**Integração router**: novo passo no `get_route` — se `rag_ingest.py query` retorna hit com score > 0.8, adicionar `route["rag_context"] = [...chunks...]`.

**Uso**: usuário faz upload de spec funcional/manual PDF → `ingest` → routing e agentes consultam automaticamente.

**Aceite**: `ingest --input ZROUTER_TECHNICAL_SPEC.md` → OK; `query --text "dispatch batch atômico"` → retorna chunk relevante do spec.

## P3.4 — 22 comandos operacionais (3h)

Adaptar commands sapstack → `.claude/skills/sap-ops-commands/` (1 skill guarda todos) ou individual `.claude/commands/*.md`. Prioridade: `sap-fi-closing`, `sap-migo-debug`, `sap-payment-run-debug`, `sap-transport-debug`.

---

# Ordem de Execução e Gates

```
P0.1 dedup ──┐
P0.2 agents ─┼─→ GATE 1: agents list OK + rotas antigas inalteradas
P0.3 maps ───┤
P0.4 yaml ───┘
     ↓
P1.1 registry ─┐
P1.2 selflearn ┼─→ GATE 2: route contém confidence + health + agent match
P1.3 health ───┤
P1.4 tools ────┘
     ↓
P2.1 índices ──┐
P2.2 9 agents ─┼─→ GATE 3: 12 agentes; T-code detection; fallback executável
P2.3 fallback ─┘
     ↓
P3.* plataforma → GATE 4: multi-model + CrewAI + RAG smoke tests
```

## Suite de regressão (rodar em CADA gate)

```bash
cd sap-router-skill

# 1. Routing básico inalterado
python scripts/sap_router.py route --action read_source          # → arc-1
python scripts/sap_router.py route --action CREATE_MATERIAL      # → needs-functional-context
python scripts/sap_router.py route --action CREATE_MATERIAL --functional  # → BAPI_MATERIAL_SAVEDATA
python scripts/sap_router.py route --action SPRO_CONFIG          # → GUI SPRO

# 2. Memory manager
python scripts/memory_manager.py verify --input scripts/MEMORY.md

# 3. Healthcheck não quebra
python scripts/healthcheck.py --quiet --json > /dev/null; echo $?  # 0, 1 ou 2 — nunca traceback

# 4. Novos (a partir do Gate 2)
python scripts/sap_router.py agents list
python scripts/sap_router.py agents match --task "extrato bancario MT940"
python scripts/sap_router.py feedback --action TEST_ACTION --success true
```

## Regras invioláveis (de sap_router.py v4.2 — preservar)

1. **ZROUTER é opt-in**: nunca auto-instalar/auto-probar. Decline persiste.
2. **BAPI gate**: write BAPIs só com `--functional`. Bare token → `needs-functional-context`.
3. **ADT-first**: dev/read ops sempre tentam ADT antes de GUI.
4. **Fail-open**: qualquer componente novo (YAML, self_learn, healthcheck, RAG) indisponível → routing continua com comportamento v4.2.
5. **MEMORY.md ≤ 100 linhas**: compactação automática preservada.
6. **Credenciais**: nunca commitar `.env`; `settings.local.json` contém token — NÃO versionar (adicionar a `.gitignore` se repo git for criado).

---

## Resumo de Entregas

| Fase | Entregas | Arquivos novos | Arquivos modificados |
|---|---|---|---|
| P0 | dedup, 3 agentes, 2 maps, config YAML | 7 | 1 (`sap_router.py`) |
| P1 | registry, self-learn (+fix round-trip LEARN), health (+fix env check), tools | 0 | 7 (`sap_router.py`, `memory_manager.py`, `self_learn.py`, `healthcheck.py`, 3 agentes) |
| P2 | índices, 9 agentes, fallback real | 12+ | 2 (`sap_router.py`, `fallback_engine.py`) |
| P3 | multi-model, CrewAI, RAG, commands | 25+ | 2 |

**Versão alvo final**: sap_router.py `__version__ = "5.0.0"` (bump ao concluir Gate 2).
