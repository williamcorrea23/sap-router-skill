"""Public command wiring for the controlled executor; no CLI/provider launched."""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'python'))
import sap_harness


class FakeExecutor:
    calls = []

    def __init__(self, backend, model):
        self.backend, self.model = backend, model

    def run(self, task, classification, skills, target):
        self.calls.append((self.backend, self.model, classification, skills, target))
        return {'state': 'Success', 'run_id': 'fixture-run', 'reason': 'verified-goal',
                'evidence': [{'level': 3, 'status': 'PASS', 'summary': 'field assertion'}]}


class HarnessCliTest(unittest.TestCase):
    def setUp(self):
        FakeExecutor.calls = []
        self.route = {'capability': 'sap.cpi.artifact.read', 'profile': 'sap-cpi-developer',
                      'selected_server': 'sap-cpi-mcp', 'selection_reason': 'fixture'}

    def test_plan_is_default_and_does_not_construct_executor(self):
        args = sap_harness.build_parser().parse_args(['run', '--task', 'read CPI packages'])
        with mock.patch('sap_router_core.registry.classify_task', return_value=dict(self.route)), \
             mock.patch.object(sap_harness.mcp_launcher, 'list_capability', return_value={
                 'sap.cpi.artifact.read': {'selected': 'sap-cpi-mcp', 'ready': [{'server': 'sap-cpi-mcp'}], 'blocked': []}}), \
             mock.patch.object(sap_harness, 'HarnessExecutor', side_effect=AssertionError('must stay plan-only')):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(sap_harness.cmd_run(args), 0)
        self.assertEqual(FakeExecutor.calls, [])

    def test_execution_requires_model_and_uses_selected_backend(self):
        args = sap_harness.build_parser().parse_args(['run', '--task', 'read CPI packages', '--execute'])
        with mock.patch('sap_router_core.registry.classify_task', return_value=dict(self.route)), \
             mock.patch.object(sap_harness.mcp_launcher, 'list_capability', return_value={
                 'sap.cpi.artifact.read': {'selected': 'sap-cpi-mcp', 'ready': [{'server': 'sap-cpi-mcp'}], 'blocked': []}}), \
             mock.patch.object(sap_harness.source_catalog, 'search', side_effect=lambda *args: print(json.dumps({
                 'results': [{'name': 'cpi-iflow-development', 'trust': 'canonical', 'status': 'enabled'}]}))), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sap_harness.cmd_run(args), 2)
        self.assertEqual(FakeExecutor.calls, [])

        args = sap_harness.build_parser().parse_args(['run', '--task', 'read CPI packages', '--execute',
                                                       '--backend', 'claude', '--model', 'fixture-model'])
        with mock.patch('sap_router_core.registry.classify_task', return_value=dict(self.route)), \
             mock.patch.object(sap_harness.mcp_launcher, 'list_capability', return_value={
                 'sap.cpi.artifact.read': {'selected': 'sap-cpi-mcp', 'ready': [{'server': 'sap-cpi-mcp'}], 'blocked': []}}), \
             mock.patch.object(sap_harness.source_catalog, 'search', side_effect=lambda *args: print(json.dumps({
                 'results': [{'name': 'cpi-iflow-development', 'trust': 'canonical', 'status': 'enabled'}]}))), \
             mock.patch.object(sap_harness, 'HarnessExecutor', FakeExecutor), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sap_harness.cmd_run(args), 0)
        self.assertEqual(FakeExecutor.calls[0][:2], ('claude', 'fixture-model'))
        self.assertEqual(FakeExecutor.calls[0][3], ['cpi-iflow-development'])


if __name__ == '__main__':
    unittest.main()
