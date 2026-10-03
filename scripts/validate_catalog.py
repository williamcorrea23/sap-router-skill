#!/usr/bin/env python3
"""Validate skill/MCP/profile catalog consistency.

Runs two independent validators and merges their findings:

1. validate()  - capability reachability, approval gating and catalogue /
   registry reconciliation (defined in this module).
2. sap_router_core.registry.validate_catalog() - registry schema, route and
   profile integrity, bundled-source locking.

Both always run. Neither can mask the other: a failure in either fails the
whole check. Exit code is 1 when any error is reported.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from harness_contracts import load_contracts

ROOT = Path(__file__).resolve().parent.parent
REGISTRIES = ROOT / ".agents" / "registries"
REGISTRY = REGISTRIES / "mcp-capabilities.json"
MCP_CONFIG = ROOT / ".mcp.json"
SKILLS_DIR = ROOT / ".agents" / "skills"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if(path: Path, default: dict) -> dict:
    return load_json(path) if path.exists() else default


def skill_names() -> set[str]:
    return {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}


def validate_mcp_target_profiles(root: Path | str = ROOT) -> list[str]:
    """Keep selected, not-yet-provisioned MCP trials explicitly non-routable."""
    base = Path(root)
    registries = base / ".agents" / "registries"
    errors: list[str] = []
    try:
        profiles = json.loads((registries / "mcp-target-profiles.json").read_text(encoding="utf-8"))
        candidate_registry = json.loads((registries / "mcp-candidates.json").read_text(encoding="utf-8"))
        mcp_registry = json.loads((registries / "mcps.json").read_text(encoding="utf-8"))
        client_config = json.loads((base / ".mcp.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        return [f"MCP target profiles: registry could not be read ({type(exc).__name__})"]

    if profiles.get("schema_version") != 1 or not isinstance(profiles.get("profiles"), list):
        return ["MCP target profiles: invalid schema version or profiles list"]

    candidates = {item.get("id"): item for item in candidate_registry.get("candidates", [])}
    registered_servers = {item.get("id") for item in mcp_registry.get("servers", [])}
    active_servers = set(client_config.get("mcpServers", {}))
    expected_abapilot_tools = {
        "sap_read_code",
        "sap_read_includes",
        "sap_read_object_details",
        "sap_read_object_info",
        "sap_read_table_structure",
        "sap_check_type_exists",
        "sap_read_domain_values",
        "sap_read_field_domain_values",
        "sap_read_foreign_keys",
        "sap_read_where_used",
        "sap_get_enhancements",
        "sap_list_package_objects",
        "sap_syntax_check",
    }
    forbidden_abapilot_tools = {
        "sap_write_code",
        "sap_write_code_safe",
        "sap_patch_code",
        "sap_run_program",
        "sap_run_transaction",
        "sap_save_variant",
        "sap_call_function",
        "sap_write_translations",
        "sap_translate",
        "sap_upload_note_v2",
    }
    seen: set[str] = set()

    for profile in profiles["profiles"]:
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not profile_id or profile_id in seen:
            errors.append("MCP target profiles: missing or duplicate profile id")
            continue
        seen.add(profile_id)
        candidate_id = profile.get("candidate_id")
        candidate = candidates.get(candidate_id)
        if not candidate or candidate.get("status") != "disabled_candidate":
            errors.append(f"MCP target profile {profile_id}: candidate is missing or not disabled")
        if profile.get("status") != "blocked":
            errors.append(f"MCP target profile {profile_id}: unprovisioned target must remain blocked")
        if candidate_id in registered_servers or candidate_id in active_servers:
            errors.append(f"MCP target profile {profile_id}: disabled candidate is wired as a live server")

        source = profile.get("source", {})
        if candidate and source.get("revision") != candidate.get("revision"):
            errors.append(f"MCP target profile {profile_id}: source revision differs from candidate pin")
        if source.get("license") != "MIT" or source.get("npm_package") != "abapilot@1.0.6":
            errors.append(f"MCP target profile {profile_id}: unreviewed ABAPilot package or license")
        artifact_hash = source.get("npm_tarball_sha256", "")
        if not isinstance(artifact_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", artifact_hash):
            errors.append(f"MCP target profile {profile_id}: invalid npm artifact SHA-256")

        target = profile.get("target", {})
        if target.get("environment") != "DEV" or target.get("system_id") is not None:
            errors.append(f"MCP target profile {profile_id}: exact DEV system identity is not established")

        runtime = profile.get("runtime", {})
        if (runtime.get("transport") != "stdio" or runtime.get("command") is not None or
                runtime.get("args") != [] or runtime.get("installed") is not False or
                runtime.get("runtime_fetch") is not False or runtime.get("runtime_execution") is not False):
            errors.append(f"MCP target profile {profile_id}: runtime must remain unavailable and non-executable")

        auth = profile.get("auth", {})
        refs = [auth.get(key) for key in (
            "url_env_ref", "username_env_ref", "password_env_ref", "token_env_ref", "tls_insecure_env_ref"
        )]
        refs.append(auth.get("client_env_ref", target.get("client_env_ref")))
        if any(not isinstance(ref, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{1,63}", ref) for ref in refs):
            errors.append(f"MCP target profile {profile_id}: auth fields must contain environment variable names only")
        if auth.get("https_required") is not True or auth.get("tls_insecure_allowed") is not False:
            errors.append(f"MCP target profile {profile_id}: TLS verification must remain mandatory")

        tool_policy = profile.get("tool_policy", {})
        allowlist = tool_policy.get("allowlist", [])
        if (tool_policy.get("default_deny") is not True or
                tool_policy.get("server_side_authorization_required") is not True or
                not isinstance(allowlist, list) or set(allowlist) != expected_abapilot_tools):
            errors.append(f"MCP target profile {profile_id}: ABAPilot tool allowlist is incomplete or unsafe")
        if forbidden_abapilot_tools.intersection(allowlist):
            errors.append(f"MCP target profile {profile_id}: mutating or executing ABAPilot tool is allowlisted")

        blockers = profile.get("blockers")
        if not isinstance(blockers, list) or not blockers or any(not isinstance(item, str) or not item.strip() for item in blockers):
            errors.append(f"MCP target profile {profile_id}: blocked state requires concrete blockers")
        if profile.get("live_sap_validation") != "NOT_RUN":
            errors.append(f"MCP target profile {profile_id}: unavailable SAP evidence cannot be marked passed")

    return errors


def validate_skill_source_imports(root: Path | str = ROOT) -> list[str]:
    """Check imported skill provenance without treating skill text as a runtime."""
    base = Path(root)
    registry_path = base / ".agents" / "registries" / "skill-imports.json"
    if not registry_path.exists():
        return []
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        return [f"skill imports: registry could not be read ({type(exc).__name__})"]

    if registry.get("schema_version") != 1 or not isinstance(registry.get("imports"), list):
        return ["skill imports: invalid schema version or imports list"]

    errors: list[str] = []
    seen: set[str] = set()
    for item in registry["imports"]:
        skill_id = item.get("id")
        if not isinstance(skill_id, str) or not skill_id or skill_id in seen:
            errors.append("skill imports: missing or duplicate skill id")
            continue
        seen.add(skill_id)
        revision = item.get("revision", "")
        content_hash = item.get("source_skill_sha256", "")
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            errors.append(f"skill import {skill_id}: source revision is not immutable")
        if not isinstance(content_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", content_hash):
            errors.append(f"skill import {skill_id}: source skill hash is invalid")
        if item.get("kind") != "skill_only" or item.get("license") not in {"MIT", "Apache-2.0"}:
            errors.append(f"skill import {skill_id}: unsupported import kind or unverified license")
        if item.get("cli_runtime_installed") is not False or item.get("mcp_server_registered") is not False:
            errors.append(f"skill import {skill_id}: documentation import cannot imply installed runtime or MCP")

        skill_path = base / item.get("canonical_skill_path", "")
        license_path = base / item.get("license_path", "")
        if not skill_path.is_file() or not license_path.is_file():
            errors.append(f"skill import {skill_id}: canonical skill or license file missing")
            continue
        content = skill_path.read_text(encoding="utf-8")
        for value in (revision, content_hash):
            if value not in content:
                errors.append(f"skill import {skill_id}: canonical front matter does not match source lock")
                break
        if skill_path.parent.name != skill_id:
            errors.append(f"skill import {skill_id}: canonical path does not match skill id")

    return errors


def validate_harness_contracts(root: Path | str = ROOT) -> list[str]:
    """Validate every reviewed harness tool contract against canonical registries."""
    base = Path(root)
    registries = base / ".agents" / "registries"
    errors: list[str] = []

    def read(name: str) -> dict:
        return json.loads((registries / name).read_text(encoding="utf-8"))

    try:
        contract_registry = read("harness-tool-contracts.json")
        policy = contract_registry.get("policy")
        if (not isinstance(policy, dict) or policy.get("runtime_fetch") is not False or
                policy.get("requires_reviewed_schema") is not True or
                not isinstance(policy.get("real_effects"), list)):
            return ["harness contracts: invalid or unsafe registry policy"]

        allowed_effects = set(policy["real_effects"])
        if not allowed_effects <= {"read", "mutating", "destructive"}:
            errors.append("harness contracts: policy contains an unknown effect")

        contracts = load_contracts(base)
        capabilities = {item["id"]: item for item in read("capabilities.json")["capabilities"]}
        servers = {item["id"]: item for item in read("mcps.json")["servers"]}
        mcp_specs = read("mcp-capabilities.json").get("capabilities", {})
        profiles = [json.loads(path.read_text(encoding="utf-8"))
                    for path in (base / ".agents" / "profiles").glob("*.json")]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"harness contracts: registry could not be validated ({type(exc).__name__})"]

    seen_tools: set[tuple[str, str, str]] = set()
    for contract in contracts:
        contract_id = contract["id"]
        key = (contract["server"], contract["capability"], contract["tool"])
        if key in seen_tools:
            errors.append(f"harness contract {contract_id}: duplicate server/capability/tool binding")
        seen_tools.add(key)

        effect = contract["effect"]
        if effect not in allowed_effects:
            errors.append(f"harness contract {contract_id}: effect is forbidden by registry policy")

        capability = capabilities.get(contract["capability"])
        if not capability:
            errors.append(f"harness contract {contract_id}: unknown capability")
            continue
        if capability.get("effect") != effect:
            errors.append(f"harness contract {contract_id}: effect differs from canonical capability")

        server = servers.get(contract["server"])
        if not server or server.get("status") != "enabled":
            errors.append(f"harness contract {contract_id}: server is not enabled")
            continue
        if contract["capability"] not in server.get("capabilities", []):
            errors.append(f"harness contract {contract_id}: server does not advertise capability")

        spec = mcp_specs.get(contract["capability"])
        if not isinstance(spec, dict):
            errors.append(f"harness contract {contract_id}: canonical MCP capability route missing")
        else:
            route_servers = [spec.get("primary"), *spec.get("fallbacks", [])]
            if contract["server"] not in route_servers:
                errors.append(f"harness contract {contract_id}: server outside canonical capability route")
            if bool(spec.get("mutation")) != (effect != "read"):
                errors.append(f"harness contract {contract_id}: canonical mutation effect mismatch")
            if effect != "read" and spec.get("requires_approval") is not True:
                errors.append(f"harness contract {contract_id}: mutation lacks approval policy")

        permission_bucket = "allow" if effect == "read" else "gated"
        eligible = [profile for profile in profiles
                    if contract["capability"] in profile.get("capabilities", {}).get(permission_bucket, [])
                    and contract["capability"] not in profile.get("capabilities", {}).get("deny", [])]
        if not eligible:
            errors.append(f"harness contract {contract_id}: no profile grants the capability effect")

    return errors


def validate(strict: bool = False) -> dict:
    """Capability reachability plus catalogue reconciliation.

    A capability is reachable only when at least one of its candidate servers
    is present in .mcp.json mcpServers. A server listed only under
    plannedServers is known but cannot be launched, so it never counts toward
    reachability - that is what fail-closed means here.
    """
    errors: list[str] = []
    warnings: list[str] = []
    gaps: list[str] = []

    errors.extend(validate_mcp_target_profiles(ROOT))
    errors.extend(validate_skill_source_imports(ROOT))
    registry = load_json(REGISTRY)
    mcp = load_json(MCP_CONFIG)
    configured = set(mcp.get("mcpServers", {}))
    planned = set(mcp.get("plannedServers", {}))
    skills = skill_names()

    if registry.get("default_policy") != "fail_closed":
        errors.append("Registry default_policy must be fail_closed.")

    for cap, spec in registry.get("capabilities", {}).items():
        primary = spec.get("primary")
        candidates = ([primary] if primary else []) + list(spec.get("fallbacks", []))
        if not primary and spec.get("status") != "planned":
            errors.append("{0}: missing primary.".format(cap))

        reachable = []
        for server in candidates:
            if not server or server.startswith("plugin:"):
                continue
            if server in configured:
                reachable.append(server)
            elif server in planned:
                warnings.append(
                    "{0}: server {1} is planned only - not launchable, excluded from routing.".format(cap, server)
                )
            else:
                errors.append(
                    "{0}: server {1} is in neither mcpServers nor plannedServers of .mcp.json.".format(cap, server)
                )

        if not reachable:
            msg = "{0}: no reachable provider - every candidate is planned or unknown.".format(cap)
            if spec.get("status") == "planned":
                gaps.append(msg + " Declared planned; fail-closed at runtime.")
            else:
                errors.append(msg)

        if spec.get("mutation") and not spec.get("requires_approval"):
            errors.append("{0}: mutating capability must require approval.".format(cap))

    for profile, spec in registry.get("profiles", {}).items():
        for skill in spec.get("skills", []):
            if skill not in skills:
                warnings.append("{0}: skill {1} missing from .agents/skills.".format(profile, skill))
        for cap in spec.get("capabilities", []):
            if cap not in registry.get("capabilities", {}):
                errors.append("{0}: capability {1} missing.".format(profile, cap))

    errors.extend(reconcile_catalogue())
    if strict:
        errors.extend(validate_harness_contracts(ROOT))

    return {
        "status": "FAIL" if errors else "PASS",
        "skills": len(skills),
        "mcp_servers": len(configured),
        "planned_servers": len(planned),
        "capabilities": len(registry.get("capabilities", {})),
        "profiles": len(registry.get("profiles", {})),
        "errors": errors,
        "warnings": warnings,
        "gaps": gaps,
    }


def reconcile_catalogue() -> list[str]:
    """Every catalogued MCP source must resolve to a registry record.

    Guards against the failure this check exists for: a repository listed in
    bundled-sources.json that appears nowhere in mcps.json or
    mcp-candidates.json, so it reads as integrated while being unreachable
    and unreviewed.
    """
    errors: list[str] = []
    sources = load_json_if(REGISTRIES / "bundled-sources.json", {"sources": []}).get("sources", [])
    server_records = load_json_if(REGISTRIES / "mcps.json", {"servers": []}).get("servers", [])
    candidate_records = load_json_if(REGISTRIES / "mcp-candidates.json", {"candidates": []}).get("candidates", [])
    servers = {s["id"] for s in server_records}
    candidates = {c["id"] for c in candidate_records}
    known = servers | candidates

    for source in sources:
        if source.get("kind") != "mcp":
            continue
        sid = source["id"]
        wired = source.get("wired_as")
        if sid in known:
            continue
        if wired and wired in known:
            continue
        if wired:
            errors.append(
                "bundled source {0}: wired_as '{1}' is not a registered server or candidate.".format(sid, wired)
            )
        else:
            errors.append(
                "bundled source {0}: kind=mcp but absent from mcps.json and mcp-candidates.json "
                "(catalogued without being wired or reviewed).".format(sid)
            )

    for record in candidate_records:
        if record.get("status") == "disabled_candidate" and not record.get("reason"):
            errors.append("candidate {0}: disabled candidates must state a reason.".format(record["id"]))

    for server in server_records:
        if server.get("status") != "enabled":
            continue
        if not server.get("runtime", {}).get("command"):
            errors.append("server {0}: enabled but has no runtime command.".format(server["id"]))

    return errors


def run_registry_validator() -> dict:
    sys.path.insert(0, str(ROOT / "python"))
    try:
        from sap_router_core.registry import validate_catalog as registry_validate
    except Exception as exc:  # noqa: BLE001 - surfaced, never swallowed
        return {"status": "FAIL", "errors": ["registry validator unavailable: {0}".format(exc)], "warnings": []}
    try:
        return registry_validate()
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAIL", "errors": ["registry validator raised: {0}".format(exc)], "warnings": []}


def merge(local: dict, registry: dict) -> dict:
    merged = dict(local)
    merged["errors"] = list(local.get("errors", [])) + [
        "[registry] {0}".format(m) for m in registry.get("errors", [])
    ]
    merged["warnings"] = list(local.get("warnings", [])) + [
        "[registry] {0}".format(m) for m in registry.get("warnings", [])
    ]
    merged["registry_counts"] = registry.get("counts", {})
    merged["status"] = "FAIL" if merged["errors"] else "PASS"
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SAP Router catalog.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also validates reviewed harness tool contracts against canonical registries.",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Write validation JSON to this path.")
    args = parser.parse_args()

    result = merge(validate(strict=args.strict), run_registry_validator())

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            "Catalog: {status} skills={skills} mcps={mcps} planned={planned} "
            "capabilities={caps} profiles={profiles}".format(
                status=result["status"],
                skills=result.get("skills", "n/a"),
                mcps=result.get("mcp_servers", "n/a"),
                planned=result.get("planned_servers", "n/a"),
                caps=result.get("capabilities", "n/a"),
                profiles=result.get("profiles", "n/a"),
            )
        )
        for key in ("errors", "warnings", "gaps"):
            for msg in result.get(key, []):
                print("  {0}: {1}".format(key[:-1].upper(), msg))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
