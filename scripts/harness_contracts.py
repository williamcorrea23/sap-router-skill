"""Reviewed MCP contracts and deterministic argument/result verification.

Contracts describe an observed tool schema, canonical capability/effect, and
concrete response fields. Loading this module never starts an MCP or calls SAP.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_JSON_BYTES = 1_048_576
MAX_DEPTH = 20


def schema_hash(schema: dict) -> str:
    return hashlib.sha256(json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def load_contracts(root: Path | str | None = None) -> list[dict]:
    path = Path(root or ROOT) / ".agents" / "registries" / "harness-tool-contracts.json"
    raw = path.read_bytes()
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("contract registry exceeds size limit")
    registry = json.loads(raw)
    if registry.get("schema_version") != 1 or not isinstance(registry.get("contracts"), list):
        raise ValueError("invalid harness contract registry")
    contracts = registry["contracts"]
    seen = set()
    for item in contracts:
        _validate_shape(item)
        if item["id"] in seen:
            raise ValueError("duplicate harness contract id")
        seen.add(item["id"])
    return contracts


def _validate_shape(contract: dict) -> None:
    if not isinstance(contract, dict) or contract.get("status") != "reviewed":
        raise ValueError("tool contract is not reviewed")
    for key in ("id", "capability", "server", "tool"):
        if not isinstance(contract.get(key), str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,160}", contract[key]):
            raise ValueError(f"invalid contract {key}")
    if contract.get("effect") not in {"read", "mutating", "destructive"}:
        raise ValueError("invalid contract effect")
    if not isinstance(contract.get("input_schema"), dict):
        raise ValueError("contract input schema missing")
    if contract.get("schema_sha256") != schema_hash(contract["input_schema"]):
        raise ValueError("contract schema hash mismatch")
    if not isinstance(contract.get("result_assertions"), list) or not contract["result_assertions"]:
        raise ValueError("contract requires concrete result assertions")
    if contract["effect"] != "read" and contract.get("approval_mode") not in {"broker-only", "server-broker"}:
        raise ValueError("mutating contract requires explicit approval mode")


def validate_contract(contract: dict, capability: dict | str, server: dict | str, profile: dict) -> None:
    _validate_shape(contract)
    if isinstance(capability, str) or isinstance(server, str):
        # String identities still resolve through canonical registries; they
        # cannot substitute for the effect/status checks.
        if isinstance(capability, str):
            items = json.loads((ROOT / ".agents/registries/capabilities.json").read_text(encoding="utf-8"))["capabilities"]
            capability = next((item for item in items if item.get("id") == capability), {})
        if isinstance(server, str):
            items = json.loads((ROOT / ".agents/registries/mcps.json").read_text(encoding="utf-8"))["servers"]
            server = next((item for item in items if item.get("id") == server), {})
    if capability.get("id") != contract["capability"] or capability.get("effect") != contract["effect"]:
        raise ValueError("contract capability/effect does not match canonical capability")
    if server.get("id") != contract["server"] or server.get("status") != "enabled":
        raise ValueError("contract server is not enabled")
    if contract["capability"] not in server.get("capabilities", []):
        raise ValueError("server does not declare the contract capability")
    permissions = profile.get("capabilities", {})
    cap = contract["capability"]
    if cap in permissions.get("deny", []):
        raise ValueError("profile denies contract capability")
    group = "allow" if contract["effect"] == "read" else "gated"
    if cap not in permissions.get(group, []):
        raise ValueError(f"profile does not {group} contract capability")


def validate_arguments(schema: dict, args: Any) -> None:
    if len(json.dumps(args, ensure_ascii=True, allow_nan=False).encode()) > MAX_JSON_BYTES:
        raise ValueError("tool arguments exceed size limit")
    _validate_value(schema, args, "$", 0)


def _validate_value(schema: dict, value: Any, path: str, depth: int) -> None:
    if depth > MAX_DEPTH or not isinstance(schema, dict):
        raise ValueError(f"{path}: invalid or overly nested schema")
    unsupported = set(schema) - {"type", "properties", "required", "additionalProperties", "enum", "const", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "minLength", "maxLength", "minItems", "maxItems", "items", "pattern", "description", "title", "default", "examples", "$schema", "format"}
    if unsupported:
        raise ValueError(f"{path}: unsupported schema keywords")
    expected = schema.get("type")
    checks = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list), "string": lambda x: isinstance(x, str), "integer": lambda x: isinstance(x, int) and not isinstance(x, bool), "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool), "boolean": lambda x: isinstance(x, bool), "null": lambda x: x is None}
    if expected not in checks or not checks[expected](value):
        raise ValueError(f"{path}: expected {expected}")
    if "enum" in schema and not any(type(value) is type(item) and value == item for item in schema["enum"]):
        raise ValueError(f"{path}: value outside enum")
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        raise ValueError(f"{path}: value differs from const")
    if expected == "object":
        properties = schema.get("properties", {})
        if not isinstance(properties, dict) or not isinstance(schema.get("required", []), list):
            raise ValueError(f"{path}: invalid object schema")
        for key in schema.get("required", []):
            if key not in value:
                raise ValueError(f"{path}: required field {key} missing")
        for key, child in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path}: object keys must be strings")
            if key in properties:
                _validate_value(properties[key], child, f"{path}.{key}", depth + 1)
            elif isinstance(schema.get("additionalProperties"), dict):
                _validate_value(schema["additionalProperties"], child, f"{path}.{key}", depth + 1)
            elif schema.get("additionalProperties", True) is False:
                raise ValueError(f"{path}: unexpected field {key}")
    elif expected == "array":
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", 10_000):
            raise ValueError(f"{path}: array length outside bounds")
        if "items" in schema:
            for i, child in enumerate(value):
                _validate_value(schema["items"], child, f"{path}[{i}]", depth + 1)
    elif expected == "string":
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", 25_000):
            raise ValueError(f"{path}: string length outside bounds")
        if "pattern" in schema:
            # Arbitrary regex contracts are not part of the reviewed v1 dialect.
            raise ValueError(f"{path}: pattern schemas require a reviewed validator")
        if schema.get("format") not in (None, ""):
            raise ValueError(f"{path}: format schemas require a reviewed validator")
    elif expected in {"number", "integer"}:
        if value < schema.get("minimum", float("-inf")) or value > schema.get("maximum", float("inf")):
            raise ValueError(f"{path}: number outside bounds")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            raise ValueError(f"{path}: number outside exclusive bounds")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            raise ValueError(f"{path}: number outside exclusive bounds")


def _field(payload: Any, path: str) -> Any:
    value = payload
    for name in path.split("."):
        if not isinstance(value, dict) or name not in value:
            raise ValueError(f"required result field missing: {path}")
        value = value[name]
    return value


def _payload(result: dict) -> dict:
    if not isinstance(result, dict) or result.get("isError") is True:
        raise ValueError("MCP reported tool error")
    payload = result.get("structuredContent")
    if payload is None:
        texts = [item.get("text", "") for item in result.get("content", []) if isinstance(item, dict) and item.get("type") == "text"]
        raw = "\n".join(texts)
        if len(raw.encode()) > MAX_JSON_BYTES:
            raise ValueError("result exceeds verification size limit")
        payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("tool result is not a structured object")
    if payload.get("status") in {"ERROR", "FAIL", "FAILED", "BLOCKED", "UNAVAILABLE"}:
        raise ValueError("tool result reports failure")
    if payload.get("exit_code", 0) != 0:
        raise ValueError("tool process did not succeed")
    return payload


def verify_result(contract: dict, result: dict) -> tuple[bool, str]:
    """Return field evidence only; a status/exit code alone cannot verify a read."""
    try:
        _validate_shape(contract)
        payload = _payload(result)
        verified = []
        for assertion in contract["result_assertions"]:
            if not isinstance(assertion, dict) or not isinstance(assertion.get("path"), str):
                raise ValueError("invalid result assertion")
            allowed = {"path", "type", "equals", "one_of", "minimum", "maximum", "nonempty", "length_equals", "odata_json"}
            if set(assertion) - allowed or set(assertion) == {"path"}:
                raise ValueError("result assertion has no supported predicate")
            value = _field(payload, assertion["path"])
            if "type" in assertion:
                _validate_value({"type": assertion["type"]}, value, assertion["path"], 0)
            if "equals" in assertion and (type(value) is not type(assertion["equals"]) or value != assertion["equals"]):
                raise ValueError(f"result field differs: {assertion['path']}")
            if "one_of" in assertion and value not in assertion["one_of"]:
                raise ValueError(f"result field outside allowed values: {assertion['path']}")
            if "minimum" in assertion and (not isinstance(value, (float, int)) or isinstance(value, bool) or value < assertion["minimum"]):
                raise ValueError(f"result field below bound: {assertion['path']}")
            if "maximum" in assertion and (not isinstance(value, (float, int)) or isinstance(value, bool) or value > assertion["maximum"]):
                raise ValueError(f"result field above bound: {assertion['path']}")
            if assertion.get("nonempty") and not value:
                raise ValueError(f"empty result field: {assertion['path']}")
            if "length_equals" in assertion:
                collection = _field(payload, assertion["length_equals"])
                if not isinstance(collection, list) or isinstance(value, bool) or value != len(collection):
                    raise ValueError(f"result count differs from collection: {assertion['path']}")
            if assertion.get("odata_json"):
                decoded = json.loads(value)
                data = decoded.get("d", decoded) if isinstance(decoded, dict) else None
                concrete = isinstance(data, dict) and (isinstance(data.get("results", data.get("value")), list) or any(isinstance(data.get(key), str) and data[key] for key in ("Id", "Name")))
                if not concrete:
                    raise ValueError("APIM result lacks OData proxy fields")
            verified.append(assertion["path"])
        return True, "verified fields: " + ", ".join(verified)
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
        return False, str(exc)
