#!/usr/bin/env python3
"""Validate canonical skill metadata and resolvable local Markdown resources."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote
from skill_packager import validate_skill

ROOT = Path(__file__).resolve().parent.parent


def inspect_skills(root=ROOT):
    results = []
    for skill in sorted((root / '.agents/skills').glob('*/SKILL.md')):
        valid, errors = validate_skill(skill.parent)
        body = re.sub(r'```.*?```', '', skill.read_text(encoding='utf-8'), flags=re.S)
        unresolved = []
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            link = unquote(link.split('#')[0].split(' "')[0].strip('<> '))
            if not link or re.match(r'^[a-zA-Z]+:', link) or any(c in link for c in '{}*'):
                continue
            if not (skill.parent / link).exists() and not (root / link).exists():
                unresolved.append(link)
        results.append({'skill': skill.parent.name, 'metadata_valid': valid, 'errors': errors,
                        'unresolved_links': sorted(set(unresolved))})
    return {'status': 'PASS' if all(x['metadata_valid'] and not x['unresolved_links'] for x in results) else 'FAIL',
            'count': len(results), 'metadata_passed': sum(x['metadata_valid'] for x in results),
            'skills_with_unresolved_links': sum(bool(x['unresolved_links']) for x in results),
            'validation_scope': 'metadata and local Markdown links; not live behavioral proof', 'skills': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output')
    args = parser.parse_args()
    result = inspect_skills()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'skills'}, indent=2))
    for skill in result['skills']:
        if skill['errors'] or skill['unresolved_links']:
            print(json.dumps(skill))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
