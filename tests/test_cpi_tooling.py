import argparse
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python"))

import cpi_client
import sap_integration_mcp
from sap_router_core.registry import classify_task, resolve_servers_for_capability


class CpiCollectionContractTest(unittest.TestCase):
    def test_collection_result_has_stable_pagination_shape(self):
        payload = {"d": {"results": [{"Id": "A"}, {"Id": "B"}], "__count": "5"}}
        result = cpi_client.collection_result(payload, source="fixture", limit=2, offset=0)
        self.assertEqual(result["count"], 2)
        self.assertTrue(result["has_more"])
        self.assertEqual(result["next_offset"], 2)
        self.assertFalse(result["truncated"])

    def test_list_packages_escapes_odata_filter_and_bounds_page(self):
        captured = {}

        def fake_query(endpoint, params=None):
            captured.update({"endpoint": endpoint, "params": params})
            return {"d": {"results": [], "__count": "0"}}

        with mock.patch.object(cpi_client, "query_cpi_odata", side_effect=fake_query):
            result = cpi_client.list_packages(query="O'Reilly", limit=25, offset=50)
        self.assertEqual(captured["endpoint"], "/api/v1/IntegrationPackages")
        self.assertIn("O''Reilly", captured["params"]["$filter"])
        self.assertEqual(captured["params"]["$top"], 25)
        self.assertEqual(captured["params"]["$skip"], 50)
        self.assertEqual(result["offset"], 50)

    def test_limit_above_contract_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 200"):
            cpi_client.bounded_limit(201)

    def test_runtime_and_log_filters_are_composed(self):
        calls = []

        def fake_query(endpoint, params=None):
            calls.append((endpoint, params))
            return {"d": {"results": [], "__count": "0"}}

        with mock.patch.object(cpi_client, "query_cpi_odata", side_effect=fake_query):
            cpi_client.list_runtime_artifacts("STARTED", "order", 10, 0)
            cpi_client.list_logs("FAILED", "order-flow", "TRACE", "2026-01-01T00:00:00", "2026-02-01T00:00:00", 10, 0)
        self.assertIn("Status eq 'STARTED'", calls[0][1]["$filter"])
        self.assertIn("IntegrationFlowName eq 'order-flow'", calls[1][1]["$filter"])
        self.assertEqual(calls[1][1]["$orderby"], "LogStart desc")


class CpiLocalSafetyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.saved = {name: os.environ.get(name) for name in ["CPI_TOOL_WORKSPACE", *cpi_client.EXTERNAL_TOOLS.values()]}
        os.environ["CPI_TOOL_WORKSPACE"] = self.temp.name
        for name in cpi_client.EXTERNAL_TOOLS.values():
            os.environ.pop(name, None)

    def tearDown(self):
        self.temp.cleanup()
        for name, value in self.saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_workspace_path_blocks_traversal(self):
        with self.assertRaisesRegex(ValueError, "outside CPI_TOOL_WORKSPACE"):
            cpi_client.safe_workspace_path("../escape.zip")

    def test_optional_tools_fail_closed_without_install(self):
        status = cpi_client.external_tools_status()
        self.assertEqual(status["count"], 5)
        self.assertTrue(all(not item["available"] for item in status["items"]))
        result = cpi_client.run_external("cpilint", ["--version"])
        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertIn("No download", result["error"])

    def test_external_tool_runs_argument_vector_without_shell(self):
        os.environ["CPILINT_CMD"] = sys.executable
        result = cpi_client.run_external("cpilint", ["-c", "print('adapter-ok')"])
        self.assertEqual(result["status"], "OK", result)
        self.assertEqual(result["stdout"].strip(), "adapter-ok")

    def test_external_tool_timeout_is_actionable(self):
        os.environ["CPILINT_CMD"] = sys.executable
        result = cpi_client.run_external("cpilint", ["-c", "import time; time.sleep(2)"], timeout=1)
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("timed out", result["error"])

    def test_steampipe_rejects_mutating_or_chained_sql(self):
        for sql in ("DELETE FROM cpi_artifact", "SELECT * FROM x; DROP TABLE x"):
            with self.subTest(sql=sql), self.assertRaisesRegex(ValueError, "read-only SELECT"):
                cpi_client.steampipe_query(sql)


