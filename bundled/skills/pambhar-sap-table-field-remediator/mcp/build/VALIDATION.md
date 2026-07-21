# VALIDATION — sap-simplification-kb (adversarial)

**Validator:** adversarial reviewer (did not author the code). Every check below was *run*, not inferred.
**Date:** 2026-06-25
**Component:** `/Users/deep/Uni/ss2026/ai-coding/project/sap-simplification-kb/`
**Env:** `.venv/bin/python` = CPython 3.12.12, `fastmcp` 3.4.2, `pyyaml` present.
**Method:** real calls into `kb_impl` (criteria 1–3), real FastMCP `Client` over `StdioTransport` subprocess (criterion 4), grep of consumer scripts (criterion 5), real `claude` CLI headless run (criterion 6).

## Overall verdict: **SHIP — fit for purpose as Skill 3's KB layer.**
All 6 criteria PASS. Two non-blocking quality caveats (see Defects): KONV is correct only via item *body* (titles are misleading), and free-text `search()` ranking is weak on at least one query. Neither breaks the object-key lookup path that Skill 3 actually uses, and the report is produced without the KB at all (criterion 5).

---

## Criterion 1 — Index correctness (note-join). PASS

Command: `.venv/bin/python scratch_validate.py` → `from kb_impl import lookup, by_note, search`.
Every must-fix object resolved `found=True` and the expected topical item is present (object-key path ranks the right item first in all cases except the multi-item BP/KONV sets, where it is present in the set).

| Object | found | note_used | Expected item present? | Returned items (item_id, title, pages) |
|---|---|---|---|---|
| MATNR | ✓ | 2267140 | **YES** SI-3.22 first | SI-3.22 *Material Number Field Length Extension* `162-171`; + SI-49.9 *Supplier Workplace* `1140-1157` (noise) |
| VBUK | ✓ | 2198647 | **YES** SI-39.8 | SI-39.8 *SD Simplified Data Models* `991-994` |
| VBUP | ✓ | 2198647 | **YES** SI-39.8 | SI-39.8 `991-994` |
| GBSTK | ✓ | 2198647 | **YES** SI-39.8 | SI-39.8 `991-994` |
| BSEG | ✓ | 2270333 | **YES** SI-8.2 (+SI-2.35) | SI-2.35 *Removal of obsolete Data Modeler (SD11)* `91-92`; SI-8.2 *DATA MODEL CHANGES IN FIN* `239-247` |
| BUKRS | ✓ | 2270333 | **YES** | SI-2.35 `91-92`; SI-8.2 `239-247` |
| HKONT | ✓ | 2270333 | **YES** | SI-2.35 `91-92`; SI-8.2 `239-247` |
| BUZEI | ✓ | 2270333 | **YES** | SI-2.35 `91-92`; SI-8.2 `239-247` |
| RFBLG | ✓ | 2270333 | **YES** | SI-2.35 `91-92`; SI-8.2 `239-247` |
| MKPF | ✓ | 2206980 | **YES** SI-27.5 | SI-2.35 `91-92`; SI-27.5 *DATA MODEL IN INVENTORY MGMT (MMIM)* `634-644` |
| MSEG | ✓ | 2206980 | **YES** SI-27.5 | SI-2.35 `91-92`; SI-27.5 `634-644` |
| KONV | ✓ | 2220005 | **VIA BODY only** (see note) | SI-38.9 *Co-Deployment of SAP SRM* `960-979`; SI-39.9 *VBFA — Indirect Docflow Relationships* `994-1030` |
| S001 | ✓ | 2267463 | **YES** SI-29.4 | SI-29.4 *LIS in EAM* `718-721` |
| S061 | ✓ | 2267463 | **YES** SI-29.4 | SI-29.4 `718-721` |
| KNA1 | ✓ | 2265093 | **YES** SI-3.19 first | SI-3.19 *Business Partner Approach* `153-159`; +SI-3.7, SI-50.4, SI-59.7, SI-62.1 |
| LFA1 | ✓ | 2265093 | **YES** SI-3.19 first | same set as KNA1 |

### KONV deep-check (was the suspect)
`lookup("KONV", full=True)` body inspection:
- **SI-39.9** — title *"VBFA — Indirect Docflow Relationships"* (misleading), but BODY contains `PRCD_ELEMENTS` = **True**, "pricing" = **True**, SAP Note `2220005` = **True**. Pages `994-1030`.
- **SI-38.9** — title *"Co-Deployment of SAP SRM"* (misleading); body "pricing"=True, note 2220005=True, but `PRCD_ELEMENTS`=False.
- `search("pricing data model")` → **SI-39.9 ranks FIRST** (score 132). ✓

**Honest verdict on KONV: "topically adequate via body, NOT via title."** Both returned items have titles unrelated to pricing; an LLM that reads only titles would be misled, but the *bodies* (which `lookup` returns by default, `full=True`) carry the correct pricing / `PRCD_ELEMENTS` / Note 2220005 content, and free-text search resolves the correct item to the top. Skill 3's flow reads bodies, so this is acceptable — but it is the weakest link in the index.

## Criterion 2 — Page citations. PASS
Every found item carries a real `pages` range string (see table). Spot-checks per spec:
- MATNR → SI-3.22 `162-171` ✓
- BSEG → SI-8.2 `239-247`, SI-2.35 `91-92` ✓
No found item returned a null/empty `pages`.

