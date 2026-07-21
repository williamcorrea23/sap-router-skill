#!/usr/bin/env python3
"""Metadata-only secret audit for SAP Router workspace."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_PATHS = [
    ".mcp.json",
    ".codex/config.toml",
    ".codex/config.example.toml",
    ".claude/settings.local.json",
    ".env.template",
    "scripts",
]

PATTERNS = {
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "api_token": re.compile(r"\b(?:sk|pat|ghp|glpat)-[A-Za-z0-9_\-]{12,}\b"),
    "sap_password_literal": re.compile(r"(?i)(password|passwd|client_secret|api_key|auth_token)\s*[:=]\s*([\"'])(?!\$\{|<|your|change|dummy|test|example|password|secret)(.{8,}?)\2"),
    "hardcoded_sap_host": re.compile(r"https?://\d{1,3}(?:\.\d{1,3}){3}:\d+"),
}

PLACEHOLDER_MARKERS = (
    "ENV",
    "REF",
    "MISSING",
    "PLACEHOLDER",
    "TOKEN_URL",
    "CLIENT_SECRET",
    "PASSWORD",
    "API_KEY",
)

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
AUDIT_SUFFIXES = {".json", ".toml", ".yaml", ".yml", ".env", ".py", ".js", ".ts", ".md", ".txt"}
REVIEW_ONLY_PARTS = {"test", "tests", "unittests", "fixtures", "docs", "doc", "references", "examples", "spec", ".github"}


def review_only(path: Path, kind: str) -> bool:
    """Classify examples without hiding them from the audit report."""
    lowered = {part.lower() for part in path.parts}
    if kind == "hardcoded_sap_host":
        return True
    if lowered & REVIEW_ONLY_PARTS:
        return True
    if path.name.lower() in {"readme.md", "skill.md", "validate_skill.py"}:
        return True
    return False


def iter_files(paths: list[str]):
    for raw in paths:
        path = (ROOT / raw).resolve()
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in path.rglob("*"):
            if child.is_dir() and child.name in SKIP_DIRS:
                continue
            if child.is_file() and not any(part in SKIP_DIRS for part in child.parts):
                if child.suffix.lower() not in AUDIT_SUFFIXES and not child.name.startswith(".env"):
                    continue
                yield child


def audit(paths: list[str]) -> dict:
    findings = []
    for path in iter_files(paths):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(ROOT))
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                matched = match.group(0)
                value = match.group(2).strip() if name == "sap_password_literal" and match.lastindex == 2 else ""
                value_upper = value.strip("\"'`.,)").upper()
                if name == "sap_password_literal":
                    if (
                        "{" in matched
                        or "Authorization" in matched
                        or "Bearer" in matched
                        or "Basic" in matched
                        or value.startswith("$")
                        or value.startswith("{")
                        or value_upper.replace("_", "").isalnum() and value_upper == value_upper.upper()
                        or any(marker in value_upper for marker in PLACEHOLDER_MARKERS)
                    ):
                        continue
                line = text.count("\n", 0, match.start()) + 1
                findings.append({
                    "file": rel,
                    "line": line,
                    "kind": name,
                    "length": len(matched),
                    "classification": "review_only" if review_only(path, name) else "actionable",
                })
    actionable = [item for item in findings if item["classification"] == "actionable"]
    return {
        "root": str(ROOT),
        "status": "FAIL" if actionable else "PASS",
        "findings_count": len(findings),
        "actionable_findings_count": len(actionable),
        "review_only_findings_count": len(findings) - len(actionable),
        "findings": findings,
        "note": "Values are intentionally not printed. Rotate any credential that appeared in tracked config.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit workspace for literal secrets without printing secret values.")
    parser.add_argument("paths", nargs="*", help="Files or directories to scan. Defaults to high-risk config paths.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when findings exist. Default behavior already does this; kept for npm compatibility.")
    parser.add_argument("--include-local-env", action="store_true", help="Also scan ignored local .env files.")
    parser.add_argument("--include-packages", action="store_true", help="Also scan ignored vendored package directories.")
    args = parser.parse_args()
    paths = args.paths or DEFAULT_PATHS
    if args.include_local_env and not args.paths:
        paths = paths + [".env", ".env.local"]
    if args.include_packages and not args.paths:
        paths = paths + ["packages"]
    result = audit(paths)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Secret audit: {result['status']} ({result['findings_count']} findings)")
        for item in result["findings"]:
            print(f"  {item['file']}:{item['line']} {item['kind']} len={item['length']}")
        print(result["note"])
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
