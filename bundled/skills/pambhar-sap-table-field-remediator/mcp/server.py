#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["fastmcp>=2.0", "pyyaml>=6.0"]
# ///
"""server.py — FastMCP server exposing the Simplification-List knowledge layer.

Run it either way:
  • venv:  /path/to/.venv/bin/python server.py        (deps pre-installed)
  • uv:    uv run --no-project server.py               (deps auto-bootstrapped from the
                                                        PEP 723 block above — no venv)
The plugin launches it via `uv run`, so an end user needs no venv or pip.

This is the ONLY public surface of the knowledge layer. Consumer skills call these
MCP tools and nothing else; the chunk store, the index, and the note-join method are
private implementation details (see kb_impl.py) that can change without any consumer
noticing. Keep this file thin — all logic lives in kb_impl.

Transport: local stdio. Register with Claude Code:
    claude mcp add --transport stdio simplification-kb -- \
        <abs path to python> <abs path to this file>

The tool docstrings ARE the contract the calling LLM sees. Write them as crisp usage
instructions, not internals.
"""
from fastmcp import FastMCP

import kb_impl

mcp = FastMCP("simplification-kb")


@mcp.tool
def lookup(object: str, full: bool = True) -> dict:
    """Look up what changes for one SAP object in S/4HANA, with a page citation.

    Use this when deriving a fix for a flagged custom-code statement that accesses a SAP
    table, field, or function-module. Pass the exact object name (e.g. "BSEG", "MATNR",
    "KONV", "VBUK"). The tool joins the object to its SAP Note and returns the matching
    Simplification-List item(s) — title, page range, and full markdown body.

    This is EVIDENCE, not an answer. The body tells you what changed and where to read;
    YOU derive the variant-correct fix for the specific statement (the right target
    depends on how the code uses the object, not just the object name). When multiple
    items are returned, disambiguate by reading their titles/bodies.

    Args:
        object: exact SAP object name (case-insensitive). Tables, fields, FMs, BAPIs.
        full:   include the full markdown body (default True); pass False for metadata only.

    Returns a dict:
        {object, found, note_used, items: [{item_id, title, pages, sap_notes,
         components, body?}], message}
    On a miss (object not affected / not cataloged): found=false, items=[], and a
    message telling you to treat it as not-affected or verify. A miss is normal and safe
    — it never means the tool failed.
    """
    return kb_impl.lookup(object, full=full)


@mcp.tool
def by_note(note: str) -> list:
    """List the Simplification-List items that cite a given SAP Note number.

    Use this to pivot from a SAP Note (7-digit, e.g. "2270333") to the item(s) that
    reference it — handy when a code comment or another item points you at a note.
    Returns metadata only (item_id, title, pages, sap_notes, components); call lookup or
    search if you need the full body. Empty list = no item cites that note.
    """
    return kb_impl.by_note(note)


@mcp.tool
def search(query: str, limit: int = 5) -> list:
    """Free-text search across Simplification-List item titles and bodies.

    Use this for the exploratory / multi-hop case when you do NOT have an exact object
    key — e.g. "pricing API", "business partner", "material ledger". Returns up to
    `limit` ranked hits: item_id, title, page range, and a short snippet. Follow up with
    lookup/by_note to read the full item. Empty list = no match.
    """
    return kb_impl.search(query, limit=limit)


if __name__ == "__main__":
    mcp.run()  # stdio transport
