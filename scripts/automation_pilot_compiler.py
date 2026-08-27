#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP Automation Pilot MCP Server Definition Generator & Compiler.
Adheres to the schema defined in automation-pilot-mcp-server-generation.

Generates and validates MCP server definition JSON files that expose
SAP Automation Pilot commands to AI assistants as MCP tools.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# Standard Automation Pilot Catalog Definitions
STANDARD_CATALOG_COMMANDS: dict[str, list[dict[str, Any]]] = {
    "cf": [
        {
            "name": "list_cf_orgs",
            "title": "List Cloud Foundry Orgs",
            "command": "ListCfOrgs",
            "version": "1",
            "readOnly": True,
            "idempotent": True,
            "openWorld": True,
            "destructive": False,
            "suffix": "-sapcp"
        },
        {
            "name": "restart_cf_app",
            "title": "Restart Cloud Foundry App",
            "command": "RestartCfApp",
            "version": "1",
            "readOnly": False,
            "idempotent": True,
            "openWorld": False,
            "destructive": False,
            "suffix": "-sapcp"
        },
        {
            "name": "scale_cf_app",
            "title": "Scale Cloud Foundry App",
            "command": "ScaleCfApp",
            "version": "1",
            "readOnly": False,
            "idempotent": True,
            "openWorld": False,
            "destructive": False,
            "suffix": "-sapcp"
        }
    ],
    "hanalm": [
        {
            "name": "get_hana_cloud_instance",
            "title": "Get HANA Cloud Instance Status",
            "command": "GetHanaCloudInstance",
            "version": "1",
            "readOnly": True,
            "idempotent": True,
            "openWorld": False,
            "destructive": False,
            "suffix": "-sapcp"
        },
        {
            "name": "restart_hana_cloud_instance",
            "title": "Restart HANA Cloud Instance",
            "command": "RestartHanaCloudInstance",
            "version": "1",
            "readOnly": False,
            "idempotent": True,
            "openWorld": False,
            "destructive": True,
            "suffix": "-sapcp"
        }
    ],
    "ctms": [
        {
            "name": "list_transport_nodes",
            "title": "List Cloud Transport Nodes",
            "command": "ListTransportNodes",
            "version": "1",
            "readOnly": True,
            "idempotent": True,
            "openWorld": True,
            "destructive": False,
            "suffix": "-sapcp"
        },
        {
            "name": "export_transport_request",
            "title": "Export Transport Request",
            "command": "ExportTransportRequest",
            "version": "1",
            "readOnly": False,
            "idempotent": False,
            "openWorld": False,
            "destructive": False,
            "suffix": "-sapcp"
        },
        {
            "name": "import_transport_request",
            "title": "Import Transport Request to Node",
            "command": "ImportTransportRequest",
            "version": "1",
            "readOnly": False,
            "idempotent": False,
            "openWorld": False,
            "destructive": True,
            "suffix": "-sapcp"
        }
    ],
    "calmhm": [
        {
            "name": "get_service_health",
            "title": "Get Cloud ALM Service Health",
            "command": "GetServiceHealth",
            "version": "1",
            "readOnly": True,
            "idempotent": True,
            "openWorld": True,
            "destructive": False,
            "suffix": "-sapcp"
        }
    ]
}


def validate_server_definition(data: dict[str, Any]) -> list[str]:
    """Validates an Automation Pilot MCP server definition against strict schema rules."""
    errors = []
    
    # Validate top-level
    name = data.get("name")
    if not name or not isinstance(name, str):
        errors.append("Top-level 'name' must be a non-empty string.")
    elif not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        errors.append(f"Server name '{name}' must be kebab-case (e.g., 'cf-app-management').")
        
    if "enabled" not in data or not isinstance(data["enabled"], bool):
        errors.append("Top-level 'enabled' must be a boolean.")
        
    if "instructions" not in data or not isinstance(data["instructions"], str):
        errors.append("Top-level 'instructions' must be a string description.")
        
    tools = data.get("mcpTools")
    if not isinstance(tools, list) or len(tools) == 0:
        errors.append("'mcpTools' must be a non-empty array of tool objects.")
        return errors
        
    # Validate each tool object
    tool_names = set()
    for idx, tool in enumerate(tools):
        tname = tool.get("name")
        if not tname or not isinstance(tname, str):
            errors.append(f"Tool [{idx}] 'name' is required.")
        elif not re.match(r"^[a-z0-9]+(_[a-z0-9]+)*$", tname):
            errors.append(f"Tool [{idx}] name '{tname}' must be snake_case.")
        elif tname in tool_names:
            errors.append(f"Duplicate tool name '{tname}'.")
        else:
            tool_names.add(tname)
            
        cid = tool.get("commandId")
        if not cid or not isinstance(cid, str):
            errors.append(f"Tool [{idx}] 'commandId' is required.")
        elif not re.match(r"^[a-zA-Z0-9_-]+:[a-zA-Z0-9_-]+:[0-9]+$", cid):
            errors.append(f"Tool [{idx}] commandId '{cid}' must match '<catalog>-<suffix>:<CommandName>:<version>'.")
            
        for hint in ("destructiveHint", "idempotentHint", "openWorldHint", "readOnlyHint"):
            if hint not in tool or not isinstance(tool[hint], bool):
                errors.append(f"Tool [{idx}] '{hint}' must be a boolean.")
                
        if tool.get("tags") != {}:
            errors.append(f"Tool [{idx}] 'tags' must be an empty object '{{}}'.")
            
        if not tool.get("title") or not isinstance(tool.get("title"), str):
            errors.append(f"Tool [{idx}] 'title' must be a Title Case string.")
            
    return errors


