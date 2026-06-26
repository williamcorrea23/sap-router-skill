---
name: sap-crew-analysis
description: >-
  Background ABAP code analysis and debugging via local CrewAI multi-agent
  pipeline. 7 specialized SAP agents analyze code for errors, security issues,
  performance problems, and Clean ABAP compliance. Use when asked to analyze
  ABAP code, debug ABAP programs, find errors in ABAP, review SAP code quality,
  audit ABAP security, optimize ABAP performance, or get improvement suggestions
  for ABAP/CDS/RAP code. Triggers on: "analyze this ABAP", "debug Z* code",
  "find errors in program", "review ZCL_* class", "check code quality",
  "audit ABAP security", "optimize ABAP", "improve SAP code".
---

# SAP Crew Analysis — Background ABAP Debug & Review

Invokes the local **sap-crew-agent** (7 agents, 13 tools, 4-phase pipeline)
in background to deeply analyze ABAP code, find errors, and suggest improvements.

## Architecture

```
You (VS Code chat):
  "analyze ZCL_MATERIAL_HANDLER for errors and improvements"
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              sap-crew-analysis (this skill)           │
│                                                       │
│  1. sap_router.py route → ZROUTER RFC? ARC-1 ADT?   │
│  2. Read ABAP source via ADT MCP (arc-1/aibap)       │
│  3. Pass source to sap-crew-agent in BACKGROUND       │
│     ┌──────────────────────────────────────┐          │
│     │  sap-crew-agent (local CrewAI)       │          │
│     │                                       │          │
│     │  Phase 1: Analysis                    │          │
│     │    ├─ Architect agent: design review  │          │
│     │    ├─ ABAP agent: code patterns      │          │
│     │    └─ Security agent: vulnerability  │          │
│     │                                       │          │
│     │  Phase 2: Design                      │          │
│     │    └─ Architect: improvement plan    │          │
│     │                                       │          │
│     │  Phase 3: Code Generation             │          │
│     │    └─ ABAP agent: corrected code     │          │
│     │                                       │          │
│     │  Phase 4: Review                      │          │
│     │    ├─ Security agent: verify fixes   │          │
│     │    └─ QA agent: final sign-off       │          │
│     └──────────────────────────────────────┘          │
│  4. Synthesize findings → structured report           │
└──────────────────────────────────────────────────────┘
       │
       ▼
  Report returned:
    ├─ Errors found (CRITICAL/HIGH/MEDIUM/LOW)
    ├─ Fix suggestions with code snippets
    ├─ Performance improvements
    ├─ Security audit results
    └─ Clean ABAP compliance score
```

## Quick Start — Analyze ABAP Code

### From VS Code / Claude Code

```
You: "analyze ZCL_ROUTER_HANDLER_MM for bugs, security issues, and Clean ABAP compliance"

Skill auto-triggers: sap-crew-analysis
MCP called: arc-1/aibap → SAPRead(source) → gets ABAP source
Background: sap-crew-agent runs full 4-phase pipeline
Result: structured report with errors, fixes, and compliance score
```

### CLI (Direct)

```bash
# Full ABAP analysis pipeline (background)
python sap_crew/run.py "Analisar código ABAP do programa ZMM_REPORT em busca de erros, problemas de segurança e violações Clean ABAP. Código: $(cat templates/ZROUTER_DISPATCH.abap | head -200)"

# Quick analysis (faster, 2 phases)
python sap_crew/run.py --mode quick "Revisar segurança da classe ZCL_MATERIAL_HANDLER: $(aibap get_class ZCL_MATERIAL_HANDLER)"

# Troubleshooting (specific problem)
python sap_crew/run.py --mode troubleshoot "CDS view ZI_PRODUCT com erro de sintaxe no join com MARA"
```

### Via MCP Bridge (Background)

```bash
# Start MCP bridge (run once, stays alive)
python sap_crew_mcp_bridge.py &

# Then from any MCP client
# Call: sap_crew_delegate(task="Analisar ZCL_MATERIAL_HANDLER...", mode="full")
```

## Analysis Modes

| Mode | Phases | Time (estimated) | Best For |
|---|---|---|---|
| `full` | Analysis → Design → Code → Review | 3-5 min | Full security + quality audit |
| `quick` | Analysis → Code+Review | 1-2 min | Bug fixes, small improvements |
| `troubleshoot` | Diagnosis only | 30s-1min | Syntax errors, specific errors |
| `domain abap` | Full pipeline, ABAP-only agents | 2-3 min | ABAP-specific deep analysis |
| `domain security` | Full pipeline, security agent only | 2-3 min | Security-focused audit |

