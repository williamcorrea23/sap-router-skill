#!/usr/bin/env python3
"""Reconcile only router-owned project MCP sections; preserve personal settings."""
import argparse
import json
import re
import shutil
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALIASES = {'aibap': ['aibap-39912']}
RETIRED = {'ci-mcp-server', 'sap-api-management'}


def render(existing, servers, global_config):
    managed = {s['id'] for s in servers} | RETIRED
    # Preserve all sections except the router-owned MCP entries, including their nested env tables.
    pieces = re.split(r'(?=^\[)', existing, flags=re.MULTILINE)
    kept = []
    for piece in pieces:
        match = re.match(r'\[mcp_servers\.([^\].]+|"[^"]+")', piece)
        if match and match.group(1).strip('"') in managed:
            continue
        kept.append(piece)
    output = ''.join(kept).rstrip() + '\n\n'
    aliases = {}
    for server in servers:
        if server['status'] != 'enabled':
            continue
        sid = server['id']
        alias = next((x for x in ALIASES.get(sid, [])
                      if global_config.get('mcp_servers', {}).get(x, {}).get('enabled', True)
                      and x in global_config.get('mcp_servers', {})), None)
        if alias:
            aliases[sid] = alias
            continue
        output += f'[mcp_servers.{json.dumps(sid)}]\n'
        output += f'command = {json.dumps(sys.executable)}\n'
        output += 'args = ' + json.dumps([str(ROOT / 'scripts/mcp_launcher.py'), 'run', '--server', sid]) + '\n'
        output += 'cwd = ' + json.dumps(str(ROOT)) + '\n'
        output += 'startup_timeout_sec = 30\n'
    tomllib.loads(output)
    return output, aliases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    target = ROOT / '.codex/config.toml'
    current = target.read_text(encoding='utf-8') if target.exists() else ''
    global_path = Path.home() / '.codex/config.toml'
    global_config = tomllib.loads(global_path.read_text(encoding='utf-8')) if global_path.exists() else {}
    servers = json.loads((ROOT / '.agents/registries/mcps.json').read_text())['servers']
    desired, aliases = render(current, servers, global_config)
    backup = None
    if args.apply and desired != current:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        if target.exists():
            backup = ROOT / '.sap-router/backups' / stamp / 'codex-config.toml'
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(desired, encoding='utf-8')
    print(json.dumps({'status': 'PASS' if args.apply or current == desired else 'DRIFT',
                      'aliases': aliases, 'backup': str(backup) if backup else None,
                      'restart_required': args.apply and current != desired}, indent=2))
    return 0 if args.apply or current == desired else 1


if __name__ == '__main__':
    raise SystemExit(main())