def build_mcp_server(
    name: str,
    instructions: str,
    catalog: str,
    tenant_id: str | None = None,
    custom_command: str | None = None,
    is_destructive: bool = False,
    is_read_only: bool = False
) -> dict[str, Any]:
    """Builds a compliant Automation Pilot MCP server dictionary."""
    suffix = f"-{tenant_id}" if tenant_id else "-sapcp"
    mcp_tools: list[dict[str, Any]] = []

    if custom_command:
        snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", custom_command).lower()
        title = re.sub(r"(?<!^)(?=[A-Z])", " ", custom_command).title()
        tool_obj = {
            "commandId": f"{catalog}{suffix}:{custom_command}:1",
            "name": snake_name,
            "enabled": True,
            "inputReferences": [f"{catalog}-<<<TENANT_ID>>>:Credentials:1"] if tenant_id else [],
            "tags": {},
            "title": title,
            "destructiveHint": is_destructive,
            "idempotentHint": is_read_only,
            "openWorldHint": is_read_only,
            "readOnlyHint": is_read_only
        }
        mcp_tools.append(tool_obj)
    elif catalog in STANDARD_CATALOG_COMMANDS:
        for cmd_def in STANDARD_CATALOG_COMMANDS[catalog]:
            cmd_suffix = suffix if tenant_id else cmd_def["suffix"]
            tool_obj = {
                "commandId": f"{catalog}{cmd_suffix}:{cmd_def['command']}:{cmd_def['version']}",
                "name": cmd_def["name"],
                "enabled": True,
                "inputReferences": [f"{catalog}-<<<TENANT_ID>>>:DefaultInputs:1"] if tenant_id else [],
                "tags": {},
                "title": cmd_def["title"],
                "destructiveHint": cmd_def["destructive"],
                "idempotentHint": cmd_def["idempotent"],
                "openWorldHint": cmd_def["openWorld"],
                "readOnlyHint": cmd_def["readOnly"]
            }
            mcp_tools.append(tool_obj)
    else:
        raise ValueError(f"Unknown catalog '{catalog}'. Supported standard catalogs: {list(STANDARD_CATALOG_COMMANDS.keys())}")

    server_def = {
        "name": name,
        "enabled": True,
        "instructions": instructions,
        "mcpTools": mcp_tools
    }

    errors = validate_server_definition(server_def)
    if errors:
        raise ValueError(f"Generated server definition is invalid: {'; '.join(errors)}")

    return server_def


def main() -> int:
    parser = argparse.ArgumentParser(description="SAP Automation Pilot MCP Server Compiler")
    parser.add_argument("--name", default="cf-app-management", help="Kebab-case MCP server name")
    parser.add_argument("--catalog", default="cf", help="Catalog prefix (cf, hanalm, ctms, calmhm)")
    parser.add_argument("--command", help="Optional specific command name (e.g. ListCfOrgs)")
    parser.add_argument("--tenant-id", help="Optional tenant ID placeholder")
    parser.add_argument("--instructions", default="SAP Automation Pilot operations bridge for landscape management.")
    parser.add_argument("--output", help="Output file path for generated JSON")
    parser.add_argument("--validate-file", help="Validate an existing definition file")
    parser.add_argument("--destructive", action="store_true", help="Set destructive hint")
    parser.add_argument("--read-only", action="store_true", help="Set read-only hint")

    args = parser.parse_args()

    if args.validate_file:
        path = Path(args.validate_file)
        if not path.exists():
            print(f"Error: file not found {path}")
            return 1
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_server_definition(data)
        if errors:
            print(f"FAILED validation ({len(errors)} errors):")
            for err in errors:
                print(f"  - {err}")
            return 1
        print(f"PASS: {path.name} conforms to Automation Pilot MCP schema.")
        return 0

    server_def = build_mcp_server(
        name=args.name,
        instructions=args.instructions,
        catalog=args.catalog,
        tenant_id=args.tenant_id,
        custom_command=args.command,
        is_destructive=args.destructive,
        is_read_only=args.read_only
    )

    content = json.dumps(server_def, indent=2) + "\n"
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"Wrote Automation Pilot MCP definition to: {out_path}")
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
