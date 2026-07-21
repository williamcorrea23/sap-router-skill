#!/usr/bin/env python3
"""crv.py — load the CRV successor dictionary (a released-target lookup). OPTIONAL.

`crv-successors.json` is distilled from SAP's Cloudification Repository (built by
mcp/build/crv_ingest.py). It maps an ECC object -> its released successor (CDS view /
table), so classify.py can FILL/VERIFY a finding's `replacement` and suggest a target
for catalog-miss (review-queue) items.

CRITICAL: this is a TARGET dictionary only. CRV `state` is clean-core API readiness,
NOT brownfield breakage — never derive world/tier from it (see crv_ingest.py header).
Enrichment is advisory and optional: if the file is absent, load() returns {} and every
caller degrades to catalog-only behaviour (same contract as the Simplification KB).

Resolution order (mirrors catalog.py):
  1. explicit path arg
  2. $CRV_SUCCESSORS
  3. ./crv-successors.json
  4. bundled ../references/crv-successors.json
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED = os.path.normpath(os.path.join(HERE, "..", "references", "crv-successors.json"))


def find(explicit: str | None = None) -> str | None:
    for c in (explicit, os.environ.get("CRV_SUCCESSORS"),
              os.path.join(os.getcwd(), "crv-successors.json"), BUNDLED):
        if c and os.path.isfile(c):
            return c
    return None


def load(path: str | None = None) -> dict[str, dict]:
    """Return {OBJECT: {object_type,state,preferred,preferred_type,all[]}} or {} if absent."""
    p = find(path)
    if not p:
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        return {k.upper(): v for k, v in (doc.get("successors") or {}).items()}
    except (OSError, ValueError):
        return {}


def preferred(crv: dict, obj: str) -> str | None:
    hit = crv.get((obj or "").upper())
    return hit.get("preferred") if hit else None


def main() -> int:
    import sys
    crv = load()
    if not crv:
        print("(no crv-successors.json found)")
        return 0
    args = sys.argv[1:]
    if args:
        hit = crv.get(args[0].upper())
        print(json.dumps(hit, indent=2) if hit else f"(no CRV successor: {args[0]})")
    else:
        print(f"crv successors: {len(crv)} objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
