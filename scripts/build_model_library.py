#!/usr/bin/env python3
"""Model Library builder.

Two jobs:

  1. convert-split2 : turn the concrete v5 ZROUTER objects in deploy/split2 into a
                      valid abapGit repository layout under deploy/abapgit_full/.
                      Demonstrates the split2 -> abapGit migration (design doc section 8).

  2. generate       : stamp a parameterized template from model-library/ into a concrete
                      instance (TMPL identifier rename + {{value}} slot fill).
                      Demonstrates the generator workflow (design doc section 7).

Only CLAS / INTF / PROG are auto-converted. DDIC tables (.tabl) and function groups
(.fugr) need object-specific metadata (DD03P field lists, FUGR includes) and are listed
as a follow-up rather than emitted with wrong metadata.

Usage:
  python scripts/build_model_library.py convert-split2
  python scripts/build_model_library.py generate --template handler-concrete --token MM \
         --set ENTITY=MATERIAL --set BAPI_NAME=BAPI_MATERIAL_SAVEDATA
  python scripts/build_model_library.py validate
"""

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
SPLIT2_DIR = SKILL_DIR / "deploy" / "split2"
LIBRARY_DIR = SKILL_DIR / "model-library"
MANIFEST = LIBRARY_DIR / "manifest.json"

# abap_serializer lives next to this script.
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from abap_serializer import generate_abapgit, xml_escape
except ModuleNotFoundError:
    from scripts.abap_serializer import generate_abapgit, xml_escape  # type: ignore

# Object types we can convert reliably (source suffix -> abapGit type code).
CONVERTIBLE = {"clas": "CLAS", "intf": "INTF", "prog": "PROG"}
# Object types that need object-specific metadata; converted in a later pass.
DEFERRED = {"tabl", "fugr", "ddl"}

ABAPGIT_ROOT = """<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DEVC" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DATA>
    <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
    <STARTING_FOLDER>/src/</STARTING_FOLDER>
    <FOLDER_LOGIC>PREFIX</FOLDER_LOGIC>
    <IGNORE>
     <item>/manifest.json</item>
     <item>/README.md</item>
    </IGNORE>
   </DATA>
  </asx:values>
 </asx:abap>
</abapGit>
"""


def _package_devc(ctext: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<abapGit version="v1.0.0" serializer="LCL_OBJECT_DEVC" serializer_version="v1.0.0">\n'
        ' <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">\n'
        "  <asx:values>\n"
        "   <DEVC>\n"
        f"    <CTEXT>{ctext}</CTEXT>\n"
        "   </DEVC>\n"
        "  </asx:values>\n"
        " </asx:abap>\n"
        "</abapGit>\n"
    )


def _parse_object_file(path: Path):
    """From 'zcl_foo.clas.abap' return (name, suffix). None if not an object source."""
    parts = path.name.split(".")
    if len(parts) < 3 or parts[-1] != "abap":
        return None
    suffix = parts[-2].lower()
    name = ".".join(parts[:-2]).upper()
    return name, suffix


# --- DDIC table: DDL source -> abapGit .tabl.xml ------------------------------
# The repo's validated DDIC deploy path is DDL via ADT (scripts/deploy_all.py).
# This produces the abapGit-package sidecar so ZABAPGIT users get the table too.
# NOTE: generated offline; confirm with one ZABAPGIT round-trip before relying on it.

_DDL_LABEL_RE = re.compile(r"@EndUserText\.label\s*:\s*'([^']*)'")
_DDL_FIELD_RE = re.compile(
    r"^\s*(key\s+)?(\w+)\s*:\s*([A-Za-z0-9_.]+(?:\(\d+(?:,\d+)?\))?)\s*(not\s+null)?\s*;",
    re.IGNORECASE,
)


def _ddl_field_meta(type_token: str) -> dict:
    """Map a DDL type to abapGit DD03P attributes. Standard data elements are used
    for client / UUID / timestamp so no internal-length guesswork is needed."""
    t = type_token.lower()
    fixed = {"abap.clnt": "MANDT", "sysuuid_c32": "SYSUUID_C32", "abap.timestampl": "TIMESTAMPL"}
    if t in fixed:
        return {"ROLLNAME": fixed[t]}
    m = re.match(r"abap\.char\((\d+)\)", t)
    if m:
        return {"DATATYPE": "CHAR", "LENG": f"{int(m.group(1)):06d}"}
    m = re.match(r"abap\.numc\((\d+)\)", t)
    if m:
        return {"DATATYPE": "NUMC", "LENG": f"{int(m.group(1)):06d}"}
    m = re.match(r"abap\.dec\((\d+),(\d+)\)", t)
    if m:
        return {"DATATYPE": "DEC", "LENG": f"{int(m.group(1)):06d}",
                "DECIMALS": f"{int(m.group(2)):06d}"}
    if t == "abap.int4":
        return {"DATATYPE": "INT4", "LENG": "000010"}
    if t == "abap.string":
        return {"DATATYPE": "STRG", "LENG": "0000000000"}
    return {"ROLLNAME": type_token.upper()}


