#!/usr/bin/env python3
"""Structural, frontmatter, size, link, and security-heuristic validator for
Agent Skills packaged under ``skills/<slug>/SKILL.md``.

The validator uses the Python standard library only. It never contacts the
network. It never prints suspected secret values in full.

Usage:

    python validate_skill.py <skill-directory> [--json] [--strict] \
        [--repository-root <path>]

Exit codes:

    0  Validation passed with no failures.
    1  One or more validation failures were reported.
    2  Invalid invocation or internal validation error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_SKILL_LINES = 500

SUPPORTED_TOP_LEVEL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

VAGUE_PHRASES = (
    "best practices",
    "handle errors appropriately",
    "use when needed",
    "comprehensive solution",
    "as needed",
    "seamless",
    "state-of-the-art",
)

# Suspicious substrings used for heuristic secret scanning.
# Placeholder strings are handled downstream; matches are context-analysed.
SECRET_PATTERNS: tuple[tuple[str, str], ...] = (
    ("password=", "possible hardcoded password assignment"),
    ("passwd=", "possible hardcoded password assignment"),
    ("pwd=", "possible hardcoded password assignment"),
    ("Authorization:", "possible Authorization header with credentials"),
    ("Bearer ", "possible bearer token"),
    ("BEGIN PRIVATE KEY", "possible private key material"),
    ("BEGIN RSA PRIVATE KEY", "possible private key material"),
    ("BEGIN OPENSSH PRIVATE KEY", "possible private key material"),
    ("client_secret", "possible OAuth client secret"),
    ("api_key", "possible API key assignment"),
    ("access_token", "possible access token"),
    ("refresh_token", "possible refresh token"),
    ("session_cookie", "possible session cookie"),
    ("verify=False", "TLS verification disabled"),
    ("verify = False", "TLS verification disabled"),
    ("shell=True", "subprocess shell=True usage"),
    ("shell = True", "subprocess shell=True usage"),
)

PLACEHOLDER_TOKENS = (
    "<password>",
    "<token>",
    "<value>",
    "<secret>",
    "<api-key>",
    "<user>",
    "<api_key>",
    "<access_token>",
    "<refresh_token>",
    "example.com",
    "example.org",
    "placeholder",
    "your-",
    "REDACTED",
    "TOP_SECRET_PLACEHOLDER",
)

# Words that mark a line as discussing a pattern rather than embedding a
# real secret. Common in security documentation.
DOCUMENTATION_CONTEXT_TOKENS = (
    "reject",
    "rejects",
    "pattern",
    "patterns",
    "warn",
    "warns",
    "warning",
    "warnings",
    "flag",
    "flagged",
    "avoid",
    "avoids",
    "never use",
    "do not use",
    "must not",
    "must never",
    "forbid",
    "disallow",
    "example",
    "documenting",
    "documents",
    "documented",
    "vulnerabilit",  # covers vulnerabilities/vulnerability
    "insecure",
    "unsafe",
    "banned",
    "safety",
    "safety prompt",
    "prompt",
    "prompts",
    "trigger",
    "triggers",
    "quoted",
    "sample",
    "guidance",
    "checklist",
    "prohibit",
    "prohibited",
    "guarded",
    "guard",
    "audit",
    "review",
    "should not",
    "should never",
    "malicious",
    "attacker",
)

# File suffixes that look like SAP hostnames in the pattern but are file
# references. Exclude to reduce false positives on docs that mention
# files like sap-library-submission.md.
NON_HOSTNAME_SUFFIXES = {
    "md",
    "markdown",
    "txt",
    "py",
    "ts",
    "js",
    "json",
    "yaml",
    "yml",
    "toml",
    "cfg",
    "ini",
    "sh",
    "ps1",
    "html",
    "css",
    "svg",
    "png",
    "jpg",
    "gif",
    "pdf",
    "csv",
    "log",
}

# Rough hostname pattern; SAP-looking values may be real, so we only flag,
# never confirm.
SAP_HOSTNAME_HINT = re.compile(
    r"\b(sap[\w-]*\.[a-z]{2,}(:\d{2,5})?)\b", re.IGNORECASE
)

USER_HOME_PATTERN = re.compile(r"C:\\Users\\[A-Za-z0-9_.-]+", re.IGNORECASE)
NIX_HOME_PATTERN = re.compile(r"/home/[A-Za-z0-9_.-]+")

MARKDOWN_LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\(([^)\s]+?)(?:\s+\"[^\"]*\")?\)"
)

TEXT_FILE_SUFFIXES = {
    ".md",
    ".markdown",
    ".txt",
    ".yml",
    ".yaml",
    ".py",
    ".sh",
    ".ps1",
    ".ts",
    ".js",
    ".json",
    ".toml",
    ".cfg",
    ".ini",
}


# --------------------------------------------------------------------------- #
# Report model
# --------------------------------------------------------------------------- #

SEVERITY_PASS = "PASS"
SEVERITY_WARN = "WARN"
SEVERITY_FAIL = "FAIL"


@dataclass
class Finding:
    """A single validation result."""

    rule: str
    severity: str
    message: str
    file: str | None = None
    line: int | None = None
    remediation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return {k: v for k, v in payload.items() if v is not None}


@dataclass
class Report:
    """Aggregated validation report."""

    skill_directory: str
    findings: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def has_failures(self) -> bool:
        return any(f.severity == SEVERITY_FAIL for f in self.findings)

    def has_warnings(self) -> bool:
        return any(f.severity == SEVERITY_WARN for f in self.findings)

    def counts(self) -> dict[str, int]:
        counts = {SEVERITY_PASS: 0, SEVERITY_WARN: 0, SEVERITY_FAIL: 0}
        for finding in self.findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_directory": self.skill_directory,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }


# --------------------------------------------------------------------------- #
# Minimal YAML subset parser
# --------------------------------------------------------------------------- #

def _strip_inline_comment(line: str) -> str:
    """Remove a trailing YAML comment while respecting quotes."""
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index].rstrip()
    return line.rstrip()


def _unquote(value: str) -> str:
    """Remove matching wrapping quotes when present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _coerce_scalar(value: str) -> Any:
    """Coerce a scalar-looking string. Everything else is returned as-is."""
    stripped = value.strip()
    if not stripped:
        return ""
    lowered = stripped.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    return _unquote(stripped)


