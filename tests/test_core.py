import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python"))

from sap_router import SapRouter
from sap_router_core.registry import classify_task, validate_catalog


class RouterContractsTest(unittest.TestCase):
    def test_functional_write_is_gated(self):
        route = SapRouter().get_route("MM_CREATE_MATERIAL")
        self.assertEqual(route["strategy"], "needs-functional-context")

    def test_functional_route_is_classified_without_execution(self):
        route = SapRouter().get_route("MM_CREATE_MATERIAL", functional_context=True)
        self.assertEqual(route["strategy"], "bapi-functional")
        self.assertEqual(route["bapi"], "BAPI_MATERIAL_SAVEDATA")

    def test_catalog_is_valid(self):
        result = validate_catalog()
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["counts"]["capabilities"], 0)

    def test_classifier_requires_confirmation_for_mutation(self):
        decision = classify_task("deploy api proxy to DEV")
        self.assertEqual(decision["capability"], "sap.apim.proxy.deploy")

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
