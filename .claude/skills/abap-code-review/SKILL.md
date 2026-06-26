---
name: abap-code-review
description: >-
  Pre-release ABAP code security and quality review across 9 dimensions
  (SEC, AUTH, DATA, PERF, STD, INTERFACE, CHANGE, COMP, FUNC). Produces
  formal GO/NO-GO assessment. Integrated with abaplint static analysis
  and sap-crew-analysis deep review. Use before transporting ABAP code
  to QA or PRD. Adapted from shrek-abaper/sap-engineering-skill patterns.
  Triggers on: "review ABAP", "code review", "pre-release check", "transport
  review", "assess code quality", "audit security", "release gate".
---

# ABAP Code Review — 9-Dimension Pre-Release Gate

Structured peer review of ABAP code before transport release.
Integrated into sap-workflow-pipeline stages 3 and 7.

## 9 Dimensions

| # | Dimension | What It Checks | Severity Threshold |
|---|---|---|---|
| 1 | **SEC** — Security | SQL injection, dynamic code, OS calls, credential exposure, cross-site scripting in HTTP handlers | CRITICAL=0 |
| 2 | **AUTH** — Authorization | Missing AUTHORITY-CHECK, S_DEVELOP gaps, DCL role design, IAM catalog gaps | HIGH=0 |
| 3 | **DATA** — Data Integrity | Missing BAPIRET2 check, no ENQUEUE before write, COMMIT without WAIT, transaction safety | HIGH=0 |
| 4 | **PERF** — Performance | SELECT in loop, SELECT *, missing WHERE on large tables, full table scans, nested LOOPs | MEDIUM<=2 |
| 5 | **STD** — Standards | Deprecated statements (TABLES, COMPUTE, MOVE-CORRESPONDING), hardcoding, naming violations, Clean ABAP score < 70 | MEDIUM<=5 |
| 6 | **INTERFACE** — Interfaces | RFC destination hardcoded, missing timeout on HTTP calls, OData auth gaps, IDoc structure issues | HIGH=0 |
| 7 | **CHANGE** — Change Impact | Objects not in transport, missing dependencies, SAP standard modifications, shared INCLUDEs affected | HIGH=0 |
| 8 | **COMP** — Compliance | PII exposure, missing CDHDR/CDPOS change logging, dual-control gaps, SoD conflicts, GDPR issues | HIGH=0 |
| 9 | **FUNC** — Functional | Business logic errors, edge cases not handled, BAPI params vs module config mismatch, requirement coverage gaps | MEDIUM<=3 |

## Review Process

```
ABAP Source Code
    │
    ▼
1. STATIC ANALYSIS (abaplint)
   npm run abap:lint → JSON report
   npm run abap:review:security → security gate
   npm run abap:review:clean → clean code gate
    │
    ▼
2. 9-DIMENSION REVIEW (this skill)
   Analyze each dimension → severity-tagged findings
   Cross-reference with abaplint report
    │
    ▼
3. DEEP ANALYSIS (sap-crew-analysis, optional)
   7-agent pipeline: Architect, ABAP, Security, HANA, QA
    │
    ▼
4. GO/NO-GO DECISION
   GO: all CRITICAL=0, all HIGH=0, MEDIUM <= thresholds
   NO-GO: any CRITICAL or HIGH > 0
   CONDITIONAL: MEDIUM exceeds threshold → review board decision
```

## GO/NO-GO Criteria

| Finding Level | Threshold | Action on Exceed |
|---|---|---|
| **CRITICAL** | 0 | BLOCK transport — fix mandatory |
| **HIGH** | 0 (security/auth/interface/change/comp), 3 (others) | BLOCK transport for security dimensions |
| **MEDIUM** | See per-dimension thresholds | WARNING — document in transport log |
| **LOW** | 20 | Advisory only — no block |

## Integration with sap-workflow-pipeline

```
Stage 3 — PEER REVIEW 1 (this skill):
  Input: TECHNICAL_PROPOSAL.md from Stage 2
  Review: 9 dimensions on proposed architecture
  Output: REVIEW_1.md with GO/NO-GO
  If NO-GO → back to Stage 2 (revise proposal)

Stage 7 — PEER REVIEW 2 (this skill):
  Input: Implemented + linted code from Stages 4-6
  Review: 9 dimensions on actual code
  Compare with REVIEW_1 expectations
  Output: REVIEW_2.md with transport GO/NO-GO
  If NO-GO → back to Stage 4 (fix implementation)
```

## Review Report Template

```markdown
# ABAP Code Review — {Object Name}
Date: {date} | Reviewer: ABAP Code Review Skill | Transport: {TR number}

## Scores by Dimension

| Dim | Score | Threshold | Status |
|---|---|---|---|
| SEC | 0C/0H/1M | C=0 | PASS |
| AUTH | 0C/0H/0M | H=0 | PASS |
| DATA | 0C/1H/2M | H=0 | FAIL |
| PERF | 0C/0H/3M | M<=2 | FAIL |
| STD | 0C/0H/4M | M<=5 | PASS |
| INTERFACE | 0C/0H/0M | H=0 | PASS |
| CHANGE | 0C/0H/1M | H=0 | PASS |
| COMP | 0C/0H/0M | H=0 | PASS |
| FUNC | 0C/0H/2M | M<=3 | PASS |

## Overall: CONDITIONAL (2 FAIL, 0 CRITICAL)

### Findings

**DATA-1 [HIGH]**: Missing ENQUEUE before BAPI_PO_CREATE1
  Line 245, Method: create_purchase_order
  Fix: Add ENQUEUE_READ before BAPI call, ENQUEUE_WRITE after COMMIT

**PERF-1 [MEDIUM]**: SELECT in LOOP at line 312
  Method: get_material_details
  Fix: Use FOR ALL ENTRIES or JOIN instead

**PERF-2 [MEDIUM]**: SELECT * at line 298
  Fix: Specify field list: SELECT matnr, maktx, matkl FROM mara

**PERF-3 [MEDIUM]**: Missing ORDER BY on SELECT at line 338
  Fix: Add ORDER BY PRIMARY KEY

## Recommendations

1. Fix DATA-1 before transport (HIGH, blocking)
2. Fix PERF-1/2/3 in next iteration (MEDIUM, non-blocking)
3. Add ABAP Unit test for create_purchase_order edge cases
```

## Gotchas

- **abaplint is mandatory first pass**: Never review code that hasn't passed abaplint
- **FUNC dimension needs module expertise**: Cross-reference with module_maps/ for config table validation
- **CRITICAL findings always override**: Single CRITICAL = NO-GO regardless of other scores
- **Review is advisory**: Final transport decision rests with human release manager
- **Cumulative state**: Each review builds on prior. Stage 7 MUST reference Stage 3 findings.
