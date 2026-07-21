# After-report review — per-bucket prompt scripting

Detail for SKILL.md §"After the report (interactive worklist + human sign-off)". Load this when you
actually run the interactive walk. **Interactive-only** — never in `claude -p`.

The `worklist.py` ledger is dumb by design (stdlib, no LLM): it seeds decisions from the report +
review-queue and persists whatever a human decides. Your job is to present each finding clearly, get a
human decision, and record it. Identity for every `record` is `finding_ref = file::object::line`
(file exactly as it appears in the report). Valid statuses:
`pending | approved | rejected | answered | acknowledged | deferred`.

## Order of the walk
Group findings by `action` and go in **ascending judgment order** — cheap/mechanical first, so the
human warms up before the hard calls:
`auto_apply` (T1) → `propose` (T2) → `escalate` (T3) → `verify` → `route_to_sibling` → review-queue.
Run `python3 scripts/worklist.py status` at any point to see what is still open.

## T1 `auto_apply` — batch approve
Mechanical, variant-safe fixes the guard already blessed. Present **all T1s in one list** (object,
file:line, one-line fix) and take a single batch decision rather than one prompt each.
```
python3 scripts/worklist.py record --ref "<finding_ref>" --status approved
```
"Approve" authorizes the mechanical fix. The actual local-file edit is written later by `apply.py`
in the Apply step (below), which respects any `rejected` decision. If the human rejects one, record it
`rejected` with a `--comment` saying why.

## T2 `propose` — before → after
For each, show the source line as **before** and the finding's `replacement` as **after**, with
`rationale`. Draft/sharpen the after-text from the matching `references/playbooks/<category>.md`.
- Approve as-is → `--status approved`.
- Human edits the target → `--status approved --comment "<the edited after-text>"`.
- Not a real fix / drop → `--status rejected --comment "<why>"`.
```
python3 scripts/worklist.py record --ref "<finding_ref>" --status approved --comment "<edited target, if any>"
```

## T3 `escalate` — the headline sign-off moment
Show the `intent_question` (and the object's KB evidence if you pulled it in §2). The human answers
inline; capture the answer verbatim and the disposition (what to do) in the comment.
```
python3 scripts/worklist.py record --ref "<finding_ref>" --status answered \
  --answer "<human's answer to the intent_question>" --comment "<disposition / next step>"
```

## `verify` — acknowledge
A-verify/B-verify items (e.g. KNA1, LFA1): no fix asserted, just confirm a human saw it and owns the
check.
```
python3 scripts/worklist.py record --ref "<finding_ref>" --status acknowledged --comment "<owner, optional>"
```

## `route_to_sibling` — log & defer
Belongs to another skill's lane. Log the handoff and defer.
```
python3 scripts/worklist.py record --ref "<finding_ref>" --status deferred --comment "<handoff note: which sibling, why>"
```

## Review-queue items — decide fix or skip
Catalog-misses (`not_in_catalog`, e.g. MARD) that `init` already loaded into the ledger. This is
SKILL §2.1's decide-or-skip, now recorded: the human returns a verdict **plus a short comment**
(recommended approach, caveat, or why it is safe to skip).
- Promote to a fix → `--status approved --comment "<recommended fix / KB pages>"`.
- Skip → `--status rejected --comment "<why safe to skip>"`.

## Apply the approved fixes (writes local source)
Once decisions are recorded, write the mechanical fixes to the local `.abap` files:
- **T1 `auto_apply`** → run `apply.py`. It swaps each object token whole-word (e.g. `KONV` ->
  `PRCD_ELEMENTS`), emits a reversible unified diff + `apply-log.json`, honors ledger `rejected`/
  `deferred` decisions, and never touches T2/T3. Preview with `--dry-run` first.
  ```
  python3 scripts/apply.py --report ./remediation-report.json --src . --ledger ./remediation-ledger.json --dry-run
  python3 scripts/apply.py --report ./remediation-report.json --src . --ledger ./remediation-ledger.json
  ```
- **Approved T2/T3** → Claude writes these via its editor (variant-dependent; not mechanical).
- **Verify** no must-fix reference survives: `python3 scripts/residual_check.py --src ./src`.

**Boundary:** all of this edits LOCAL files only. Pushing/activating the change in the SAP system is
the client's step — the tool has no system access. "Unsafe auto-applies = 0" still holds (guard.py).

## Close out
1. **Sign-off** (gates the after-action report):
   ```
   python3 scripts/worklist.py signoff --by "<name>"
   ```
2. **After-action report** (human-readable md + html; auto-detects `apply-log.json` next to the report):
   ```
   python3 scripts/after_action.py --report ./remediation-report.json --ledger ./remediation-ledger.json
   ```
3. **Retro (optional, demo)**:
   ```
   python3 scripts/retro.py --ledger ./remediation-ledger.json --review-queue ./review-queue.json
   ```
