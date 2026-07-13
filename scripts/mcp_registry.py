#!/usr/bin/env python3
"""MCP registry loader and launcher-plan generator.

This module is intentionally offline. It does not start MCP processes or touch
credentials; it only normalizes registry metadata for router and healthcheck.
"""
import argparse
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = SKILL_DIR / "config" / "mcp_registry.json"


def load_registry(path=None):
    registry_path = Path(path) if path else REGISTRY_PATH
    with registry_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    data.setdefault("mcps", {})
    data.setdefault("default_chains", {})
    return data


def list_mcps(kind=None, include_planned=True):
    data = load_registry()
    rows = []
    for name, spec in sorted(data["mcps"].items()):
        if kind and spec.get("kind") != kind:
            continue
        if not include_planned and spec.get("planned"):
            continue
        rows.append({"name": name, **spec})
    return rows


def get_mcp(name):
    return load_registry()["mcps"].get(name)


def get_chain(name):
    data = load_registry()
    return data["default_chains"].get(name, [])


def healthcheck_spec():
    """Return registry entries in healthcheck-compatible shape."""
    spec = {}
    for name, item in load_registry()["mcps"].items():
        entry = {
            "env_vars": item.get("env_vars", []),
            "probe_command": item.get("probe_command"),
            "probe_command_alt": item.get("probe_command_alt"),
            "criticality": item.get("criticality", "LOW"),
            "description": item.get("description") or _describe(name, item),
        }
        if item.get("config_file"):
            entry["config_file"] = item["config_file"]
        if item.get("planned"):
            entry["planned"] = True
        spec[name] = entry
    return spec


def launcher_plan(profile):
    """Build an execution-neutral launcher plan for a routing profile."""
    data = load_registry()
    chain = data["default_chains"].get(profile, [])
    return {
        "profile": profile,
        "chain": [
            {"name": name, **data["mcps"].get(name, {"missing": True})}
            for name in chain
        ],
        "approval_model": "plan_* -> external approval broker -> commit_*",
        "note": "Plan only. No MCP process is started and no credential is exposed.",
    }


def _describe(name, item):
    caps = ", ".join(item.get("capabilities", [])[:4])
    suffix = f": {caps}" if caps else ""
    return f"{name} ({item.get('kind', 'mcp')}){suffix}"


def main():
    parser = argparse.ArgumentParser(description="Inspect SAP Router MCP registry")
    sub = parser.add_subparsers(dest="command", required=True)

    list_p = sub.add_parser("list", help="List MCPs")
    list_p.add_argument("--kind", help="Filter by kind, e.g. cpi, gui, cap")
    list_p.add_argument("--active-only", action="store_true", help="Hide planned candidates")

    show_p = sub.add_parser("show", help="Show one MCP")
    show_p.add_argument("name")

    chain_p = sub.add_parser("chain", help="Show fallback chain")
    chain_p.add_argument("profile")

    launch_p = sub.add_parser("launcher", help="Show launcher plan for a profile")
    launch_p.add_argument("profile")

    health_p = sub.add_parser("health-spec", help="Emit healthcheck-compatible spec")

    args = parser.parse_args()
    if args.command == "list":
        print(json.dumps(list_mcps(args.kind, not args.active_only), indent=2))
    elif args.command == "show":
        spec = get_mcp(args.name)
        if not spec:
            raise SystemExit(f"unknown MCP: {args.name}")
        print(json.dumps({"name": args.name, **spec}, indent=2))
    elif args.command == "chain":
        print(json.dumps({"profile": args.profile, "chain": get_chain(args.profile)}, indent=2))
    elif args.command == "launcher":
        print(json.dumps(launcher_plan(args.profile), indent=2))
    elif args.command == "health-spec":
        print(json.dumps(healthcheck_spec(), indent=2))


if __name__ == "__main__":
    main()