def _parse_block_scalar(
    header: str, lines: list[str], start: int, base_indent: int
) -> tuple[str, int]:
    """Parse a folded/literal block scalar starting at *start*.

    Only the subset needed for typical Agent Skills frontmatter is supported:
    ``>`` (folded), ``|`` (literal), each with the optional strip indicator
    ``-``.
    """
    indicator = header.strip()
    style = indicator[0]  # '>' or '|'
    strip_final = "-" in indicator[1:]

    collected: list[str] = []
    idx = start
    child_indent: int | None = None
    while idx < len(lines):
        raw = lines[idx]
        if not raw.strip():
            collected.append("")
            idx += 1
            continue
        current_indent = len(raw) - len(raw.lstrip(" "))
        if current_indent <= base_indent:
            break
        if child_indent is None:
            child_indent = current_indent
        collected.append(raw[child_indent:])
        idx += 1

    if style == ">":
        joined = _fold_lines(collected)
    else:
        joined = "\n".join(collected)

    if strip_final:
        joined = joined.rstrip("\n")
    elif not joined.endswith("\n"):
        joined = joined + "\n"

    return joined.rstrip(), idx


def _fold_lines(lines: list[str]) -> str:
    """Fold YAML folded-style block content into a single string."""
    result: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            result.append(" ".join(part.strip() for part in buffer if part.strip()))
            buffer.clear()

    for line in lines:
        if line.strip() == "":
            flush()
            result.append("")
        else:
            buffer.append(line)
    flush()

    # Collapse duplicated empty markers.
    folded_parts: list[str] = []
    for chunk in result:
        if chunk == "" and folded_parts and folded_parts[-1] == "":
            continue
        folded_parts.append(chunk)
    return " ".join(part for part in folded_parts if part).strip()


class FrontmatterError(ValueError):
    """Raised when frontmatter cannot be parsed."""


