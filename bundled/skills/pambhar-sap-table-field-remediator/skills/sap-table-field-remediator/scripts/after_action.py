#!/usr/bin/env python3
"""after_action.py — human-friendly after-action report from the machine artifacts.

Reads the deterministic `remediation-report.json` (findings) and the durable
review `remediation-ledger.json` (decisions + sign-off), joins them, and renders
a presentation-ready after-action report as BOTH Markdown and self-contained HTML.

Read-only over its inputs. It never writes the ledger (only worklist.py does) and
never edits ABAP. It exists to make the audit trail legible: what was found, what a
human decided, what's still outstanding.

Join identity: `finding_ref` = f"{file}::{object}::{line}" (same key worklist.py
uses). The ledger is the spine of the record (it holds human state + review-queue
items); report findings enrich each row with tier/category/rationale where present.

Drift guard: recompute sha256(json.dumps(report['findings'], sort_keys=True)) and
compare to the ledger's stored fingerprint. If they differ, the report changed
after decisions were recorded and a prominent warning is rendered in both outputs.

Usage:
  python3 after_action.py --report ./remediation-report.json \
                          --ledger ./remediation-ledger.json [--out-dir DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sys
from datetime import datetime, timezone

GENERATOR = "after_action.py 0.1"

# Canonical orderings (mirror worklist.py's vocabulary).
STATUS_ORDER = ["approved", "answered", "acknowledged", "deferred", "rejected", "pending"]
ACTION_ORDER = ["auto_apply", "propose", "escalate", "verify", "route_to_sibling", "review_queue"]
TIER_ORDER = ["T1", "T2", "T3"]
# A decision is "resolved" only if it reached a terminal human verdict. `deferred` is a
# handoff, not a resolution — it is outstanding, never counted toward % resolved.
DECIDED_STATUSES = ("approved", "rejected", "answered", "acknowledged")
OUTSTANDING_STATUSES = ("pending", "deferred")


# --------------------------------------------------------------------------- #
# Helpers (rendering idiom copied from eval/score.py — same house style)
# --------------------------------------------------------------------------- #
def pct(x):
    return f"{x * 100:.1f}%"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def findings_fingerprint(report: dict) -> str:
    blob = json.dumps(report.get("findings", []), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def finding_ref(file: str, object_: str, line) -> str:
    return f"{file}::{object_}::{line}"


def load_apply_log(path: str | None) -> dict | None:
    """Load an apply-log.json (written by apply.py) if present. Returns None when the
    file is absent/unreadable so callers can fall back to the analysis-only wording."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def apply_summary(apply_log: dict | None) -> dict:
    """Normalize the apply-log into the fields the renderers need."""
    if not apply_log:
        return {"applied_count": 0, "files": 0, "refs": []}
    applied = apply_log.get("applied", [])
    files = {a.get("file") for a in applied if a.get("file")}
    return {
        "applied_count": apply_log.get("applied_count", len(applied)),
        "files": len(files),
        "refs": [a.get("finding_ref", "") for a in applied],
    }


def basename_line(file: str, line) -> str:
    return f"{os.path.basename(file)}:{line}"


