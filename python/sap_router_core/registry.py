from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".agents"
REGISTRIES = AGENTS / "registries"
PROFILES = AGENTS / "profiles"
CREWS = AGENTS / "crews"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_capabilities() -> dict[str, dict[str, Any]]:
    data = load_json(REGISTRIES / "capabilities.json")
    return {item["id"]: item for item in data.get("capabilities", [])}


def load_servers() -> dict[str, dict[str, Any]]:
    data = load_json(REGISTRIES / "mcps.json")
    return {item["id"]: item for item in data.get("servers", [])}


def load_mcp_capability_specs() -> dict[str, dict[str, Any]]:
    path = REGISTRIES / "mcp-capabilities.json"
    if not path.exists():
        return {}
    return load_json(path).get("capabilities", {})


def load_policies() -> dict[str, Any]:
    return load_json(REGISTRIES / "policies.json")


def load_routes() -> list[dict[str, Any]]:
    return load_json(REGISTRIES / "routes.json").get("routes", [])


def load_profiles() -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    if not PROFILES.exists():
        return profiles
    for path in PROFILES.glob("*.json"):
        data = load_json(path)
        profiles[data["id"]] = data
    return profiles


def resolve_servers_for_capability(capability: str) -> list[dict[str, Any]]:
    servers = [
        server for server in load_servers().values()
        if capability in server.get("capabilities", [])
        and server.get("status") == "enabled"
    ]
    if servers:
        return sorted(servers, key=lambda item: item.get("routing", {}).get("priority", 999))
    # Fail closed. Reviewed candidates remain visible in diagnostics/search but
    # never become route selections until explicitly promoted into mcps.json.
    return []


def classify_task(task: str) -> dict[str, Any]:
    text = task.lower()
    if any(token in text for token in ("undeploy", "desimplantar")) and any(token in text for token in ("cpi", "iflow", "integration flow")):
        route = {"capability": "sap.cpi.artifact.undeploy", "profile": "sap-cpi-developer", "fallback_group": "cpi"}
        servers = resolve_servers_for_capability(route["capability"])
        return {
            "request_id": str(uuid.uuid4()),
            "intent": task,
            "capability": route["capability"],
            "profile": route["profile"],
            "fallback_group": route["fallback_group"],
            "candidate_servers": [server["id"] for server in servers],
            "selected_server": servers[0]["id"] if servers else None,
            "selection_reason": "destructive verb matched; approval and strong confirmation required",
            "created_at": now_iso(),
        }
    if any(token in text for token in ("deploy", "implantar", "publicar")) and any(token in text for token in ("cpi", "iflow", "integration flow")):
        route = {"capability": "sap.cpi.artifact.deploy", "profile": "sap-cpi-developer", "fallback_group": "cpi"}
        servers = resolve_servers_for_capability(route["capability"])
        return {
            "request_id": str(uuid.uuid4()),
            "intent": task,
            "capability": route["capability"],
            "profile": route["profile"],
            "fallback_group": route["fallback_group"],
            "candidate_servers": [server["id"] for server in servers],
            "selected_server": servers[0]["id"] if servers else None,
            "selection_reason": "mutating verb matched; readiness requires probe",
            "created_at": now_iso(),
        }
    if any(token in text for token in ("alterar", "change", "modify", "deploy", "implantar", "publicar")) and any(token in text for token in ("apim", "api management", "api proxy", "policy")):
        capability = "sap.apim.proxy.deploy" if any(token in text for token in ("deploy", "implantar", "publicar")) else "sap.apim.proxy.modify"
        servers = resolve_servers_for_capability(capability)
        return {
            "request_id": str(uuid.uuid4()),
            "intent": task,
            "capability": capability,
            "profile": "sap-api-management-consultant",
            "fallback_group": "apim",
            "candidate_servers": [server["id"] for server in servers],
            "selected_server": servers[0]["id"] if servers else None,
            "selection_reason": "mutating verb matched; readiness requires probe",
            "created_at": now_iso(),
        }
    for route in load_routes():
        if any(str(token).lower() in text for token in route.get("match", [])):
            servers = resolve_servers_for_capability(route["capability"])
            return {
                "request_id": str(uuid.uuid4()),
                "intent": task,
                "capability": route["capability"],
                "profile": route["profile"],
                "fallback_group": route["fallback_group"],
                "candidate_servers": [server["id"] for server in servers],
                "selected_server": servers[0]["id"] if servers else None,
                "selection_reason": "first enabled registry candidate; readiness requires probe" if servers else "no enabled candidate",
                "created_at": now_iso(),
            }
    return {
        "request_id": str(uuid.uuid4()),
        "intent": task,
        "capability": None,
        "profile": None,
        "candidate_servers": [],
        "selected_server": None,
        "selection_reason": "unknown task; fail-closed until route is registered",
        "created_at": now_iso(),
    }