class CpiApprovalContractTest(unittest.TestCase):
    def test_plan_contains_all_hashes_and_commit_contract(self):
        broker = {
            "action_id": "action-1",
            "status": "PENDING",
            "plan_hash": "plan-hash",
            "argument_hash": "argument-hash",
            "precondition_hash": "precondition-hash",
        }
        with mock.patch.object(cpi_client, "run_approval_broker", return_value=broker):
            plan = cpi_client.make_plan(
                "sap.cpi.iflow.generate", "out.zip", "generate", "mutating",
                {"name": "flow"}, {"target_available": True},
                [sys.executable, "scripts/cpi_client.py", "generate", "commit"],
            )
        self.assertIn("--action-id action-1", plan["commit_command"])
        self.assertIn("--argument-hash argument-hash", plan["commit_command"])
        self.assertIn("--precondition-hash precondition-hash", plan["commit_command"])

    def test_commit_consumes_exact_argument_and_precondition_hashes(self):
        args = argparse.Namespace(
            action_id="action-1", plan_hash="plan-hash",
            argument_hash="argument-hash", precondition_hash="precondition-hash",
        )
        with mock.patch.object(cpi_client, "run_approval_broker") as broker:
            cpi_client.consume_plan(args, {"a": 1}, {"ready": True})
        command = broker.call_args.args[0]
        self.assertEqual(command[:3], ["consume", "action-1", "--plan-hash"])
        self.assertIn("argument-hash", command)
        self.assertIn("precondition-hash", command)


class CpiMcpContractTest(unittest.TestCase):
    def test_router_selects_only_promoted_cpi_server(self):
        servers = resolve_servers_for_capability("sap.cpi.artifact.read")
        self.assertEqual([item["id"] for item in servers], ["sap-cpi-mcp"])
        self.assertNotIn("vadimklimov-cpi-mcp-server", [item["id"] for item in servers])

    def test_undeploy_is_classified_as_destructive_capability(self):
        decision = classify_task("undeploy CPI iFlow order-api")
        self.assertEqual(decision["capability"], "sap.cpi.artifact.undeploy")
        self.assertEqual(decision["selected_server"], "sap-cpi-mcp")

    def test_all_cpi_tools_have_schema_output_and_annotations(self):
        tools = sap_integration_mcp.cpi_tools()
        names = {item["name"] for item in tools}
        self.assertEqual(len(names), 21)
        self.assertIn("cpi_undeploy_commit", names)
        self.assertIn("cpi_external_tools_status", names)
        for item in tools:
            self.assertEqual(item["inputSchema"]["type"], "object")
            self.assertEqual(item["outputSchema"]["type"], "object")
            self.assertEqual(
                set(item["annotations"]),
                {"title", "readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"},
            )

    def test_operational_failure_is_a_tool_error_not_protocol_error(self):
        result = sap_integration_mcp.tool_result(
            {"ok": False, "exit_code": 1, "result": {"status": "ERROR", "error": "missing config"}}
        )
        self.assertTrue(result["isError"])
        self.assertEqual(result["structuredContent"]["error"], "missing config")

    def test_stdio_initialize_list_and_read_only_call(self):
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2026-07-28"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "cpi_external_tools_status", "arguments": {}}},
        ]
        proc = subprocess.run(
            [sys.executable, "scripts/sap_integration_mcp.py", "--product", "cpi"],
            cwd=ROOT,
            input="".join(json.dumps(item) + "\n" for item in requests),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        messages = [json.loads(line) for line in proc.stdout.splitlines()]
        by_id = {item.get("id"): item for item in messages}
        self.assertEqual(by_id[1]["result"]["serverInfo"]["version"], "0.3.0")
        self.assertEqual(len(by_id[2]["result"]["tools"]), 21)
        self.assertIn("structuredContent", by_id[3]["result"])


if __name__ == "__main__":
    unittest.main()
