# Quickstart — SAP Table & Field Remediator

Detect custom ABAP that breaks in an S/4HANA brownfield conversion, tier each fix by how
much human judgment it needs, and get a machine-readable `remediation-report.json`. A
page-cited Simplification KB rides along over MCP.

## 1. Prerequisites (one-time)

| Need | Why | Install |
|---|---|---|
| **Claude Code** | runs the skill | you already have it |
| **Node.js** ≥ 18 | the abaplint AST detector | https://nodejs.org (or `brew install node`) |
| **uv** *(optional)* | runs the bundled KB server with **no venv/pip** | https://docs.astral.sh/uv (`curl -LsSf https://astral.sh/uv/install.sh \| sh`) |

uv is optional: the skill detects and tiers findings **without** the KB. The KB only
enriches the harder (T3) fixes with page-cited SAP evidence. No uv → it degrades quietly.

## 2. Install (one command)

```
/plugin marketplace add pambhar-deepkumar/sap-table-field-remediator
/plugin install sap-table-field-remediator@sap-remediator
```

That installs the **skill + the `simplification-kb` MCP server** in one shot — no path
editing, no `claude mcp add`. The server self-bootstraps its Python deps via `uv` on first
use, so there is no venv to manage.

## 3. Try it (no code of your own needed)

Open Claude Code and just ask:

> **"Run the SAP Table & Field Remediator on the bundled example and show me the report."**

It will scan `examples/zdemo_s4_check.abap` and produce a `remediation-report.json` with one
finding per problematic statement — BSEG → I_JournalEntryItem (T3), VBUK → I_SalesOrder (T2),
KONV pricing (T3), MATNR length (T1) — while correctly **suppressing** the benign `MARA` read.

For a T3 finding, the skill calls the KB: `lookup("BSEG")` → item **SI-8.2 "Data Model
Changes in FIN", pp. 239–247** — page-cited evidence it reads before proposing the fix (read via
the released view `I_JournalEntryItem`). The Remediation Catalog **locates**; the model **derives** the fix; a human signs off.

## 4. Use it on your own code

Point Claude at a directory of `*.abap`:

> **"Remediate the ABAP in `./src` for an S/4HANA brownfield conversion."**

The first run installs the detector's `@abaplint/core` automatically (needs Node). Output is
`remediation-report.json` at your working-dir root.

## What's inside the plugin

```
sap-table-field-remediator/
├── skills/sap-table-field-remediator/   the skill (SKILL.md + detector/classifier/guard)
├── mcp/                                  the KB server (server.py + 429 page-cited chunks)
├── examples/zdemo_s4_check.abap          the zero-setup demo above
└── .mcp.json                             launches the KB server via `uv run`
```

The KB is reached **only** through the MCP tools (`lookup` · `by_note` · `search`) — the
chunk store and the note-join are private, swappable internals.
