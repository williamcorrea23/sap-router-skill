---
name: abap-code-review
description: >-
  Pre-release ABAP code security and quality peer review across 12 dimensions.
  Auto-runs abaplint + ATC. Produces structured GO/NO-GO report with cumulative
  tracking between pipeline stages. Covers ZROUTER HTTP/OData/RFC/BDC patterns.
  Use before transporting ABAP code to QA or PRD.
trigger:
  - "review ABAP"
  - "code review"
  - "peer review"
  - "pre-release check"
  - "transport review"
  - "assess code quality"
  - "audit security"
  - "release gate"
  - "ABAP review"
  - "GO NO-GO"
  - "ATC check"
  - "revisar codigo"
  - "quality gate"
  - "melhore o peer-review"
---

# ABAP Code Review v3.0 — 12-Dimension Pre-Release Gate

Structured peer review with cumulative tracking. Pipeline stages:
- **Stage 3** (Proposal review): Architecture + design against 12 dims -> `REVIEW_1.md`
- **Stage 7** (Code review): Implemented code vs Stage 3 findings -> `REVIEW_2.md`

## Prerequisites (auto-run)

```bash
# Step 0 — Auto lint (mandatory, runs first)
npm run abap:lint 2>&1 | tee reports/lint.txt

# Step 0b — ATC check (if ADT available)
npm run abap:review 2>&1 | tee reports/atc.txt
```

## 12-Dimension Scoring

Each dimension scored 0-100. Weighted average determines GO/NO-GO.

### Core (original 9)
| # | Key | Weight | Description | Error Threshold |
|---|---|---|---|---|
| 1 | **SEC** | 2.0 | SQL injection, dynamic code, credential exposure, XSS in HTTP handler | CRITICAL=0 |
| 2 | **AUTH** | 1.5 | Missing AUTHORITY-CHECK, S_DEVELOP gaps, ICF auth bypass | HIGH=0 |
| 3 | **DATA** | 1.5 | No BAPIRET2 check, missing ENQUEUE, COMMIT without WAIT, LUW integrity | HIGH=0 |
| 4 | **PERF** | 1.0 | SELECT in loop, SELECT *, missing WHERE, nested LOOP, HTTP timeout missing | MEDIUM<=2 |
| 5 | **STD** | 1.0 | Deprecated statements, hardcoding, naming, Clean ABAP violations | MEDIUM<=5 |
| 6 | **INTERFACE** | 1.0 | Hardcoded RFC dest, missing HTTP timeout, CORS misconfig, missing Content-Type | HIGH=0 |
| 7 | **CHANGE** | 1.5 | Objects not in transport, shared INCLUDEs, cross-module impact | HIGH=0 |
| 8 | **COMP** | 1.0 | PII exposure, missing change docs, GDPR, NW 7.40 compatibility | HIGH=0 |
| 9 | **FUNC** | 1.0 | Logic errors, edge cases, requirement gaps, BAPI param validation | MEDIUM<=3 |

### ZROUTER v5 (new 3)
| # | Key | Weight | Description | Error Threshold |
|---|---|---|---|---|
| 10 | **HTTP** | 1.5 | IF_HTTP_EXTENSION security, CORS config, CSRF protection, path traversal, JSON injection, Content-Type validation | HIGH=0 |
| 11 | **BDC** | 1.0 | BDC_OKCODE must be explicit, BDC_CURSOR set, MODE N validation, SHDB recording integrity, CALL TRANSACTION error handling | MEDIUM<=2 |
| 12 | **RFC** | 1.5 | RFC destination not hardcoded, PARAMETER-TABLE security, dynamic CALL FUNCTION allowlist, bgRFC error handling, timeout config | HIGH=0 |

## Auto-Check Rules (applied per file)

### SEC — Security Patterns
```bash
# Mandatory checks - every file
grep -n "CONCATENATE.*INTO.*sql"          # SQL injection via dynamic SQL
grep -n "GENERATE SUBROUTINE"              # Dynamic code generation
grep -n "INSERT REPORT"                    # Program injection
grep -n 'PASSWORD.*=.*'\''[^$]'            # Hardcoded password
grep -n "CALL FUNCTION.*DESTINATION"       # Hardcoded RFC dest
grep -n "cl_http_client=>create_by_url"    # HTTP client without timeout
```

### HTTP — REST/HTTP Security (ZROUTER v5)
```bash
grep -n "set_header_field.*Origin"         # CORS config present
grep -n "get_cdata("                       # Must validate Content-Type
grep -n "get_form_field("                  # Must escape/validate input
grep -n "CS.*'/sap/"                       # Path traversal check
grep -n "escape_url\|escape_html"          # Output escaping present
```

### BDC — Batch Input Security (YFG_SBDC)
```bash
grep -n "BDC_OKCODE"                       # Must be explicit per screen
grep -n "BDC_CURSOR"                       # Must be set per screen
grep -n "MODE.*'N'"                        # Silent mode must handle errors
grep -n "MESSAGES INTO"                    # Must capture messages
```

