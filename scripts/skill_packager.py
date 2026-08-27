#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Packager & Distributor for SAP Router / Harness.
Adheres to skill-share and skill-creator patterns.

Validates skill directories, checks frontmatter, builds distributable .zip
archives, and formats sharing cards for team distribution.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".agents" / "skills"


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extracts YAML frontmatter from a markdown file."""
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    raw_yaml = parts[1]
    result: dict[str, str] = {}
    current_key = ""
    current_val = []

    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line and not line.startswith("-"):
            if current_key:
                result[current_key] = " ".join(current_val).strip()
            key, val = line.split(":", 1)
            current_key = key.strip()
            current_val = [val.strip().strip('"').strip("'")]
        elif current_key:
            current_val.append(line.strip().strip('"').strip("'"))

    if current_key:
        result[current_key] = " ".join(current_val).strip()

    return result


def validate_skill(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validates the skill folder against skill-creator conventions."""
    errors = []
    if not skill_dir.is_dir():
        return False, [f"Skill path is not a directory: {skill_dir}"]

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return False, [f"Missing required SKILL.md in {skill_dir}"]

    content = skill_file.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    name = fm.get("name")
    if not name:
        errors.append("SKILL.md frontmatter missing 'name'.")
    elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(f"Skill name '{name}' should be kebab-case.")

    desc = fm.get("description")
    if not desc:
        errors.append("SKILL.md frontmatter missing 'description'.")

    return len(errors) == 0, errors


def package_skill(skill_dir: Path, output_zip: Path | None = None) -> Path:
    """Packages a skill folder into a clean .zip bundle."""
    valid, errors = validate_skill(skill_dir)
    if not valid:
        raise ValueError(f"Skill validation failed for {skill_dir.name}: {'; '.join(errors)}")

    if not output_zip:
        dist_dir = ROOT / "scratch" / "skill-packages"
        dist_dir.mkdir(parents=True, exist_ok=True)
        output_zip = dist_dir / f"{skill_dir.name}.zip"
    else:
        output_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in skill_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(skill_dir.parent)
                archive.write(file_path, arcname=str(rel_path))

    return output_zip


def format_slack_card(skill_name: str, description: str, zip_path: Path) -> dict[str, Any]:
    """Generates Slack block kit payload as per skill-share specification."""
    return {
        "text": f"New Skill Published: *{skill_name}*",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 New Skill: {skill_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📦 Package: `{zip_path.name}` ({zip_path.stat().st_size} bytes)"
                    }
                ]
            }
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SAP Harness Skill Packager and Distributor")
    # Two call shapes are accepted:
    #   skill_packager.py <skill> [--validate-only]
    #   skill_packager.py validate --skill <skill>
    # The second is the form the harness verification plan and `sap_harness
    # share` use; both resolve to the same code path.
    parser.add_argument("command", nargs="?", help="'validate', 'package', or a skill name")
    parser.add_argument("skill_positional", nargs="?", help="Skill name when a command is given")
    parser.add_argument("--skill", help="Name of skill directory in .agents/skills or path to skill")
    parser.add_argument("--output", help="Optional output zip file path")
    parser.add_argument("--slack-json", action="store_true", help="Print Slack block kit card")
    parser.add_argument("--validate-only", action="store_true", help="Only validate without packaging")

    args = parser.parse_args()

    commands = {"validate", "package"}
    if args.command in commands:
        skill_arg = args.skill or args.skill_positional
        validate_only = args.validate_only or args.command == "validate"
    else:
        skill_arg = args.skill or args.command
        validate_only = args.validate_only

    if not skill_arg:
        parser.error("a skill is required: pass it positionally or with --skill")

    skill_path = Path(skill_arg)
    if not skill_path.exists():
        skill_path = SKILLS_DIR / skill_arg
    if not skill_path.exists():
        print(f"Error: Skill not found at {skill_arg} or {skill_path}")
        return 1

    valid, errors = validate_skill(skill_path)
    if not valid:
        print(f"Validation FAILED for '{skill_path.name}':")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"PASS: '{skill_path.name}' is valid.")
    if validate_only:
        return 0

    out_zip = package_skill(skill_path, Path(args.output) if args.output else None)
    print(f"Packaged skill to: {out_zip}")

    if args.slack_json:
        fm = parse_frontmatter((skill_path / "SKILL.md").read_text(encoding="utf-8"))
        card = format_slack_card(fm.get("name", skill_path.name), fm.get("description", ""), out_zip)
        print("\n--- Slack Notification Payload ---")
        print(json.dumps(card, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
