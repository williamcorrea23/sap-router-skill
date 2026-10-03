from __future__ import annotations

import json
import os
import queue
import re
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


def validate_harness_candidates(servers: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    path = REGISTRIES / "harness-candidates.json"
    if not path.exists():
        return ["harness candidates: registry is missing"]
    data = load_json(path)
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        return ["harness candidates: schema_version must be 1"]
    policy = data.get("policy", {})
    if not isinstance(policy, dict):
        return ["harness candidates: invalid policy"]
    for field, expected in (("status", "disabled_candidate"), ("runtime_fetch", False),
                            ("runtime_execution", False)):
        if (expected is False and policy.get(field) is not False) or (expected is not False and policy.get(field) != expected):
            errors.append(f"harness candidates: policy {field} must be {expected}")
    promotion = policy.get("promotion_requires", [])
    required_review = {"license_review", "security_review", "tests", "explicit_registry_change"}
    if not isinstance(promotion, list) or not all(isinstance(item, str) for item in promotion) or not required_review.issubset(promotion):
        errors.append("harness candidates: promotion requires license/security review, tests and explicit registry change")
    candidates = data.get("candidates", [])
    if not isinstance(candidates, list):
        return errors + ["harness candidates: candidates must be a list"]
    if not candidates:
        errors.append("harness candidates: no audited candidate records")
    seen: set[str] = set()
    enabled = {sid for sid, server in servers.items() if server.get("status") == "enabled"}
    def normalize_repository(value: Any) -> str:
        return value.rstrip("/").removesuffix(".git").casefold() if isinstance(value, str) else ""
    enabled_repositories = {normalize_repository(server.get("source", {}).get("repository")) for server in servers.values()
                            if server.get("status") == "enabled"}
    config_path = ROOT / ".mcp.json"
    configured = set(load_json(config_path).get("mcpServers", {})) if config_path.exists() else set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("harness candidate: record must be an object")
            continue
        sid = candidate.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", sid):
            errors.append("harness candidate: id must be a nonempty canonical identifier")
            sid = "invalid-id"
        elif sid in seen:
            errors.append(f"harness candidate {sid}: duplicate id")
        seen.add(sid)
        revision = candidate.get("revision", "")
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            errors.append(f"harness candidate {sid}: revision must be a full lowercase SHA40")
        repository = candidate.get("repository", "")
        if not isinstance(repository, str) or not re.fullmatch(r"https://github\.com/[^/\s]+/[^/\s]+", repository):
            errors.append(f"harness candidate {sid}: repository must be a GitHub repository URL")
        for field in ("license", "license_evidence", "utility", "kind"):
            if not isinstance(candidate.get(field), str) or not candidate[field].strip():
                errors.append(f"harness candidate {sid}: {field} must state audited evidence or an explicit unresolved value")
        if not isinstance(candidate.get("license"), str) or candidate.get("license") not in {"MIT", "Apache-2.0", "unverified", "absent"}:
            errors.append(f"harness candidate {sid}: license must be reviewed SPDX metadata or explicitly unverified/absent")
        for field, expected in (("status", "disabled_candidate"), ("runtime_fetch", False),
                                ("runtime_execution", False)):
            if (expected is False and candidate.get(field) is not False) or (expected is not False and candidate.get(field) != expected):
                errors.append(f"harness candidate {sid}: {field} must be {expected}")
        blockers = candidate.get("blockers")
        if not isinstance(blockers, list) or not blockers or not all(isinstance(item, str) and item.strip() for item in blockers):
            errors.append(f"harness candidate {sid}: blockers must record pending review")
        if sid in enabled or sid in configured or normalize_repository(repository) in enabled_repositories:
            errors.append(f"harness candidate {sid}: disabled candidate cannot be an enabled MCP")
    return errors


def validate_execution_protocol(profile_id: str, profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = f"profile {profile_id}: execution_protocols"
    protocol = profile.get("execution_protocols")
    if not isinstance(protocol, dict) or type(protocol.get("schema_version")) is not int or protocol.get("schema_version") != 1:
        return [f"{prefix} schema_version must be 1"]
    skills = protocol.get("required_skills", [])
    required_skills = {"karpathy-guidelines", "loop-specification", "verification-loop"}
    if not isinstance(skills, list) or not all(isinstance(skill, str) for skill in skills) or not required_skills.issubset(skills):
        errors.append(f"{prefix} must require Karpathy, loop specification and verification loop")
    else:
        for skill in skills:
            if not (AGENTS / "skills" / skill / "SKILL.md").is_file():
                errors.append(f"{prefix} references missing skill {skill}")
    loop = protocol.get("loop", {})
    verification = protocol.get("verification", {})
    if not isinstance(loop, dict) or not isinstance(verification, dict):
        return errors + [f"{prefix} loop and verification must be objects"]
    for field, ceiling in (("max_iterations", 8), ("max_seconds", 900),
                           ("call_timeout_seconds", 120), ("max_stagnant_iterations", 3)):
        value = loop.get(field)
        if type(value) is not int or not 0 < value <= ceiling:
            errors.append(f"{prefix} {field} must be an integer in 1..{ceiling}")
    if type(loop.get("max_iterations")) is int and type(loop.get("max_stagnant_iterations")) is int:
        if loop["max_stagnant_iterations"] > loop["max_iterations"]:
            errors.append(f"{prefix} stagnation limit exceeds iteration limit")
    if type(loop.get("max_seconds")) is int and type(loop.get("call_timeout_seconds")) is int:
        if loop["call_timeout_seconds"] > loop["max_seconds"]:
            errors.append(f"{prefix} call timeout exceeds total duration")
    def matches_list(value: Any, expected: set[Any]) -> bool:
        return isinstance(value, list) and all(type(item) in (str, int) for item in value) and set(value) == expected
    for field, expected in (("terminal_states", {"Success", "No-Op", "Blocked", "Stalled", "Exhausted"}),
                            ("checkpoint_states", {"PENDING_APPROVAL"})):
        if not matches_list(loop.get(field), expected):
            errors.append(f"{prefix} invalid {field}")
    for field, expected in (("maker_checker", "fresh_process"), ("uncertain_mutation", "reconcile_before_retry"),
                            ("durable_state", "harness_run_state_or_named_local_artifact")):
        if loop.get(field) != expected:
            errors.append(f"{prefix} {field} must be {expected}")
    if not matches_list(verification.get("statuses"), {"PASS", "FAIL", "NOT_RUN"}):
        errors.append(f"{prefix} verification statuses must be PASS/FAIL/NOT_RUN")
    if not matches_list(verification.get("levels"), {1, 2, 3, 4, 5}):
        errors.append(f"{prefix} verification levels must be 1..5")
    evidence = {"check", "status", "verification_level", "command_or_tool", "target", "observed_result", "artifact_or_reference"}
    if not matches_list(verification.get("required_evidence"), evidence):
        errors.append(f"{prefix} verification evidence is incomplete")
    for field, expected in (("not_run_requires", "reason"),
                            ("success_requires", "all_required_checks_pass_with_goal_evidence"),
                            ("live_sap_requires", "field_response_for_requested_target")):
        if verification.get(field) != expected:
            errors.append(f"{prefix} verification {field} must be {expected}")
    return errors


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
        elif cap in capabilities:
            profile_caps = profiles[profile].get("capabilities", {})
            allowed = set(profile_caps.get("allow", [])) | set(profile_caps.get("gated", []))
            if cap not in allowed:
                errors.append(f"route permission missing: profile {profile} does not allow or gate {cap}")
    for profile_id, profile in profiles.items():
        errors.extend(validate_execution_protocol(profile_id, profile))
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
            else:
                effect = capabilities[capability].get("effect", "read")
                expected_mutation = effect != "read"
                if bool(spec.get("mutation", False)) != expected_mutation:
                    errors.append(f"MCP capability {capability}: effect mismatch (canonical {effect})")
                if expected_mutation and not spec.get("requires_approval", False):
                    errors.append(f"MCP capability {capability}: mutating effect requires approval")
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
    errors.extend(validate_harness_candidates(servers))
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
