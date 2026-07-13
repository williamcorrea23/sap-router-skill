#!/usr/bin/env python3
"""Minimal stdio MCP bridge for SAP CPI/APIM helpers."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def run_cli(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    text = result.stdout.strip()
    try:
        payload: Any = json.loads(text) if text else {"stdout": text}
    except json.JSONDecodeError:
        payload = {"stdout": text}
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "result": payload,
        "stderr": result.stderr.strip()[:4000],
    }


def tool_result(value: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, indent=2)}]}


def response(message_id: Any, result: Any) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": message_id, "result": result}) + "\n")
    sys.stdout.flush()


def error(message_id: Any, code: int, message: str) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()


def string_prop(description: str) -> dict[str, str]:
    return {"type": "string", "description": description}


def cpi_tools() -> list[dict[str, Any]]:
    return [
        {"name": "cpi_test_connection", "description": "Validate CPI OAuth and API connectivity.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "cpi_packages", "description": "List or read CPI integration packages.", "inputSchema": {"type": "object", "properties": {"id": string_prop("Optional package id.")}}},
        {"name": "cpi_artifacts", "description": "List CPI design-time or runtime artifacts.", "inputSchema": {"type": "object", "properties": {"package_id": string_prop("Optional package id filter."), "runtime": {"type": "boolean"}}}},
        {"name": "cpi_logs", "description": "Read CPI message processing logs.", "inputSchema": {"type": "object", "properties": {"top": {"type": "integer", "default": 10}}}},
        {
            "name": "cpi_deploy_plan",
            "description": "Create approval plan for CPI upload/deploy. Does not mutate tenant.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "artifact_id": string_prop("Integration flow artifact id."),
                    "version": {"type": "string", "default": "active"},
                    "zip": string_prop("Optional iFlow ZIP path to upload."),
                    "strategy": {"type": "string", "enum": ["auto", "put", "post-override"], "default": "auto"},
                    "runtime_deploy": {"type": "boolean", "default": True},
                },
                "required": ["artifact_id"],
            },
        },
        {
            "name": "cpi_deploy_commit",
            "description": "Consume approval and execute CPI upload/deploy.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "artifact_id": string_prop("Integration flow artifact id."),
                    "version": {"type": "string", "default": "active"},
                    "zip": string_prop("Optional iFlow ZIP path to upload."),
                    "strategy": {"type": "string", "enum": ["auto", "put", "post-override"], "default": "auto"},
                    "runtime_deploy": {"type": "boolean", "default": True},
                    "action_id": string_prop("Approval broker action id."),
                    "plan_hash": string_prop("Approval broker plan hash."),
                    "argument_hash": string_prop("Approval broker argument hash."),
                    "precondition_hash": string_prop("Approval broker precondition hash."),
                },
                "required": ["artifact_id", "action_id", "plan_hash"],
            },
        },
    ]


def apim_tools() -> list[dict[str, Any]]:
    return [
        {"name": "apim_health", "description": "Validate SAP API Management API connectivity.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "apim_proxies", "description": "List or export APIM API proxies.", "inputSchema": {"type": "object", "properties": {"id": string_prop("Optional proxy id for export.")}}},
        {"name": "apim_policy_validate", "description": "Validate local APIM policy XML file.", "inputSchema": {"type": "object", "properties": {"file": string_prop("Policy XML path.")}, "required": ["file"]}},
        {
            "name": "apim_deploy_plan",
            "description": "Create approval plan for APIM proxy/policy mutation. Does not mutate tenant.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "bundle": string_prop("Bundle/file path to send."),
                    "target": {"type": "string", "default": "default"},
                    "path": string_prop("Optional relative APIM API path."),
                    "method": {"type": "string", "enum": ["PUT", "POST", "PATCH", "DELETE"], "default": "PUT"},
                    "strategy": {"type": "string", "enum": ["auto", "direct", "post-override"], "default": "auto"},
                    "content_type": string_prop("Optional content type."),
                },
                "required": ["bundle"],
            },
        },
        {
            "name": "apim_deploy_execute",
            "description": "Consume approval and execute APIM mutation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "plan_id": string_prop("APIM local plan id."),
                    "action_id": string_prop("Approval broker action id."),
                    "plan_hash": string_prop("Approval broker plan hash."),
                    "argument_hash": string_prop("Approval broker argument hash."),
                    "precondition_hash": string_prop("Approval broker precondition hash."),
                    "confirm": {"type": "boolean", "default": False},
                },
                "required": ["plan_id", "action_id", "plan_hash", "confirm"],
            },
        },
    ]


def tools(product: str) -> list[dict[str, Any]]:
    return cpi_tools() if product == "cpi" else apim_tools()


def call_cpi(name: str, args: dict[str, Any]) -> dict[str, Any]:
    cmd = ["scripts/cpi_client.py"]
    if name == "cpi_test_connection":
        return run_cli(cmd + ["test-connection"])
    if name == "cpi_packages":
        call = cmd + ["packages"]
        if args.get("id"):
            call += ["--id", str(args["id"])]
        return run_cli(call)
    if name == "cpi_artifacts":
        call = cmd + ["artifacts"]
        if args.get("package_id"):
            call += ["--package-id", str(args["package_id"])]
        if args.get("runtime"):
            call.append("--runtime")
        return run_cli(call)
    if name == "cpi_logs":
        return run_cli(cmd + ["logs", "--top", str(args.get("top", 10))])
    if name in {"cpi_deploy_plan", "cpi_deploy_commit"}:
        action = "plan" if name.endswith("_plan") else "commit"
        call = cmd + ["deploy", action, "--artifact-id", str(args["artifact_id"]), "--version", str(args.get("version", "active")), "--strategy", str(args.get("strategy", "auto"))]
        if args.get("zip"):
            call += ["--zip", str(args["zip"])]
        if args.get("runtime_deploy", True):
            call.append("--runtime-deploy")
        if action == "commit":
            call += ["--action-id", str(args["action_id"]), "--plan-hash", str(args["plan_hash"])]
            if args.get("argument_hash"):
                call += ["--argument-hash", str(args["argument_hash"])]
            if args.get("precondition_hash"):
                call += ["--precondition-hash", str(args["precondition_hash"])]
        return run_cli(call)
    raise ValueError(f"Unknown CPI tool: {name}")


def call_apim(name: str, args: dict[str, Any]) -> dict[str, Any]:
    cmd = ["scripts/apim_client.py"]
    if name == "apim_health":
        return run_cli(cmd + ["health"])
    if name == "apim_proxies":
        if args.get("id"):
            return run_cli(cmd + ["proxies", "export", "--id", str(args["id"])])
        return run_cli(cmd + ["proxies", "list"])
    if name == "apim_policy_validate":
        return run_cli(cmd + ["policies", "validate", "--file", str(args["file"])])
    if name == "apim_deploy_plan":
        call = cmd + ["deploy", "plan", "--bundle", str(args["bundle"]), "--target", str(args.get("target", "default")), "--method", str(args.get("method", "PUT")), "--strategy", str(args.get("strategy", "auto"))]
        if args.get("path"):
            call += ["--path", str(args["path"])]
        if args.get("content_type"):
            call += ["--content-type", str(args["content_type"])]
        return run_cli(call)
    if name == "apim_deploy_execute":
        call = cmd + ["deploy", "execute", "--plan-id", str(args["plan_id"]), "--action-id", str(args["action_id"]), "--plan-hash", str(args["plan_hash"])]
        if args.get("argument_hash"):
            call += ["--argument-hash", str(args["argument_hash"])]
        if args.get("precondition_hash"):
            call += ["--precondition-hash", str(args["precondition_hash"])]
        if args.get("confirm"):
            call.append("--confirm")
        return run_cli(call)
    raise ValueError(f"Unknown APIM tool: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SAP Integration MCP stdio bridge.")
    parser.add_argument("--product", choices=["cpi", "apim"], required=True)
    args = parser.parse_args()
    product = args.product

    for raw in sys.stdin:
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        message_id = message.get("id")
        method = message.get("method")
        try:
            if method == "initialize":
                response(message_id, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": f"sap-{product}-mcp", "version": "0.2.0"}})
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                response(message_id, {"tools": tools(product)})
            elif method == "tools/call":
                name = message.get("params", {}).get("name", "")
                tool_args = message.get("params", {}).get("arguments", {}) or {}
                value = call_cpi(name, tool_args) if product == "cpi" else call_apim(name, tool_args)
                response(message_id, tool_result(value))
            else:
                error(message_id, -32601, f"Unsupported method: {method}")
        except Exception as exc:
            error(message_id, -32000, str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
