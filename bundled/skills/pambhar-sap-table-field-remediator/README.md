# SAP Table & Field Remediator

A Claude Code **plugin** that scans custom ECC ABAP for table/field accesses that break in an
**S/4HANA brownfield conversion**, tiers each fix by how much human judgment it needs (T1/T2/T3),
and emits a machine-readable `remediation-report.json`. Detection is deterministic (abaplint AST +
the **Remediation Catalog**); the LLM does judgment only on the hard cases; a human signs off. Ships
a **page-cited Simplification KB** served over MCP.

> **Three names, kept distinct:** the **SAP Simplification List** is SAP's official ECC→S/4 change
> document (the upstream source). The **Remediation Catalog** (`simplification-list.yaml`) is *our*
> curated, per-engagement lookup keyed by table/field object — status, tier, target. The
> **Simplification KB** is SAP's document chunked + page-cited over MCP, queried by the LLM for
> evidence on hard cases.

## Install

```
claude plugin marketplace add pambhar-deepkumar/sap-table-field-remediator
claude plugin install sap-table-field-remediator@sap-remediator
```

One command set installs the skill **and** the `simplification-kb` MCP server — no path editing,
no venv. Prerequisites:

| Need | Why | Install |
|---|---|---|
| **Claude Code** | runs the plugin | — |
| **Node.js** ≥ 18 | the abaplint AST detector | https://nodejs.org |
| **uv** *(optional)* | runs the bundled KB server with no venv/pip | https://docs.astral.sh/uv |

`uv` is optional — the skill detects and tiers findings without the KB; the KB only enriches the
harder (T3) fixes with page-cited SAP evidence.

## Update

To pull a newer version into Claude Code, refresh the **marketplace first**, then update the plugin:

```
claude plugin marketplace update sap-remediator     # git-pulls the latest manifest
claude plugin install sap-table-field-remediator@sap-remediator   # re-installs the new version
```

Or interactively: `/plugin` → **Marketplaces** → update `sap-remediator` → then update the plugin.
A fresh `claude` session picks up the new version; an already-running session keeps the one it loaded
at startup.

> ⚠️ **Updates are version-gated, not commit-gated.** `claude plugin update` compares the `version`
> in `.claude-plugin/plugin.json`, **not** the git commit. If you push code changes but leave the
> version unchanged, `/plugin` reports *"already at the latest version"* and consumers silently keep
> the **old** code. **Maintainers: bump `version` in `.claude-plugin/plugin.json` on every release**
> (even docs/script-only changes), or the update won't propagate. The installed cache lives at
> `~/.claude/plugins/cache/sap-remediator/sap-table-field-remediator/<version>/` — confirm the active
> version there if a change isn't showing up.

## Try it

In Claude Code, with no code of your own:

> *"Run the SAP Table & Field Remediator on the bundled example."*

It scans `examples/zdemo_s4_check.abap` and produces a tiered report. Then point it at your code:

> *"Remediate the ABAP in `./src` for an S/4HANA brownfield conversion."*

Full walkthrough: **[QUICKSTART.md](QUICKSTART.md)**.

## What it does

1. **Detect** every DB-access statement (SELECT/JOIN/FOR ALL ENTRIES, `IMPORT … FROM DATABASE`,
   `EXEC SQL`) via abaplint's AST — not regex — **plus field-level faults** outside DB statements
   (MATNR truncation on assignment, VBTYP single-char comparisons).
2. **Classify & tier** each finding: T1 mechanical (`auto_apply`), T2 bounded (`propose`), T3
   intent-needed (`escalate`). A structural guard guarantees **0 unsafe auto-applies, by construction**.
3. **Derive** the variant-correct fix for T3 cases from the bundled Simplification KB
   (page-cited), reached over MCP — evidence, not an oracle.
4. **Emit** a schema-valid `remediation-report.json`. A human reviews and signs off.

### Custom overrides (client-specific mappings)

