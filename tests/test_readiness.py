import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'python')]
import healthcheck
from sap_router_core import registry


class ReadinessTest(unittest.TestCase):
    def test_offline_uses_only_canonical_active_servers_without_launching(self):
        checker = healthcheck.HealthChecker(verbose=False)
        checker.offline = True
        checker.read_only = True
        with mock.patch('subprocess.Popen', side_effect=AssertionError('offline launch')), \
             mock.patch('subprocess.run', side_effect=AssertionError('offline launch')):
            result = checker.run_full_check()
        active = {k for k, v in registry.load_servers().items() if v['status'] == 'enabled'}
        self.assertEqual(set(result['mcp_checks']), active)
        self.assertFalse(any(v['status'] == 'READY' for v in result['mcp_checks'].values()))
        self.assertIn('planned', result['inventory'])

    def test_read_only_never_creates_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            checker = healthcheck.HealthChecker(project_root=temp, verbose=False)
            checker.offline = True
            checker.read_only = True
            checker.run_full_check()
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_handshake_alone_cannot_prove_remote_domain(self):
        with mock.patch.dict(os.environ, {'SAP_ALLOW_UNAUTHORIZED': 'false'}, clear=True), \
             mock.patch.object(registry, '_env_status', return_value='ALL_SET'), \
             mock.patch.object(registry, '_run_jsonrpc_stdio', return_value={
                 'initialize': 'PASS', 'tools_list': 'PASS', 'error': None,
                 'domain_probe': 'NOT_PROVED'}):
            result = registry.probe_server('sap-cpi-mcp', execute=True)
        self.assertNotEqual(result['status'], 'READY')
        self.assertEqual(result['capabilities_ready'], [])

    def test_insecure_tls_blocks_execution(self):
        with mock.patch.dict(os.environ, {'SAP_ALLOW_UNAUTHORIZED': 'true'}, clear=True), \
             mock.patch.object(registry, '_run_jsonrpc_stdio') as launch:
            result = registry.probe_server('aibap', execute=True)
        launch.assert_not_called()
        self.assertEqual(result['error_code'], 'TLS_VERIFICATION_REQUIRED')

    def test_package_runner_is_not_launched_by_probe(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(registry, '_run_jsonrpc_stdio') as launch:
            result = registry.probe_server('ui5-mcp', execute=True)
        launch.assert_not_called()
        self.assertEqual(result['error_code'], 'LOCAL_RUNTIME_REQUIRED')

    def test_registered_planned_server_cannot_launch(self):
        import mcp_launcher
        with mock.patch('subprocess.call') as call, mock.patch('sys.stderr'):
            self.assertEqual(mcp_launcher.run_server('smartform-ai-generator'), 2)
        call.assert_not_called()

    def test_semantic_errors_never_pass_as_success(self):
        from sap_router_core.probe_transport import domain_ok
        for server in ('cap-mcp', 'fiori-mcp', 'ui5-mcp', 'context-mode', 'arc-1', 'aibap', 'sap-cpi-mcp', 'sap-apim-mcp'):
            with self.subTest(server=server):
                self.assertFalse(domain_ok({'isError': True, 'content': [{'type': 'text', 'text': 'context-mode Error'}]}, server))
        self.assertFalse(domain_ok({'structuredContent': {'status': 'OK', 'body': '<html>Login</html>'}}, 'sap-apim-mcp'))

    def test_healthy_probe_does_not_grant_mutation_capability(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(registry, '_run_jsonrpc_stdio', return_value={
                'initialize': 'PASS', 'tools_list': 'PASS', 'domain_probe': 'PASS', 'error': None}):
            result = registry.probe_server('sap-cpi-mcp', execute=True)
        self.assertEqual(result['status'], 'READY')
        self.assertFalse(result['mutation_ready'])
        self.assertNotIn('sap.cpi.artifact.deploy', result['capabilities_ready'])


if __name__ == '__main__':
    unittest.main()