def parse_frontmatter(text: str) -> tuple[dict[str, Any], int]:
    """Parse a minimal YAML subset from the leading ``---`` block.

    Returns the mapping and the number of physical lines consumed (including
    the opening and closing ``---`` markers). Only mappings, scalar values,
    quoted scalars, and top-level block scalars (``>`` / ``|``) are supported.
    Nested mappings are supported for the ``metadata`` field.
    """
    lines = text.splitlines()
    if not lines:
        raise FrontmatterError("SKILL.md is empty; frontmatter is required.")
    if lines[0].strip() != "---":
        raise FrontmatterError(
            "SKILL.md must start with '---' on line 1 to declare frontmatter."
        )

    idx = 1
    result: dict[str, Any] = {}
    active_key: str | None = None
    active_nested: dict[str, Any] | None = None

    while idx < len(lines):
        raw = lines[idx]
        stripped = raw.strip()
        if stripped == "---":
            return result, idx + 1

        line = _strip_inline_comment(raw)
        if not line.strip():
            idx += 1
            continue

        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()

        # Detect nested key/value under an active parent mapping.
        if indent > 0 and active_nested is not None:
            if ":" not in content:
                raise FrontmatterError(
                    f"Unexpected line inside '{active_key}': '{content}'"
                )
            key, _, value = content.partition(":")
            active_nested[key.strip()] = _coerce_scalar(value.strip())
            idx += 1
            continue

        # Top-level entries reset any active nested mapping.
        active_nested = None
        active_key = None

        if ":" not in content:
            raise FrontmatterError(
                f"Malformed frontmatter line (missing ':'): '{content}'"
            )
        key, _, raw_value = content.partition(":")
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value == "":
            # Could be a nested mapping (metadata) or an empty scalar.
            look_ahead = idx + 1
            if look_ahead < len(lines):
                nxt = lines[look_ahead]
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                nxt_stripped = nxt.strip()
                if (
                    nxt_stripped
                    and nxt_stripped != "---"
                    and nxt_indent > indent
                    and ":" in nxt_stripped
                ):
                    active_key = key
                    active_nested = {}
                    result[key] = active_nested
                    idx += 1
                    continue
            result[key] = ""
            idx += 1
            continue

        if raw_value.startswith(">") or raw_value.startswith("|"):
            value, idx = _parse_block_scalar(raw_value, lines, idx + 1, indent)
            result[key] = value
            continue

        result[key] = _coerce_scalar(raw_value)
        idx += 1

    raise FrontmatterError(
        "SKILL.md frontmatter is not closed with '---' before end of file."
    )


# --------------------------------------------------------------------------- #
# Redaction helpers
# --------------------------------------------------------------------------- #

def _redact(value: str, keep: int = 4) -> str:
    """Return a short redacted rendering suitable for reports."""
    trimmed = value.strip()
    if not trimmed:
        return "<empty>"
    if len(trimmed) <= keep + 3:
        return "<redacted>"
    return trimmed[:keep] + "..."


def _looks_like_placeholder(context: str) -> bool:
    lowered = context.lower()
    for token in PLACEHOLDER_TOKENS:
        if token.lower() in lowered:
            return True
    return False


def _looks_like_documentation(context: str) -> bool:
    """Return True when the surrounding text signals a documentation
    or pattern-definition context rather than a live secret usage."""
    lowered = context.lower()
    for token in DOCUMENTATION_CONTEXT_TOKENS:
        if token in lowered:
            return True
    return False


def _iter_code_fence_ranges(text: str) -> list[tuple[int, int]]:
    """Return (start_line, end_line) ranges (1-based, inclusive) inside
    fenced code blocks."""
    ranges: list[tuple[int, int]] = []
    open_line: int | None = None
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if open_line is None:
                open_line = idx
            else:
                ranges.append((open_line, idx))
                open_line = None
    return ranges


def _offset_in_fence(text: str, offset: int) -> bool:
    line_no = text.count("\n", 0, offset) + 1
    for start, end in _iter_code_fence_ranges(text):
        if start <= line_no <= end:
            return True
    return False


def _line_in_fence(fences: list[tuple[int, int]], line_no: int) -> bool:
    for start, end in fences:
        if start <= line_no <= end:
            return True
    return False


