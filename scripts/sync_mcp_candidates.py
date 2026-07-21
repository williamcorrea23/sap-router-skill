#!/usr/bin/env python3
"""Preserve non-canonical .mcp.json servers as fail-closed fallback candidates."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_CONFIG = ROOT / ".mcp.json"
SERVERS = ROOT / ".agents" / "registries" / "mcps.json"
OUTPUT = ROOT / ".agents" / "registries" / "mcp-candidates.json"


def main() -> int:
    configured = json.loads(MCP_CONFIG.read_text(encoding="utf-8")).get("mcpServers", {})
    reviewed = {server["id"] for server in json.loads(SERVERS.read_text(encoding="utf-8")).get("servers", [])}
    candidates = []
    for server_id, spec in sorted(configured.items()):
        if server_id in reviewed:
            continue
        candidates.append({
            "id": server_id,
            "status": "disabled_candidate",
            "reason": "Retained fallback; promote only after runtime and safety review.",
            "runtime": {key: spec.get(key) for key in ("type", "command", "args") if key in spec},
            "env_refs": sorted({value[2:-1] for value in spec.get("env", {}).values()
                                if isinstance(value, str) and value.startswith("${") and value.endswith("}")}),
            "description": spec.get("description", ""),
        })
    OUTPUT.write_text(json.dumps({"schema_version": 1, "policy": "fail_closed", "candidates": candidates}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(candidates)} fallback MCP candidates to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
