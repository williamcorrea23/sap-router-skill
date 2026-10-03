"""Controlled execution gates, exercised without providers or SAP credentials."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'python'))
import harness_executor as execution
import approval_broker
import mcp_launcher


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def contains_secret(value, secret):
    if isinstance(value, dict):
        return any(contains_secret(item, secret) for item in value.values())
    if isinstance(value, list):
        return any(contains_secret(item, secret) for item in value)
    if isinstance(value, str):
        if secret in value:
            return True
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return False
        return decoded != value and contains_secret(decoded, secret)
    return False


class FakeBackend:
    def __init__(self, proposal=None, goal_met=True):
        self.proposal = proposal or {'kind': 'call', 'contract_id': 'fixture-read',
                                     'arguments': {}, 'target': 'DEV'}
        self.calls = []
        self.goal_met = goal_met

    def invoke(self, role, payload, schema, timeout):
        self.calls.append((role, payload))
        if role == 'maker':
            return self.proposal.copy()
        return {'accepted': True, 'goal_met': self.goal_met if role == 'result_checker' else False,
                'no_change_needed': False, 'reason': 'field checked'}


class FakeClient:
    calls = []
    schema = {'type': 'object', 'properties': {}, 'additionalProperties': False}
    tools_hook = None

    def __init__(self, server_id, timeout=30):
        self.server_id = server_id

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def tools(self):
        if type(self).tools_hook:
            type(self).tools_hook()
        return [{'name': 'fixture', 'inputSchema': self.schema}]

    def call(self, tool, arguments):
        self.calls.append((tool, arguments))
        return {'structuredContent': {'Id': 'DEV'}, 'content': []}


class HarnessExecutionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        FakeClient.calls = []
        FakeClient.schema = {'type': 'object', 'properties': {}, 'additionalProperties': False}
        FakeClient.tools_hook = None
        self.state = self.root / 'state'
        self.registry = self.root / '.agents' / 'registries'
        self.registry.mkdir(parents=True)
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts' / 'source_catalog.py').write_text('# local\n')
        self.capability = {'id': 'fixture.read', 'effect': 'read'}
        self.server = {'id': 'fixture-mcp', 'status': 'enabled', 'capabilities': ['fixture.read'],
                       'runtime': {'command': sys.executable, 'args': []}}
        self.profile = {'id': 'fixture-agent', 'capabilities': {'allow': ['fixture.read'], 'gated': [], 'deny': []}}
        profiles = self.root / '.agents' / 'profiles'
        profiles.mkdir()
        (profiles / 'fixture-agent.json').write_text(json.dumps(self.profile))
        self.contract = {'id': 'fixture-read', 'capability': 'fixture.read', 'server': 'fixture-mcp',
                         'tool': 'fixture', 'effect': 'read', 'status': 'reviewed',
                         'input_schema': FakeClient.schema, 'schema_sha256': digest(FakeClient.schema),
                         'result_assertions': [{'path': 'Id', 'nonempty': True}]}
        self.classification = {'capability': 'fixture.read', 'profile': 'fixture-agent',
                               'selected_server': 'fixture-mcp'}
        self.backend = FakeBackend()
        FakeClient.calls = []
        self.save_catalog()

    def tearDown(self):
        self.temp.cleanup()

    def save_catalog(self):
        for name, value in {
            'capabilities.json': {'capabilities': [self.capability]},
            'mcps.json': {'servers': [self.server]},
            'mcp-capabilities.json': {'capabilities': {self.capability['id']: {
                'primary': self.server['id'], 'fallbacks': [], 'mutation': self.capability['effect'] != 'read',
                'requires_approval': self.capability['effect'] != 'read'}}},
            'routes.json': {'routes': [{'capability': self.capability['id'], 'profile': self.profile['id']}]},
            'harness-tool-contracts.json': {'schema_version': 1, 'contracts': [self.contract]},
        }.items():
            (self.registry / name).write_text(json.dumps(value), encoding='utf-8')
        (self.root / '.agents/profiles/fixture-agent.json').write_text(json.dumps(self.profile))
        for name in ['fixture-skill', 'karpathy-guidelines', 'loop-specification', 'verification-loop']:
            path = self.root / '.agents/skills' / name
            path.mkdir(parents=True, exist_ok=True)
            (path / 'SKILL.md').write_text('---\nname: '+name+'\n---\nLocal procedure\n')

    def engine(self, **kwargs):
        return execution.HarnessExecutor('codex', 'fixture-model', root=self.root, state_dir=self.state,
                                          adapter=self.backend, client_factory=FakeClient, **kwargs)

    def run_task(self, **kwargs):
        return self.engine(**kwargs).run('read DEV', self.classification, ['fixture-skill'], 'DEV')

    def test_read_requires_field_and_fresh_checker_then_succeeds(self):
        run = self.run_task()
        self.assertEqual(run['state'], 'Success', run)
        self.assertEqual(len(FakeClient.calls), 1)
        self.assertEqual([x[0] for x in self.backend.calls], ['maker', 'checker', 'result_checker'])
        self.assertTrue(run['evidence'])
        self.assertEqual(self.engine().status(run['run_id'])['state'], 'Success')

    def test_credentials_in_structured_and_text_results_never_reach_checker_or_state(self):
        cases = []
        for source in ('content', 'structuredContent'):
            secret = f'c1-{source}-secret-"quoted"-\\tail-not-in-env'
            fields = {'Id': 'DEV', 'nested': {'refresh_token': secret}}
            if source == 'structuredContent':
                result = {'structuredContent': fields, 'content': []}
            else:
                result = {'content': [{'type': 'text', 'text': json.dumps(fields)}]}
            cases.append((source, secret, result))

        for source, secret, result in cases:
            with self.subTest(source=source):
                self.assertNotIn(secret, os.environ.values())
                with mock.patch.object(FakeClient, 'call', return_value=result):
                    run = self.run_task()
                persisted = self.engine().path(run['run_id']).read_text(encoding='utf-8')
                checker_payloads = [payload for role, payload in self.backend.calls if role in {'checker', 'result_checker'}]
                evidence = next(item for item in run['evidence'] if item.get('level') == 3)
                self.assertFalse(contains_secret(checker_payloads, secret))
                self.assertFalse(contains_secret(json.loads(persisted), secret))
                self.assertFalse(contains_secret(run, secret))
                self.assertEqual(evidence['result_hash'], digest(execution.sanitize(result)))

    def test_schema_drift_blocks_before_tool_call(self):
        FakeClient.schema = {'type': 'object'}
        run = self.run_task()
        self.assertEqual(run['state'], 'Blocked')
        self.assertEqual(FakeClient.calls, [])

    def test_unknown_tool_and_profile_deny_cannot_reach_mcp(self):
        self.backend.proposal = {'kind': 'call', 'contract_id': 'unknown', 'arguments': {}, 'target': 'DEV'}
        self.assertEqual(self.run_task()['state'], 'Blocked')
        self.profile['capabilities']['deny'] = ['fixture.read']
        self.save_catalog()
        self.assertEqual(self.run_task()['state'], 'Blocked')
        self.assertEqual(FakeClient.calls, [])

    def test_checker_cannot_override_invalid_arguments(self):
        self.backend.proposal = {'kind': 'call', 'contract_id': 'fixture-read',
                                 'arguments': {'unexpected': 'synthetic-sensitive'}, 'target': 'DEV'}
        run = self.run_task()
        self.assertEqual(run['state'], 'Blocked')
        self.assertEqual(FakeClient.calls, [])
        self.assertNotIn('synthetic-sensitive', json.dumps(run))

    def test_independent_checker_rejection_blocks_before_mcp(self):
        invoke = self.backend.invoke

        def reject(role, payload, schema, timeout):
            if role == 'checker':
                return {'accepted': False, 'goal_met': False,
                        'no_change_needed': False, 'reason': 'contract rejected'}
            return invoke(role, payload, schema, timeout)

        with mock.patch.object(self.backend, 'invoke', side_effect=reject):
            run = self.run_task()
        self.assertEqual(run['state'], 'Blocked')
        self.assertEqual(run['reason'], 'independent-checker-rejected')
        self.assertEqual(FakeClient.calls, [])

    def test_no_op_requires_prior_field_evidence_and_checker_confirmation(self):
        proposals = [
            {'kind': 'call', 'contract_id': 'fixture-read', 'arguments': {}, 'target': 'DEV'},
            {'kind': 'no_op', 'contract_id': '', 'arguments': {}, 'target': 'DEV'},
        ]
        result_checks = [
            {'accepted': True, 'goal_met': False, 'no_change_needed': False,
             'reason': 'read evidence gathered'},
            {'accepted': True, 'goal_met': True, 'no_change_needed': True,
             'reason': 'goal already holds'},
        ]

        def scripted(role, payload, schema, timeout):
            if role == 'maker':
                return proposals.pop(0)
            if role == 'checker':
                return {'accepted': True, 'goal_met': False,
                        'no_change_needed': False, 'reason': 'proposal allowed'}
            return result_checks.pop(0)

        with mock.patch.object(self.backend, 'invoke', side_effect=scripted):
            run = self.run_task()
        self.assertEqual(run['state'], 'No-Op', run)
        self.assertTrue(any(item.get('level') == 3 and item.get('status') == 'PASS'
                            for item in run['evidence']))
        self.assertEqual(len(FakeClient.calls), 1)

    def test_no_op_without_field_evidence_is_blocked(self):
        self.backend.proposal = {'kind': 'no_op', 'contract_id': '', 'arguments': {}, 'target': 'DEV'}
        self.assertEqual(self.run_task()['state'], 'Blocked')
        self.assertEqual(FakeClient.calls, [])

    def test_stagnation_stops_repeated_reads(self):
        self.backend.goal_met = False
        run = self.run_task()
        self.assertEqual(run['state'], 'Stalled', run)
        self.assertEqual(len(FakeClient.calls), 1)

    def test_budget_and_backend_timeout_are_terminal(self):
        self.backend.goal_met = False
        run = self.run_task(limits={'max_iterations': 1})
        self.assertEqual(run['state'], 'Exhausted')
        with mock.patch.object(self.backend, 'invoke', side_effect=TimeoutError):
            self.assertEqual(self.run_task()['state'], 'Blocked')

    def test_elapsed_total_budget_prevents_approval_reservation_and_tool_dispatch(self):
        self.capability['effect'] = 'mutating'
        self.profile['capabilities'] = {'allow': [], 'gated': ['fixture.read'], 'deny': []}
        self.contract.update(effect='mutating', approval_mode='broker-only')
        self.save_catalog()
        with mock.patch.object(approval_broker, 'STORE', self.state / 'actions'):
            engine = self.engine(limits={'max_seconds': 1})
            pending = engine.run('change DEV', self.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(pending['state'], 'PENDING_APPROVAL', pending)
            approval_broker.set_status(pending['approval']['action_id'], 'APPROVED')
            FakeClient.tools_hook = lambda: __import__('time').sleep(1.05)
            with mock.patch.object(approval_broker, 'begin', wraps=approval_broker.begin) as begin:
                run = engine.resume(pending['run_id'])
        self.assertEqual(run['state'], 'Exhausted', run)
        self.assertEqual(run['reason'], 'run-budget-exhausted')
        self.assertEqual(begin.call_count, 0)
        self.assertEqual(FakeClient.calls, [])

    def test_unknown_capability_is_a_structured_block_without_dispatch(self):
        classification = dict(self.classification, capability='fixture.missing')
        run = self.engine().run('read DEV', classification, ['fixture-skill'], 'DEV')
        self.assertEqual(run['state'], 'Blocked', run)
        self.assertEqual(run['reason'], 'unknown-capability')
        self.assertEqual(FakeClient.calls, [])

    def test_pending_run_expires_at_exact_boundary_and_resume_stays_local(self):
        self.capability['effect'] = 'mutating'
        self.profile['capabilities'] = {'allow': [], 'gated': ['fixture.read'], 'deny': []}
        self.contract.update(effect='mutating', approval_mode='broker-only')
        self.save_catalog()
        created = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        with mock.patch.object(approval_broker, 'STORE', self.state / 'actions'), \
             mock.patch.object(execution, 'now', return_value=created.isoformat()):
            engine = self.engine()
            pending = engine.run('change DEV', self.classification, ['fixture-skill'], 'DEV')
        self.assertEqual(pending['state'], 'PENDING_APPROVAL', pending)

        just_before = (created + timedelta(seconds=execution.RUN_STATE_TTL_SECONDS) - timedelta(microseconds=1)).isoformat()
        with mock.patch.object(execution, 'now', return_value=just_before):
            self.assertEqual(engine.status(pending['run_id'])['state'], 'PENDING_APPROVAL')

        boundary = (created + timedelta(seconds=execution.RUN_STATE_TTL_SECONDS)).isoformat()
        with mock.patch.object(execution, 'now', return_value=boundary), \
             mock.patch.object(approval_broker, 'begin', side_effect=AssertionError('expired run reached approval broker')):
            expired = engine.resume(pending['run_id'])
        self.assertEqual(expired['state'], 'Blocked')
        self.assertEqual(expired['reason'], 'run-state-expired')
        saved = json.loads(engine.path(pending['run_id']).read_text(encoding='utf-8'))
        self.assertEqual(saved['state'], 'Blocked')
        self.assertEqual(saved['reason'], 'run-state-expired')
        self.assertEqual(FakeClient.calls, [])

    def test_terminal_run_remains_queryable_after_expiry_window(self):
        created = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        with mock.patch.object(execution, 'now', return_value=created.isoformat()):
            run = self.run_task()
        future = (created + timedelta(seconds=execution.RUN_STATE_TTL_SECONDS + 1)).isoformat()
        with mock.patch.object(execution, 'now', return_value=future):
            status = self.engine().status(run['run_id'])
        self.assertEqual(status['state'], 'Success')

    def test_mutation_waits_approval_resumes_once_and_preserves_uncertain_outcome(self):
        self.capability['effect'] = 'mutating'
        self.profile['capabilities'] = {'allow': [], 'gated': ['fixture.read'], 'deny': []}
        self.contract.update(effect='mutating', approval_mode='broker-only')
        self.save_catalog()
        with mock.patch.object(approval_broker, 'STORE', self.state / 'actions'):
            engine = self.engine()
            run = engine.run('change DEV', self.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'PENDING_APPROVAL', run)
            self.assertEqual(FakeClient.calls, [])
            wrong_backend = execution.HarnessExecutor(
                'claude', 'other-model', root=self.root, state_dir=self.state,
                adapter=self.backend, client_factory=FakeClient)
            with self.assertRaisesRegex(ValueError, 'backend-or-model-mismatch'):
                wrong_backend.resume(run['run_id'])
            self.assertEqual(FakeClient.calls, [])
            self.assertEqual(approval_broker.set_status(run['approval']['action_id'], 'APPROVED')['status'], 'APPROVED')
            done = engine.resume(run['run_id'])
            self.assertEqual(done['state'], 'Success', done)
            engine.resume(run['run_id'])
            self.assertEqual(len(FakeClient.calls), 1)
            self.assertEqual(approval_broker.read_plan(run['approval']['action_id'])['status'], 'CONSUMED')

    def test_interrupted_inflight_mutation_requires_reconciliation_before_retry(self):
        self.capability['effect'] = 'mutating'
        self.profile['capabilities'] = {'allow': [], 'gated': ['fixture.read'], 'deny': []}
        self.contract.update(effect='mutating', approval_mode='broker-only')
        self.save_catalog()
        with mock.patch.object(approval_broker, 'STORE', self.state / 'actions'):
            engine = self.engine()
            run = engine.run('change DEV', self.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'PENDING_APPROVAL', run)
            approval_broker.set_status(run['approval']['action_id'], 'APPROVED')
            with mock.patch.object(FakeClient, 'call', side_effect=KeyboardInterrupt):
                interrupted = engine.resume(run['run_id'])
            self.assertEqual(interrupted['state'], 'Blocked', interrupted)
            self.assertEqual(interrupted['reason'], 'reconciliation-required')
            calls_after_interrupt = len(FakeClient.calls)
            retried = engine.resume(run['run_id'])
            self.assertEqual(retried['state'], 'Blocked', retried)
            self.assertEqual(retried['reason'], 'reconciliation-required')
            self.assertEqual(len(FakeClient.calls), calls_after_interrupt)

    def test_approval_target_drift_blocks_before_mcp_call(self):
        self.capability['effect'] = 'mutating'
        self.profile['capabilities'] = {'allow': [], 'gated': ['fixture.read'], 'deny': []}
        self.contract.update(effect='mutating', approval_mode='broker-only')
        self.save_catalog()
        with mock.patch.object(approval_broker, 'STORE', self.state / 'actions'):
            engine = self.engine()
            run = engine.run('change DEV', self.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'PENDING_APPROVAL', run)
            approval_broker.set_status(run['approval']['action_id'], 'APPROVED')
            path = engine.path(run['run_id'])
            record = json.loads(path.read_text(encoding='utf-8'))
            record['target'] = 'QAS'
            record.pop('record_hash')
            record['record_hash'] = execution.fingerprint(record)
            path.write_text(json.dumps(record), encoding='utf-8')
            resumed = engine.resume(run['run_id'])
        self.assertEqual(resumed['state'], 'Blocked', resumed)
        self.assertEqual(resumed['reason'], 'target-drift')
        self.assertEqual(FakeClient.calls, [])

    def test_expired_approval_blocks_before_mcp_call(self):
        self.capability['effect'] = 'mutating'
        self.profile['capabilities'] = {'allow': [], 'gated': ['fixture.read'], 'deny': []}
        self.contract.update(effect='mutating', approval_mode='broker-only')
        self.save_catalog()
        with mock.patch.object(approval_broker, 'STORE', self.state / 'actions'):
            engine = self.engine()
            run = engine.run('change DEV', self.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'PENDING_APPROVAL', run)
            approval_broker.set_status(run['approval']['action_id'], 'APPROVED')
            with mock.patch.object(approval_broker, 'begin',
                                   return_value={'status': 'ERROR', 'error': 'approval-expired'}):
                resumed = engine.resume(run['run_id'])
        self.assertEqual(resumed['state'], 'Blocked', resumed)
        self.assertEqual(resumed['reason'], 'approval-expired')
        self.assertEqual(FakeClient.calls, [])

    def test_opaque_ids_and_corrupt_state_fail_closed(self):
        with self.assertRaises(ValueError):
            self.engine().status('../escape')
        run = self.run_task()
        path = self.state / 'harness-runs' / (run['run_id'] + '.json')
        saved = json.loads(path.read_text())
        saved['target'] = 'changed'
        path.write_text(json.dumps(saved))
        with self.assertRaises(ValueError):
            self.engine().resume(run['run_id'])

    def test_version_incompatible_run_state_fails_closed(self):
        run = self.run_task()
        path = self.state / 'harness-runs' / (run['run_id'] + '.json')
        record = json.loads(path.read_text(encoding='utf-8'))
        record.pop('record_hash')
        record['version'] = execution.VERSION + 1
        record['record_hash'] = execution.fingerprint(record)
        path.write_text(json.dumps(record), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'state-integrity-or-version-mismatch'):
            self.engine().status(run['run_id'])


class CliIsolationTest(unittest.TestCase):
    def test_sap_credentials_are_excluded_from_model_environment(self):
        with mock.patch.dict(os.environ, {'SAP_PASSWORD': 'synthetic-sap', 'ARC_SAP_PASSWORD': 'synthetic-arc',
                                         'CPI_CLIENT_SECRET': 'synthetic-cpi', 'APIM_CLIENT_SECRET': 'synthetic-api'}):
            env = execution.model_environment('codex')
        self.assertFalse(any(value in env.values() for value in ['synthetic-sap', 'synthetic-arc', 'synthetic-cpi', 'synthetic-api']))

    def test_missing_cli_blocks_without_mcp_call(self):
        fixture = HarnessExecutionTest()
        fixture.setUp()
        try:
            with mock.patch.object(execution.shutil, 'which', return_value=None):
                engine = execution.HarnessExecutor(
                    'codex', 'fixture-model', root=fixture.root,
                    state_dir=fixture.state, adapter=execution.CliBackend('codex', 'fixture-model'),
                    client_factory=FakeClient)
                run = engine.run('read DEV', fixture.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'Blocked')
            self.assertEqual(run['reason'], 'backend-not-installed')
            self.assertEqual(FakeClient.calls, [])
        finally:
            fixture.tearDown()

    def test_malformed_cli_response_blocks_without_mcp_call(self):
        fixture = HarnessExecutionTest()
        fixture.setUp()
        try:
            def malformed(command, input_text='', **kwargs):
                if '--help' in command:
                    return '--ignore-user-config --ignore-rules --output-schema --disable'
                return 'not-json'

            with mock.patch.object(execution.shutil, 'which', return_value='fixture-cli'), \
                 mock.patch.object(execution, 'bounded_process', side_effect=malformed):
                engine = execution.HarnessExecutor(
                    'codex', 'fixture-model', root=fixture.root,
                    state_dir=fixture.state, adapter=execution.CliBackend('codex', 'fixture-model'),
                    client_factory=FakeClient)
                run = engine.run('read DEV', fixture.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'Blocked')
            self.assertEqual(FakeClient.calls, [])
        finally:
            fixture.tearDown()

    def test_cli_native_tool_event_is_rejected_before_mcp_call(self):
        fixture = HarnessExecutionTest()
        fixture.setUp()
        try:
            def native_event(command, input_text='', **kwargs):
                if '--help' in command:
                    return '--ignore-user-config --ignore-rules --output-schema --disable'
                return json.dumps({'type': 'item.completed',
                                   'item': {'type': 'function_call', 'name': 'unsafe_shell'}})

            with mock.patch.object(execution.shutil, 'which', return_value='fixture-cli'), \
                 mock.patch.object(execution, 'bounded_process', side_effect=native_event):
                engine = execution.HarnessExecutor(
                    'codex', 'fixture-model', root=fixture.root,
                    state_dir=fixture.state, adapter=execution.CliBackend('codex', 'fixture-model'),
                    client_factory=FakeClient)
                run = engine.run('read DEV', fixture.classification, ['fixture-skill'], 'DEV')
            self.assertEqual(run['state'], 'Blocked')
            self.assertEqual(run['reason'], 'native-tool-event-rejected')
            self.assertEqual(FakeClient.calls, [])
        finally:
            fixture.tearDown()

    def test_mcp_child_receives_only_its_auth_refs_and_runtime_values(self):
        with mock.patch.dict(os.environ, {'CPI_OAUTH_CLIENT_SECRET': 'fixture-cpi-auth',
                                         'APIM_PASSWORD': 'fixture-apim-auth',
                                         'OPENAI_API_KEY': 'fixture-provider-key'}):
            env = mcp_launcher._server_environment(
                {'id': 'sap-cpi-mcp', 'auth': {'env_refs': ['CPI_OAUTH_CLIENT_SECRET']}},
                {'env': {'CPI_TOOL_WORKSPACE': 'workspace'}})
        self.assertEqual(env['CPI_OAUTH_CLIENT_SECRET'], 'fixture-cpi-auth')
        self.assertEqual(env['CPI_TOOL_WORKSPACE'], 'workspace')
        self.assertNotIn('APIM_PASSWORD', env)
        self.assertNotIn('OPENAI_API_KEY', env)

    def test_both_backend_commands_disable_native_tools_and_pin_model(self):
        with tempfile.TemporaryDirectory() as directory:
            for backend in ['codex', 'claude']:
                adapter = execution.CliBackend(backend, 'fixture-model')
                command = adapter.command('backend', Path(directory), Path(directory) / 'schema.json', {})
                self.assertIn('fixture-model', command)
                if backend == 'codex':
                    self.assertIn('--ignore-user-config', command)
                    self.assertIn('shell_tool', command)
                    self.assertIn('read-only', command)
                else:
                    self.assertIn('--tools', command)
                    self.assertIn('--safe-mode', command)
                    self.assertIn('--strict-mcp-config', command)

    def test_mocked_codex_and_claude_complete_read_through_fake_mcp(self):
        for backend in ['codex', 'claude']:
            with self.subTest(backend=backend):
                fixture = HarnessExecutionTest()
                fixture.setUp()
                commands = []

                def fake_process(command, input_text='', **kwargs):
                    commands.append(command)
                    if '--help' in command:
                        return '--ignore-user-config --ignore-rules --output-schema --disable --tools --safe-mode --strict-mcp-config --json-schema'
                    role = json.loads(input_text)['role']
                    if role == 'maker':
                        value = {'kind': 'call', 'contract_id': 'fixture-read',
                                 'arguments': {}, 'target': 'DEV'}
                    else:
                        value = {'accepted': True, 'goal_met': role == 'result_checker',
                                 'no_change_needed': False, 'reason': 'fixture field checked'}
                    if backend == 'codex':
                        return json.dumps({'type': 'item.completed', 'item': {
                            'type': 'agent_message', 'text': json.dumps(value)}})
                    return json.dumps({'structured_output': value})

                try:
                    adapter = execution.CliBackend(backend, 'fixture-model')
                    with mock.patch.object(execution.shutil, 'which', return_value='fixture-cli'), \
                         mock.patch.object(execution, 'bounded_process', side_effect=fake_process):
                        engine = execution.HarnessExecutor(
                            backend, 'fixture-model', root=fixture.root,
                            state_dir=fixture.state, adapter=adapter,
                            client_factory=FakeClient)
                        run = engine.run('read DEV', fixture.classification,
                                         ['fixture-skill'], 'DEV')
                    self.assertEqual(run['state'], 'Success', run)
                    self.assertEqual(len(FakeClient.calls), 1)
                    self.assertEqual(len(commands), 4)
                    self.assertTrue(all('fixture-model' in command for command in commands[1:]))
                finally:
                    fixture.tearDown()


if __name__ == '__main__':
    unittest.main()
