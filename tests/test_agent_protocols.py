import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SKILLS = {"karpathy-guidelines", "loop-specification", "verification-loop"}
TERMINAL_STATES = {"Success", "No-Op", "Blocked", "Stalled", "Exhausted"}
EVIDENCE_FIELDS = {
    "check", "status", "verification_level", "command_or_tool", "target",
    "observed_result", "artifact_or_reference",
}


class AgentProtocolTests(unittest.TestCase):
    def test_every_canonical_profile_has_bounded_independent_execution_protocol(self):
        profiles = list((ROOT / ".agents/profiles").glob("*.json"))
        self.assertTrue(profiles, "Canonical profiles must be discoverable")
        for path in profiles:
            with self.subTest(profile=path.stem):
                profile = json.loads(path.read_text(encoding="utf-8"))
                protocol = profile.get("execution_protocols", {})
                self.assertEqual(protocol.get("schema_version"), 1)
                self.assertEqual(set(protocol.get("required_skills", [])), REQUIRED_SKILLS)
                loop = protocol.get("loop", {})
                self.assertEqual(loop.get("max_iterations"), 8)
                self.assertEqual(loop.get("max_seconds"), 900)
                self.assertEqual(loop.get("call_timeout_seconds"), 120)
                self.assertEqual(loop.get("max_stagnant_iterations"), 3)
                self.assertEqual(set(loop.get("terminal_states", [])), TERMINAL_STATES)
                self.assertEqual(loop.get("checkpoint_states"), ["PENDING_APPROVAL"])
                self.assertEqual(loop.get("maker_checker"), "fresh_process")
                self.assertEqual(loop.get("uncertain_mutation"), "reconcile_before_retry")
                verification = protocol.get("verification", {})
                self.assertEqual(set(verification.get("statuses", [])), {"PASS", "FAIL", "NOT_RUN"})
                self.assertEqual(verification.get("levels"), [1, 2, 3, 4, 5])
                self.assertEqual(set(verification.get("required_evidence", [])), EVIDENCE_FIELDS)
                self.assertEqual(verification.get("not_run_requires"), "reason")
                self.assertEqual(verification.get("live_sap_requires"), "field_response_for_requested_target")

    def test_required_protocol_skills_are_available_in_canonical_source(self):
        for skill in REQUIRED_SKILLS:
            with self.subTest(skill=skill):
                self.assertTrue((ROOT / ".agents/skills" / skill / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
