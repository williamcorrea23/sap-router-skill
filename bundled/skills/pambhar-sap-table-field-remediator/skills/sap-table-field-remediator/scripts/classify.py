#!/usr/bin/env python3
"""classify.py — turn detected DB-access statements into classified findings.

Reads detect.js JSON, looks each accessed object up in the catalog, and assigns the
THREE composed axes per finding:
  - world     (must-I-fix; from catalog)
  - category  (syntactic/structural/semantic/functional — the playbook key)
  - tier+action (the SCORED output: T1->auto_apply, T2->propose, T3->escalate)

It does the deterministic floor itself (static tables, clusters, native SQL, dynamic
targets resolvable by simple constant-propagation, MATNR offset-slice writes), suppresses
the precision traps (VALID / DECLUSTERED_SAME_NAME reads / World-B), and emits `verify`
for A-verify/B-verify. Anything it can't resolve alone (unresolved dynamic target,
read-only offset judgment) is listed under `escalations` for the LLM — the report stays
valid either way.

The auto_apply SAFETY guarantee is NOT enforced here — guard.py is the structural backstop
(it re-derives and downgrades). classify.py sets the *intended* action.

Usage:
  node detect.js <src> | python3 classify.py [--catalog P] > classified.json
  python3 classify.py --detect detect.json [--catalog P]
"""
from __future__ import annotations

import json
import os
import re
import sys

import catalog as catalog_mod
import crv as crv_mod

# CRV successor dictionary (released-target lookup). OPTIONAL — {} if the file is absent,
# in which case every enrichment below silently no-ops (catalog-only behaviour). Set once
# by classify(); a target dictionary ONLY (never a world/tier source — see crv.py).
CRV: dict = {}

WRITE_ACCESS = {"write", "native_write"}
# statuses whose objects still read fine -> never a must-fix on a plain read
SUPPRESS_READ_STATUS = {"VALID", "DECLUSTERED_SAME_NAME"}
TIER_ACTION = {"T1": "auto_apply", "T2": "propose", "T3": "escalate"}

OBJ_TYPE_MAP = {
    "table": "table",
    "field": "field",
    "bapi": "bapi",
    "function_module": "function_module",
}


# --------------------------------------------------------------------------- #
# Source-text helpers (auxiliary resolution only — detection is abaplint's job)
# --------------------------------------------------------------------------- #
def read_source(path: str) -> str:
    try:
        return open(path, "r").read()
    except OSError:
        return ""


