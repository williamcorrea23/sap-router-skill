---
name: sap-crew-analysis
description: >-
  Multi-agent ABAP code analysis via local CrewAI pipeline. 7 specialized agents
  find errors, security flaws, performance bottlenecks, and Clean ABAP violations.
trigger:
  keywords:
    - "analyze this ABAP"
    - "debug Z* code"
    - "find errors in program"
    - "review ZCL_* class"
    - "check code quality"
    - "audit ABAP security"
    - "optimize ABAP"
    - "improve SAP code"
    - "SAP crew analysis"
  intent: >-
    Run multi-agent ABAP code analysis to find errors, security flaws, performance bottlenecks, and Clean ABAP violations.
  patterns:
    - "Z[A-Z]{3,}.*error"
    - "ZCL_.*review"
    - "ABAP.*(debug|analyze|audit)"
---

# SAP Crew Analysis — 7-Agent ABAP Debug & Review

You give it ABAP source. It returns a structured report: errors found (severity-tagged),
fix suggestions with code snippets, performance hotspots, security audit results, and a
Clean ABAP compliance score. 7 agents, 13 tools, 4 phases. Runs locally — no data leaves your machine.

## Prerequisites

```bash
# 1. Clone the crew agent repo
git clone https://github.com/your-org/sap-crew-agent.git ~/sap-crew-agent

# 2. Install Python dependencies
cd ~/sap-crew-agent/sap-crew-agent && pip install -r requirements.txt

# 3. Set LLM API key (any one works)
cp .env.example .env
# Edit .env → OPENAI_API_KEY=sk-... or DEEPSEEK_API_KEY=... or OPENROUTER_API_KEY=sk-or-...

# 4. Verify installation
python sap_crew/run.py --mode quick "Syntax check: is ABAP keyword CLASS valid?"
```

**Requires:** Python 3.10+, valid LLM API key, ADT MCP (arc-1/aibap) for source retrieval.

## Quick Start

### Analyze ABAP code (CLI)

```bash
# Full pipeline — security + quality + performance (3-5 min)
python sap_crew/run.py "Analyze ZCL_MATERIAL_HANDLER for bugs, security, and Clean ABAP compliance. Code: $(cat templates/ZROUTER_DISPATCH.abap | head -200)"

# Quick mode — fast bug hunt (1-2 min)
python sap_crew/run.py --mode quick "Review security of ZCL_MATERIAL_HANDLER: $(aibap get_class ZCL_MATERIAL_HANDLER)"

# Troubleshoot — diagnose a specific error (30s-1min)
python sap_crew/run.py --mode troubleshoot "CDS view ZI_PRODUCT has syntax error in join with MARA"
```

### Via MCP Bridge (background, long-lived)

```bash
# Start MCP bridge once — stays alive, serves all requests
python sap_crew_mcp_bridge.py &

# Then call from any MCP client:
# sap_crew_delegate(task="Analyze ZCL_MATERIAL_HANDLER...", mode="full")
```

## Analysis Modes

- **full** — Analysis → Design → Code → Review. 3-5 min. Use for complete security + quality audit.
- **quick** — Analysis → Code+Review. 1-2 min. Use for bug fixes and small improvements.
- **troubleshoot** — Diagnosis only. 30s-1min. Use for syntax errors and specific bugs.
- **domain security** — Security agent only. 2-3 min. Focused security audit.
- **domain abap** — ABAP-only agents. 2-3 min. ABAP-specific deep analysis.

## The 7 Agents

- **SAP Architect** — Design review: architecture patterns, extensibility, design flaws.
- **ABAP Developer** — Code quality: Clean ABAP, BAPI patterns, modern syntax, inline declarations.
- **HANA Specialist** — DB performance: SELECT optimization, CDS perf, DB access patterns.
- **CPI Expert** — Integration flows: iFlow design, Groovy scripts, message mappings.
- **CAP Developer** — CAP services: CDS models, handlers, XSUAA auth, OData config.
- **UI5/Fiori Dev** — Frontend: UI5 patterns, Fiori guidelines, TypeScript compliance.
- **Security Architect** — Security audit: SQL injection, AUTHORITY-CHECK gaps, data privacy, SoD.

## 9 Analysis Dimensions

