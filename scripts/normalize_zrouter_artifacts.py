#!/usr/bin/env python3
"""Keep every ZROUTER distribution artifact aligned with the hardened source."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANONICAL_HANDLER = ROOT / "deploy" / "abapgit_full" / "src" / "zcl_zrouter_handler_abstract.clas.abap"
ARTIFACTS = [
    *ROOT.glob("deploy/**/*.abap"),
    *ROOT.glob("deploy/**/*.xml"),
    *ROOT.glob("deploy/**/*.nugg"),
]
HANDLER_RE = re.compile(
    r"(?ms)^CLASS zcl_zrouter_handler_abstract DEFINITION.*?^ENDCLASS\.\s*"
    r"^CLASS zcl_zrouter_handler_abstract IMPLEMENTATION\..*?^ENDCLASS\."
)
UNSAFE_RE = re.compile(r"(?i)\bGENERATE\s+SUBROUTINE\s+POOL\b|\bMETHOD\s+evaluate_expression\b")


def normalize(check: bool) -> int:
    canonical = CANONICAL_HANDLER.read_text(encoding="utf-8")
    changed: list[Path] = []
    unsafe: list[Path] = []
    for path in ARTIFACTS:
        if path == CANONICAL_HANDLER:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        updated, count = HANDLER_RE.subn(canonical.rstrip(), text)
        if count:
            if check and updated != text:
                changed.append(path)
            elif not check and updated != text:
                path.write_text(updated, encoding="utf-8")
                changed.append(path)
            text = updated
        if UNSAFE_RE.search(text):
            unsafe.append(path)
    if changed:
        print("normalized:")
        print("\n".join(str(path.relative_to(ROOT)) for path in changed))
    if unsafe:
        print("unsafe dynamic execution:")
        print("\n".join(str(path.relative_to(ROOT)) for path in unsafe))
        return 1
    return 1 if check and changed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    return normalize(check=parser.parse_args().check)


if __name__ == "__main__":
    raise SystemExit(main())
