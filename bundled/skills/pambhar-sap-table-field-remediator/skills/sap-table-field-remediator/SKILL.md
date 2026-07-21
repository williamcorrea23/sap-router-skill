---
name: sap-table-field-remediator
description: Scans custom ECC ABAP for data access (SELECT, SELECT SINGLE, JOIN, FOR ALL ENTRIES, IMPORT FROM DATABASE cluster reads, and EXEC SQL native SQL) on tables or fields that change in an S/4HANA brownfield conversion, classifies each finding by remediation complexity (syntactic, structural, semantic, functional tiers T1/T2/T3), routes it (auto_apply, propose, escalate, verify, route_to_sibling) with a deterministic safety guard, and emits a machine-readable remediation-report.json. Use for "S/4HANA conversion", "ATC remediation", "what breaks in S/4HANA", "table/field remediation", "S/4 SELECT/table check", "remediate this ABAP for S/4HANA", or analyzing legacy ABAP against the SAP simplification list.
---

# SAP Table & Field Remediator

Detect custom ABAP that references tables/fields that change in an **S/4HANA brownfield
conversion**, classify each by **how much human judgment its fix needs**, and emit a
machine-readable `remediation-report.json`. Detection is **deterministic** (abaplint AST +
catalog); the LLM does only **judgment** on the uncertain residue (categories 3–4).

## When to use
Legacy/custom ECC ABAP + a question like "what breaks in S/4HANA?", "remediate this for the
conversion", "run the ATC table/field check". Inputs: a directory of `*.abap` and the public
catalog `simplification-list.yaml`.

## Mental model (do not skip)
- **The Remediation Catalog is the evidence locator — not an oracle.** `simplification-list.yaml` (key `object`; statuses VALID, CHANGED,
  RENAMED, ABOLISHED, RESTRUCTURED, DECLUSTERED_SAME_NAME, REDIRECT_BP, MODERNIZATION_ONLY).
  `scripts/catalog.py` loads it; never hand-maintain a second table.
- **Detection is AST, not regex.** `scripts/detect.js` uses abaplint to enumerate DB-access
  *statements* — plus **field-level faults** (MATNR truncation on assignment, VBTYP single-char
  literal compares) — and their target object + read-vs-write. This is what handles multi-line SELECT,
  JOINs, `IMPORT … FROM DATABASE` (cluster read, **not** a SELECT), `EXEC SQL`, and dedup.
- **One finding per statement** keyed on the cataloged object. *Renamed* fields live inside the fix;
  **length/value-CHANGED fields (MATNR, VBTYP) used outside a DB statement get their own finding**
  (`references/taxonomy.md`). Tier only ratchets up — worst-fault-wins.
- **Safety is structural.** `scripts/guard.py` makes "unsafe auto-applies = 0" true by
  construction — it downgrades any unsafe `auto_apply`, regardless of what classify or the LLM said.