def _tabl_xml(name: str, ddl_text: str) -> str:
    label_m = _DDL_LABEL_RE.search(ddl_text)
    label = label_m.group(1) if label_m else name
    fields = []
    for line in ddl_text.splitlines():
        fm = _DDL_FIELD_RE.match(line)
        if fm:
            fields.append((fm.group(2).upper(), bool(fm.group(1)), _ddl_field_meta(fm.group(3))))

    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<abapGit version="v1.0.0" serializer="LCL_OBJECT_TABL" serializer_version="v1.0.0">',
           ' <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">',
           '  <asx:values>',
           '   <DD02V>',
           f'    <TABNAME>{name}</TABNAME>',
           '    <DDLANGUAGE>E</DDLANGUAGE>',
           '    <TABCLASS>TRANSP</TABCLASS>',
           f'    <DDTEXT>{xml_escape(label)}</DDTEXT>',
           '    <CONTFLAG>A</CONTFLAG>',
           '    <EXCLASS>1</EXCLASS>',
           '   </DD02V>',
           '   <DD09L>',
           f'    <TABNAME>{name}</TABNAME>',
           '    <AS4LOCAL>A</AS4LOCAL>',
           '    <TABKAT>0</TABKAT>',
           '    <TABART>APPL1</TABART>',
           '    <BUFALLOW>N</BUFALLOW>',
           '   </DD09L>',
           '   <DD03P_TABLE>']
    for pos, (fname, is_key, meta) in enumerate(fields, start=1):
        out.append('    <DD03P>')
        out.append(f'     <FIELDNAME>{fname}</FIELDNAME>')
        out.append(f'     <POSITION>{pos:04d}</POSITION>')
        if is_key:
            out.append('     <KEYFLAG>X</KEYFLAG>')
        out.append('     <ADMINFIELD>0</ADMINFIELD>')
        if "ROLLNAME" in meta:
            out.append(f'     <ROLLNAME>{meta["ROLLNAME"]}</ROLLNAME>')
        else:
            out.append(f'     <DATATYPE>{meta["DATATYPE"]}</DATATYPE>')
            out.append(f'     <LENG>{meta["LENG"]}</LENG>')
            if "DECIMALS" in meta:
                out.append(f'     <DECIMALS>{meta["DECIMALS"]}</DECIMALS>')
        out.append('    </DD03P>')
    out += ['   </DD03P_TABLE>', '  </asx:values>', ' </asx:abap>', '</abapGit>']
    return "\n".join(out) + "\n"


def convert_split2():
    out_dir = SKILL_DIR / "deploy" / "abapgit_full"
    src_dir = out_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / ".abapgit.xml").write_text(ABAPGIT_ROOT, encoding="utf-8")
    (src_dir / "package.devc.xml").write_text(
        _package_devc("ZROUTER v5 - generated from deploy/split2"), encoding="utf-8"
    )

    converted, deferred = [], []
    for path in sorted(SPLIT2_DIR.iterdir()):
        # DDIC table: DDL source -> abapGit .tabl.xml
        if path.name.endswith(".tabl.ddl"):
            tname = path.name[: -len(".tabl.ddl")].upper()
            xml = _tabl_xml(tname, path.read_text(encoding="utf-8", errors="replace"))
            (src_dir / f"{tname.lower()}.tabl.xml").write_text(xml, encoding="utf-8")
            converted.append(f"{tname} (TABL)")
            continue
        parsed = _parse_object_file(path)
        if not parsed:
            continue
        name, suffix = parsed
        if suffix == "tabl":
            # .tabl.abap is a comment stub; the .tabl.ddl sibling is authoritative.
            if not (SPLIT2_DIR / f"{name.lower()}.tabl.ddl").exists():
                deferred.append(path.name)
            continue
        if suffix not in CONVERTIBLE:
            # e.g. *.fugr.abap -- function groups need include decomposition (follow-up)
            deferred.append(path.name)
            continue
        obj_type = CONVERTIBLE[suffix]
        source = path.read_text(encoding="utf-8", errors="replace")
        files = generate_abapgit(name, obj_type, source, desc=name)
        for fname, content in files.items():
            (src_dir / fname).write_text(content, encoding="utf-8")
        converted.append(f"{name} ({obj_type})")

    print(f"Converted {len(converted)} objects into {src_dir}")
    for c in converted:
        print(f"  [OK] {c}")
    if deferred:
        print(f"\nDeferred {len(deferred)} objects (need object-specific metadata):")
        for d in deferred:
            print(f"  [SKIP] {d}")
    print("\nInstall on SAP: ZABAPGIT online/offline repo -> pull -> activate.")
    return 0