## Criterion 3 — Graceful miss. PASS (no exceptions raised)
```
PCL2:       found=False  note_used=None
  msg: No Simplification item resolved for PCL2 (catalog SAP Note 2409530 for PCL2 is
       flagged UNVERIFIED and was not used for the join; catalog status = ABOLISHED)...
BKPF:       found=False  note_used=None
  msg: No Simplification item resolved for BKPF (no SAP Note is cataloged for BKPF;
       catalog status = VALID)... Weak object-name matches (verify, low confidence): ['SI-10.1'].
ZZ_NONSENSE:found=False  note_used=None
  msg: 'ZZ_NONSENSE' is not in the simplification catalog. No tracked S/4HANA
       simplification references it. Treat as not-affected...
```
- PCL2 → `found=false`, message explicitly flags the catalog note as **UNVERIFIED** ✓
- BKPF → `found=false`, **null note** ("no SAP Note is cataloged"), plus a low-confidence weak-match hint ✓
- ZZ_NONSENSE → `found=false`, **uncataloged** message ✓
- None raised. Each `message` is actionable ("treat as not-affected, or verify manually").

## Criterion 4 — Server runs over stdio. PASS
Command: `.venv/bin/python scratch_stdio.py` (cwd = package dir), `StdioTransport(command=".venv/bin/python", args=["server.py"])` via `from fastmcp.client.transports import StdioTransport`.

Transcript (real subprocess transport):
```
INFO  Starting MCP server 'simplification-kb' with transport 'stdio'
TOOLS: ['lookup', 'by_note', 'search']

lookup(BSEG) -> True 2270333
    SI-2.35 2.35 S4TWL - Removal of obsolete Data Modeler (SD11) content 91-92
    SI-8.2  8.2 S4TWL - DATA MODEL CHANGES IN FIN 239-247

by_note(2270333) -> [('SI-2.35', '91-92'), ('SI-8.2', '239-247')]

search(business partner) top -> [('SI-60.9','Retail Additionals'),
                                 ('SI-2.32','Business User Management'),
                                 ('SI-30.9','ANSI/ISA S95 Interface')]
```
All three tools enumerate and return real data across the process boundary. ✓
(Note the `search("business partner")` ranking — see Defect 2.)

## Criterion 5 — Consumer degradation. PASS
Skill 3 detection scripts live in
`sap-table-field-remediator/skills/sap-table-field-remediator/scripts/`
(`analyze.py`, `catalog.py`, `classify.py`, `guard.py`, `residual_check.py`, `detect.js`).

Grep evidence (zero hits):
```
grep -rniE "simplification.kb|import kb_impl|mcp__|fastmcp|by_note|simplification_kb" <scripts dir>
→ NO MATCHES (exit nonzero)
```
The detection/classification/guard pipeline has **no import of, and no runtime dependency on, this MCP server.** `remediation-report.json` is produced entirely without the KB; the KB only *enriches* fix derivation downstream. Degradation is therefore total-safe: KB down → Skill 3 still emits its report. ✓

## Criterion 6 — Headless (claude CLI). PASS (ran in this environment)
`which claude` → `/Users/deep/.local/bin/claude`. Ran:
```
claude -p "Use the simplification-kb tools to look up what changes for BSEG in S/4HANA
 and cite the page range" --mcp-config ./.mcp.json --strict-mcp-config
 --allowedTools "mcp__simplification-kb__lookup" --permission-mode acceptEdits
```
(`--strict-mcp-config` + project `.mcp.json` which points at the venv python + abs server.py path.)

The model **invoked the tool and got BSEG back correctly**: it cited **SI-8.2 "Data Model Changes in FIN", pp. 239–247, SAP Note 2270333** (the expected 239-247 range), correctly explained the ACDOCA/Universal Journal change, and — notably — **down-weighted the SI-2.35 noise hit** on its own ("low-relevance hit … not a real data-access concern for BSEG"). EXIT=0. The page-91-92 alternative was present but correctly deprioritised by the model. ✓

---

## Defects / caveats found (none blocking)
1. **Note-join over-returns (precision, not recall).** Several objects return extra items that share the same SAP Note but are topically secondary: MATNR→SI-49.9 (Supplier Workplace), KNA1/LFA1→4 extra items, and BSEG/BUKRS/.../MKPF/MSEG all carry SI-2.35 *"Removal of obsolete SD11 Data Modeler content"* (`91-92`) as a low-value first entry. The must-fix item is always present, but it is **not always first** (BSEG lists SI-2.35 before SI-8.2). The headless LLM handled this gracefully; still, ordering is by item-id, not relevance — an LLM reading only the first hit could anchor on the weaker item.
2. **`search()` ranking is weak on `business partner`.** Top-3 = SI-60.9 Retail Additionals, SI-2.32 Business User Management, SI-30.9 ANSI/ISA — the canonical SI-3.19 *Business Partner Approach* does **not** appear in the top hits. Cause: naive term-frequency scoring rewards long bodies that merely repeat the words. This does **not** affect Skill 3's primary path (object-key `lookup("KNA1")` correctly returns SI-3.19 first), but `search` as an exploratory fallback is unreliable for at least this query. `search("pricing data model")` did rank correctly, so it is query-dependent.
3. **KONV titles are misleading** (covered above): correct only because `lookup` returns bodies by default. If a future consumer ever switches to `full=False` and reasons over titles alone, KONV resolution degrades to misleading.

## Recommendation
Ship to Skill 3. The contract surface (3 tools over stdio), page citations, graceful misses, and consumer-independence all hold up under real execution. Track defects 1–2 as quality follow-ups (relevance-rank the note-join output; improve search scoring, e.g. length-normalisation or title boosting) — they are enhancements, not ship-blockers, because the object-key lookup path the consumer relies on is correct and the bodies carry the right evidence.

---
*Validation scripts used (`scratch_validate.py`, `scratch_stdio.py`) were temporary and removed after this report; no production code was modified.*
