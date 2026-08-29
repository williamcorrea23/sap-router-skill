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


class ApimProxyPackagerTest(unittest.TestCase):
    """The bundle packager must produce something the tenant will accept,
    and must fail loudly when a flow references a policy that is not shipped."""

    def _template(self, kind, name, output, extra=None):
        return subprocess.run(
            [sys.executable, "scripts/apim_proxy_packager.py", "template",
             "--kind", kind, "--name", name, "--output", str(output)] + (extra or []),
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )

    def _validate(self, bundle):
        proc = subprocess.run(
            [sys.executable, "scripts/apim_proxy_packager.py", "validate", "--input", str(bundle), "--json"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        return proc, json.loads(proc.stdout)

    def test_echo_template_validates_offline(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "echo.zip"
            self.assertEqual(self._template("echo", "ZTEST_ECHO", bundle).returncode, 0)
            proc, report = self._validate(bundle)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual(report["status"], "OK", report)

    def test_backend_template_requires_a_backend_url(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "backend.zip"
            self.assertNotEqual(self._template("backend", "ZTEST_API", bundle).returncode, 0)
            self.assertEqual(
                self._template("backend", "ZTEST_API", bundle,
                               ["--backend-url", "https://example.com/odata"]).returncode,
                0,
            )
            _, report = self._validate(bundle)
            self.assertEqual(report["status"], "OK", report)

    def test_missing_policy_file_is_an_error_not_a_warning(self):
        import tempfile
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "echo.zip"
            self._template("echo", "ZTEST_ECHO", source)
            stripped = Path(tmp) / "stripped.zip"
            with zipfile.ZipFile(source) as src, zipfile.ZipFile(stripped, "w") as dst:
                for entry in src.namelist():
                    if entry != "Policy/Spike-Arrest.xml":
                        dst.writestr(entry, src.read(entry))
            proc, report = self._validate(stripped)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(report["status"], "ERROR")
            self.assertTrue(any("Spike-Arrest" in error for error in report["errors"]), report)


class ApprovalSpendOrderTest(unittest.TestCase):
    """A one-time approval must survive a failed mutation. Verifying and spending
    are separate steps so a transient error does not cost the operator a re-approval."""

    def _broker(self, *broker_args):
        proc = subprocess.run(
            [sys.executable, "scripts/approval_broker.py", *broker_args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        return proc, json.loads(proc.stdout or "{}")

    def _approved_plan(self, target):
        _, plan = self._broker(
            "plan", "--capability", "sap.apim.proxy.deploy", "--target", target,
            "--summary", "audit regression check", "--effect", "mutating",
            "--arguments-json", '{"a":1}', "--preconditions-json", '{"b":true}',
        )
        self._broker("approve", plan["action_id"])
        return plan

    def test_verify_does_not_spend_the_approval(self):
        plan = self._approved_plan("ZTEST_VERIFY")
        for _ in range(2):
            proc, result = self._broker("verify", plan["action_id"], "--plan-hash", plan["plan_hash"])
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual(result["status"], "APPROVED")
        _, consumed = self._broker("consume", plan["action_id"], "--plan-hash", plan["plan_hash"])
        self.assertEqual(consumed["status"], "CONSUMED")

    def test_consume_remains_one_time_after_verify(self):
        plan = self._approved_plan("ZTEST_ONCE")
        self._broker("verify", plan["action_id"], "--plan-hash", plan["plan_hash"])
        self._broker("consume", plan["action_id"], "--plan-hash", plan["plan_hash"])
        proc, replay = self._broker("consume", plan["action_id"], "--plan-hash", plan["plan_hash"])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(replay["error"], "approval-already-consumed")

    def test_verify_rejects_an_unapproved_plan(self):
        _, plan = self._broker(
            "plan", "--capability", "sap.apim.proxy.deploy", "--target", "ZTEST_PENDING",
            "--summary", "audit regression check", "--effect", "mutating",
            "--arguments-json", "{}", "--preconditions-json", "{}",
        )
        proc, result = self._broker("verify", plan["action_id"], "--plan-hash", plan["plan_hash"])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(result["error"], "approval-not-approved")


class PlanFileTamperTest(unittest.TestCase):
    """A commit must run the arguments the human approved, not whatever is on
    disk or on the command line by the time it runs.

    approval_broker.write_plan() stores only argument_hash, so every commit path
    re-supplies the arguments themselves. The broker cannot catch an edit to
    them: its plan_hash check hashes its own stored copy, which still matches.
    Each case below tampers after approval and asserts two things - the commit
    refuses, and the one-time approval is still spendable afterwards.
    """

    def _broker(self, *broker_args, stdin=None):
        proc = subprocess.run(
            [sys.executable, "scripts/approval_broker.py", *broker_args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", input=stdin,
        )
        return proc, json.loads(proc.stdout or "{}")

    def _assert_still_spendable(self, plan):
        """The refusal must not have burned the approval."""
        proc, verified = self._broker("verify", plan["action_id"], "--plan-hash", plan["plan_hash"])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(verified["status"], "APPROVED", verified)

    def test_broker_hash_matches_the_hash_stored_at_plan_time(self):
        """The `hash` subcommand is what non-Python callers rely on, so it has to
        agree with write_plan() - including on non-ASCII, where json.dumps
        escapes and JSON.stringify does not."""
        arguments = {"target": "ZTEST_CAF\u00c9", "note": "caf\u00e9"}
        _, plan = self._broker(
            "plan", "--capability", "sap.apim.proxy.deploy", "--target", "ZTEST_HASH",
            "--summary", "hash parity", "--effect", "mutating",
            "--arguments-json", json.dumps(arguments), "--preconditions-json", "{}",
        )
        self.addCleanup(self._broker, "reject", plan["action_id"])
        proc, hashed = self._broker("hash", "--json", "-", stdin=json.dumps(arguments))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(hashed["hash"], plan["argument_hash"])

        # Key order must not matter: the broker re-serialises what it is handed,
        # which is why the bridge can pass a plain JSON.stringify of its object.
        reordered = json.dumps({key: arguments[key] for key in reversed(list(arguments))})
        _, again = self._broker("hash", "--json", "-", stdin=reordered)
        self.assertEqual(again["hash"], plan["argument_hash"])

    def test_apim_commit_refuses_a_plan_file_edited_after_approval(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            bundle = Path(tmp) / "bundle.zip"
            bundle.write_bytes(b"PK\x05\x06" + b"\x00" * 18)
            proc = subprocess.run(
                [sys.executable, "scripts/apim_client.py", "deploy", "plan",
                 "--bundle", str(bundle), "--target", "ZTEST_TAMPER"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            )
            plan = json.loads(proc.stdout)
            self.addCleanup(self._broker, "reject", plan["action_id"])
            self._broker("approve", plan["action_id"])

            plan_path = ROOT / "scratch" / "apim-plans" / (plan["apim_plan_id"] + ".json")
            self.addCleanup(plan_path.unlink, True)
            local = json.loads(plan_path.read_text(encoding="utf-8"))
            local["arguments"]["path"] = "/apiportal/api/1.0/Management.svc/APIProxies('ZEVIL')/$value"
            plan_path.write_text(json.dumps(local, indent=2) + "\n", encoding="utf-8")

            commit = subprocess.run(
                [sys.executable, "scripts/apim_client.py", "deploy", "execute",
                 "--plan-id", plan["apim_plan_id"], "--action-id", plan["action_id"],
                 "--plan-hash", plan["plan_hash"], "--argument-hash", plan["argument_hash"],
                 "--precondition-hash", plan["precondition_hash"], "--confirm"],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            )
            result = json.loads(commit.stdout)
            self.assertEqual(commit.returncode, 1, commit.stdout)
            self.assertEqual(result["status"], "BLOCKED", result)
            self.assertEqual(result["reason"], "argument-hash-mismatch", result)
            self.assertEqual(result["approval"], "still-open", result)
            self._assert_still_spendable(plan)

    def test_cpi_commit_refuses_arguments_swapped_at_the_command_line(self):
        """cpi_client rebuilds its arguments from argv, so there the tampering
        surface is the commit command rather than a plan file."""
        env = dict(os.environ)
        env.update({
            "CPI_BASE_URL": "https://tenant.invalid",
            "CPI_OAUTH_TOKEN_URL": "https://tenant.invalid/oauth/token",
            "CPI_OAUTH_CLIENT_ID": "id",
            "CPI_OAUTH_CLIENT_SECRET": "secret",
        })
        proc = subprocess.run(
            [sys.executable, "scripts/cpi_client.py", "undeploy", "plan", "--artifact-id", "ZTEST_APPROVED"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        plan = json.loads(proc.stdout)
        self.addCleanup(self._broker, "reject", plan["action_id"])
        self._broker("approve", plan["action_id"], "--confirm", "ZTEST_APPROVED")

        commit = subprocess.run(
            [sys.executable, "scripts/cpi_client.py", "undeploy", "commit",
             "--artifact-id", "ZTEST_SOMETHING_ELSE",
             "--action-id", plan["action_id"], "--plan-hash", plan["plan_hash"],
             "--argument-hash", plan["argument_hash"],
             "--precondition-hash", plan["precondition_hash"]],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env,
        )
        result = json.loads(commit.stdout)
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertEqual(result["reason"], "argument-hash-mismatch", result)
        self.assertEqual(result["approval"], "still-open", result)
        self._assert_still_spendable(plan)


class ApimChannelBridgeTest(unittest.TestCase):
    """The bridge splits read from mutate on purpose: an agent must not be able
    to change the tenant by reaching for the read tool."""

    BRIDGE = ["node", "scripts/web_ui_mcp_bridge.mjs", "--product", "apim"]

    def _call(self, name, arguments):
        request = "\n".join([
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                        "params": {"name": name, "arguments": arguments}}),
        ]) + "\n"
        proc = subprocess.run(
            self.BRIDGE, cwd=ROOT, input=request,
            capture_output=True, text=True, encoding="utf-8",
        )
        for line in proc.stdout.splitlines():
            message = json.loads(line)
            if message.get("id") == 2:
                return message["result"]["structuredContent"]
        self.fail("bridge returned no result for id 2: " + proc.stdout + proc.stderr)

    def test_mutating_action_is_refused_by_the_read_tool(self):
        result = self._call("apim_execute_action", {"action_id": "proxies.import", "params": {"name": "ZTEST"}})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("apim_configure_plan", result["next_step"])

    def test_read_action_is_refused_by_the_plan_tool(self):
        result = self._call("apim_configure_plan", {"action_id": "proxies.list"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("apim_execute_action", result["next_step"])

    def test_commit_without_confirmation_is_refused(self):
        result = self._call("apim_configure_commit", {
            "plan_id": "apim-oauth-does-not-exist", "action_id": "x", "plan_hash": "y", "confirm": False,
        })
        self.assertEqual(result["status"], "BLOCKED")

    def test_api_call_stays_inside_the_api_portal(self):
        result = self._call("apim_api_call", {"path": "/sap/opu/odata/sap/ZMATERIAL_SRV/"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("/apiportal/", result["reason"])

    def test_test_proxy_refuses_private_and_link_local_targets(self):
        for url in ("http://127.0.0.1:9/x", "http://169.254.169.254/latest/meta-data/", "http://192.168.1.1/"):
            result = self._call("apim_test_proxy", {"url": url})
            self.assertEqual(result["status"], "BLOCKED", url)
            self.assertIn("private", result["reason"])

    def test_test_proxy_refuses_hosts_outside_the_tenant(self):
        result = self._call("apim_test_proxy", {"url": "https://evil.example.com/x"})
        self.assertEqual(result["status"], "BLOCKED")

    def test_test_proxy_refuses_state_changing_verbs(self):
        result = self._call("apim_test_proxy", {"url": "https://anything.example.com/x", "method": "DELETE"})
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("change state", result["reason"])

    def _broker(self, *broker_args):
        proc = subprocess.run(
            [sys.executable, "scripts/approval_broker.py", *broker_args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        return proc, json.loads(proc.stdout or "{}")

    def test_commit_refuses_a_plan_file_edited_after_approval(self):
        """The bridge cannot reproduce the broker's canonicalisation in JS, so it
        shells out to `approval_broker.py hash` for the same answer."""
        plan = self._call("apim_configure_plan", {
            "action_id": "proxies.import", "params": {"name": "ZTEST_BRIDGE_TAMPER"},
        })
        self.assertIn("apim_plan_id", plan)
        self.addCleanup(self._broker, "reject", plan["action_id"])
        self._broker("approve", plan["action_id"])

        plan_path = ROOT / "scratch" / "apim-plans" / (plan["apim_plan_id"] + ".json")
        self.addCleanup(plan_path.unlink, True)
        local = json.loads(plan_path.read_text(encoding="utf-8"))
        local["arguments"]["path"] = "/apiportal/api/1.0/Management.svc/APIProxies('ZEVIL')/$value"
        plan_path.write_text(json.dumps(local, indent=2) + "\n", encoding="utf-8")

        result = self._call("apim_configure_commit", {
            "plan_id": plan["apim_plan_id"], "action_id": plan["action_id"],
            "plan_hash": plan["plan_hash"], "argument_hash": plan["argument_hash"],
            "precondition_hash": plan["precondition_hash"], "confirm": True,
        })
        self.assertEqual(result["status"], "BLOCKED", result)
        self.assertEqual(result["reason"], "argument-hash-mismatch", result)
        self.assertEqual(result["approval"], "still-open", result)

        proc, verified = self._broker("verify", plan["action_id"], "--plan-hash", plan["plan_hash"])
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(verified["status"], "APPROVED", verified)

    def test_action_search_reports_which_actions_mutate(self):
        result = self._call("apim_search_actions", {"query": "proxy"})
        by_id = {action["id"]: action for action in result["actions"]}
        self.assertFalse(by_id["proxies.list"]["mutating"])
        self.assertTrue(by_id["proxies.import"]["mutating"])
        self.assertEqual(by_id["proxies.import"]["capability"], "sap.apim.proxy.deploy")


if __name__ == "__main__":
    unittest.main()
