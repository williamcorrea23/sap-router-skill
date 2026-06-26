---
name: sap-transport-gate
description: >-
  SAP Transport Release Gate — 10-dimension risk assessment before releasing
  transport requests. Checks: object completeness, dependencies, syntax errors,
  unit test coverage, ATC compliance, authorization impact, cross-client impact,
  table key changes, upgrade safety, and regression risk. Produces GO/NO-GO
  decision with evidence. Adapted from shrek-abaper/sap-engineering-skill
  transport-gate patterns. Triggers on: "release transport", "transport gate",
  "before transport", "release check", "ready for PRD", "transport risk",
  "can this go to production".
---

# SAP Transport Gate — 10-Dimension Release Risk Assessment

Final gate before transport release. Checks everything that could break
in QA or PRD after import.

## 10 Risk Dimensions

| # | Dimension | What It Checks | Severity |
|---|---|---|---|
| 1 | **OBJECTS** — Completeness | All changed objects in transport? No orphans? Entry in E070/E071 correct? | CRITICAL |
| 2 | **DEPENDENCIES** — Prerequisites | All prerequisite transports imported first? DDIC active before code? | CRITICAL |
| 3 | **SYNTAX** — Compilability | All objects syntax-check clean? No inactive objects? | CRITICAL |
| 4 | **UNIT_TESTS** — Test Coverage | ABAP Unit all green? Coverage >= 70%? No skipped tests? | HIGH |
| 5 | **ATC** — Quality Gate | ATC check variant pass? no priority 1/2 findings? Exemptions documented? | HIGH |
| 6 | **AUTH** — Authorization Impact | New auth objects? Changed role behavior? IAM catalog updated? | HIGH |
| 7 | **CROSS_CLIENT** — Client Safety | Client-dependent changes? SCC1 needed? Cross-client customizing risk? | MEDIUM |
| 8 | **TABLE_KEYS** — DDIC Impact | Table key changes? Data loss risk? Conversion needed? | CRITICAL |
| 9 | **UPGRADE** — SPAU/SPDD Risk | Will SAP upgrade overwrite? Modification adjustment needed? | MEDIUM |
| 10 | **REGRESSION** — Blast Radius | What could break? Dependent programs/classes checked? Integration tested? | HIGH |

## Decision Matrix

```
ALL CRITICAL pass + ALL HIGH pass → GO
Any CRITICAL fail → NO-GO (fix mandatory)
HIGH fail in SYNTAX, DEPENDENCIES, AUTH → NO-GO
HIGH fail in UNIT_TESTS, ATC, REGRESSION → CONDITIONAL (document risk)
MEDIUM fail → WARNING (log, don't block)
```

## Integration with sap-workflow-pipeline Stage 8

```
Stage 8 — TRANSPORT GATE (this skill):
  Input: All artifacts from Stages 1-7:
    - Spec Analysis (Stage 1)
    - Technical Proposal (Stage 2)
    - Peer Review 1 + 2 (Stages 3, 7)
    - abaplint report (Stage 5)
    - Crew Analysis (Stage 6)
    - Unit test results (Stage 4 implicit)

  Actions:
    1. Verify all 10 dimensions
    2. Create transport request if not exists
    3. Include all changed objects
    4. Run final syntax check
    5. Produce TRANSPORT_DECISION.md

  Output: TRANSPORT_DECISION.md with GO/NO-GO
  If GO → transport released
  If NO-GO → back to Stage 4 with specific fix list
```

## Transport Decision Report Template

```markdown
# TRANSPORT DECISION — {TR Number}
Date: {date} | Target: {DEV→QA / QA→PRD} | Release Manager: {name}

## Gate Results

| # | Dimension | Status | Details |
|---|---|---|---|
| 1 | OBJECTS | PASS | 3 objects: ZCL_MM_HANDLER, ZCL_MM_HELPER, ZMM_LOG |
| 2 | DEPENDENCIES | PASS | Prerequisite TR DEVK900041 already imported |
| 3 | SYNTAX | PASS | All objects active, syntax check clean |
| 4 | UNIT_TESTS | PASS | 12/12 green, coverage 82% |
| 5 | ATC | PASS | 0 priority 1, 0 priority 2, exemptions: none |
| 6 | AUTH | PASS | No new auth objects, existing roles sufficient |
| 7 | CROSS_CLIENT | PASS | Client-independent changes only |
| 8 | TABLE_KEYS | PASS | No DDIC changes in transport |
| 9 | UPGRADE | PASS | No SAP standard modifications |
| 10 | REGRESSION | PASS | Integration test green, no dependent breakage |

## Overall: GO

### Evidence

- abaplint: 0 CRITICAL, 0 HIGH, 3 MEDIUM (documented)
- ABAP Unit: 12/12 tests pass, 82% coverage
- Peer Review 2 score: 85/100 (all dimensions pass)
- Crew Analysis score: 82/100 (0 critical fixes needed)

### Transport Contents

| Object | Type | Package | Description |
|---|---|---|---|
| ZCL_MM_HANDLER | CLAS | ZROUTER | Material handler class |
| ZCL_MM_HELPER | CLAS | ZROUTER | Config validation utility |
| ZMM_LOG | TABL | ZROUTER | Audit log table |

### Post-Release Verification

- [ ] Verify objects active in target system
- [ ] Run integration test suite
- [ ] Check ST22 for new dumps (24h monitoring)
- [ ] Validate MM03 for test material created during verification
```

## CLI Commands

```bash
# Run transport gate on a specific transport
python scripts/sap_router.py route --action BASIS_RELEASE_REQUEST

# Check transport readiness without releasing
aibap: check_transport(transport="DEVK900042", mode="dry-run")

# Full gate with all 10 dimensions
# Triggered automatically by sap-workflow-pipeline Stage 8
```

## Gotchas

- **Table key changes**: Any transport with TABL objects containing key changes → automatic NO-GO. Needs manual review.
- **Cross-client customizing**: Client-dependent entries must be flagged. SCC1 needed for non-000 clients.
- **ATC exemptions**: Must be documented with expiration. Unexpired exemptions block release.
- **SPAU/SPDD**: Any SAP standard modification needs upgrade impact assessment.
- **Transport sequence**: Multiple transports must be released in dependency order. Check E070/E071 TRDIR.
- **Post-release freeze**: Production transports may need change freeze window. Check with Basis team.
