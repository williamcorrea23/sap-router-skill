# SAP Simplification-List Knowledge Base + MCP Server

Shared knowledge layer over SAP's **S/4HANA Simplification List**, exposed as a local
**MCP server** (FastMCP, stdio). Any of the Custom Code Analyzer skills can ask *"what
changes for object X in S/4HANA?"* and get the relevant, **page-cited** Simplification-List
item back. Skill 3 (Table & Field Remediator) is the first consumer.

This is a **harness, not an oracle.** The server returns the relevant SAP guidance + page
citation; the consuming LLM reads it and derives the variant-correct fix. The server never
asserts "the answer is X."

## Architecture (three layers — kept separate)

```
 consumer skills ──calls──▶  server.py  [ MCP TOOLS ]   ← only public surface (stable contract)
                                  │
                             kb_impl.py  [ impl ]        ← private, swappable (note-join today)
                                  │
                             common/     [ data ]        ← per-item .md chunks + index.json + catalog
```

**Rule:** consumers call the MCP tools and nothing else. The chunk format and the lookup
method (SAP-Note join over markdown) are private, swappable details — we can later move to
SQLite or vectors behind the same tool contract without any consumer changing.

## Layout

```
sap-simplification-kb/
├── server.py             # FastMCP server — thin @mcp.tool wrappers (the public contract)
├── kb_impl.py            # private impl: lookup / by_note / search (no MCP imports)
├── build_index.py        # builds common/index.json via the SAP-Note join
├── pyproject.toml        # deps: fastmcp, pyyaml  (+ [build] extra: docling)
├── common/
│   ├── items/*.md        # 429 per-item chunks (frontmatter: item_id,title,pages,sap_notes,…)
│   ├── index.json        # note-join index (object→items, note→items, scan, catalog)
│   └── kb-index-catalog.yaml   # the public catalog (the join-key source)
├── build/                # how the chunk store is reproduced from the PDF (run rarely)
│   ├── convert_full.py   # docling: PDF → DoclingDocument JSON (accurate tables, no-OCR)
│   └── chunk.py          # JSON → per-item .md chunks
├── README.md
└── VALIDATION.md         # commands run + outputs (acceptance evidence)
```

## The tools (the contract the LLM sees)

| Tool | Use it for | Returns |
|---|---|---|
| `lookup(object, full=True)` | exact object key (table/field/FM) → its Simplification item(s) | `{object, found, note_used, items:[{item_id,title,pages,sap_notes,components,body?}], message}` |
| `by_note(note)` | pivot from a 7-digit SAP Note → items citing it | list of item metadata |
| `search(query, limit=5)` | exploratory / multi-hop, no exact key | ranked `{item_id,title,pages,score,snippet}` |

A **miss is data, not an error**: `lookup` returns `found=false` + an actionable message
(treat as not-affected / verify). Consumers degrade gracefully — detection never depends on
this server.

### How lookup resolves (the precision decision)

`object` → catalog `sap_note` → items citing that note. The **SAP-Note join** is the primary,
high-precision path (an object-name scan is noisy: `KONV` matched an unrelated "VBFA Docflow"
item). Object-name scan is kept only as a *labeled secondary hint* (`weak_matches`) for objects
whose catalog note is missing/unverified (e.g. `PCL2`).

## Setup

```bash
cd sap-simplification-kb
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python fastmcp pyyaml
```

### Rebuild the index (after editing the catalog or chunks)

```bash
.venv/bin/python build_index.py          # writes common/index.json
```

### Rebuild the chunk store from the PDF (rare — ~18 min, needs docling)

```bash
uv pip install --python .venv/bin/python docling
.venv/bin/python build/convert_full.py    # PDF → full.json  (intermediate, not committed)
.venv/bin/python build/chunk.py full.json --out common
.venv/bin/python build_index.py
```

### Rebuild the CRV successor dictionary (Skill-3 target enrichment)

`crv_ingest.py` distils SAP's **Cloudification Repository** (open JSON, Apache-2.0,
`github.com/SAP/abap-atc-cr-cv-s4hc`) into `skills/sap-table-field-remediator/references/crv-successors.json`
— an object→released-successor (CDS view) lookup that `classify.py` uses to fill/verify a
finding's `replacement` and to seed a target on catalog-miss review-queue items.

**Target dictionary ONLY.** CRV `state` is clean-core API readiness, NOT brownfield
breakage — never derive world/tier from it (see the script header).

#### What the CRV `state` values mean

CRV states are **clean-core / ABAP Cloud API-governance** labels — "are you allowed to use
this object in released ABAP Cloud code?" — NOT "does the object still physically exist / work
after a brownfield conversion?"

| State | Meaning |
|---|---|
| `released` | SAP has published this object as an official, stable **public API**. You may use it in ABAP Cloud / clean-core code. These are usually CDS views (e.g. `I_JournalEntry`). |
| `notToBeReleased` | SAP will **not** release this object as an API. Do not use it in clean-core code — use its `successor` instead. **Not the same as "removed":** most raw tables (e.g. `BKPF`, `MARA`) still exist and a classic `SELECT` still works after a brownfield conversion; SAP simply steers new code to the successor. |
| `notToBeReleasedStable` | Same as `notToBeReleased`, but the object is not expected to change soon (stable). |
| `deprecated` | On its way out of use. |

**Analogy.** `released` = "this product is on the shelf, warranted — use it."
`notToBeReleased` = "we no longer sell this; buy the newer model instead" — the old one may
still work at home, but the store won't recommend it for new work.

**Why this matters for us.** `notToBeReleased` ≠ "breaks in brownfield". `MARA`/`VBAK` are
`notToBeReleased` yet still read fine on-stack, and the tables that truly break (`VBUK`,
`RFBLG`, LIS) are **absent** from CRV. So CRV answers *"is this a clean-core API?"* while our
catalog answers *"does this break in the conversion?"* — two different questions. That is why
CRV feeds only the **target** (successor), never the world/tier decision.

```bash
# 1. fetch the PCE release-info file (pick the release you target)
curl -sSLo objectReleaseInfo_PCELatest.json \
  https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfo_PCELatest.json
# 2. rebuild the dictionary (add --hand <catalog.yaml> for a coverage report)
python3 crv_ingest.py --crv objectReleaseInfo_PCELatest.json \
  --out ../../skills/sap-table-field-remediator/references/crv-successors.json --types TABL
```

## Register with Claude Code

**Project scope** (writes/uses `.mcp.json` at the project root — already present):

```bash
claude mcp add --transport stdio simplification-kb -- \
  /ABS/PATH/sap-simplification-kb/.venv/bin/python \
  /ABS/PATH/sap-simplification-kb/server.py
```

Then open `claude` and run `/mcp` — `simplification-kb` should show **connected** with tools
`mcp__simplification-kb__lookup`, `…__by_note`, `…__search`.

**Headless** (`claude -p`, e.g. the scored eval run):

```bash
claude -p "look up what changes for BSEG in S/4HANA and cite the page" \
  --mcp-config /ABS/PATH/project/.mcp.json --strict-mcp-config \
  --allowedTools "mcp__simplification-kb__lookup,mcp__simplification-kb__search,mcp__simplification-kb__by_note"
```

> `.mcp.json` uses **absolute, machine-local paths**. Regenerate it if the repo moves.

## Quick check

```bash
.venv/bin/python -c "import kb_impl, json; print(json.dumps({k:v for k,v in kb_impl.lookup('BSEG',full=False).items()}, indent=1))"
```

See `VALIDATION.md` for the full acceptance run.