The Remediation Catalog ships SAP's standard mappings. To make the tool defer to your own rules for
specific objects, add a custom overrides file — it wins over the standard catalog per object; anything
you don't list falls through to the standard catalog.

1. Copy the template: `cp skills/sap-table-field-remediator/references/custom-overrides.example.yaml custom-overrides.yaml`
   (put it in your working dir, or point `$CUSTOM_OVERRIDES` at it).
2. Edit it. Each entry has the same shape as a catalog entry (`object`, `status`, `world`,
   `baseline_tier`, `s4_replacement`/`cds_view`); an entry **fully replaces** the standard entry for that object.
3. Run the skill as usual (`python3 scripts/analyze.py --src ./src`). Findings that used your override are
   tagged `[custom override]` in the rationale.
4. Check what's active any time: `python3 scripts/catalog.py --show-overrides`.

The safety guard still applies — an override changes the *mapping*, it cannot make an unsafe change
auto-apply (a write is still escalated).

### Cloudification Repo target enrichment (CRV)

The **Cloudification Repo** (SAP's official object→successor map, internally *CRV*) is a **target
verifier**, not a decision source. It confirms or flags the catalog's fix *target*, fills a gap when
the catalog leaves the target open, and suggests a target on a catalog miss. Tables only (**262**
objects). It **never** sets the world or tier — the Remediation Catalog stays authoritative; CRV only
touches the `replacement`. Built and enabled by default (`references/crv-successors.json`).

**This release (v0.3.0)** adds three things on top of detection + tiering: local **apply** of T1 fixes
(`apply.py`), **custom overrides** (client mappings win), and **Cloudification Repo (CRV)** target
enrichment.

## Evaluation

Blind-run against a synthetic ground-truth corpus (18 abapGit objects, 31 labeled findings across
SD/MM/FI). The skill saw only the code + the public Remediation Catalog; the scorer ran outside the sandbox
against a secret answer key it never exposed to the skill. Single run, `claude-opus-4-8`, analysis
mode, 2026-07-02 (label `v2-2026-07-02`).

| Metric | Result |
|---|---|
| Detection F1 | **97.3%** (precision 94.7% · recall 100%, 18/18) |
| Tier accuracy | **100%** (18/18) |
| Unsafe auto-applies | **0** (guaranteed by construction) |
| Distractor over-claims | **0 / 7** (0 / 5 on clean negatives) |
| Correct-replacement rate | 94.4% (17/18) |
| Cost / run | **$2.02** (~$0.11 per correct finding · ~4.6 min · 35 turns) |

Full scorecard: [`eval/scorecard-v2-2026-07-02.md`](eval/scorecard-v2-2026-07-02.md).

**Caveats (read before quoting):** one spurious over-claim (PCL2) remains — it accounts for the 94.7%
precision. Tier accuracy is perfect but the easy tiers still rest on a thin base (T3 is well-covered).
Single run, so cost is a point estimate. Supersedes the 2026-06-27 `opus48-v1` run (F1 90.9% /
recall 15-of-17), which predated field-level detection.

## How it's packaged

One repo = the skill + the KB MCP server + the plugin/marketplace manifest:

```
.claude-plugin/         marketplace.json + plugin.json
.mcp.json               launches the KB server via `uv run`
skills/sap-table-field-remediator/   the skill (SKILL.md + scripts/references)
mcp/                    the KB server (server.py + 429 page-cited chunks)
examples/               a demo ABAP program for zero-setup trials
```

## Project context

Part of a TUM × Deloitte research project (Summer 2026): *AI-Powered SAP Custom Code Analyzer*.
Skill 3 of 6 (Table & Field Remediator). Built entirely from **public** SAP material + **synthetic**
sample data.

## Contributing

See `CONTRIBUTING.md` for the PR flow. `CLAUDE.md` documents the skill-authoring spec followed in
`skills/sap-table-field-remediator/`.