def _rename_token(text: str, token: str) -> str:
    """Case-preserving replace of the TMPL identifier slot with the target token."""
    text = re.sub(r"TMPL", token.upper(), text)
    text = re.sub(r"tmpl", token.lower(), text)
    return text


def _fill_slots(text: str, values: dict) -> str:
    def repl(m):
        key = m.group(1)
        if key not in values:
            raise SystemExit(f"Missing value for slot {{{{{key}}}}}. Pass --set {key}=...")
        return values[key]

    return re.sub(r"\{\{(\w+)\}\}", repl, text)


def generate(template_id: str, token: str, values: dict, out_root: Path):
    if not MANIFEST.exists():
        raise SystemExit(f"Manifest not found: {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next((t for t in manifest["templates"] if t["id"] == template_id), None)
    if not entry:
        ids = ", ".join(t["id"] for t in manifest["templates"])
        raise SystemExit(f"Unknown template '{template_id}'. Known: {ids}")

    # Required-slot check up front.
    for slot in entry.get("value_slots", []):
        if slot.get("required") and slot["name"] not in values:
            raise SystemExit(f"Template '{template_id}' requires slot {slot['name']}.")

    out_dir = out_root / token.lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    # A template entry plus its declared dependencies all get stamped.
    paths = [entry["path"]] + [
        d for d in entry.get("requires_paths", [])
    ]
    for rel in paths:
        src = LIBRARY_DIR / rel
        raw = src.read_text(encoding="utf-8", errors="replace")
        stamped = _fill_slots(_rename_token(raw, token), values)
        # Rename the file itself (TMPL -> token) and drop the abapGit .xml sidecar suffix
        # handling: keep the same two-file convention.
        new_name = _rename_token(src.name, token)
        (out_dir / new_name).write_text(stamped, encoding="utf-8")
        written.append(new_name)

    print(f"Generated instance '{token}' from template '{template_id}' -> {out_dir}")
    for w in written:
        print(f"  [OK] {w}")
    return 0


def validate():
    """Structural checks: manifest <-> files, abapGit filename convention."""
    problems = []
    if not (LIBRARY_DIR / ".abapgit.xml").exists():
        problems.append("missing model-library/.abapgit.xml")
    if not MANIFEST.exists():
        problems.append("missing model-library/manifest.json")
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for t in manifest["templates"]:
            p = LIBRARY_DIR / t["path"]
            if not p.exists():
                problems.append(f"template '{t['id']}' path missing: {t['path']}")
    # abapGit convention: every *.abap under src/ has a matching *.xml sidecar.
    src = LIBRARY_DIR / "src"
    if src.exists():
        for abap in src.rglob("*.abap"):
            xml = abap.with_suffix(".xml")
            if not xml.exists():
                problems.append(f"no metadata sidecar for {abap.relative_to(LIBRARY_DIR)}")
    if problems:
        print(f"VALIDATION FAILED ({len(problems)} issue(s)):")
        for p in problems:
            print(f"  [FAIL] {p}")
        return 1
    print("VALIDATION OK")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Model Library builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("convert-split2", help="Convert deploy/split2 to abapGit layout")
    sub.add_parser("validate", help="Structural checks on model-library")

    g = sub.add_parser("generate", help="Stamp a template into a concrete instance")
    g.add_argument("--template", required=True)
    g.add_argument("--token", required=True, help="Identifier replacing TMPL, e.g. MM")
    g.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                   help="Fill a {{KEY}} value slot (repeatable)")
    g.add_argument("--out", default=str(SKILL_DIR / "deploy" / "generated"))

    args = parser.parse_args()

    if args.cmd == "convert-split2":
        return convert_split2()
    if args.cmd == "validate":
        return validate()
    if args.cmd == "generate":
        values = {}
        for pair in args.set:
            if "=" not in pair:
                raise SystemExit(f"--set expects KEY=VALUE, got '{pair}'")
            k, v = pair.split("=", 1)
            values[k] = v
        return generate(args.template, args.token, values, Path(args.out))
    return 1


if __name__ == "__main__":
    sys.exit(main())
