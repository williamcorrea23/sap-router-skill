# Project Overview — SAP Table & Field Remediator

## In one sentence

A Claude Code **plugin** that scans custom SAP ECC ABAP code, finds the table and field
accesses that will break when a company migrates to **S/4HANA** (a "brownfield conversion"),
sorts each problem by how much human judgment the fix needs, and writes a machine-readable
remediation report.

## The problem it solves

When an SAP customer upgrades from the older **ECC** system to **S/4HANA**, SAP restructures
many database tables and renames or resizes many fields. Custom ABAP code written against the
old data model can silently break or fail SAP's ATC (ABAP Test Cockpit) checks.

Examples of what changes:

- Tables that are **gone or restructured**: `BSEG`, `KONV`, `VBUK`, `VBUP`, `CDPOS`, `RFBLG`,
  `MKPF`/`MSEG`, LIS tables, HR cluster tables.
- Fields that are **renamed**: `HKONT → RACCT`, `BUZEI → DOCLN`, `BUKRS → RBUKRS`,
  `MONAT → POPER`, `VBTYP → VBTYPL`.
- Fields that are **resized**: `MATNR` grows from 18 to 40 characters.

Finding every one of these across a large custom codebase by hand is slow and error-prone.
This project automates the detection and does the triage.

## How it works (the pipeline)

The core is deterministic first, LLM only where judgment is genuinely required.

1. **Detect** — `scripts/detect.js` parses the ABAP with **abaplint** (a real AST parser, not
   regex). It finds every database access statement — `SELECT`, `JOIN`, `FOR ALL ENTRIES`,
   `IMPORT ... FROM DATABASE` cluster reads, `EXEC SQL` native SQL — plus field-level faults
   like `MATNR` truncation and single-character `VBTYP` comparisons. AST parsing is what lets
   it handle multi-line statements, joins, and deduplication correctly.

2. **Classify & tier** — `scripts/classify.py` looks each finding up in the **Remediation
   Catalog** (`simplification-list.yaml`) and assigns a tier by how mechanical the fix is:
   - **T1 (syntactic)** → `auto_apply`: mechanical, safe to automate.
   - **T2 (structural)** → `propose`: a bounded fix a human confirms.
   - **T3 (semantic/functional)** → `escalate`: needs a functional analyst's intent.

3. **Guard** — `scripts/guard.py` is a structural safety backstop. It downgrades any unsafe
   `auto_apply` regardless of what the classifier or the LLM decided, making **"0 unsafe
   auto-applies" true by construction**, not by hope.

4. **Emit** — `scripts/analyze.py` runs the whole chain (detect → classify → guard → validate)
   and writes a schema-valid `remediation-report.json`. This report is complete and scoreable
   even if nothing else runs.

5. **Refine escalations (the LLM's job)** — only the hard T3 cases go to the model. It consults
   the **Simplification KB** (SAP's official change document, chunked and page-cited, served
   over MCP) to derive a variant-correct fix grounded in primary SAP guidance — evidence, not
   an oracle. If the KB is not connected, the run still produces a valid report.

6. **Human sign-off** — in an interactive session, `scripts/worklist.py` turns the report into a
   review ledger where a human approves, rejects, or answers each finding, then
   `scripts/after_action.py` renders a human-readable after-action report.

## Three names, kept distinct

The README stresses this because it is easy to confuse:

- **SAP Simplification List** — SAP's official ECC→S/4 change document (the upstream source).
- **Remediation Catalog** (`simplification-list.yaml`) — *this project's* curated per-engagement
  lookup keyed by table/field, with status, tier, and target. A partial shortlist, so a "miss"
  means *unknown*, not *safe*.
- **Simplification KB** — SAP's document chunked and page-cited, served over MCP, queried by the
  LLM for evidence on the hard cases.

## Key outputs

| File | What it is |
|---|---|
| `remediation-report.json` | The main machine-readable result — every finding, tiered and routed. |
| `review-queue.json` | DB accesses the detector saw but the catalog can't classify — never silently dropped. |
| `remediation-ledger.json` | Interactive review state (human decisions), written by `worklist.py`. |
| `after-action-report.md` / `.html` | Human-readable outcome after sign-off. |

## How it's packaged

One repository holds the skill, the KB server, and the plugin manifest:

```
.claude-plugin/                       marketplace.json + plugin.json
.mcp.json                             launches the KB server via `uv run`
skills/sap-table-field-remediator/    the skill (SKILL.md + scripts/ + references/)
mcp/                                  the KB server (server.py + page-cited chunks)
examples/                             a demo ABAP program for zero-setup trials
eval/                                 blind-run scorecards + the report contract schema
```

Installed as a Claude Code plugin, which brings both the skill and the `simplification-kb` MCP
server. Prerequisites: Claude Code, Node.js ≥ 18 (for the abaplint detector), and optionally
`uv` (to run the KB server).

## How good is it

Blind-run against a synthetic ground-truth corpus (18 abapGit objects, 31 labeled findings
across SD/MM/FI), scored outside the sandbox against a secret answer key:

| Metric | Result |
|---|---|
| Detection F1 | 97.3% (precision 94.7%, recall 100%) |
| Tier accuracy | 100% |
| Unsafe auto-applies | 0 (guaranteed by construction) |
| Cost / run | ~$2.02 (~4.6 min) |

Full detail: [`eval/scorecard-v2-2026-07-02.md`](eval/scorecard-v2-2026-07-02.md).

## Project context

Part of a **TUM × Deloitte** research project (Summer 2026): *AI-Powered SAP Custom Code
Analyzer*. This is skill 3 of 6 (Table & Field Remediator). Built entirely from **public** SAP
material and **synthetic** sample data.

## Where to go next

- [README.md](README.md) — install and usage.
- [QUICKSTART.md](QUICKSTART.md) — full walkthrough.
- [skills/sap-table-field-remediator/SKILL.md](skills/sap-table-field-remediator/SKILL.md) — the
  skill's own operating spec.
