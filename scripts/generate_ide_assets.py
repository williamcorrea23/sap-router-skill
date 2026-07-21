#!/usr/bin/env python3
"""Generate/check multi-IDE SAP Router assets from canonical .agents source."""
from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_SKILLS = ROOT / ".agents" / "skills"
TARGET_SKILLS = {
    "claude": ROOT / ".claude" / "skills",
    "gemini": ROOT / ".gemini" / "skills",
}
TEXT_TARGETS = {
    "codex": {
        "path": ROOT / ".codex" / "AGENTS.md",
        "label": "Codex",
    },
    "cursor": {
        "path": ROOT / ".cursor" / "AGENTS.md",
        "label": "Cursor",
    },
    "kiro": {
        "path": ROOT / ".kiro" / "steering" / "sap-router.md",
        "label": "Kiro",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def manifest() -> dict:
    skills = sorted(CANONICAL_SKILLS.glob("*/SKILL.md"))
    profiles = sorted((ROOT / ".agents" / "profiles").glob("*.json"))
    registries = sorted((ROOT / ".agents" / "registries").glob("*.json"))
    versions_path = ROOT / ".agents" / "registries" / "versions.json"
    versions = json.loads(versions_path.read_text(encoding="utf-8")) if versions_path.exists() else {}
    return {
        "schema_version": 1,
        "source": ".agents",
        "skill_count": len(skills),
        "skill_count_target": versions.get("skill_count_target"),
        "profile_count": len(profiles),
        "profile_count_target": versions.get("profile_count_target"),
        "registry_count": len(registries),
        "skills_hash": hashlib.sha256("".join(sha256(p) for p in skills).encode("utf-8")).hexdigest(),
        "profiles_hash": hashlib.sha256("".join(sha256(p) for p in profiles).encode("utf-8")).hexdigest(),
        "registries_hash": hashlib.sha256("".join(sha256(p) for p in registries).encode("utf-8")).hexdigest(),
    }


def text_body(target: str) -> str:
    data = manifest()
    label = TEXT_TARGETS[target]["label"]
    return (
        f"# SAP Router Skill for {label}\n\n"
        "Canonical source: `.agents/`.\n"
        "Karpathy wrapper: mandatory. Caveman compression: default.\n"
        "Do not copy or fork skill bodies here; regenerate from canonical source.\n\n"
        "Dynamic local discovery:\n"
        "- search skills: `python scripts/source_catalog.py search \"task description\"`\n"
        "- search MCPs: `python scripts/mcp_launcher.py search --query \"task description\"`\n"
        "- bundled MCPs are disabled candidates until reviewed; no runtime GitHub lookup.\n\n"
        "Local optimization:\n"
        "- prefer `rtk` for supported verbose CLI commands.\n"
        "- use Context Mode for large outputs, indexed fetches, and session checkpoints.\n\n"
        "Parity proof:\n"
        f"- skills: {data['skill_count']} sha256:{data['skills_hash']}\n"
        f"- profiles: {data['profile_count']} sha256:{data['profiles_hash']}\n"
        f"- registries: {data['registry_count']} sha256:{data['registries_hash']}\n\n"
        "Run:\n"
        "`python scripts/generate_ide_assets.py check`\n"
    )


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def compare_dirs(left: Path, right: Path) -> list[str]:
    diffs: list[str] = []
    if not right.exists():
        return [f"missing:{right}"]
    for src in left.rglob("SKILL.md"):
        rel = src.relative_to(left)
        dst = right / rel
        if not dst.exists():
            diffs.append(f"missing:{dst}")
        elif not filecmp.cmp(src, dst, shallow=False):
            diffs.append(f"diff:{dst}")
    return diffs


def generate(targets: list[str]) -> dict:
    changed = []
    for target in targets:
        if target in TARGET_SKILLS:
            copy_tree(CANONICAL_SKILLS, TARGET_SKILLS[target])
            changed.append(str(TARGET_SKILLS[target].relative_to(ROOT)))
        if target in TEXT_TARGETS:
            spec = TEXT_TARGETS[target]
            spec["path"].parent.mkdir(parents=True, exist_ok=True)
            spec["path"].write_text(text_body(target), encoding="utf-8")
            changed.append(str(spec["path"].relative_to(ROOT)))
    manifest_path = ROOT / "generated-assets.json"
    manifest_path.write_text(json.dumps(manifest(), indent=2) + "\n", encoding="utf-8")
    changed.append(str(manifest_path.relative_to(ROOT)))
    return {"status": "OK", "generated": changed}


def check() -> dict:
    data = manifest()
    result = {
        "canonical_skills": data["skill_count"],
        "canonical_profiles": data["profile_count"],
        "skill_count_target": data.get("skill_count_target"),
        "profile_count_target": data.get("profile_count_target"),
        "targets": {},
        "status": "PASS",
    }
    if data.get("skill_count_target") is not None and data["skill_count"] != int(data["skill_count_target"]):
        result["status"] = "FAIL"
        result.setdefault("errors", []).append(f"skills {data['skill_count']} != target {data['skill_count_target']}")
    if data.get("profile_count_target") is not None and data["profile_count"] != int(data["profile_count_target"]):
        result["status"] = "FAIL"
        result.setdefault("errors", []).append(f"profiles {data['profile_count']} != target {data['profile_count_target']}")
    for target, path in TARGET_SKILLS.items():
        diffs = compare_dirs(CANONICAL_SKILLS, path)
        result["targets"][target] = {"path": str(path.relative_to(ROOT)), "diffs": diffs, "skills": len(list(path.glob("*/SKILL.md"))) if path.exists() else 0}
        if diffs:
            result["status"] = "FAIL"
    for target, spec in TEXT_TARGETS.items():
        path = spec["path"]
        diffs = [] if path.exists() and path.read_text(encoding="utf-8") == text_body(target) else [f"diff:{path}"]
        result["targets"][target] = {"path": str(path.relative_to(ROOT)), "diffs": diffs}
        if diffs:
            result["status"] = "FAIL"
    manifest_path = ROOT / "generated-assets.json"
    desired = json.dumps(manifest(), indent=2) + "\n"
    manifest_diffs = [] if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") == desired else [f"diff:{manifest_path}"]
    result["targets"]["manifest"] = {"path": "generated-assets.json", "diffs": manifest_diffs}
    if manifest_diffs:
        result["status"] = "FAIL"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate/check IDE assets.")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--targets", default="all", help="Comma-separated: all,claude,gemini,codex,cursor,kiro")
    sub.add_parser("check")
    sub.add_parser("diff")
    args = parser.parse_args()

    if args.command == "generate":
        targets = list(TARGET_SKILLS) + list(TEXT_TARGETS) if args.targets == "all" else [t.strip() for t in args.targets.split(",")]
        result = generate(targets)
    else:
        result = check()
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in ("OK", "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
