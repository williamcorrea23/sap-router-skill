#!/usr/bin/env python3
"""Offline crew planner for caveman-style parallel SAP work."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, UTC
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREW = ROOT / ".agents" / "crews" / "caveman-crew.json"
CREW_FALLBACK = ROOT / ".agents" / "crews" / "caveman.json"
STORE = ROOT / "scratch" / "crew-plans"


def load_crew() -> dict:
    path = CREW if CREW.exists() else CREW_FALLBACK
    return json.loads(path.read_text(encoding="utf-8"))


def plan_task(task: str) -> dict:
    text = task.lower()
    workers = []
    for worker in load_crew().get("workers", []):
        if any(trigger in text for trigger in worker.get("triggers", [])):
            workers.append(worker["id"])
    if not workers:
        workers = ["cavecrew-investigator"]
    plan_id = str(uuid.uuid4())
    plan = {
        "plan_id": plan_id,
        "task": task,
        "mode": "parallel" if len(workers) > 1 else "single",
        "workers": workers,
        "status": "PLANNED",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    STORE.mkdir(parents=True, exist_ok=True)
    (STORE / f"{plan_id}.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return plan


def read_plan(plan_id: str) -> dict:
    path = STORE / f"{plan_id}.json"
    if not path.exists():
        return {"status": "ERROR", "error": "not-found", "plan_id": plan_id}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan caveman/crew work.")
    sub = parser.add_subparsers(dest="command", required=True)
    plan_p = sub.add_parser("plan")
    plan_p.add_argument("--task", required=True)
    status_p = sub.add_parser("status")
    status_p.add_argument("--plan-id", required=True)
    exec_p = sub.add_parser("execute")
    exec_p.add_argument("--plan-id", required=True)
    args = parser.parse_args()

    if args.command == "plan":
        result = plan_task(args.task)
    elif args.command == "status":
        result = read_plan(args.plan_id)
    elif args.command == "execute":
        result = read_plan(args.plan_id)
        if result.get("status") != "ERROR":
            result["status"] = "READY_FOR_ORCHESTRATOR"
            result["note"] = "Launch listed workers as subagents in one wave."
    else:
        result = {"status": "ERROR", "error": "unknown-command"}
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") != "ERROR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
