#!/usr/bin/env python3
"""Offline evidence review; never installs or promotes an MCP candidate."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def review():
    registries = ROOT / '.agents/registries'
    candidates = json.loads((registries / 'mcp-candidates.json').read_text())['candidates']
    servers = json.loads((registries / 'mcps.json').read_text())['servers']
    candidates += [s for s in servers if s['status'] == 'planned' and s['id'] not in {c['id'] for c in candidates}]
    snapshots = json.loads((registries / 'bundled-sources.lock.json').read_text())['sources']
    rows = []
    for candidate in candidates:
        sid = candidate['id']
        description = candidate.get('description', '') + ' ' + json.dumps(candidate.get('source', {}))
        matches = [s for s in snapshots if s['id'] == sid or
                   (s.get('origin') and s['origin'].removesuffix('.git').removeprefix('https://github.com/') in description)]
        evidence = []
        for snapshot in matches:
            root = ROOT / snapshot['path']
            if not root.is_dir():
                continue
            manifests = []
            for name in ('package.json', 'pyproject.toml', 'requirements.txt', 'go.mod'):
                path = root / name
                if path.exists():
                    manifests.append({'file': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            licenses = [str((root / n).relative_to(ROOT)) for n in snapshot.get('license_files', []) if (root / n).is_file()]
            evidence.append({'snapshot': snapshot['path'], 'origin': snapshot.get('origin'),
                             'revision': snapshot.get('revision'), 'license_files': licenses, 'dependency_manifests': manifests})
        priority = 'gap' if sid == 'smartform-ai-generator' else 'fallback' if re.search(r'adt|abap|gui|cpi|apim', sid) else 'overlap-or-optional'
        rows.append({'id': sid, 'classification': 'pending_evidence', 'priority': priority,
                     'evidence': evidence, 'promotion_allowed': False,
                     'missing': (['unambiguous local snapshot'] if len(evidence) != 1 else []) +
                         ['dependency/security review', 'read-only protocol and semantic tests',
                          'mutation approval/replay tests', 'maintenance verification', 'explicit promotion approval'],
                     'reason': 'Static evidence is not sufficient to approve a live pilot.'})
    return {'status': 'REVIEWED_WITH_GAPS', 'count': len(rows), 'network_used': False,
            'promoted': [], 'approved_for_pilot': 0, 'candidates': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = review()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'count': result['count'], 'with_snapshot': sum(bool(c['evidence']) for c in result['candidates']),
                      'pending_evidence': result['count'], 'promoted': 0}))


if __name__ == '__main__':
    main()
