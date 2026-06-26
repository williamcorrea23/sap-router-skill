---
name: sap-workflow-pipeline
description: >-
  Automated spec-to-production ABAP pipeline — reads specification,
  identifies functional modules, routes to correct ABAP skill, generates
  technical proposal, peer reviews with abaplint, runs sap-crew-analysis
  (7 agents, 9 dimensions), applies review gate, and produces transport-ready
  code. End-to-end: spec → analyze → route → proposal → implement → lint →
  peer-review → transport-gate. Use when user asks to "implement this spec",
  "create ABAP from requirements", "full pipeline", "end-to-end ABAP",
  "from spec to transport", or "automated ABAP workflow". Triggers on:
  "implement specification", "build from spec", "ABAP pipeline", "full
  workflow", "spec to code", "automated development".
---

# SAP Workflow Pipeline — Spec → Transport Automated

Single automated pipeline from specification document to transport-ready
ABAP code with integrated peer review.

## Pipeline Stages

```
SPEC DOC (.md / .pdf / text)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 1 — SPEC ANALYSIS (sap-router-skill)           │
│                                                       │
│  1. Parse specification document                     │
│  2. Identify functional module(s): MM/SD/FI/QM/...   │
│  3. Extract requirements: BAPIs, tables, config      │
│  4. Output: MODULE_ANALYSIS.md                       │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 2 — TECHNICAL PROPOSAL (sap-crew-analysis)     │
│                                                       │
│  1. SAP Architect agent: solution design             │
│  2. ABAP Developer agent: implementation patterns    │
│  3. Security Architect: threat model                  │
│  4. Output: TECHNICAL_PROPOSAL.md with sections:     │
│     - Architecture overview                          │
│     - Classes/interfaces to create                   │
│     - BAPI/RFC calls needed                          │
│     - DDIC objects (tables, structures)              │
│     - Authorization objects                          │
│     - Test strategy                                  │
│     - Risk assessment                                │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 3 — PEER REVIEW 1 (abap-code-review)          │
│                                                       │
│  1. Review proposal against 9 dimensions:            │
│     SEC | AUTH | DATA | PERF | STD | INTERFACE       │
│     CHANGE | COMP | FUNC                             │
│  2. Output: REVIEW_1.md with GO/NO-GO decision       │
│  3. If NO-GO → revise proposal (back to Stage 2)     │
└───────────────────────┬─────────────────────────────┘
                        │ GO
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 4 — IMPLEMENTATION (cavecrew-builder + ADT)   │
│                                                       │
│  1. cavecrew-builder: implement each class/method    │
│  2. ADT MCP (arc-1): write source to SAP system      │
│  3. ADT MCP: syntax check each object                │
│  4. ADT MCP: unit test creation                      │
│  5. Output: deployed ABAP objects + test results     │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 5 — STATIC ANALYSIS (abaplint)                │
│                                                       │
│  1. npm run abap:lint → abaplint report             │
│  2. npm run abap:review:security → security gate    │
│  3. npm run abap:review:clean → clean code gate     │
│  4. npm run abap:review:report → HTML report        │
│  5. Output: abap-review-report.html                 │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 6 — DEEP ANALYSIS (sap-crew-analysis)         │
│                                                       │
│  1. 7-agent pipeline (full mode, 3-5 min)           │
│  2. 9-dimension analysis of implemented code         │
│  3. Fix suggestions with code snippets               │
│  4. Output: CREW_ANALYSIS_REPORT.md                  │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 7 — PEER REVIEW 2 (abap-code-review)          │
│                                                       │
│  1. 9-dimension review of implemented + linted code  │
│  2. Compare with REVIEW_1 expectations               │
│  3. Output: REVIEW_2.md with transport GO/NO-GO      │
│  4. If NO-GO → fix issues (back to Stage 4)          │
└───────────────────────┬─────────────────────────────┘
                        │ GO
                        ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 8 — TRANSPORT GATE (sap-transport-gate)       │
│                                                       │
│  1. 10-dimension risk assessment                     │
│  2. Transport request creation                       │
│  3. Object inclusion verification                    │
│  4. Output: TRANSPORT_DECISION.md                    │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
                   TRANSPORT RELEASED
```

## Pipeline CLI

