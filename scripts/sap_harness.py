#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAP Harness - capability routing, evaluation and distribution front end.

What this tool does:
- resolves a task to a capability, a profile agent and a launchable MCP server
- registers mutating work with the approval broker before anything runs
- runs the evaluation suite offline (hermetic) or live
- inspects the MCP catalog and packages skills for distribution

What it does not do: execute the resolved plan. There is no agent dispatcher
wired into this repository yet, so `run` produces a plan and says so. It never
reports work as done that it did not do.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python"))

from harness_eval_suite import SCENARIO_MAP, run_all_evals
import approval_broker
import mcp_launcher
import skill_packager
import source_catalog

__version__ = "7.1.0"

# Registered Specialized Subagents
SPECIALIZED_AGENTS = {
    "cpi": {
        "name": "sap-cpi-flowpilot",
        "domain": "Cloud Integration & Integration Suite",
        "skills": ["sap-cpi-flowpilot", "cpi-iflow-development", "btp-integration-suite"],
        "capabilities": ["sap.cpi.artifact.read", "sap.cpi.message.read", "sap.cpi.bundle.package"],
        "primary_mcp": "sap-cpi-mcp",
    },
    "abap": {
        "name": "sap-abap-engineer",
        "domain": "ABAP Development & Clean Core",
        "skills": ["sap-abap", "clean-abap", "cds-view-entities"],
        "capabilities": ["sap.abap.source.read", "sap.abap.source.modify", "sap.remotefs.file.read"],
        "primary_mcp": "arc-1",
    },
    "fiori": {
        "name": "sap-fiori-ux-architect",
        "domain": "Fiori Elements, UI5 & Theme Designer",
        "skills": ["sap-fiori", "sapui5-framework", "sap-ui-theme-designer-plugins"],
        "capabilities": ["sap.fiori.app.generate", "sap.ui5.project.validate", "sap.ui5.webcomponents.render"],
        "primary_mcp": "fiori-mcp",
    },
    "bdc": {
        "name": "sap-bdc-automation-bot",
        "domain": "Classic SAP GUI & BDC Automation",
        "skills": ["sap-gui-scripting", "sap-bdc-plugin", "sap-report-automation-workflow"],
        "capabilities": ["sap.gui.transaction.run"],
        "primary_mcp": "mcp-sap-gui",
    },
    "sre": {
        "name": "sap-incident-resolution-agent",
        "domain": "SRE, ST22 Triage & Self-Healing",
        "skills": ["sap-incident-resolution", "sap-health-triage", "sap-automation-pilot-agent-skills"],
        "capabilities": ["sap.incident.resolution.diagnose", "sap.incident.resolution.remediate"],
        "primary_mcp": "arc-1",
    },
}

BANNER = "=" * 56


def _header(title: str) -> None:
    print("\n{0}\n  SAP Harness v{1} - {2}\n{0}".format(BANNER, __version__, title))


