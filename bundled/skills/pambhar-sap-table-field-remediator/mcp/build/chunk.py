#!/usr/bin/env python3
"""chunk.py — split a docling DoclingDocument JSON into per-simplification-item files.

Walks the doc in reading order; starts a new chunk at every section_header whose text
matches a simplification-item title (e.g. "3.22 S4TWL - Material Number Field Length
Extension"). Sub-headings (Symptom/Solution/...) are also level-1, so we key on the title
regex, not the level. Each chunk -> a Markdown file with YAML frontmatter:
  item_id, title, pages, sap_notes, components, objects (catalog tables/fields it mentions)
plus an index.json (object -> [item_id]) for the lookup tool.

Usage: python chunk.py <docling.json> [--out out] [--catalog PATH]
"""
import json, os, re, sys

from docling_core.types.doc import DoclingDocument

ITEM_RE = re.compile(r"^\s*(\d+(?:\.\d+)+)\s+(S4TWL|ABAPTWL|SWTL)\b\s*[-–]?\s*(.*)", re.I)
NOTE_RE = re.compile(r"\b(\d{7})\b")
COMP_RE = re.compile(r"Application\s+Components?\s*:?\s*(.+)", re.I)


def load_catalog_objects(path):
    try:
        import yaml
        cat = yaml.safe_load(open(path))["catalog"]
        return sorted({str(c["object"]).upper() for c in cat}, key=len, reverse=True)
    except Exception as e:  # noqa
        sys.stderr.write(f"[chunk] no catalog ({e}); objects index will be empty.\n")
        return []


def page_of(item):
    return item.prov[0].page_no if getattr(item, "prov", None) else None


def main():
    src = sys.argv[1]
    # This script lives in mcp/build/; KB data lives in mcp/common/ (= ../common).
    # Default writes chunks + a basic index.json in place; build_index.py then
    # overwrites index.json with the richer note-join index. Override with --out/--catalog.
    HERE = os.path.dirname(os.path.abspath(__file__))
    out = os.path.normpath(os.path.join(HERE, "..", "common"))
    catalog = os.path.join(out, "simplification-list.yaml")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    if "--catalog" in sys.argv:
        catalog = sys.argv[sys.argv.index("--catalog") + 1]

    objects = load_catalog_objects(catalog)
    doc = DoclingDocument.model_validate(json.load(open(src)))

    chunks = []
    cur = None
    for item, _level in doc.iterate_items():
        label = str(getattr(item, "label", ""))
        text = getattr(item, "text", "") or ""
        pg = page_of(item)

        if label.endswith("section_header"):
            m = ITEM_RE.match(text)
            if m:
                num, _kind, rest = m.group(1), m.group(2), m.group(3).strip()
                cur = {"num": num, "title": text.strip(), "subtitle": rest,
                       "parts": [], "pages": set()}
                if pg:
                    cur["pages"].add(pg)
                chunks.append(cur)
                continue
            # sub-heading inside an item
            if cur is not None:
                cur["parts"].append(f"## {text.strip()}")
                if pg:
                    cur["pages"].add(pg)
            continue

        if cur is None:
            continue  # front matter / TOC before the first item
        if label.endswith(("page_header", "page_footer")):
            continue  # drop running headers/footers
        if label.endswith("table"):
            try:
                cur["parts"].append(item.export_to_markdown(doc))
            except Exception:
                pass
        elif text:
            cur["parts"].append(text.strip())
        if pg:
            cur["pages"].add(pg)

    os.makedirs(os.path.join(out, "items"), exist_ok=True)
    index = {}
    note_index = {}
    written = []
    for c in chunks:
        body = "\n\n".join(c["parts"]).strip()
        pages = sorted(p for p in c["pages"] if p)
        p_lo, p_hi = (pages[0], pages[-1]) if pages else (None, None)
        notes = sorted(set(NOTE_RE.findall(body + " " + c["title"])))
        cm = COMP_RE.search(body)
        comps = [x.strip() for x in re.split(r"[;,]", cm.group(1))][:8] if cm else []
        objs = sorted({o for o in objects if re.search(rf"\b{re.escape(o)}\b", body)})
        item_id = "SI-" + c["num"]

        fm = ["---",
              f"item_id: {item_id}",
              f"title: {json.dumps(c['title'])}",
              f"pages: {p_lo}-{p_hi}" if p_lo else "pages: null",
              f"sap_notes: [{', '.join(notes)}]",
              f"components: [{', '.join(comps)}]",
              f"objects: [{', '.join(objs)}]",
              "---", ""]
        with open(os.path.join(out, "items", f"{item_id}.md"), "w") as f:
            f.write("\n".join(fm) + body + "\n")
        written.append(item_id)
        for o in objs:
            index.setdefault(o, []).append(item_id)
        for n in notes:
            note_index.setdefault(n, []).append(item_id)

    json.dump({"object_to_items": index, "note_to_items": note_index,
               "items": written}, open(os.path.join(out, "index.json"), "w"), indent=2)

    sys.stderr.write(f"[chunk] {len(written)} item chunks -> {out}/items/\n")
    sys.stderr.write(f"[chunk] objects indexed: {len(index)}  "
                     f"(e.g. {dict(list(index.items())[:5])})\n")


if __name__ == "__main__":
    main()
