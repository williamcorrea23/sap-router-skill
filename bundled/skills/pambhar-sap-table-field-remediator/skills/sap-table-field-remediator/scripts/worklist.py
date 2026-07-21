#!/usr/bin/env python3
"""worklist.py — session-state helper for the SAP table/field remediation review.

The spine of the post-report human workflow. It turns the deterministic
`remediation-report.json` (plus the `review-queue.json` sidecar) into a durable
ledger of REVIEW DECISIONS and lets a human record approvals / answers / sign-off.

Deliberately DUMB: no LLM, no inference, stdlib only. It only reads the report to
seed a ledger, then persists whatever decisions a human makes. The ledger holds
irreplaceable human state, so `init` refuses to clobber an existing one without
--force, and this is the ONLY script that ever writes the ledger.

Identity: each decision is keyed by a `finding_ref` = f"{file}::{object}::{line}"
(file exactly as it appears in the report — repo-relative). Unique because the
skill emits one finding per (statement, object).

Commands:
  init     build the ledger from a report (+ optional review-queue), all pending
  record   upsert one decision (status / answer / comment / decided_by)
  signoff  stamp a sign-off with per-status counts
  status   friendly human-readable summary of the ledger

Usage:
  python3 worklist.py init --report ./remediation-report.json [--review-queue P] \
                           [--ledger ./remediation-ledger.json] [--force]
  python3 worklist.py record --ref "<finding_ref>" --status approved \
                             [--answer "..."] [--comment "..."] [--by NAME] [--ledger P]
  python3 worklist.py signoff --by NAME [--ledger P]
  python3 worklist.py status [--ledger P]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"
GENERATOR = "worklist.py 0.1"
DEFAULT_LEDGER = "./remediation-ledger.json"
TIMESTAMP_SOURCE = "system_clock (worklist.py)"

STATUSES = ["pending", "approved", "rejected", "answered", "acknowledged", "deferred"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_by() -> str:
    return os.environ.get("USER") or "unknown"


def finding_ref(file: str, object_: str, line) -> str:
    return f"{file}::{object_}::{line}"


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def write_ledger(ledger: dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(ledger, f, indent=2)
        f.write("\n")


def fingerprint(report: dict) -> str:
    blob = json.dumps(report.get("findings", []), sort_keys=True)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


# --- commands ---------------------------------------------------------------

def cmd_init(args) -> int:
    ledger_path = args.ledger

    if os.path.exists(ledger_path) and not args.force:
        sys.stderr.write(
            f"REFUSING to overwrite existing ledger: {ledger_path}\n"
            f"  It holds irreplaceable human review state. Re-run with --force to replace it.\n"
        )
        return 1

    try:
        report = load_json(args.report)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: report not found: {args.report}\n")
        return 1

    decisions = []

    # 1) report findings -> decisions (carry tier/action)
    for f in report.get("findings", []):
        ref = finding_ref(f["file"], f["object"], f["line"])
        decisions.append({
            "finding_ref": ref,
            "file": f["file"],
            "line": f["line"],
            "object": f["object"],
            "tier": f.get("tier"),
            "action": f.get("action"),
            "status": "pending",
            "human_answer": "",
            "comment": "",
            "decided_by": "",
            "timestamp": "",
            "timestamp_source": TIMESTAMP_SOURCE,
        })

    # 2) review-queue items -> decisions (tier=null, action=review_queue)
    rq_path = args.review_queue
    if rq_path is None:
        sibling = os.path.join(os.path.dirname(os.path.abspath(args.report)), "review-queue.json")
        if os.path.exists(sibling):
            rq_path = sibling

    if rq_path and os.path.exists(rq_path):
        rq = load_json(rq_path)
        for item in rq.get("items", []):
            ref = finding_ref(item["file"], item["object"], item["line"])
            reason = item.get("reason", "")
            decisions.append({
                "finding_ref": ref,
                "file": item["file"],
                "line": item["line"],
                "object": item["object"],
                "tier": None,
                "action": "review_queue",
                "status": "pending",
                "human_answer": "",
                "comment": f"queue:{reason}" if reason else "queue",
                "decided_by": "",
                "timestamp": "",
                "timestamp_source": TIMESTAMP_SOURCE,
            })

    ledger = {
        "schema_version": SCHEMA_VERSION,
        "generator": GENERATOR,
        "report_ref": args.report,
        "report_fingerprint": fingerprint(report),
        "created": now_iso(),
        "signoff": None,
        "decisions": decisions,
    }

    write_ledger(ledger, ledger_path)
    n_find = len(report.get("findings", []))
    n_queue = len(decisions) - n_find
    sys.stderr.write(
        f"[worklist] wrote {ledger_path}: {len(decisions)} decisions "
        f"({n_find} findings + {n_queue} review-queue), all pending\n"
    )
    return 0


def cmd_record(args) -> int:
    ledger_path = args.ledger
    if args.status not in STATUSES:
        sys.stderr.write(
            f"FATAL: invalid --status '{args.status}'. Valid: {', '.join(STATUSES)}\n"
        )
        return 1

    try:
        ledger = load_json(ledger_path)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: ledger not found: {ledger_path} (run `init` first)\n")
        return 1

    target = None
    for d in ledger.get("decisions", []):
        if d["finding_ref"] == args.ref:
            target = d
            break

    if target is None:
        sys.stderr.write(f"FATAL: finding_ref not found in ledger: {args.ref}\n")
        return 1

    target["status"] = args.status
    if args.answer is not None:
        target["human_answer"] = args.answer
    if args.comment is not None:
        target["comment"] = args.comment
    target["decided_by"] = args.by or default_by()
    target["timestamp"] = now_iso()
    target["timestamp_source"] = TIMESTAMP_SOURCE

    write_ledger(ledger, ledger_path)
    sys.stderr.write(
        f"[worklist] recorded {args.ref} -> {args.status} (by {target['decided_by']})\n"
    )
    return 0


def cmd_signoff(args) -> int:
    ledger_path = args.ledger
    try:
        ledger = load_json(ledger_path)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: ledger not found: {ledger_path} (run `init` first)\n")
        return 1

    counts = {}
    for d in ledger.get("decisions", []):
        counts[d["status"]] = counts.get(d["status"], 0) + 1

    ledger["signoff"] = {
        "by": args.by,
        "at": now_iso(),
        "counts": counts,
    }
    write_ledger(ledger, ledger_path)
    sys.stderr.write(f"[worklist] signed off by {args.by}: {counts}\n")
    return 0


def cmd_status(args) -> int:
    ledger_path = args.ledger
    try:
        ledger = load_json(ledger_path)
    except FileNotFoundError:
        sys.stderr.write(f"FATAL: ledger not found: {ledger_path} (run `init` first)\n")
        return 1

    decisions = ledger.get("decisions", [])
    counts = {}
    for d in decisions:
        counts[d["status"]] = counts.get(d["status"], 0) + 1

    print(f"Remediation review — {ledger.get('report_ref', '?')}")
    print(f"  ledger: {ledger_path}")
    print(f"  total decisions: {len(decisions)}")
    print("  by status:")
    for st in STATUSES:
        if counts.get(st):
            print(f"    {st:13s} {counts[st]}")

    open_refs = [d["finding_ref"] for d in decisions if d["status"] in ("pending", "deferred")]
    if open_refs:
        print(f"  open (pending/deferred): {len(open_refs)}")
        for ref in open_refs[:20]:
            print(f"    - {ref}")
        if len(open_refs) > 20:
            print(f"    ... and {len(open_refs) - 20} more")
    else:
        print("  open (pending/deferred): none — all decided")

    so = ledger.get("signoff")
    if so:
        print(f"  signoff: {so['by']} at {so['at']}")
    else:
        print("  signoff: not yet signed off")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Session-state ledger for SAP remediation review.")
    sub = ap.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="build the ledger from a report (all pending)")
    p_init.add_argument("--report", required=True)
    p_init.add_argument("--review-queue", default=None)
    p_init.add_argument("--ledger", default=DEFAULT_LEDGER)
    p_init.add_argument("--force", action="store_true", help="overwrite an existing ledger")
    p_init.set_defaults(func=cmd_init)

    p_rec = sub.add_parser("record", help="upsert one decision")
    p_rec.add_argument("--ref", required=True)
    p_rec.add_argument("--status", required=True)
    p_rec.add_argument("--answer", default=None)
    p_rec.add_argument("--comment", default=None)
    p_rec.add_argument("--by", default=None)
    p_rec.add_argument("--ledger", default=DEFAULT_LEDGER)
    p_rec.set_defaults(func=cmd_record)

    p_so = sub.add_parser("signoff", help="stamp a sign-off with per-status counts")
    p_so.add_argument("--by", required=True)
    p_so.add_argument("--ledger", default=DEFAULT_LEDGER)
    p_so.set_defaults(func=cmd_signoff)

    p_st = sub.add_parser("status", help="friendly human-readable summary")
    p_st.add_argument("--ledger", default=DEFAULT_LEDGER)
    p_st.set_defaults(func=cmd_status)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
