#!/usr/bin/env python3
"""
HDI / SQLScript Lint v4.2.0

Lightweight regex-based lint for HANA HDI artefacts and SQLScript sources.
Checks the pitfalls documented in .claude/skills/sap-hana-sqlscript/SKILL.md.
Exit codes: 0 = clean or LOW/MEDIUM only, 1 = HIGH findings (or any finding
with --strict), 2 = usage error.
"""

import os
import re
import sys
import argparse

__version__ = "4.2.0"

LINT_EXTENSIONS = (".hdbprocedure", ".hdbfunction", ".hdbtablefunction",
                   ".hdbview", ".sql", ".sqlscript")

# (rule, severity, compiled regex, message)
RULES = [
    ("SELECT_STAR", "MEDIUM", re.compile(r"\bSELECT\s+\*", re.IGNORECASE),
     "SELECT * - list explicit columns to keep the plan stable"),
    ("SECURITY_DEFINER", "HIGH", re.compile(r"SQL\s+SECURITY\s+DEFINER", re.IGNORECASE),
     "SQL SECURITY DEFINER grants owner privileges - prefer INVOKER"),
    ("DYNAMIC_SQL", "HIGH", re.compile(r"\b(EXECUTE\s+IMMEDIATE|EXEC\s*\()", re.IGNORECASE),
     "Dynamic SQL - injection risk, validate/whitelist inputs"),
    ("CE_FUNCTION", "LOW", re.compile(r"\bCE_[A-Z_]+\s*\(", re.IGNORECASE),
     "CE function bypasses the SQL optimizer - benchmark declarative SQL first"),
    ("CURSOR_LOOP", "LOW", re.compile(r"\bFOR\s+\w+\s+AS\s+\w*\s*CURSOR\b|\bDECLARE\s+CURSOR\b",
                                      re.IGNORECASE),
     "Cursor loop - optimizer cannot rewrite imperative logic, try declarative first"),
    ("COMMIT_IN_PROC", "MEDIUM", re.compile(r"^\s*COMMIT\s*;", re.IGNORECASE),
     "COMMIT inside procedure - not allowed in HDI containers"),
    ("UNBOUNDED_DELETE", "MEDIUM",
     re.compile(r"^\s*DELETE\s+FROM\s+[\"\w.]+\s*;", re.IGNORECASE),
     "DELETE without WHERE on the same statement - verify intent"),
]

SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def collect_files(path):
    if os.path.isfile(path):
        return [path]
    found = []
    for root, _dirs, files in os.walk(path):
        for name in files:
            if name.lower().endswith(LINT_EXTENSIONS):
                found.append(os.path.join(root, name))
    return sorted(found)


def lint_file(path):
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"[ERROR] Cannot read {path}: {exc}", file=sys.stderr)
        return findings
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("--") or stripped.startswith("//"):
            continue
        for rule, severity, pattern, message in RULES:
            if pattern.search(line):
                findings.append((path, lineno, severity, rule, message))
    return findings


def main():
    parser = argparse.ArgumentParser(description="HDI / SQLScript Lint v4.2.0")
    parser.add_argument("--path", required=True, help="File or directory to lint")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on any finding (default: HIGH only)")
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"[ERROR] Path not found: {args.path}", file=sys.stderr)
        sys.exit(2)

    files = collect_files(args.path)
    if not files:
        print(f"[WARN] No SQLScript/HDI files under {args.path} "
              f"(extensions: {', '.join(LINT_EXTENSIONS)})")
        sys.exit(0)

    all_findings = []
    for path in files:
        all_findings.extend(lint_file(path))
    all_findings.sort(key=lambda f: (SEVERITY_ORDER[f[2]], f[0], f[1]))

    for path, lineno, severity, rule, message in all_findings:
        print(f"{path}:{lineno}: [{severity}] {rule}: {message}")

    high = sum(1 for f in all_findings if f[2] == "HIGH")
    print(f"\n{len(files)} file(s) checked, {len(all_findings)} finding(s), {high} HIGH")
    if high or (args.strict and all_findings):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
