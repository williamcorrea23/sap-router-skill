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
from sap_router_core.registry import classify_task, load_servers, validate_catalog
from source_catalog import INDEX_FILE, load, score_asset


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

    def test_mcp_config_preserves_only_reviewed_or_fail_closed_candidates(self):
        configured = set(json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers", {}))
        candidates = json.loads((ROOT / ".agents" / "registries" / "mcp-candidates.json").read_text(encoding="utf-8"))
        candidate_ids = {item["id"] for item in candidates["candidates"]}
        self.assertTrue(configured.issubset(set(load_servers()) | candidate_ids))
        self.assertEqual(configured - set(load_servers()), candidate_ids)
        self.assertTrue(all(item["status"] == "disabled_candidate" for item in candidates["candidates"]))

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
