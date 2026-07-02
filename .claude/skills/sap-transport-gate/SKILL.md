---
name: sap-transport-gate
description: >-
  SAP Transport Release Gate — 10-dimension risk assessment before releasing
  transport requests. Verifies object completeness, dependencies, syntax,
  unit tests, ATC, authorization, cross-client, table keys, upgrade safety,
  and regression. Produces GO/NO-GO with evidence. Integrates STMS, SE09,
  SE10, E070/E071 inspection.
trigger:
  - release transport
  - transport gate
  - before transport
  - release check
  - ready for PRD
  - transport risk
  - can this go to production
---

# SAP Transport Gate — 10-Dimension Release Risk Assessment

**Mental model:** A transport request (TRKORR) is a container. Before you
release it from DEV, you export its objects to data files and flag them for
import into QA/PRD via STMS. Once released, the contents are frozen — any
fix requires a new transport. The gate exists because a bad release is
irreversible without a cleanup transport.

## Prerequisites

- SAP system access (DEV client with change rights)
- Transport request already created (SE09/SE10 or `TR_INSERT_REQUEST_WITH_TASKS`)
- All development objects assigned to the request (E071 entries populated)
- ATC check variant configured (transaction ATC / `SCI` for custom variants)
- ABAP Unit test classes written and runnable
- STMS configured across landscape (DEV → QA → PRD transport route)
- Authorization: `S_TRANSPRT` with release activity

## 10 Risk Dimensions

- **1. OBJECTS — Completeness** [CRITICAL]: All changed objects in transport? No orphans? E070/E071 consistent?
- **2. DEPENDENCIES — Prerequisites** [CRITICAL]: Prerequisite transports imported first? DDIC active before code?
- **3. SYNTAX — Compilability** [CRITICAL]: All objects syntax-check clean? No inactive versions?
- **4. UNIT_TESTS — Coverage** [HIGH]: ABAP Unit all green? Coverage ≥ 70%? No skipped tests?
- **5. ATC — Quality Gate** [HIGH]: ATC pass? No priority 1/2 findings? Exemptions documented with expiry?
- **6. AUTH — Authorization Impact** [HIGH]: New auth objects? Changed role behavior? IAM catalog updated?
- **7. CROSS_CLIENT — Client Safety** [MEDIUM]: Client-dependent changes? SCC1 needed? Cross-client customizing risk?
- **8. TABLE_KEYS — DDIC Impact** [CRITICAL]: Table key changes? Data loss risk? Table conversion needed?
- **9. UPGRADE — SPAU/SPDD Risk** [MEDIUM]: Will SAP upgrade overwrite? Modification adjustment needed?
- **10. REGRESSION — Blast Radius** [HIGH]: What breaks? Dependent programs checked? Integration tested?

## Decision Matrix

```
ALL CRITICAL pass + ALL HIGH pass          → GO
Any CRITICAL fail                           → NO-GO (fix mandatory)
HIGH fail in SYNTAX, DEPENDENCIES, AUTH     → NO-GO
HIGH fail in UNIT_TESTS, ATC, REGRESSION    → CONDITIONAL (document risk)
MEDIUM fail                                 → WARNING (log, don't block)
```

## Copyable Commands

### 1. Create transport request (if not exists)

```bash
# Via sap_router.py
python scripts/sap_router.py route --action BASIS_CREATE_REQUEST \
  --text "ZMM: Material handler implementation"
```

```abap
" Via RFC — TR_INSERT_REQUEST_WITH_TASKS
DATA: lv_trkorr TYPE trkorr.
CALL FUNCTION 'TR_INSERT_REQUEST_WITH_TASKS'
  EXPORTING iv_type         = 'K'   " K = Workbench, W = Customizing
            iv_text         = 'ZMM: Material handler'
  IMPORTING ev_request      = lv_trkorr.
```

### 2. Inspect transport contents (E070/E071)

```bash
# Via sap_router.py
python scripts/sap_router.py route --action BASIS_CODE_ANALYSIS \
  --trkorr DEVK900042
```

