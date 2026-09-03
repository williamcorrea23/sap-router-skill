#!/usr/bin/env python3
"""Check DEV test prerequisites. This command never approves or executes SAP writes."""
import argparse
import json
from pathlib import Path


def validate(data):
    errors = []
    if data.get('environment') != 'DEV':
        errors.append('Only DEV is allowed')
    if data.get('approval_required_per_operation') is not True:
        errors.append('Per-operation approval is mandatory')
    for field in ('system', 'client'):
        if not data.get(field):
            errors.append('Missing ' + field)
    required = {'abap': ('object', 'package', 'cleanup'), 'cpi': ('tenant', 'iflow_id', 'cleanup'),
                'apim': ('tenant', 'proxy_id', 'cleanup'),
                'mm': ('material', 'material_type', 'industry_sector', 'base_unit', 'views', 'organizational_levels', 'cleanup')}
    for scenario, fields in required.items():
        values = data.get('scenarios', {}).get(scenario, {})
        for field in fields:
            if not values.get(field):
                errors.append(f'{scenario}: missing {field}')
    return {'status': 'BLOCKED' if errors else 'READY_FOR_REVIEW', 'errors': errors,
            'write_authorized': False, 'next_step': 'Obtain separate target-bound approval before each operation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.manifest.read_text(encoding='utf-8')))
    print(json.dumps(result, indent=2))
    return 2 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
