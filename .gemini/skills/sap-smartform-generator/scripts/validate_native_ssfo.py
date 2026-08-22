#!/usr/bin/env python3
"""Fail-closed structural preflight for native SAP Smart Forms XML."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable


SMARTFORM_NS = "urn:sap-com:SmartForms:2000:internal-structure"
IFR_NS = "urn:sap-com:sdixml-ifr:2000"
FORM_NAME_PATTERN = re.compile(r"^[ZY][A-Z0-9_]{0,29}$")


def split_tag(tag: str) -> tuple[str, str]:
    if tag.startswith("{") and "}" in tag:
        namespace, local_name = tag[1:].split("}", 1)
        return namespace, local_name
    return "", tag


def local_name(element: ET.Element) -> str:
    return split_tag(element.tag)[1]


def elements_named(root: ET.Element, name: str) -> Iterable[ET.Element]:
    return (element for element in root.iter() if local_name(element) == name)


def element_texts(root: ET.Element, name: str) -> list[str]:
    return [
        text
        for element in elements_named(root, name)
        if (text := (element.text or "").strip())
    ]


def has_main_window(root: ET.Element) -> bool:
    for window in elements_named(root, "WINDOW"):
        descendants = list(window.iter())
        inames = {
            (element.text or "").strip().upper()
            for element in descendants
            if local_name(element) == "INAME"
        }
        window_types = {
            (element.text or "").strip().upper()
            for element in descendants
            if local_name(element) == "WTYPE"
        }
        if "MAIN" in inames and "M" in window_types:
            return True
    return False


def validate(
    input_path: Path,
    expected_form_name: str | None,
    required_tokens: list[str],
    forbidden_tokens: list[str],
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, object] = {"input": str(input_path.resolve())}

    if not input_path.is_file():
        return {
            "is_valid": False,
            "errors": [f"File not found: {input_path}"],
            "warnings": [],
            "evidence": evidence,
        }

    try:
        raw = input_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        return {
            "is_valid": False,
            "errors": [f"XML is not valid UTF-8: {exc}"],
            "warnings": [],
            "evidence": evidence,
        }

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return {
            "is_valid": False,
            "errors": [f"XML parse failure: {exc}"],
            "warnings": [],
            "evidence": evidence,
        }

    root_namespace, root_local_name = split_tag(root.tag)
    evidence["root"] = root_local_name
    evidence["root_namespace"] = root_namespace

    if root_local_name != "SMARTFORM":
        errors.append(
            f"Root must be SMARTFORM, found {root_local_name!r}; custom wrappers are not native SSFO"
        )
    if root_namespace != SMARTFORM_NS:
        errors.append(
            f"Root namespace must be {SMARTFORM_NS!r}, found {root_namespace!r}"
        )

    namespaces = sorted(
        {
            namespace
            for element in root.iter()
            if (namespace := split_tag(element.tag)[0])
        }
    )
    evidence["namespaces"] = namespaces
    if IFR_NS not in namespaces:
        warnings.append(f"IFR namespace {IFR_NS!r} was not found")

    required_sections = ("HEADER", "INTERFACE", "VARHEADER", "PAGETREE")
    missing_sections = [
        section
        for section in required_sections
        if next(elements_named(root, section), None) is None
    ]
    if missing_sections:
        errors.append(f"Missing native sections: {', '.join(missing_sections)}")

    form_names = sorted(set(element_texts(root, "FORMNAME")))
    evidence["form_names"] = form_names
    if not form_names:
        errors.append("No FORMNAME was found")
    elif len(form_names) != 1:
        errors.append(f"Inconsistent FORMNAME values: {', '.join(form_names)}")

    canonical_name = expected_form_name.upper() if expected_form_name else (
        form_names[0].upper() if len(form_names) == 1 else ""
    )
    evidence["canonical_form_name"] = canonical_name
    if canonical_name and not FORM_NAME_PATTERN.fullmatch(canonical_name):
        errors.append(
            f"Form name {canonical_name!r} must start with Z/Y, use ABAP-safe characters, and be <= 30 characters"
        )
    if expected_form_name and form_names and set(form_names) != {canonical_name}:
        errors.append(
            f"Expected FORMNAME {canonical_name!r}, found {', '.join(form_names)}"
        )

    main_window = has_main_window(root)
    evidence["main_window"] = main_window
    if not main_window:
        errors.append("No MAIN window with WTYPE=M was found")

    raw_upper = raw.upper()
    for token in required_tokens:
        if token.upper() not in raw_upper:
            errors.append(f"Required token not found: {token}")
    for token in forbidden_tokens:
        if token.upper() in raw_upper:
            errors.append(f"Forbidden token found: {token}")

    if "\ufffd" in raw:
        errors.append("Unicode replacement characters were found")
    if "Ã" in raw or "Â" in raw:
        warnings.append("Possible UTF-8 mojibake was found; review captions and text lines")

    volatile_fields = [
        field
        for field in ("DEVCLASS", "FIRSTUSER", "LASTUSER", "LASTDATE", "LASTTIME")
        if element_texts(root, field)
    ]
    evidence["volatile_metadata"] = volatile_fields
    if volatile_fields:
        warnings.append(
            "Volatile metadata is present; normalize it with the reviewed abapGit serializer before diffing"
        )

    warnings.append(
        "Structural preflight does not prove SAP import, activation, generated function-module resolution, or rendering"
    )
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate structural invariants of native SAP Smart Forms XML"
    )
    parser.add_argument("--input", required=True, help="Path to native SSFO XML")
    parser.add_argument("--form-name", help="Expected canonical Z/Y Smart Form name")
    parser.add_argument(
        "--require-token",
        action="append",
        default=[],
        help="Case-insensitive token that must occur; repeat as needed",
    )
    parser.add_argument(
        "--forbid-token",
        action="append",
        default=[],
        help="Case-insensitive residue/placeholder that must not occur; repeat as needed",
    )
    args = parser.parse_args()

    result = validate(
        Path(args.input),
        args.form_name,
        args.require_token,
        args.forbid_token,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["is_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