```abap
" Direct table read — verify objects in transport
SELECT e~trkorr, e~trstatus, o~object, o~obj_name
  FROM e070 AS e
  INNER JOIN e071 AS o ON e~trkorr = o~trkorr
  WHERE e~trkorr = 'DEVK900042'
  INTO TABLE @DATA(lt_objects).
```

### 3. Run dry-run gate (check without releasing)

```bash
python scripts/sap_router.py route --action BASIS_RELEASE_REQUEST \
  --trkorr DEVK900042 --mode dry-run
```

### 4. Release transport (SE09/SE10 equivalent)

```bash
# Full release via sap_router.py
python scripts/sap_router.py route --action BASIS_RELEASE_REQUEST \
  --trkorr DEVK900042
```

```abap
" Via RFC — TR_RELEASE_REQUEST
" ATC checks run automatically during release
CALL FUNCTION 'TR_RELEASE_REQUEST'
  EXPORTING iv_trkorr = 'DEVK900042'
  EXCEPTIONS OTHERS   = 1.
```

### 5. Check import status in target (STMS)

```bash
# Verify transport reached QA import queue
python scripts/sap_router.py route --action BASIS_STMS_CHECK \
  --trkorr DEVK900042 --system QA1
```

```abap
" Check import status via STMS tables
SELECT * FROM tmscsys WHERE sysnam = 'QA1'.
" Import queue: STMS → Overview → Imports → Select system → Import Queue
```

### 6. Post-import verification — check for dumps

```bash
python scripts/sap_router.py route --action BASIS_ST22_SCAN \
  --since 24h
```

```abap
" Direct ST22 dump check
SELECT datum, errid, ahname
  FROM snap
  WHERE datum >= @lv_yesterday
  INTO TABLE @DATA(lt_dumps).
```

## Pitfalls

- **Frozen after release**: Once released, a transport cannot be modified. Any fix needs a new transport — plan accordingly.
- **Table key changes**: Any TABL with key modifications → automatic NO-GO. Requires manual review and possibly a table conversion.
- **DDIC ordering**: DDIC objects (domains, data elements, tables) must be in a transport released BEFORE the code that uses them. Check TRDIR/E071 ordering.
- **Single import risk**: Importing a single transport from the middle of a queue can cause inconsistencies. SAP recommends full-queue imports. The single import stays in queue and reimports on next full run.
- **Cross-client customizing**: Client-dependent entries need SCC1 copy in non-000 clients. Flag these explicitly.
- **ATC exemptions**: Must have an expiry date. Expired exemptions block release. Check in transaction ATC → Exemptions.
- **SPAU/SPDD**: Any SAP standard modification requires upgrade impact assessment before release. Check during SPAU/SPDD transactions after upgrade.
- **Transport of copies**: Don't use transport-of-copies for regular development flow — they bypass the standard route and can cause version conflicts.
- **Locked objects**: If a developer hasn't released their task, the parent request can't be released. All tasks must be released first.
- **Post-release freeze**: PRD transports may need a change freeze window. Coordinate with Basis team for import scheduling.

## Verification Checklist

After gate assessment, verify:

- [ ] E070/TRSTATUS = 'R' (released) for the transport
- [ ] E071 contains all expected objects (no missing entries)
- [ ] No inactive objects in transport (SE80/SE38 syntax check clean)
- [ ] ABAP Unit: all tests pass, coverage ≥ 70%
- [ ] ATC: 0 priority 1, 0 priority 2 findings
- [ ] Transport visible in STMS import queue of target system
- [ ] ST22 shows no new dumps after import (24h monitoring)
- [ ] Integration test suite passes in target system
- [ ] SPAU/SPDD clean (no pending adjustments)
- [ ] TRANSPORT_DECISION.md produced with GO/NO-GO

## Anti-Patterns to Avoid

- ❌ Releasing a transport without ATC check → always verify ATC ran
- ❌ Importing out of sequence → respect dependency order
- ❌ Releasing with skipped unit tests → no exemptions for test skips
- ❌ Manual object addition after release → impossible by design
- ❌ Using SE01 to bypass SE09/SE10 workflow → same engine, no shortcut
- ❌ Ignoring cross-client impact → causes SCC1 issues downstream
- ❌ Releasing a transport with pending locks → tasks not released = request locked