def resolve_constant(src: str, var: str) -> str | None:
    """Light constant-propagation for dynamic table names.

    Handles:  var = 'LIT'.   |   DATA/CONSTANTS var ... VALUE 'LIT'   |
              CONCATENATE a b ... INTO var   (recursively resolved)
    """
    var = var.strip()
    up = var.upper()

    # CONCATENATE a b c INTO var
    m = re.search(
        r"CONCATENATE\s+(.+?)\s+INTO\s+" + re.escape(var) + r"\b",
        src,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        parts = m.group(1).split()
        out = []
        for p in parts:
            if p.startswith("'") and p.endswith("'"):
                out.append(p.strip("'"))
            else:
                r = resolve_constant(src, p)
                if r is None:
                    return None
                out.append(r)
        return "".join(out)

    # direct literal assignment:  var = 'LIT'.
    m = re.search(re.escape(var) + r"\s*=\s*'([^']*)'", src, re.IGNORECASE)
    if m:
        return m.group(1)

    # DATA/CONSTANTS var ... VALUE 'LIT'
    m = re.search(
        r"\b" + re.escape(var) + r"\b[^.\n]*?VALUE\s+'([^']*)'",
        src,
        re.IGNORECASE,
    )
    if m:
        return m.group(1)
    return None


def changed_fields(cat: dict) -> set:
    """Catalogued fields whose length/value CHANGED in S/4 (MATNR 18->40, VBTYP CHAR1->4).

    These are the ONLY fields a plain assignment/comparison can silently break, so they
    gate the field-level detection (kept tiny -> precision stays high)."""
    return {o for o, e in cat.items()
            if e.get("type") == "field" and e.get("status") == "CHANGED"}


def resolve_changed_field(src: str, expr: str | None, changed: set) -> str | None:
    """Return the catalogued CHANGED field an expression's leaf refers to, or None.

    Matches directly on the leaf name (gs_mseg-matnr -> MATNR; vbtyp -> VBTYP), else
    traces a `leaf TYPE|LIKE <tab>-<field>` declaration to a changed field."""
    if not expr:
        return None
    leaf = expr.strip().split("-")[-1].strip()
    if not leaf:
        return None
    if leaf.upper() in changed:
        return leaf.upper()
    m = re.search(r"\b" + re.escape(leaf) + r"\b\s+(?:TYPE|LIKE)\s+([A-Za-z_][\w-]*)",
                  src, re.IGNORECASE)
    if m:
        f = m.group(1).split("-")[-1].upper()
        if f in changed:
            return f
    return None


def truncating_target(src: str, expr: str | None, field: str) -> bool:
    """True if an assignment target is a fixed-length char SHORTER than the field's S/4
    length (40 for MATNR) -> the extended value is silently truncated.

    Conservative: a target typed AS the field (TYPE matnr / LIKE x-matnr) is safe; only an
    explicit short fixed length flags. Unknown -> False (never over-flag)."""
    if not expr:
        return False
    leaf = expr.strip().split("-")[-1].strip()
    if re.search(r"\b" + re.escape(leaf) + r"\b\s+(?:TYPE|LIKE)\s+[A-Za-z_][\w-]*"
                 + re.escape(field), src, re.IGNORECASE):
        return False  # typed as the field itself -> no truncation
    m = re.search(r"\b" + re.escape(leaf) + r"\b\s*\(\s*(\d+)\s*\)", src)
    if m:
        return int(m.group(1)) < 40
    m = re.search(r"\b" + re.escape(leaf) + r"\b\s+TYPE\s+c\s+LENGTH\s+(\d+)",
                  src, re.IGNORECASE)
    if m:
        return int(m.group(1)) < 40
    return False


def base_field_of_offset(src: str, base_var: str) -> str | None:
    """Trace an offset base variable's declared type to a catalogued field.

    e.g. `DATA gv_matnr TYPE mara-matnr`  or  `matnr LIKE mara-matnr` -> MATNR.
    Conservative: returns the field token if the declared type clearly names it.
    """
    if not base_var:
        return None
    # strip a struct prefix:  wa-matnr -> matnr
    leaf = base_var.split("-")[-1]
    # declaration of the leaf var with a TYPE/LIKE referencing <tab>-<field> or <field>
    pat = (
        r"\b" + re.escape(leaf) + r"\b\s+(?:TYPE|LIKE)\s+([a-zA-Z_][\w-]*)"
    )
    for m in re.finditer(pat, src, re.IGNORECASE):
        typ = m.group(1)
        field = typ.split("-")[-1].upper()
        if field in ("MATNR",):  # length-changed fields that break offset access
            return field
    # also: the var name itself ends in a known field (gv_matnr)
    if leaf.upper().endswith("MATNR"):
        return "MATNR"
    return None


# --------------------------------------------------------------------------- #
# Classification core
# --------------------------------------------------------------------------- #
def category_for(status: str, tier: str | None, access: str, escalated: bool) -> str | None:
    if access in WRITE_ACCESS and escalated:
        return "functional"  # write to a broken object -> redesign (e.g. KONV write)
    if tier == "T1":
        return "syntactic"
    if tier == "T2":
        return "structural"
    if tier == "T3":
        return "semantic" if status == "RESTRUCTURED" else "functional"
    return None


def intent_question_for(obj: str, category: str | None, entry: dict) -> str:
    fp = (entry.get("fix_pattern") or "").strip()
    if category == "semantic":
        return (
            f"{obj} is restructured in S/4HANA ({entry.get('s4_replacement')}). "
            f"What is this read's intent — full line-item granularity, or is the "
            f"aggregated/Universal-Journal target sufficient? Confirm key/ledger semantics "
            f"before redirecting. ({fp})"
        )
    if category == "functional":
        return (
            f"{obj} is removed/abolished in S/4HANA; there is no 1:1 target. "
            f"What business capability does this serve, and should it be redesigned onto "
            f"{entry.get('s4_replacement') or 'a released API / CDS'} or handed off? ({fp})"
        )
    return (
        f"{obj} changes in S/4HANA. Confirm the intended target and semantics before fixing. ({fp})"
    )


def preferred_replacement(entry: dict, tier: str | None) -> str | None:
    """Recommended remediation target, released-API-first.

    Deloitte expert review (2026-06-30, Bishnu Trivedi): the clean-core-correct target
    is the RELEASED CDS API, not the raw successor table — a SELECT on ACDOCA works but
    I_JournalEntryItem is the sanctioned forward path. So for structural/semantic/
    functional findings (T2/T3) we surface the released CDS view when the catalog has
    one. The T1 SYNTACTIC auto-apply is the deliberate exception: there the successor
    table is a field-identical 1:1 (KONV -> PRCD_ELEMENTS) and IS the mechanical fix, so
    its compat view (V_KONV) would be a wrong, non-applicable target. Falls back to
    whichever target exists. See working-notes/DECISIONS.md [2026-07-01].
    """
    s4 = entry.get("s4_replacement")
    s4 = s4 if (s4 and s4 != "<same>") else None
    cds = entry.get("cds_view")
    # In-place length/value change (MATNR 18->40, VBTYP CHAR1->CHAR4): the fix is
    # adjusting the access in place, not re-pointing to a CDS view — keep the object.
    if entry.get("status") == "CHANGED":
        return s4 or cds or None
    if tier in ("T2", "T3") and cds:
        return cds
    return s4 or cds or None


def finding(file, line, obj, entry, tier, action, category, escalated,
            access="read", must_escalate=False):
    replacement = preferred_replacement(entry, tier)
    # CRV enrichment (optional, advisory): the hand-catalog target WINS; CRV only fills a
    # gap and adds an authoritative citation / flags a divergence. Target dict only.
    crv_hit = CRV.get(obj.upper()) if obj else None
    crv_note = ""
    if crv_hit and crv_hit.get("preferred"):
        crv_tgt = crv_hit["preferred"]
        crv_ty = crv_hit.get("preferred_type")
        if replacement is None:
            # FILL — catalog had no target: adopt CRV's released successor (all tiers).
            replacement = crv_tgt
            crv_note = f" [target from CRV: {crv_tgt} ({crv_ty}); SAP cloudification repo]"
        elif crv_tgt.upper() == str(replacement).upper():
            # CONFIRM — CRV agrees with the catalog target (all tiers).
            crv_note = f" [confirmed by CRV: {crv_tgt}]"
        elif tier in ("T2", "T3") and entry.get("status") != "CHANGED":
            # DIVERGENCE FLAG — only where our target is a genuine forward choice.
            # Suppressed for T1 and status-CHANGED: there the raw successor table (e.g.
            # KONV->PRCD_ELEMENTS) is the intended target and CRV's CDS view would emit a
            # spurious "confirm vs" note on every such case. See DECISIONS.md [2026-07-07].
            crv_note = f" [CRV lists released successor {crv_tgt} ({crv_ty}); confirm vs {replacement}]"
        # else (T1 / status-CHANGED divergence): suppress — no CRV note.
    rationale = (
        f"{obj}: status {entry.get('status')} (world {entry.get('world')}). "
        f"{(entry.get('fix_pattern') or '').strip()}{crv_note}"
    )
    # Provenance: a per-client custom-override entry wins over the standard catalog.
    # Marker goes into the rationale string only — the finding schema is closed (12 keys).
    if entry.get("origin") == "custom":
        rationale = "[custom override] " + rationale + " (per client custom override)."
    iq = None
    if action == "escalate" or tier == "T3":
        iq = intent_question_for(obj, category, entry)
    return {
        "file": file,
        "line": line,
        "object": obj,
        "object_type": OBJ_TYPE_MAP.get(entry.get("type", "table"), "table"),
        "world": entry.get("world"),
        "tier": tier,
        "action": action,
        "category": category,
        "replacement": replacement,
        "rationale": rationale,
        "intent_question": iq,
        "patch": None,
        # internal guard metadata (stripped before the schema report is written)
        "_meta": {
            "access": access,
            "baseline_tier": entry.get("baseline_tier"),
            "status": entry.get("status"),
            "escalated": escalated,
            "must_escalate": must_escalate,
        },
    }


def classify(detect: dict, cat: dict, crv: dict | None = None) -> dict:
    global CRV
    CRV = crv if crv is not None else crv_mod.load()  # {} if no crv-successors.json
    findings = []
    escalations = []
    suppressed = []
    review_queue = []  # accesses the detector SAW but the catalog can't classify
                       # (not_in_catalog). NOT silently dropped: surfaced for KB-search
                       # + expert decide-or-skip. See DECISIONS.md [2026-06-27].
    changed = changed_fields(cat)  # length/value-changed fields (MATNR, VBTYP) for field-level faults

    for st in detect["statements"]:
        file = st["file"]
        line = st["line"]
        access = st["access"]
        kind = st["kind"]
        src = read_source(file)

        # --- offset/length slice access (MATNR-extension risk) ------------ #
        if kind == "offset_access":
            base = st["offsets"][0].get("base") if st["offsets"] else None
            field = base_field_of_offset(src, base)
            if not field or field not in cat:
                continue  # offset on a non-length-changed field -> not a finding
            entry = cat[field]
            if access == "slice_assign":
                # writing a sub-range INTO another field propagates the 18-char
                # assumption downstream -> high-confidence semantic escalation.
                f = finding(file, line, field, entry, "T3", "escalate", "semantic", True,
                            access="slice_assign", must_escalate=True)
                findings.append(f)
                escalations.append(
                    {"file": file, "line": line, "object": field, "reason": "matnr_offset_slice",
                     "note": "Offset slice on extended field; confirm the layout assumption."}
                )
            else:
                # read-only prefix compare (e.g. +0(8) leading-zero check) — needs
                # judgment; do NOT auto-flag (protects precision). Hand to the LLM.
                escalations.append(
                    {"file": file, "line": line, "object": field, "reason": "matnr_offset_read",
                     "note": "Read-only offset compare; LLM to judge if it breaks under length 40."}
                )
            continue

        # --- field-level faults on non-DB statements (length/value-changed fields) --- #
        # Worst-fault-wins [DECISIONS.md 2026-07-01]: these surface faults the DB-access
        # scan can't see (MATNR truncation on assign, VBTYP single-char literal compare).
        # Gated to catalogued CHANGED fields, so precision holds.
        if kind == "field_assign":
            fld = resolve_changed_field(src, st.get("source_expr"), changed)
            if fld and fld in cat and truncating_target(src, st.get("target_expr"), fld):
                entry = cat[fld]
                tier = entry.get("baseline_tier") or "T1"
                f = finding(file, line, fld, entry, tier, TIER_ACTION.get(tier, "propose"),
                            category_for(entry.get("status"), tier, "read", False), False,
                            access="assign", must_escalate=False)
                findings.append(f)
            continue

        if kind == "literal_compare":
            fld = next((r for r in (resolve_changed_field(src, fx, changed)
                                    for fx in st.get("fields", [])) if r), None)
            if fld and fld in cat:
                entry = cat[fld]
                tier = entry.get("baseline_tier") or "T2"
                f = finding(file, line, fld, entry, tier, TIER_ACTION.get(tier, "propose"),
                            category_for(entry.get("status"), tier, "read", False), False,
                            access="compare", must_escalate=False)
                findings.append(f)
            continue

        # --- resolve the accessed object (handle dynamic targets) --------- #
        raw = st["objects"][0] if st["objects"] else None
        if raw is None:
            continue
        resolved_dynamic = False
        if st.get("dynamic"):
            var = raw.strip("()").strip()
            val = resolve_constant(src, var)
            if val:
                raw = val
                resolved_dynamic = True
            else:
                escalations.append(
                    {"file": file, "line": line, "object": raw, "reason": "unresolved_dynamic",
                     "note": f"Dynamic DB target {raw}; LLM to resolve the table name and classify."}
                )
                continue
        obj = raw.upper()

        # --- EXEC SQL native -> statement-level smell -> sibling handoff -- #
        if kind == "exec_sql":
            entry = cat.get(obj, {"world": None, "type": "table", "status": "?"})
            exec_rationale = (f"Native EXEC SQL on {obj}: statement-level portability smell; "
                              f"hand off to the statement-smell sibling skill (Skill-4).")
            if entry.get("origin") == "custom":
                exec_rationale = "[custom override] " + exec_rationale + " (per client custom override)."
            f = {
                "file": file, "line": line, "object": obj,
                "object_type": OBJ_TYPE_MAP.get(entry.get("type", "table"), "table"),
                "world": entry.get("world"), "tier": None, "action": "route_to_sibling",
                "category": None,
                "replacement": None,
                "rationale": exec_rationale,
                "intent_question": None, "patch": None,
                "_meta": {"access": access, "baseline_tier": None, "status": entry.get("status"),
                          "escalated": False, "must_escalate": False},
            }
            findings.append(f)
            continue

        # --- catalog lookup ------------------------------------------------ #
        entry = cat.get(obj)
        if entry is None:
            # Unknown != safe. The catalog is a PARTIAL shortlist, so a miss means
            # "we don't know", not "not affected". Route to the review queue (KB-search
            # + expert decide) instead of dropping it. See DECISIONS.md [2026-06-27].
            # CRV enrichment: attach an authoritative released successor as a starting
            # target for the reviewer/LLM (advisory; None if CRV doesn't know it).
            crv_hit = CRV.get(obj)
            review_queue.append({"file": file, "line": line, "object": obj,
                                 "object_type": "table",  # unknown object; table-level by default
                                 "access": access, "reason": "not_in_catalog",
                                 "crv_successor": crv_hit.get("preferred") if crv_hit else None,
                                 "crv_successor_type": crv_hit.get("preferred_type") if crv_hit else None,
                                 "crv_state": crv_hit.get("state") if crv_hit else None})
            continue
        status = entry.get("status")
        world = entry.get("world")

        # suppress precision traps: still-valid / declustered-same-name reads
        if status in SUPPRESS_READ_STATUS and access not in WRITE_ACCESS:
            suppressed.append({"file": file, "line": line, "object": obj,
                               "reason": f"{status}_read_suppressed"})
            continue
        # World-B clean-core modernization that still works -> not a must-fix
        if status == "MODERNIZATION_ONLY" and world == "B":
            suppressed.append({"file": file, "line": line, "object": obj, "reason": "world_b_modernization"})
            continue

        # A-verify / B-verify -> verify only (never auto_apply)
        if world in ("A-verify", "B-verify"):
            f = finding(file, line, obj, entry, entry.get("baseline_tier"), "verify",
                        category_for(status, entry.get("baseline_tier"), access, False), False,
                        access=access, must_escalate=False)
            f["intent_question"] = None
            findings.append(f)
            continue

        # --- tier + escalation -------------------------------------------- #
        base_tier = entry.get("baseline_tier")
        escalated = False
        tier = base_tier
        if access in WRITE_ACCESS and status != "VALID":
            tier = "T3"  # writing to a removed/restructured object -> redesign
            escalated = True

        if tier is None:
            # cataloged but no tier (shouldn't happen for world-A must-fix) -> skip
            suppressed.append({"file": file, "line": line, "object": obj, "reason": "no_tier"})
            continue

        action = TIER_ACTION[tier]
        category = category_for(status, tier, access, escalated)
        must_esc = escalated or (base_tier in ("T2", "T3"))
        f = finding(file, line, obj, entry, tier, action, category, escalated,
                    access=access, must_escalate=must_esc)
        findings.append(f)
        if action == "escalate":
            escalations.append(
                {"file": file, "line": line, "object": obj, "reason": "tier3_escalate",
                 "category": category, "dynamic_resolved": resolved_dynamic,
                 "note": "Confirm intent_question + replacement; refine rationale."}
            )

    n_custom = sum(1 for f in findings if str(f.get("rationale", "")).startswith("[custom override]"))
    if n_custom:
        sys.stderr.write(f"[classify] {n_custom} finding(s) used a custom override\n")

    return {"findings": findings, "escalations": escalations,
            "suppressed": suppressed, "review_queue": review_queue}


def main() -> int:
    args = sys.argv[1:]
    cat_path = None
    detect_path = None
    if "--catalog" in args:
        i = args.index("--catalog"); cat_path = args[i + 1]; del args[i : i + 2]
    if "--detect" in args:
        i = args.index("--detect"); detect_path = args[i + 1]; del args[i : i + 2]

    detect = json.load(open(detect_path)) if detect_path else json.load(sys.stdin)
    cat = catalog_mod.load(cat_path)
    result = classify(detect, cat)
    result["scanned_files"] = detect.get("scanned_files", [])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
