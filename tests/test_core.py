import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python"))

import sap_router
from sap_router import SapRouter
from sap_router_core.registry import classify_task, load_servers, validate_catalog
from source_catalog import INDEX_FILE, load, score_asset


class FunctionalWriteGateTest(unittest.TestCase):
    """The gate that stops a BAPI firing outside an explicit functional context.

    Every action below once slipped through because matching was on raw
    substrings: 'LIST' is inside 'LISTING' and 'PICKLIST', 'GET' is inside
    'BUDGET' and 'TARGET', and any action containing 'GUI' was waved past.
    """

    WRITES = [
        "MM_CREATE_MATERIAL",
        "CREATE_MATERIAL",
        "CREATE_MATERIAL_LISTING",   # LIST inside LISTING
        "CREATE_MATERIAL_GUI",       # former GUI escape hatch
        "CREATE_PO_CHECKLIST",       # CHECK inside CHECKLIST
        "GET_CREATE_PO",
        "POST_BUDGET_DOCUMENT",      # GET inside BUDGET
        "CREATE_PICKLIST",
        "UPDATE_PRICELIST",
        "POST_CHECK_RUN",
        "CREATE_TARGET_PLAN",        # GET inside TARGET
        "REVERSE_DOCUMENT",
        "BAPI_USER_CREATE1",
    ]

    READS = [
        "DISPLAY_MATERIAL",
        "READ_SOURCE",
        "MM03_GUI",
        "SPRO_CONFIG",
        "MMBE_STOCK_OVERVIEW",
    ]

    def test_every_write_action_is_gated(self):
        router = SapRouter()
        for action in self.WRITES:
            with self.subTest(action=action):
                self.assertTrue(
                    router._is_functional_write(action),
                    f"{action} slipped the functional-write gate",
                )

    def test_reads_and_navigation_stay_ungated(self):
        router = SapRouter()
        for action in self.READS:
            with self.subTest(action=action):
                self.assertFalse(
                    router._is_functional_write(action),
                    f"{action} is a read but was gated as a write",
                )

    def test_gated_action_is_not_dispatched_without_context(self):
        route = SapRouter().get_route("CREATE_MATERIAL_LISTING")
        self.assertEqual(route["strategy"], "needs-functional-context")

    def test_bapi_lookup_does_not_match_across_token_boundaries(self):
        router = SapRouter()
        # CREATE_PO must not claim CREATE_PORTAL_USER or CREATE_POSTING.
        self.assertIsNone(router._lookup_bapi("CREATE_PORTAL_USER"))
        self.assertIsNone(router._lookup_bapi("CREATE_POSTING"))
        self.assertEqual(router._lookup_bapi("CREATE_PO"), "BAPI_PO_CREATE1")
        self.assertEqual(
            router._lookup_bapi("MM_CREATE_MATERIAL"), "BAPI_MATERIAL_SAVEDATA"
        )


class SoapRfcContractTest(unittest.TestCase):
    """_call_soap_rfc returns (body, status); callers must unpack it.

    Testing the tuple itself for None always passed, so the probe reported the
    endpoint reachable even when the POST failed, and the raw tuple reached
    re.search inside _parse_soap_return.
    """

    def setUp(self):
        self.router = SapRouter()
        self._saved = sap_router._soap_rfc_available
        sap_router._soap_rfc_available = None
        os.environ.setdefault("ARC_SAP_URL", "https://sap.invalid")
        os.environ.setdefault("ARC_SAP_USER", "tester")

    def tearDown(self):
        sap_router._soap_rfc_available = self._saved

    def test_probe_reports_unavailable_when_the_call_fails(self):
        self.router._call_soap_rfc = lambda *a, **k: (None, 0)
        self.assertFalse(self.router._probe_soap_rfc())

    def test_probe_reports_available_only_on_http_200(self):
        self.router._call_soap_rfc = lambda *a, **k: ("<ok/>", 200)
        self.assertTrue(self.router._probe_soap_rfc())

    def test_non_200_response_does_not_become_a_route(self):
        self.router._probe_soap_rfc = lambda: True
        self.router._call_soap_rfc = lambda *a, **k: (None, 500)
        self.assertIsNone(self.router._try_soap_rfc("CREATE_MATERIAL"))

    def test_parse_soap_return_never_receives_a_tuple(self):
        # Guards the TypeError that fired after the POST had already hit SAP.
        with self.assertRaises(TypeError):
            self.router._parse_soap_return(("<RETURN/>", 200), "BAPI_X")


