#!/usr/bin/env python3
"""Fail-closed MCP capability launcher and registry inspector."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / ".agents" / "registries" / "mcp-capabilities.json"
MCP_CONFIG = ROOT / ".mcp.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if value and key not in os.environ:
            os.environ[key] = value


def server_ready(server_id: str, config: dict) -> tuple[bool, str]:
    if server_id.startswith("plugin:"):
        return True, "plugin-managed"
    spec = config.get("mcpServers", {}).get(server_id)
    if not spec:
        return False, "not-configured"
    env = spec.get("env", {})
    missing = []
    for value in env.values():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            var = value[2:-1]
            if not os.environ.get(var):
                missing.append(var)
    if missing:
        return False, "missing-env:" + ",".join(sorted(set(missing)))
    return True, "ready"


def list_capability(capability: str | None = None) -> dict:
    registry = load_json(REGISTRY)
    config = load_json(MCP_CONFIG)
    caps = registry.get("capabilities", {})
    selected = {capability: caps[capability]} if capability else caps
    result = {}
    for cap, spec in selected.items():
        candidates = [spec["primary"]] + spec.get("fallbacks", [])
        ready = []
        blocked = []
        for server in candidates:
            ok, reason = server_ready(server, config)
            (ready if ok else blocked).append({"server": server, "reason": reason})
        result[cap] = {
            "selected": ready[0]["server"] if ready else None,
            "ready": ready,
            "blocked": blocked,
            "mutation": spec.get("mutation", False),
            "requires_approval": spec.get("requires_approval", False),
        }
    return result


def probe(server_id: str) -> dict:
    config = load_json(MCP_CONFIG)
    ok, reason = server_ready(server_id, config)
    return {"server": server_id, "ready": ok, "reason": reason}


def run_server(server_id: str) -> int:
    canonical_registry = ROOT / ".agents" / "registries" / "mcps.json"
    if canonical_registry.exists():
        sys.path.insert(0, str(ROOT / "python"))
        from sap_router_core.registry import load_servers
        server = load_servers().get(server_id)
        if not server:
            print(json.dumps({"error": "fallback-candidate-not-promoted", "server": server_id,
                              "reason": "Review and promote the candidate in .agents/registries/mcps.json first."}), file=sys.stderr)
            return 2
        runtime = server.get("runtime", {})
        command = runtime.get("command")
        if not command:
            print(json.dumps({"error": "missing-runtime", "server": server_id}), file=sys.stderr)
            return 2
        missing = [name for name in server.get("auth", {}).get("env_refs", []) if not os.environ.get(name)]
        if missing:
            print(json.dumps({"error": "server-not-ready", "server": server_id, "reason": "missing-env:" + ",".join(missing)}), file=sys.stderr)
            return 2
        env = os.environ.copy()
        env.update({key: str(value) for key, value in runtime.get("env", {}).items()})
        return subprocess.call([command] + runtime.get("args", []), cwd=ROOT, env=env)
    config = load_json(MCP_CONFIG)
    ok, reason = server_ready(server_id, config)
    if not ok:
        print(json.dumps({"error": "server-not-ready", "server": server_id, "reason": reason}), file=sys.stderr)
        return 2
    spec = config["mcpServers"][server_id]
    env = os.environ.copy()
    for key, value in spec.get("env", {}).items():
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env[key] = os.environ.get(value[2:-1], "")
        else:
            env[key] = str(value)
    cmd = [spec["command"]] + spec.get("args", [])
    return subprocess.call(cmd, cwd=ROOT, env=env)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="SAP Router MCP launcher.")
    sub = parser.add_subparsers(dest="command", required=True)
    list_p = sub.add_parser("list")
    list_p.add_argument("--capability")
    list_p.add_argument("--json", action="store_true")
    probe_p = sub.add_parser("probe")
    probe_p.add_argument("--server", required=True)
    probe_p.add_argument("--execute", action="store_true")
    run_p = sub.add_parser("run")
    run_p.add_argument("--server", required=True)
    search_p = sub.add_parser("search", help="Rank reviewed and bundled MCPs for a task")
    search_p.add_argument("--query", required=True)
    search_p.add_argument("--capability")
    search_p.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.command == "list":
        if (ROOT / ".agents" / "registries" / "mcps.json").exists():
            sys.path.insert(0, str(ROOT / "python"))
            from sap_router_core.registry import load_servers, resolve_servers_for_capability
            servers = resolve_servers_for_capability(args.capability) if args.capability else list(load_servers().values())
            result = [{"id": s["id"], "status": s["status"], "readiness": "probe-required", "capabilities": s["capabilities"], "owner": s.get("owner")} for s in servers]
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                for item in result:
                    print(f"{item['id']}: {item['status']}")
            return 0 if result else 1
        result = list_capability(args.capability)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for cap, info in result.items():
                print(f"{cap}: {info['selected'] or 'BLOCKED'}")
        return 0 if all(info["selected"] for info in result.values()) else 1
    if args.command == "probe":
        if (ROOT / ".agents" / "registries" / "mcps.json").exists():
            sys.path.insert(0, str(ROOT / "python"))
            from sap_router_core.registry import probe_server
            result = probe_server(args.server, execute=args.execute)
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "READY" else 1
        result = probe(args.server)
        print(json.dumps(result, indent=2))
        return 0 if result["ready"] else 1
    if args.command == "run":
        return run_server(args.server)
    if args.command == "search":
        sys.path.insert(0, str(ROOT / "scripts"))
        from source_catalog import search
        return search(args.query, "mcp", args.capability, args.limit)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
