#!/usr/bin/env python3
"""crv_ingest.py — build the CRV SUCCESSOR DICTIONARY (a released-target lookup).

SAP publishes the authoritative classic-object -> released-successor mapping as open
JSON (Apache-2.0) at github.com/SAP/abap-atc-cr-cv-s4hc. This script distils the PCE
release-info file into a small `crv-successors.json` the skill uses to FILL/VERIFY the
`replacement` (released-API target) on findings we already raise, and to suggest a
target for catalog-miss (review-queue) items.

WHY only a target dictionary — NOT a world/tier source (learned the hard way):
  CRV `state = notToBeReleased` means "not a released API for ABAP Cloud (clean core)",
  NOT "breaks in an ECC->S/4 brownfield conversion". Proof from the PCE data:
    - VBAK/VBAP/MARA/T001/SKAT/MARD are notToBeReleased yet still SELECT fine on-stack
      -> mapping state->World-A must-fix would OVER-CLAIM and tank precision.
    - the tables that truly break in brownfield (VBUK/VBUP/RFBLG/S001/S061/PCL2) are
      ABSENT from CRV -> it cannot be the brownfield must-fix authority.
  So brownfield world/tier stays with the hand catalog (Simplification List + curation).
  CRV's genuine, low-risk value is the SUCCESSOR TARGET: table -> released CDS view.

Input (objectReleaseInfo_PCELatest.json):
  { formatVersion, objectReleaseInfo: [ {objectType, objectKey, tadirObjName, state,
    successors?[{objectType,objectKey}], successorConceptName?} ] }

Output (crv-successors.json):
  { format, source, generated_from, count,
    successors: { OBJECT: {object_type, state, preferred, preferred_type,
                           all:[{type,key}]} } }

Usage:
  python3 crv_ingest.py --crv objectReleaseInfo_PCELatest.json \
      --out ../../skills/sap-table-field-remediator/references/crv-successors.json \
      [--types TABL]   [--hand <hand-catalog.yaml> for a coverage report]
"""
from __future__ import annotations

import argparse
import json
import sys

NOT_RELEASED_STATES = {"notToBeReleased", "notToBeReleasedStable", "deprecated"}
# target preference: a released CDS view is the clean-core-correct forward target;
# fall back to a transparent successor table, then anything listed.
TYPE_PRIORITY = ["CDS_STOB", "TABL", "FUNC", "CLAS", "INTF"]


def load_crv(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for k in ("objectReleaseInfo", "objectClassifications"):
        if isinstance(data.get(k), list):
            return data[k]
    raise SystemExit(f"unrecognised CRV file: {path} (keys={list(data)})")


def successors_of(entry: dict) -> list[dict]:
    out = [{"type": s.get("objectType"), "key": s.get("objectKey")}
           for s in (entry.get("successors") or []) if s.get("objectKey")]
    if not out and entry.get("successorConceptName"):
        out = [{"type": entry.get("successorClassification") or "?",
                "key": entry.get("successorConceptName")}]
    return out


def pick_preferred(succ: list[dict]) -> dict | None:
    for t in TYPE_PRIORITY:
        for s in succ:
            if s["type"] == t:
                return s
    return succ[0] if succ else None


def build(raw: list[dict], keep: set[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for e in raw:
        if (e.get("objectType") or "").upper() not in keep:
            continue
        if e.get("state") not in NOT_RELEASED_STATES:
            continue  # released objects need no target
        succ = successors_of(e)
        if not succ:
            continue  # no successor -> nothing to enrich a target with
        obj = (e.get("objectKey") or e.get("tadirObjName") or "").upper()
        if not obj:
            continue
        pref = pick_preferred(succ)
        out[obj] = {
            "object_type": e.get("objectType"),
            "state": e.get("state"),
            "preferred": pref["key"] if pref else None,
            "preferred_type": pref["type"] if pref else None,
            "all": succ,
        }
    return out


def hand_objects(path: str) -> set[str]:
    try:
        import yaml
    except ImportError:
        sys.stderr.write("(pyyaml missing — skipping hand-catalog coverage report)\n")
        return set()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {str(c["object"]).upper() for c in data.get("catalog", [])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--crv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--types", default="TABL", help="comma list of CRV objectTypes to keep")
    ap.add_argument("--hand", default=None, help="hand catalog yaml, for a coverage report")
    args = ap.parse_args()

    keep = {t.strip().upper() for t in args.types.split(",")}
    raw = load_crv(args.crv)
    succ = build(raw, keep)

    doc = {
        "format": "crv-successors/1",
        "source": "SAP/abap-atc-cr-cv-s4hc (Apache-2.0), objectReleaseInfo PCE",
        "generated_from": args.crv.replace("\\", "/").split("/")[-1],
        "note": ("Target dictionary ONLY. CRV state is clean-core API readiness, NOT "
                 "brownfield breakage; do not derive world/tier from it."),
        "types": sorted(keep),
        "count": len(succ),
        "successors": dict(sorted(succ.items())),
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

    with_cds = sum(1 for v in succ.values() if v["preferred_type"] == "CDS_STOB")
    sys.stderr.write(
        f"[crv] {sorted(keep)}: {len(succ)} objects with a released successor "
        f"({with_cds} -> CDS view)\n[crv] wrote {args.out}\n"
    )
    if args.hand:
        hand = hand_objects(args.hand)
        gen = set(succ)
        sys.stderr.write(
            f"[coverage] hand catalog {len(hand)} objects; CRV supplies a target for "
            f"{len(hand & gen)} of them: {sorted(hand & gen)}\n"
            f"[coverage] CRV adds targets for {len(gen - hand)} objects beyond the hand catalog\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
