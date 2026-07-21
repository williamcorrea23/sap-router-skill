"""Offline unit tests for the sap-skills-creator validator.

These tests never touch the network. Every fixture is written to a
`tempfile.TemporaryDirectory` and validated in isolation. The validator
module is loaded through ``importlib.util`` because the script file has a
``.py`` name that lives outside a normal package.

Run from the repository root:

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stdout


_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_VALIDATOR_PATH = (
    _REPO_ROOT
    / "skills"
    / "sap-skills-creator"
    / "scripts"
    / "validate_skill.py"
)


def _load_validator_module():
    module_name = "sap_skills_creator_validator_under_test"
    spec = importlib.util.spec_from_file_location(module_name, _VALIDATOR_PATH)
    assert spec and spec.loader, f"could not build import spec for {_VALIDATOR_PATH}"
    module = importlib.util.module_from_spec(spec)
    # Register before exec so introspection tools (e.g. dataclass) can resolve
    # the owning module via sys.modules[cls.__module__].
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator_module()


MINIMAL_FRONTMATTER = """---
name: example-skill
description: >-
  Guides an agent through a repeatable example workflow. Use when the user
  asks to run the example task and no MCP tool covers it.
license: Apache-2.0
compatibility: Requires filesystem access.
metadata:
  author: Example Author
  version: "1.0.0"
---

# Example Skill

