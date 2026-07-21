#!/usr/bin/env python3
"""retro.py — the skill's self-improvement step (single worked example).

Closes the learning loop for ONE known gap: a review-queue item (a data access the
catalog could not classify, `not_in_catalog`) that a human then judged a real
must-fix in the review ledger. That human-vs-tool delta is exactly the signal the
deterministic floor missed — so retro turns it into two concrete, paste-ready
improvements:

  1. a human-readable recommendation (Markdown + self-contained HTML), and
  2. a `proposed-eval-case.yaml` stub — a findings.yaml entry that, once locked into
     ground truth, regression-locks the gap so it can never silently reappear.

SCOPE — this is a SINGLE WORKED EXAMPLE, not a general retro engine. It finds the
first review-queue/not_in_catalog item the human marked as a fix (the MARD case in
the synthetic corpus) and stops. A general "mine every human-vs-tool delta" engine
is roadmap. See working-notes/DECISIONS.md.

Read-only over its inputs. It NEVER edits ground truth (findings.yaml /
simplification-list.yaml) — it only emits a stub for a human to paste. It never
edits ABAP and never writes the ledger (only worklist.py does).

Identity: ledger decisions are keyed by finding_ref = f"{file}::{object}::{line}"
(same key worklist.py / after_action.py use). We match a review-queue item to its
ledger decision by that ref.

Usage:
  python3 retro.py --ledger ./remediation-ledger.json \
                   --review-queue ./review-queue.json [--out-dir DIR]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from datetime import datetime, timezone

GENERATOR = "retro.py 0.1"

# A ledger status counts as a "fix" verdict (human says: this IS a real must-fix).
# Robust to either vocabulary worklist.py records for an accepted item.
FIX_STATUSES = ("approved", "answered")

# Src-relative convention used by ground-truth/findings.yaml. review-queue.json paths
# are repo-root-relative (they carry this prefix); strip it so the emitted stub matches
# the findings.yaml `actual_file` convention (scoring keys on basename either way).
CORPUS_PREFIX = "synthetic-sap-codebase/"


# --------------------------------------------------------------------------- #
# Helpers (rendering idiom copied from after_action.py — same house style)
# --------------------------------------------------------------------------- #
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def finding_ref(file: str, object_: str, line) -> str:
    return f"{file}::{object_}::{line}"


def basename_line(file: str, line) -> str:
    return f"{os.path.basename(file)}:{line}"


def src_relative(path: str) -> str:
    """Normalise a review-queue path to the findings.yaml `actual_file` convention."""
    p = path or ""
    # Real prefix strips (NOT lstrip char-sets, which would gnaw leading '.'/'/'):
    p = p[2:] if p.startswith("./") else p
    p = p[len(CORPUS_PREFIX):] if p.startswith(CORPUS_PREFIX) else p
    return p


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


def md_cell(x) -> str:
    """Escape a value for a Markdown table cell (same idiom as after_action.py ~L236)."""
    return str(x if x is not None else "").replace("|", "\\|").replace("\n", " ")


# --------------------------------------------------------------------------- #
# The one thing this script does: find the human-vs-tool delta
# --------------------------------------------------------------------------- #
def find_delta(review_queue: dict, ledger: dict) -> dict | None:
    """Return the FIRST review-queue/not_in_catalog item the human marked as a fix.

    A delta = a review-queue item whose matching ledger decision has a fix-verdict
    status (approved/answered) with a human comment. Returns a plain dict describing
    the delta, or None if there's nothing to learn from.
    """
    decisions = ledger.get("decisions", [])
    dec_by_ref = {d.get("finding_ref"): d for d in decisions}

    # Visibility guard: track promoted catalog-misses that lacked a real verdict comment,
    # so we can hint (fix 6) rather than silently emit "no deltas".
    promoted_without_comment = False

    for item in review_queue.get("items", []):
        # Scope: only catalog-miss items are the "tool left it unclassified" signal.
        if item.get("reason") != "not_in_catalog":
            continue

        # SINGLE WORKED EXAMPLE: render_eval_case emits a MARD-specific stub (F-MM-11,
        # ZMM_R_MATNR_SPLIT, select_single, MARD expected_fix). A non-MARD delta would get
        # MARD's stub — a wrong paste-ready artifact — so scope the delta to MARD only.
        # General delta-mining (per-object stubs) is roadmap. See working-notes/DECISIONS.md.
        if item.get("object") != "MARD":
            continue

        ref = finding_ref(item["file"], item["object"], item["line"])
        dec = dec_by_ref.get(ref)
        if dec is None:
            continue

        status = dec.get("status", "")
        note = (dec.get("human_answer") or dec.get("comment") or "").strip()
        # A fix verdict: an accepted/answered decision that carries a human comment.
        # (Robust: require a real note so a bare status flip isn't read as a verdict.)
        if status in FIX_STATUSES and note and not note.startswith("queue"):
            return {
                "ref": ref,
                "file": item["file"],
                "line": item["line"],
                "object": item["object"],
                "object_type": item.get("object_type", "table"),
                "access": item.get("access", "read"),
                "reason": item.get("reason"),
                "human_status": status,
                "human_note": note,
                "decided_by": dec.get("decided_by", ""),
            }

        # Promoted (approved/answered) but no real verdict comment to build a fix from.
        if status in FIX_STATUSES and (not note or note.startswith("queue")):
            promoted_without_comment = True

    if promoted_without_comment:
        sys.stderr.write(
            "[retro] found promoted queue items but none carried a --comment verdict; "
            "add one to generate a recommendation.\n"
        )
    return None


# --------------------------------------------------------------------------- #
# Eval-case stub (paste-ready findings.yaml entry) — retro does NOT edit gt
# --------------------------------------------------------------------------- #
def render_eval_case(delta: dict) -> str:
    """Emit a findings.yaml-shaped stub for the delta object (MARD).

    Fields mirror the real schema. Tier/fix are seeded from the human verdict; a human
    tightens them before locking into ground truth. retro NEVER writes ground truth.
    """
    actual_file = src_relative(delta["file"])
    obj = delta["object"]
    # Fold newlines to a single line so the note stays a valid one-line `#` YAML comment.
    note = " ".join(delta["human_note"].split())
    L = []
    L.append("# proposed-eval-case.yaml — PASTE-READY findings.yaml entry (a STUB).")
    L.append(f"# Emitted by {GENERATOR} on {now_iso()} from the human-vs-tool delta:")
    L.append(f"#   {obj} @ {basename_line(delta['file'], delta['line'])} was a review-queue")
    L.append(f"#   ({delta['reason']}) item the human marked '{delta['human_status']}' = must-fix.")
    L.append("#")
    L.append("# retro.py does NOT edit ground truth. A human reviews this stub, tightens")
    L.append("# expected_tier / expected_fix, then appends it to ground-truth/findings.yaml to")
    L.append("# regression-lock the gap. SINGLE WORKED EXAMPLE — a general engine is roadmap.")
    L.append("")
    L.append(f"  - id: F-MM-11")
    L.append(f"    verified: true")
    L.append(f"    actual_file: {actual_file}")
    L.append(f"    line: {delta['line']}")
    L.append(f"    module: MM")
    L.append(f"    package: ZMM")
    L.append(f"    planned_file: {actual_file}")
    L.append(f"    object_type: report")
    L.append(f"    object_name: ZMM_R_MATNR_SPLIT")
    L.append(f"    object: {obj}")
    L.append(f"    sql_pattern: select_single       # SELECT SINGLE labst FROM mard")
    L.append(f"    world: A")
    L.append(f"    baseline_tier: T3")
    L.append(f"    expected_tier: T3")
    L.append(f"    must_escalate: false")
    L.append(f'    expected_fix: "Stock fields (LABST etc.) no longer persisted on MARD in S/4; '
             f'read on-the-fly via MATDOC / I_MaterialStock (CDS). Verify aggregation intent."')
    L.append(f'    intent_question: "Does this read need the live current stock (recomputed in S/4) '
             f'or a historical snapshot? That decides the MATDOC/CDS read shape."')
    L.append(f"    is_negative: false")
    L.append(f"    is_distractor: false")
    L.append(f"    # human verdict that seeded this case (from the ledger):")
    L.append(f"    #   status={delta['human_status']} by={delta['decided_by'] or '?'}")
    L.append(f"    #   note: {note}")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Recommendation — Markdown
# --------------------------------------------------------------------------- #
def render_markdown(delta: dict) -> str:
    loc = basename_line(delta["file"], delta["line"])
    obj = delta["object"]
    L = []
    L.append("# Retro Recommendation — SAP Table & Field Remediation")
    L.append("")
    L.append("> **Single worked example.** This closes the learning loop for ONE known gap "
             f"(`{obj}`). A general retro engine that mines every human-vs-tool delta is "
             "**roadmap**, not built here.")
    L.append("")
    L.append(f"_Generated by {GENERATOR} at `{now_iso()}`._")
    L.append("")

    L.append("## 1. The delta (human vs tool)")
    L.append("")
    L.append("| | |")
    L.append("|---|---|")
    L.append(f"| Object | `{obj}` ({delta['object_type']}, {delta['access']}) |")
    L.append(f"| Location | `{loc}` |")
    L.append(f"| Tool outcome | **left unclassified** — routed to review-queue "
             f"(`{delta['reason']}`); no tier, no fix |")
    L.append(f"| Human verdict | **must-fix** (ledger status `{delta['human_status']}`"
             + (f", by {delta['decided_by']}" if delta['decided_by'] else "") + ") |")
    L.append(f"| Human note | {md_cell(delta['human_note'])} |")
    L.append("")

    L.append("## 2. The gap")
    L.append("")
    L.append(f"The deterministic floor never flagged `{obj}` because it is **missing from the "
             "Remediation Catalog** (`simplification-list.yaml`). With no catalog row, the "
             "classifier cannot tier or route it, so it falls to the review-queue as "
             "`not_in_catalog`. The tool was silent exactly where a human found a real problem — "
             "the catalog's coverage, not the detector, is the miss.")
    L.append("")

    L.append("## 3. Recommendation")
    L.append("")
    L.append(f"1. **Add `{obj}` to the Remediation Catalog** so the deterministic floor flags it "
             "on the next run (status `RESTRUCTURED`, `s4_replacement: MATDOC`, "
             "`cds_view: I_MaterialStock`, `baseline_tier: T3`). This turns a silent miss into a "
             "routed, tiered finding.")
    L.append(f"2. **Lock a matching eval case** — append the emitted `proposed-eval-case.yaml` stub "
             "to `ground-truth/findings.yaml` so the gap is regression-locked: recall will now "
             f"*measure* whether `{obj}` is caught, and can never silently reopen.")
    L.append("")
    L.append("The order matters: add the eval case first and recall **drops** (a must-fix the "
             "current report misses); add the catalog row and re-run, and recall **recovers** "
             "(the miss becomes a true positive). That drop-then-recover is the proof the loop "
             "closed.")
    L.append("")

    L.append("## 4. Artifacts emitted by this run")
    L.append("")
    L.append("- `retro-recommendation.md` / `retro-recommendation.html` — this recommendation.")
    L.append("- `proposed-eval-case.yaml` — paste-ready `findings.yaml` stub (a human tightens "
             "`expected_tier` / `expected_fix` before locking it in).")
    L.append("")
    L.append("> retro.py **only emits the stub** — it does **not** edit ground truth. The "
             "catalog + findings.yaml edits are a deliberate human step.")
    L.append("")
    L.append(f"_Generated by {GENERATOR}._")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Recommendation — HTML (self-contained, site palette copied from after_action.py)
# --------------------------------------------------------------------------- #
STYLE = """
:root{
  --ink:#0f172a; --ink-soft:#334155; --muted:#64748b; --line:#e2e8f0;
  --line-soft:#f1f5f9; --bg:#f8fafc; --bg-tint:#f1f5f9; --card:#ffffff;
  --accent:#4f46e5; --accent-700:#4338ca; --accent-soft:#eef2ff;
  --t1:#059669; --t1-bg:#d1fae5; --t2:#d97706; --t2-bg:#fef3c7;
  --t3:#e11d48; --t3-bg:#ffe4e6;
  --good:#047857; --good-bg:#d1fae5; --warn:#b91c1c; --warn-bg:#fee2e2; --human:#b91c1c;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box;}
body{margin:0;font-family:var(--sans);font-size:15px;line-height:1.6;
  color:var(--ink-soft);background:var(--bg);}
.wrap{width:min(1040px,92vw);margin:0 auto;padding:2.5rem 0 4rem;}
h1{color:var(--ink);font-size:1.9rem;margin:0 0 .3rem;letter-spacing:-.02em;}
h2{color:var(--ink);font-size:1.25rem;margin:2.2rem 0 .8rem;letter-spacing:-.01em;
  padding-bottom:.35rem;border-bottom:2px solid var(--line);}
.sub{color:var(--muted);margin:0 0 1.5rem;}
code,.mono{font-family:var(--mono);font-size:.85em;background:var(--accent-soft);
  color:var(--accent-700);padding:.1em .4em;border-radius:6px;}
.scope{background:var(--accent-soft);border:1px solid var(--line);
  border-left:4px solid var(--accent);border-radius:10px;padding:.9rem 1.2rem;margin:0 0 1.4rem;}
table{width:100%;border-collapse:collapse;background:var(--card);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;
  box-shadow:0 1px 3px rgba(15,23,42,.06);margin:.4rem 0 1rem;font-size:.9rem;}
th,td{text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--line-soft);
  vertical-align:top;}
