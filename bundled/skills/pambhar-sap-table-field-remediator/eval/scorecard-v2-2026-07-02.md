# Scorecard — v2-2026-07-02

**Run:** full LLM blind run of the **current** skill (`claude-opus-4-8`, analysis mode), scored blind
against the secret answer key. Supersedes `opus48-v1` (2026-06-27), which predated field-level
detection + released-API targeting.

> Note: the tool ran against the current skill via a sandbox-local `.claude/skills/` override — the
> installed plugin was stale at run time. Reproduce with `eval/run.sh --label <name>` once the plugin
> is updated. Machine scorecard: `synthetic-sap-codebase/eval/results/v2-2026-07-02/scorecard.{md,json}`.

## Headline

| # | Metric | Value |
|---|--------|-------|
| 1 | Detection F1 | **97.3%** (precision 94.7% · recall 100%, 18/18) |
| 2 | Tier accuracy | **100%** (18/18) |
| 3 | Unsafe auto-applies | **0** (guaranteed by the structural guard) |
| 4 | Correct-replacement rate | 94.4% (17/18) |
| 5 | % auto-resolved | 14.3% |
| — | Cost / run | **$2.02** (~$0.11 per correct finding · ~4.6 min · 35 turns) |

Per-module recall: FI 4/4 · MM 9/9 · SD 5/5 (all 100%).
Over-claims: **1** — `PCL2` @ `zfi_fg_payroll…:35` (accounts for the 94.7% precision).
Distractor over-claims: 0 / 7 · negative-control over-claims: 0 / 5.

## Corpus

31 labeled findings = 18 clear must-fixes + 7 distractors + 5 negative controls + 1 note-unverified.
36 catalog objects. `MARD` (F-MM-11) was added 2026-07-02 via the retro self-improvement loop and is
detected as a T3 finding here.

## What changed since `opus48-v1` (F1 90.9%)

- **Field-level detection** (MATNR truncation-on-assignment, VBTYP literal compares) — recovered the
  two former misses (F-MM-03, F-SD-05); recall 88.2% → 100%.
- **Released-API-first `replacement`** — T2/T3 emit the released CDS view; fix-quality accepts either
  the released view or the successor table.
- **Self-improvement loop** — MARD promoted from the review-queue into a regression-locked eval case.

> Cost caveat: the `total_cost_usd` above is from the `claude -p` CLI result. The scorer's own
> `usage`/cost fields read `$0` because the model can't populate its own token counters in the report
> (`run.sh` back-patches them in a normal run; this manual run did not).