# --------------------------------------------------------------------------- #
# Aggregation — build a plain dict the renderers consume
# --------------------------------------------------------------------------- #
def aggregate(report: dict, ledger: dict, report_path: str, ledger_path: str) -> dict:
    decisions = ledger.get("decisions", [])

    # index report findings by finding_ref for enrichment
    find_by_ref = {}
    for f in report.get("findings", []):
        find_by_ref[finding_ref(f["file"], f["object"], f["line"])] = f

    # per-status counts
    status_counts = {st: 0 for st in STATUS_ORDER}
    for d in decisions:
        st = d.get("status", "pending")
        status_counts[st] = status_counts.get(st, 0) + 1

    total = len(decisions)
    pending = status_counts.get("pending", 0)
    # decided = terminal verdicts only; deferred stays outstanding (not resolved).
    decided = sum(status_counts.get(st, 0) for st in DECIDED_STATUSES)
    resolved_pct = (decided / total) if total else 0.0

    # disposition: action bucket x status
    disposition = {a: {st: 0 for st in STATUS_ORDER} for a in ACTION_ORDER}
    for d in decisions:
        action = d.get("action") or "review_queue"
        st = d.get("status", "pending")
        disposition.setdefault(action, {st2: 0 for st2 in STATUS_ORDER})
        disposition[action][st] = disposition[action].get(st, 0) + 1

    # per-finding rows (ledger is the record; enrich from report)
    rows = []
    for d in decisions:
        f = find_by_ref.get(d["finding_ref"], {})
        note = d.get("human_answer") or d.get("comment") or ""
        rows.append({
            "object": d.get("object", ""),
            "file": d.get("file", ""),
            "line": d.get("line", ""),
            "tier": d.get("tier") or f.get("tier"),
            "action": d.get("action") or "review_queue",
            "status": d.get("status", "pending"),
            "category": f.get("category", ""),
            "note": note,
            "decided_by": d.get("decided_by", ""),
        })

    outstanding = [r for r in rows if r["status"] in OUTSTANDING_STATUSES]

    # Count review-queue rows directly (robust under drift) rather than deriving
    # total - report_findings, which mis-counts if the ledger and report diverge.
    review_queue_items = max(0, sum(
        1 for d in decisions if (d.get("action") or "review_queue") == "review_queue"))

    signoff = ledger.get("signoff")

    return {
        "report_path": report_path,
        "ledger_path": ledger_path,
        "run": report.get("run", {}),
        "created": ledger.get("created", ""),
        "generated_at": now_iso(),
        "signoff": signoff,
        "total": total,
        "decided": decided,
        "pending": pending,
        "resolved_pct": resolved_pct,
        "status_counts": status_counts,
        "disposition": disposition,
        "rows": rows,
        "outstanding": outstanding,
        "report_findings": len(report.get("findings", [])),
        "review_queue_items": review_queue_items,
    }


# --------------------------------------------------------------------------- #
# Drift check
# --------------------------------------------------------------------------- #
def check_drift(report: dict, ledger: dict) -> dict:
    computed = findings_fingerprint(report)
    stored_raw = ledger.get("report_fingerprint", "") or ""
    stored = stored_raw.split("sha256:", 1)[-1] if stored_raw else ""
    return {
        "drifted": bool(stored) and stored != computed,
        "computed": computed,
        "stored": stored,
    }