1. **SEC** (Security + ABAP) — SQL injection, dynamic code, OS calls, credential exposure.
2. **AUTH** (Security) — AUTHORITY-CHECK, S_DEVELOP, DCL roles, IAM gaps.
3. **DATA** (ABAP + HANA) — Error handling, ENQUEUE, COMMIT patterns, transaction safety.
4. **PERF** (HANA + ABAP) — SELECT in loop, SELECT *, missing indexes, full table scans.
5. **STD** (ABAP + Architect) — Deprecated statements, hardcoding, Clean ABAP violations.
6. **INTERFACE** (CPI + Architect) — RFC params, OData auth, timeout config, IDoc structure.
7. **CHANGE** (Architect) — Affected objects, SAP standard mods, shared INCLUDEs.
8. **COMP** (Security + Architect) — PII, dual-control, CDHDR/CDPOS logging, SoD.
9. **FUNC** (ABAP + Architect) — Requirements coverage, logic errors, edge cases.

## ZROUTER Pipeline Integration

```
1. npm run abap:lint          ← abaplint static checks
2. sap-crew-analysis          ← 7-agent AI deep analysis (this skill)
3. npm run abap:review        ← combined lint + security gate
4. abap-code-review skill     ← structured 9-dimension report
5. sap-transport-gate skill   ← GO/NO-GO transport release gate
```

## Example Output

```
## SAP Crew Analysis Report — ZCL_ROUTER_HANDLER_MM

### Errors Found (2 CRITICAL, 1 HIGH, 3 MEDIUM)

CRITICAL-1: BAPI_MATERIAL_SAVEDATA missing mandatory field
  Line: 421 | HEADDATA-MATERIAL_TYPE not set → BAPI returns E-type error
  Fix: ls_header-material_type = 'FERT'  " before BAPI call

CRITICAL-2: Missing BAPIRET2 table check
  Line: 426 | Only checks IMPORTING RETURN, misses TABLES RETURNMESSAGES
  Fix: READ TABLE lt_ret WITH KEY type = 'E'. IF sy-subrc = 0 OR ls_ret-type = 'E'.

HIGH-1: No ENQUEUE before BAPI
  Line: 420 | Concurrent users may hit lock errors
  Fix: Wrap in ENQUEUE_READ/ENQUEUE_WRITE block.

### Clean ABAP Compliance: 72/100
  ✅ Inline declarations (3/3)
  ✅ BAPI_TRANSACTION_COMMIT with WAIT (1/1)
  ❌ Long method: create_material is 67 lines (max 50)
  ❌ Missing method documentation
  ⚠️  SELECT * in get_material line 442
```

## MCP Configuration

Add to `.mcp.json`:

```json
{
  "sap-crew-local": {
    "type": "stdio",
    "command": "python",
    "args": ["/path/to/sap-crew-agent/sap_crew_mcp_bridge.py"],
    "description": "Local CrewAI — 7 agents, 13 tools, 4-phase pipeline. No cloud dependency."
  }
}
```

## Pitfalls

- **First run is slow** — CrewAI initializes 7 LLM agents (~30s startup). Not an error.
- **API costs scale with mode** — quick ≈ 1K tokens; full ≈ 8K tokens. Choose `troubleshoot` for single-issue diagnosis.
- **.env location matters** — LLM key must be in `sap-crew-agent/.env`, not ambient shell env.
- **Not a replacement for abaplint** — Crew finds logic bugs (AI); abaplint finds syntax/pattern violations (deterministic). Use both.
- **AI can hallucinate ABAP syntax** — Always review suggestions before applying. The report is advisory, not authoritative.
- **MCP bridge is long-lived** — One instance serves all requests. Don't start multiple instances.
- **Large source files** — Truncate to ~200 lines for `run.py` CLI; full source via MCP bridge only.

## Verification

```bash
# 1. Confirm crew agent is installed and responsive
python ~/sap-crew-agent/sap-crew-agent/sap_crew/run.py --mode quick "echo test"

# 2. Confirm MCP bridge starts without errors
python ~/sap-crew-agent/sap-crew-agent/sap_crew_mcp_bridge.py --health

# 3. Run a real analysis and check output structure
python sap_crew/run.py --mode troubleshoot "Check ZCL_TEST for syntax errors" | jq '.phases[] | {phase, status, findings}'

# 4. Verify report contains all 9 dimensions
python sap_crew/run.py --mode quick "Analyze: CLASS zcl_test DEFINITION. ENDCLASS." | grep -c 'SEC\|AUTH\|DATA\|PERF\|STD\|INTERFACE\|CHANGE\|COMP\|FUNC'
# Expected: ≥ 9 (one per dimension)
```

## Performance & Resource Notes

- All processing is local — no source code leaves your machine.
- Full pipeline timeout: 10 min. Quick: 2 min. Troubleshoot: 1 min.
- ZROUTER dispatches to background thread — doesn't block main session.
- Same source + same request → crew reuses cached analysis when available.
- Monitor system resources with ST03N/SAT during large analyses (per SAP Performance Optimization Guide).