## The 7 Agents

| Agent | Role | What It Checks |
|---|---|---|
| **SAP Architect** | Solution design review | Architecture patterns, design flaws, extensibility |
| **ABAP Developer** | Code quality + generation | Clean ABAP, BAPI patterns, inline declarations, modern syntax |
| **HANA Specialist** | Database performance | SELECT optimization, CDS performance, DB access patterns |
| **CPI Expert** | Integration flows | iFlow design, Groovy scripts, message mappings |
| **CAP Developer** | CAP service analysis | CDS models, handlers, XSUAA auth, OData config |
| **UI5/Fiori Dev** | Frontend review | UI5 patterns, Fiori guidelines, TypeScript compliance |
| **Security Architect** | Security audit | SQL injection, auth checks, XSUAA, IAM, data privacy |

## Analysis Dimensions (9)

Each analysis run covers:

| # | Dimension | Agents | Checks |
|---|---|---|---|
| 1 | **SEC** — Security | Security + ABAP | SQL injection, dynamic code, OS calls, credential exposure |
| 2 | **AUTH** — Authorization | Security | AUTHORITY-CHECK, S_DEVELOP, DCL roles, IAM gaps |
| 3 | **DATA** — Data Integrity | ABAP + HANA | Error handling, ENQUEUE, COMMIT patterns, transaction safety |
| 4 | **PERF** — Performance | HANA + ABAP | SELECT in loop, SELECT *, missing indexes, full table scans |
| 5 | **STD** — Standards | ABAP + Architect | Deprecated stmts, hardcoding, Clean ABAP violations, naming |
| 6 | **INTERFACE** — Interfaces | CPI + Architect | RFC params, OData auth, timeout config, IDoc structure |
| 7 | **CHANGE** — Change Impact | Architect | Affected objects, SAP standard mods, shared INCLUDEs |
| 8 | **COMP** — Compliance | Security + Architect | PII, dual-control, CDHDR/CDPOS logging, SoD |
| 9 | **FUNC** — Functional | ABAP + Architect | Requirements coverage, logic errors, edge cases |

## Integration with ZROUTER Pipeline

The sap-crew-analysis skill integrates into the full ZROUTER review flow:

```
1. npm run abap:lint         ← Static lint check (abaplint)
2. sap-crew-analysis         ← AI-powered deep analysis (7 agents)
3. npm run abap:review       ← Combined lint + security gate
4. abap-code-review skill    ← Structured 9-dimension report
5. sap-transport-gate skill  ← Transport release gate (GO/NO-GO)
```

### How ZROUTER calls sap-crew in background

```python
# ZROUTER_BASIS handler — CODE_ANALYSIS action enhanced
METHOD code_analysis.
  " 1. Get ABAP source via ADT
  DATA(lv_source) = get_source_from_adt( iv_program = iv_payload ).

  " 2. Call sap-crew-agent in background via MCP bridge
  DATA(lo_mcp) = NEW zcl_sap_crew_mcp_client( ).
  DATA(ls_analysis) = lo_mcp->delegate(
    iv_task     = |Analisar código ABAP em busca de erros e melhorias: { lv_source }|
    iv_mode     = 'full'
    iv_timeout  = 600  " 10 min timeout for full pipeline
  ).

  " 3. Parse findings → structured report
  DATA(ls_report) = parse_crew_analysis( ls_analysis ).

  " 4. Store via BAL log
  mo_logger->log_action(
    iv_module  = 'BASIS'
    iv_action  = 'CODE_ANALYSIS'
    iv_status  = ls_report-status
    iv_message = ls_report-summary ).
ENDMETHOD.
```

## Example: Full ABAP Debug Session

### Input
```
You: "debug ZCL_ROUTER_HANDLER_MM. It's returning error 'Material creation failed'
      for material type FERT. Check the BAPI call, error handling, and suggest fixes."

Skill: sap-crew-analysis
Mode: troubleshoot (fast diagnostic)

MCP step 1: arc-1 → SAPRead(uri="/sap/bc/adt/oo/classes/zcl_zrouter_handler_mm/source/main")
MCP step 2: arc-1 → sap_crew_delegate(task="Diagnosticar erro...", mode="troubleshoot")
```

