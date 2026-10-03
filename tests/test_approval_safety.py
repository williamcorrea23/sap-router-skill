import argparse
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from datetime import datetime, timedelta, UTC

os.environ['SAP_ROUTER_OFFLINE'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import approval_broker as broker
import cpi_client


class ApprovalSafetyTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        patch = mock.patch.object(broker, 'STORE', Path(self.temp.name))
        patch.start()
        self.addCleanup(patch.stop)
        self.plan = broker.write_plan({'target': 'DEV-test', 'effect': 'mutating',
                                      'arguments_json': '{"a":1}', 'preconditions_json': '{"ready":true}'})
        self.id = self.plan['action_id']
        self.hashes = [self.id, self.plan['plan_hash'], self.plan['argument_hash'], self.plan['precondition_hash']]

    def broker_reply(self, command):
        if command[0] == 'show':
            return {'argument_hash': self.plan['argument_hash']}
        return {'status': 'APPROVED'}

    def test_pending_and_expired_are_blocked(self):
        self.assertEqual(broker.begin(*self.hashes)['error'], 'approval-not-approved')
        broker.set_status(self.id, 'APPROVED')
        with mock.patch.object(broker, 'datetime') as clock:
            clock.now.return_value = datetime.now(UTC) + timedelta(hours=1)
            clock.fromisoformat.side_effect = datetime.fromisoformat
            self.assertEqual(broker.begin(*self.hashes)['error'], 'approval-expired')

    def test_reservation_blocks_concurrent_and_uncertain_replay(self):
        broker.set_status(self.id, 'APPROVED')
        self.assertEqual(broker.begin(*self.hashes)['status'], 'APPROVED')
        self.assertEqual(broker.begin(*self.hashes)['error'], 'reconciliation-required')
        self.assertEqual(broker.consume(*self.hashes)['status'], 'CONSUMED')
        self.assertEqual(broker.begin(*self.hashes)['error'], 'approval-already-consumed')

    def test_hashes_bind_actual_arguments_and_preconditions(self):
        args = argparse.Namespace(action_id=self.id, plan_hash=self.plan['plan_hash'],
                                  argument_hash=self.plan['argument_hash'], precondition_hash=self.plan['precondition_hash'])
        with mock.patch.object(cpi_client, 'run_approval_broker', side_effect=self.broker_reply) as call:
            result = cpi_client.with_approval(args, {'a': 2}, {'ready': True}, lambda: {'status': 'OK'})
        self.assertEqual(result['reason'], 'argument-hash-mismatch')
        call.assert_called_once_with(['show', self.id])

        # Environment preconditions are re-derived on commit. A still-approved
        # plan may proceed when the target remains safe; the original approval
        # hash remains the broker's comparison value.
        with mock.patch.object(cpi_client, 'run_approval_broker', side_effect=self.broker_reply) as call:
            result = cpi_client.with_approval(args, {'a': 1}, {'ready': False}, lambda: {'status': 'OK'})
        self.assertEqual(result['approval'], 'spent')
        self.assertEqual([item.args[0][0] for item in call.call_args_list], ['show', 'verify', 'begin', 'consume'])
        self.assertIn(self.plan['precondition_hash'], call.call_args_list[1].args[0])

    def test_timeout_never_advises_retry_or_consumes(self):
        args = argparse.Namespace(action_id=self.id, plan_hash=self.plan['plan_hash'],
                                  argument_hash=None, precondition_hash=None)
        def timeout():
            raise TimeoutError('unknown result')
        with mock.patch.object(cpi_client, 'run_approval_broker', side_effect=self.broker_reply) as call:
            result = cpi_client.with_approval(args, {'a': 1}, {'ready': True}, timeout)
        self.assertEqual(result['approval'], 'reconciliation-required')
        self.assertEqual([c.args[0][0] for c in call.call_args_list], ['show', 'verify', 'begin'])
