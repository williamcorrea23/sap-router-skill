# Change taxonomy → tier/action routing (the classification spec)

Three composed axes per finding. `tier` + `action` are the **scored** fields; `category`
is the playbook key (informative); `world` is catalog-derived (must-I-fix).

## The 4 categories → tier → action

| Category | Nature of change | Tier | Action | Playbook |
|---|---|---|---|---|
| **1 Syntactic** | rename / field length — mechanical 1:1 | T1 | `auto_apply` | `playbooks/syntactic.md` |
| **2 Structural** | type / compat view — adjust the access | T2 | `propose` | `playbooks/structural.md` |
| **3 Semantic** | data reshaped — rebuild intent | T3 | `escalate` | `playbooks/semantic.md` |
| **4 Functional** | capability gone — redesign / triage | T3 | `escalate` | `playbooks/functional.md` |

Plus two non-tier routes:
- **A-verify / B-verify** → `action: verify` (never `auto_apply`). KNA1, LFA1, credit BAPI.
- **Statement-level smell** (EXEC SQL native, `SELECT *`, DB-in-LOOP) → `action: route_to_sibling`,
  `tier: null` (the Skill-3 → Skill-4 handoff).

ATC covers categories 1–2; **we earn our keep at 3–4 — value peaks at 3, triage at 4.**

## How `classify.py` derives each axis (deterministic)

`tier` starts at the catalog's `baseline_tier`, then **ratchets UP only**:
- a **write** (`INSERT/UPDATE/MODIFY/DELETE`, incl. dynamic + native) to a non-VALID object → **T3**
- an **offset/length slice** assigned off a length-changed field (MATNR) → **T3**

`category`:
- T1 → `syntactic` · T2 → `structural`
- T3 + status `RESTRUCTURED` → `semantic` (BSEG/MKPF/MSEG)
- T3 + status `ABOLISHED` (no clean 1:1: clusters, LIS) → `functional` (RFBLG/S001/S061/PCL2)
- escalated **write** → `functional` (capability removed, e.g. KONV write forbidden)

`action`: T1→`auto_apply`, T2→`propose`, T3→`escalate`; then **guard.py** is the structural
backstop — it independently re-checks and downgrades any unsafe `auto_apply` to `escalate`.

`replacement` (recommended target) — **released-API-first** (`preferred_replacement()`).
T2/T3 findings surface the released CDS view (`cds_view`) when the catalog has one: per the
2026-06-30 Deloitte review, a `SELECT` on the raw successor table (ACDOCA) works but the
released API (`I_JournalEntryItem`) is the clean-core-correct forward target. **T1 syntactic
auto-applies are the exception** — there the successor table is a field-identical 1:1
(`KONV → PRCD_ELEMENTS`) and IS the mechanical fix; its compat view (`V_KONV`) is not an
applicable target. The underlying table + field renames still appear in `rationale` /
`intent_question` for the human reviewer.

## Suppression — emit NOTHING on these (precision traps)

| What | In corpus | Why |
|---|---|---|
| **VALID** tables | MARA, MAKT, VBAK, VBAP, BKPF, T001, SKAT | not broken — a read needs no remediation |
| **DECLUSTERED_SAME_NAME** reads | CDPOS, CDHDR | declustered to a transparent table of the *same name*; a plain `SELECT` still works |
| **World-B** working BAPIs/FMs | BAPI_SALESORDER_*, BAPI_MATERIAL_GET_DETAIL, COMMIT/ROLLBACK | released, clean-core modernization is not ATC-forced (we don't scan `CALL FUNCTION`, so these never surface) |
| not in catalog | MARD etc. | unknown → assume valid |

Only **direct CDCLS cluster IMPORT/EXPORT** would make a change-document access a must-fix
(not present in the corpus). A `SELECT FROM cdpos` is never a must-fix.

## Object grain (one finding per statement)

- **One finding per DB-access statement**, keyed on the cataloged object — a JOIN on MKPF+MSEG
  yields a MKPF finding *and* an MSEG finding; a file naming BSEG on 15 lines yields findings only
  on the `SELECT`/`IMPORT`/`EXEC` lines, never `TABLES`/`TYPES` declarations.
- **Renamed/relocated fields live inside the fix**, not as separate findings: a `SELECT FROM vbuk`
  reading GBSTK/VBTYP is ONE VBUK finding (replacement carries the field moves), not three.
- **Length/value-CHANGED fields used OUTSIDE a DB statement DO get their own finding** — this is the
  field-level detection [DECISIONS.md 2026-07-01, Decision B]. Only catalog `status: CHANGED` fields
  qualify (MATNR 18→40, VBTYP CHAR1→CHAR4), so precision holds:
  - `MOVE …-matnr TO tgt` where `tgt` is a shorter fixed-length char → truncation, **T1** (widen target).
  - `IF vbtyp = 'C'` (single-char literal on a widened field) → **T2** (fix the comparisons).
  - Worst-fault-wins [Decision A]: `tier` only ever ratchets UP, so a field fault on the same line as
    a table fault cannot lower severity.

## Scored-metric implications (why the rules are shaped this way)

- **Detection F1** — flag every world-A must-fix (recall) without flagging VALID/distractors/World-B (precision).
- **Tier accuracy** — emit the catalog `baseline_tier`, ratcheted by write/offset escalation.
- **Unsafe auto-applies = 0** — guard.py makes this true by construction (see `playbooks/syntactic.md`).
- **% auto-resolved** — only genuine T1 reads (KONV→PRCD_ELEMENTS) auto-apply; everything else routes up.