# --------------------------------------------------------------------------- #
# Validation building blocks
# --------------------------------------------------------------------------- #

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _validate_structure(report: Report, skill_dir: Path) -> Path | None:
    if not skill_dir.exists() or not skill_dir.is_dir():
        report.add(
            Finding(
                rule="structure.directory",
                severity=SEVERITY_FAIL,
                message=f"Skill directory not found: {skill_dir}",
                remediation="Provide a valid path to skills/<slug>/.",
            )
        )
        return None

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists() or not skill_md.is_file():
        report.add(
            Finding(
                rule="structure.skill_md",
                severity=SEVERITY_FAIL,
                message="SKILL.md is missing at the skill root.",
                file=str(skill_md),
                remediation="Create skills/<slug>/SKILL.md with frontmatter.",
            )
        )
        return None

    # Empty subdirectories are a smell.
    for child in skill_dir.iterdir():
        if child.is_dir():
            entries = [entry for entry in child.iterdir() if entry.name != ".gitkeep"]
            if not entries:
                report.add(
                    Finding(
                        rule="structure.empty_dir",
                        severity=SEVERITY_WARN,
                        message=f"Empty subdirectory: {child.name}",
                        file=str(child),
                        remediation="Remove the directory or add real content.",
                    )
                )
    return skill_md


def _validate_frontmatter(
    report: Report, skill_dir: Path, skill_md: Path
) -> dict[str, Any] | None:
    text = _read_text(skill_md)
    try:
        data, _ = parse_frontmatter(text)
    except FrontmatterError as exc:
        report.add(
            Finding(
                rule="frontmatter.parse",
                severity=SEVERITY_FAIL,
                message=str(exc),
                file=str(skill_md),
                remediation="Fix the YAML frontmatter block at the top of SKILL.md.",
            )
        )
        return None

    for field_name in data:
        if field_name not in SUPPORTED_TOP_LEVEL_FIELDS:
            report.add(
                Finding(
                    rule="frontmatter.unknown_field",
                    severity=SEVERITY_WARN,
                    message=f"Unsupported top-level frontmatter field: '{field_name}'",
                    file=str(skill_md),
                    remediation=(
                        "Remove the field or move it under metadata:"
                    ),
                )
            )

    _validate_name(report, skill_md, skill_dir, data.get("name"))
    _validate_description(report, skill_md, data.get("description"))
    _validate_license(report, skill_md, data.get("license"))
    _validate_compatibility(report, skill_md, data.get("compatibility"))
    _validate_metadata(report, skill_md, data.get("metadata"))
    _validate_allowed_tools(report, skill_md, data.get("allowed-tools"))
    return data


def _validate_name(
    report: Report, skill_md: Path, skill_dir: Path, value: Any
) -> None:
    if value in (None, ""):
        report.add(
            Finding(
                rule="frontmatter.name.required",
                severity=SEVERITY_FAIL,
                message="Frontmatter 'name' is required.",
                file=str(skill_md),
                remediation="Add 'name: <slug>' matching the directory name.",
            )
        )
        return
    if not isinstance(value, str):
        report.add(
            Finding(
                rule="frontmatter.name.type",
                severity=SEVERITY_FAIL,
                message="Frontmatter 'name' must be a string.",
                file=str(skill_md),
            )
        )
        return
    if len(value) > MAX_NAME_LENGTH:
        report.add(
            Finding(
                rule="frontmatter.name.length",
                severity=SEVERITY_FAIL,
                message=(
                    f"Frontmatter 'name' is {len(value)} characters; "
                    f"maximum is {MAX_NAME_LENGTH}."
                ),
                file=str(skill_md),
            )
        )
    if not NAME_PATTERN.match(value):
        report.add(
            Finding(
                rule="frontmatter.name.pattern",
                severity=SEVERITY_FAIL,
                message=(
                    "Frontmatter 'name' must be lowercase ASCII letters, digits, "
                    "and single hyphens with no leading, trailing, or "
                    "consecutive hyphen."
                ),
                file=str(skill_md),
                remediation="Rename the skill to match the pattern.",
            )
        )
    if value != skill_dir.name:
        report.add(
            Finding(
                rule="frontmatter.name.directory_match",
                severity=SEVERITY_FAIL,
                message=(
                    f"Frontmatter 'name' ('{value}') does not match the "
                    f"parent directory ('{skill_dir.name}')."
                ),
                file=str(skill_md),
                remediation=(
                    "Rename the directory or change 'name' so they match."
                ),
            )
        )


