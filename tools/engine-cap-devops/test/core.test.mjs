import test from 'node:test';
import assert from 'node:assert/strict';
import { sanitize, assertVersion, assertDevOnly, Journal } from '../dist/core.js';
import { mkdtemp, readFile } from 'node:fs/promises';
import os from 'node:os';
test('sanitizes PAT userinfo and bearer values',()=>assert.equal(sanitize('https://PAT@dev.azure.com/x Bearer abc.def'), 'https://[REDACTED]@dev.azure.com/x [REDACTED]'));
test('blocks MTA downgrade',()=>assert.throws(()=>assertVersion('1.0.1','1.0.2'),/DOWNGRADE_BLOCKED/));
test('requires DEV-only expanded pipeline guard',()=>assert.throws(()=>assertDevOnly('stages:\n- stage: Deploy_QA','app-dev'),/DEV/));
const devYaml=`stages:
- stage: VerifyArtifact
  jobs: []
- stage: Deploy_DEV
  jobs:
  - deployment: DeployDev
    environment: cockpit-dev
    strategy:
      runOnce:
        deploy:
          steps:
          - script: |
              cf login -a https://api.example -o Engine -s dev
              cf target
          - script: python3 pipeline/mta_version_guard.py
            displayName: engine-cap-mta-version-guard
            env:
              EXPECTED_CF_API: https://api.example
              EXPECTED_CF_ORG: Engine
              EXPECTED_CF_SPACE: dev
              ENVIRONMENT: dev
          - script: cf deploy app.mtar
`;
test('accepts one structurally ordered DEV deploy',()=>assert.deepEqual(assertDevOnly(devYaml,'cockpit-dev',{api:'https://api.example',org:'Engine',space:'dev'}).stages,['VerifyArtifact','Deploy_DEV']));
test('rejects a second CF login inside DEV',()=>assert.throws(()=>assertDevOnly(devYaml.replace('- script: cf deploy app.mtar','- script: cf login -a https://other\n          - script: cf deploy app.mtar'),'cockpit-dev'),/sequência/i));
test('rejects target mutation after guard',()=>assert.throws(()=>assertDevOnly(devYaml.replace('- script: cf deploy app.mtar','- script: cf target -o other -s qa\n          - script: cf deploy app.mtar'),'cockpit-dev'),/target/i));
test('rejects a guard wired to another target',()=>assert.throws(()=>assertDevOnly(devYaml,'cockpit-dev',{api:'https://api.wrong',org:'Engine',space:'dev'}),/destino DEV/i));
test('journal reconciles existing uncertain write',async()=>{const dir=await mkdtemp(`${os.tmpdir()}\\engine-cap-test-`);const j=new Journal(dir);let calls=0;const first=await j.once({x:1},async()=>{calls++;throw new Error('timeout')},async()=>[{id:7}]);const second=await j.once({x:1},async()=>{calls++;return {id:8}},async()=>[{id:7}]);assert.equal(calls,1);assert.equal(first.state,'unknown');assert.equal(second.repeated,false);});
test('journal reuses original timestamp during reconciliation',async()=>{const dir=await mkdtemp(`${os.tmpdir()}\\engine-cap-time-`);const j=new Journal(dir);const seen=[];await j.once({x:2},async()=>{throw new Error('timeout')},async at=>{seen.push(at);return {exact:[]}});await j.once({x:2},async()=>({id:2}),async at=>{seen.push(at);return {exact:[]}});assert.equal(seen[0],seen[1]);});
test('journal retries a reconciled failed QuickStart at most through gated path',async()=>{const dir=await mkdtemp(`${os.tmpdir()}\\engine-cap-retry-`);const j=new Journal(dir);let calls=0;await j.once({x:3},async()=>({id:1}),async()=>({exact:[]}));await j.once({x:3},async()=>{calls++;return {id:2}},async()=>({exact:[{status:'completed',result:'failed'}]}),true);assert.equal(calls,1);});
