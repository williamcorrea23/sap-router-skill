#!/usr/bin/env python3
"""SAP Cloud Integration API client and fail-closed local tooling adapters.

Tenant mutations and persistent local writes use the approval broker's
plan/approve/commit contract. Optional community tools are executed only when
an explicit command is configured; this module never installs or downloads
them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shlex
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:  # pragma: no cover - exercised by CLI startup environments
    requests = None
    HAS_REQUESTS = False


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LIMIT = 50
MAX_LIMIT = 200
CHARACTER_LIMIT = 25_000
HTTP_TIMEOUT = 60
EXTERNAL_TIMEOUT = 120

EXTERNAL_TOOLS = {
    "cpilint": "CPILINT_CMD",
    "sync": "CPI_SYNC_CMD",
    "steampipe": "CPI_STEAMPIPE_CMD",
    "plotter": "CPI_IFLOW_PLOTTER_CMD",
    "mapping_test": "CPI_MAPPING_TEST_CMD",
}

ARTIFACT_ENTITY_SETS = {
    "integration_flow": "IntegrationDesigntimeArtifacts",
    "value_mapping": "ValueMappingDesigntimeArtifacts",
    "message_mapping": "MessageMappingDesigntimeArtifacts",
    "script_collection": "ScriptCollectionDesigntimeArtifacts",
}


def _load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def env_value(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def json_sha256(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def shell_quote(value: Any) -> str:
    text = str(value)
    if not text:
        return '""'
    if any(ch.isspace() for ch in text) or any(ch in text for ch in '"&|<>'):
        return '"' + text.replace('"', '\\"') + '"'
    return text


def odata_quote(value: Any) -> str:
    return str(value).replace("'", "''")


def require_requests() -> None:
    if not HAS_REQUESTS:
        raise RuntimeError("Missing dependency 'requests'. Install the project dependencies before using CPI HTTP operations.")


def bounded_limit(value: int | None) -> int:
    limit = DEFAULT_LIMIT if value is None else int(value)
    if limit < 1 or limit > MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}")
    return limit


def cpi_base_url() -> str:
    base_url = env_value("CPI_BASE_URL", "CPI_TENANT_URL")
    if not base_url:
        raise ValueError("Missing CPI_BASE_URL in environment")
    return base_url.rstrip("/")


def get_oauth_token() -> str:
    require_requests()
    url = env_value("CPI_OAUTH_TOKEN_URL", "CPI_TOKEN_URL")
    client_id = env_value("CPI_OAUTH_CLIENT_ID", "CPI_CLIENT_ID")
    client_secret = env_value("CPI_OAUTH_CLIENT_SECRET", "CPI_CLIENT_SECRET")
    if not url or not client_id or not client_secret:
        raise ValueError(
            "Missing CPI OAuth configuration: CPI_OAUTH_TOKEN_URL, "
            "CPI_OAUTH_CLIENT_ID and CPI_OAUTH_CLIENT_SECRET are required"
        )
    response = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise RuntimeError("OAuth response did not contain access_token")
    return str(token)


def cpi_session():
    require_requests()
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {get_oauth_token()}", "Accept": "application/json"})
    return session


def query_cpi_odata(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    session = cpi_session()
    response = session.get(f"{cpi_base_url()}{endpoint}", params=params, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    return response.json()


def _odata_items(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int | None]:
    data: Any = payload.get("d", payload)
    if isinstance(data, dict):
        raw_items = data.get("results", data.get("value"))
        total = data.get("__count", data.get("@odata.count", payload.get("@odata.count")))
        if raw_items is None and any(key in data for key in ("Id", "Name", "Status")):
            raw_items = [data]
        items = raw_items if isinstance(raw_items, list) else []
    elif isinstance(data, list):
        items, total = data, None
    else:
        items, total = [], None
    try:
        total_value = int(total) if total is not None else None
    except (TypeError, ValueError):
        total_value = None
    return [item for item in items if isinstance(item, dict)], total_value


def collection_result(
    payload: dict[str, Any], *, source: str, limit: int, offset: int
) -> dict[str, Any]:
    items, total = _odata_items(payload)
    has_more = (total > offset + len(items)) if total is not None else len(items) >= limit
    result: dict[str, Any] = {
        "items": items,
        "count": len(items),
        "total_count": total,
        "offset": offset,
        "limit": limit,
        "has_more": has_more,
        "next_offset": offset + len(items) if has_more else None,
        "source": source,
        "truncated": False,
    }
    while len(stable_json(result)) > CHARACTER_LIMIT and result["items"]:
        result["items"].pop()
        result["truncated"] = True
    result["count"] = len(result["items"])
    if result["truncated"]:
        result["has_more"] = True
        result["next_offset"] = offset + result["count"]
        result["truncation_message"] = "Response truncated. Continue with next_offset or add filters."
    return result


def list_collection(
    entity_set: str,
    *,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
    filters: list[str] | None = None,
    order_by: str | None = None,
) -> dict[str, Any]:
    limit = bounded_limit(limit)
    if offset < 0:
        raise ValueError("offset must be zero or greater")
    params: dict[str, Any] = {"$top": limit, "$skip": offset, "$inlinecount": "allpages"}
    if filters:
        params["$filter"] = " and ".join(f"({item})" for item in filters if item)
    if order_by:
        params["$orderby"] = order_by
    payload = query_cpi_odata(f"/api/v1/{entity_set}", params=params)
    return collection_result(payload, source=f"cpi:{entity_set}", limit=limit, offset=offset)


def list_packages(package_id: str = "", query: str = "", limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict[str, Any]:
    if package_id:
        payload = query_cpi_odata(f"/api/v1/IntegrationPackages('{odata_quote(package_id)}')")
        return collection_result(payload, source="cpi:IntegrationPackages", limit=1, offset=0)
    filters = []
    if query:
        value = odata_quote(query)
        filters.append(f"substringof('{value}',Id) or substringof('{value}',Name)")
    return list_collection("IntegrationPackages", limit=limit, offset=offset, filters=filters)


def list_artifacts(
    package_id: str = "",
    query: str = "",
    artifact_type: str = "integration_flow",
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    entity_set = ARTIFACT_ENTITY_SETS.get(artifact_type)
    if not entity_set:
        raise ValueError(f"Unsupported artifact_type: {artifact_type}")
    filters = []
    if package_id:
        filters.append(f"PackageId eq '{odata_quote(package_id)}'")
    if query:
        value = odata_quote(query)
        filters.append(f"substringof('{value}',Id) or substringof('{value}',Name)")
    return list_collection(entity_set, limit=limit, offset=offset, filters=filters)


def get_artifact(artifact_id: str, version: str = "active", artifact_type: str = "integration_flow") -> dict[str, Any]:
    entity_set = ARTIFACT_ENTITY_SETS.get(artifact_type)
    if not entity_set:
        raise ValueError(f"Unsupported artifact_type: {artifact_type}")
    endpoint = f"/api/v1/{entity_set}(Id='{odata_quote(artifact_id)}',Version='{odata_quote(version)}')"
    payload = query_cpi_odata(endpoint)
    items, _ = _odata_items(payload)
    item: Any = items[0] if items else payload.get("d", payload)
    return {"item": item, "source": f"cpi:{entity_set}", "truncated": False}


def list_runtime_artifacts(status: str = "", query: str = "", limit: int = DEFAULT_LIMIT, offset: int = 0) -> dict[str, Any]:
    filters = []
    if status:
        filters.append(f"Status eq '{odata_quote(status)}'")
    if query:
        value = odata_quote(query)
        filters.append(f"substringof('{value}',Id) or substringof('{value}',Name)")
    return list_collection("IntegrationRuntimeArtifacts", limit=limit, offset=offset, filters=filters)


def list_logs(
    status: str = "",
    integration_flow_id: str = "",
    log_level: str = "",
    from_time: str = "",
    to_time: str = "",
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    filters = []
    if status:
        filters.append(f"Status eq '{odata_quote(status)}'")
    if integration_flow_id:
        filters.append(f"IntegrationFlowName eq '{odata_quote(integration_flow_id)}'")
    if log_level:
        filters.append(f"LogLevel eq '{odata_quote(log_level)}'")
    if from_time:
        filters.append(f"LogStart ge datetime'{odata_quote(from_time)}'")
    if to_time:
        filters.append(f"LogStart le datetime'{odata_quote(to_time)}'")
    return list_collection(
        "MessageProcessingLogs", limit=limit, offset=offset, filters=filters, order_by="LogStart desc"
    )


def message_details(message_guid: str, include_adapter_attributes: bool = False, include_custom_headers: bool = False, include_trace: bool = False) -> dict[str, Any]:
    guid = odata_quote(message_guid)
    base = f"/api/v1/MessageProcessingLogs('{guid}')"
    payload = query_cpi_odata(base)
    result: dict[str, Any] = {"message": payload.get("d", payload), "source": "cpi:MessageProcessingLogs"}
    expansions = []
    if include_adapter_attributes:
        expansions.append(("adapter_attributes", "AdapterAttributes"))
    if include_custom_headers:
        expansions.append(("custom_headers", "CustomHeaderProperties"))
    if include_trace:
        expansions.append(("trace", "TraceMessages"))
    warnings = []
    for key, navigation in expansions:
        try:
            nav_payload = query_cpi_odata(f"{base}/{navigation}")
            result[key], _ = _odata_items(nav_payload)
        except Exception as exc:  # optional navigation differs by tenant/API level
            warnings.append(f"{navigation} unavailable: {type(exc).__name__}")
    if warnings:
        result["warnings"] = warnings
    return result


def fetch_csrf(session: Any, endpoint: str = "/api/v1/") -> str:
    response = session.get(
        f"{cpi_base_url()}{endpoint}", headers={"X-CSRF-Token": "Fetch"}, timeout=HTTP_TIMEOUT
    )
    response.raise_for_status()
    token = response.headers.get("X-CSRF-Token") or response.headers.get("x-csrf-token")
    if not token:
        raise RuntimeError("CPI did not return an X-CSRF-Token")
    session.headers.update({"X-CSRF-Token": token})
    return str(token)


def cpi_mutating_request(session: Any, method: str, endpoint: str, body: bytes = b"", headers: dict[str, str] | None = None):
    fetch_csrf(session)
    return session.request(
        method,
        f"{cpi_base_url()}{endpoint}",
        data=body,
        headers=headers or {},
        timeout=HTTP_TIMEOUT,
    )


def design_artifact_path(artifact_id: str, version: str) -> str:
    return f"/api/v1/IntegrationDesigntimeArtifacts(Id='{odata_quote(artifact_id)}',Version='{odata_quote(version)}')"


def read_binary(path: str) -> bytes:
    candidate = safe_workspace_path(path, must_exist=True)
    if not candidate.is_file():
        raise ValueError(f"File not found: {path}")
    return candidate.read_bytes()


def method_is_blocked(response: Any) -> bool:
    text = response.text[:500].lower()
    return response.status_code in {403, 405, 501} and any(
        token in text for token in ("method", "put", "not allowed", "not implemented", "forbidden")
    )


def upload_iflow_zip(artifact_id: str, version: str, zip_file: str, strategy: str = "auto") -> dict[str, Any]:
    session = cpi_session()
    body = read_binary(zip_file)
    content_type = mimetypes.guess_type(zip_file)[0] or "application/zip"
    endpoint = design_artifact_path(artifact_id, version) + "/$value"
    headers = {"Content-Type": content_type, "Accept": "application/json"}
    attempts = []

    def attempt(name: str, method: str, extra_headers: dict[str, str] | None = None):
        request_headers = dict(headers)
        request_headers.update(extra_headers or {})
        response = cpi_mutating_request(session, method, endpoint, body=body, headers=request_headers)
        attempts.append({"strategy": name, "method": method, "http_status": response.status_code, "ok": response.ok})
        return response

    if strategy in {"auto", "put"}:
        response = attempt("put", "PUT")
        if response.ok:
            return {"status": "OK", "operation": "upload", "strategy": "put", "attempts": attempts}
        if strategy == "put" or not method_is_blocked(response):
            response.raise_for_status()
    response = attempt("post-override", "POST", {"X-HTTP-Method-Override": "PUT"})
    response.raise_for_status()
    return {"status": "OK", "operation": "upload", "strategy": "post-override", "attempts": attempts}


def deploy_runtime_artifact(artifact_id: str, version: str) -> dict[str, Any]:
    params = urllib.parse.urlencode({"Id": f"'{artifact_id}'", "Version": f"'{version}'"}, safe="'")
    response = cpi_mutating_request(
        cpi_session(), "POST", f"/api/v1/DeployIntegrationDesigntimeArtifact?{params}",
        headers={"Content-Type": "application/octet-stream"},
    )
    response.raise_for_status()
    return {"status": "OK", "operation": "deploy-runtime", "http_status": response.status_code}


def undeploy_runtime_artifact(artifact_id: str) -> dict[str, Any]:
    endpoint = f"/api/v1/IntegrationRuntimeArtifacts('{odata_quote(artifact_id)}')"
    response = cpi_mutating_request(cpi_session(), "DELETE", endpoint)
    response.raise_for_status()
    return {"status": "OK", "operation": "undeploy-runtime", "artifact_id": artifact_id, "http_status": response.status_code}


def workspace_root() -> Path:
    return Path(env_value("CPI_TOOL_WORKSPACE") or ROOT).expanduser().resolve()


def safe_workspace_path(value: str, *, must_exist: bool = False) -> Path:
    if not value:
        raise ValueError("A workspace-relative path is required")
    root = workspace_root()
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path is outside CPI_TOOL_WORKSPACE: {value}") from exc
    if must_exist and not candidate.exists():
        raise ValueError(f"Path does not exist: {value}")
    return candidate


def command_parts(tool: str) -> list[str]:
    env_name = EXTERNAL_TOOLS[tool]
    configured = env_value(env_name)
    if not configured:
        return []
    parts = shlex.split(configured, posix=os.name != "nt")
    parts = [part[1:-1] if len(part) >= 2 and part[0] == part[-1] == '"' else part for part in parts]
    if not parts:
        return []
    executable = shutil.which(parts[0])
    if not executable and Path(parts[0]).expanduser().is_file():
        executable = str(Path(parts[0]).expanduser().resolve())
    if not executable:
        return []
    return [executable, *parts[1:]]


def external_tools_status() -> dict[str, Any]:
    items = []
    for tool, env_name in EXTERNAL_TOOLS.items():
        configured = bool(env_value(env_name))
        resolved = command_parts(tool)
        items.append({
            "id": tool,
            "env": env_name,
            "configured": configured,
            "available": bool(resolved),
            "executable": Path(resolved[0]).name if resolved else None,
            "auto_install": False,
        })
    return {"items": items, "count": len(items), "source": "local:configured-adapters", "truncated": False}


def run_external(tool: str, args: list[str], timeout: int = EXTERNAL_TIMEOUT) -> dict[str, Any]:
    command = command_parts(tool)
    if not command:
        env_name = EXTERNAL_TOOLS[tool]
        return {
            "status": "UNAVAILABLE",
            "tool": tool,
            "error": f"Configure {env_name} with an installed executable. No download was attempted.",
        }
    try:
        result = subprocess.run(
            [*command, *args],
            cwd=workspace_root(),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "ERROR", "tool": tool, "error": f"Tool timed out after {timeout} seconds"}
    return {
        "status": "OK" if result.returncode == 0 else "ERROR",
        "tool": tool,
        "exit_code": result.returncode,
        "stdout": result.stdout[:CHARACTER_LIMIT],
        "stderr": result.stderr[:4000],
        "truncated": len(result.stdout) > CHARACTER_LIMIT,
    }


def quality_check(path: str, engine: str = "auto") -> dict[str, Any]:
    target = safe_workspace_path(path, must_exist=True)
    structural = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "cpi_iflow_packager.py"), "validate", "--input", str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=EXTERNAL_TIMEOUT,
    )
    checks = [{
        "engine": "structural",
        "status": "PASS" if structural.returncode == 0 else "FAIL",
        "output": (structural.stdout or structural.stderr)[:CHARACTER_LIMIT],
    }]
    if engine in {"auto", "cpilint"}:
        if command_parts("cpilint"):
            lint = run_external("cpilint", [str(target)])
            checks.append({"engine": "cpilint", **lint})
        elif engine == "cpilint":
            return {"status": "UNAVAILABLE", "checks": checks, "error": "CPILINT_CMD is not configured or resolvable"}
        else:
            checks.append({"engine": "cpilint", "status": "SKIPPED", "reason": "CPILINT_CMD unavailable"})
    failed = any(item.get("status") in {"FAIL", "ERROR"} for item in checks)
    return {"status": "FAIL" if failed else "PASS", "path": str(target), "checks": checks}


def steampipe_query(sql: str) -> dict[str, Any]:
    compact = re.sub(r"\s+", " ", sql.strip())
    forbidden = re.compile(r"\b(insert|update|delete|drop|alter|create|copy|grant|revoke|call)\b", re.I)
    if not compact.lower().startswith("select ") or ";" in compact or forbidden.search(compact):
        raise ValueError("Only one read-only SELECT statement without semicolons is allowed")
    return run_external("steampipe", ["query", compact, "--output", "json"])


def mapping_test(mapping: str, input_file: str, expected_file: str = "") -> dict[str, Any]:
    mapping_path = safe_workspace_path(mapping, must_exist=True)
    input_path = safe_workspace_path(input_file, must_exist=True)
    args = ["test", "--mapping", str(mapping_path), "--input", str(input_path)]
    if expected_file:
        args += ["--expected", str(safe_workspace_path(expected_file, must_exist=True))]
    return run_external("mapping_test", args)


def run_approval_broker(command_args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "approval_broker.py"), *command_args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        payload = {"status": "ERROR", "error": (result.stdout or result.stderr)[:4000]}
    if result.returncode != 0:
        raise RuntimeError(stable_json(payload))
    return payload


def make_plan(capability: str, target: str, summary: str, effect: str, arguments: dict[str, Any], preconditions: dict[str, Any], commit_command: list[str]) -> dict[str, Any]:
    plan = run_approval_broker([
        "plan", "--capability", capability, "--target", target, "--summary", summary,
        "--effect", effect, "--arguments-json", stable_json(arguments),
        "--preconditions-json", stable_json(preconditions),
    ])
    commit_command += [
        "--action-id", plan["action_id"], "--plan-hash", plan["plan_hash"],
        "--argument-hash", plan["argument_hash"], "--precondition-hash", plan["precondition_hash"],
    ]
    plan["commit_command"] = " ".join(shell_quote(item) for item in commit_command)
    plan["arguments"] = arguments
    plan["preconditions"] = preconditions
    return plan


def approval_hash_args(args: argparse.Namespace, arguments: dict[str, Any], preconditions: dict[str, Any]) -> list[str]:
    return [
        args.action_id, "--plan-hash", args.plan_hash,
        "--argument-hash", args.argument_hash or json_sha256(arguments),
        "--precondition-hash", args.precondition_hash or json_sha256(preconditions),
    ]


def with_approval(args: argparse.Namespace, arguments: dict[str, Any], preconditions: dict[str, Any], run) -> dict[str, Any]:
    """Verify the approval, run the mutation, then spend it.

    Spending up front burns a one-time approval on transient failures - a network
    error or an HTTP 500 would leave the operator re-approving a change that
    never landed.
    """
    hash_args = approval_hash_args(args, arguments, preconditions)
    run_approval_broker(["verify"] + hash_args)
    # The runtime helpers raise on HTTP errors, so catch here: the caller has to
    # learn whether the approval is still spendable, not just see a traceback.
    try:
        result = run()
    except Exception as exc:  # noqa: BLE001 - reported, not swallowed
        result = {"status": "ERROR", "error": str(exc), "error_type": type(exc).__name__}
    if result.get("status") != "OK":
        result["approval"] = "still-open"
        result["next_step"] = (
            "The operation failed, so approval {0} was not spent. Retry the commit, or reject it with: "
            "python scripts/approval_broker.py reject {0}".format(args.action_id)
        )
        return result
    try:
        run_approval_broker(["consume"] + hash_args)
        result["approval"] = "spent"
    except RuntimeError as exc:
        result["approval"] = "applied-but-not-spent"
        result["warning"] = (
            "The operation succeeded but approval {0} could not be marked consumed: {1}. "
            "Reject it so it cannot be replayed.".format(args.action_id, exc)
        )
    return result


def deploy_arguments(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "artifact_id": args.artifact_id,
        "version": args.version,
        "zip": str(safe_workspace_path(args.zip, must_exist=False)) if args.zip else "",
        "strategy": args.strategy,
        "runtime_deploy": bool(args.runtime_deploy),
    }


def tenant_preconditions(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    checks = {
        "base_url_configured": bool(env_value("CPI_BASE_URL", "CPI_TENANT_URL")),
        "token_url_configured": bool(env_value("CPI_OAUTH_TOKEN_URL", "CPI_TOKEN_URL")),
        "client_id_configured": bool(env_value("CPI_OAUTH_CLIENT_ID", "CPI_CLIENT_ID")),
        "client_secret_configured": bool(env_value("CPI_OAUTH_CLIENT_SECRET", "CPI_CLIENT_SECRET")),
    }
    checks.update(extra or {})
    return checks


def plan_deploy(args: argparse.Namespace) -> dict[str, Any]:
    arguments = deploy_arguments(args)
    preconditions = tenant_preconditions({"zip_exists": bool(not args.zip or Path(arguments["zip"]).is_file())})
    if not preconditions["zip_exists"]:
        raise ValueError(f"ZIP file not found: {args.zip}")
    commit = [sys.executable, "scripts/cpi_client.py", "deploy", "commit", "--artifact-id", args.artifact_id, "--version", args.version, "--strategy", args.strategy]
    if arguments["zip"]:
        commit += ["--zip", arguments["zip"]]
    if args.runtime_deploy:
        commit.append("--runtime-deploy")
    return make_plan(
        "sap.cpi.artifact.deploy", f"{args.artifact_id}:{args.version}",
        f"CPI upload/deploy {args.artifact_id}:{args.version}", "mutating", arguments, preconditions, commit,
    )


def commit_deploy(args: argparse.Namespace) -> dict[str, Any]:
    arguments = deploy_arguments(args)
    preconditions = tenant_preconditions({"zip_exists": bool(not args.zip or Path(arguments["zip"]).is_file())})
    if not all(preconditions.values()):
        return {"status": "BLOCKED", "reason": "preconditions-not-met", "preconditions": preconditions}
    def run() -> dict[str, Any]:
        steps = []
        if args.zip:
            steps.append(upload_iflow_zip(args.artifact_id, args.version, arguments["zip"], args.strategy))
        if args.runtime_deploy:
            steps.append(deploy_runtime_artifact(args.artifact_id, args.version))
        failed = [step for step in steps if isinstance(step, dict) and step.get("status") not in (None, "OK")]
        return {
            "status": "ERROR" if failed else "OK",
            "artifact_id": args.artifact_id,
            "version": args.version,
            "steps": steps,
        }

    return with_approval(args, arguments, preconditions, run)


def plan_undeploy(args: argparse.Namespace) -> dict[str, Any]:
    arguments = {"artifact_id": args.artifact_id}
    preconditions = tenant_preconditions()
    commit = [sys.executable, "scripts/cpi_client.py", "undeploy", "commit", "--artifact-id", args.artifact_id]
    return make_plan(
        "sap.cpi.artifact.undeploy", args.artifact_id, f"CPI undeploy {args.artifact_id}",
        "destructive", arguments, preconditions, commit,
    )


def commit_undeploy(args: argparse.Namespace) -> dict[str, Any]:
    arguments = {"artifact_id": args.artifact_id}
    preconditions = tenant_preconditions()
    if not all(preconditions.values()):
        return {"status": "BLOCKED", "reason": "preconditions-not-met", "preconditions": preconditions}
    return with_approval(args, arguments, preconditions, lambda: undeploy_runtime_artifact(args.artifact_id))


def local_operation_data(args: argparse.Namespace, operation: str) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    if operation == "generate":
        output = safe_workspace_path(args.output)
        arguments = {"name": args.name, "output": str(output), "overwrite": bool(args.overwrite)}
        preconditions = {"workspace_exists": workspace_root().is_dir(), "target_available": bool(args.overwrite or not output.exists())}
        command = [sys.executable, "scripts/cpi_client.py", "generate", "commit", "--name", args.name, "--output", str(output)]
        if args.overwrite:
            command.append("--overwrite")
    elif operation == "plot":
        source = safe_workspace_path(args.input, must_exist=True)
        output = safe_workspace_path(args.output)
        arguments = {"input": str(source), "output": str(output), "format": args.format, "overwrite": bool(args.overwrite)}
        preconditions = {"source_exists": source.is_file(), "plotter_available": bool(command_parts("plotter")), "target_available": bool(args.overwrite or not output.exists())}
        command = [sys.executable, "scripts/cpi_client.py", "plot", "commit", "--input", str(source), "--output", str(output), "--format", args.format]
        if args.overwrite:
            command.append("--overwrite")
    else:
        repo = safe_workspace_path(args.workspace, must_exist=True)
        arguments = {"workspace": str(repo), "direction": args.direction}
        preconditions = {"workspace_exists": repo.is_dir(), "sync_available": bool(command_parts("sync"))}
        command = [sys.executable, "scripts/cpi_client.py", "sync", "commit", "--workspace", str(repo), "--direction", args.direction]
    return arguments, preconditions, command


def plan_local_operation(args: argparse.Namespace, operation: str) -> dict[str, Any]:
    arguments, preconditions, command = local_operation_data(args, operation)
    target = arguments.get("output", arguments.get("workspace", ""))
    effect = "destructive" if arguments.get("overwrite") else "mutating"
    capability = {
        "generate": "sap.cpi.iflow.generate",
        "plot": "sap.cpi.diagram.generate",
        "sync": "sap.cpi.sync.execute",
    }[operation]
    return make_plan(capability, str(target), f"CPI {operation} {target}", effect, arguments, preconditions, command)


def commit_local_operation(args: argparse.Namespace, operation: str) -> dict[str, Any]:
    arguments, preconditions, _ = local_operation_data(args, operation)
    if not all(preconditions.values()):
        return {"status": "BLOCKED", "reason": "preconditions-not-met", "preconditions": preconditions}
    def run() -> dict[str, Any]:
        if operation == "generate":
            output = Path(arguments["output"])
            if output.exists() and args.overwrite:
                output.unlink()
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "cpi_iflow_packager.py"), "template", "--name", args.name, "--output", str(output)],
                cwd=ROOT, capture_output=True, text=True, timeout=EXTERNAL_TIMEOUT,
            )
            return {"status": "OK" if result.returncode == 0 else "ERROR", "operation": "generate", "output": str(output), "stdout": result.stdout[:CHARACTER_LIMIT], "stderr": result.stderr[:4000]}
        if operation == "plot":
            return run_external("plotter", ["--input", arguments["input"], "--output", arguments["output"], "--format", arguments["format"]])
        return run_external("sync", [arguments["direction"], "--workspace", arguments["workspace"]])

    return with_approval(args, arguments, preconditions, run)


def test_connection() -> dict[str, Any]:
    token = get_oauth_token()
    response = requests.get(
        f"{cpi_base_url()}/api/v1/",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=HTTP_TIMEOUT,
    )
    response.raise_for_status()
    return {"status": "OK", "oauth": "OK", "api_http_status": response.status_code}


def add_pagination(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--offset", type=int, default=0)


def add_approval(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--action-id", required=True)
    parser.add_argument("--plan-hash", required=True)
    parser.add_argument("--argument-hash")
    parser.add_argument("--precondition-hash")


def add_plan_commit(parent: argparse.ArgumentParser, configure) -> Any:
    sub = parent.add_subparsers(dest=f"{parent.prog.split()[-1]}_command", required=True)
    for name in ("plan", "commit"):
        child = sub.add_parser(name)
        configure(child)
    add_approval(sub.choices["commit"])
    return sub


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SAP CPI OData client and approved local tooling adapters")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("test-connection")

    packages = sub.add_parser("packages")
    packages.add_argument("--id", default="")
    packages.add_argument("--query", default="")
    add_pagination(packages)

    artifacts = sub.add_parser("artifacts")
    artifacts.add_argument("--package-id", default="")
    artifacts.add_argument("--query", default="")
    artifacts.add_argument("--artifact-type", choices=sorted(ARTIFACT_ENTITY_SETS), default="integration_flow")
    artifacts.add_argument("--runtime", action="store_true", help="Compatibility alias for the runtime command")
    add_pagination(artifacts)

    artifact = sub.add_parser("artifact")
    artifact.add_argument("--id", required=True)
    artifact.add_argument("--version", default="active")
    artifact.add_argument("--artifact-type", choices=sorted(ARTIFACT_ENTITY_SETS), default="integration_flow")

    runtime = sub.add_parser("runtime")
    runtime.add_argument("--status", default="")
    runtime.add_argument("--query", default="")
    add_pagination(runtime)

    logs = sub.add_parser("logs")
    logs.add_argument("--top", type=int, help="Compatibility alias for --limit")
    logs.add_argument("--status", default="")
    logs.add_argument("--integration-flow-id", default="")
    logs.add_argument("--log-level", default="")
    logs.add_argument("--from-time", default="")
    logs.add_argument("--to-time", default="")
    add_pagination(logs)

    message = sub.add_parser("message")
    message.add_argument("--guid", required=True)
    message.add_argument("--include-adapter-attributes", action="store_true")
    message.add_argument("--include-custom-headers", action="store_true")
    message.add_argument("--include-trace", action="store_true")

    quality = sub.add_parser("quality")
    quality.add_argument("--input", required=True)
    quality.add_argument("--engine", choices=["auto", "structural", "cpilint"], default="auto")
    sub.add_parser("tools-status")
    sql = sub.add_parser("steampipe")
    sql.add_argument("--query", required=True)
    mapping = sub.add_parser("mapping-test")
    mapping.add_argument("--mapping", required=True)
    mapping.add_argument("--input", required=True)
    mapping.add_argument("--expected", default="")

    deploy = sub.add_parser("deploy")
    def configure_deploy(child):
        child.add_argument("--artifact-id", required=True)
        child.add_argument("--version", default="active")
        child.add_argument("--zip")
        child.add_argument("--strategy", choices=["auto", "put", "post-override"], default="auto")
        child.add_argument("--runtime-deploy", action="store_true")
    add_plan_commit(deploy, configure_deploy)

    undeploy = sub.add_parser("undeploy")
    add_plan_commit(undeploy, lambda child: child.add_argument("--artifact-id", required=True))

    generate = sub.add_parser("generate")
    def configure_generate(child):
        child.add_argument("--name", required=True)
        child.add_argument("--output", required=True)
        child.add_argument("--overwrite", action="store_true")
    add_plan_commit(generate, configure_generate)

    plot = sub.add_parser("plot")
    def configure_plot(child):
        child.add_argument("--input", required=True)
        child.add_argument("--output", required=True)
        child.add_argument("--format", choices=["html", "svg", "png"], default="html")
        child.add_argument("--overwrite", action="store_true")
    add_plan_commit(plot, configure_plot)

    sync = sub.add_parser("sync")
    def configure_sync(child):
        child.add_argument("--workspace", required=True)
        child.add_argument("--direction", choices=["pull", "push", "export", "import"], required=True)
    add_plan_commit(sync, configure_sync)
    return parser


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "test-connection":
        return test_connection()
    if args.command == "packages":
        return list_packages(args.id, args.query, args.limit, args.offset)
    if args.command == "artifacts":
        return list_runtime_artifacts(query=args.query, limit=args.limit, offset=args.offset) if args.runtime else list_artifacts(args.package_id, args.query, args.artifact_type, args.limit, args.offset)
    if args.command == "artifact":
        return get_artifact(args.id, args.version, args.artifact_type)
    if args.command == "runtime":
        return list_runtime_artifacts(args.status, args.query, args.limit, args.offset)
    if args.command == "logs":
        return list_logs(args.status, args.integration_flow_id, args.log_level, args.from_time, args.to_time, args.top or args.limit, args.offset)
    if args.command == "message":
        return message_details(args.guid, args.include_adapter_attributes, args.include_custom_headers, args.include_trace)
    if args.command == "quality":
        return quality_check(args.input, args.engine)
    if args.command == "tools-status":
        return external_tools_status()
    if args.command == "steampipe":
        return steampipe_query(args.query)
    if args.command == "mapping-test":
        return mapping_test(args.mapping, args.input, args.expected)
    action = getattr(args, f"{args.command}_command")
    if args.command == "deploy":
        return plan_deploy(args) if action == "plan" else commit_deploy(args)
    if args.command == "undeploy":
        return plan_undeploy(args) if action == "plan" else commit_undeploy(args)
    return plan_local_operation(args, args.command) if action == "plan" else commit_local_operation(args, args.command)


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = execute(args)
        print(json.dumps(result, indent=2, default=str))
        return 1 if result.get("status") in {"ERROR", "FAIL", "BLOCKED", "UNAVAILABLE"} else 0
    except Exception as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc), "error_type": type(exc).__name__}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