def _validate_description(report: Report, skill_md: Path, value: Any) -> None:
    if value in (None, ""):
        report.add(
            Finding(
                rule="frontmatter.description.required",
                severity=SEVERITY_FAIL,
                message="Frontmatter 'description' is required.",
                file=str(skill_md),
                remediation="Explain what the skill does and when to use it.",
            )
        )
        return
    if not isinstance(value, str):
        report.add(
            Finding(
                rule="frontmatter.description.type",
                severity=SEVERITY_FAIL,
                message="Frontmatter 'description' must be a string.",
                file=str(skill_md),
            )
        )
        return
    if len(value) > MAX_DESCRIPTION_LENGTH:
        report.add(
            Finding(
                rule="frontmatter.description.length",
                severity=SEVERITY_FAIL,
                message=(
                    f"Frontmatter 'description' is {len(value)} characters; "
                    f"maximum is {MAX_DESCRIPTION_LENGTH}."
                ),
                file=str(skill_md),
                remediation="Tighten the description while retaining triggers.",
            )
        )
    lowered = value.lower()
    triggered = [phrase for phrase in VAGUE_PHRASES if phrase in lowered]
    if triggered:
        report.add(
            Finding(
                rule="frontmatter.description.vague",
                severity=SEVERITY_WARN,
                message=(
                    "Description contains vague phrases that hurt trigger "
                    "quality: " + ", ".join(triggered)
                ),
                file=str(skill_md),
                remediation="Replace vague phrases with concrete triggers.",
            )
        )
    if "use when" not in lowered and "activate" not in lowered:
        report.add(
            Finding(
                rule="frontmatter.description.trigger",
                severity=SEVERITY_WARN,
                message=(
                    "Description does not clearly state when to activate."
                ),
                file=str(skill_md),
                remediation=(
                    "Include a 'Use when ...' clause with specific triggers."
                ),
            )
        )