```bash
# Full pipeline from spec to transport (all 8 stages)
python scripts/sap_router.py pipeline --spec requirements.md --module auto

# Fast pipeline: analyze → implement → lint (4 stages, skip crew analysis)
python scripts/sap_router.py pipeline --spec requirements.md --mode fast

# Dry run: analyze spec only, output proposal, don't write code
python scripts/sap_router.py pipeline --spec requirements.md --dry-run

# Resume from specific stage (after fixing issues)
python scripts/sap_router.py pipeline --spec requirements.md --resume-from stage4

# Parallel waves (DEFAULT): same-wave stages launch concurrently; Stage 4 fans out 1 builder per object
python scripts/sap_router.py pipeline --spec requirements.md            # --parallel is the default
python scripts/sap_router.py pipeline --spec requirements.md --serial   # one stage per wave (no concurrency)

# Emit just the machine-readable wave plan (stages 2-8) for the orchestrator to launch in batches
python scripts/sap_router.py dispatch-plan --spec requirements.md
# Plan concurrent caveman subagents for an ad-hoc task
python scripts/sap_router.py crew-dispatch --task "find the leak then review the diff"
```

## Parallel Dispatch (waves)

Stages are grouped into WAVES; stages sharing a wave run concurrently (the
orchestrator launches all same-wave subagents in ONE batch). `dispatch-plan`
and `pipeline` emit a machine-readable plan: `{ "mode": "parallel", "waves": [ {wave, concurrent, stages:[...]} ] }`.

```
Wave 0  [sequential]  stage1 Spec Analysis            (must run first)
Wave 1  [sequential]  stage2 Technical Proposal
Wave 2  [sequential]  stage3 Peer Review 1
Wave 3  [concurrent]  stage4 Implementation (fan-out x N objects — 1 cavecrew-builder per object)
Wave 4  [concurrent]  stage5 Static Analysis (abaplint)  ||  stage6 Deep Analysis (Crew)
Wave 5  [sequential]  stage7 Peer Review 2
Wave 6  [sequential]  stage8 Transport Gate
```

Rules:
- Same wave => launch agents concurrently in one batch. Different waves => sequential (barrier between).
- Stage 4 fans out one `cavecrew-builder` per detected object — the big parallel win.
- `--serial` collapses to one stage per wave (no concurrency) for debugging.
- ZROUTER is never required; the pipeline runs ADT-first -> SAP GUI scripting regardless of opt-in.

## Stage 1 Detail: Spec Analysis

```python
# spec_analyzer.py — reads spec, identifies module, extracts requirements
def analyze_spec(spec_text: str) -> dict:
    """Parse specification and return structured requirements."""
    analysis = {
        'modules': identify_modules(spec_text),
        'entities': extract_entity_requirements(spec_text),
        'bapis': identify_bapi_requirements(spec_text),
        'config_tables': identify_config_tables(spec_text),
        'authorizations': extract_auth_requirements(spec_text),
        'integrations': identify_integration_points(spec_text),
        'complexity': assess_complexity(spec_text),  # SIMPLE | MODERATE | COMPLEX | VERY_COMPLEX
        'estimated_objects': estimate_object_count(spec_text),
    }

    # Route to correct module skill
    primary_module = analysis['modules'][0] if analysis['modules'] else 'BASIS'
    analysis['routing'] = {
        'primary_skill': f'sap-bapi-integration',
        'module_skill': 'sap-bapi-integration',
        'abap_skills': ['clean-abap', 'abap-code-patterns', 'abap-unit-testing'],
    }

    return analysis

# Module keyword detection
MODULE_KEYWORDS = {
    'MM': ['material', 'purchase order', 'PO', 'MIGO', 'inventory', 'vendor',
           'procurement', 'goods receipt', 'stock', 'MRP', 'source list'],
    'SD': ['sales order', 'customer', 'delivery', 'billing', 'pricing',
           'shipping', 'credit memo', 'invoice', 'VA01', 'VA02', 'VL01N'],
    'FI': ['GL account', 'journal entry', 'posting', 'balance', 'profit',
           'ledger', 'AP', 'AR', 'asset', 'tax', 'FB01', 'FB50'],
    'QM': ['inspection', 'quality', 'lot', 'defect', 'specification',
           'QA01', 'QA02', 'QE01', 'inspection plan'],
    'PP': ['production order', 'BOM', 'routing', 'MRP', 'capacity',
           'CO01', 'CS01', 'CA01', 'work center'],
    'WM': ['warehouse', 'transfer order', 'storage bin', 'picking',
           'LT01', 'MIGO', 'handling unit'],
    'CO': ['cost center', 'internal order', 'allocation', 'assessment',
           'KO01', 'KS01', 'KA01', 'cost element'],
    'HCM': ['employee', 'personnel', 'infotype', 'PA20', 'PA30',
           'org unit', 'payroll', 'time management'],
}
```

