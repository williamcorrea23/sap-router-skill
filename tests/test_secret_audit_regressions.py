"""Secret checks ignore static templates but still catch synthetic secrets."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import secret_audit


class SecretAuditRegressionTest(unittest.TestCase):
    def test_static_api_key_xml_policy_template_is_not_a_credential(self):
        result = secret_audit.audit(["scripts/apim_proxy_packager.py"])
        false_positives = [item for item in result["findings"]
                           if Path(item["file"]).as_posix() == "scripts/apim_proxy_packager.py"
                           and item["kind"] == "sap_password_literal"]
        self.assertEqual(false_positives, [])

    def test_synthetic_password_remains_detected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            sample = root / "fixture.py"
            sample.write_text('PASSWORD = "AbCdEf123456789!"\n', encoding="utf-8")
            with mock.patch.object(secret_audit, "ROOT", root):
                result = secret_audit.audit(["fixture.py"])
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["actionable_findings_count"], 1)

    def test_credentials_embedded_in_policy_xml_remain_detected(self):
        sample = '''POLICY_VERIFY_API_KEY = """<?xml version="1.0"?>
<Config password="secretAbCdEf123456" api_key="RealAbCdEf123456"/>
<Token>sk-AbCdEf1234567890</Token>
"""
'''
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "policy.py").write_text(sample, encoding="utf-8")
            with mock.patch.object(secret_audit, "ROOT", root):
                result = secret_audit.audit(["policy.py"])
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["actionable_findings_count"], 3)

    def test_json_credential_keys_are_detected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "config.json").write_text('{"client_secret": "RealAbCdEf123456"}', encoding="utf-8")
            with mock.patch.object(secret_audit, "ROOT", root):
                result = secret_audit.audit(["config.json"])
        self.assertEqual(result["actionable_findings_count"], 1)


if __name__ == "__main__":
    unittest.main()