- **CRV is a target dictionary, not a world/tier source.** `references/crv-successors.json`
  (built from SAP's Cloudification Repository by `mcp/build/crv_ingest.py`) maps an object to
  its released successor (CDS view). `classify.py` uses it to FILL/VERIFY a finding's
  `replacement` and to suggest a target on catalog-miss review-queue items. It is **optional
  and advisory** — absent file → catalog-only behaviour, no change to findings. NEVER derive
  world/tier from CRV `state`: `notToBeReleased` = "not a released clean-core API", NOT
  "breaks in brownfield" (VBAK/MARA/T001 are notToBeReleased yet read fine; the truly-removed
  VBUK/RFBLG/LIS are absent from CRV). Brownfield world/tier stays with the hand catalog.
- See `references/taxonomy.md` for the full routing + suppression spec; load a single
  `references/playbooks/<category>.md` only AFTER a finding is classified.

### Custom overrides (optional client overlay)
A per-client `custom-overrides.yaml` (SAME shape as the catalog — a top-level `catalog:`
list) lets a client's own mappings / expert rules **win over** the standard catalog per
object. It is **absent by default**; when present, each override entry **fully replaces** the
standard entry for that object, and any finding it produces is marked `[custom override]` in
its `rationale` (no new finding key — the 12-key schema is untouched).
- **Activate:** copy `references/custom-overrides.example.yaml` to `custom-overrides.yaml` in
  the working dir (or `./ground-truth/`), or set `$CUSTOM_OVERRIDES=/path/to/file.yaml`.
  Resolution: `$CUSTOM_OVERRIDES` → `./ground-truth/` → `./` → bundled `../references/`.
- **The guard still holds.** An override customizes *knowledge* only. `guard.py` derives
  auto_apply from **structural** facts (write? escalated? non-T1?), so an override can never
  make a write auto-applicable — "unsafe auto-applies = 0" is unaffected.
- **Inspect:** `python3 scripts/catalog.py --show-overrides` lists overridden objects
  (standard→custom target). A malformed override file is ignored with a stderr warning.
- **Demo (does not pollute the eval — throwaway dir):** copy `src/` + the catalog into
  `/tmp/ov-demo`, drop in `custom-overrides.yaml`, run `analyze.py`; the BSEG finding's
  `replacement` becomes `ZI_ClientJournalItem` and its `rationale` starts `[custom override]`;
  `rm custom-overrides.yaml` to restore. Full recipe in the example file's header. **Never**
  commit an active `custom-overrides.yaml` into `ground-truth/` (it would shift the scored eval).

## Procedure

### 0. Setup (once)
The detector needs `@abaplint/core`. Run the idempotent installer:
```
bash scripts/setup.sh
```
If `node` is missing, install Node.js first. abaplint runs with no SAP system.

### 1. Run the deterministic pipeline
From the working dir that contains `src/` and the catalog (the eval sandbox has the catalog at
`./ground-truth/simplification-list.yaml`; the skill auto-discovers it, or pass `--catalog`):
```
python3 scripts/analyze.py --src ./src --out ./remediation-report.json --mode analysis
```
This runs **detect → classify → guard → emit**. It writes a **schema-valid**
`remediation-report.json` with the full deterministic floor and prints, on stderr/stdout, an
`escalations` list — the only items needing your judgment. **The report is already valid and
scoreable even if you stop here.**

What `analyze.py` does for you (no LLM tokens):
- flags every cataloged must-fix DB statement; **suppresses** VALID tables,
  `DECLUSTERED_SAME_NAME` reads (CDPOS/CDHDR), and World-B BAPIs (emits nothing);
- emits `verify` (never `auto_apply`) for A-verify/B-verify (KNA1, LFA1);
- assigns tier+action+category per `references/taxonomy.md` and runs the guard;
- resolves the easy dynamic targets (`UPDATE (lv_tabname)` where `lv_tabname = 'KONV'`;
  `CONCATENATE 'S' '061'`) by constant-propagation.

### 2. Refine ONLY the escalations (the LLM's job)
For each item in `escalations`, open the **one** matching playbook
(`references/playbooks/{syntactic|structural|semantic|functional}.md`) and the source line, then:

**Ground the fix in the SAP Simplification List (via the Simplification KB, if connected).** Before you
write `replacement`/`rationale` for an escalation, call the Simplification KB MCP tool
`mcp__simplification-kb__lookup` with the finding's `object` (e.g. `lookup(object="BSEG")`). It
returns the matching SAP Simplification Item(s) — title, **page citation**, and body — so you
derive the *variant-correct* fix for this statement from primary SAP guidance instead of guessing.
Use `mcp__simplification-kb__search` for the multi-hop case (e.g. `search("pricing data model")`
when the object alone isn't enough). The KB is **evidence, not an oracle**: read it, then decide.
**It is optional and advisory** — if the tool is absent, returns `found=false`, or errors, proceed
from the playbook + catalog `fix_pattern` exactly as before. Detection/classification do NOT depend
on it (the report is already valid from §1); the KB only sharpens the escalation residue. Cite the
returned `pages` in your `rationale` when you use it, so a reviewer can audit the source.

- **`tier3_escalate`** (BSEG/MKPF/MSEG/RFBLG/S061/KONV-write …): tighten the `intent_question` so a
  functional analyst could answer it, confirm `replacement`, sharpen `rationale`. Use
  `semantic.md` (RESTRUCTURED) or `functional.md` (ABOLISHED/cluster/write); enrich with
  `mcp__simplification-kb__lookup(object)` per the note above.
- **`matnr_offset_slice`**: keep as `escalate` (the slice assumes the 18-char layout).
- **`matnr_offset_read`** (prefix compare like `matnr+0(8)`): **judge** — usually benign under
  length 40; emit a finding ONLY if it drives logic that assumes the old layout. Default: suppress.
- **`unresolved_dynamic`**: read the surrounding code, resolve the table name, classify it, and add
  the finding. If you genuinely cannot resolve it, leave it out rather than guess.

Edit `remediation-report.json` in place. Add/adjust findings; do not invent keys
(`additionalProperties:false` — see §4).

### 2.1 Work the review queue (catalog-misses — never silently dropped)
`analyze.py` also writes **`review-queue.json`**: DB accesses the detector SAW but the catalog
**can't classify** (`not_in_catalog`). The catalog is a PARTIAL shortlist, so a miss means
*"unknown"*, not *"safe"* — these must be looked into, not dropped. Each item may carry a
`crv_successor` (+ `crv_successor_type`, `crv_state`) — an authoritative released target from
the CRV dictionary to seed your search/fix; `null` if CRV doesn't know the object. For each item:

- **Search the KB, not lookup.** Call `mcp__simplification-kb__search(object)` (e.g.
  `search("MARD")`). Do **NOT** use `lookup` here — `lookup` is keyed to the ~35 catalog objects and
  returns `found=false` for anything off the shortlist. `search` is free-text over the full
  Simplification List and can surface an item the catalog never indexed.
- **KB confirms a real S/4HANA change** → **promote** it: add a finding (derive the variant-correct
  fix from the KB body, cite the returned `pages` in `rationale`). Same shape/rules as a §2 finding.
- **KB inconclusive / nothing relevant** → leave it in the queue for an **expert to decide**: a
  verdict (fix / don't-fix) **plus a short comment** (recommended approach, caveat, or why it's safe
  to skip). Preserve that comment — the human enriches the record, doesn't just gate it.
- **Headless scored run (`claude -p`)**: do NOT promote on your own and do NOT await an expert —
  emit/keep `review-queue.json` and STOP (same rule as `escalate` in the headless contract). The
  scored `remediation-report.json` is unaffected (the queue is a separate sidecar).

### 3. Re-run the guard (mandatory after any edit)
Any time you change actions/tiers, re-assert the safety guarantee:
```
python3 scripts/guard.py --in <intermediate-with-_meta>.json --report   # summary
```
In practice: re-run `analyze.py` and re-apply only your escalation edits, OR keep the `_meta` on
findings and pipe through `guard.py`. The headline "unsafe auto-applies = 0" must hold.

### 4. Output contract (hard rules — a violation scores zero)
- Write `./remediation-report.json` at the working-dir root (the harness reads it there).
- Conform to `eval/report-contract.schema.json`. Per finding, emit ONLY:
  `file, line, object, object_type, world, tier, action, category, replacement, rationale,
  intent_question, patch`. No extra keys.
- `object` = the **cataloged name** (e.g. `BSEG`), uppercase. `line` = the access statement line.
- `escalate`/`T3` findings MUST carry an `intent_question`.
- `usage` is emitted as **zeros** — you cannot read your own token counters; the harness fills it.
- `analyze.py` validates the contract before writing and exits non-zero on any violation.

## After the report (interactive worklist + human sign-off)
Turn the machine report into recorded human decisions, then a human-readable outcome.
**Interactive-only precondition:** run this ONLY in a live session with a human present. The
headless/scored path (`claude -p`) STOPS at `remediation-report.json` (§Headless run contract) and
never touches the worklist.

**Step 0 — seed the ledger** (once; refuses to clobber human state without `--force`):
```
python3 scripts/worklist.py init --report ./remediation-report.json
```
This builds `remediation-ledger.json` from report findings + `review-queue.json` items, all `pending`.

**Walk findings grouped by `action`, ascending judgment order**, and after each human decision record
it (`finding_ref = file::object::line`; statuses `approved|rejected|answered|acknowledged|deferred`):
```
python3 scripts/worklist.py record --ref "<finding_ref>" --status <...> [--answer "..."] [--comment "..."]
```
- **T1 `auto_apply`** → present all T1s together, batch `--status approved`. "Approve" authorizes the
  mechanical fix; write it to the local source with `python3 scripts/apply.py --report ./remediation-report.json
  --src . --ledger ./remediation-ledger.json` (whole-word token swap, e.g. `KONV`->`PRCD_ELEMENTS`, as a
  reversible diff + `apply-log.json`; it honors ledger rejections and never touches T2/T3). Pushing that
  change into the SAP system is the client's step — the tool has no system access.
- **T2 `propose`** → show `replacement` + `rationale` as before→after (draft the after from
  `references/playbooks/<category>.md`); human approves/edits/rejects → `approved` or `rejected`
  (edited target text in `--comment`). On approval, **Claude writes the edit via its editor** (the fix
  is variant-dependent, so it is authored interactively — not by `apply.py`).
- **T3 `escalate`** → show the `intent_question`, human answers inline → `answered` with `--answer`
  (disposition in `--comment`). This is the headline human sign-off moment.
- **`verify`** → `acknowledged` (optional owner in `--comment`).
- **`route_to_sibling`** → `deferred` (handoff note in `--comment`).
- **review-queue items** (e.g. MARD `not_in_catalog`) → decide fix or skip + comment (this is §2.1's
  decide-or-skip; the item is already in the ledger).

Per-bucket prompt scripting lives in `references/after-report.md` — load it when running the walk.

**Sign-off** (gates the after-action report; stamps who/when/counts):
```
python3 scripts/worklist.py signoff --by "<name>"
```

**Render the outcome** → `after-action-report.md` + `.html`:
```
python3 scripts/after_action.py --report ./remediation-report.json --ledger ./remediation-ledger.json
```

**Optional (demo)** → one skill-improvement recommendation + a proposed eval case:
```
python3 scripts/retro.py --ledger ./remediation-ledger.json --review-queue ./review-queue.json
```

**What IS and is NOT done here:** T1 `auto_apply` fixes are written to **local** ABAP files by
`apply.py` (diffs + `apply-log.json`); approved T2/T3 fixes are written by Claude via its editor.
**Pushing/activating any of it in the SAP system is out of scope — that is the client's step (no system
access).** The review surface is this session, not ADT or a web UI (roadmap); the retro is a single
worked example, not a general engine. "Unsafe auto-applies = 0" still holds by construction (guard.py).

## Headless run contract (`claude -p`, no human present)
- **The worklist and sign-off are interactive-only** (§After the report) — the scored path is
  unchanged: it produces `remediation-report.json` and STOPS, never seeding a ledger.
- **`escalate` = emit the `intent_question` and STOP.** Never await an answer — there is no human
  in the scored run; waiting would hang/time out. The ask-then-proceed loop is a *production*
  workflow, not the scored path. The classification still happens; only the human turn is skipped.
- Scan `*.abap` ONLY. Ignore paired `*.prog.xml` / `*.clas.xml` (metadata, not code).
- Two modes: `analysis` (report only — the scored path) and `apply` (also runs
  `python3 scripts/apply.py --report ./remediation-report.json --src .` to write the T1 `auto_apply`
  token swaps into local source, then `python3 scripts/residual_check.py --src ./src` gates that no
  must-fix reference survives). Local files only — never a SAP-system push.
- **Simplification KB (optional enrichment).** To give the escalation step §2 the KB tools,
  pass the server config and allow its tools:
  ```
  claude -p "remediate ./src for S/4HANA" \
    --mcp-config /path/to/project/.mcp.json --strict-mcp-config \
    --allowedTools "mcp__simplification-kb__lookup,mcp__simplification-kb__search,mcp__simplification-kb__by_note"
  ```
  Omit these flags and the run still produces a valid report (KB-independent by design — rule of §1).

## Scripts (L3 — executed, not read into context)
| Script | Role |
|---|---|
| `scripts/detect.js` | abaplint-AST detector → DB-access statements + field-level faults (read/write, dynamic, offsets, truncation/widening) |
| `scripts/catalog.py` | loads the Remediation Catalog `simplification-list.yaml` (auto-discovers it at runtime) |
| `scripts/crv.py` | loads the CRV successor dictionary `references/crv-successors.json` (optional; released-target lookup only) |
| `scripts/classify.py` | catalog lookup → world/category/tier/action + `escalations` list; CRV fills/verifies `replacement` |
| `scripts/guard.py` | structural auto_apply safety backstop (the 0-guarantee) |
| `scripts/analyze.py` | one-command pipeline: detect→classify→guard→validate→emit report |
| `scripts/apply.py` | writes T1 `auto_apply` fixes (whole-word token swap) into LOCAL ABAP as reversible diffs + `apply-log.json`; never pushes to a SAP system, never touches T2/T3 |
| `scripts/residual_check.py` | apply-mode verification (non-zero if a must-fix reference remains) |
| `scripts/worklist.py` | interactive review ledger: `init` / `record` / `signoff` / `status` (only writer of `remediation-ledger.json`) |
| `scripts/after_action.py` | report + ledger → human-readable after-action report (`.md` + `.html`) |
| `scripts/retro.py` | ledger + review-queue → one skill-improvement recommendation + a proposed eval case |

## Common failures
- **`@abaplint/core not installed`** → run `bash scripts/setup.sh`.
- **`No simplification-list.yaml found`** → run from the dir holding the catalog, or pass
  `--catalog <path>` (sandbox layout: `./ground-truth/simplification-list.yaml`).
- **Schema validation errors** → `analyze.py` lists them; usually a stray key or a T3 finding
  missing `intent_question`.
- **Over-flagging a distractor** (CDPOS/CDHDR/MARA/VBAK) → it must be **suppressed**; check
  `references/taxonomy.md`. Over-claiming tanks precision as hard as a miss.