### RFC — Dynamic RFC Security
```bash
grep -n "CALL FUNCTION.*lv_\|("             # Dynamic FM call needs allowlist
grep -n "PARAMETER-TABLE"                  # Must validate before call
grep -n "DESTINATION.*lv_\|("              # Dynamic destination needs validation
```

## Scoring Algorithm

```
score = 100 - (critical * 25) - (high * 10) - (medium * 3) - (low * 1)
weighted = sum(score[i] * weight[i]) / sum(weight[i])

GO:         all CRITICAL=0, all HIGH=0, weighted >= 70
CONDITIONAL: no CRITICAL, some HIGH=0, weighted >= 50
NO-GO:      any CRITICAL > 0 OR weighted < 50
```

## Output Format

### REVIEW_1.md (Stage 3 — Proposal)
```markdown
# Peer Review 1 — Architecture Assessment
**Date**: {date} | **Stage**: 3/8 | **Objects**: {count}

## Dimension Scores
| # | Dim | Score | Weight | Findings C/H/M/L | Status |
|---|-----|-------|--------|------------------|--------|
| 1 | SEC | 100 | 2.0 | 0/0/0/0 | PASS |
| 2 | AUTH | 85 | 1.5 | 0/1/0/0 | FAIL |
| ... | ... | ... | ... | ... | ... |

## Weighted Score: {score}/100 → {GO|CONDITIONAL|NO-GO}

## Findings
### AUTH-1 [HIGH] — Missing AUTHORITY-CHECK in dispatch_action()
**File**: zcl_zrouter_http.clas.abap:287
**Problem**: No authorization check before dispatching action.
**Fix**: Add `AUTHORITY-CHECK OBJECT 'ZROUTER' ID 'ACTIVITY' FIELD lv_activity.`
**Stage 7 tracking**: Must be resolved before transport.

### HTTP-1 [HIGH] — CORS wildcard without validation
**File**: zcl_zrouter_http.clas.abap:102
**Problem**: Access-Control-Allow-Origin: * without request validation.
**Fix**: Validate Origin header against allowlist before setting wildcard.
**Stage 7 tracking**: If prod, restrict to known domains.

## Cumulative — Findings requiring Stage 7 verification
| ID | Severity | Object | Line | Status |
|----|----------|--------|------|--------|
| AUTH-1 | HIGH | ZCL_ZROUTER_HTTP | 287 | → Stage 7 |
| HTTP-1 | HIGH | ZCL_ZROUTER_HTTP | 102 | → Stage 7 |
```

### REVIEW_2.md (Stage 7 — Code Review)
```markdown
# Peer Review 2 — Code Verification
**Date**: {date} | **Stage**: 7/8 | **Transport**: {TR}

## Stage 3 Resolution
| ID | Was | Resolution | Status |
|----|-----|------------|--------|
| AUTH-1 | HIGH | AUTHORITY-CHECK added line 291 | RESOLVED |
| HTTP-1 | HIGH | Origin allowlist implemented line 104 | RESOLVED |

## New Findings (post-implementation)
...same format as Stage 3...

## Transport Gate Decision
**All Stage 3 findings resolved**: YES
**New CRITICAL/HIGH**: 0
**Weighted Score**: 92/100
**Decision**: GO — Ready for transport
```

## Pipeline Integration

### Stage 3 Execution
```python
# In sap_router.py pipeline stage 3
def stage3_peer_review(proposal_files):
    results = []
    for file in proposal_files:
        lint = run_abaplint(file)
        review = agent("sap-code-reviewer",
            prompt=f"Review {file} architecture against 12 dimensions. Output per SKILL.md format.",
            schema=REVIEW_SCHEMA)
        results.append(review)
    return synthesize_review_1(results)
```

### Stage 7 Execution
```python
def stage7_peer_review(implemented_files, review_1):
    for finding in review_1.findings:
        verify_resolution(finding, implemented_files)
    new_findings = agent("sap-code-reviewer",
        prompt=f"Review implemented code in {implemented_files}. "
                f"Reference Stage 3 findings: {review_1.findings}. "
                f"Output per SKILL.md format with resolution tracking.",
        schema=REVIEW_SCHEMA)
    return synthesize_review_2(review_1, new_findings)
```

## Verification

```bash
# Run full review pipeline
npm run abap:review

# Check lint report
test -f reports/lint.txt && echo "OK: lint report" || echo "FAIL: no lint"

# Check zero CRITICAL
! grep -q "severity.*critical" reports/lint.txt && echo "OK: 0 critical" || echo "FAIL: critical"

# Verify review decision
grep -E "^(GO|NO-GO|CONDITIONAL)" reports/REVIEW_2.md && echo "OK: decision" || echo "FAIL: no decision"

# Check cumulative tracking
grep -c "RESOLVED" reports/REVIEW_2.md | xargs -I{} test {} -gt 0 && echo "OK: Stage 3 resolved" || echo "WARN: no Stage 3 tracking"

# Auto-fix common issues
npm run abap:lint:fix   # Fix keyword casing, obsolete statements
```

## Self-Learning

After each review, record outcomes:
```bash
npm run learn:route -- --action CODE_REVIEW --success true --score 92
npm run learn:mcp -- --mcp abaplint --latency 2.3 --success true
```
