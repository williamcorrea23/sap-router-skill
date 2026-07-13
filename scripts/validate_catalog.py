#!/usr/bin/env python3
"""Validate skill/MCP/profile catalog consistency."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / ".agents" / "registries" / "mcp-capabilities.json"
MCP_CONFIG = ROOT / ".mcp.json"
SKILLS_DIR = ROOT / ".agents" / "skills"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def skill_names() -> set[str]:
    return {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}


def validate(strict: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    registry = load_json(REGISTRY)
    mcp = load_json(MCP_CONFIG)
    servers = set(mcp.get("mcpServers", {}))
    skills = skill_names()

    if registry.get("default_policy") != "fail_closed":
        errors.append("Registry default_policy must be fail_closed.")

    for cap, spec in registry.get("capabilities", {}).items():
        primary = spec.get("primary")
        candidates = [primary] + list(spec.get("fallbacks", []))
        if not primary:
            errors.append(f"{cap}: missing primary.")
        for server in candidates:
            if server and not server.startswith("plugin:") and server not in servers:
                msg = f"{cap}: server {server} not configured in .mcp.json."
                (errors if strict else warnings).append(msg)
        if spec.get("mutation") and not spec.get("requires_approval"):
            errors.append(f"{cap}: mutating capability must require approval.")

    for profile, spec in registry.get("profiles", {}).items():
        for skill in spec.get("skills", []):
            if skill not in skills:
                warnings.append(f"{profile}: skill {skill} missing from .agents/skills.")
        for cap in spec.get("capabilities", []):
            if cap not in registry.get("capabilities", {}):
                errors.append(f"{profile}: capability {cap} missing.")

    return {
        "status": "FAIL" if errors else "PASS",
        "skills": len(skills),
        "mcp_servers": len(servers),
        "capabilities": len(registry.get("capabilities", {})),
        "profiles": len(registry.get("profiles", {})),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SAP Router catalog.")
    parser.add_argument("--strict", action="store_true", help="Treat missing MCP fallback config as error.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Write validation JSON to this path.")
    args = parser.parse_args()
    if (ROOT / ".agents" / "registries" / "mcps.json").exists():
        sys.path.insert(0, str(ROOT / "python"))
        from sap_router_core.registry import validate_catalog
        result = validate_catalog()
    else:
        result = validate(strict=args.strict)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        counts = result.get("counts", {})
        skills = result.get("skills", "n/a")
        mcps = result.get("mcp_servers", counts.get("servers", "n/a"))
        caps = result.get("capabilities", counts.get("capabilities", "n/a"))
        profiles = result.get("profiles", counts.get("profiles", "n/a"))
        print(f"Catalog: {result['status']} skills={skills} mcps={mcps} capabilities={caps} profiles={profiles}")
        for key in ("errors", "warnings"):
            for msg in result.get(key, []):
                print(f"  {key[:-1].upper()}: {msg}")
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