# --------------------------------------------------------------------------- #
# Markdown renderer
# --------------------------------------------------------------------------- #
def render_markdown(s: dict, drift: dict) -> str:
    L = []
    L.append("# After-Action Report — SAP Table & Field Remediation")
    L.append("")

    if drift["drifted"]:
        L.append("> ## WARNING: report drift detected")
        L.append(">")
        L.append("> The report changed **after** decisions were recorded — the ledger may be stale.")
        L.append(f"> Recorded fingerprint `sha256:{drift['stored'][:16]}…` vs current "
                 f"`sha256:{drift['computed'][:16]}…`.")
        L.append("> Re-run `worklist.py init --force` against the current report, then re-review.")
        L.append("")

    # 1. Run + session metadata
    run = s["run"]
    so = s["signoff"]
    L.append("## 1. Run + session metadata")
    L.append("")
    L.append(f"- model: `{run.get('model', '?')}`")
    L.append(f"- skill_version: `{run.get('skill_version', '?')}`")
    L.append(f"- mode: `{run.get('mode', '?')}`")
    L.append(f"- report: `{s['report_path']}`")
    L.append(f"- ledger: `{s['ledger_path']}`")
    L.append(f"- ledger created: `{s['created'] or '?'}`")
    if so:
        L.append(f"- signed off by: **{so.get('by', '?')}** at `{so.get('at', '?')}`")
    else:
        L.append("- signed off: **not yet signed off**")
    L.append(f"- report generated: `{s['generated_at']}`")
    L.append("")

    # 2. HEADLINE
    sc = s["status_counts"]
    L.append("## 2. HEADLINE")
    L.append("")
    L.append("| # | Metric | Value |")
    L.append("|---|--------|-------|")
    L.append(f"| 1 | Total findings | **{s['total']}** "
             f"({s['report_findings']} report + {s['review_queue_items']} review-queue) |")
    L.append(f"| 2 | Decided vs pending | **{s['decided']}** decided / **{s['pending']}** pending |")
    L.append(f"| 3 | % resolved in session | **{pct(s['resolved_pct'])}** (decided/total) |")
    L.append(f"| 4 | Unsafe auto-applies | **0** (inherited — guaranteed by the structural guard) |")
    L.append("")
    L.append("Per-status counts:")
    L.append("")
    L.append("| Status | Count |")
    L.append("|--------|-------|")
    for st in STATUS_ORDER:
        L.append(f"| {st} | {sc.get(st, 0)} |")
    L.append("")

    # 3. Disposition by action / tier
    disp = s["disposition"]
    L.append("## 3. Disposition by action")
    L.append("")
    header = "| Action | " + " | ".join(STATUS_ORDER) + " | total |"
    L.append(header)
    L.append("|" + "---|" * (len(STATUS_ORDER) + 2))
    for a in ACTION_ORDER:
        if a not in disp:
            continue
        row = disp[a]
        total = sum(row.values())
        if total == 0:
            continue
        cells = " | ".join(str(row.get(st, 0)) for st in STATUS_ORDER)
        L.append(f"| {a} | {cells} | {total} |")
    L.append("")

    # 4. Per-finding ledger
    L.append("## 4. Per-finding ledger (auditable record)")
    L.append("")
    L.append("| Object | File:line | Tier | Action | Status | Human answer / comment |")
    L.append("|--------|-----------|------|--------|--------|------------------------|")
    for r in s["rows"]:
        note = (r["note"] or "").replace("|", "\\|").replace("\n", " ")
        if len(note) > 120:
            note = note[:117] + "…"
        L.append(f"| `{r['object']}` | {basename_line(r['file'], r['line'])} "
                 f"| {r['tier'] or '—'} | {r['action']} | {r['status']} | {note or '—'} |")
    L.append("")

    # 5. Outstanding
    L.append("## 5. Outstanding (what's left / handed off)")
    L.append("")
    if not s["outstanding"]:
        L.append("None — every finding is decided.")
    else:
        L.append(f"{len(s['outstanding'])} item(s) still pending or deferred:")
        L.append("")
        L.append("| Object | File:line | Tier | Action | Status |")
        L.append("|--------|-----------|------|--------|--------|")
        for r in s["outstanding"]:
            L.append(f"| `{r['object']}` | {basename_line(r['file'], r['line'])} "
                     f"| {r['tier'] or '—'} | {r['action']} | {r['status']} |")
    L.append("")

    # 6. Roadmap note
    L.append("## 6. Roadmap note")
    L.append("")
    ap = s.get("apply", {"applied_count": 0, "files": 0, "refs": []})
    if ap["applied_count"] > 0:
        L.append(f"- **{ap['applied_count']} fix(es) applied to {ap['files']} file(s)** as local diffs "
                 "(see `apply-log.json`). Not yet pushed/activated in the SAP system — that hand-off is "
                 "the client's step (no system access).")
        refs = ", ".join(f"`{r}`" for r in ap["refs"][:10])
        if len(ap["refs"]) > 10:
            refs += f", … (+{len(ap['refs']) - 10} more)"
        if refs:
            L.append(f"  - Applied: {refs}")
    else:
        L.append("- **No fixes were written to source in this run (analysis-only).** Local-file apply is "
                 "available via `apply.py`; pushing into the SAP system remains the client's step.")
    L.append("- **Review surface = this session.** In-system review via ADT / a web review surface is "
             "roadmap, not yet wired.")
    L.append("- Unsafe auto-applies remain **0** by construction (structural guard), inherited from the "
             "skill's safety contract — not recomputed here.")
    L.append("")
    L.append(f"_Generated by {GENERATOR}._")
    L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# HTML renderer (self-contained, inline style, site palette)
# --------------------------------------------------------------------------- #
def _tier_class(tier):
    return {"T1": "t1", "T2": "t2", "T3": "t3"}.get(tier or "", "tnone")


def _status_class(status):
    if status in ("approved", "answered", "acknowledged"):
        return "st-good"
    if status in ("pending", "deferred"):
        return "st-open"
    return "st-muted"  # rejected + anything else


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