### Output (from 7-agent analysis)
```
## SAP Crew Analysis Report — ZCL_ROUTER_HANDLER_MM

### Errors Found (2 CRITICAL, 1 HIGH, 3 MEDIUM)

**CRITICAL-1: BAPI_MATERIAL_SAVEDATA missing mandatory field**
  Line: 421, Method: create_material
  Issue: HEADDATA-MATERIAL_TYPE not set. BAPI_MATERIAL_SAVEDATA requires
         MATERIAL_TYPE field populated in BAPIMATHEAD structure.
  Fix: Add `ls_header-material_type = 'FERT'` before BAPI call.
  Impact: BAPI returns E-type error without clear message.

**CRITICAL-2: Missing BAPIRET2 table check**
  Line: 426, Method: create_material
  Issue: Only checks IMPORTING RETURN. BAPI_MATERIAL_SAVEDATA also returns
         messages in TABLES RETURN parameter that are missed.
  Fix:
  ```abap
  CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
    EXPORTING headdata = ls_header
    IMPORTING return   = ls_ret
    TABLES  returnmessages = lt_ret.
  READ TABLE lt_ret INTO DATA(ls_msg) WITH KEY type = 'E'.
  IF sy-subrc = 0 OR ls_ret-type = 'E'.
    " Handle error
  ENDIF.
  ```

**HIGH-1: No ENQUEUE before BAPI**
  Line: 420, Method: create_material
  Issue: BAPI called without prior ENQUEUE. Concurrent users may create
         duplicate materials or encounter lock errors.
  Fix: Wrap in ENQUEUE_READ/ENQUEUE_WRITE block.

**MEDIUM-1: Hardcoded plant not validated**
**MEDIUM-2: Missing COMMIT confirmation check**
**MEDIUM-3: No BAL logging for audit trail**

### Clean ABAP Compliance: 72/100
- ✅ Inline declarations used (3/3)
- ✅ BAPI_TRANSACTION_COMMIT with WAIT (1/1)
- ❌ Long method: create_material is 67 lines (max 50)
- ❌ Missing method documentation (%_check)
- ⚠️  SELECT * in get_material line 442
```

## Performance & Resource Notes

- **sap-crew-agent runs locally** — no data leaves your machine
- **LLM API key required**: set `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, or `OPENROUTER_API_KEY` in `.env`
- **Timeout**: full pipeline up to 10 min; quick up to 2 min
- **Parallel analysis**: ZROUTER dispatches to background thread, doesn't block
- **Caching**: same ABAP source + same request → crew can reuse previous analysis

## Installation

```bash
# Clone sap-crew-agent (if not already present)
git clone https://github.com/<user>/sap-crew-agent.git C:/Users/%USERNAME%/Documents/GitHub/sap-crew-agent

# Install dependencies
cd sap-crew-agent/sap-crew-agent
pip install -r requirements.txt

# Configure LLM API key
cp .env.example .env
# Edit .env → set OPENAI_API_KEY or DEEPSEEK_API_KEY

# Verify
python sap_crew/run.py --mode quick "Syntactic check: is ABAP keyword CLASS valid?"
```

## MCP Configuration

Add to `.mcp.json`:

```json
{
  "sap-crew-local": {
    "type": "stdio",
    "command": "python",
    "args": [
      "C:\\Users\\William Correa\\Documents\\GitHub\\sap-crew-agent\\sap-crew-agent\\sap_crew_mcp_bridge.py"
    ],
    "description": "Local SAP CrewAI — 7 agents, 13 tools, 4-phase pipeline for ABAP analysis, code review, debugging, and code generation. Runs entirely on local machine — no cloud dependency."
  }
}
```

## Gotchas

- **First run slow**: CrewAI initializes 7 LLM agents — ~30s startup
- **API costs**: quick mode ~1K tokens; full mode ~8K tokens (depends on LLM model)
- **sap-crew-agent must be in PATH** or referenced by absolute path
- **.env file**: LLM API key must be set in sap-crew-agent/.env, not in ambient environment
- **Not a replacement for abaplint**: Crew analysis is AI-powered (finds logic bugs). abaplint is deterministic (finds syntax/pattern violations). Use both.
- **Analysis is advisory**: AI agents can hallucinate ABAP syntax. Always review suggestions before applying.
- **Background execution**: `sap_crew_mcp_bridge.py` runs as long-lived MCP server. One instance serves all analysis requests.
