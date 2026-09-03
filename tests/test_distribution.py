import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import generate_ide_assets as assets
import sync_codex_config as config


class DistributionTest(unittest.TestCase):
    def test_scoped_sync_preserves_unowned_files_and_global_instructions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source'
            (source / 'test-skill').mkdir(parents=True)
            (source / 'test-skill/SKILL.md').write_text('new')
            dest = root / '.codex/skills'
            (dest / 'test-skill').mkdir(parents=True)
            (dest / 'test-skill/SKILL.md').write_text('old')
            (dest / 'test-skill/personal.md').write_text('keep')
            (dest.parent / 'AGENTS.md').write_text('personal instructions')
            with mock.patch.object(assets, 'CANONICAL_SKILLS', source), \
                 mock.patch.object(assets, 'GLOBAL_SKILLS_TARGETS', {'codex': dest}):
                result = assets.sync_global_skills(['codex'])['codex']
            self.assertEqual(result['diffs'], [])
            self.assertEqual((dest / 'test-skill/personal.md').read_text(), 'keep')
            self.assertEqual((dest.parent / 'AGENTS.md').read_text(), 'personal instructions')
            self.assertEqual((Path(result['backup']) / 'test-skill/SKILL.md').read_text(), 'old')

    def test_config_removes_only_retired_entries_and_avoids_global_alias(self):
        existing = '[features]\ncustom = true\n[mcp_servers.personal]\ncommand = "mine"\n[mcp_servers.ci-mcp-server]\ncommand = "old"\n'
        servers = [{'id': 'aibap', 'status': 'enabled'}, {'id': 'sap-cpi-mcp', 'status': 'enabled'}]
        out, aliases = config.render(existing, servers, {'mcp_servers': {'aibap-39912': {'command': 'aibap.mcp'}}})
        self.assertIn('custom = true', out)
        self.assertIn('command = "mine"', out)
        self.assertNotIn('ci-mcp-server', out)
        self.assertEqual(aliases, {'aibap': 'aibap-39912'})
        self.assertIn('sap-cpi-mcp', out)
