#!/usr/bin/env python3
"""UserPromptSubmit hook — re-assert cavecrew delegation on every turn.

The sap-router-skill SKILL.md tells the model to delegate small-scope work to the
cavecrew subagents (Principle -1). A skill is loaded once; its instructions then
compete with everything else in a long session and decay. This hook re-injects the
delegation rule on the turns where it actually applies, so the instruction stays
fresh without costing tokens on turns where it does not.

Single source of truth: the trigger keywords are read from CAVEMAN_DELEGATION in
scripts/sap_router.py. They are NOT duplicated here -- duplicated routing tables are
the failure mode this repository already has too much of.

Reading them by importing sap_router costs ~860ms (module-level YAML + heavy imports),
which is too slow to run on every prompt. Parsing the module with `ast` instead costs
~170ms and never executes it. That result is then cached against the mtime of
sap_router.py, so the steady-state cost is a single small JSON read.

Contract:
  stdin  : JSON with a "prompt" field (Claude Code UserPromptSubmit payload)
  stdout : delegation instruction, injected into the model's context (exit 0)
  exit 0 : always -- a hook failure must never block the user's turn
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTER = ROOT / "scripts" / "sap_router.py"
CACHE = ROOT / ".cavecrew_triggers.json"

# Same precedence as SapRouter._check_caveman_delegation: an edit request that also
# contains a search word must reach the builder, not the investigator.
PRECEDENCE = ("builder", "investigator", "reviewer")


def extract_table() -> dict:
    """Read CAVEMAN_DELEGATION out of sap_router.py without executing the module."""
    tree = ast.parse(ROUTER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", "") == "CAVEMAN_DELEGATION" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    return {}


def load_table() -> dict:
    """Return the trigger table, using the mtime-keyed cache when it is still valid."""
    try:
        stamp = ROUTER.stat().st_mtime_ns
    except OSError:
        return {}

    try:
        cached = json.loads(CACHE.read_text(encoding="utf-8"))
        if cached.get("router_mtime_ns") == stamp:
            return cached["table"]
    except Exception:
        pass

    table = extract_table()
    if table:
        try:
            CACHE.write_text(
                json.dumps({"router_mtime_ns": stamp, "table": table}),
                encoding="utf-8",
            )
        except OSError:
            pass  # cache is an optimisation, never a requirement
    return table


def classify(prompt: str, table: dict) -> tuple[str, str] | None:
    """Return (role, agent_type) for the first matching role, or None."""
    low = prompt.lower()
    for role in PRECEDENCE:
        spec = table.get(role)
        if not spec:
            continue
        if any(kw in low for kw in spec.get("trigger_keywords", [])):
            return role, spec.get("agent_type", "cavecrew-" + role)
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    prompt = (payload.get("prompt") or "").strip()
    if not prompt or not ROUTER.exists():
        return 0

    table = load_table()
    hit = classify(prompt, table)
    if not hit:
        return 0

    role, agent_type = hit
    refusal = ""
    if role == "builder":
        refusal = (
            "\n- Scope cap is 2 files. If the agent returns `REFUSE:`, that is a correct "
            "outcome: take the work back into the main context. Do not re-dispatch it."
        )

    context = (
        "[cavecrew] This request matches the {role} trigger set.\n"
        "If it is genuinely small-scope, delegate it NOW instead of working in the main "
        "context:\n"
        "  Agent(subagent_type=\"{agent}\")\n"
        "- Dispatch before reading or searching -- the subagent does its own lookup.{extra}\n"
        "- If the task is larger than that (spec work, transport, multi-object ABAP), "
        "ignore this and run the normal sap-router-skill flow."
    ).format(role=role, agent=agent_type, extra=refusal)

    json.dump(
        {
            "suppressOutput": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            },
        },
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