# ---------------------------------------------------------------------------
# run - resolve a task into an executable plan
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    task = args.task
    _header("Plan for: {0}".format(task))
    print("Mode:  {0}".format("LIVE" if args.live else "OFFLINE (hermetic)"))

    agent = SPECIALIZED_AGENTS.get(args.agent) if args.agent else None
    if agent:
        print("Agent: {0} ({1})".format(agent["name"], agent["domain"]))

    try:
        from sap_router_core.registry import classify_task
        classification = classify_task(task)
    except Exception as exc:  # noqa: BLE001
        print("Routing unavailable: {0}".format(exc))
        return 1

    capability = classification.get("capability")
    server = classification.get("selected_server")
    print("Capability:      {0}".format(capability or "unresolved"))
    print("Selected server: {0}".format(server or "none"))
    print("Reason:          {0}".format(classification.get("selection_reason")))

    if not capability:
        print("\nNo route registered for this task. Fail-closed: nothing will run.")
        print("Register a route in .agents/registries/routes.json, then re-plan.")
        return 1

    readiness = mcp_launcher.list_capability(capability).get(capability, {})
    print("Ready servers:   {0}".format([r["server"] for r in readiness.get("ready", [])] or "none"))
    for blocked in readiness.get("blocked", []):
        print("  blocked: {0} ({1})".format(blocked["server"], blocked["reason"]))

    if not readiness.get("selected"):
        print("\nNo launchable provider for {0}. Fail-closed: nothing will run.".format(capability))
        return 1

    if readiness.get("requires_approval"):
        plan = approval_broker.write_plan({
            "capability": capability,
            "effect": "mutating",
            "target": args.target or task,
            "summary": task,
        })
        print("\nMutating capability. Approval plan registered, NOT approved:")
        print("  action_id: {0}".format(plan["action_id"]))
        print("  plan_hash: {0}".format(plan["plan_hash"]))
        print("  expires:   {0}".format(plan["expires_at"]))
        print("  approve:   python scripts/approval_broker.py approve --action-id {0}".format(plan["action_id"]))

    if args.execute:
        print("\nRefusing --execute: no agent dispatcher is wired into this harness.")
        print("The plan above is complete; run it through the MCP client or a skill.")
        return 2

    print("\nPlan resolved. Nothing was executed (planning is this command's whole job).")
    return 0


# ---------------------------------------------------------------------------
# eval / benchmark
# ---------------------------------------------------------------------------

def _selected_scenarios(args: argparse.Namespace) -> list[str] | None:
    if getattr(args, "scenario", None):
        return list(args.scenario)
    suite = getattr(args, "suite", None)
    if suite and suite != "all":
        return [suite]
    return None


def _print_eval(results: dict[str, Any]) -> None:
    print("Overall:  {0} ({1} mode)".format(results["status"], results["mode"]))
    print("Scenarios: {0}/{1} passed ({2}%)".format(
        results["scenarios_passed"], results["scenarios_tested"], results["pass_rate_percent"]))
    print("Checks:    {0}/{1} passed".format(results["checks_passed"], results["checks_total"]))
    print("Avg latency: {0} ms\n".format(results["avg_latency_ms"]))
    for r in results["results"]:
        print("  [{0}] {1:<24} {2}/{3} checks  {4} ms".format(
            r["status"], r["scenario"], r["checks_passed"], r["checks_total"], r["latency_ms"]))
        for failure in r["failures"]:
            print("        FAILED: {0}".format(failure))


def cmd_eval(args: argparse.Namespace) -> int:
    scenarios = _selected_scenarios(args)
    _header("Evaluation Suite")
    try:
        results = run_all_evals(live=args.live, scenarios=scenarios)
    except KeyError as exc:
        print(exc)
        print("Available scenarios: {0}".format(", ".join(SCENARIO_MAP)))
        return 1
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        _print_eval(results)
    return 0 if results["status"] == "PASS" else 1


def cmd_benchmark(args: argparse.Namespace) -> int:
    _header("Benchmark")
    scenarios = _selected_scenarios(args)
    try:
        results = run_all_evals(live=args.live, scenarios=scenarios)
    except KeyError as exc:
        print(exc)
        print("Available scenarios: {0}".format(", ".join(SCENARIO_MAP)))
        return 1

    # The safety gate is reported from the validator, not asserted as a constant.
    import validate_catalog
    catalog = validate_catalog.merge(validate_catalog.validate(), validate_catalog.run_registry_validator())

    print("Mode:            {0}".format(results["mode"]))
    print("Scenario pass:   {0}%".format(results["pass_rate_percent"]))
    print("Check pass:      {0}/{1}".format(results["checks_passed"], results["checks_total"]))
    print("Average latency: {0} ms".format(results["avg_latency_ms"]))
    print("Catalog gate:    {0} ({1} errors, {2} warnings, {3} declared gaps)".format(
        catalog["status"], len(catalog.get("errors", [])),
        len(catalog.get("warnings", [])), len(catalog.get("gaps", []))))
    for failure in (r for res in results["results"] for r in res["failures"]):
        print("  FAILED: {0}".format(failure))
    for err in catalog.get("errors", []):
        print("  CATALOG ERROR: {0}".format(err))

    return 0 if results["status"] == "PASS" and catalog["status"] == "PASS" else 1


