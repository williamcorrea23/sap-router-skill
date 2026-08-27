#!/usr/bin/env python3
"""Validate skill/MCP/profile catalog consistency.

Runs two independent validators and merges their findings:

1. validate()  - capability reachability, approval gating and catalogue /
   registry reconciliation (defined in this module).
2. sap_router_core.registry.validate_catalog() - registry schema, route and
   profile integrity, bundled-source locking.

Both always run. Neither can mask the other: a failure in either fails the
whole check. Exit code is 1 when any error is reported.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRIES = ROOT / ".agents" / "registries"
REGISTRY = REGISTRIES / "mcp-capabilities.json"
MCP_CONFIG = ROOT / ".mcp.json"
SKILLS_DIR = ROOT / ".agents" / "skills"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if(path: Path, default: dict) -> dict:
    return load_json(path) if path.exists() else default


def skill_names() -> set[str]:
    return {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}


def validate(strict: bool = False) -> dict:
    """Capability reachability plus catalogue reconciliation.

    A capability is reachable only when at least one of its candidate servers
    is present in .mcp.json mcpServers. A server listed only under
    plannedServers is known but cannot be launched, so it never counts toward
    reachability - that is what fail-closed means here.
    """
    errors: list[str] = []
    warnings: list[str] = []
    gaps: list[str] = []

    registry = load_json(REGISTRY)
    mcp = load_json(MCP_CONFIG)
    configured = set(mcp.get("mcpServers", {}))
    planned = set(mcp.get("plannedServers", {}))
    skills = skill_names()

    if registry.get("default_policy") != "fail_closed":
        errors.append("Registry default_policy must be fail_closed.")

    for cap, spec in registry.get("capabilities", {}).items():
        primary = spec.get("primary")
        candidates = [primary] + list(spec.get("fallbacks", []))
        if not primary:
            errors.append("{0}: missing primary.".format(cap))

        reachable = []
        for server in candidates:
            if not server or server.startswith("plugin:"):
                continue
            if server in configured:
                reachable.append(server)
            elif server in planned:
                warnings.append(
                    "{0}: server {1} is planned only - not launchable, excluded from routing.".format(cap, server)
                )
            else:
                errors.append(
                    "{0}: server {1} is in neither mcpServers nor plannedServers of .mcp.json.".format(cap, server)
                )

        if not reachable:
            msg = "{0}: no reachable provider - every candidate is planned or unknown.".format(cap)
            if spec.get("status") == "planned":
                gaps.append(msg + " Declared planned; fail-closed at runtime.")
            else:
                errors.append(msg)

        if spec.get("mutation") and not spec.get("requires_approval"):
            errors.append("{0}: mutating capability must require approval.".format(cap))

    for profile, spec in registry.get("profiles", {}).items():
        for skill in spec.get("skills", []):
            if skill not in skills:
                warnings.append("{0}: skill {1} missing from .agents/skills.".format(profile, skill))
        for cap in spec.get("capabilities", []):
            if cap not in registry.get("capabilities", {}):
                errors.append("{0}: capability {1} missing.".format(profile, cap))

    errors.extend(reconcile_catalogue())

    return {
        "status": "FAIL" if errors else "PASS",
        "skills": len(skills),
        "mcp_servers": len(configured),
        "planned_servers": len(planned),
        "capabilities": len(registry.get("capabilities", {})),
        "profiles": len(registry.get("profiles", {})),
        "errors": errors,
        "warnings": warnings,
        "gaps": gaps,
    }


def reconcile_catalogue() -> list[str]:
    """Every catalogued MCP source must resolve to a registry record.

    Guards against the failure this check exists for: a repository listed in
    bundled-sources.json that appears nowhere in mcps.json or
    mcp-candidates.json, so it reads as integrated while being unreachable
    and unreviewed.
    """
    errors: list[str] = []
    sources = load_json_if(REGISTRIES / "bundled-sources.json", {"sources": []}).get("sources", [])
    server_records = load_json_if(REGISTRIES / "mcps.json", {"servers": []}).get("servers", [])
    candidate_records = load_json_if(REGISTRIES / "mcp-candidates.json", {"candidates": []}).get("candidates", [])
    servers = {s["id"] for s in server_records}
    candidates = {c["id"] for c in candidate_records}
    known = servers | candidates

    for source in sources:
        if source.get("kind") != "mcp":
            continue
        sid = source["id"]
        wired = source.get("wired_as")
        if sid in known:
            continue
        if wired and wired in known:
            continue
        if wired:
            errors.append(
                "bundled source {0}: wired_as '{1}' is not a registered server or candidate.".format(sid, wired)
            )
        else:
            errors.append(
                "bundled source {0}: kind=mcp but absent from mcps.json and mcp-candidates.json "
                "(catalogued without being wired or reviewed).".format(sid)
            )

    for record in candidate_records:
        if record.get("status") == "disabled_candidate" and not record.get("reason"):
            errors.append("candidate {0}: disabled candidates must state a reason.".format(record["id"]))

    for server in server_records:
        if server.get("status") != "enabled":
            continue
        if not server.get("runtime", {}).get("command"):
            errors.append("server {0}: enabled but has no runtime command.".format(server["id"]))

    return errors


def run_registry_validator() -> dict:
    sys.path.insert(0, str(ROOT / "python"))
    try:
        from sap_router_core.registry import validate_catalog as registry_validate
    except Exception as exc:  # noqa: BLE001 - surfaced, never swallowed
        return {"status": "FAIL", "errors": ["registry validator unavailable: {0}".format(exc)], "warnings": []}
    try:
        return registry_validate()
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAIL", "errors": ["registry validator raised: {0}".format(exc)], "warnings": []}


def merge(local: dict, registry: dict) -> dict:
    merged = dict(local)
    merged["errors"] = list(local.get("errors", [])) + [
        "[registry] {0}".format(m) for m in registry.get("errors", [])
    ]
    merged["warnings"] = list(local.get("warnings", [])) + [
        "[registry] {0}".format(m) for m in registry.get("warnings", [])
    ]
    merged["registry_counts"] = registry.get("counts", {})
    merged["status"] = "FAIL" if merged["errors"] else "PASS"
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SAP Router catalog.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Reserved for future tightening; reachability and approval checks always run.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Write validation JSON to this path.")
    args = parser.parse_args()

    result = merge(validate(strict=args.strict), run_registry_validator())

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            "Catalog: {status} skills={skills} mcps={mcps} planned={planned} "
            "capabilities={caps} profiles={profiles}".format(
                status=result["status"],
                skills=result.get("skills", "n/a"),
                mcps=result.get("mcp_servers", "n/a"),
                planned=result.get("planned_servers", "n/a"),
                caps=result.get("capabilities", "n/a"),
                profiles=result.get("profiles", "n/a"),
            )
        )
        for key in ("errors", "warnings", "gaps"):
            for msg in result.get(key, []):
                print("  {0}: {1}".format(key[:-1].upper(), msg))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
