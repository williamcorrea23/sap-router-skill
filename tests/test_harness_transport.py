"""Offline regression checks for the harness contract and MCP boundary."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import harness_contracts as contracts
from harness_mcp_client import McpClient, McpProtocolError
import sap_integration_mcp


FIXTURE = '''import json, sys, time, subprocess, os
mode = sys.argv[1]
pid_file = sys.argv[2] if len(sys.argv) > 2 else None
for line in sys.stdin:
    request = json.loads(line)
    if "id" not in request:
        continue
    method = request["method"]
    if mode == "hang" and method == "tools/list":
        time.sleep(30)
    if mode == "oversize" and method == "tools/list":
        sys.stdout.write("x" * (1024 * 1024 + 2) + "\\n")
        sys.stdout.flush()
        continue
    if method == "initialize":
        result = {"protocolVersion":"2024-11-05", "capabilities":{"tools":{}}, "serverInfo":{"name":"offline-fixture","version":"1"}}
        if mode == "write-block":
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if pid_file:
                with open(pid_file, "w", encoding="ascii") as stream:
                    stream.write(str(child.pid))
    elif method == "tools/list":
        if mode == "orphan":
            subprocess.Popen([sys.executable, "-c", "import time; time.sleep(6)"], stdout=sys.stdout, stderr=sys.stderr, stdin=subprocess.DEVNULL)
        result = {"tools":[{"name":"fixture_read", "inputSchema":{"type":"object", "properties":{"id":{"type":"string"}}, "required":["id"], "additionalProperties":False}}]}
    elif method == "tools/call":
        result = {"structuredContent":{"item":{"Id":request["params"]["arguments"]["id"]}}}
    else:
        result = {}
    sys.stdout.write(json.dumps({"jsonrpc":"2.0", "id":request["id"], "result":result}) + "\\n")
    sys.stdout.flush()
    if mode == "write-block" and method == "initialize":
        time.sleep(30)
        break
    if mode == "orphan" and method == "tools/list":
        os._exit(0)
'''


class HarnessContractsTests(unittest.TestCase):
    def test_curated_contract_schemas_match_canonical_bridge(self):
        known = {t["name"]: t for t in sap_integration_mcp.cpi_tools() + sap_integration_mcp.apim_tools()}
        curated = contracts.load_contracts()
        self.assertGreaterEqual(len(curated), 4)
        for item in curated:
            with self.subTest(tool=item["tool"]):
                self.assertEqual(item["effect"], "read")
                self.assertEqual(item["input_schema"], known[item["tool"]]["inputSchema"])
                self.assertEqual(item["schema_sha256"], contracts.schema_hash(item["input_schema"]))
                self.assertTrue(item["result_assertions"])

    def test_profile_effect_and_schema_drift_fail_closed(self):
        contract = contracts.load_contracts()[0]
        cap = {"id": contract["capability"], "effect": "read"}
        server = {"id": contract["server"], "status": "enabled", "capabilities": [cap["id"]]}
        profile = {"capabilities": {"allow": [cap["id"]], "gated": [], "deny": []}}
        contracts.validate_contract(contract, cap, server, profile)
        for override in ({"effect": "mutating"}, {"schema_sha256": "0" * 64}):
            broken = {**contract, **override}
            with self.assertRaises(ValueError):
                contracts.validate_contract(broken, cap, server, profile)
        with self.assertRaises(ValueError):
            contracts.validate_contract(contract, cap, {**server, "status": "disabled_candidate"}, profile)
        with self.assertRaises(ValueError):
            contracts.validate_contract(contract, cap, server, {"capabilities": {"allow": []}})

    def test_arguments_reject_extra_and_wrong_type(self):
        schema = {"type": "object", "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 200}}, "required": ["limit"], "additionalProperties": False}
        contracts.validate_arguments(schema, {"limit": 3})
        for args in ({"limit": True}, {"limit": 201}, {"limit": 3, "shell": "echo unsafe"}, {}):
            with self.assertRaises(ValueError):
                contracts.validate_arguments(schema, args)
        with self.assertRaises(ValueError):
            contracts.validate_arguments({"type": "number"}, float("nan"))

    def test_success_requires_actual_result_fields(self):
        contract = next(c for c in contracts.load_contracts() if c["tool"] == "cpi_packages")
        success = {"structuredContent": {"items": [{"Id": "Package1"}], "count": 1, "source": "cpi:IntegrationPackages", "exit_code": 0}}
        self.assertTrue(contracts.verify_result(contract, success)[0])
        for result in ({"structuredContent": {"status": "OK"}}, {"structuredContent": {"items": [], "count": 1, "source": "cpi:IntegrationPackages"}}, {**success, "isError": True}):
            self.assertFalse(contracts.verify_result(contract, result)[0])
        apim = next(c for c in contracts.load_contracts() if c["tool"] == "apim_proxies")
        self.assertTrue(contracts.verify_result(apim, {"structuredContent": {"status": "OK", "http_status": 200, "body": json.dumps({"d": {"results": [{"Name": "P1"}]}})}})[0])
        self.assertFalse(contracts.verify_result(apim, {"structuredContent": {"status": "OK", "http_status": 200, "body": "<html>login</html>"}})[0])


class McpTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sap-harness-transport-")
        self.addCleanup(self.tmp.cleanup)
        self.fixture = Path(self.tmp.name) / "fixture.py"
        self.fixture.write_text(FIXTURE, encoding="utf-8")

    def client(self, mode="normal", timeout=5, *extra):
        return McpClient("offline-fixture", timeout=timeout,
                         command=[sys.executable, str(self.fixture), mode, *map(str, extra)])

    def test_initialize_list_call_and_cleanup(self):
        with self.client() as client:
            self.assertEqual(client.tools()[0]["name"], "fixture_read")
            response = client.call("fixture_read", {"id": "X1"})
            self.assertEqual(response["structuredContent"]["item"]["Id"], "X1")
            process = client.process
        self.assertIsNotNone(process.poll())

    def test_timeout_closes_transport(self):
        with self.client("hang", timeout=2) as client:
            client.timeout = 0.2
            with self.assertRaises(TimeoutError):
                client.tools()
            self.assertIsNotNone(client.process.poll())

    def test_blocked_stdin_write_obeys_deadline_and_kills_process_tree(self):
        pid_file = Path(self.tmp.name) / "child.pid"
        with self.client("write-block", 3, pid_file) as client:
            child_pid = int(pid_file.read_text(encoding="ascii"))
            child_handle = None
            kernel = None
            if os.name == "nt":
                import ctypes
                from ctypes import wintypes

                kernel = ctypes.WinDLL("kernel32", use_last_error=True)
                kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
                kernel.OpenProcess.restype = wintypes.HANDLE
                kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
                kernel.WaitForSingleObject.restype = wintypes.DWORD
                kernel.CloseHandle.argtypes = [wintypes.HANDLE]
                kernel.CloseHandle.restype = wintypes.BOOL
                child_handle = kernel.OpenProcess(0x00100000, False, child_pid)  # SYNCHRONIZE
                self.assertTrue(child_handle, "could not open fixture child process")
                self.addCleanup(kernel.CloseHandle, child_handle)
            client.timeout = 0.4
            errors = []

            def request():
                try:
                    client._request("tools/call", {"blob": "x" * 512_000})
                except BaseException as exc:
                    errors.append(exc)

            started = time.monotonic()
            worker = threading.Thread(target=request, daemon=True)
            worker.start()
            worker.join(1.5)
            still_blocked = worker.is_alive()
            if still_blocked:
                client.close()
                worker.join(2)
            elapsed = time.monotonic() - started
            process = client.process
            self.assertFalse(still_blocked, "MCP request remained blocked while writing stdin")
            self.assertIsInstance(errors[0], TimeoutError)
            self.assertLess(elapsed, 1.2)
            self.assertIsNotNone(process.poll())
            if os.name == "nt":
                self.assertEqual(kernel.WaitForSingleObject(child_handle, 1000), 0)
            else:
                with self.assertRaises(ProcessLookupError):
                    os.kill(child_pid, 0)

    def test_oversized_response_closes_transport(self):
        with self.client("oversize") as client:
            with self.assertRaises(McpProtocolError):
                client.tools()
            self.assertIsNotNone(client.process.poll())

    def test_unlisted_tool_is_rejected(self):
        with self.client() as client:
            with self.assertRaises(ValueError):
                client.call("unreviewed_tool", {})

    def test_cleanup_kills_descendants_after_launcher_exit(self):
        with self.client("orphan") as client:
            client.tools()
            client.process.wait(timeout=2)
            started = time.monotonic()
            client.close()
            self.assertLess(time.monotonic() - started, 3)


if __name__ == "__main__":
    unittest.main()