th{background:var(--bg-tint);color:var(--ink);font-weight:600;
  font-size:.78rem;text-transform:uppercase;letter-spacing:.03em;}
tr:last-child td{border-bottom:none;}
.pill{display:inline-block;padding:.1em .55em;border-radius:999px;
  font-size:.78rem;font-weight:600;white-space:nowrap;}
.t3{background:var(--t3-bg);color:var(--t3);}
.tool{color:var(--muted);font-weight:600;}
.human{color:var(--human);font-weight:700;}
.hl{font-weight:700;color:var(--ink);}
ol li,ul li{margin:.35rem 0;}
.note{background:var(--warn-bg);border:1px solid var(--warn);color:var(--human);
  border-radius:10px;padding:.8rem 1.1rem;margin:1rem 0;}
footer{margin-top:2.5rem;color:var(--muted);font-size:.8rem;}
"""


def render_html(delta: dict) -> str:
    loc = basename_line(delta["file"], delta["line"])
    obj = delta["object"]
    P = []
    P.append("<!doctype html>")
    P.append('<html lang="en"><head><meta charset="utf-8">')
    P.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    P.append("<title>Retro Recommendation — SAP Table &amp; Field Remediation</title>")
    P.append(f"<style>{STYLE}</style>")
    P.append("</head><body><div class='wrap'>")

    P.append("<h1>Retro Recommendation</h1>")
    P.append("<p class='sub'>SAP Table &amp; Field Remediation — self-improvement step</p>")
    P.append(f"<div class='scope'><strong>Single worked example.</strong> This closes the "
             f"learning loop for ONE known gap (<code>{esc(obj)}</code>). A general retro engine "
             "that mines every human-vs-tool delta is <strong>roadmap</strong>, not built here.</div>")

    # 1. delta
    P.append("<h2>1. The delta (human vs tool)</h2>")
    P.append("<table><tbody>")
    P.append(f"<tr><th>Object</th><td><code>{esc(obj)}</code> "
             f"({esc(delta['object_type'])}, {esc(delta['access'])})</td></tr>")
    P.append(f"<tr><th>Location</th><td class='mono'>{esc(loc)}</td></tr>")
    P.append(f"<tr><th>Tool outcome</th><td><span class='tool'>left unclassified</span> — routed "
             f"to review-queue (<code>{esc(delta['reason'])}</code>); no tier, no fix</td></tr>")
    who = f", by {esc(delta['decided_by'])}" if delta['decided_by'] else ""
    P.append(f"<tr><th>Human verdict</th><td><span class='human'>must-fix</span> "
             f"(ledger status <code>{esc(delta['human_status'])}</code>{who})</td></tr>")
    P.append(f"<tr><th>Human note</th><td>{esc(delta['human_note'])}</td></tr>")
    P.append("</tbody></table>")

    # 2. gap
    P.append("<h2>2. The gap</h2>")
    P.append(f"<p>The deterministic floor never flagged <code>{esc(obj)}</code> because it is "
             "<strong>missing from the Remediation Catalog</strong> "
             "(<code>simplification-list.yaml</code>). With no catalog row the classifier cannot "
             "tier or route it, so it falls to the review-queue as <code>not_in_catalog</code>. "
             "The tool was silent exactly where a human found a real problem — the catalog's "
             "coverage, not the detector, is the miss.</p>")

    # 3. recommendation
    P.append("<h2>3. Recommendation</h2>")
    P.append("<ol>")
    P.append(f"<li><strong>Add <code>{esc(obj)}</code> to the Remediation Catalog</strong> so the "
             "deterministic floor flags it on the next run (status <code>RESTRUCTURED</code>, "
             "<code>s4_replacement: MATDOC</code>, <code>cds_view: I_MaterialStock</code>, "
             "<code>baseline_tier: T3</code>). Turns a silent miss into a routed, tiered "
             "finding.</li>")
    P.append("<li><strong>Lock a matching eval case</strong> — append the emitted "
             "<code>proposed-eval-case.yaml</code> stub to "
             "<code>ground-truth/findings.yaml</code> so the gap is regression-locked: recall now "
             f"<em>measures</em> whether <code>{esc(obj)}</code> is caught, and can never silently "
             "reopen.</li>")
    P.append("</ol>")
    P.append("<p>The order matters: add the eval case first and recall <span class='hl'>drops</span> "
             "(a must-fix the current report misses); add the catalog row and re-run, and recall "
             "<span class='hl'>recovers</span> (the miss becomes a true positive). That "
             "drop-then-recover is the proof the loop closed.</p>")

    # 4. artifacts
    P.append("<h2>4. Artifacts emitted by this run</h2>")
    P.append("<ul>")
    P.append("<li><code>retro-recommendation.md</code> / <code>retro-recommendation.html</code> — "
             "this recommendation.</li>")
    P.append("<li><code>proposed-eval-case.yaml</code> — paste-ready <code>findings.yaml</code> "
             "stub (a human tightens <code>expected_tier</code> / <code>expected_fix</code> before "
             "locking it in).</li>")
    P.append("</ul>")
    P.append("<div class='note'>retro.py <strong>only emits the stub</strong> — it does "
             "<strong>not</strong> edit ground truth. The catalog + findings.yaml edits are a "
             "deliberate human step.</div>")

    P.append(f"<footer>Generated by {esc(GENERATOR)}.</footer>")
    P.append("</div></body></html>")
    return "\n".join(P)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Self-improvement step: turn ONE human-vs-tool delta (a review-queue "
                    "catalog-miss a human marked must-fix) into a recommendation + eval-case stub.")
    ap.add_argument("--ledger", required=True, help="path to remediation-ledger.json")
    ap.add_argument("--review-queue", required=True, help="path to review-queue.json")
    ap.add_argument("--out-dir", default=None,
                    help="output directory (default: directory of the ledger)")
    args = ap.parse_args()

    try:
        ledger = load_json(args.ledger)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: ledger not found: {args.ledger} (run worklist.py init first)\n")
        return 1
    try:
        review_queue = load_json(args.review_queue)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: review-queue not found: {args.review_queue}\n")
        return 1

    delta = find_delta(review_queue, ledger)
    if delta is None:
        sys.stderr.write(
            "[retro] no deltas to learn from — no review-queue/not_in_catalog item was "
            "marked as a fix in the ledger. Nothing to do.\n"
        )
        return 0

    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.ledger))
    os.makedirs(out_dir, exist_ok=True)

    md_path = os.path.join(out_dir, "retro-recommendation.md")
    html_path = os.path.join(out_dir, "retro-recommendation.html")
    yaml_path = os.path.join(out_dir, "proposed-eval-case.yaml")

    with open(md_path, "w") as f:
        f.write(render_markdown(delta))
    with open(html_path, "w") as f:
        f.write(render_html(delta))
    with open(yaml_path, "w") as f:
        f.write(render_eval_case(delta))

    sys.stderr.write(
        f"[retro] delta: {delta['object']} @ {basename_line(delta['file'], delta['line'])} "
        f"(tool: review-queue/{delta['reason']} -> human: {delta['human_status']} = must-fix)\n"
        f"[retro] wrote {md_path}, {html_path}, {yaml_path}\n"
        f"[retro] SINGLE WORKED EXAMPLE — a general retro engine is roadmap.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