STYLE = """
:root{
  --ink:#0f172a; --ink-soft:#334155; --muted:#64748b; --line:#e2e8f0;
  --line-soft:#f1f5f9; --bg:#f8fafc; --bg-tint:#f1f5f9; --card:#ffffff;
  --accent:#4f46e5; --accent-700:#4338ca; --accent-soft:#eef2ff;
  --t1:#059669; --t1-bg:#d1fae5; --t2:#d97706; --t2-bg:#fef3c7;
  --t3:#e11d48; --t3-bg:#ffe4e6;
  --det:#0f766e; --llm:#7c3aed; --human:#b91c1c;
  --good:#047857; --good-bg:#d1fae5; --warn:#b91c1c; --warn-bg:#fee2e2;
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
.meta{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:1rem 1.3rem;box-shadow:0 1px 3px rgba(15,23,42,.06);}
.meta ul{margin:0;padding-left:1.1rem;}
.meta li{margin:.15rem 0;}
table{width:100%;border-collapse:collapse;background:var(--card);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;
  box-shadow:0 1px 3px rgba(15,23,42,.06);margin:.4rem 0 1rem;font-size:.9rem;}
th,td{text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--line-soft);
  vertical-align:top;}
th{background:var(--bg-tint);color:var(--ink);font-weight:600;
  font-size:.78rem;text-transform:uppercase;letter-spacing:.03em;}
tr:last-child td{border-bottom:none;}
td.num{text-align:right;font-variant-numeric:tabular-nums;}
.pill{display:inline-block;padding:.1em .55em;border-radius:999px;
  font-size:.78rem;font-weight:600;white-space:nowrap;}
.t1{background:var(--t1-bg);color:var(--t1);}
.t2{background:var(--t2-bg);color:var(--t2);}
.t3{background:var(--t3-bg);color:var(--t3);}
.tnone{background:var(--line);color:var(--muted);}
.st-good{color:var(--good);font-weight:600;}
.st-open{color:var(--warn);font-weight:600;}
.st-muted{color:var(--muted);}
.hl{font-weight:700;color:var(--ink);}
.warn-banner{background:var(--warn-bg);border:2px solid var(--warn);
  color:var(--human);border-radius:12px;padding:1rem 1.3rem;margin:0 0 1.5rem;}
.warn-banner h2{color:var(--human);border:none;margin:.1rem 0 .5rem;font-size:1.1rem;}
.ok-note{color:var(--good);font-weight:600;}
.roadmap li{margin:.35rem 0;}
footer{margin-top:2.5rem;color:var(--muted);font-size:.8rem;}
"""


