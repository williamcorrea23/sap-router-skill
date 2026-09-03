"""Resolve exact-version, already-installed Node packages without invoking npm."""
import json
import os
import shutil
from pathlib import Path

PINS = {'arc-1': ('arc-1', '1.1.2'), 'ui5-mcp': ('@ui5/mcp-server', '0.2.14'),
        'fiori-mcp': ('@sap-ux/fiori-mcp-server', '1.8.1'), 'cap-mcp': ('@cap-js/mcp-server', '0.0.5')}


def runtime_environment(server_id, runtime):
    env = os.environ.copy()
    env.update({k: str(v) for k, v in runtime.get('env', {}).items()})
    if server_id == 'arc-1':
        for name in ('URL', 'USER', 'PASSWORD', 'CLIENT'):
            if os.environ.get('ARC_SAP_' + name):
                env['SAP_' + name] = os.environ['ARC_SAP_' + name]
    return env


def resolve_runtime(root, server_id, runtime):
    runtime = dict(runtime)
    if server_id == 'context-mode':
        runtime.update(command=shutil.which('node') or 'node', args=[str(root / 'scripts/context_mode_safe.mjs')])
        return runtime
    if server_id not in PINS:
        return runtime
    package, version = PINS[server_id]
    roots = [root / '.sap-router/runtimes/node_modules', root / 'node_modules']
    for env in ('APPDATA', 'LOCALAPPDATA'):
        if os.environ.get(env):
            cache = Path(os.environ[env]) / 'npm-cache/_npx'
            if cache.is_dir():
                roots.extend(p / 'node_modules' for p in sorted(cache.iterdir()) if p.is_dir())
    for packages in roots:
        directory = packages / package
        manifest = directory / 'package.json'
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text(encoding='utf-8'))
        if data.get('name') != package or data.get('version') != version:
            continue
        bins = data.get('bin', {})
        entry = bins if isinstance(bins, str) else next(iter(bins.values()), '')
        executable = (directory / entry).resolve()
        if not entry or not executable.is_file() or directory.resolve() not in executable.parents:
            continue
        runtime.update(command=shutil.which('node') or 'node', args=[str(executable)], package=package, version=version)
        if server_id == 'cap-mcp':
            runtime['env'] = {**runtime.get('env', {}), 'CDS_MCP_OFFLINE': 'true'}
        return runtime
    return runtime
