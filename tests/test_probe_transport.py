import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from sap_router_core.probe_transport import stdio_probe

FAKE = '''
import sys,json
initialized=False
for line in sys.stdin:
 m=json.loads(line); method=m['method']
 if method=='notifications/initialized':
  initialized=True
  continue
 if method=='initialize': result={'protocolVersion':'2024-11-05','capabilities':{},'serverInfo':{'name':'test','version':'1'}}
 elif method=='tools/list':
  assert initialized
  result={'tools':[{'name':'cpi_test_connection','inputSchema':{'type':'object'}}]}
 else: result={'structuredContent':{'status':'OK'}}
 print(json.dumps({'jsonrpc':'2.0','id':m['id'],'result':result}),flush=True)
'''


class TransportTest(unittest.TestCase):
    def test_handshake_then_semantic_tool_in_order(self):
        result = stdio_probe(sys.executable, ['-S', '-u', '-c', FAKE], 15, os.environ.copy(), Path.cwd(), 'sap-cpi-mcp')
        self.assertEqual(result['initialize'], 'PASS')
        self.assertEqual(result['tools_list'], 'PASS')
        self.assertEqual(result['domain_probe'], 'PASS')

    def test_deadline_terminates_owned_process(self):
        result = stdio_probe(sys.executable, ['-S', '-c', 'import time; time.sleep(60)'], 1, os.environ.copy(), Path.cwd())
        self.assertEqual(result['initialize'], 'NOT_PROVED')
        self.assertIn('TimeoutError', result['error'])