def _validate_license(report: Report, skill_md: Path, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        report.add(
            Finding(
                rule="frontmatter.license.type",
                severity=SEVERITY_WARN,
                message="Frontmatter 'license' should be a non-empty string.",
                file=str(skill_md),
            )
        )


def _validate_compatibility(report: Report, skill_md: Path, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        report.add(
            Finding(
                rule="frontmatter.compatibility.type",
                severity=SEVERITY_FAIL,
                message="Frontmatter 'compatibility' must be a string.",
                file=str(skill_md),
            )
        )
        return
    if len(value) > MAX_COMPATIBILITY_LENGTH:
        report.add(
            Finding(
                rule="frontmatter.compatibility.length",
                severity=SEVERITY_FAIL,
                message=(
                    f"Frontmatter 'compatibility' is {len(value)} characters; "
                    f"maximum is {MAX_COMPATIBILITY_LENGTH}."
                ),
                file=str(skill_md),
            )
        )


def _validate_metadata(report: Report, skill_md: Path, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        report.add(
            Finding(
                rule="frontmatter.metadata.type",
                severity=SEVERITY_FAIL,
                message="Frontmatter 'metadata' must be a mapping.",
                file=str(skill_md),
            )
        )
        return
    for key, entry in value.items():
        if not isinstance(entry, str):
            report.add(
                Finding(
                    rule="frontmatter.metadata.value_type",
                    severity=SEVERITY_FAIL,
                    message=(
                        f"Metadata value for '{key}' must be a string. "
                        "Quote version numbers explicitly, for example "
                        "'\"1.0.0\"'."
                    ),
                    file=str(skill_md),
                )
            )


def _validate_allowed_tools(report: Report, skill_md: Path, value: Any) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        report.add(
            Finding(
                rule="frontmatter.allowed_tools.type",
                severity=SEVERITY_WARN,
                message=(
                    "Frontmatter 'allowed-tools' should be a string when used."
                ),
                file=str(skill_md),
            )
        )


def _validate_progressive_disclosure(
    report: Report, skill_dir: Path, skill_md: Path
) -> None:
    text = _read_text(skill_md)
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_LINES:
        report.add(
            Finding(
                rule="progressive_disclosure.skill_length",
                severity=SEVERITY_FAIL,
                message=(
                    f"SKILL.md has {line_count} lines; maximum is "
                    f"{MAX_SKILL_LINES}. Move detail into references/."
                ),
                file=str(skill_md),
                remediation=(
                    "Extract sections into focused reference files and link "
                    "them from SKILL.md."
                ),
            )
        )
    elif line_count > 450:
        report.add(
            Finding(
                rule="progressive_disclosure.skill_length_soft",
                severity=SEVERITY_WARN,
                message=(
                    f"SKILL.md has {line_count} lines; target 300-450 for "
                    "progressive disclosure."
                ),
                file=str(skill_md),
            )
        )

    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        referenced_paths = _collect_referenced_relative_paths(skill_dir)
        for entry in references_dir.iterdir():
            if entry.is_file() and entry.suffix == ".md":
                rel = entry.relative_to(skill_dir).as_posix()
                if rel not in referenced_paths:
                    report.add(
                        Finding(
                            rule="progressive_disclosure.unlinked_reference",
                            severity=SEVERITY_WARN,
                            message=(
                                f"Reference file '{rel}' is not linked from "
                                "SKILL.md or another linked file."
                            ),
                            file=str(entry),
                            remediation=(
                                "Link the reference or remove it."
                            ),
                        )
                    )


def _collect_referenced_relative_paths(skill_dir: Path) -> set[str]:
    referenced: set[str] = set()
    queue: list[Path] = [skill_dir / "SKILL.md"]
    visited: set[Path] = set()

    while queue:
        current = queue.pop()
        if current in visited or not current.exists() or not current.is_file():
            continue
        visited.add(current)
        text = _read_text(current)
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(2).strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            candidate = (current.parent / target).resolve()
            try:
                rel = candidate.relative_to(skill_dir.resolve()).as_posix()
            except ValueError:
                continue
            referenced.add(rel)
            if candidate.suffix == ".md" and candidate.exists():
                queue.append(candidate)
    return referenced


def _validate_relative_links(
    report: Report, skill_dir: Path
) -> None:
    for markdown_file in _iter_markdown_files(skill_dir):
        text = _read_text(markdown_file)
        fences = _iter_code_fence_ranges(text)
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(2).strip()
            if not target or target.startswith(
                ("http://", "https://", "mailto:", "#")
            ):
                continue
            line_no = _line_of_offset(text, match.start())
            if _line_in_fence(fences, line_no):
                # Links inside fenced code blocks are example content.
                continue
            local_target = target.split("#", 1)[0]
            if not local_target:
                continue
            resolved = (markdown_file.parent / local_target).resolve()
            if not resolved.exists():
                report.add(
                    Finding(
                        rule="links.missing_target",
                        severity=SEVERITY_FAIL,
                        message=(
                            f"Relative link points to a missing file: "
                            f"'{target}'"
                        ),
                        file=str(markdown_file),
                        line=line_no,
                        remediation=(
                            "Fix the path or create the referenced file."
                        ),
                    )
                )


def _line_of_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _iter_markdown_files(skill_dir: Path) -> Iterable[Path]:
    for entry in skill_dir.rglob("*.md"):
        if any(part == ".git" for part in entry.parts):
            continue
        yield entry


def _validate_scripts_and_assets(report: Report, skill_dir: Path) -> None:
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for entry in scripts_dir.rglob("*"):
            if entry.is_file() and entry.suffix in {".exe", ".dll", ".so", ".bin"}:
                report.add(
                    Finding(
                        rule="scripts.binary_present",
                        severity=SEVERITY_FAIL,
                        message=(
                            "Binary artifact detected in scripts/. Binaries "
                            "must not be committed to the default branch."
                        ),
                        file=str(entry),
                    )
                )


def _security_scan(report: Report, skill_dir: Path) -> None:
    for candidate in skill_dir.rglob("*"):
        if not candidate.is_file():
            continue
        if candidate.suffix not in TEXT_FILE_SUFFIXES:
            continue
        text = _read_text(candidate)
        _scan_secret_patterns(report, candidate, text)
        _scan_sap_hostnames(report, candidate, text)
        _scan_user_paths(report, candidate, text)


def _scan_secret_patterns(report: Report, path: Path, text: str) -> None:
    # The validator's own source defines the patterns it looks for; scanning
    # it re-reports each literal. Skip self-scan for these patterns.
    if path.name == "validate_skill.py":
        return
    lines = text.splitlines()
    for pattern, message in SECRET_PATTERNS:
        lowered_pattern = pattern.lower()
        for line_no, line in enumerate(lines, start=1):
            if pattern in line or lowered_pattern in line.lower():
                context = line.strip()
                if _looks_like_placeholder(context):
                    continue
                if _has_documentation_context(lines, line_no):
                    continue
                _, _, tail = context.partition(pattern)
                redacted = _redact(tail) if tail else "<none>"
                report.add(
                    Finding(
                        rule="security.secret_heuristic",
                        severity=SEVERITY_WARN,
                        message=(
                            f"{message} (pattern: '{pattern}', redacted: "
                            f"'{redacted}')"
                        ),
                        file=str(path),
                        line=line_no,
                        remediation=(
                            "Use placeholders or environment variables; never "
                            "commit real secret material."
                        ),
                    )
                )


def _has_documentation_context(lines: list[str], line_no: int, window: int = 3) -> bool:
    """Return True when a documentation trigger word appears in the current
    line or the *window* lines immediately above or below."""
    start = max(0, line_no - 1 - window)
    end = min(len(lines), line_no + window)
    snippet = "\n".join(lines[start:end])
    return _looks_like_documentation(snippet)


_MIME_OR_NS_PREFIXES = (
    "application/",
    "text/",
    "image/",
    "audio/",
    "video/",
    "vnd.",
    "urn:",
    "http://",
    "https://",
    "com.",
    "org.",
    "net.",
)


def _is_mime_or_ns_prefix(line: str, match_start: int) -> bool:
    """Return True when the match appears to be inside a MIME type,
    namespace identifier, URI, or reverse-domain package identifier."""
    prefix_span = line[max(0, match_start - 32):match_start].lower()
    for token in _MIME_OR_NS_PREFIXES:
        if token in prefix_span:
            return True
    # A slash immediately before the match usually means it is a path or
    # MIME type body.
    if match_start > 0 and line[match_start - 1] in "/":
        return True
    return False


def _scan_sap_hostnames(report: Report, path: Path, text: str) -> None:
    # The validator's own source defines the SAP hostname pattern and
    # references it by identifier. Skip self-scan.
    if path.name == "validate_skill.py":
        return
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        for match in SAP_HOSTNAME_HINT.finditer(line):
            host = match.group(0)
            lowered_host = host.lower()
            hostname_only = lowered_host.split(":", 1)[0]
            tld = hostname_only.rsplit(".", 1)[-1]
            if tld in NON_HOSTNAME_SUFFIXES:
                continue
            if _is_mime_or_ns_prefix(line, match.start()):
                # Matches inside MIME types / namespaces / paths are not
                # hostnames (for example 'application/vnd.sap.adt.x.v1').
                continue
            if _looks_like_placeholder(line):
                continue
            if _has_documentation_context(lines, line_no):
                continue
            if hostname_only.startswith(("sap.example", "sap.internal.example")):
                continue
            if "example.com" in hostname_only:
                continue
            report.add(
                Finding(
                    rule="security.sap_hostname",
                    severity=SEVERITY_WARN,
                    message=(
                        "Possible SAP hostname in text. Replace with a "
                        "documented placeholder unless it is intentionally "
                        "public documentation."
                    ),
                    file=str(path),
                    line=line_no,
                    remediation=(
                        "Use a placeholder such as 'sap.example.com'."
                    ),
                )
            )
            break


def _scan_user_paths(report: Report, path: Path, text: str) -> None:
    for pattern in (USER_HOME_PATTERN, NIX_HOME_PATTERN):
        for match in pattern.finditer(text):
            snippet = match.group(0)
            if _looks_like_placeholder(snippet):
                continue
            line_no = _line_of_offset(text, match.start())
            report.add(
                Finding(
                    rule="security.user_home_path",
                    severity=SEVERITY_WARN,
                    message=(
                        "Developer-specific home directory path detected. "
                        "Replace with a portable placeholder."
                    ),
                    file=str(path),
                    line=line_no,
                    remediation=(
                        "Use '<home>' or environment variables in documentation."
                    ),
                )
            )


def _validate_repository_readiness(
    report: Report, skill_dir: Path, repository_root: Path | None
) -> None:
    if repository_root is None:
        return
    if not repository_root.exists():
        report.add(
            Finding(
                rule="repository.root",
                severity=SEVERITY_FAIL,
                message=f"Repository root not found: {repository_root}",
            )
        )
        return

    resolved_root = repository_root.resolve()
    resolved_skill = skill_dir.resolve()
    try:
        relative = resolved_skill.relative_to(resolved_root)
    except ValueError:
        report.add(
            Finding(
                rule="repository.skill_layout",
                severity=SEVERITY_FAIL,
                message=(
                    "Skill directory is not inside the repository root."
                ),
                remediation="Move the skill under 'skills/<slug>/'.",
            )
        )
        return
    parts = relative.parts
    if len(parts) < 2 or parts[0] != "skills":
        report.add(
            Finding(
                rule="repository.skill_layout",
                severity=SEVERITY_FAIL,
                message=(
                    "Skill must live at 'skills/<slug>/SKILL.md' under the "
                    "repository root."
                ),
            )
        )

    _check_repo_file(report, repository_root, "README.md", SEVERITY_WARN)
    _check_repo_file(report, repository_root, "LICENSE", SEVERITY_WARN)
    _check_repo_file(report, repository_root, "SECURITY.md", SEVERITY_WARN)
    _check_repo_file(report, repository_root, "CONTRIBUTING.md", SEVERITY_WARN)

    readme = repository_root / "README.md"
    if readme.exists():
        text = _read_text(readme)
        if resolved_skill.name not in text:
            report.add(
                Finding(
                    rule="repository.readme_catalog",
                    severity=SEVERITY_WARN,
                    message=(
                        "Root README.md does not mention this skill slug in the "
                        "catalog."
                    ),
                    file=str(readme),
                    remediation=(
                        "Add the skill row to the catalog table."
                    ),
                )
            )


def _check_repo_file(
    report: Report,
    repository_root: Path,
    filename: str,
    severity: str,
) -> None:
    target = repository_root / filename
    if not target.exists():
        report.add(
            Finding(
                rule=f"repository.{filename.lower().replace('.', '_')}",
                severity=severity,
                message=f"Repository file missing: {filename}",
                file=str(target),
                remediation=f"Add a {filename} file to the repository root.",
            )
        )


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def _human_render(report: Report) -> str:
    counts = report.counts()
    lines: list[str] = []
    lines.append(f"Skill: {report.skill_directory}")
    lines.append(
        "Summary: "
        f"PASS={counts.get(SEVERITY_PASS, 0)} "
        f"WARN={counts.get(SEVERITY_WARN, 0)} "
        f"FAIL={counts.get(SEVERITY_FAIL, 0)}"
    )
    if not report.findings:
        lines.append("No findings.")
        return "\n".join(lines)

    order = {SEVERITY_FAIL: 0, SEVERITY_WARN: 1, SEVERITY_PASS: 2}
    for finding in sorted(
        report.findings, key=lambda f: (order.get(f.severity, 9), f.rule)
    ):
        location = ""
        if finding.file:
            location = f" [{finding.file}"
            if finding.line is not None:
                location += f":{finding.line}"
            location += "]"
        remediation = ""
        if finding.remediation:
            remediation = f"\n    Fix: {finding.remediation}"
        lines.append(
            f"[{finding.severity}] {finding.rule}: {finding.message}"
            f"{location}{remediation}"
        )
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI entry point
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_skill",
        description=(
            "Validate an Agent Skill directory against the "
            "sap-skills-creator quality gates."
        ),
    )
    parser.add_argument(
        "skill_directory",
        help="Path to the skill directory containing SKILL.md.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON on stdout.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures for the exit code.",
    )
    parser.add_argument(
        "--repository-root",
        default=None,
        help=(
            "Path to the repository root. When set, repository readiness "
            "checks run (README catalog, LICENSE, SECURITY, CONTRIBUTING)."
        ),
    )
    return parser


def run_validation(
    skill_directory: str,
    repository_root: str | None,
) -> Report:
    skill_dir = Path(skill_directory)
    report = Report(skill_directory=str(skill_dir))
    skill_md = _validate_structure(report, skill_dir)
    if skill_md is None:
        return report
    _validate_frontmatter(report, skill_dir, skill_md)
    _validate_progressive_disclosure(report, skill_dir, skill_md)
    _validate_relative_links(report, skill_dir)
    _validate_scripts_and_assets(report, skill_dir)
    _security_scan(report, skill_dir)
    if repository_root:
        _validate_repository_readiness(
            report, skill_dir, Path(repository_root)
        )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2

    try:
        report = run_validation(args.skill_directory, args.repository_root)
    except Exception as exc:  # pragma: no cover - defensive
        message = f"validate_skill: internal error: {exc}"
        if args.json:
            print(json.dumps({"error": message}))
        else:
            print(message, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(_human_render(report))

    if report.has_failures():
        return 1
    if args.strict and report.has_warnings():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
