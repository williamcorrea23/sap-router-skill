#!/usr/bin/env python3
"""catalog.py — load the S/4HANA Remediation Catalog (the evidence locator, not an oracle).

The catalog is `simplification-list.yaml` (schema: key `object`; statuses VALID,
CHANGED, RENAMED, ABOLISHED, RESTRUCTURED, DECLUSTERED_SAME_NAME, REDIRECT_BP,
MODERNIZATION_ONLY; plus `world`, `baseline_tier`, `s4_replacement`, `cds_view`).

This REPLACES the old json loaders (key `ecc_table`, status "COMPATIBILITY VIEW"):
that schema KeyErrors on the YAML and silently misses BSEG/MKPF/MSEG (RESTRUCTURED).

Resolution order at runtime (skill reads whatever catalog is in its working dir):
  1. $CATALOG env var, if set
  2. ./ground-truth/simplification-list.yaml   (the eval sandbox layout)
  3. ./simplification-list.yaml
  4. the copy bundled in ../references/simplification-list.yaml (production fallback)

Custom overrides (OPTIONAL overlay — absent by default):
  A per-client `custom-overrides.yaml` (SAME shape as the catalog: a top-level `catalog:`
  list of object entries) WINS over the standard catalog per object — client-specific
  mappings / expert overrides. An override entry FULLY replaces the standard entry for that
  object (not a field-merge) and is tagged `origin: custom`. Resolution order:
  $CUSTOM_OVERRIDES -> ./ground-truth/custom-overrides.yaml -> ./custom-overrides.yaml ->
  ../references/custom-overrides.yaml. Absence is NOT an error (returns the standard catalog
  unchanged); a present-but-broken file falls back to standard with a stderr warning.
  NOTE: overrides customize KNOWLEDGE only — guard.py still decides auto_apply from
  structural facts, so an override cannot make a write auto-applicable.

Usage as a CLI:  python3 catalog.py [--path P] [--show-overrides] [OBJECT]
  - no OBJECT: print a summary; OBJECT: print that entry as JSON.
  - --show-overrides: list which objects a custom-overrides file overrides.
"""
from __future__ import annotations

import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: pyyaml required (pip install pyyaml).\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED = os.path.normpath(os.path.join(HERE, "..", "references", "simplification-list.yaml"))
BUNDLED_OVERRIDES = os.path.normpath(os.path.join(HERE, "..", "references", "custom-overrides.yaml"))


def find_catalog(explicit: str | None = None) -> str:
    candidates = [
        explicit,
        os.environ.get("CATALOG"),
        os.path.join(os.getcwd(), "ground-truth", "simplification-list.yaml"),
        os.path.join(os.getcwd(), "simplification-list.yaml"),
        BUNDLED,
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    raise FileNotFoundError(
        "No simplification-list.yaml found (looked in $CATALOG, ./ground-truth/, ./, bundled)."
    )


def find_overrides(explicit: str | None = None) -> str | None:
    """Locate an OPTIONAL custom-overrides.yaml. Returns None if none exists (not an error)."""
    candidates = [
        explicit,
        os.environ.get("CUSTOM_OVERRIDES"),
        os.path.join(os.getcwd(), "ground-truth", "custom-overrides.yaml"),
        os.path.join(os.getcwd(), "custom-overrides.yaml"),
        BUNDLED_OVERRIDES,
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def load(path: str | None = None, overrides_path: str | None = None) -> dict[str, dict]:
    p = find_catalog(path)
    with open(p, "r") as f:
        data = yaml.safe_load(f)
    catalog = data["catalog"]
    cat = {str(c["object"]).upper(): c for c in catalog}

    # OPTIONAL custom-override overlay: per-object FULL replacement, tagged origin=custom.
    ov_path = find_overrides(overrides_path)
    if not ov_path:
        return cat  # no overrides -> standard catalog unchanged (byte-for-byte default)
    try:
        with open(ov_path, "r") as f:
            ov_data = yaml.safe_load(f)
        ov_list = (ov_data or {}).get("catalog")
        if not ov_list:
            return cat  # empty / no `catalog:` list -> treat as no overrides
        merged = dict(cat)
        for entry in ov_list:
            obj = str(entry["object"]).upper()
            entry["origin"] = "custom"
            merged[obj] = entry  # full per-object replacement, not a field-merge
    except Exception as e:  # malformed override must never break a normal run
        sys.stderr.write(f"[catalog] WARNING: ignoring unreadable custom overrides {ov_path}: {e}\n")
        return cat
    return merged


def main() -> int:
    args = sys.argv[1:]
    path = None
    show_overrides = False
    if "--path" in args:
        i = args.index("--path")
        path = args[i + 1]
        del args[i : i + 2]
    if "--show-overrides" in args:
        show_overrides = True
        args.remove("--show-overrides")

    if show_overrides:
        std = {str(c["object"]).upper(): c for c in
               yaml.safe_load(open(find_catalog(path)))["catalog"]}
        cat = load(path)
        overridden = sorted(o for o, e in cat.items() if e.get("origin") == "custom")
        ov_path = find_overrides()
        print(f"custom overrides: {ov_path or '(none found)'}")
        if not overridden:
            print("  (none active)")
        else:
            for o in overridden:
                std_tgt = (std.get(o, {}).get("s4_replacement")
                           or std.get(o, {}).get("cds_view") or "-")
                cus_tgt = (cat[o].get("s4_replacement") or cat[o].get("cds_view") or "-")
                print(f"  {o:22} standard->{std_tgt}   custom->{cus_tgt}")
        return 0

    cat = load(path)
    n_custom = sum(1 for e in cat.values() if e.get("origin") == "custom")
    if args:
        obj = args[0].upper()
        entry = cat.get(obj)
        print(json.dumps(entry, indent=2) if entry else f"(not in catalog: {obj})")
    else:
        by_status: dict[str, list[str]] = {}
        for obj, e in sorted(cat.items()):
            by_status.setdefault(e.get("status", "?"), []).append(obj)
        summary = f"catalog: {find_catalog(path)}  ({len(cat)} objects)"
        if n_custom:
            summary += f"  ({n_custom} custom overrides active)"
        print(summary)
        for st in sorted(by_status):
            print(f"  {st:22} {', '.join(by_status[st])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
