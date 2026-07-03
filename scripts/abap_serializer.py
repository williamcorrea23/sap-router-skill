#!/usr/bin/env python3
"""
ABAP Serializer — multi-format ABAP object packer/unpacker.

Three output formats, all modeled on real SAP serialization tools:
  .nugg    — single-file XML (abapblog/fidley format)
  abapgit  — two-file: XML metadata + .abap source
  xml      — ZDOWNLOAD-style full-metadata XML

Usage:
  python abap_serializer.py generate --source FILE --name OBJNAME --type CLAS|PROG|INTF --format nugg|abapgit|xml --output DIR
  python abap_serializer.py extract  --input FILE.nugg|DIR --output DIR
  python abap_serializer.py split    --source FILE --output DIR
  python abap_serializer.py package  --source FILE --name OBJNAME --type CLAS --output DIR
"""

import argparse
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


# ---------------------------------------------------------------------------
# Constants — ZDOWNLOAD-style metadata tables
# ---------------------------------------------------------------------------
ABAP_TYPES = {
    "CLAS": {"su": "1", "rstat": "K", "tab": "VSEOCLASS"},
    "INTF": {"su": "1", "rstat": "K", "tab": "VSEOINTERF"},
    "PROG": {"su": "1", "rstat": "K", "tab": "TRDIR"},
    "FUGR": {"su": "1", "rstat": "K", "tab": "TFDIR"},
    "TABL": {"su": "1", "rstat": "K", "tab": "DD02L"},
    "TYPE": {"su": "1", "rstat": "K", "tab": "DD40L"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_ts():
    """ISO timestamp for session header."""
    from datetime import datetime
    return datetime.now().isoformat(timespec="seconds")


def _md5(content: str) -> str:
    import hashlib
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def _safe_filename(name: str, suffix: str) -> str:
    return f"{name.lower()}.{suffix}"


def _split_abap_objects(source: str):
    """Split a multi-object ABAP file into individual CLASS/INTERFACE/FUNCTION stanzas.

    Returns list of (kind, name, code) tuples.
    """
    # Normalize line endings
    source = source.replace("\r\n", "\n")

    objects = []
    # Match CLASS definitions
    class_re = re.compile(
        r'^\s*(CLASS)\s+(Z?\w+)\s+(DEFINITION|IMPLEMENTATION)\b',
        re.MULTILINE | re.IGNORECASE,
    )
    # Match INTERFACE definitions (handles both "INTERFACE zif_foo " and "INTERFACE zif_foo.")
    intf_re = re.compile(
        r'^\s*(INTERFACE)\s+(Z?\w+)',
        re.MULTILINE | re.IGNORECASE,
    )
    # Match FUNCTION
    func_re = re.compile(
        r'^\s*(FUNCTION)\s+(Z?\w+(?:_FM)?)\b',
        re.MULTILINE | re.IGNORECASE,
    )

    seen = set()

    for m in class_re.finditer(source):
        kind = m.group(1).upper()
        name = m.group(2).upper()
        key = f"{kind}:{name}"
        if key in seen:
            continue
        seen.add(key)

        # Extract block — from this CLASS keyword to the next CLASS/INTERFACE/FUNCTION or EOF
        code, end = _extract_block(source, m.start())
        objects.append((kind, name, code))

    for m in intf_re.finditer(source):
        kind = m.group(1).upper()
        name = m.group(2).upper()
        key = f"{kind}:{name}"
        if key in seen:
            continue
        seen.add(key)

        code, end = _extract_block(source, m.start())
        objects.append((kind, name, code))

    for m in func_re.finditer(source):
        kind = m.group(1).upper()
        name = m.group(2).upper()
        key = f"{kind}:{name}"
        if key in seen:
            continue
        seen.add(key)

        code, end = _extract_block(source, m.start(), is_function=True)
        objects.append((kind, name, code))

    return objects


def _extract_block(source: str, start: int, is_function=False):
    """Extract code block from start position to next top-level CLASS/INTERFACE/FUNCTION or EOF."""
    # For functions, the block ends with ENDFUNCTION.
    if is_function:
        end_match = re.search(r'^\s*ENDFUNCTION\.', source[start:], re.MULTILINE | re.IGNORECASE)
        if end_match:
            end_pos = start + end_match.end()
            return source[start:end_pos], end_pos

    # For classes: find ENDCLASS + whitespace + next keyword or EOF
    end_match = re.search(r'^\s*ENDCLASS\.', source[start:], re.MULTILINE | re.IGNORECASE)
    if end_match:
        end_pos = start + end_match.end()
        return source[start:end_pos], end_pos

    # For interfaces
    end_match = re.search(r'^\s*ENDINTERFACE\.', source[start:], re.MULTILINE | re.IGNORECASE)
    if end_match:
        end_pos = start + end_match.end()
        return source[start:end_pos], end_pos

    return source[start:], len(source)


def _class_to_type(name: str) -> str:
    """Map ABAP object name to ZDOWNLOAD type code."""
    if name.startswith("ZCL_"):
        return "CLAS"
    if name.startswith("ZIF_"):
        return "INTF"
    if name.startswith("ZCX_"):
        return "CLAS"
    if name.startswith("Z"):
        return "PROG"
    return "PROG"


# ---------------------------------------------------------------------------
# .nugg format generator
# ---------------------------------------------------------------------------

def generate_nugg(name: str, obj_type: str, source: str, desc: str = "") -> str:
    """Generate .nugg XML — single-file format per abapblog/fidley spec.

    XML structure:
      <nugget name="ZNAME">
        <CLAS|PROG|INTF NAME="..." SUBC="1" RSTAT="K" ...>
          <source><![CDATA[...]]></source>
          <textPool>...</textPool>   (optional)
          <dynpros>...</dynpros>     (optional)
          <pfstatus>...</pfstatus>   (optional)
        </CLAS|PROG|INTF>
      </nugget>
    """
    type_info = ABAP_TYPES.get(obj_type, ABAP_TYPES["PROG"])
    su = type_info["su"]
    rstat = type_info["rstat"]

    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append(f'<nugget name="{name}">')

    obj_tag = obj_type if obj_type in ("CLAS", "INTF") else "PROG"
    lines.append(f'  <{obj_tag} NAME="{name}" SUBC="{su}" RSTAT="{rstat}"')
    lines.append(f'           FIXPT="X" UCCHECK="X"')
    lines.append(f'           DESC="{xml_escape(desc)}">')

    # Source in CDATA
    lines.append("    <source><![CDATA[")
    for line in source.split("\n"):
        lines.append(line)
    lines.append("]]></source>")

    # Text pool — extract text elements if any
    text_pool = _extract_text_pool(source)
    if text_pool:
        lines.append(text_pool)

    lines.append(f"  </{obj_tag}>")
    lines.append("</nugget>")
    return "\n".join(lines) + "\n"


def _extract_text_pool(source: str) -> str:
    """Extract text-element-like SELECT-OPTIONS / PARAMETER texts and message class refs."""
    # Simplified: look for text symbols text-xxx patterns in source
    texts = re.findall(r"text-(\w{3})", source)
    if not texts:
        return ""

    lines = ["    <textPool>"]
    for t in sorted(set(texts)):
        lines.append(f'      <textElement ID="{t}" ENTRY="{t}" LENGTH="30"/>')
    lines.append("    </textPool>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# abapGit format generator
# ---------------------------------------------------------------------------

def generate_abapgit(name: str, obj_type: str, source: str, desc: str = "") -> dict:
    """Generate abapGit-format files.

    Returns dict with paths and content:
      {name}.{type}.xml   — metadata (asx:abap envelope)
      {name}.{type}.abap  — source code
    """
    type_lower = obj_type.lower()
    safe = name.lower()

    meta_xml = _abapgit_meta_xml(name, obj_type, desc)
    source_abap = source

    return {
        f"{safe}.{type_lower}.xml": meta_xml,
        f"{safe}.{type_lower}.abap": source_abap,
    }


def _abapgit_meta_xml(name: str, obj_type: str, desc: str = "") -> str:
    """Build abapGit metadata XML with asx:abap envelope.

    Uses real ZDOWNLOAD table names per object type."""
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<abapGit version="v1.0.0"')
    lines.append(f'          serializer="LCL_OBJECT_{obj_type}">')
    lines.append('  <asx:abap xmlns:asx="http://www.sap.com/abapxml">')
    lines.append('    <asx:values>')

    if obj_type == "CLAS":
        lines.append("      <VSEOCLASS>")
        lines.append(f"        <CLSNAME>{name}</CLSNAME>")
        lines.append("        <LANGU>E</LANGU>")
        lines.append(f"        <DESCRIPT>{xml_escape(desc or name)}</DESCRIPT>")
        lines.append("        <STATE>1</STATE>")
        lines.append("        <CLSCCINCL>X</CLSCCINCL>")
        lines.append("        <FIXPT>X</FIXPT>")
        lines.append("        <UNICODE>X</UNICODE>")
        lines.append("        <WITH_UNIT_TESTS> </WITH_UNIT_TESTS>")
        lines.append("      </VSEOCLASS>")
    elif obj_type == "INTF":
        lines.append("      <VSEOINTERF>")
        lines.append(f"        <CLSNAME>{name}</CLSNAME>")
        lines.append("        <LANGU>E</LANGU>")
        lines.append(f"        <DESCRIPT>{xml_escape(desc or name)}</DESCRIPT>")
        lines.append("        <STATE>1</STATE>")
        lines.append("        <UNICODE>X</UNICODE>")
        lines.append("      </VSEOINTERF>")
    else:
        lines.append("      <PROGDIR>")
        lines.append(f"        <NAME>{name}</NAME>")
        lines.append(f"        <SUBC>{ABAP_TYPES.get(obj_type, ABAP_TYPES['PROG'])['su']}</SUBC>")
        lines.append(f"        <DESCRIPT>{xml_escape(desc or name)}</DESCRIPT>")
        lines.append("        <FIXPT>X</FIXPT>")
        lines.append("        <UCCHECK>X</UCCHECK>")
        lines.append("      </PROGDIR>")

    lines.append("    </asx:values>")
    lines.append("  </asx:abap>")
    lines.append("</abapGit>")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# ZDOWNLOAD-style XML generator (full metadata)
# ---------------------------------------------------------------------------

def generate_zdload_xml(name: str, obj_type: str, source: str, desc: str = "") -> str:
    """Generate ZDOWNLOAD-style XML with table-like metadata blocks.

    Includes:
      - Object header (TRDIR/VSEOCLASS-style)
      - Source code metadata
      - Text elements (if any)
    """
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append(f'<zdload name="{name}" type="{obj_type}" timestamp="{_now_ts()}">')
    lines.append("")

    # Metadata block
    lines.append(f"  <objectHeader>")
    lines.append(f"    <name>{name}</name>")
    lines.append(f"    <type>{obj_type}</type>")
    lines.append(f"    <description>{xml_escape(desc or name)}</description>")
    lines.append(f"    <lines>{source.count(chr(10)) + 1}</lines>")
    lines.append(f"    <chars>{len(source)}</chars>")
    lines.append(f"    <checksum>{_md5(source)[:16]}</checksum>")
    lines.append(f"  </objectHeader>")
    lines.append("")

    # Source
    lines.append("  <source>")
    for line in source.split("\n"):
        lines.append(xml_escape(line))
    lines.append("  </source>")

    lines.append("")
    lines.append(f"</zdload>")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Extract / Parse
# ---------------------------------------------------------------------------

def extract_from_nugg(filepath: str, output_dir: str):
    """Extract ABAP source from .nugg file."""
    content = Path(filepath).read_text(encoding="utf-8")

    # Parse name
    m = re.search(r'<nugget\s+name="([^"]+)"', content)
    name = m.group(1) if m else "UNKNOWN"

    # Parse source
    m = re.search(r"<source><!\[CDATA\[(.*?)\]\]></source>", content, re.DOTALL)
    source = m.group(1) if m else ""

    if not source:
        print(f"ERROR: No source found in {filepath}")
        return None

    obj_type = "CLAS" if "CLAS " in content[:500] else "INTF" if "INTF " in content[:500] else "PROG"

    out_path = Path(output_dir) / f"{name.lower()}.{obj_type.lower()}.abap"
    out_path.write_text(source, encoding="utf-8")
    print(f"Extracted {name} ({obj_type}) => {out_path}")
    return {"name": name, "type": obj_type, "source": source}


def extract_from_abapgit(dirpath: str, output_dir: str):
    """Extract ABAP source from abapGit directory (XML + .abap files)."""
    dirpath = Path(dirpath)
    results = []

    for f in dirpath.glob("*.abap"):
        source = f.read_text(encoding="utf-8")

        # Find matching XML
        xml_path = f.with_suffix(".xml")
        name = f.stem.split(".")[0] if "." in f.stem else f.stem
        obj_type = "CLAS"  # default

        if xml_path.exists():
            xml_content = xml_path.read_text(encoding="utf-8")
            m = re.search(r'serializer="LCL_OBJECT_(\w+)"', xml_content)
            if m:
                obj_type = m.group(1)

        out_path = Path(output_dir) / f.name
        out_path.write_text(source, encoding="utf-8")
        results.append({"name": name, "type": obj_type, "source": source, "file": out_path.name})
        print(f"Extracted {name} ({obj_type}) => {out_path}")

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_generate(args):
    source = Path(args.source).read_text(encoding="utf-8")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    name = args.name or Path(args.source).stem.upper()
    obj_type = args.type or _class_to_type(name)
    desc = args.desc or f"Generated by abap_serializer — {name}"

    if args.format == "nugg":
        xml = generate_nugg(name, obj_type, source, desc)
        out = output_dir / f"{name.lower()}.nugg"
        out.write_text(xml, encoding="utf-8")
        print(f"Generated .nugg: {out}  ({len(xml)} bytes)")

    elif args.format == "abapgit":
        files = generate_abapgit(name, obj_type, source, desc)
        for fname, content in files.items():
            out = output_dir / fname
            out.write_text(content, encoding="utf-8")
            print(f"Generated abapGit: {out}  ({len(content)} bytes)")

    elif args.format == "xml":
        xml = generate_zdload_xml(name, obj_type, source, desc)
        out = output_dir / f"{name.lower()}_zdload.xml"
        out.write_text(xml, encoding="utf-8")
        print(f"Generated ZDOWNLOAD XML: {out}  ({len(xml)} bytes)")

    else:
        print(f"ERROR: Unknown format '{args.format}'")
        sys.exit(1)


def cmd_extract(args):
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_file() and input_path.suffix == ".nugg":
        extract_from_nugg(str(input_path), str(output_dir))

    elif input_path.is_dir():
        has_nugg = list(input_path.glob("*.nugg"))
        has_abapgit = list(input_path.glob("*.abap"))
        if has_abapgit and not has_nugg:
            extract_from_abapgit(str(input_path), str(output_dir))
        elif has_nugg:
            for f in has_nugg:
                extract_from_nugg(str(f), str(output_dir))
        else:
            print(f"ERROR: No .nugg or .abap files found in {input_path}")
            sys.exit(1)

    else:
        print(f"ERROR: Unknown input: {input_path}")
        sys.exit(1)


def cmd_split(args):
    """Split multi-object ABAP file into individual source files, then serialize each.

    ZDOWNLOAD-style: the split produces individual ABAP sources ready for serialization.
    """
    source = Path(args.source).read_text(encoding="utf-8")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    objects = _split_abap_objects(source)
    if not objects:
        print("ERROR: No CLASS/INTERFACE/FUNCTION objects found in source")
        sys.exit(1)

    for kind, name, code in objects:
        type_map = {"CLASS": "CLAS", "INTERFACE": "INTF", "FUNCTION": "FUGR"}
        obj_type = type_map.get(kind, "PROG")

        # Write source file
        ext = obj_type.lower()
        src_file = output_dir / f"{name.lower()}.{ext}.abap"
        src_file.write_text(code, encoding="utf-8")
        print(f"Split {kind}:{name} => {src_file}  ({len(code)} chars)")

    print(f"\nSplit {len(objects)} objects from {Path(args.source).name}")


def cmd_package(args):
    """Package an ABAP source into ALL formats at once."""
    source = Path(args.source).read_text(encoding="utf-8")
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    name = args.name or Path(args.source).stem.upper()
    obj_type = args.type or _class_to_type(name)
    desc = args.desc or f"Generated by abap_serializer — {name}"

    # Format subdirs
    for fmt in ("nugg", "abapgit", "xml"):
        fmt_dir = output_dir / fmt
        fmt_dir.mkdir(parents=True, exist_ok=True)

        if fmt == "nugg":
            xml = generate_nugg(name, obj_type, source, desc)
            out = fmt_dir / f"{name.lower()}.nugg"
            out.write_text(xml, encoding="utf-8")
            print(f"  nugg   => {out}  ({len(xml)} bytes)")

        elif fmt == "abapgit":
            files = generate_abapgit(name, obj_type, source, desc)
            for fname, content in files.items():
                out = fmt_dir / fname
                out.write_text(content, encoding="utf-8")
                print(f"  abapgit => {out}  ({len(content)} bytes)")

        elif fmt == "xml":
            xml = generate_zdload_xml(name, obj_type, source, desc)
            out = fmt_dir / f"{name.lower()}_zdload.xml"
            out.write_text(xml, encoding="utf-8")
            print(f"  xml     => {out}  ({len(xml)} bytes)")

    print(f"\nPackaged {name} ({obj_type}) in 3 formats => {output_dir}/")


def cmd_list_formats(args):
    """List all known formats with description."""
    print("""
ABAP Serialization Formats - Supported Outputs
===============================================

Format     File(s)              Based on                Import/Export
------     -------              --------                -------------
.nugg      {name}.nugg          abapblog/fidley         Both (single XML)
abapgit    {name}.{typ}.xml     abapGit                 Both (meta + source)
           {name}.{typ}.abap
xml        {name}_zdload.xml    ZDOWNLOAD tables         Export only

ZDOWNLOAD metadata tables referenced:
  TRDIR        - program headers (NAME, SUBC, RSTAT, VARCL)
  TFDIR        - function module registry
  VSEOCLASS    - OO class definitions (CLSNAME, STATE, CLSCCINCL)
  VSEOINTERF   - OO interface definitions
  DD02L        - table/structure headers
  DD40L        - table type headers
  D020S        - screen headers
  D022S        - screen flow logic
""")


def main():
    parser = argparse.ArgumentParser(
        description="ABAP Serializer — .nugg, abapGit, and ZDOWNLOAD-style XML",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # generate
    g = sub.add_parser("generate", help="Generate serialized ABAP from source")
    g.add_argument("--source", "-s", required=True, help="ABAP source file")
    g.add_argument("--name", "-n", help="ABAP object name (default: filename stem)")
    g.add_argument("--type", "-t", choices=["CLAS", "INTF", "PROG", "FUGR", "TABL", "TYPE"],
                   help="ABAP object type (auto-detected from name if omitted)")
    g.add_argument("--format", "-f", choices=["nugg", "abapgit", "xml"], default="nugg",
                   help="Output format")
    g.add_argument("--output", "-o", default=".", help="Output directory")
    g.add_argument("--desc", "-d", help="Object description")

    # extract
    e = sub.add_parser("extract", help="Extract ABAP source from serialized format")
    e.add_argument("--input", "-i", required=True, help=".nugg file or directory with abapGit files")
    e.add_argument("--output", "-o", default=".", help="Output directory")

    # split
    s = sub.add_parser("split", help="Split multi-class ABAP into individual objects")
    s.add_argument("--source", "-s", required=True, help="Multi-object ABAP source file")
    s.add_argument("--output", "-o", default=".", help="Output directory")

    # package — all formats at once
    p = sub.add_parser("package", help="Generate all 3 formats at once")
    p.add_argument("--source", "-s", required=True, help="ABAP source file")
    p.add_argument("--name", "-n", help="ABAP object name")
    p.add_argument("--type", "-t", choices=["CLAS", "INTF", "PROG", "FUGR", "TABL", "TYPE"],
                   help="ABAP object type")
    p.add_argument("--output", "-o", default=".", help="Output root directory")
    p.add_argument("--desc", "-d", help="Object description")

    # list-formats
    sub.add_parser("list-formats", help="Show supported formats and metadata tables")

    args = parser.parse_args()

    dispatch = {
        "generate": cmd_generate,
        "extract": cmd_extract,
        "split": cmd_split,
        "package": cmd_package,
        "list-formats": cmd_list_formats,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