# ---------------------------------------------------------------------------
# agents / mcp / share
# ---------------------------------------------------------------------------

def cmd_agents(_args: argparse.Namespace) -> int:
    _header("Specialized Subagents")
    for key, agent in SPECIALIZED_AGENTS.items():
        readiness = {}
        for capability in agent["capabilities"]:
            try:
                readiness[capability] = mcp_launcher.list_capability(capability)[capability]["selected"]
            except KeyError:
                readiness[capability] = None
        print("[{0}] {1}".format(key, agent["name"]))
        print("    Domain:       {0}".format(agent["domain"]))
        print("    Primary MCP:  {0}".format(agent["primary_mcp"]))
        print("    Skills:       {0}".format(", ".join(agent["skills"])))
        for capability, server in readiness.items():
            print("    {0:<38} -> {1}".format(capability, server or "NO PROVIDER (fail-closed)"))
        print("")
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    _header("MCP Catalog")
    if args.mcp_command == "list":
        listing = mcp_launcher.list_capability(args.capability)
        if args.json:
            print(json.dumps(listing, indent=2))
            return 0
        for capability, spec in sorted(listing.items()):
            flag = " [mutating, approval required]" if spec["mutation"] else ""
            print("{0:<40} -> {1}{2}".format(capability, spec["selected"] or "NO PROVIDER", flag))
            for blocked in spec["blocked"]:
                print("    blocked: {0} ({1})".format(blocked["server"], blocked["reason"]))
        return 0

    if args.mcp_command == "probe":
        report = mcp_launcher.probe(args.server)
        print(json.dumps(report, indent=2))
        return 0 if report.get("ready") else 1

    if args.mcp_command == "search":
        return source_catalog.search(query=args.query, kind=args.kind, capability=args.capability, limit=args.limit)

    return 1


def cmd_share(args: argparse.Namespace) -> int:
    _header("Skill Distribution")
    skill_path = Path(args.skill)
    if not skill_path.exists():
        skill_path = ROOT / ".agents" / "skills" / args.skill
    if not skill_path.exists():
        print("Skill not found: {0}".format(args.skill))
        return 1

    valid, errors = skill_packager.validate_skill(skill_path)
    if not valid:
        print("Validation FAILED for '{0}':".format(skill_path.name))
        for err in errors:
            print("  - {0}".format(err))
        return 1
    print("Validation PASS: {0}".format(skill_path.name))

    if args.validate_only:
        return 0

    archive = skill_packager.package_skill(skill_path, Path(args.output) if args.output else None)
    print("Packaged: {0} ({1} bytes)".format(archive, archive.stat().st_size))

    if args.slack_json:
        frontmatter = skill_packager.parse_frontmatter((skill_path / "SKILL.md").read_text(encoding="utf-8"))
        card = skill_packager.format_slack_card(
            frontmatter.get("name", skill_path.name), frontmatter.get("description", ""), archive)
        print(json.dumps(card, indent=2))
    return 0


# ---------------------------------------------------------------------------
# test-remote-fs
# ---------------------------------------------------------------------------