def _env_status(env_refs: list[str]) -> str:
    concrete_refs = [
        ref for ref in env_refs
        if not ref.endswith("_REF")
    ]
    if not concrete_refs:
        return "NO_ENV_NEEDED"
    missing = [ref for ref in concrete_refs if not os.environ.get(ref)]
    if not missing:
        return "ALL_SET"
    if len(missing) == len(concrete_refs):
        return "NONE_SET"
    return "PARTIAL"


def _resolve_command(command: str) -> str:
    resolved = shutil.which(command)
    if resolved:
        return resolved
    if sys.platform.startswith("win") and not command.lower().endswith((".exe", ".cmd", ".bat")):
        for suffix in (".cmd", ".exe", ".bat"):
            resolved = shutil.which(command + suffix)
            if resolved:
                return resolved
    return command


def _run_jsonrpc_stdio(command: str, args: list[str], timeout: int, env=None, cwd=None, server_id=None):
    from .probe_transport import stdio_probe
    return stdio_probe(command, args, timeout, env, cwd or ROOT, server_id)


def tls_error() -> bool:
    return (os.environ.get("ARC_SAP_SSL_VERIFY", "true").lower() in {"false", "0", "no"}
            or any(os.environ.get(k, "false").lower() in {"true", "1", "yes"}
                   for k in ("SAP_ALLOW_UNAUTHORIZED", "WEB_ALLOW_UNAUTHORIZED"))
            or os.environ.get("NODE_TLS_REJECT_UNAUTHORIZED") == "0")


def _run_command_probe(command: str, args: list[str], timeout: int) -> dict[str, Any]:
    result = subprocess.run(
        [_resolve_command(command)] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "exit_code": result.returncode,
        "binary": "AVAILABLE" if result.returncode == 0 else "ERROR",
        "domain_probe": "PASS" if result.returncode == 0 else "FAIL",
        "error": (result.stderr or result.stdout)[:300] if result.returncode != 0 else None,
    }


def _run_cli_domain_probe(command: str, args: list[str], probe_name: str, timeout: int) -> dict[str, Any]:
    result = _run_command_probe(command, args, timeout)
    binary_status = result["binary"]
    domain_status = "FAIL"
    error = result["error"]
    if probe_name == "help_command":
        domain_status = "DEGRADED" if binary_status == "AVAILABLE" else "FAIL"
        error = error or "Help command proves install only, not SAP domain readiness"
    elif probe_name in {"cpi_test_connection", "apim_health"}:
        domain_status = "PASS" if result["exit_code"] == 0 else "FAIL"
        if result["exit_code"] != 0:
            error = error or f"{probe_name} failed"
    else:
        domain_status = "NOT_PROVED" if binary_status == "AVAILABLE" else "FAIL"
        error = error or f"No domain probe implementation for {probe_name}"
    return {
        "exit_code": result["exit_code"],
        "binary": binary_status,
        "domain_probe": domain_status,
        "error": error,
    }


