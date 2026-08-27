#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP Harness evaluation suite.

Every scenario exercises code that ships in this repository and asserts an
outcome that a regression would break. Where a property must hold, the
scenario also feeds a deliberately broken input and requires the check to
reject it - a scenario that cannot fail measures nothing.

Offline is the default and is hermetic: no network, no SAP system, no MCP
subprocess. ``--live`` adds the checks that need a real backend; scenarios
report which mode produced their result.
"""

from __future__ import annotations

import importlib
import json
import re
import shutil
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python"))


class Check:
    """Collects named assertions so a scenario reports what failed, not just that it failed."""

    def __init__(self) -> None:
        self.results: list[dict[str, Any]] = []

    def expect(self, name: str, condition: bool, detail: str = "") -> bool:
        self.results.append({"check": name, "passed": bool(condition), "detail": detail})
        return bool(condition)

    def expect_equal(self, name: str, actual: Any, expected: Any) -> bool:
        return self.expect(name, actual == expected, "expected={0!r} actual={1!r}".format(expected, actual))

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r["passed"])

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def failures(self) -> list[str]:
        return ["{0} ({1})".format(r["check"], r["detail"]) if r["detail"] else r["check"]
                for r in self.results if not r["passed"]]

    def score(self) -> float:
        return round(self.passed / self.total, 4) if self.total else 0.0


def _result(scenario: str, check: Check, live: bool, started: float, details: dict[str, Any]) -> dict[str, Any]:
    score = check.score()
    return {
        "scenario": scenario,
        "status": "PASS" if score == 1.0 else "FAIL",
        "score": score,
        "checks_passed": check.passed,
        "checks_total": check.total,
        "failures": check.failures,
        "mode": "live" if live else "offline",
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "details": details,
    }


# ---------------------------------------------------------------------------
# Scenario 1 - the catalog validator must fail closed, and must be able to fail
# ---------------------------------------------------------------------------

CATALOG_FILES = [
    ".mcp.json",
    ".agents/registries/mcp-capabilities.json",
    ".agents/registries/mcps.json",
    ".agents/registries/mcp-candidates.json",
    ".agents/registries/bundled-sources.json",
]


def _catalog_fixture(tmp: Path) -> Path:
    """Copies the files validate() reads into a writable tree."""
    for rel in CATALOG_FILES:
        dest = tmp / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    (tmp / ".agents" / "skills").mkdir(parents=True, exist_ok=True)
    return tmp


def _validate_tree(tree: Path) -> dict[str, Any]:
    """Runs the real validate() against an alternate root."""
    module = importlib.import_module("validate_catalog")
    saved = (module.ROOT, module.REGISTRIES, module.REGISTRY, module.MCP_CONFIG, module.SKILLS_DIR)
    try:
        module.ROOT = tree
        module.REGISTRIES = tree / ".agents" / "registries"
        module.REGISTRY = module.REGISTRIES / "mcp-capabilities.json"
        module.MCP_CONFIG = tree / ".mcp.json"
        module.SKILLS_DIR = tree / ".agents" / "skills"
        return module.validate()
    finally:
        (module.ROOT, module.REGISTRIES, module.REGISTRY, module.MCP_CONFIG, module.SKILLS_DIR) = saved


def eval_catalog_fail_closed(live: bool = False) -> dict[str, Any]:
    """The validator must accept the real catalog and reject broken variants."""
    started = time.perf_counter()
    check = Check()
    details: dict[str, Any] = {}

    baseline = _validate_tree(ROOT)
    details["baseline_errors"] = baseline["errors"]
    check.expect("real catalog validates", not baseline["errors"], "; ".join(baseline["errors"][:3]))

    with tempfile.TemporaryDirectory() as raw:
        tmp = _catalog_fixture(Path(raw))
        caps_path = tmp / ".agents" / "registries" / "mcp-capabilities.json"

        # Mutation A: policy is no longer fail-closed.
        caps = json.loads(caps_path.read_text(encoding="utf-8"))
        caps["default_policy"] = "open"
        caps_path.write_text(json.dumps(caps), encoding="utf-8")
        mutated = _validate_tree(tmp)
        check.expect("rejects default_policy != fail_closed",
                     any("fail_closed" in e for e in mutated["errors"]),
                     str(mutated["errors"][:2]))

        # Mutation B: a capability points at a server nobody declared.
        caps = json.loads((ROOT / ".agents/registries/mcp-capabilities.json").read_text(encoding="utf-8"))
        caps["capabilities"]["sap.abap.source.read"]["primary"] = "server-that-does-not-exist"
        caps_path.write_text(json.dumps(caps), encoding="utf-8")
        mutated = _validate_tree(tmp)
        check.expect("rejects unknown provider",
                     any("server-that-does-not-exist" in e for e in mutated["errors"]),
                     str(mutated["errors"][:2]))

        # Mutation C: a mutating capability that does not require approval.
        caps = json.loads((ROOT / ".agents/registries/mcp-capabilities.json").read_text(encoding="utf-8"))
        caps["capabilities"]["sap.abap.source.modify"].pop("requires_approval", None)
        caps_path.write_text(json.dumps(caps), encoding="utf-8")
        mutated = _validate_tree(tmp)
        check.expect("rejects unapproved mutation",
                     any("must require approval" in e for e in mutated["errors"]),
                     str(mutated["errors"][:2]))

        # Mutation D: an MCP source catalogued but wired nowhere.
        shutil.copy2(ROOT / ".agents/registries/mcp-capabilities.json", caps_path)
        sources_path = tmp / ".agents" / "registries" / "bundled-sources.json"
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        sources["sources"].append({"id": "ghost-mcp", "repository": "https://example.invalid/ghost", "kind": "mcp"})
        sources_path.write_text(json.dumps(sources), encoding="utf-8")
        mutated = _validate_tree(tmp)
        check.expect("rejects catalogued-but-unwired MCP source",
                     any("ghost-mcp" in e for e in mutated["errors"]),
                     str(mutated["errors"][:2]))

    return _result("catalog_fail_closed", check, live, started, details)


# ---------------------------------------------------------------------------
# Scenario 2 - capability routing resolves only to launchable servers
# ---------------------------------------------------------------------------

def eval_capability_routing(live: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
    check = Check()
    details: dict[str, Any] = {}

    import mcp_launcher

    configured = set(json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers", {}))

    reachable = mcp_launcher.list_capability("sap.abap.source.read")["sap.abap.source.read"]
    details["sap.abap.source.read"] = reachable
    check.expect("read capability selects a server", reachable["selected"] is not None)
    check.expect("selected server is configured in .mcp.json",
                 reachable["selected"] in configured,
                 "selected={0}".format(reachable["selected"]))

    # A capability whose only provider is planned must resolve to nothing.
    planned_only = mcp_launcher.list_capability("sap.smartform.analyze")["sap.smartform.analyze"]
    details["sap.smartform.analyze"] = planned_only
    check.expect("planned-only capability selects nothing",
                 planned_only["selected"] is None,
                 "selected={0}".format(planned_only["selected"]))

    # Mutating capabilities must carry the approval flag through to the router.
    modify = mcp_launcher.list_capability("sap.abap.source.modify")["sap.abap.source.modify"]
    check.expect("mutating capability is flagged", modify["mutation"] is True)
    check.expect("mutating capability requires approval", modify["requires_approval"] is True)

    # An unregistered capability must not resolve at all.
    from sap_router_core.registry import resolve_servers_for_capability
    check.expect_equal("unregistered capability resolves to nothing",
                       resolve_servers_for_capability("sap.capability.that.does.not.exist"), [])

    if live:
        from sap_router_core.registry import probe_server
        target = reachable["selected"]
        probe = probe_server(target, execute=True, timeout=20)
        details["live_probe"] = probe
        check.expect("live stdio handshake succeeds",
                     probe.get("status") in {"OK", "READY", "PASS"},
                     json.dumps(probe)[:200])
    else:
        details["live_probe"] = "skipped - offline mode does not start MCP subprocesses"

    return _result("capability_routing", check, live, started, details)


# ---------------------------------------------------------------------------
# Scenario 3 - the approval broker actually blocks
# ---------------------------------------------------------------------------

def eval_approval_gate(live: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
    check = Check()
    details: dict[str, Any] = {}

    import approval_broker

    action_id = "eval-{0}".format(uuid.uuid4())
    plan = approval_broker.write_plan({
        "action_id": action_id,
        "capability": "sap.abap.source.modify",
        "effect": "mutating",
        "target": "ZCL_EVAL_HARNESS_PROBE",
        "summary": "harness evaluation - never executed",
    })
    details["plan_status"] = plan["status"]

    try:
        check.expect_equal("new plan is pending", plan["status"], "PENDING")

        blocked = approval_broker.consume(action_id, plan_hash_arg=plan["plan_hash"])
        check.expect_equal("consume before approval is rejected", blocked.get("error"), "approval-not-approved")

        approved = approval_broker.set_status(action_id, "APPROVED")
        check.expect_equal("approval succeeds", approved["status"], "APPROVED")

        wrong = approval_broker.consume(action_id, plan_hash_arg="0" * 64)
        check.expect_equal("wrong plan hash is rejected", wrong.get("error"), "plan-hash-confirmation-mismatch")

        missing = approval_broker.consume(action_id)
        check.expect_equal("missing plan hash is rejected", missing.get("error"), "plan-hash-required")

        consumed = approval_broker.consume(action_id, plan_hash_arg=approved["plan_hash"])
        check.expect_equal("correct hash consumes the approval", consumed["status"], "CONSUMED")

        replay = approval_broker.consume(action_id, plan_hash_arg=approved["plan_hash"])
        check.expect_equal("approval cannot be replayed", replay.get("error"), "approval-already-consumed")
    finally:
        approval_broker.plan_file(action_id).unlink(missing_ok=True)

    return _result("approval_gate", check, live, started, details)


# ---------------------------------------------------------------------------
# Scenario 4 - the Remote FS client and its ABAP backend agree
# ---------------------------------------------------------------------------

CLIENT_TS = ROOT / "packages" / "vscode-abap-remote-fs-zrouter" / "src" / "zrouter_client.ts"
DISPATCHER = ROOT / "templates" / "zrouter_dispatch.prog.abap"


def eval_zrouter_fs_contract(live: bool = False) -> dict[str, Any]:
    """Every FS_* action the TypeScript client sends must exist in the dispatcher."""
    started = time.perf_counter()
    check = Check()
    details: dict[str, Any] = {}

    if not check.expect("client source present", CLIENT_TS.exists(), str(CLIENT_TS)):
        return _result("zrouter_fs_contract", check, live, started, details)
    if not check.expect("dispatcher template present", DISPATCHER.exists(), str(DISPATCHER)):
        return _result("zrouter_fs_contract", check, live, started, details)

    client = CLIENT_TS.read_text(encoding="utf-8")
    abap = DISPATCHER.read_text(encoding="utf-8")

    dispatched = sorted(set(re.findall(r"'(FS_[A-Z_]+)'", client)))
    handled = sorted(set(re.findall(r"WHEN\s+'(FS_[A-Z_]+)'", abap)))
    details["dispatched_by_client"] = dispatched
    details["handled_by_abap"] = handled

    check.expect("client dispatches FS actions", len(dispatched) > 0)
    missing = [a for a in dispatched if a not in handled]
    check.expect("every dispatched action has a handler branch", not missing, "missing={0}".format(missing))

    check.expect("FS handler class exists",
                 "CLASS zcl_zrouter_handler_fs IMPLEMENTATION" in abap)
    check.expect("dispatcher factory routes module FS",
                 re.search(r"WHEN\s+'FS'\.\s*\n\s*ro_handler\s*=\s*NEW\s+zcl_zrouter_handler_fs", abap) is not None)
    check.expect("FS mutations demand a transport",
                 "FS mutation requires an explicit transport request" in abap)

    # The SOAP envelope must escape every interpolated value or a payload
    # containing markup breaks the request - or injects into it.
    envelope = re.search(r"<urn:ZROUTER_DISPATCH_FM>([\s\S]*?)</urn:ZROUTER_DISPATCH_FM>", client)
    check.expect("SOAP envelope found in client", envelope is not None)
    if envelope:
        interpolations = re.findall(r"\$\{([^}]*)\}", envelope.group(1))
        unescaped = [i for i in interpolations if "escapeXml" not in i]
        check.expect("all SOAP interpolations are XML-escaped", not unescaped, "raw={0}".format(unescaped))

    # SOAP response parsing must tolerate namespace prefixes.
    check.expect("SOAP parser tolerates namespace prefixes", "[A-Za-z_][\\\\w.-]*:" in client)

    if live:
        details["live_dispatch"] = "requires a ZROUTER-enabled system; run npm run zrouter:http:test"
        check.expect("live ZROUTER endpoint configured",
                     bool(__import__("os").environ.get("ZROUTER_BASE_URL")),
                     "ZROUTER_BASE_URL is unset")
    else:
        details["live_dispatch"] = "skipped - offline mode does not contact SAP"

    return _result("zrouter_fs_contract", check, live, started, details)


# ---------------------------------------------------------------------------
# Scenario 5 - skill packaging validation accepts good and rejects bad
# ---------------------------------------------------------------------------

def eval_skill_packaging(live: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
    check = Check()
    details: dict[str, Any] = {}

    import skill_packager

    real = sorted(p.parent for p in (ROOT / ".agents" / "skills").glob("*/SKILL.md"))
    if not check.expect("repository ships at least one skill", bool(real)):
        return _result("skill_packaging", check, live, started, details)

    ok, errors = skill_packager.validate_skill(real[0])
    details["sample_skill"] = real[0].name
    check.expect("a shipped skill validates", ok, "; ".join(errors[:3]))

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)

        broken = tmp / "no-frontmatter"
        broken.mkdir()
        (broken / "SKILL.md").write_text("# Just a heading, no frontmatter\n", encoding="utf-8")
        ok_broken, errs_broken = skill_packager.validate_skill(broken)
        check.expect("skill without frontmatter is rejected", not ok_broken, str(errs_broken[:2]))

        empty = tmp / "no-skill-md"
        empty.mkdir()
        ok_empty, errs_empty = skill_packager.validate_skill(empty)
        check.expect("directory without SKILL.md is rejected", not ok_empty, str(errs_empty[:2]))

        ok_missing, errs_missing = skill_packager.validate_skill(tmp / "does-not-exist")
        check.expect("missing directory is rejected", not ok_missing, str(errs_missing[:2]))

    details["live"] = "skipped - packaging validation has no live component" if not live else "no live component"
    return _result("skill_packaging", check, live, started, details)


SCENARIO_MAP: dict[str, Callable[[bool], dict[str, Any]]] = {
    "catalog_fail_closed": eval_catalog_fail_closed,
    "capability_routing": eval_capability_routing,
    "approval_gate": eval_approval_gate,
    "zrouter_fs_contract": eval_zrouter_fs_contract,
    "skill_packaging": eval_skill_packaging,
}


def run_all_evals(live: bool = False, scenarios: list[str] | None = None) -> dict[str, Any]:
    """Runs the selected scenarios and aggregates their outcomes.

    A scenario that raises is reported as a failure with its traceback rather
    than being swallowed - an eval that cannot run has not passed.
    """
    names = scenarios or list(SCENARIO_MAP)
    unknown = [n for n in names if n not in SCENARIO_MAP]
    if unknown:
        raise KeyError("unknown scenario(s): {0}".format(", ".join(unknown)))

    results = []
    for name in names:
        started = time.perf_counter()
        try:
            results.append(SCENARIO_MAP[name](live))
        except Exception as exc:  # noqa: BLE001 - reported, never hidden
            results.append({
                "scenario": name,
                "status": "FAIL",
                "score": 0.0,
                "checks_passed": 0,
                "checks_total": 0,
                "failures": ["scenario raised {0}: {1}".format(type(exc).__name__, exc)],
                "mode": "live" if live else "offline",
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                "details": {},
            })

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    checks_total = sum(r["checks_total"] for r in results)
    checks_passed = sum(r["checks_passed"] for r in results)

    return {
        "status": "PASS" if passed == total and total else "FAIL",
        "mode": "live" if live else "offline",
        "scenarios_tested": total,
        "scenarios_passed": passed,
        "pass_rate_percent": round((passed / total) * 100, 1) if total else 0.0,
        "checks_total": checks_total,
        "checks_passed": checks_passed,
        "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / total, 2) if total else 0.0,
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_all_evals(live="--live" in sys.argv), indent=2))
