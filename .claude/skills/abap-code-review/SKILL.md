---
name: abap-code-review
description: >-
  Pre-release ABAP code security and quality review across 9 dimensions.
  Produces formal GO/NO-GO assessment. Integrated with abaplint and ATC.
  Use before transporting ABAP code to QA or PRD.
trigger:
  - "review ABAP"
  - "code review"
  - "pre-release check"
  - "transport review"
  - "assess code quality"
  - "audit security"
  - "release gate"
  - "ABAP review"
  - "GO NO-GO"
  - "ATC check"
---

# ABAP Code Review — 9-Dimension Pre-Release Gate

Structured peer review before transport release. Integrated into
sap-workflow-pipeline stages 3 (proposal review) and 7 (code review).

## Prerequisites

- abaplint installed: `npx abaplint --version`
- abaplint config at `/opt/data/abaplint.json`
- ATC accessible via ADT or `mcp_hermes_unified_sap_adt_cli`
- Source code accessible at `/opt/data/src/`

## 1. Run Static Analysis

```bash
# Lint all ABAP source files
npx abaplint --config /opt/data/abaplint.json "/opt/data/src/**/*.abap" > /opt/data/reports/lint.json

# Security-focused review
npx abaplint --config /opt/data/abaplint.json --rule "*security*" "/opt/data/src/**/*.abap"

# Clean code score
npx abaplint --config /opt/data/abaplint.json --rule "clean_code" "/opt/data/src/**/*.abap"
```

## 2. 9-Dimension Review

- **SEC** — Security: SQL injection, dynamic code, credential exposure → CRITICAL=0
- **AUTH** — Authorization: Missing AUTHORITY-CHECK, S_DEVELOP gaps → HIGH=0
- **DATA** — Data Integrity: No BAPIRET2 check, missing ENQUEUE, COMMIT without WAIT → HIGH=0
- **PERF** — Performance: SELECT in loop, SELECT *, missing WHERE → MEDIUM≤2
- **STD** — Standards: Deprecated statements, hardcoding, naming → MEDIUM≤5
- **INTERFACE** — Interfaces: Hardcoded RFC dest, missing HTTP timeout → HIGH=0
- **CHANGE** — Change Impact: Objects not in transport, shared INCLUDEs → HIGH=0
- **COMP** — Compliance: PII exposure, missing change docs, GDPR → HIGH=0
- **FUNC** — Functional: Logic errors, edge cases, requirement gaps → MEDIUM≤3

## 3. GO/NO-GO Decision

- **GO**: All CRITICAL=0, all HIGH=0, MEDIUM within thresholds
- **NO-GO**: Any CRITICAL or HIGH > 0 → block transport
- **CONDITIONAL**: MEDIUM exceeds threshold → review board decision

## 4. Generate Review Report

```bash
# Create review report from lint output
cat > /opt/data/reports/REVIEW_2.md << 'EOF'
# ABAP Code Review — {Object Name}
Date: {date} | Transport: {TR number}

## Scores by Dimension
| Dim | Findings | Threshold | Status |
|-----|----------|-----------|--------|
| SEC | 0C/0H/1M | C=0       | PASS   |
| AUTH| 0C/0H/0M | H=0       | PASS   |
| DATA| 0C/1H/2M | H=0       | FAIL   |

## Overall: CONDITIONAL

### Findings
**DATA-1 [HIGH]**: Missing ENQUEUE before BAPI_PO_CREATE1 (line 245)
  Fix: Add ENQUEUE_READ before BAPI, DEQUEUE after COMMIT

**PERF-1 [MEDIUM]**: SELECT in LOOP (line 312)
  Fix: Use FOR ALL ENTRIES or JOIN
EOF
```

## 5. Pipeline Integration

- **Stage 3** (Proposal review): Review architecture against 9 dimensions → `REVIEW_1.md`
- **Stage 7** (Code review): Review implemented code, compare with Stage 3 → `REVIEW_2.md`
- Stage 7 MUST reference Stage 3 findings for cumulative tracking

## Pitfalls

- **abaplint skipped**:
  - Cause: Reviewer starts manual review without running linter first.
  - Solution: Always run abaplint as step 1 — never review unlinted code.
- **CRITICAL finding overridden**:
  - Cause: Reviewer marks GO despite a CRITICAL finding for "business urgency".
  - Solution: Single CRITICAL = mandatory NO-GO. No exceptions.
- **FUNC dimension without module expertise**:
  - Cause: Reviewer lacks module-specific config knowledge.
  - Solution: Cross-reference `/opt/data/module_maps/` for config validation.
- **Stage 7 ignores Stage 3**:
  - Cause: Reviewer treats Stage 7 as standalone, losing prior context.
  - Solution: Stage 7 report must explicitly address each Stage 3 finding.

## Verification

```bash
# Verify lint report was generated
test -f /opt/data/reports/lint.json && echo "OK: lint report exists" || echo "FAIL: no lint report"

# Verify no CRITICAL findings in lint output
grep -c '"severity":"critical"' /opt/data/reports/lint.json | xargs -I{} test {} -eq 0 && echo "OK: 0 critical" || echo "FAIL: critical findings present"

# Verify review report has GO/NO-GO
grep -E "^(GO|NO-GO|CONDITIONAL)" /opt/data/reports/REVIEW_2.md && echo "OK: decision present" || echo "FAIL: no decision"

# Check for SELECT * in source (should be 0)
grep -rn "SELECT \*" /opt/data/src/ && echo "FAIL: SELECT * found" || echo "OK: no SELECT *"
```
