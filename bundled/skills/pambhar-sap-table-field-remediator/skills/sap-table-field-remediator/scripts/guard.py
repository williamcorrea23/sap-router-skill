#!/usr/bin/env python3
"""guard.py — the deterministic auto_apply safety backstop.

This is what makes the headline "unsafe auto-applies = 0" TRUE BY CONSTRUCTION rather
than a prompt hope. It re-derives safety from each finding's metadata and DOWNGRADES any
finding that claims `auto_apply` but isn't provably safe. It runs LAST — after classify.py
and after any LLM edits — so neither a classifier bug nor an over-eager model can leak an
unsafe auto-apply into the report.

A finding may keep `action: auto_apply` ONLY when ALL hold:
  - it is NOT a write (INSERT/UPDATE/MODIFY/DELETE, incl. native)   ... writes need redesign
  - its catalog `baseline_tier` is T1 (not T2/T3)                   ... only mechanical 1:1
  - it was NOT escalated by detection/classification               ... offset-parsed, dynamic
  - tier == T1
Otherwise → action becomes `escalate`, tier is bumped to at least T3, and an
intent_question is ensured. The ratchet only moves UP the 1->4 spectrum, never down.

Operates on the intermediate classified JSON (findings carry a private `_meta` block).
Run BEFORE stripping `_meta` for the schema report (emit.py does the stripping).

Usage:
  python3 guard.py < classified.json > guarded.json
  python3 guard.py --in classified.json --report   # human summary to stderr
"""
from __future__ import annotations

import json
import sys


def is_safe_auto_apply(f: dict) -> bool:
    meta = f.get("_meta", {}) or {}
    if meta.get("access") in ("write", "native_write", "slice_assign"):
        return False
    if meta.get("escalated"):
        return False
    if meta.get("must_escalate"):
        return False
    if meta.get("baseline_tier") not in (None, "T1"):
        return False
    if f.get("tier") not in (None, "T1"):
        return False
    return True


def guard(findings: list[dict]) -> tuple[list[dict], list[dict]]:
    downgraded = []
    for f in findings:
        if f.get("action") != "auto_apply":
            continue
        if is_safe_auto_apply(f):
            continue
        # unsafe -> ratchet up
        before = {"object": f.get("object"), "file": f.get("file"),
                  "line": f.get("line"), "from_tier": f.get("tier")}
        f["action"] = "escalate"
        if f.get("tier") in (None, "T1", "T2"):
            f["tier"] = "T3"
        if not f.get("intent_question"):
            f["intent_question"] = (
                f"{f.get('object')} cannot be auto-applied safely (write / non-T1 / "
                f"escalated). Confirm intended target and semantics before any change."
            )
        downgraded.append(before)
    return findings, downgraded


def main() -> int:
    args = sys.argv[1:]
    report = "--report" in args
    in_path = None
    if "--in" in args:
        i = args.index("--in"); in_path = args[i + 1]

    data = json.load(open(in_path)) if in_path else json.load(sys.stdin)
    findings = data.get("findings", [])
    findings, downgraded = guard(findings)
    data["findings"] = findings
    data["guard"] = {"downgraded_count": len(downgraded), "downgraded": downgraded}

    if report:
        sys.stderr.write(f"[guard] downgraded {len(downgraded)} unsafe auto_apply finding(s):\n")
        for d in downgraded:
            sys.stderr.write(f"  - {d['object']} @ {d['file']}:{d['line']} ({d['from_tier']} -> T3 escalate)\n")
    else:
        print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
