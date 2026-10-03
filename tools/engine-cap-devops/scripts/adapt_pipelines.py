"""Prepare reviewable DEV_ONLY/managed CI changes; never commit or deploy."""
from pathlib import Path
import argparse
import shutil
import re
import subprocess


def adapt(root, shared, environment, expected_api, expected_org, scaffold=False):
    suffix = '.handlebars' if scaffold else ''
    cd_path = root / ('azure-pipelines-cd.yml' + suffix)
    ci_path = root / ('azure-pipelines-ci.yml' + suffix)
    cd, ci = cd_path.read_text(encoding='utf-8-sig'), ci_path.read_text(encoding='utf-8-sig')
    if 'name: engineCapMode' in cd or 'name: engineCapManaged' in ci:
        raise ValueError('Already adapted; inspect instead of applying twice')
    declaration = "  - name: engineCapMode\n    type: string\n    default: EXISTING_FLOW\n    values: [EXISTING_FLOW, DEV_ONLY]\n"
    cd = cd.replace('parameters:\n', 'parameters:\n' + declaration, 1) if '\nparameters:\n' in cd else declaration.join([]) + 'parameters:\n' + declaration + '\n' + cd
    # Preserve the complete existing stage graph under the alternate mode.
    head, stages = cd.split('\nstages:\n', 1)
    legacy = '\n'.join('  '+line if line else '' for line in stages.splitlines())
    env = '{{appName}}-dev' if scaffold else environment
    artifact = '$(artifactName)'
    dev = f'''  - ${{{{ if eq(parameters.engineCapMode, 'DEV_ONLY') }}}}:
    - template: pipeline/engine-cap-dev-only.yml
      parameters:
        environment: {env}
        artifactName: {artifact}
        expectedApi: {expected_api}
        expectedOrg: {expected_org}
        expectedSpace: dev
'''
    cd = head + '\nstages:\n' + dev + "  - ${{ if ne(parameters.engineCapMode, 'DEV_ONLY') }}:\n" + legacy + '\n'
    # N8N variable group is unnecessary for the managed path.
    cd = cd.replace('  - group: N8N', "  - ${{ if ne(parameters.engineCapMode, 'DEV_ONLY') }}:\n    - group: N8N")
    ci = "parameters:\n  - name: engineCapManaged\n    type: boolean\n    default: false\n\n" + ci
    ci = ci.replace('  - group: N8N', "  - ${{ if not(parameters.engineCapManaged) }}:\n    - group: N8N")
    lines = ci.splitlines(); out=[]; i=0
    while i<len(lines):
        line=lines[i]
        if line.lstrip().startswith('- template:') and 'notify-n8n' in line or line.lstrip().startswith('- bash:') and 'build.addbuildtag' in '\n'.join(lines[i:i+5]):
            indent=len(line)-len(line.lstrip()); end=i+1
            while end<len(lines) and (not lines[end].strip() or len(lines[end])-len(lines[end].lstrip())>indent): end+=1
            out.append(' '*indent+'- ${{ if not(parameters.engineCapManaged) }}:')
            out.extend('  '+x if x else '' for x in lines[i:end]);i=end;continue
        out.append(line);i+=1
    ci='\n'.join(out)+'\n'
    # Marker is a real emitted step, retained in expanded YAML (comments disappear).
    ci=ci.replace('        steps:\n', "        steps:\n        - script: echo engine-cap-managed-ci\n          displayName: 'Engine CAP managed CI contract'\n",1)
    template_file=shared/'stages/deploy-stages-template-azure-artfacts.yml'
    template=template_file.read_text(encoding='utf-8-sig')
    shared_commit=subprocess.run(['git','rev-parse','HEAD'],cwd=shared,check=True,capture_output=True,text=True).stdout.strip()
    if not re.fullmatch(r'[a-f0-9]{40}',shared_commit): raise ValueError('Shared template checkout is not an immutable commit')
    ref_match=re.search(r'^\s*ref:\s*(refs/tags/[^\s]+)',cd,re.M)
    if not ref_match: raise ValueError('CD must pin the shared template to a tag')
    shared_ref=ref_match.group(1)
    resolved_ref=subprocess.run(['git','rev-parse',shared_ref+'^{}'],cwd=shared,check=True,capture_output=True,text=True).stdout.strip()
    if resolved_ref != shared_commit: raise ValueError('Shared template tag does not resolve to checkout HEAD')
    # Reuse reviewed shared implementation locally, with provenance and only DEV defaults.
    template=template[:template.index('                - template: ../steps/notify-n8n')]
    template=template.replace('parameters:\n','parameters:\n  - name: expectedApi\n    type: string\n  - name: expectedOrg\n    type: string\n  - name: expectedSpace\n    type: string\n',1)
    defaults={'stageName':'Deploy_DEV','displayName':'Deploy DEV','deploymentName':'DeployDev','varGroup':'DEV','sourcePipeline':'ci'}
    for name,value in defaults.items():
        template=template.replace(f'  - name: {name}\n    type: string\n',f'  - name: {name}\n    type: string\n    default: {value}\n')
    template=template.replace('    default: ci\n    default: current','    default: ci')
    template=template.replace('  - name: dependsOn\n    type: object','  - name: dependsOn\n    type: object\n    default: []')
    template=template.replace('  - name: condition\n    type: string','  - name: condition\n    type: string\n    default: succeeded()')
    template=template.replace("                - checkout: templates", "                - checkout: self\n                  path: 'engine-source'\n                - checkout: templates",1)
    guard='''                - script: python3 "$(Pipeline.Workspace)/engine-source/pipeline/mta_version_guard.py"
                  displayName: engine-cap-mta-version-guard
                  env:
                    EXPECTED_CF_API: ${{ parameters.expectedApi }}
                    EXPECTED_CF_ORG: ${{ parameters.expectedOrg }}
                    EXPECTED_CF_SPACE: ${{ parameters.expectedSpace }}
                    ENVIRONMENT: ${{ parameters.expectedSpace }}
                    MTAR_PATH: $(MTAR_PATH)
                    MTAEXT_PATH: $(MTAEXT_PATH)

'''
    template=template.replace('                - script: |\n                    echo "Deploying:',guard+'                - script: |\n                    set -euo pipefail\n                    echo "Deploying:')
    template=template.replace('                    MTAR=$(ls "${DROP}"/*.mtar | head -n 1)', '                    mapfile -t MTARS < <(find "$DROP" -maxdepth 1 -name "*.mtar" -type f)\n                    [ "${#MTARS[@]}" -eq 1 ] || { echo "Expected exactly one MTAR"; exit 1; }\n                    MTAR="${MTARS[0]}"')
    template=template.replace('                    cf login -a', '                    set -euo pipefail\n                    cf login -a')
    (root/'pipeline').mkdir(exist_ok=True)
    (root/'pipeline/engine-cap-dev-only.yml').write_text(f'# Derived from azure-pipelines-templates {shared_ref} ({shared_commit}).\n'+template,encoding='utf-8')
    shutil.copyfile(Path(__file__).resolve().parent.parent/'assets/mta_version_guard.py', root/'pipeline/mta_version_guard.py')
    if scaffold:
        # Handlebars must emit Azure compile-time expressions literally.
        cd=cd.replace('${{','$\\{{');ci=ci.replace('${{','$\\{{')
    cd_path.write_text(cd,encoding='utf-8');ci_path.write_text(ci,encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('shared',type=Path);p.add_argument('--environment',required=True);p.add_argument('--expected-api',required=True);p.add_argument('--expected-org',required=True);p.add_argument('--scaffold',action='store_true');a=p.parse_args();adapt(a.root,a.shared,a.environment,a.expected_api,a.expected_org,a.scaffold)
