#!/usr/bin/env python3
"""analyze.py — one-command deterministic pipeline: detect -> classify -> guard -> emit.

Produces a schema-valid `remediation-report.json` from a directory of ABAP source, with
ZERO LLM involvement. The SKILL.md procedure runs this first to get the deterministic
floor, then (only for the listed `escalations`) the model refines rationale/intent_question
and judges the ambiguous residue, and finally re-runs guard.py before writing.

Pipeline:
  1. node detect.js <src>            -> DB-access statements (abaplint AST)
  2. classify.py                     -> catalog-classified findings + escalations
  3. guard.py                        -> downgrade any unsafe auto_apply (structural 0-guarantee)
  4. strip internal metadata, assemble + validate the contract, write the report

`usage` is emitted as ZEROS — the model can't read its own token counters; the headless
harness overwrites `usage` from the `claude -p --output-format json` result.

Usage:
  python3 analyze.py --src ./src [--catalog P] [--mode analysis|apply] \
                     [--out ./remediation-report.json] [--model M] [--skill-version V]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import classify as classify_mod
import guard as guard_mod
import catalog as catalog_mod

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_VERSION = "1.0"
SKILL_VERSION = "1.2.0"

FINDING_KEYS = {
    "file", "line", "object", "object_type", "world", "tier", "action",
    "category", "replacement", "rationale", "intent_question", "patch",
}
ACTIONS = {"auto_apply", "propose", "escalate", "verify", "route_to_sibling"}
TIERS = {"T1", "T2", "T3", None}
WORLDS = {"A", "A-verify", "B", "B-verify", None}
OBJ_TYPES = {"table", "field", "bapi", "function_module", "report", "class", "enhancement"}
CATEGORIES = {"syntactic", "structural", "semantic", "functional", None}


def run_detect(src: str) -> dict:
    detect_js = os.path.join(HERE, "detect.js")
    try:
        out = subprocess.run(
            ["node", detect_js, src],
            check=True, capture_output=True, text=True,
        )
    except FileNotFoundError:
        sys.stderr.write("FATAL: `node` not found. Install Node.js to run the detector.\n")
        sys.exit(3)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("FATAL: detect.js failed:\n" + e.stderr + "\n")
        sys.exit(3)
    return json.loads(out.stdout)


def strip_internal(f: dict) -> dict:
    return {k: v for k, v in f.items() if not k.startswith("_")}


def validate(report: dict) -> list[str]:
    """Lightweight contract check (no jsonschema dep). Returns a list of errors."""
    errs = []
    for k in ("schema_version", "run", "scanned_files", "findings", "usage"):
        if k not in report:
            errs.append(f"missing top-level key: {k}")
    for rk in ("model", "skill_version", "mode"):
        if rk not in report.get("run", {}):
            errs.append(f"run.{rk} missing")
    if report.get("run", {}).get("mode") not in ("analysis", "apply"):
        errs.append("run.mode must be analysis|apply")
    for uk in ("input_tokens", "output_tokens", "cache_read_tokens", "cost_usd", "turns", "latency_ms"):
        if uk not in report.get("usage", {}):
            errs.append(f"usage.{uk} missing")
    for i, f in enumerate(report.get("findings", [])):
        extra = set(f) - FINDING_KEYS
        if extra:
            errs.append(f"finding[{i}] has disallowed keys: {extra}")
        for rk in ("file", "line", "object", "object_type", "world", "tier", "action"):
            if rk not in f:
                errs.append(f"finding[{i}] missing required key: {rk}")
        if f.get("action") not in ACTIONS:
            errs.append(f"finding[{i}] bad action: {f.get('action')}")
        if f.get("tier") not in TIERS:
            errs.append(f"finding[{i}] bad tier: {f.get('tier')}")
        if f.get("world") not in WORLDS:
            errs.append(f"finding[{i}] bad world: {f.get('world')}")
        if f.get("object_type") not in OBJ_TYPES:
            errs.append(f"finding[{i}] bad object_type: {f.get('object_type')}")
        if f.get("category") not in CATEGORIES:
            errs.append(f"finding[{i}] bad category: {f.get('category')}")
        if not isinstance(f.get("line"), int) or f.get("line", 0) < 1:
            errs.append(f"finding[{i}] line must be int >= 1")
        # escalate / T3 must carry an intent_question
        if (f.get("action") == "escalate" or f.get("tier") == "T3") and not f.get("intent_question"):
            errs.append(f"finding[{i}] escalate/T3 needs intent_question")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="./src")
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--mode", default="analysis", choices=["analysis", "apply"])
    ap.add_argument("--out", default="./remediation-report.json")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--skill-version", default=SKILL_VERSION)
    ap.add_argument("--date", default="", help="ISO date stamp (harness/caller supplies)")
    args = ap.parse_args()

    detect = run_detect(args.src)
    cat = catalog_mod.load(args.catalog)
    classified = classify_mod.classify(detect, cat)

    guarded, downgraded = guard_mod.guard(classified["findings"])

    findings = [strip_internal(f) for f in guarded]
    # stable order: by file then line
    findings.sort(key=lambda f: (f["file"], f["line"], f["object"]))

    run_meta = {"model": args.model, "skill_version": args.skill_version, "mode": args.mode}
    if args.date:
        run_meta["date"] = args.date

    report = {
        "schema_version": SCHEMA_VERSION,
        "run": run_meta,
        "scanned_files": detect.get("scanned_files", []),
        "findings": findings,
        "usage": {  # HARNESS-filled; the model cannot read its own counters
            "input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0,
            "cost_usd": 0, "turns": 0, "latency_ms": 0,
        },
    }

    errs = validate(report)
    if errs:
        sys.stderr.write("SCHEMA VALIDATION ERRORS:\n" + "\n".join("  - " + e for e in errs) + "\n")
        return 1

    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    # SIDECAR files (the scored report schema is additionalProperties:false, so these
    # can't live in args.out). The detector SAW every statement below; we record them
    # instead of silently discarding. See working-notes/DECISIONS.md [2026-06-27].
    from collections import Counter
    out_dir = os.path.dirname(args.out) or "."

    # 1) suppressed = catalog AFFIRMATIVELY says safe (VALID / declustered-same-name /
    #    world-B modernization / no-tier). These may be dropped.
    suppressed = classified.get("suppressed", [])
    sup_path = os.path.join(out_dir, "suppressed-report.json")
    by_reason = dict(Counter(s.get("reason", "?") for s in suppressed))
    with open(sup_path, "w") as f:
        json.dump({"count": len(suppressed), "by_reason": by_reason,
                   "suppressed": suppressed}, f, indent=2)
        f.write("\n")
    sys.stderr.write(f"[analyze] wrote {sup_path}: {len(suppressed)} suppressed ({by_reason})\n")

    # 2) review_queue = accesses the catalog can't classify (not_in_catalog). UNKNOWN,
    #    not safe -> surfaced for KB-search + expert decide-or-skip (SKILL.md §2.1), never
    #    silently dropped. Additive: NOT part of the scored remediation-report.json.
    review_queue = classified.get("review_queue", [])
    rq_path = os.path.join(out_dir, "review-queue.json")
    with open(rq_path, "w") as f:
        json.dump({"count": len(review_queue), "items": review_queue}, f, indent=2)
        f.write("\n")
    sys.stderr.write(f"[analyze] wrote {rq_path}: {len(review_queue)} for review "
                     f"(catalog-miss -> KB-search + expert decide)\n")

    # advisory output for the LLM stage (NOT part of the contract)
    sys.stderr.write(
        f"[analyze] wrote {args.out}: {len(findings)} findings "
        f"(auto_apply={sum(1 for x in findings if x['action']=='auto_apply')}, "
        f"propose={sum(1 for x in findings if x['action']=='propose')}, "
        f"escalate={sum(1 for x in findings if x['action']=='escalate')}, "
        f"verify={sum(1 for x in findings if x['action']=='verify')}, "
        f"route_to_sibling={sum(1 for x in findings if x['action']=='route_to_sibling')})\n"
    )
    sys.stderr.write(f"[analyze] guard downgraded {len(downgraded)} unsafe auto_apply\n")
    esc = classified.get("escalations", [])
    if esc:
        sys.stderr.write(f"[analyze] {len(esc)} escalation(s) for LLM review:\n")
        for e in esc:
            sys.stderr.write(f"  - {e['object']} @ {os.path.basename(e['file'])}:{e['line']} "
                             f"[{e['reason']}] {e.get('note','')}\n")
    # echo escalations as JSON on stdout so the LLM step can consume them
    print(json.dumps({"escalations": esc, "report": args.out}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
