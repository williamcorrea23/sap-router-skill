"""Bounded read-only MCP probes. No package installation or bootstrap repair."""
from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path


def stop_process(proc):
    """Terminate only the process tree owned by this probe."""
    close_job = getattr(proc, '_close_probe_job', None)
    if close_job:
        close_job()
        proc._close_probe_job = None
    if proc.poll() is None and not close_job:
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            except (OSError, subprocess.TimeoutExpired):
                proc.kill()
        else:
            import signal
            os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)


def semantic_call(server_id):
    fixture = (Path(__file__).resolve().parents[2] / 'tests/fixtures/probe-project').as_posix()
    # Allowlisted read operations; arbitrary runtime-supplied tool names are not executed.
    return {
        'arc-1': ('SAPRead', {'type': 'SYSTEM'}),
        'ui5-mcp': ('get_project_info', {'projectDir': fixture}),
        'cap-mcp': ('search_model', {'projectPath': fixture, 'name': 'router.probe.Sample', 'namesOnly': True, 'topN': 1}),
        'fiori-mcp': ('list_fiori_apps', {'searchPath': [fixture]}),
        'context-mode': ('ctx_stats', {}),
        'aibap': ('search_objects', {'query': 'ZCL_ZROUTER*', 'max_results': 1}),
        'sap-cpi-mcp': ('cpi_test_connection', {}),
        'integration-suite-ui-mcp': ('cpi_webui_probe', {}),
        'sap-apim-mcp': ('apim_health', {}),
        'apim-ui-mcp': ('apim_api_call', {'path': '/apiportal/api/1.0/Management.svc/APIProxies?$top=1', 'method': 'GET'}),
    }.get(server_id)


def domain_ok(result, server_id):
    if not isinstance(result, dict) or result.get('isError'):
        return False
    value = result.get('structuredContent')
    texts = '\n'.join(b.get('text', '') for b in result.get('content', []) if b.get('type') == 'text')
    if server_id == 'context-mode':
        return texts.startswith('context-mode') and 'Error' not in texts and 'calls' in texts
    if value is None:
        for block in result.get('content', []):
            if block.get('type') == 'text':
                try:
                    value = json.loads(block['text'])
                    break
                except (ValueError, KeyError):
                    continue
    if server_id == 'cap-mcp':
        return isinstance(value, list) and value == ['router.probe.Sample']
    if server_id == 'fiori-mcp':
        return isinstance(value, dict) and isinstance(value.get('applications'), list) and not value.get('error')
    if not isinstance(value, dict):
        return False
    if server_id == 'ui5-mcp':
        return value.get('projectName') == 'sap-router-probe' and value.get('projectType') == 'application'
    if server_id == 'aibap':
        return isinstance(value.get('count'), int) and value.get('count', -1) >= 0 and 'results' in value
    if server_id == 'arc-1':
        return bool(value.get('user')) and isinstance(value.get('collections'), list) and bool(value['collections'])
    if server_id in ('apim-ui-mcp', 'sap-apim-mcp'):
        if value.get('status') != 'OK':
            return False
        try:
            body = json.loads(value.get('body', ''))
            return isinstance(body.get('d', {}).get('results', body.get('value')), list)
        except (ValueError, TypeError, AttributeError):
            return False
    if value.get('status') in ('ERROR', 'BLOCKED', 'UNAVAILABLE', 'FAIL') or value.get('error'):
        return False
    return value.get('status') in ('OK', 'READY') or (
        value.get('ok') is True and isinstance(value.get('status'), int) and 200 <= value['status'] < 300)


def stdio_probe(command, args, timeout, env, cwd, server_id=None):
    result = {'initialize': 'NOT_PROVED', 'tools_list': 'NOT_PROVED',
              'domain_probe': 'NOT_PROVED', 'error': None}
    proc = subprocess.Popen([shutil.which(command) or command, *args], cwd=cwd, env=env,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding='utf-8', errors='replace',
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                            start_new_session=os.name != 'nt')
    from .process_job import attach
    proc._close_probe_job = attach(proc)
    messages = queue.Queue(maxsize=128)
    def read():
        for line in proc.stdout:
            if len(line) > 2_000_000:
                continue
            try:
                value = json.loads(line)
                if isinstance(value, dict) and value.get('id') in (1, 2, 3):
                    messages.put_nowait(value)
            except (ValueError, queue.Full):
                pass
    def drain():
        # Drain without retaining credentials or backend payloads.
        for _ in proc.stderr:
            pass
    readers = [threading.Thread(target=read, daemon=True), threading.Thread(target=drain, daemon=True)]
    for thread in readers:
        thread.start()
    deadline = time.monotonic() + timeout
    def send(method, params, id=None):
        message = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if id is not None:
            message['id'] = id
        proc.stdin.write(json.dumps(message) + '\n')
        proc.stdin.flush()
    def receive(id):
        while time.monotonic() < deadline:
            try:
                message = messages.get(timeout=min(.2, max(.01, deadline-time.monotonic())))
            except queue.Empty:
                if proc.poll() is not None:
                    break
                continue
            if message.get('id') == id:
                return message
        raise TimeoutError('MCP response deadline exceeded')
    try:
        send('initialize', {'protocolVersion': '2024-11-05', 'capabilities': {},
                            'clientInfo': {'name': 'sap-router-probe', 'version': '1.0.0'}}, 1)
        if not isinstance(receive(1).get('result'), dict):
            raise ValueError('MCP initialization failed')
        result['initialize'] = 'PASS'
        send('notifications/initialized', {})
        send('tools/list', {}, 2)
        listing = receive(2).get('result', {}).get('tools')
        if not isinstance(listing, list):
            raise ValueError('MCP tool listing failed')
        result['tools_list'] = 'PASS'
        result['tool_names'] = [t.get('name') for t in listing]
        result['tool_schemas'] = {t.get('name'): t.get('inputSchema') for t in listing}
        selected = semantic_call(server_id)
        if selected and selected[0] in {t.get('name') for t in listing}:
            send('tools/call', {'name': selected[0], 'arguments': selected[1]}, 3)
            result['domain_probe'] = 'PASS' if domain_ok(receive(3).get('result'), server_id) else 'FAIL'
            if result['domain_probe'] == 'FAIL':
                result['error'] = 'Semantic read failed; check authentication, TLS and target configuration.'
        else:
            result['error'] = 'No reviewed semantic read available; handshake is not domain readiness.'
    except (TimeoutError, ValueError, OSError) as exc:
        result['error'] = type(exc).__name__ + ': MCP probe failed; no backend payload retained.'
    finally:
        stop_process(proc)
        for thread in readers:
            thread.join(timeout=1)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            stream.close()
    return result
