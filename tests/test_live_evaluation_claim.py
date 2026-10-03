"""A configured URL alone cannot prove a live ZROUTER integration."""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import harness_eval_suite


class LiveEvaluationClaimTest(unittest.TestCase):
    def test_url_environment_variable_alone_does_not_pass_live_domain_check(self):
        with mock.patch.dict(os.environ, {"ZROUTER_BASE_URL": "https://not-contacted.invalid"}):
            result = harness_eval_suite.eval_zrouter_fs_contract(live=True)
        self.assertNotEqual(result["status"], "PASS")
        self.assertIn("NOT_RUN", result.get("details", {}).get("live_dispatch", ""))


if __name__ == "__main__":
    unittest.main()
