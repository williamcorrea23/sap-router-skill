"""Fail closed on target, artifact identity and downgrade before cf deploy."""
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile


def version(value):
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError("Only stable numeric MTA versions are supported")
    return tuple(map(int, value.split('.')))


def fields(text):
    result = {}
    for key in ('ID', 'version', 'extends'):
        match = re.search(r'^' + key + r':\s*[\'\"]?([^\s\'\"#]+)', text, re.M)
        if match:
            result[key] = match.group(1)
    return result


def check(mtar, extension, inventory):
    with zipfile.ZipFile(mtar) as archive:
        metadata = fields(archive.read('META-INF/mtad.yaml').decode('utf-8'))
    if not metadata.get('ID') or not metadata.get('version'):
        raise ValueError('Artifact lacks MTA ID/version')
    ext = fields(Path(extension).read_text(encoding='utf-8-sig'))
    if ext.get('extends') != metadata['ID']:
        raise ValueError('Extension extends a different MTA')
    candidate = version(metadata['version'])
    if ext.get('version') and version(ext['version']) != candidate:
        raise ValueError('Extension version differs from artifact')
    empty_inventory = re.search(r'(?i)no multi-target apps', inventory)
    header = re.search(r'(?im)^\s*(?:mta\s+)?id\s+version\b', inventory)
    if not empty_inventory and not header:
        raise ValueError('Unrecognized CF MTA inventory; cannot prove deployed version')
    # Consume only rows whose first column is the exact MTA ID. A recognized
    # empty inventory or recognized table without this ID means first deploy.
    rows = [line.split() for line in inventory.splitlines()
            if line.strip() and not line.lstrip().lower().startswith(('name ', 'id ', 'no multi-target'))]
    matches = [row for row in rows if row[0] == metadata['ID']]
    if len(matches) > 1:
        raise ValueError('Ambiguous MTA inventory')
    deployed = matches[0][1] if matches else None
    if deployed and candidate < version(deployed):
        raise ValueError('DOWNGRADE_BLOCKED: bump version; never use --version-rule ALL')
    return {**metadata, 'deployedVersion': deployed, 'result': 'passed'}


def main():
    cf_config = json.loads((Path(os.environ.get('CF_HOME', str(Path.home()))) / '.cf' / 'config.json').read_text())
    expected = (os.environ['EXPECTED_CF_API'].rstrip('/'), os.environ['EXPECTED_CF_ORG'], os.environ['EXPECTED_CF_SPACE'])
    actual = (cf_config['Target'].rstrip('/'), cf_config['OrganizationFields']['Name'], cf_config['SpaceFields']['Name'])
    if expected != actual or expected[2] != 'dev' or os.environ['ENVIRONMENT'] != 'dev':
        raise ValueError('Cloud Foundry target is not the configured DEV target')
    inventory = subprocess.run(['cf', 'mtas'], check=True, capture_output=True, text=True, timeout=60).stdout
    print(json.dumps(check(os.environ['MTAR_PATH'], os.environ['MTAEXT_PATH'], inventory)))


if __name__ == '__main__':
    main()
