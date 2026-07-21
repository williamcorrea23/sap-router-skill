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
from datetime import datetime, timedelta
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
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_capabilities() -> dict[str, dict[str, Any]]:
    data = load_json(REGISTRIES / "capabilities.json")
    return {item["id"]: item for item in data.get("capabilities", [])}


def load_servers() -> dict[str, dict[str, Any]]:
    data = load_json(REGISTRIES / "mcps.json")
    return {item["id"]: item for item in data.get("servers", [])}


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
    return sorted(servers, key=lambda item: item.get("routing", {}).get("priority", 999))


def classify_task(task: str) -> dict[str, Any]:
    text = task.lower()
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
        if not ref.endswith("_REF") and "PASSWORD" not in ref and "SECRET" not in ref and "TOKEN" not in ref
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


def _run_jsonrpc_stdio(command: str, args: list[str], timeout: int, env: dict[str, str] | None = None) -> dict[str, Any]:
    requests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "sap-router-probe", "version": "1.0.0"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    payload = "".join(json.dumps(request) + "\n" for request in requests)
    proc = subprocess.Popen(
        [_resolve_command(command)] + args,
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    responses: dict[int, dict[str, Any]] = {}
    output: list[str] = []
    errors: list[str] = []
    lines: queue.Queue[str | None] = queue.Queue()

    def read_stream(stream: Any, destination: list[str], publish: bool = False) -> None:
        for line in iter(stream.readline, ""):
            destination.append(line)
            if publish:
                lines.put(line)
        if publish:
            lines.put(None)

    stdout_thread = threading.Thread(target=read_stream, args=(proc.stdout, output, True), daemon=True)
    stderr_thread = threading.Thread(target=read_stream, args=(proc.stderr, errors), daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    assert proc.stdin is not None
    proc.stdin.write(payload)
    proc.stdin.flush()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not (1 in responses and 2 in responses):
        try:
            line = lines.get(timeout=min(0.2, max(0.01, deadline - time.monotonic())))
        except queue.Empty:
            if proc.poll() is not None:
                break
            continue
        if line is None:
            break
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(message.get("id"), int):
            responses[message["id"]] = message
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
    stdout_thread.join(timeout=1)
    stderr_thread.join(timeout=1)
    stdout = "".join(output)
    stderr = "".join(errors)
    init_ok = 1 in responses and "result" in responses[1]
    tools_ok = 2 in responses and isinstance(responses[2].get("result", {}).get("tools"), list)
    error = None
    if not init_ok or not tools_ok:
        error = (stderr or stdout or "MCP did not return initialize/tools_list responses")[:300]
    return {
        "initialize": "PASS" if init_ok else "NOT_PROVED",
        "tools_list": "PASS" if tools_ok else "NOT_PROVED",
        "error": error,
    }


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
    servers = load_servers()
    if server_id not in servers:
        return {
            "server_id": server_id,
            "status": "UNAVAILABLE",
            "checked_at": now_iso(),
            "error_code": "UNKNOWN_SERVER",
        }
    server = servers[server_id]
    if server.get("status") != "enabled":
        return {
            "server_id": server_id,
            "status": server.get("status", "DISABLED").upper(),
            "checked_at": now_iso(),
            "error_code": "SERVER_NOT_ENABLED",
        }
    runtime = server.get("runtime", {})
    command = runtime.get("command")
    args = runtime.get("args", [])
    transport = runtime.get("transport", "stdio")
    env_status = _env_status(server.get("auth", {}).get("env_refs", []))
    binary_status = "SKIPPED"
    initialize_status = "NOT_PROVED"
    tools_list_status = "NOT_PROVED"
    domain_probe_status = "NOT_PROVED"
    exit_code = None
    error = None
    if execute and command:
        try:
            runtime_env = os.environ.copy()
            runtime_env.update({key: str(value) for key, value in runtime.get("env", {}).items()})
            probe_name = server.get("probes", {}).get("domain_probe")
            if transport == "stdio" and server.get("probes", {}).get("initialize") and server.get("probes", {}).get("tools_list"):
                stdio = _run_jsonrpc_stdio(command, args, timeout, runtime_env)
                binary_status = "AVAILABLE" if stdio["initialize"] == "PASS" or stdio["tools_list"] == "PASS" else "ERROR"
                initialize_status = stdio["initialize"]
                tools_list_status = stdio["tools_list"]
                error = stdio["error"]
                if probe_name in {"browser_session_probe", "sap_gui_session_probe"}:
                    domain = _run_named_domain_probe(probe_name, timeout)
                    domain_probe_status = domain["domain_probe"]
                    error = domain["error"] or error
                elif probe_name == "help_command":
                    domain_probe_status = "DEGRADED"
                    error = error or "Help command proves install only, not domain readiness"
                elif probe_name == "jsonrpc_tools":
                    domain_probe_status = "PASS" if initialize_status == "PASS" and tools_list_status == "PASS" else "NOT_PROVED"
                else:
                    domain_probe_status = "NOT_PROVED"
            else:
                command_probe = _run_cli_domain_probe(command, args, probe_name or "command", timeout)
                exit_code = command_probe["exit_code"]
                binary_status = command_probe["binary"]
                initialize_status = "NOT_APPLICABLE"
                tools_list_status = "NOT_APPLICABLE"
                domain_probe_status = command_probe["domain_probe"]
                error = command_probe["error"]
        except FileNotFoundError:
            binary_status = "NOT_INSTALLED"
            error = f"Command not found: {command}"
        except subprocess.TimeoutExpired:
            binary_status = "TIMEOUT"
            error = "Probe timed out"
    ready = (
        env_status in ("ALL_SET", "NO_ENV_NEEDED")
        and binary_status == "AVAILABLE"
        and domain_probe_status == "PASS"
        and (
            (initialize_status == "PASS" and tools_list_status == "PASS")
            or (initialize_status == "NOT_APPLICABLE" and tools_list_status == "NOT_APPLICABLE")
        )
    )
    status = "READY" if ready else "UNAVAILABLE"
    if not execute and env_status in ("ALL_SET", "NO_ENV_NEEDED"):
        status = "DEGRADED"
        error = "Domain probe not executed; SKIPPED is not READY"
    elif execute and domain_probe_status == "DEGRADED":
        status = "DEGRADED"
    return {
        "server_id": server_id,
        "status": status,
        "checked_at": now_iso(),
        "expires_at": (datetime.utcnow() + timedelta(minutes=15)).replace(microsecond=0).isoformat() + "Z",
        "checks": {
            "env": env_status,
            "binary": binary_status,
            "initialize": initialize_status,
            "tools_list": tools_list_status,
            "domain_probe": domain_probe_status,
        },
        "capabilities_ready": server.get("capabilities", []) if ready else [],
        "exit_code": exit_code,
        "error_code": None if ready else "NOT_READY",
        "error": error,
    }


def validate_catalog() -> dict[str, Any]:
    errors: list[str] = []
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
        configured_ids = set(load_json(mcp_config_path).get("mcpServers", {}))
        candidate_ids = {item["id"] for item in load_json(candidates_path).get("candidates", [])}
        unmanaged = configured_ids - set(servers) - candidate_ids
        if unmanaged:
            errors.append(f"MCP config has unmanaged servers: {sorted(unmanaged)}")
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
    }