class RouterContractsTest(unittest.TestCase):
    def test_functional_write_is_gated(self):
        route = SapRouter().get_route("MM_CREATE_MATERIAL")
        self.assertEqual(route["strategy"], "needs-functional-context")

    def test_functional_route_is_classified_without_execution(self):
        route = SapRouter().get_route("MM_CREATE_MATERIAL", functional_context=True)
        self.assertEqual(route["strategy"], "bapi-functional")
        self.assertEqual(route["bapi"], "BAPI_MATERIAL_SAVEDATA")

    def test_caveman_delegation_targets_are_real_agents(self):
        """Every cavecrew agent_type the router emits must exist as an agent file.

        Regression guard: these were dangling 'caveman:cavecrew-*' references
        pointing at a plugin that was never installed.
        """
        agents_dir = ROOT / ".claude" / "agents"
        for task, expected in (
            ("find the material master class", "cavecrew-investigator"),
            ("fix typo in readme", "cavecrew-builder"),
            ("review this diff", "cavecrew-reviewer"),
        ):
            decision = SapRouter()._check_caveman_delegation(task)
            self.assertIsNotNone(decision, f"no delegation for {task!r}")
            agent_type = decision["agent_type"]
            self.assertEqual(agent_type, expected)
            self.assertTrue(
                (agents_dir / f"{agent_type}.md").is_file(),
                f"{agent_type} routed but .claude/agents/{agent_type}.md is missing",
            )

    def test_catalog_is_valid(self):
        result = validate_catalog()
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["counts"]["capabilities"], 0)

    def test_classifier_requires_confirmation_for_mutation(self):
        decision = classify_task("deploy api proxy to DEV")
        self.assertEqual(decision["capability"], "sap.apim.proxy.deploy")

    def test_bundled_catalog_is_complete_and_fail_closed(self):
        index = load(INDEX_FILE, {})
        self.assertEqual(index.get("missing_sources"), [])
        self.assertGreater(index.get("asset_count", 0), 100)
        candidates = [item for item in index.get("assets", []) if item.get("kind") == "mcp" and item.get("trust") == "bundled_unreviewed"]
        self.assertTrue(candidates)
        self.assertTrue(all(item.get("status") == "disabled_candidate" for item in candidates))

    def test_dynamic_search_prefers_reviewed_gui_mcp(self):
        assets = load(INDEX_FILE, {}).get("assets", [])
        ranked = sorted(assets, key=lambda item: score_asset(item, "SAP GUI transaction automation", "mcp", None), reverse=True)
        self.assertEqual(ranked[0]["id"], "registered-mcp:mcp-sap-gui")

    def test_dynamic_search_does_not_classify_capability_as_cap(self):
        assets = {item["id"]: item for item in load(INDEX_FILE, {}).get("assets", [])}
        query = "SAP CAP CDS application model"
        self.assertGreater(
            score_asset(assets["canonical:sap-cap"], query, "skill", None),
            score_asset(assets["canonical:authorization-iam"], query, "skill", None),
        )

    def test_only_reviewed_servers_are_launched(self):
        """No unpromoted candidate may sit in mcpServers.

        scripts/mcp_launcher.py refuses to run a candidate and there is a test
        below pinning that refusal, but every candidate used to ship as a live
        mcpServers entry -- so the client launched exactly what the fail-closed
        policy says must not run. Candidates now live under plannedServers.
        """
        mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        configured = set(mcp.get("mcpServers", {}))
        planned = set(mcp.get("plannedServers", {}))
        candidates = json.loads(
            (ROOT / ".agents" / "registries" / "mcp-candidates.json").read_text(encoding="utf-8")
        )
        candidate_ids = {item["id"] for item in candidates["candidates"]}

        self.assertTrue(
            configured.issubset(set(load_servers())),
            f"unreviewed servers are live: {sorted(configured - set(load_servers()))}",
        )
        self.assertFalse(
            configured & candidate_ids,
            f"candidates must not be launched: {sorted(configured & candidate_ids)}",
        )
        self.assertTrue(
            candidate_ids.issubset(planned),
            f"candidates missing from plannedServers: {sorted(candidate_ids - planned)}",
        )
        self.assertFalse(configured & planned, "a server cannot be both live and planned")
        self.assertTrue(all(item["status"] == "disabled_candidate" for item in candidates["candidates"]))

    def test_every_live_server_has_a_resolvable_entrypoint(self):
        """A live mcpServers entry must point at something that exists.

        18 entries shared the identical args ["dist/index.js"] against a dist/
        directory that was never built, and the healthcheck reported them ready.
        """
        sys.path.insert(0, str(ROOT / "scripts"))
        from healthcheck import HealthChecker

        checker = HealthChecker()
        mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        broken = {
            name: checker.check_mcp_target(name)
            for name in mcp.get("mcpServers", {})
            if checker.check_mcp_target(name)["status"] not in ("PRESENT", "EXTERNAL")
        }
        self.assertEqual(broken, {}, f"live servers with a missing entrypoint: {broken}")

    def test_mcp_launcher_blocks_unreviewed_fallback_execution(self):
        proc = subprocess.run(
            [sys.executable, "scripts/mcp_launcher.py", "run", "--server", "sf-mcp"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("fallback-candidate-not-promoted", proc.stderr)

    def test_zrouter_artifacts_have_no_dynamic_evaluator(self):
        proc = subprocess.run(
            [sys.executable, "scripts/normalize_zrouter_artifacts.py", "--check"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_healthcheck_json_is_machine_readable(self):
        proc = subprocess.run(
            [sys.executable, "scripts/healthcheck.py", "--quiet", "--json", "--read-only"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        payload = json.loads(proc.stdout)
        self.assertIn(payload["overall_status"], {"PASS", "DEGRADED", "BLOCKED"})
        self.assertEqual(proc.stderr, "")


if __name__ == "__main__":
    unittest.main()
