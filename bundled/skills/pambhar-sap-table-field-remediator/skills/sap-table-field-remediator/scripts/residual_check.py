#!/usr/bin/env python3
"""residual_check.py — apply-mode verification sensor.

Re-runs detect -> classify over (already-remediated) source and exits NON-ZERO if any
must-fix reference still survives. Dual use:
  - DETECT (pre-fix): list the obsolete references.
  - VERIFY (post-fix): gate a patch — fail CI if a T1 auto_apply left a residual KONV etc.

A "residual must-fix" = a finding whose action is auto_apply/propose/escalate (i.e. world-A
must-fix), excluding `verify`/`route_to_sibling` notes. Pair with `abaplint` itself for the
post-fix parse check (the harness wires that separately).

Usage:
  python3 residual_check.py --src ./src [--catalog P] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import classify as classify_mod
import catalog as catalog_mod

HERE = os.path.dirname(os.path.abspath(__file__))
MUSTFIX_ACTIONS = {"auto_apply", "propose", "escalate"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="./src")
    ap.add_argument("--catalog", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    detect = json.loads(
        subprocess.run(["node", os.path.join(HERE, "detect.js"), args.src],
                       check=True, capture_output=True, text=True).stdout
    )
    cat = catalog_mod.load(args.catalog)
    result = classify_mod.classify(detect, cat)
    residual = [f for f in result["findings"] if f.get("action") in MUSTFIX_ACTIONS]

    if args.json:
        print(json.dumps({"residual_count": len(residual),
                          "residual": [{k: f[k] for k in ("file", "line", "object", "action")} for f in residual]},
                         indent=2))
    else:
        if not residual:
            print("CLEAN: no residual must-fix references.")
        else:
            print(f"RESIDUAL: {len(residual)} must-fix reference(s) remain:")
            for f in residual:
                print(f"  {os.path.basename(f['file'])}:{f['line']}  {f['object']}  ({f['action']})")
    return 1 if residual else 0


if __name__ == "__main__":
    raise SystemExit(main())
