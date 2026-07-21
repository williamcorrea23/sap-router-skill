"""kb_impl.py — private implementation of the Simplification-List knowledge layer.

This module is the SWAPPABLE layer behind the MCP tool contract. It holds all the
business logic (note-join lookup, note index, free-text search) over the markdown chunk
store. It deliberately imports NO MCP code, so the lookup method can later change
(grep -> note-join -> SQLite -> vectors) without touching the server or any consumer.

Data it reads (all under common/):
  index.json        the note-join index (see build_index.py)
  items/<id>.md     per-item chunks (frontmatter + body)

Public functions: lookup(), by_note(), search(). They return plain dicts/lists of
JSON-serializable primitives — no exceptions leak to consumers; a miss is data, not an
error (the KB only enriches fix-derivation; a blank lookup must degrade gracefully).
"""
import json
import os
import re
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(HERE, "common")
INDEX_PATH = os.path.join(COMMON, "index.json")
ITEMS_DIR = os.path.join(COMMON, "items")


@lru_cache(maxsize=1)
def _index():
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def _body(item_id):
    """Return the markdown body of a chunk (frontmatter stripped), or '' if missing."""
    path = os.path.join(ITEMS_DIR, f"{item_id}.md")
    if not os.path.isfile(path):
        return ""
    text = open(path, encoding="utf-8").read()
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def _note_url(note):
    """Synthesize the SAP Note URL from its number (docling doesn't extract PDF links).
    Requires an S-user login to open; constructed, not scraped."""
    return f"https://me.sap.com/notes/{str(note).strip()}"


def _item_dict(item_id, full=False):
    """Assemble the public item record from the index metadata (+ body if full)."""
    meta = _index()["items"].get(item_id, {})
    notes = meta.get("sap_notes", [])
    rec = {
        "item_id": item_id,
        "title": meta.get("title"),
        "pages": meta.get("pages"),
        "sap_notes": notes,
        "note_urls": [_note_url(n) for n in notes],
        "components": meta.get("components", []),
    }
    if full:
        rec["body"] = _body(item_id)
    return rec


def lookup(object: str, full: bool = True) -> dict:
    """Resolve a single SAP object (table/field/FM name) to its Simplification item(s).

    object -> catalog SAP Note -> item(s) citing that note. Exact-key, deterministic.
    Returns a dict; never raises. On a miss, found=false with a clear, actionable message.
    """
    if not object or not isinstance(object, str):
        return {"object": object, "found": False, "note_used": None, "items": [],
                "message": "empty or invalid object name."}
    obj = object.strip().upper()
    idx = _index()
    entry = idx["object_to_items"].get(obj)

    if entry is None:
        return {
            "object": obj, "found": False, "note_used": None, "items": [],
            "message": (f"'{obj}' is not in the simplification catalog. No tracked "
                        "S/4HANA simplification references it. Treat as not-affected, "
                        "or verify manually if you suspect coverage is incomplete."),
        }

    item_ids = entry.get("items", [])
    if item_ids:
        items = [_item_dict(i, full=full) for i in item_ids]
        return {
            "object": obj, "found": True, "note_used": entry.get("note_used"),
            "items": items,
            "message": (f"{len(items)} Simplification item(s) cite SAP Note "
                        f"{entry.get('note_used')} for {obj}. Read the body/page "
                        "citation and derive the variant-correct fix for THIS statement; "
                        "the item is evidence, not a prescribed answer."),
        }

    # In-catalog but the note-join yielded nothing (note missing or flagged unverified).
    weak = entry.get("weak_matches", [])
    note_verified = entry.get("note_verified", False)
    cat = idx.get("catalog", {}).get(obj, {})
    raw_note = cat.get("sap_note")
    if raw_note and not note_verified:
        why = (f"catalog SAP Note {raw_note} for {obj} is flagged UNVERIFIED and was "
               "not used for the join")
    else:
        why = f"no SAP Note is cataloged for {obj}"
    weak_hint = (f" Weak object-name matches (verify, low confidence): {weak}."
                 if weak else "")
    status = cat.get("status")
    return {
        "object": obj, "found": False, "note_used": None, "items": [],
        "message": (f"No Simplification item resolved for {obj} ({why}; catalog status "
                    f"= {status}). Treat as not-affected, or verify manually.{weak_hint}"),
    }


def by_note(note: str) -> list:
    """Return all Simplification items citing a given 7-digit SAP Note number.

    Metadata only (item_id, title, pages, sap_notes, components). Never raises.
    """
    n = str(note).strip()
    ids = _index()["note_to_items"].get(n, [])
    return [_item_dict(i, full=False) for i in ids]


def search(query: str, limit: int = 5) -> list:
    """Free-text search over item titles + bodies. Use for the not-yet-cataloged /
    multi-hop case (e.g. exploring 'pricing API' when no exact object key applies).

    Returns up to `limit` ranked hits: item_id, title, pages, and a short snippet.
    Never raises; an empty list means no match.
    """
    if not query or not isinstance(query, str):
        return []
    terms = [t for t in re.split(r"\s+", query.strip().lower()) if t]
    if not terms:
        return []
    idx = _index()
    scored = []
    for item_id, meta in idx["items"].items():
        title = (meta.get("title") or "").lower()
        body = _body(item_id).lower()
        hay = title + "\n" + body
        # score: title hits weighted higher than body hits
        score = sum(3 * title.count(t) + body.count(t) for t in terms)
        if score and all(t in hay for t in terms):  # require every term to appear
            scored.append((score, item_id, meta, body))
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, item_id, meta, body in scored[:max(1, int(limit))]:
        out.append({
            "item_id": item_id,
            "title": meta.get("title"),
            "pages": meta.get("pages"),
            "score": score,
            "snippet": _snippet(body, terms),
        })
    return out


def _snippet(body, terms, width=160):
    """A short context window around the first matched term."""
    low = body.lower()
    pos = min((low.find(t) for t in terms if low.find(t) != -1), default=-1)
    if pos == -1:
        return body[:width].strip().replace("\n", " ")
    start = max(0, pos - width // 3)
    return ("…" if start else "") + body[start:start + width].strip().replace("\n", " ") + "…"
