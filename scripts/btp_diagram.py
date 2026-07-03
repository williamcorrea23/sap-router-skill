#!/usr/bin/env python3
"""
BTP Diagram Generator v4.2.0

Converts a BTP landscape JSON specification into Mermaid or PlantUML source.
Spec schema (see .claude/skills/btp-diagram-generator/SKILL.md):
  {
    "solution": str, "subaccount": str,
    "nodes": [{"id", "type", "name", ...}],
    "connections": [{"from", "to", "protocol", "binding"?, "destination"?}]
  }
Node types: application, ui, database, service, external.
"""

import os
import sys
import json
import argparse

__version__ = "4.2.0"


def _mermaid_node(node):
    nid = node["id"]
    label = node.get("name", nid)
    ntype = node.get("type", "application")
    if ntype == "database":
        return f"{nid}[({label})]"
    if ntype == "service":
        return f"{nid}{{{label}}}"
    if ntype == "external":
        return f"{nid}[({label})]"
    return f"{nid}[{label}]"


def to_mermaid(spec):
    solution = spec.get("solution", "BTP Solution")
    subaccount = spec.get("subaccount", "DEV")
    nodes = spec.get("nodes", [])
    connections = spec.get("connections", [])

    internal = [n for n in nodes if n.get("type") != "external"]
    external = [n for n in nodes if n.get("type") == "external"]

    lines = ["graph TD"]
    # Subgraph ID must differ from every node ID (Mermaid cycle-error rule).
    sub_id = "BTP_" + "".join(c for c in subaccount.upper() if c.isalnum())
    lines.append(f'  subgraph {sub_id}["SAP BTP - {subaccount} Subaccount ({solution})"]')
    for node in internal:
        lines.append(f"    {_mermaid_node(node)}")
    lines.append("  end")
    for node in external:
        lines.append(f"  {_mermaid_node(node)}")
    for conn in connections:
        label = conn.get("protocol", "")
        if conn.get("destination"):
            label = f"{label} via {conn['destination']}" if label else conn["destination"]
        arrow = f"-->|{label}|" if label else "-->"
        lines.append(f"  {conn['from']} {arrow} {conn['to']}")
    return "\n".join(lines) + "\n"


def to_plantuml(spec):
    solution = spec.get("solution", "BTP Solution")
    subaccount = spec.get("subaccount", "DEV")
    nodes = spec.get("nodes", [])
    connections = spec.get("connections", [])

    lines = ["@startuml", "!include <C4/C4_Container>"]
    lines.append(f'System_Boundary(btp, "SAP BTP - {subaccount} ({solution})") {{')
    for node in nodes:
        if node.get("type") == "external":
            continue
        nid = node["id"]
        label = node.get("name", nid)
        tech = node.get("runtime") or node.get("service") or node.get("type", "")
        if node.get("type") == "database":
            lines.append(f'  ContainerDb({nid}, "{label}", "{tech}")')
        else:
            lines.append(f'  Container({nid}, "{label}", "{tech}")')
    lines.append("}")
    for node in nodes:
        if node.get("type") != "external":
            continue
        nid = node["id"]
        label = node.get("name", nid)
        system = node.get("system", "External")
        lines.append(f'System_Ext({nid}, "{label}", "{system}")')
    for conn in connections:
        label = conn.get("protocol", "uses")
        detail = conn.get("destination", "")
        if detail:
            lines.append(f'Rel({conn["from"]}, {conn["to"]}, "{label}", "{detail}")')
        else:
            lines.append(f'Rel({conn["from"]}, {conn["to"]}, "{label}")')
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="BTP Diagram Generator v4.2.0")
    parser.add_argument("--input", required=True, help="Landscape spec JSON file")
    parser.add_argument("--format", choices=["mermaid", "plantuml"], default="mermaid",
                        help="Output format (default: mermaid)")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"[ERROR] Spec file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"[ERROR] Invalid JSON in {args.input}: {exc}", file=sys.stderr)
        sys.exit(1)

    missing = [key for key in ("nodes", "connections") if key not in spec]
    if missing:
        print(f"[ERROR] Spec missing required keys: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)
    node_ids = {n.get("id") for n in spec["nodes"]}
    for conn in spec["connections"]:
        for endpoint in (conn.get("from"), conn.get("to")):
            if endpoint not in node_ids:
                print(f"[ERROR] Connection references unknown node id: {endpoint}",
                      file=sys.stderr)
                sys.exit(1)

    output = to_mermaid(spec) if args.format == "mermaid" else to_plantuml(spec)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"[OK] {args.format} diagram written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
