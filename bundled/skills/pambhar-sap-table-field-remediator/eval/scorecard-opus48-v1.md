# Scorecard — opus48-v1

> **Cost note:** the report's `usage` block was empty, so the scorer prints $0 below. The real
> cost from the `claude -p` CLI wrapper: **$2.7468 / run** (~$0.183 per correct finding),
> ~315 s, 30 turns, 24,982 output tokens (cache-read 772,466). Treat the $0 cost lines below as
> "not captured by the report," not as free.

## Run metadata

- model: `claude-opus-4-8`
- skill_version: `1.0.0`
- mode: `analysis`
- schema_version: `1.0`
- scanned_files: 20
- findings_reported: 22

## HEADLINE

| # | Metric | Value |
|---|--------|-------|
| 1 | Detection F1 | **90.9%** |
| 2 | Tier accuracy | **100.0%** |
| 3 | Unsafe auto-applies | **0** (OK, must be 0) |
| 4 | Cost per run | **$0.0000** |
| 5 | % auto-resolved | **9.1%** |
| ratio | Cost per correct finding | **$0.0000** |

## DIAGNOSTIC

### Precision / recall split

- precision: 93.8%  (15 TP / 16 claimed)
- recall: 88.2%  (15 / 17 clear must-fixes)
- F1: 90.9%
- missed must-fixes: F-MM-03, F-SD-05
- over-claims:
  - SPURIOUS `PCL2` @ src/zfi_finance/zfi_fg_payroll.fugr.z_read_payroll_amount.abap:35 action=escalate (overclaim_spurious)

### Tier confusion matrix (rows=expected, cols=reported; over detected must-fixes)

| expected \ reported | T1 | T2 | T3 | (none) |
|---|---|---|---|---|
| T1 | 2 | 0 | 0 | 0 |
| T2 | 0 | 3 | 0 | 0 |
| T3 | 0 | 0 | 10 | 0 |

- tier accuracy: 100.0%  (15 / 15)

### Over-claim rate on distractors

- distractor over-claim rate: 0.0%  (0 / 7)
- negatives over-claimed: 0 / 5

### Fix quality (correct replacement vs catalog)

- correct-replacement rate: 80.0%  (12 / 15)
  - [ok] F-FI-01 `BSEG`: catalog `ACDOCA` vs reported `ACDOCA`
  - [MISS] F-FI-02 `RFBLG`: catalog `ACDOCA` vs reported `BSEG`
  - [ok] F-FI-03 `BSEG`: catalog `ACDOCA` vs reported `ACDOCA`
  - [ok] F-FI-05 `BSEG`: catalog `ACDOCA` vs reported `ACDOCA`
  - [ok] F-MM-01 `MSEG`: catalog `MATDOC` vs reported `MATDOC`
  - [ok] F-MM-02 `MKPF`: catalog `MATDOC` vs reported `MATDOC`
  - [ok] F-MM-04 `KONV`: catalog `PRCD_ELEMENTS` vs reported `PRCD_ELEMENTS`
  - [ok] F-MM-06 `MATNR`: catalog `MATNR` vs reported `MATNR (CHAR40) - redesign grouping, no fixed-offset split`
  - [MISS] F-MM-08 `KONV`: catalog `PRCD_ELEMENTS` vs reported `pricing conditions API (no direct table write)`
  - [ok] F-MM-09 `MSEG`: catalog `MATDOC` vs reported `MATDOC`
  - [MISS] F-MM-10 `S061`: catalog `Embedded Analytics / released CDS` vs reported `released analytics CDS view / Embedded Analytics`
  - [ok] F-SD-01 `VBUK`: catalog `VBAK` vs reported `VBAK`
  - [ok] F-SD-02 `VBUP`: catalog `VBAP` vs reported `VBAP`
  - [ok] F-SD-03 `VBUK`: catalog `VBAK` vs reported `VBAK`
  - [ok] F-SD-06 `KONV`: catalog `PRCD_ELEMENTS` vs reported `PRCD_ELEMENTS`

### Cost breakdown

- cost: $0.0000  (per correct finding: $0.0000)
- turns: 0  (the real driver)
- output tokens: 0
- input tokens: 0  (cache-read: 0)
- latency: 0 ms

### Auto-resolved

- % of all findings auto-applied: 9.1%  (2 findings)
- auto-applied on clear must-fixes: 2

### Side counts (excluded from headline)

- bonus verify findings (A-verify/B-verify handled correctly): 2
- tolerated notes on negatives/distractors: 1
- note_unverified reported: 1 / 1 (kept out of headline)

### Per-module drilldown

| module | detected / must-fixes | recall |
|---|---|---|
| FI | 4 / 4 | 100.0% |
| MM | 7 / 8 | 87.5% |
| SD | 4 / 5 | 80.0% |