def render_html(s: dict, drift: dict) -> str:
    run = s["run"]
    so = s["signoff"]
    sc = s["status_counts"]
    P = []
    P.append("<!doctype html>")
    P.append('<html lang="en"><head><meta charset="utf-8">')
    P.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    P.append("<title>After-Action Report — SAP Table &amp; Field Remediation</title>")
    P.append(f"<style>{STYLE}</style>")
    P.append("</head><body><div class='wrap'>")

    P.append("<h1>After-Action Report</h1>")
    P.append("<p class='sub'>SAP Table &amp; Field Remediation — human review record</p>")

    if drift["drifted"]:
        P.append("<div class='warn-banner'>")
        P.append("<h2>WARNING: report drift detected</h2>")
        P.append("<p>The report changed <strong>after</strong> decisions were recorded — "
                 "the ledger may be stale.</p>")
        P.append(f"<p>Recorded fingerprint <code>sha256:{esc(drift['stored'][:16])}…</code> vs "
                 f"current <code>sha256:{esc(drift['computed'][:16])}…</code>. "
                 "Re-run <code>worklist.py init --force</code> against the current report, then "
                 "re-review.</p>")
        P.append("</div>")

    # 1. metadata
    P.append("<h2>1. Run + session metadata</h2>")
    P.append("<div class='meta'><ul>")
    P.append(f"<li>model: <code>{esc(run.get('model', '?'))}</code></li>")
    P.append(f"<li>skill_version: <code>{esc(run.get('skill_version', '?'))}</code></li>")
    P.append(f"<li>mode: <code>{esc(run.get('mode', '?'))}</code></li>")
    P.append(f"<li>report: <code>{esc(s['report_path'])}</code></li>")
    P.append(f"<li>ledger: <code>{esc(s['ledger_path'])}</code></li>")
    P.append(f"<li>ledger created: <code>{esc(s['created'] or '?')}</code></li>")
    if so:
        P.append(f"<li>signed off by: <span class='hl'>{esc(so.get('by', '?'))}</span> "
                 f"at <code>{esc(so.get('at', '?'))}</code></li>")
    else:
        P.append("<li>signed off: <span class='st-open'>not yet signed off</span></li>")
    P.append(f"<li>report generated: <code>{esc(s['generated_at'])}</code></li>")
    P.append("</ul></div>")

    # 2. headline
    P.append("<h2>2. Headline</h2>")
    P.append("<table><thead><tr><th>#</th><th>Metric</th><th>Value</th></tr></thead><tbody>")
    P.append(f"<tr><td>1</td><td>Total findings</td><td><span class='hl'>{s['total']}</span> "
             f"({s['report_findings']} report + {s['review_queue_items']} review-queue)</td></tr>")
    P.append(f"<tr><td>2</td><td>Decided vs pending</td><td><span class='hl'>{s['decided']}</span> "
             f"decided / <span class='hl'>{s['pending']}</span> pending</td></tr>")
    P.append(f"<tr><td>3</td><td>% resolved in session</td>"
             f"<td><span class='hl'>{pct(s['resolved_pct'])}</span> (decided/total)</td></tr>")
    P.append("<tr><td>4</td><td>Unsafe auto-applies</td>"
             "<td><span class='ok-note'>0</span> "
             "(inherited — guaranteed by the structural guard)</td></tr>")
    P.append("</tbody></table>")

    P.append("<table><thead><tr><th>Status</th><th>Count</th></tr></thead><tbody>")
    for st in STATUS_ORDER:
        cls = _status_class(st)
        P.append(f"<tr><td><span class='{cls}'>{esc(st)}</span></td>"
                 f"<td class='num'>{sc.get(st, 0)}</td></tr>")
    P.append("</tbody></table>")

    # 3. disposition
    P.append("<h2>3. Disposition by action</h2>")
    P.append("<table><thead><tr><th>Action</th>")
    for st in STATUS_ORDER:
        P.append(f"<th>{esc(st)}</th>")
    P.append("<th>total</th></tr></thead><tbody>")
    disp = s["disposition"]
    for a in ACTION_ORDER:
        if a not in disp:
            continue
        row = disp[a]
        total = sum(row.values())
        if total == 0:
            continue
        P.append(f"<tr><td><code>{esc(a)}</code></td>")
        for st in STATUS_ORDER:
            P.append(f"<td class='num'>{row.get(st, 0)}</td>")
        P.append(f"<td class='num hl'>{total}</td></tr>")
    P.append("</tbody></table>")

    # 4. per-finding ledger
    P.append("<h2>4. Per-finding ledger (auditable record)</h2>")
    P.append("<table><thead><tr><th>Object</th><th>File:line</th><th>Tier</th>"
             "<th>Action</th><th>Status</th><th>Human answer / comment</th></tr></thead><tbody>")
    for r in s["rows"]:
        tcls = _tier_class(r["tier"])
        scls = _status_class(r["status"])
        P.append(
            "<tr>"
            f"<td><code>{esc(r['object'])}</code></td>"
            f"<td class='mono'>{esc(basename_line(r['file'], r['line']))}</td>"
            f"<td><span class='pill {tcls}'>{esc(r['tier'] or '—')}</span></td>"
            f"<td>{esc(r['action'])}</td>"
            f"<td><span class='{scls}'>{esc(r['status'])}</span></td>"
            f"<td>{esc(r['note'] or '—')}</td>"
            "</tr>"
        )
    P.append("</tbody></table>")

    # 5. outstanding
    P.append("<h2>5. Outstanding (what's left / handed off)</h2>")
    if not s["outstanding"]:
        P.append("<p class='ok-note'>None — every finding is decided.</p>")
    else:
        P.append(f"<p>{len(s['outstanding'])} item(s) still pending or deferred:</p>")
        P.append("<table><thead><tr><th>Object</th><th>File:line</th><th>Tier</th>"
                 "<th>Action</th><th>Status</th></tr></thead><tbody>")
        for r in s["outstanding"]:
            tcls = _tier_class(r["tier"])
            scls = _status_class(r["status"])
            P.append(
                "<tr>"
                f"<td><code>{esc(r['object'])}</code></td>"
                f"<td class='mono'>{esc(basename_line(r['file'], r['line']))}</td>"
                f"<td><span class='pill {tcls}'>{esc(r['tier'] or '—')}</span></td>"
                f"<td>{esc(r['action'])}</td>"
                f"<td><span class='{scls}'>{esc(r['status'])}</span></td>"
                "</tr>"
            )
        P.append("</tbody></table>")

    # 6. roadmap note
    P.append("<h2>6. Roadmap note</h2>")
    P.append("<ul class='roadmap'>")
    ap = s.get("apply", {"applied_count": 0, "files": 0, "refs": []})
    if ap["applied_count"] > 0:
        refs = ", ".join(f"<code>{esc(r)}</code>" for r in ap["refs"][:10])
        if len(ap["refs"]) > 10:
            refs += f", … (+{len(ap['refs']) - 10} more)"
        P.append(f"<li><strong>{ap['applied_count']} fix(es) applied to {ap['files']} file(s)</strong> "
                 "as local diffs (see <code>apply-log.json</code>). Not yet pushed/activated in the SAP "
                 "system — that hand-off is the client's step (no system access)."
                 + (f"<br>Applied: {refs}" if refs else "") + "</li>")
    else:
        P.append("<li><strong>No fixes were written to source in this run (analysis-only).</strong> "
                 "Local-file apply is available via <code>apply.py</code>; pushing into the SAP system "
                 "remains the client's step.</li>")
    P.append("<li><strong>Review surface = this session.</strong> In-system review via ADT / a web "
             "review surface is roadmap, not yet wired.</li>")
    P.append("<li>Unsafe auto-applies remain <span class='ok-note'>0</span> by construction "
             "(structural guard), inherited from the skill's safety contract — not recomputed here.</li>")
    P.append("</ul>")

    P.append(f"<footer>Generated by {esc(GENERATOR)}.</footer>")
    P.append("</div></body></html>")
    return "\n".join(P)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render a human-friendly after-action report from the remediation "
                    "report + review ledger.")
    ap.add_argument("--report", required=True, help="path to remediation-report.json")
    ap.add_argument("--ledger", required=True, help="path to remediation-ledger.json")
    ap.add_argument("--out-dir", default=None,
                    help="output directory (default: directory of the report)")
    ap.add_argument("--apply-log", default=None,
                    help="path to apply-log.json from apply.py (default: alongside the report)")
    args = ap.parse_args()

    try:
        report = load_json(args.report)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: report not found: {args.report}\n")
        return 1
    try:
        ledger = load_json(args.ledger)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: ledger not found: {args.ledger} (run `worklist.py init` first)\n")
        return 1

    out_dir = args.out_dir or os.path.dirname(os.path.abspath(args.report))
    os.makedirs(out_dir, exist_ok=True)

    drift = check_drift(report, ledger)
    if drift["drifted"]:
        sys.stderr.write(
            "[after_action] WARNING: report fingerprint drift — ledger may be stale "
            "(report changed after decisions were recorded)\n"
        )

    s = aggregate(report, ledger, args.report, args.ledger)

    # Reflect what apply.py actually did (if it ran). Default: apply-log.json next to
    # the report; --apply-log overrides. Absent -> analysis-only wording.
    apply_log_path = args.apply_log or os.path.join(
        os.path.dirname(os.path.abspath(args.report)), "apply-log.json")
    s["apply"] = apply_summary(load_apply_log(apply_log_path))

    md_path = os.path.join(out_dir, "after-action-report.md")
    html_path = os.path.join(out_dir, "after-action-report.html")

    with open(md_path, "w") as f:
        f.write(render_markdown(s, drift))
    with open(html_path, "w") as f:
        f.write(render_html(s, drift))

    sys.stderr.write(
        f"[after_action] wrote {md_path} and {html_path}: "
        f"{s['total']} findings, {s['decided']} decided / {s['pending']} pending "
        f"({pct(s['resolved_pct'])} resolved)"
        + (" — DRIFT WARNING active\n" if drift["drifted"] else "\n")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