Body content.
"""


def _write_skill(tmp_root: pathlib.Path, name: str, skill_md: str) -> pathlib.Path:
    skill_dir = tmp_root / "skills" / name
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
    (skill_dir / "assets").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    return skill_dir


class FrontmatterParserTests(unittest.TestCase):
    def test_valid_minimal_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", MINIMAL_FRONTMATTER)
            report = validator.run_validation(str(skill_dir), None)
            self.assertFalse(
                report.has_failures(),
                msg=validator._human_render(report),
            )

    def test_frontmatter_must_start_on_line_one(self):
        content = "\n" + MINIMAL_FRONTMATTER
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings}
            self.assertIn("frontmatter.parse", rules)

    def test_block_scalar_folded(self):
        text = MINIMAL_FRONTMATTER
        data, _ = validator.parse_frontmatter(text)
        self.assertIn("description", data)
        self.assertNotIn("\n", data["description"])
        self.assertIn("example workflow", data["description"])


class NameValidationTests(unittest.TestCase):
    def _make(self, name: str) -> str:
        return (
            "---\n"
            f"name: {name}\n"
            "description: Test. Use when running unit tests.\n"
            "---\n\n# Body\n"
        )

    def test_invalid_uppercase_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "Invalid-Name", self._make("Invalid-Name"))
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL}
            self.assertIn("frontmatter.name.pattern", rules)

    def test_name_directory_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "actual-dir", self._make("declared-name"))
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL}
            self.assertIn("frontmatter.name.directory_match", rules)

    def test_name_too_long(self):
        long_name = "a" + "-b" * 40  # over 64 chars
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), long_name, self._make(long_name))
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL}
            self.assertIn("frontmatter.name.length", rules)


class DescriptionValidationTests(unittest.TestCase):
    def test_missing_description_fails(self):
        content = "---\nname: example-skill\n---\n\n# Body\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL}
            self.assertIn("frontmatter.description.required", rules)

    def test_description_too_long(self):
        long = "x" * 1100
        content = (
            "---\n"
            "name: example-skill\n"
            f"description: {long}\n"
            "---\n\n# Body\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL}
            self.assertIn("frontmatter.description.length", rules)

    def test_vague_description_warns(self):
        content = (
            "---\n"
            "name: example-skill\n"
            "description: Use best practices when needed for a comprehensive solution.\n"
            "---\n\n# Body\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_WARN}
            self.assertIn("frontmatter.description.vague", rules)


class CompatibilityAndMetadataTests(unittest.TestCase):
    def test_compatibility_too_long(self):
        long = "y" * 600
        content = (
            "---\n"
            "name: example-skill\n"
            "description: Guides a task. Use when running it.\n"
            f"compatibility: {long}\n"
            "---\n\n# Body\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            rules = {f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL}
            self.assertIn("frontmatter.compatibility.length", rules)

    def test_metadata_non_string_value(self):
        content = (
            "---\n"
            "name: example-skill\n"
            "description: Guides a task. Use when running it.\n"
            "metadata:\n"
            "  author: Author\n"
            "  version: 1.0.0\n"  # unquoted numeric-like value
            "---\n\n# Body\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            failing_rules = [
                f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL
            ]
            self.assertNotIn(
                "frontmatter.metadata.value_type", failing_rules,
                msg="quoted string coercion still leaves the value as string",
            )
        # Now try a genuinely non-string value using YAML mapping syntax.
        content_bad = (
            "---\n"
            "name: example-skill\n"
            "description: Guides a task. Use when running it.\n"
            "metadata:\n"
            "  author: Author\n"
            "  version: true\n"
            "---\n\n# Body\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content_bad)
            report = validator.run_validation(str(skill_dir), None)
            failing_rules = [
                f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL
            ]
            self.assertIn("frontmatter.metadata.value_type", failing_rules)


class ProgressiveDisclosureTests(unittest.TestCase):
    def test_over_size_skill_md_fails(self):
        header = (
            "---\n"
            "name: example-skill\n"
            "description: Guides a task. Use when running it.\n"
            "---\n\n"
        )
        body = "\n".join(f"line {i}" for i in range(600))
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", header + body)
            report = validator.run_validation(str(skill_dir), None)
            failing_rules = [
                f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL
            ]
            self.assertIn("progressive_disclosure.skill_length", failing_rules)

    def test_unlinked_reference_warns(self):
        content = MINIMAL_FRONTMATTER
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            (skill_dir / "references" / "unused-topic.md").write_text(
                "# Not linked\n", encoding="utf-8"
            )
            report = validator.run_validation(str(skill_dir), None)
            warn_rules = [
                f.rule for f in report.findings if f.severity == validator.SEVERITY_WARN
            ]
            self.assertIn(
                "progressive_disclosure.unlinked_reference", warn_rules
            )


class LinkValidationTests(unittest.TestCase):
    def test_missing_relative_link_fails(self):
        content = MINIMAL_FRONTMATTER + "\n[Broken](references/missing.md)\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            failing_rules = [
                f.rule for f in report.findings if f.severity == validator.SEVERITY_FAIL
            ]
            self.assertIn("links.missing_target", failing_rules)


class SecurityHeuristicTests(unittest.TestCase):
    def test_verify_false_flagged(self):
        content = MINIMAL_FRONTMATTER + "\n```python\nsession.get(url, verify=False)\n```\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            warn_rules = [
                (f.rule, f.message) for f in report.findings
                if f.severity == validator.SEVERITY_WARN
            ]
            self.assertTrue(
                any("verify=False" in msg for _, msg in warn_rules),
                msg=str(warn_rules),
            )

    def test_placeholder_password_not_flagged(self):
        content = MINIMAL_FRONTMATTER + (
            "\nSet the password using setx SAP_DEV_DEVELOPER_PWD \"<password>\".\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            secret_findings = [
                f for f in report.findings
                if f.rule == "security.secret_heuristic"
            ]
            self.assertEqual(secret_findings, [])

    def test_secret_value_is_redacted(self):
        content = MINIMAL_FRONTMATTER + "\napi_key=ABCDEFG1234567890TAILVALUE\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            report = validator.run_validation(str(skill_dir), None)
            secret_findings = [
                f for f in report.findings
                if f.rule == "security.secret_heuristic"
            ]
            self.assertTrue(secret_findings)
            for finding in secret_findings:
                self.assertNotIn("ABCDEFG1234567890TAILVALUE", finding.message)


class JsonOutputAndExitCodeTests(unittest.TestCase):
    def test_json_output_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", MINIMAL_FRONTMATTER)
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = validator.main([str(skill_dir), "--json"])
            payload = json.loads(buf.getvalue())
            self.assertIn("counts", payload)
            self.assertIn("findings", payload)
            self.assertEqual(exit_code, 0)

    def test_failing_skill_returns_exit_code_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = "---\nname: wrong-name\ndescription: x. Use when needed.\n---\n\n# Body\n"
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", content)
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = validator.main([str(skill_dir), "--json"])
            self.assertEqual(exit_code, 1)


class StrictModeTests(unittest.TestCase):
    def test_strict_mode_treats_warning_as_failure(self):
        vague = (
            "---\n"
            "name: example-skill\n"
            "description: Use best practices as needed for a comprehensive solution.\n"
            "---\n\n# Body\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = _write_skill(pathlib.Path(tmp), "example-skill", vague)
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = validator.main([str(skill_dir), "--strict"])
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