def _run_named_domain_probe(name: str, timeout: int) -> dict[str, Any]:
    probe_scripts = {
        "browser_session_probe": ["python", "scripts/browser_session_probe.py"],
        "sap_gui_session_probe": ["python", "scripts/sap_gui_session_probe.py"],
    }
    if name not in probe_scripts:
        return {"domain_probe": "NOT_PROVED", "error": f"Unknown domain probe: {name}"}
    command, *args = probe_scripts[name]
    result = subprocess.run(
        [_resolve_command(command)] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    status = None
    try:
        status = json.loads(result.stdout or "{}").get("status")
    except json.JSONDecodeError:
        status = None
    return {
        "domain_probe": "PASS" if status == "READY" else "DEGRADED" if status == "DEGRADED" else "FAIL",
        "error": None if status == "READY" else (result.stdout or result.stderr or f"Probe status: {status}")[:300],
    }


def probe_server(server_id: str, execute: bool = False, timeout: int = 10) -> dict[str, Any]:
    started = time.monotonic()
    server = load_servers().get(server_id)
    result = {
        "server_id": server_id, "status": "UNAVAILABLE", "checked_at": now_iso(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat().replace("+00:00", "Z"),
        "checks": {"env": "NOT_PROVED", "binary": "SKIPPED", "initialize": "NOT_PROVED",
                   "tools_list": "NOT_PROVED", "domain_probe": "NOT_PROVED"},
        "capabilities_ready": [], "mutation_ready": False, "exit_code": None,
        "error_code": "NOT_READY", "error": None,
    }
    def finish(code=None, error=None):
        if code:
            result.update(error_code=code, error=error)
        result["duration_ms"] = round((time.monotonic() - started) * 1000, 2)
        return result
    if not server or server.get("status") != "enabled":
        return finish("SERVER_NOT_ENABLED", "Unknown, disabled or planned server.")
    checks = result["checks"]
    checks["env"] = _env_status(server.get("auth", {}).get("env_refs", []))
    if not execute:
        result["status"] = "DEGRADED"
        return finish("NOT_EXECUTED", "Offline inventory only; semantic read not executed.")
    if tls_error():
        return finish("TLS_VERIFICATION_REQUIRED", "Enable certificate verification and configure the trusted CA before live probes.")
    from .local_runtime import resolve_runtime
    runtime = resolve_runtime(ROOT, server_id, server.get("runtime", {}))
    command = runtime.get("command", "")
    if command == 'python':
        command = sys.executable
    args = runtime.get("args", [])
    if Path(command).stem.lower() in {"npx", "npm", "uvx", "pip", "pnpm", "bunx"}:
        return finish("LOCAL_RUNTIME_REQUIRED", "Prepare a pinned local executable; probes never install packages.")
    if server_id == "context-mode" and any(str(a).endswith("start.mjs") for a in args):
        return finish("BOOTSTRAP_REVIEW_REQUIRED", "Auto-repair bootstrap is not allowed in a diagnostic.")
    cwd = (ROOT / runtime.get("cwd", ".")).resolve()
    if cwd != ROOT and ROOT not in cwd.parents:
        return finish("INVALID_CWD", "Runtime working directory must stay inside the repository.")
    if not shutil.which(command) and not Path(command).is_file():
        checks["binary"] = "NOT_INSTALLED"
        return finish("LOCAL_RUNTIME_REQUIRED", "Configured executable is not installed.")
    try:
        from .local_runtime import runtime_environment
        runtime_env = runtime_environment(server_id, runtime)
        # A child must not bypass TLS via a runtime override.
        runtime_env.update(SAP_ALLOW_UNAUTHORIZED="false", WEB_ALLOW_UNAUTHORIZED="false",
                           ARC_SAP_SSL_VERIFY="true", NODE_TLS_REJECT_UNAUTHORIZED="1")
        if command == "python":
            command = sys.executable
        stdio = _run_jsonrpc_stdio(command, args, timeout, runtime_env, cwd, server_id)
        checks.update({k: stdio[k] for k in ("initialize", "tools_list", "domain_probe") if k in stdio})
        checks["binary"] = "AVAILABLE" if checks["initialize"] == "PASS" else "ERROR"
        result["error"] = stdio.get("error")
        if server_id == "mcp-sap-gui" and checks["initialize"] == "PASS":
            domain = _run_named_domain_probe("sap_gui_session_probe", timeout)
            checks["domain_probe"] = domain["domain_probe"]
            result["error"] = None if checks["domain_probe"] == "PASS" else "No readable, non-busy SAP GUI session."
    except (OSError, subprocess.TimeoutExpired) as exc:
        return finish("PROBE_FAILED", type(exc).__name__ + ": probe failed; backend payload omitted.")
    if all(checks[k] == "PASS" for k in ("initialize", "tools_list", "domain_probe")):
        result.update(status="READY", error_code=None, error=None)
        # Domain read readiness never grants mutation authority.
        caps = load_capabilities()
        result["capabilities_ready"] = [c for c in server.get("capabilities", [])
                                       if caps.get(c, {}).get("effect") == "read"]
    elif checks["initialize"] == "PASS":
        result["status"] = "DEGRADED"
    return finish()


def validate_catalog() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    capabilities = load_capabilities()
    servers = load_servers()
    profiles = load_profiles()
    routes = load_routes()
    versions_path = REGISTRIES / "versions.json"
    versions = load_json(versions_path) if versions_path.exists() else {}
    for server_id, server in servers.items():
        for field in ("id", "status", "source", "runtime", "capabilities", "safety", "probes", "routing", "owner"):
            if field not in server:
                errors.append(f"server {server_id}: missing {field}")
        for cap in server.get("capabilities", []):
            if cap not in capabilities:
                errors.append(f"server {server_id}: unknown capability {cap}")
    for route in routes:
        cap = route.get("capability")
        profile = route.get("profile")
        if cap not in capabilities:
            errors.append(f"route {route.get('match')}: unknown capability {cap}")
        if profile not in profiles:
            errors.append(f"route {route.get('match')}: unknown profile {profile}")
    for profile_id, profile in profiles.items():
        profile_caps = profile.get("capabilities", {})
        for bucket in ("allow", "gated", "deny"):
            for cap in profile_caps.get(bucket, []):
                if cap not in capabilities:
                    errors.append(f"profile {profile_id}: unknown {bucket} capability {cap}")
    crew_path = CREWS / "caveman.json"
    crew = load_json(crew_path) if crew_path.exists() else {"workers": []}
    profile_target = versions.get("profile_count_target")
    if profile_target is not None and len(profiles) != int(profile_target):
        errors.append(f"profiles: {len(profiles)} present, target is {profile_target}")
    skill_target = versions.get("skill_count_target")
    skills_dir = AGENTS / "skills"
    if skill_target is not None and skills_dir.exists():
        skill_count = len(list(skills_dir.glob("*/SKILL.md")))
        if skill_count != int(skill_target):
            errors.append(f"skills: {skill_count} present, target is {skill_target}")
    bundled_sources = load_json(REGISTRIES / "bundled-sources.json") if (REGISTRIES / "bundled-sources.json").exists() else {"sources": []}
    bundled_lock = load_json(REGISTRIES / "bundled-sources.lock.json") if (REGISTRIES / "bundled-sources.lock.json").exists() else {"sources": []}
    declared_ids = {item["id"] for item in bundled_sources.get("sources", [])}
    locked_ids = {item["id"] for item in bundled_lock.get("sources", [])}
    if declared_ids != locked_ids:
        errors.append(f"bundled sources: declared/locked mismatch missing={sorted(declared_ids - locked_ids)} extra={sorted(locked_ids - declared_ids)}")
    for item in bundled_lock.get("sources", []):
        path = ROOT / item.get("path", "")
        if not path.is_dir():
            errors.append(f"bundled source {item.get('id')}: missing path {item.get('path')}")
        elif any(candidate.name == ".git" for candidate in path.rglob(".git")):
            errors.append(f"bundled source {item.get('id')}: nested Git metadata is forbidden")
    mcp_config_path = ROOT / ".mcp.json"
    candidates_path = REGISTRIES / "mcp-candidates.json"
    if mcp_config_path.exists() and candidates_path.exists():
        mcp_config = load_json(mcp_config_path)
        configured_ids = set(mcp_config.get("mcpServers", {}))
        planned_ids = set(mcp_config.get("plannedServers", {}))
        candidate_items = load_json(candidates_path).get("candidates", [])
        candidate_ids = [item["id"] for item in candidate_items]
        candidate_set = set(candidate_ids)
        duplicates = sorted({item for item in candidate_ids if candidate_ids.count(item) > 1})
        if duplicates:
            errors.append(f"MCP candidates contain duplicate ids: {duplicates}")
        missing_planned = sorted(candidate_set - planned_ids)
        if missing_planned:
            errors.append(f"MCP candidates missing from plannedServers: {missing_planned}")
        promoted_candidates = sorted(configured_ids & candidate_set)
        if promoted_candidates:
            errors.append(f"MCP candidates cannot be active without promotion: {promoted_candidates}")
        unmanaged = configured_ids - set(servers) - candidate_set
        if unmanaged:
            errors.append(f"MCP config has unmanaged servers: {sorted(unmanaged)}")
        mcp_specs = load_mcp_capability_specs()
        enabled_servers = {
            server_id for server_id, server in servers.items()
            if server.get("status") == "enabled"
        }
        for capability, spec in mcp_specs.items():
            if capability not in capabilities:
                errors.append(f"MCP capability {capability}: missing from capabilities.json")
            # A capability may declare status="planned" to say, on the record,
            # that it has no launchable provider yet. That is reported as a
            # warning; routing still fails closed because the server is not in
            # enabled_servers. Anything not declared planned stays an error.
            declared_planned = spec.get("status") == "planned"
            for server_id in [spec.get("primary")] + list(spec.get("fallbacks", [])):
                if not server_id or server_id.startswith("plugin:"):
                    continue
                if server_id not in enabled_servers:
                    state = "disabled candidate" if server_id in candidate_set else "unknown or disabled server"
                    message = f"MCP capability {capability}: {state} {server_id} is not routable"
                    if declared_planned:
                        warnings.append(message + " (capability declared planned)")
                    else:
                        errors.append(message)
            primary = spec.get("primary")
            if primary in servers and capability not in servers[primary].get("capabilities", []):
                errors.append(f"MCP capability {capability}: primary {primary} does not advertise the capability")
    return {
        "status": "PASS" if not errors else "FAIL",
        "checked_at": now_iso(),
        "counts": {
            "capabilities": len(capabilities),
            "servers": len(servers),
            "profiles": len(profiles),
            "routes": len(routes),
            "caveman_workers": len(crew.get("workers", [])),
            "profile_target": profile_target,
            "skill_target": skill_target,
            "bundled_sources": len(locked_ids),
        },
        "errors": errors,
        "warnings": warnings,
    }
