#!/usr/bin/env python3
"""Local approval broker for plan/commit workflows.

The model can create and inspect plans, but approval is an explicit local state
change. No credential or token is stored here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import getpass
import uuid
from datetime import datetime, timedelta, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / ".sap-router" / "actions"


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def plan_hash(data: dict) -> str:
    signed = {
        key: value for key, value in data.items()
        if key not in {"status", "created_at", "updated_at", "expires_at", "approved_at", "approved_by", "approval_signature", "consumed_at", "rejected_at", "plan_hash"}
    }
    payload = json.dumps(signed, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def json_hash(raw: str) -> str:
    try:
        value = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid-json:{exc.msg}") from exc
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def approval_signature(data: dict) -> str:
    payload = {
        "action_id": data.get("action_id"),
        "plan_hash": data.get("plan_hash"),
        "approved_by": data.get("approved_by"),
        "approved_at": data.get("approved_at"),
        "approval_scope": data.get("approval_scope"),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def plan_file(action_id: str) -> Path:
    return STORE / f"{action_id}.json"


def write_plan(data: dict) -> dict:
    STORE.mkdir(parents=True, exist_ok=True)
    action_id = data.get("action_id") or str(uuid.uuid4())
    expires_at = (datetime.now(UTC) + timedelta(minutes=5)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    data.update({
        "action_id": action_id,
        "status": "PENDING",
        "created_at": now(),
        "updated_at": now(),
        "expires_at": expires_at,
        "approval_scope": "one-time",
        "approval_token_location": "external-broker-only",
        "requested_by": getpass.getuser(),
    })
    data.setdefault("argument_hash", json_hash(data.pop("arguments_json", "{}")))
    data.setdefault("precondition_hash", json_hash(data.pop("preconditions_json", "{}")))
    data["plan_hash"] = plan_hash(data)
    plan_file(action_id).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def read_plan(action_id: str) -> dict:
    path = plan_file(action_id)
    if not path.exists():
        return {"status": "ERROR", "error": "not-found", "action_id": action_id}
    return json.loads(path.read_text(encoding="utf-8"))


def guarded_plan(action_id: str) -> dict:
    data = read_plan(action_id)
    if data.get("status") == "ERROR":
        return data
    if data.get("plan_hash") != plan_hash(data):
        return {"status": "ERROR", "error": "plan-hash-mismatch", "action_id": action_id}
    if data.get("status") == "PENDING" and datetime.now(UTC) > parse_time(data["expires_at"]):
        data["status"] = "EXPIRED"
        data["updated_at"] = now()
        plan_file(action_id).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def set_status(action_id: str, status: str, confirm: str | None = None) -> dict:
    data = guarded_plan(action_id)
    if data.get("status") == "ERROR":
        return data
    if data.get("status") == "CONSUMED":
        return {"status": "ERROR", "error": "approval-already-consumed", "action_id": action_id}
    if data.get("status") == "EXPIRED":
        return {"status": "ERROR", "error": "approval-expired", "action_id": action_id}
    if status == "APPROVED" and data.get("status") != "PENDING":
        return {"status": "ERROR", "error": "approval-not-pending", "action_id": action_id, "current_status": data.get("status")}
    if status == "APPROVED" and data.get("effect") == "destructive" and confirm != data.get("target"):
        return {"status": "ERROR", "error": "strong-confirmation-required", "action_id": action_id}
    data["status"] = status
    data["updated_at"] = now()
    if status == "APPROVED":
        data["approved_at"] = data["updated_at"]
        data["approved_by"] = getpass.getuser()
        data["approval_signature"] = approval_signature(data)
    if status == "REJECTED":
        data["rejected_at"] = data["updated_at"]
    plan_file(action_id).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def consume(
    action_id: str,
    plan_hash_arg: str | None = None,
    argument_hash_arg: str | None = None,
    precondition_hash_arg: str | None = None,
) -> dict:
    data = guarded_plan(action_id)
    if data.get("status") == "ERROR":
        return data
    if data.get("status") != "APPROVED":
        return {"status": "ERROR", "error": "approval-not-approved", "action_id": action_id, "current_status": data.get("status")}
    if data.get("effect") in {"mutating", "destructive"} and not plan_hash_arg:
        return {"status": "ERROR", "error": "plan-hash-required", "action_id": action_id, "plan_hash": data.get("plan_hash")}
    if plan_hash_arg and plan_hash_arg != data.get("plan_hash"):
        return {"status": "ERROR", "error": "plan-hash-confirmation-mismatch", "action_id": action_id}
    if argument_hash_arg and argument_hash_arg != data.get("argument_hash"):
        return {"status": "ERROR", "error": "argument-hash-mismatch", "action_id": action_id}
    if precondition_hash_arg and precondition_hash_arg != data.get("precondition_hash"):
        return {"status": "ERROR", "error": "precondition-hash-mismatch", "action_id": action_id}
    expected_signature = approval_signature(data)
    if data.get("approval_signature") != expected_signature:
        return {"status": "ERROR", "error": "approval-signature-mismatch", "action_id": action_id}
    data["status"] = "CONSUMED"
    data["consumed_at"] = now()
    data["updated_at"] = data["consumed_at"]
    plan_file(action_id).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Local approval broker.")
    sub = parser.add_subparsers(dest="command", required=True)
    plan_p = sub.add_parser("plan")
    plan_p.add_argument("--capability", required=True)
    plan_p.add_argument("--target", default="")
    plan_p.add_argument("--summary", default="")
    plan_p.add_argument("--effect", choices=["read", "mutating", "destructive"], default="mutating")
    plan_p.add_argument("--arguments-json", default="{}")
    plan_p.add_argument("--preconditions-json", default="{}")
    show_p = sub.add_parser("show")
    show_p.add_argument("action_id")
    approve_p = sub.add_parser("approve")
    approve_p.add_argument("action_id")
    approve_p.add_argument("--confirm")
    reject_p = sub.add_parser("reject")
    reject_p.add_argument("action_id")
    consume_p = sub.add_parser("consume")
    consume_p.add_argument("action_id")
    consume_p.add_argument("--plan-hash")
    consume_p.add_argument("--argument-hash")
    consume_p.add_argument("--precondition-hash")
    status_p = sub.add_parser("status")
    status_p.add_argument("action_id")
    args = parser.parse_args()

    if args.command == "plan":
        try:
            result = write_plan({
                "capability": args.capability,
                "target": args.target,
                "summary": args.summary,
                "effect": args.effect,
                "arguments_json": args.arguments_json,
                "preconditions_json": args.preconditions_json,
            })
        except ValueError as exc:
            result = {"status": "ERROR", "error": str(exc)}
    elif args.command == "show":
        result = guarded_plan(args.action_id)
    elif args.command == "approve":
        result = set_status(args.action_id, "APPROVED", args.confirm)
    elif args.command == "reject":
        result = set_status(args.action_id, "REJECTED")
    elif args.command == "consume":
        result = consume(args.action_id, args.plan_hash, args.argument_hash, args.precondition_hash)
    elif args.command == "status":
        plan = guarded_plan(args.action_id)
        result = {"action_id": args.action_id, "status": plan.get("status"), "plan_hash": plan.get("plan_hash")}
    else:
        result = {"status": "ERROR", "error": "unknown-command"}

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") != "ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