## Stage 2 Detail: Technical Proposal Template

```markdown
# TECHNICAL PROPOSAL — {Project Name}

## 1. Architecture Overview
- Primary module: {MODULE}
- Implementation approach: {ADT-first | ZROUTER RFC | Hybrid with GUI fallback}
- Estimated objects: {N} classes, {M} methods, {K} DDIC objects

## 2. Object List

### Classes
| Class | Type | Purpose | Methods | LOC Est |
|---|---|---|---|---|
| ZCL_{MODULE}_HANDLER | Handler | BAPI wrapper for {entity} | 5 | 200 |
| ZCL_{MODULE}_HELPER | Utility | Config checks, validation | 3 | 100 |

### DDIC Objects
| Object | Type | Purpose |
|---|---|---|
| Z{MODULE}_LOG | TABLE | Audit log for {entity} operations |

### BAPI/RFC Calls
| BAPI/FM | Module | Purpose |
|---|---|---|
| BAPI_MATERIAL_SAVEDATA | MM | Create material master |

## 3. Error Handling Strategy
- Exception class: ZCX_{MODULE} (inherits CX_STATIC_CHECK)
- BAL logging: all operations logged to Z{MODULE}_LOG
- BAPIRET2 validation: check TABLES RETURN, not just IMPORTING RETURN

## 4. Authorization Strategy
- Auth objects required: {list}
- Check at: method entry + before BAPI call

## 5. Test Strategy
- ABAP Unit: {N} test methods in local test class
- Risk level: {CRITICAL | DANGEROUS | HARMLESS}
- Test doubles: {list of mocks needed}

## 6. Risk Assessment
| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| BAPI returns unexpected error | High | Medium | Full BAPIRET2 TABLE check |
```

## Pipeline Integration with MEMORY.md

```
Pipeline execution → each stage writes to MEMORY.md:

### [14:32] WORKFLOW/MM-CreateMaterial-Spec
status:OK | stage:1_SpecAnalysis | module:MM | bapi:BAPI_MATERIAL_SAVEDATA

### [14:35] WORKFLOW/MM-CreateMaterial-Proposal
status:OK | stage:2_TechProposal | objects:3_classes,2_ddic | review:GO

### [14:38] WORKFLOW/MM-CreateMaterial-PeerReview1
status:OK | stage:3_PeerReview1 | score:85/100 | dimensions:SEC,AUTH,PERF

### [14:42] WORKFLOW/MM-CreateMaterial-Implement
status:OK | stage:4_Implementation | deployed:3_objects | syntax:OK

### [14:44] WORKFLOW/MM-CreateMaterial-Lint
status:OK | stage:5_Lint | critical:0 | high:0 | clean_score:78

### [14:48] WORKFLOW/MM-CreateMaterial-CrewAnalysis
status:OK | stage:6_CrewAnalysis | score:82/100 | fixes:0_critical,2_medium

### [14:50] WORKFLOW/MM-CreateMaterial-Transport
status:GO | stage:8_TransportGate | tr:DEVK900043 | release:APPROVED
```

## Gotchas

- **Spec quality matters**: Vague specs produce vague proposals. Flag underspecified sections.
- **Module misdetection**: Cross-module specs (MM+FI) need dual routing. Check keyword overlap.
- **Peer review bottleneck**: Human review needed for CRITICAL findings. AI review is advisory only.
- **Pipeline resume**: Each stage is idempotent. Resume from any stage without redoing previous work.
- **Token budget**: Full pipeline (all 8 stages) uses ~50K tokens. Fast mode uses ~15K.
- **Transport risk**: Transport gate blocks on CRITICAL security findings only. MEDIUM findings generate warnings.
- **ABAplint version**: Pin `@abaplint/cli` version in CI. Rule changes can flip gate decisions.
- **Crew analysis parallel**: sap-crew-analysis runs in background. Pipeline continues to Stage 5 (lint) in parallel.
