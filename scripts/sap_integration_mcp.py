#!/usr/bin/env python3
"""Dependency-light stdio MCP bridge for SAP CPI and APIM workflows."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CHARACTER_LIMIT = 25_000
OUTPUT_SCHEMA = {"type": "object", "additionalProperties": True}


def run_cli(args: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": 124, "result": {"status": "ERROR", "error": "Operation timed out after 120 seconds"}}
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    raw = stdout or stderr
    try:
        payload: Any = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        payload = {"status": "OK" if result.returncode == 0 else "ERROR", "output": raw[:CHARACTER_LIMIT]}
    if not isinstance(payload, dict):
        payload = {"value": payload}
    if stderr and result.returncode != 0 and "error" not in payload:
        payload["error"] = stderr[:4000]
    return {"ok": result.returncode == 0, "exit_code": result.returncode, "result": payload}


def tool_result(value: Any, *, is_error: bool | None = None) -> dict[str, Any]:
    if isinstance(value, dict) and {"ok", "result"}.issubset(value):
        payload = value.get("result") or {}
        failed = not bool(value.get("ok"))
        if isinstance(payload, dict):
            payload.setdefault("exit_code", value.get("exit_code"))
    else:
        payload = value if isinstance(value, dict) else {"value": value}
        failed = False
    failed = failed if is_error is None else is_error
    text = json.dumps(payload, indent=2, default=str)
    if len(text) > CHARACTER_LIMIT:
        text = text[:CHARACTER_LIMIT] + "\n... response text truncated; inspect structuredContent with narrower filters."
    result = {"content": [{"type": "text", "text": text}], "structuredContent": payload}
    if failed:
        result["isError"] = True
    return result


def tool_error(exc: Exception) -> dict[str, Any]:
    return tool_result(
        {"status": "ERROR", "error": str(exc), "error_type": type(exc).__name__, "next_step": "Check tool arguments, configured environment references, and adapter status."},
        is_error=True,
    )


def response(message_id: Any, result: Any) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": message_id, "result": result}) + "\n")
    sys.stdout.flush()


def protocol_error(message_id: Any, code: int, message: str) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()


def string_prop(description: str, *, enum: list[str] | None = None, default: str | None = None) -> dict[str, Any]:
    prop: dict[str, Any] = {"type": "string", "description": description}
    if enum:
        prop["enum"] = enum
    if default is not None:
        prop["default"] = default
    return prop


def integer_prop(description: str, default: int = 50, minimum: int = 1, maximum: int = 200) -> dict[str, Any]:
    return {"type": "integer", "description": description, "default": default, "minimum": minimum, "maximum": maximum}


def annotations(title: str, *, read_only: bool, destructive: bool = False, idempotent: bool = False, open_world: bool = True) -> dict[str, Any]:
    return {
        "title": title,
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": open_world,
    }


def tool(name: str, title: str, description: str, properties: dict[str, Any] | None = None, required: list[str] | None = None, *, read_only: bool, destructive: bool = False, idempotent: bool = False, open_world: bool = True) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "object", "properties": properties or {}, "additionalProperties": False}
    if required:
        schema["required"] = required
    return {
        "name": name,
        "title": title,
        "description": description,
        "inputSchema": schema,
        "outputSchema": OUTPUT_SCHEMA,
        "annotations": annotations(title, read_only=read_only, destructive=destructive, idempotent=idempotent, open_world=open_world),
    }


def pagination_props() -> dict[str, Any]:
    return {
        "limit": integer_prop("Maximum records to return (1-200)."),
        "offset": {"type": "integer", "description": "Records to skip.", "default": 0, "minimum": 0},
    }


def approval_props() -> dict[str, Any]:
    return {
        "action_id": string_prop("One-time approval broker action id."),
        "plan_hash": string_prop("Immutable approval plan hash."),
        "argument_hash": string_prop("Hash of approved arguments."),
        "precondition_hash": string_prop("Hash of approved preconditions."),
    }


def cpi_tools() -> list[dict[str, Any]]:
    artifact_types = ["integration_flow", "value_mapping", "message_mapping", "script_collection"]
    deploy = {
        "artifact_id": string_prop("Integration flow artifact id."),
        "version": string_prop("Design-time version.", default="active"),
        "zip": string_prop("Optional ZIP path inside CPI_TOOL_WORKSPACE."),
        "strategy": string_prop("Upload method strategy.", enum=["auto", "put", "post-override"], default="auto"),
        "runtime_deploy": {"type": "boolean", "default": True},
    }
    generate = {
        "name": string_prop("Bundle-SymbolicName for the generated iFlow."),
        "output": string_prop("Output ZIP path inside CPI_TOOL_WORKSPACE."),
        "overwrite": {"type": "boolean", "default": False},
    }
    plot = {
        "input": string_prop("Input iFlow ZIP path inside CPI_TOOL_WORKSPACE."),
        "output": string_prop("Output diagram path inside CPI_TOOL_WORKSPACE."),
        "format": string_prop("Diagram format.", enum=["html", "svg", "png"], default="html"),
        "overwrite": {"type": "boolean", "default": False},
    }
    sync = {
        "workspace": string_prop("Repository directory inside CPI_TOOL_WORKSPACE."),
        "direction": string_prop("Synchronization direction.", enum=["pull", "push", "export", "import"]),
    }
    tools = [
        tool("cpi_test_connection", "Test CPI Connection", "Validate CPI OAuth client-credentials and the Integration Content API. No secrets are returned.", read_only=True, idempotent=True),
        tool("cpi_packages", "List CPI Packages", "List or retrieve integration packages with bounded pagination. Returns items/count/has_more/next_offset.", {"id": string_prop("Optional exact package id."), "query": string_prop("Optional Id/Name substring filter."), **pagination_props()}, read_only=True, idempotent=True),
        tool("cpi_artifacts", "List CPI Artifacts", "List design-time integration flows, value mappings, message mappings, or script collections.", {"package_id": string_prop("Optional package id filter."), "query": string_prop("Optional Id/Name substring filter."), "artifact_type": string_prop("Artifact category.", enum=artifact_types, default="integration_flow"), "runtime": {"type": "boolean", "default": False}, **pagination_props()}, read_only=True, idempotent=True),
        tool("cpi_artifact_get", "Get CPI Artifact", "Retrieve one CPI design-time artifact by id, version, and type.", {"artifact_id": string_prop("Artifact id."), "version": string_prop("Artifact version.", default="active"), "artifact_type": string_prop("Artifact category.", enum=artifact_types, default="integration_flow")}, ["artifact_id"], read_only=True, idempotent=True),
        tool("cpi_runtime_artifacts", "List CPI Runtime Artifacts", "List deployed runtime artifacts with status/query filters and bounded pagination.", {"status": string_prop("Optional runtime status."), "query": string_prop("Optional Id/Name substring filter."), **pagination_props()}, read_only=True, idempotent=True),
        tool("cpi_logs", "List CPI Message Logs", "Read Message Processing Logs with flow, status, level and time filters.", {"status": string_prop("Optional MPL status."), "integration_flow_id": string_prop("Optional integration flow name."), "log_level": string_prop("Optional log level."), "from_time": string_prop("Optional ISO timestamp lower bound."), "to_time": string_prop("Optional ISO timestamp upper bound."), "top": integer_prop("Compatibility alias for limit.", default=50), **pagination_props()}, read_only=True, idempotent=True),
        tool("cpi_message_details", "Get CPI Message Details", "Retrieve one MPL and optional adapter attributes, custom headers, and trace navigation data.", {"message_guid": string_prop("MessageGuid from an MPL record."), "include_adapter_attributes": {"type": "boolean", "default": False}, "include_custom_headers": {"type": "boolean", "default": False}, "include_trace": {"type": "boolean", "default": False}}, ["message_guid"], read_only=True, idempotent=True),
        tool("cpi_quality_check", "Check CPI iFlow Quality", "Run built-in structural validation and optionally configured cpilint. No tool is installed automatically.", {"input": string_prop("iFlow ZIP inside CPI_TOOL_WORKSPACE."), "engine": string_prop("Quality engine.", enum=["auto", "structural", "cpilint"], default="auto")}, ["input"], read_only=True, idempotent=True, open_world=False),
        tool("cpi_external_tools_status", "Get CPI Adapter Status", "Report configuration and executable availability for cpilint, sync, Steampipe, plotter, and mapping-test adapters.", read_only=True, idempotent=True, open_world=False),
        tool("cpi_steampipe_query", "Query CPI with Steampipe", "Execute one allowlisted read-only SELECT through the configured CPI Steampipe adapter.", {"query": string_prop("Single SELECT statement; semicolons and mutating keywords are rejected.")}, ["query"], read_only=True, idempotent=True),
        tool("cpi_mapping_test", "Test CPI Mapping", "Run an optional external mapping-test adapter against workspace-confined files.", {"mapping": string_prop("Mapping file path."), "input": string_prop("Input payload path."), "expected": string_prop("Optional expected payload path.")}, ["mapping", "input"], read_only=True, idempotent=True, open_world=False),
        tool("cpi_deploy_plan", "Plan CPI Deploy", "Create an immutable one-time approval plan for upload/deploy. Does not mutate tenant.", deploy, ["artifact_id"], read_only=True, idempotent=False, open_world=False),
        tool("cpi_deploy_commit", "Commit CPI Deploy", "Consume an independently approved action and execute upload/deploy once.", {**deploy, **approval_props()}, ["artifact_id", "action_id", "plan_hash"], read_only=False, destructive=False, idempotent=False, open_world=False),
        tool("cpi_undeploy_plan", "Plan CPI Undeploy", "Create a destructive approval plan for runtime undeploy. Does not mutate tenant.", {"artifact_id": string_prop("Runtime artifact id.")}, ["artifact_id"], read_only=True, idempotent=False, open_world=False),
        tool("cpi_undeploy_commit", "Commit CPI Undeploy", "Consume a strongly confirmed approval and undeploy a runtime artifact once.", {"artifact_id": string_prop("Runtime artifact id."), **approval_props()}, ["artifact_id", "action_id", "plan_hash"], read_only=False, destructive=True, idempotent=False, open_world=False),
        tool("cpi_generate_iflow_plan", "Plan CPI iFlow Generation", "Create approval plan for writing a local starter iFlow ZIP.", generate, ["name", "output"], read_only=True, open_world=False),
        tool("cpi_generate_iflow_commit", "Commit CPI iFlow Generation", "Consume approval and write the local starter iFlow ZIP.", {**generate, **approval_props()}, ["name", "output", "action_id", "plan_hash"], read_only=False, destructive=True, open_world=False),
        tool("cpi_plot_iflow_plan", "Plan CPI iFlow Plot", "Create approval plan for writing an iFlow diagram with the configured plotter.", plot, ["input", "output"], read_only=True, open_world=False),
        tool("cpi_plot_iflow_commit", "Commit CPI iFlow Plot", "Consume approval and run the configured plotter without a shell.", {**plot, **approval_props()}, ["input", "output", "action_id", "plan_hash"], read_only=False, destructive=True, open_world=False),
        tool("cpi_sync_plan", "Plan CPI Git Sync", "Create approval plan for optional external CPI/Git synchronization.", sync, ["workspace", "direction"], read_only=True, open_world=False),
        tool("cpi_sync_commit", "Commit CPI Git Sync", "Consume approval and invoke the configured sync adapter once.", {**sync, **approval_props()}, ["workspace", "direction", "action_id", "plan_hash"], read_only=False, destructive=False, open_world=False),
    ]
    return tools


def apim_tools() -> list[dict[str, Any]]:
    plan_props = {
        "bundle": string_prop("Bundle/file path to send."),
        "target": string_prop("Target name.", default="default"),
        "path": string_prop("Optional relative APIM path."),
        "method": string_prop("HTTP method.", enum=["PUT", "POST", "PATCH", "DELETE"], default="PUT"),
        "strategy": string_prop("Mutation strategy.", enum=["auto", "direct", "post-override"], default="auto"),
        "content_type": string_prop("Optional content type."),
    }
    return [
        tool("apim_health", "Test APIM Connection", "Validate SAP API Management connectivity.", read_only=True, idempotent=True),
        tool("apim_proxies", "List APIM Proxies", "List or export API proxies.", {"id": string_prop("Optional proxy id.")}, read_only=True, idempotent=True),
        tool("apim_policy_validate", "Validate APIM Policy", "Validate a local APIM policy XML file.", {"file": string_prop("Policy XML path.")}, ["file"], read_only=True, idempotent=True, open_world=False),
        tool("apim_deploy_plan", "Plan APIM Deploy", "Create an approval plan for APIM mutation.", plan_props, ["bundle"], read_only=True, open_world=False),
        tool("apim_deploy_execute", "Commit APIM Deploy", "Consume approval and execute APIM mutation.", {"plan_id": string_prop("APIM local plan id."), **approval_props(), "confirm": {"type": "boolean", "default": False}}, ["plan_id", "action_id", "plan_hash", "confirm"], read_only=False, destructive=True, open_world=False),
    ]


def tools(product: str) -> list[dict[str, Any]]:
    return cpi_tools() if product == "cpi" else apim_tools()


def append_option(call: list[str], args: dict[str, Any], key: str, flag: str) -> None:
    value = args.get(key)
    if value not in (None, ""):
        call.extend([flag, str(value)])


def append_bool(call: list[str], args: dict[str, Any], key: str, flag: str, default: bool = False) -> None:
    if bool(args.get(key, default)):
        call.append(flag)


def append_approval(call: list[str], args: dict[str, Any]) -> None:
    for key, flag in (("action_id", "--action-id"), ("plan_hash", "--plan-hash"), ("argument_hash", "--argument-hash"), ("precondition_hash", "--precondition-hash")):
        append_option(call, args, key, flag)


def call_cpi(name: str, args: dict[str, Any]) -> dict[str, Any]:
    cmd = ["scripts/cpi_client.py"]
    if name == "cpi_test_connection":
        return run_cli(cmd + ["test-connection"])
    if name == "cpi_packages":
        call = cmd + ["packages"]
        for key, flag in (("id", "--id"), ("query", "--query"), ("limit", "--limit"), ("offset", "--offset")):
            append_option(call, args, key, flag)
        return run_cli(call)
    if name == "cpi_artifacts":
        call = cmd + ["artifacts"]
        for key, flag in (("package_id", "--package-id"), ("query", "--query"), ("artifact_type", "--artifact-type"), ("limit", "--limit"), ("offset", "--offset")):
            append_option(call, args, key, flag)
        append_bool(call, args, "runtime", "--runtime")
        return run_cli(call)
    if name == "cpi_artifact_get":
        call = cmd + ["artifact", "--id", str(args["artifact_id"])]
        append_option(call, args, "version", "--version")
        append_option(call, args, "artifact_type", "--artifact-type")
        return run_cli(call)
    if name == "cpi_runtime_artifacts":
        call = cmd + ["runtime"]
        for key, flag in (("status", "--status"), ("query", "--query"), ("limit", "--limit"), ("offset", "--offset")):
            append_option(call, args, key, flag)
        return run_cli(call)
    if name == "cpi_logs":
        call = cmd + ["logs"]
        for key, flag in (("status", "--status"), ("integration_flow_id", "--integration-flow-id"), ("log_level", "--log-level"), ("from_time", "--from-time"), ("to_time", "--to-time"), ("top", "--top"), ("limit", "--limit"), ("offset", "--offset")):
            append_option(call, args, key, flag)
        return run_cli(call)
    if name == "cpi_message_details":
        call = cmd + ["message", "--guid", str(args["message_guid"])]
        for key, flag in (("include_adapter_attributes", "--include-adapter-attributes"), ("include_custom_headers", "--include-custom-headers"), ("include_trace", "--include-trace")):
            append_bool(call, args, key, flag)
        return run_cli(call)
    if name == "cpi_quality_check":
        call = cmd + ["quality", "--input", str(args["input"])]
        append_option(call, args, "engine", "--engine")
        return run_cli(call)
    if name == "cpi_external_tools_status":
        return run_cli(cmd + ["tools-status"])
    if name == "cpi_steampipe_query":
        return run_cli(cmd + ["steampipe", "--query", str(args["query"])])
    if name == "cpi_mapping_test":
        call = cmd + ["mapping-test", "--mapping", str(args["mapping"]), "--input", str(args["input"])]
        append_option(call, args, "expected", "--expected")
        return run_cli(call)

    operation_map = {
        "cpi_deploy_plan": ("deploy", "plan"), "cpi_deploy_commit": ("deploy", "commit"),
        "cpi_undeploy_plan": ("undeploy", "plan"), "cpi_undeploy_commit": ("undeploy", "commit"),
        "cpi_generate_iflow_plan": ("generate", "plan"), "cpi_generate_iflow_commit": ("generate", "commit"),
        "cpi_plot_iflow_plan": ("plot", "plan"), "cpi_plot_iflow_commit": ("plot", "commit"),
        "cpi_sync_plan": ("sync", "plan"), "cpi_sync_commit": ("sync", "commit"),
    }
    if name not in operation_map:
        raise ValueError(f"Unknown CPI tool: {name}")
    operation, action = operation_map[name]
    call = cmd + [operation, action]
    option_sets = {
        "deploy": (("artifact_id", "--artifact-id"), ("version", "--version"), ("zip", "--zip"), ("strategy", "--strategy")),
        "undeploy": (("artifact_id", "--artifact-id"),),
        "generate": (("name", "--name"), ("output", "--output")),
        "plot": (("input", "--input"), ("output", "--output"), ("format", "--format")),
        "sync": (("workspace", "--workspace"), ("direction", "--direction")),
    }
    for key, flag in option_sets[operation]:
        append_option(call, args, key, flag)
    if operation == "deploy":
        append_bool(call, args, "runtime_deploy", "--runtime-deploy", default=True)
    if operation in {"generate", "plot"}:
        append_bool(call, args, "overwrite", "--overwrite")
    if action == "commit":
        append_approval(call, args)
    return run_cli(call)


def call_apim(name: str, args: dict[str, Any]) -> dict[str, Any]:
    cmd = ["scripts/apim_client.py"]
    if name == "apim_health":
        return run_cli(cmd + ["health"])
    if name == "apim_proxies":
        return run_cli(cmd + (["proxies", "export", "--id", str(args["id"])] if args.get("id") else ["proxies", "list"]))
    if name == "apim_policy_validate":
        return run_cli(cmd + ["policies", "validate", "--file", str(args["file"])])
    if name == "apim_deploy_plan":
        call = cmd + ["deploy", "plan", "--bundle", str(args["bundle"])]
        for key, flag in (("target", "--target"), ("path", "--path"), ("method", "--method"), ("strategy", "--strategy"), ("content_type", "--content-type")):
            append_option(call, args, key, flag)
        return run_cli(call)
    if name == "apim_deploy_execute":
        call = cmd + ["deploy", "execute", "--plan-id", str(args["plan_id"])]
        append_approval(call, args)
        append_bool(call, args, "confirm", "--confirm")
        return run_cli(call)
    raise ValueError(f"Unknown APIM tool: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SAP Integration MCP stdio bridge")
    parser.add_argument("--product", choices=["cpi", "apim"], required=True)
    product = parser.parse_args().product
    for raw in sys.stdin:
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        message_id = message.get("id")
        method = message.get("method")
        if method == "initialize":
            response(message_id, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": f"sap-{product}-mcp", "version": "0.3.0"}})
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            response(message_id, {"tools": tools(product)})
        elif method == "tools/call":
            try:
                params = message.get("params", {}) or {}
                name = str(params.get("name", ""))
                arguments = params.get("arguments", {}) or {}
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments must be an object")
                value = call_cpi(name, arguments) if product == "cpi" else call_apim(name, arguments)
                response(message_id, tool_result(value))
            except Exception as exc:
                response(message_id, tool_error(exc))
        else:
            protocol_error(message_id, -32601, f"Unsupported method: {method}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
