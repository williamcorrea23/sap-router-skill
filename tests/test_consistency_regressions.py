"""Regression coverage for Router, MCP and skill-agent catalog consistency."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

os.environ.setdefault("SAP_ROUTER_OFFLINE", "1")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "python"))

import mcp_launcher
import sap_harness
import source_catalog
import validate_catalog
import harness_contracts
from sap_router_core import registry as router_registry


class McpCapabilityConsistencyTest(unittest.TestCase):
    def test_routed_capabilities_resolve_without_key_error(self):
        routed = {
            "sap.adt.source.read",
            "sap.gui.transaction.execute",
            "sap.btp.account.read",
            "sap.successfactors.data.read",
            "sap.documentation.search",
        }
        for capability in sorted(routed):
            with self.subTest(capability=capability):
                result = mcp_launcher.list_capability(capability)
                self.assertIn(capability, result)
                self.assertNotIn("error", result[capability])

    def test_unknown_capability_is_a_structured_block(self):
        result = mcp_launcher.list_capability("sap.unknown.capability")
        self.assertIn("sap.unknown.capability", result)
        self.assertEqual(result["sap.unknown.capability"].get("error"), "unknown-capability")
        self.assertIsNone(result["sap.unknown.capability"].get("selected"))

    def test_mcp_effect_matches_canonical_capability(self):
        result = mcp_launcher.list_capability("sap.cap.project.build")["sap.cap.project.build"]
        self.assertTrue(result["mutation"])
        self.assertTrue(result["requires_approval"])

    def test_strict_catalog_rejects_effect_and_approval_drift(self):
        capabilities = {"sap.cap.project.build": {"id": "sap.cap.project.build", "effect": "mutating"}}
        mcp_specs = {"sap.cap.project.build": {"primary": "cap-mcp", "fallbacks": [],
                                                "mutation": False, "requires_approval": False}}
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(router_registry, "load_capabilities", return_value=capabilities))
            stack.enter_context(mock.patch.object(router_registry, "load_mcp_capability_specs", return_value=mcp_specs))
            stack.enter_context(mock.patch.object(router_registry, "load_servers", return_value={}))
            stack.enter_context(mock.patch.object(router_registry, "load_routes", return_value=[]))
            stack.enter_context(mock.patch.object(router_registry, "load_profiles", return_value={}))
            result = router_registry.validate_catalog()
        self.assertTrue(any("effect mismatch" in error for error in result["errors"]))

    def test_strict_catalog_rejects_route_without_profile_permission(self):
        capabilities = {"sap.documentation.search": {"id": "sap.documentation.search", "effect": "read"}}
        routes = [{"match": ["basis"], "capability": "sap.documentation.search", "profile": "sap-basis-consultant"}]
        profiles = {"sap-basis-consultant": {"id": "sap-basis-consultant", "capabilities": {
            "allow": [], "gated": [], "deny": []}}}
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(router_registry, "load_capabilities", return_value=capabilities))
            stack.enter_context(mock.patch.object(router_registry, "load_mcp_capability_specs", return_value={}))
            stack.enter_context(mock.patch.object(router_registry, "load_servers", return_value={}))
            stack.enter_context(mock.patch.object(router_registry, "load_routes", return_value=routes))
            stack.enter_context(mock.patch.object(router_registry, "load_profiles", return_value=profiles))
            result = router_registry.validate_catalog()
        self.assertTrue(any("route permission missing" in error for error in result["errors"]))

    def test_routed_read_profiles_allow_their_capability(self):
        profile_rights = {
            "sap-btp-devops-engineer": "sap.btp.account.read",
            "sap-hcm-consultant": "sap.successfactors.data.read",
            "sap-basis-consultant": "sap.documentation.search",
        }
        for profile_id, capability in profile_rights.items():
            with self.subTest(profile=profile_id):
                data = json.loads((ROOT / ".agents" / "profiles" / f"{profile_id}.json").read_text(encoding="utf-8"))
                self.assertIn(capability, data["capabilities"].get("allow", []))


class HarnessToolContractCatalogTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="harness-contract-catalog-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        registry = self.root / ".agents/registries"
        profiles = self.root / ".agents/profiles"
        registry.mkdir(parents=True)
        profiles.mkdir(parents=True)
        schema = {"type": "object", "properties": {}, "additionalProperties": False}
        self.data = {
            "capabilities.json": {"capabilities": [{"id": "fixture.read", "effect": "read"}]},
            "mcps.json": {"servers": [{"id": "fixture-mcp", "status": "enabled", "capabilities": ["fixture.read"]}]},
            "mcp-capabilities.json": {"capabilities": {"fixture.read": {
                "primary": "fixture-mcp", "fallbacks": [], "mutation": False, "requires_approval": False}}},
            "harness-tool-contracts.json": {"schema_version": 1, "policy": {
                "runtime_fetch": False, "requires_reviewed_schema": True, "real_effects": ["read"]},
                "contracts": [{"id": "fixture-read", "status": "reviewed", "capability": "fixture.read",
                    "server": "fixture-mcp", "tool": "read_fixture", "effect": "read", "approval_mode": "none",
                    "input_schema": schema, "schema_sha256": harness_contracts.schema_hash(schema),
                    "result_assertions": [{"path": "Id", "nonempty": True}]}]},
        }
        for name, value in self.data.items():
            (registry / name).write_text(json.dumps(value), encoding="utf-8")
        profile = {"id": "fixture-agent", "capabilities": {"allow": ["fixture.read"], "gated": [], "deny": []}}
        (profiles / "fixture-agent.json").write_text(json.dumps(profile), encoding="utf-8")

    def save(self, name, value):
        path = self.root / ".agents/registries" / name
        path.write_text(json.dumps(value), encoding="utf-8")

    def contract_registry(self):
        return json.loads((self.root / ".agents/registries/harness-tool-contracts.json").read_text(encoding="utf-8"))

    def test_valid_reviewed_contract_passes(self):
        self.assertEqual(validate_catalog.validate_harness_contracts(self.root), [])

    def test_strict_catalog_command_includes_contract_validation(self):
        mcp = self.root / ".mcp.json"
        mcp.write_text(json.dumps({"mcpServers": {"fixture-mcp": {"command": "fixture"}}}), encoding="utf-8")
        registry_root = self.root / ".agents/registries"
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(validate_catalog, "ROOT", self.root))
            stack.enter_context(mock.patch.object(validate_catalog, "REGISTRIES", registry_root))
            stack.enter_context(mock.patch.object(validate_catalog, "REGISTRY", registry_root / "mcp-capabilities.json"))
            stack.enter_context(mock.patch.object(validate_catalog, "MCP_CONFIG", mcp))
            stack.enter_context(mock.patch.object(validate_catalog, "SKILLS_DIR", self.root / ".agents/skills"))
            stack.enter_context(mock.patch.object(validate_catalog, "reconcile_catalogue", return_value=[]))
            invalid = self.contract_registry()
            invalid["contracts"][0]["effect"] = "mutating"
            self.save("harness-tool-contracts.json", invalid)
            result = validate_catalog.validate(strict=True)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("harness contract" in error for error in result["errors"]))

    def test_strict_catalog_rejects_hash_effect_capability_server_duplicate_and_policy_drift(self):
        cases = [
            ("schema-hash", lambda data: data["contracts"][0].update(schema_sha256="0" * 64)),
            ("effect", lambda data: data["contracts"][0].update(effect="mutating")),
            ("capability", lambda data: data["contracts"][0].update(capability="fixture.unknown")),
            ("server", lambda data: data["contracts"][0].update(server="fixture-unknown")),
            ("duplicate", lambda data: data["contracts"].append(dict(data["contracts"][0]))),
            ("policy", lambda data: data["policy"].update(runtime_fetch=True)),
        ]
        for name, mutate in cases:
            with self.subTest(name=name):
                data = self.contract_registry()
                mutate(data)
                self.save("harness-tool-contracts.json", data)
                errors = validate_catalog.validate_harness_contracts(self.root)
                self.assertTrue(errors, f"{name} drift passed strict contract validation")
                self.save("harness-tool-contracts.json", self.data["harness-tool-contracts.json"])


class PythonFloorConsistencyTest(unittest.TestCase):
    def test_harness_and_router_entry_points_require_python_311(self):
        documents = {
            ROOT / "AGENTS.md": "Requires Python 3.11+",
            ROOT / ".agents/skills/run-sap-router-skill/SKILL.md": "Python 3.11+",
            ROOT / ".agents/skills/run-sap-router-skill/MANIFEST.json": '"runtime": "python>=3.11"',
            ROOT / ".agents/skills/sap-workflow-pipeline/SKILL.md": "Python 3.11+",
            ROOT / ".agents/skills/sap-claude-skills/SKILL.md": "Python 3.11+",
            ROOT / ".agents/skills/superclaude-for-sap/SKILL.md": "Python 3.11+",
            ROOT / ".agents/skills/sap-bapi-integration/SKILL.md": "Python 3.11+",
        }
        for path, marker in documents.items():
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIn(marker, path.read_text(encoding="utf-8"))


class AgentAliasConsistencyTest(unittest.TestCase):
    def test_specialized_agents_use_installed_profiles_and_skills(self):
        for alias, agent in sap_harness.SPECIALIZED_AGENTS.items():
            with self.subTest(agent=alias):
                profile_id = agent.get("profile")
                self.assertTrue(profile_id, f"{alias} has no canonical profile")
                self.assertTrue((ROOT / ".agents" / "profiles" / f"{profile_id}.json").is_file())
                for skill_id in agent["skills"]:
                    self.assertTrue(
                        (ROOT / ".agents" / "skills" / skill_id / "SKILL.md").is_file(),
                        f"{alias} references missing skill {skill_id}",
                    )


class HarnessCandidateCatalogTest(unittest.TestCase):
    def test_current_candidate_registry_overrides_cached_status_and_revision(self):
        current = source_catalog.harness_candidate_assets()[0]
        cached = dict(current, status="enabled", trust="reviewed", revision="0" * 40)
        removed = dict(cached, id="removed-harness-candidate")
        with tempfile.TemporaryDirectory() as raw:
            index = Path(raw) / "index.json"
            index.write_text(json.dumps({"assets": [cached, removed]}), encoding="utf-8")
            output = io.StringIO()
            with mock.patch.object(source_catalog, "INDEX_FILE", index), contextlib.redirect_stdout(output):
                source_catalog.search("SAP Router harness", "knowledge", None, 100)
        candidates = {item["id"]: item for item in json.loads(output.getvalue())["results"]}
        self.assertEqual(candidates[current["id"]]["status"], "disabled_candidate")
        self.assertEqual(candidates[current["id"]]["trust"], "disabled_candidate")
        self.assertEqual(candidates[current["id"]]["revision"], current["revision"])
        self.assertNotIn("removed-harness-candidate", candidates)

    def test_strict_catalog_rejects_unsafe_or_unverifiable_candidate_records(self):
        data = json.loads(source_catalog.HARNESS_CANDIDATES_FILE.read_text(encoding="utf-8"))
        invalid_values = (("revision", "not-a-sha"), ("status", "enabled"),
                          ("runtime_fetch", True), ("runtime_execution", True),
                          ("license", ""), ("license_evidence", ""))
        for field, value in invalid_values:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as raw:
                malformed = json.loads(json.dumps(data))
                malformed["candidates"][0][field] = value
                root = Path(raw)
                (root / "harness-candidates.json").write_text(json.dumps(malformed), encoding="utf-8")
                with contextlib.ExitStack() as stack:
                    stack.enter_context(mock.patch.object(router_registry, "REGISTRIES", root))
                    for loader, default in (("load_capabilities", {}), ("load_servers", {}),
                                            ("load_profiles", {}), ("load_routes", [])):
                        stack.enter_context(mock.patch.object(router_registry, loader, return_value=default))
                    result = router_registry.validate_catalog()
                self.assertTrue(any("harness candidate" in error for error in result["errors"]))

    def test_strict_catalog_rejects_duplicate_candidate_ids(self):
        data = json.loads(source_catalog.HARNESS_CANDIDATES_FILE.read_text(encoding="utf-8"))
        data["candidates"].append(dict(data["candidates"][0]))
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "harness-candidates.json").write_text(json.dumps(data), encoding="utf-8")
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(router_registry, "REGISTRIES", root))
                for loader, default in (("load_capabilities", {}), ("load_servers", {}),
                                        ("load_profiles", {}), ("load_routes", [])):
                    stack.enter_context(mock.patch.object(router_registry, loader, return_value=default))
                result = router_registry.validate_catalog()
        self.assertTrue(any("duplicate" in error for error in result["errors"]))

    def test_nine_candidates_are_searchable_revision_pinned_and_disabled(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = source_catalog.search("SAP CPI harness skill", "knowledge", None, 100)
        self.assertEqual(status, 0)
        results = json.loads(output.getvalue())["results"]
        expected = {
            "aliulashayir-sap-dev-toolkit",
            "logalitech-sap-mdk-skills",
            "etavioxy-sap-skills",
            "shrek-abaper-sap-functional-skill",
            "manoj-iflowdev-sap-cloud-integration-odata-api-v2-clients",
            "rameshvaranganti-sap-integration-assistant",
            "pietromezzaroba-sap-cpi-iflow",
            "carlosribeirodev-sap-skill-integrationsuite-zip-generation",
            "aztun-neru-hermes-pm-skill",
        }
        candidates = [item for item in results if item.get("trust") == "disabled_candidate"]
        self.assertEqual({item["id"] for item in candidates}, expected)
        for item in candidates:
            self.assertEqual(item["status"], "disabled_candidate")
            self.assertRegex(item.get("revision", ""), r"^[0-9a-f]{40}$")

    def test_external_sources_never_enter_enabled_server_registry(self):
        servers = json.loads((ROOT / ".agents" / "registries" / "mcps.json").read_text(encoding="utf-8"))["servers"]
        repositories = {item.get("source", {}).get("repository") for item in servers if item.get("status") == "enabled"}
        for url in (
            "https://github.com/aliulashayir/sap-dev-toolkit",
            "https://github.com/logalitech/sap-mdk-skills",
            "https://github.com/Etavioxy/sap-skills",
            "https://github.com/shrek-abaper/sap-functional-skill",
            "https://github.com/manoj-iflowdev/sap-cloud-integration-odata-api-v2-clients",
            "https://github.com/rameshvaranganti/sap-integration-assistant",
            "https://github.com/PietroMezzaroba/sap-cpi-iflow",
            "https://github.com/carlosribeirodev/sap-skill-integrationsuite-zip-generation",
            "https://github.com/aztun-neru/hermes-pm-skill",
        ):
            self.assertNotIn(url, repositories)


class AbapilotDevTargetProfileTest(unittest.TestCase):
    def test_abapilot_dev_profile_is_pinned_read_only_and_not_routable(self):
        registries = ROOT / ".agents" / "registries"
        profile_registry = json.loads((registries / "mcp-target-profiles.json").read_text(encoding="utf-8"))
        candidate_registry = json.loads((registries / "mcp-candidates.json").read_text(encoding="utf-8"))
        mcp_registry = json.loads((registries / "mcps.json").read_text(encoding="utf-8"))
        client_config = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        profile = next(item for item in profile_registry["profiles"] if item["id"] == "nicohern-abapilot-mcp-dev")
        candidate = next(item for item in candidate_registry["candidates"] if item["id"] == profile["candidate_id"])

        self.assertEqual(profile["target"]["environment"], "DEV")
        self.assertEqual(profile["status"], "blocked")
        self.assertEqual(profile["source"]["revision"], candidate["revision"])
        self.assertEqual(profile["source"]["npm_package"], "abapilot@1.0.6")
        self.assertEqual(candidate["status"], "disabled_candidate")
        self.assertNotIn(candidate["id"], {item["id"] for item in mcp_registry["servers"]})
        self.assertNotIn(candidate["id"], client_config.get("mcpServers", {}))
        self.assertEqual(profile["runtime"]["runtime_fetch"], False)
        self.assertEqual(profile["runtime"]["runtime_execution"], False)
        self.assertEqual(profile["auth"]["tls_insecure_allowed"], False)
        self.assertEqual(validate_catalog.validate_mcp_target_profiles(ROOT), [])

    def test_abapilot_profile_validator_rejects_write_tool_and_installer(self):
        for change in (
            lambda profile: profile["tool_policy"]["allowlist"].append("sap_write_code"),
            lambda profile: profile["runtime"].update(command="npx", runtime_fetch=True),
        ):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as raw:
                base = Path(raw)
                registry_dir = base / ".agents" / "registries"
                registry_dir.mkdir(parents=True)
                for name in ("mcp-candidates.json", "mcps.json"):
                    (registry_dir / name).write_bytes((ROOT / ".agents" / "registries" / name).read_bytes())
                (base / ".mcp.json").write_bytes((ROOT / ".mcp.json").read_bytes())
                data = json.loads((ROOT / ".agents" / "registries" / "mcp-target-profiles.json").read_text(encoding="utf-8"))
                change(data["profiles"][0])
                (registry_dir / "mcp-target-profiles.json").write_text(json.dumps(data), encoding="utf-8")
                errors = validate_catalog.validate_mcp_target_profiles(base)
                self.assertTrue(errors)
                self.assertTrue(any("ABAPilot" in error or "runtime" in error for error in errors))


class ImportedSkillConsistencyTest(unittest.TestCase):
    def test_sap_odata_cli_is_a_pinned_skill_only_import(self):
        import_registry = json.loads(
            (ROOT / ".agents" / "registries" / "skill-imports.json").read_text(encoding="utf-8")
        )
        source = next(item for item in import_registry["imports"] if item["id"] == "sap-odata-cli")
        skill_path = ROOT / source["canonical_skill_path"]
        skill_text = skill_path.read_text(encoding="utf-8")

        self.assertIn("sap-odata-cli", validate_catalog.skill_names())
        self.assertEqual(source["license"], "MIT")
        self.assertEqual(source["revision"], "146e3b8de0764e4cfecc5cba1643fe61b40cb4ee")
        self.assertFalse(source["cli_runtime_installed"])
        self.assertFalse(source["mcp_server_registered"])
        self.assertIn("read-only", skill_text)
        self.assertIn("Never run `sap-odata setup`", skill_text)
        self.assertEqual(validate_catalog.validate_skill_source_imports(ROOT), [])

    def test_skill_import_validator_rejects_implicit_mcp_runtime(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            (base / ".agents" / "registries").mkdir(parents=True)
            skill_dir = base / ".agents" / "skills" / "sap-odata-cli"
            skill_dir.mkdir(parents=True)
            for relative in (
                ".agents/registries/skill-imports.json",
                ".agents/skills/sap-odata-cli/SKILL.md",
                ".agents/skills/sap-odata-cli/LICENSE",
            ):
                (base / relative).write_bytes((ROOT / relative).read_bytes())
            registry_path = base / ".agents" / "registries" / "skill-imports.json"
            data = json.loads(registry_path.read_text(encoding="utf-8"))
            data["imports"][0]["mcp_server_registered"] = True
            registry_path.write_text(json.dumps(data), encoding="utf-8")
            errors = validate_catalog.validate_skill_source_imports(base)
        self.assertTrue(any("cannot imply installed runtime or MCP" in error for error in errors))


class DirectMcpInstallerRegressionTest(unittest.TestCase):
    def test_active_client_config_has_no_package_installer_commands(self):
        config = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
        unsafe = {"npx", "npm", "uvx", "pip", "pnpm", "bunx"}
        offenders = [name for name, item in config.get("mcpServers", {}).items()
                     if Path(item.get("command", "")).stem.lower() in unsafe]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