def cmd_test_remote_fs(args: argparse.Namespace) -> int:
    _header("ZROUTER Remote FileSystem")
    package = ROOT / "packages" / "vscode-abap-remote-fs-zrouter"
    if not package.exists():
        print("Package not found at {0}".format(package.relative_to(ROOT)))
        return 1

    sources = sorted(package.rglob("*.ts"))
    print("Package: {0} ({1} TypeScript files)".format(package.relative_to(ROOT), len(sources)))
    for source in sources:
        print("  - {0}".format(source.relative_to(package)))

    # The contract scenario compares the client against the ABAP dispatcher.
    live = args.live and not args.mock
    result = SCENARIO_MAP["zrouter_fs_contract"](live)
    print("\nContract check: {0} ({1}/{2} assertions, {3} mode)".format(
        result["status"], result["checks_passed"], result["checks_total"], result["mode"]))
    print("  client dispatches: {0}".format(result["details"].get("dispatched_by_client")))
    print("  ABAP handles:      {0}".format(result["details"].get("handled_by_abap")))
    for failure in result["failures"]:
        print("  FAILED: {0}".format(failure))

    if args.mock:
        print("\n--mock: contract verified against the checked-in sources only; no SAP contact.")
    elif not args.live:
        print("\nOffline: no SAP contact. Use --live with ZROUTER_BASE_URL set to reach a system.")

    return 0 if result["status"] == "PASS" else 1


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SAP Harness - capability routing, evaluation and distribution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="%(prog)s {0}".format(__version__))
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Resolve a task into an executable plan")
    p_run.add_argument("--task", required=True, help="Task description or goal")
    p_run.add_argument("--agent", choices=list(SPECIALIZED_AGENTS), help="Target specialized agent")
    p_run.add_argument("--target", help="Object the plan will act on (used for strong confirmation)")
    p_run.add_argument("--live", action="store_true", help="Resolve against live backends")
    p_run.add_argument("--execute", action="store_true", help="Attempt execution (refused: no dispatcher wired)")

    p_eval = sub.add_parser("eval", help="Run evaluation scenarios")
    p_eval.add_argument("--suite", default="all", help="Scenario name or 'all'")
    p_eval.add_argument("--scenario", action="append", choices=list(SCENARIO_MAP),
                        help="Run one scenario; repeat for several")
    p_eval.add_argument("--live", action="store_true", help="Include checks that need a live backend")
    p_eval.add_argument("--json", action="store_true")

    p_bench = sub.add_parser("benchmark", help="Run benchmarks and the catalog safety gate")
    p_bench.add_argument("--scenario", action="append", choices=list(SCENARIO_MAP),
                         help="Benchmark one scenario; repeat for several")
    p_bench.add_argument("--live", action="store_true", help="Include checks that need a live backend")

    sub.add_parser("agents", help="List subagents and their provider readiness")

    p_mcp = sub.add_parser("mcp", help="Inspect the MCP capability catalog")
    mcp_sub = p_mcp.add_subparsers(dest="mcp_command", required=True)
    mcp_list = mcp_sub.add_parser("list", help="List capabilities and their selected provider")
    mcp_list.add_argument("--capability", help="Restrict to one capability")
    mcp_list.add_argument("--json", action="store_true")
    mcp_probe = mcp_sub.add_parser("probe", help="Check whether a server is ready to launch")
    mcp_probe.add_argument("--server", required=True)
    mcp_search = mcp_sub.add_parser("search", help="Rank catalogued sources for a task")
    mcp_search.add_argument("--query", required=True)
    mcp_search.add_argument("--kind")
    mcp_search.add_argument("--capability")
    mcp_search.add_argument("--limit", type=int, default=10)

    p_share = sub.add_parser("share", help="Validate and package a skill for distribution")
    p_share.add_argument("--skill", required=True, help="Skill name or path")
    p_share.add_argument("--output", help="Output zip path")
    p_share.add_argument("--slack-json", action="store_true", help="Print the Slack block kit card")
    p_share.add_argument("--validate-only", action="store_true", help="Validate without packaging")

    p_fs = sub.add_parser("test-remote-fs", help="Verify the ZROUTER Remote FileSystem contract")
    p_fs.add_argument("--mock", action="store_true", help="Check the checked-in sources only, never contact SAP")
    p_fs.add_argument("--live", action="store_true", help="Require a configured ZROUTER endpoint")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "run": cmd_run,
        "eval": cmd_eval,
        "benchmark": cmd_benchmark,
        "agents": cmd_agents,
        "mcp": cmd_mcp,
        "share": cmd_share,
        "test-remote-fs": cmd_test_remote_fs,
    }
    handler = handlers.get(args.command)
    if not handler:
        parser.print_help()
        return 0

    # Readiness is env-dependent; load .env the same way the MCP launcher CLI
    # does, otherwise every server reports missing-env in a configured repo.
    mcp_launcher.load_dotenv()
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
