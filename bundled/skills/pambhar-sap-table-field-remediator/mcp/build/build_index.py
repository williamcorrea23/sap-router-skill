#!/usr/bin/env python3
"""build_index.py — build the note-join index over the per-item chunk store.

This is the PRECISION step of the knowledge layer. The prototype indexed items by
scanning chunk bodies for catalog object names; that is noisy (e.g. KONV matched an
unrelated "VBFA Docflow" item and missed the real pricing item). Instead we JOIN on the
SAP Note number: the catalog gives each object a `sap_note`; each chunk carries the
`sap_notes` it cites; we match them.

Inputs (the durable, rebuildable-from-PDF assets):
  common/items/*.md           per-item chunks with YAML frontmatter
                              (item_id, title, pages, sap_notes, components, objects)
  common/kb-index-catalog.yaml   the public catalog (object -> sap_note + metadata)

Output:
  common/index.json with:
    items            item_id -> {title, pages, sap_notes, components}  (metadata only;
                     bodies are read on demand from the .md files)
    note_to_items    sap_note(str) -> [item_id, ...]
    object_to_items  PRIMARY map. object -> {note_used, note_verified, items:[...],
                     weak_matches:[...]} resolved via the catalog note-join.
    object_name_scan SECONDARY signal (labeled). object -> [item_id, ...] from the
                     chunk `objects` frontmatter. Used only as a hint for objects whose
                     catalog note is missing/unverified; never overrides the note-join.
    catalog          object -> catalog metadata (type, status, sap_note, note_verified,
                     s4_replacement, world, baseline_tier).

Run:  python build_index.py            # uses ./common/items + ./common/kb-index-catalog.yaml
      python build_index.py --items DIR --catalog FILE --out FILE
"""
import json
import os
import re
import sys

import yaml

# This script lives in mcp/build/; the KB data lives in mcp/common/ (= ../common).
HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.normpath(os.path.join(HERE, "..", "common"))
DEFAULT_ITEMS = os.path.join(COMMON, "items")
DEFAULT_CATALOG = os.path.join(COMMON, "kb-index-catalog.yaml")
DEFAULT_OUT = os.path.join(COMMON, "index.json")

# a `sap_note:` line whose trailing comment flags the note as not corroborated
UNVERIFIED_RE = re.compile(r"sap_note\s*:.*#.*unverified", re.I)
OBJECT_LINE_RE = re.compile(r"^\s*-\s*object\s*:\s*(\S+)", re.I)


def parse_frontmatter(path):
    """Return the YAML frontmatter dict of a chunk .md, or None if malformed."""
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return None


def load_unverified_objects(catalog_path):
    """Notes flagged UNVERIFIED live in YAML comments (stripped on parse), so scan raw."""
    unverified = set()
    cur = None
    for line in open(catalog_path, encoding="utf-8"):
        m = OBJECT_LINE_RE.match(line)
        if m:
            cur = m.group(1).upper()
        elif cur and UNVERIFIED_RE.search(line):
            unverified.add(cur)
    return unverified


def build(items_dir, catalog_path, out_path):
    catalog_raw = yaml.safe_load(open(catalog_path, encoding="utf-8"))["catalog"]
    unverified = load_unverified_objects(catalog_path)

    catalog = {}
    for c in catalog_raw:
        obj = str(c["object"]).upper()
        note = c.get("sap_note")
        catalog[obj] = {
            "type": c.get("type"),
            "status": c.get("status"),
            "sap_note": str(note) if note not in (None, "") else None,
            "note_verified": note not in (None, "") and obj not in unverified,
            "s4_replacement": c.get("s4_replacement"),
            "world": c.get("world"),
            "baseline_tier": c.get("baseline_tier"),
        }

    items = {}
    note_to_items = {}
    object_name_scan = {}
    for fn in sorted(os.listdir(items_dir)):
        if not fn.endswith(".md"):
            continue
        fm = parse_frontmatter(os.path.join(items_dir, fn))
        if not fm or "item_id" not in fm:
            sys.stderr.write(f"[index] skipped malformed chunk: {fn}\n")
            continue
        iid = fm["item_id"]
        notes = [str(n) for n in (fm.get("sap_notes") or [])]
        items[iid] = {
            "title": fm.get("title"),
            "pages": fm.get("pages"),
            "sap_notes": notes,
            "components": fm.get("components") or [],
        }
        for n in notes:
            note_to_items.setdefault(n, []).append(iid)
        for o in (fm.get("objects") or []):
            object_name_scan.setdefault(str(o).upper(), []).append(iid)

    # PRIMARY: resolve each catalog object via the SAP-Note join.
    object_to_items = {}
    for obj, meta in catalog.items():
        note = meta["sap_note"]
        verified = meta["note_verified"]
        # only trust the note-join when the catalog note is present AND corroborated
        primary = note_to_items.get(note, []) if (note and verified) else []
        object_to_items[obj] = {
            "note_used": note if (note and verified) else None,
            "note_verified": verified,
            "items": primary,
            "weak_matches": object_name_scan.get(obj, []),
        }

    index = {
        "meta": {
            "built_from": "common/items/*.md + common/kb-index-catalog.yaml",
            "method": "sap-note-join (primary) + object-name-scan (secondary, labeled)",
            "chunk_count": len(items),
            "catalog_object_count": len(catalog),
        },
        "items": items,
        "note_to_items": note_to_items,
        "object_to_items": object_to_items,
        "object_name_scan": object_name_scan,
        "catalog": catalog,
    }
    json.dump(index, open(out_path, "w", encoding="utf-8"), indent=2)
    resolved = sum(1 for v in object_to_items.values() if v["items"])
    sys.stderr.write(
        f"[index] {len(items)} chunks, {len(catalog)} catalog objects, "
        f"{resolved} resolved via note-join -> {out_path}\n")
    return index


def main():
    args = sys.argv[1:]

    def opt(flag, default):
        return args[args.index(flag) + 1] if flag in args else default

    build(opt("--items", DEFAULT_ITEMS),
          opt("--catalog", DEFAULT_CATALOG),
          opt("--out", DEFAULT_OUT))


if __name__ == "__main__":
    main()
