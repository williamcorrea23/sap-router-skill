import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile, writeFile, mkdir, realpath, mkdtemp, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createHash } from 'node:crypto';
import { parse } from 'yaml';
import semver from 'semver';
import { z } from 'zod';

export const Config = z.object({
  organization: z.literal('https://dev.azure.com/EngineBR'),
  project: z.string().min(1), roots: z.array(z.string()).min(1), stateDir: z.string(),
  azurePython: z.string().optional(), allowWrites: z.boolean().default(false),
  quickstartId: z.number().int().positive().default(128),
  projects: z.array(z.object({repository:z.string(),ci:z.number().int(),cd:z.number().int(),
    devEnvironment:z.string(), devApi:z.string().url(),devOrg:z.string(),devSpace:z.literal('dev')})).default([])
}).strict();
export type Settings = z.infer<typeof Config>;
export type Obj = Record<string, unknown>;
export const object = (v: unknown): Obj => v && typeof v === 'object' && !Array.isArray(v) ? v as Obj : {};
export const array = (v: unknown): unknown[] => Array.isArray(v) ? v : [];
export const sha = z.string().regex(/^[a-f0-9]{40}$/);
export const quickParams = z.object({REPOSITORY_NAME:z.string().regex(/^btp-[a-z0-9]+(?:-[a-z0-9]+)+$/).max(100),
  APP_NAME:z.string().regex(/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/).max(60),
  OWNER_EMAIL:z.string().email().regex(/^[a-zA-Z0-9_.+@-]+$/),OWNER_EMAIL2:z.string().email().regex(/^[a-zA-Z0-9_.+@-]+$/).optional(),
  FEATURE_ID:z.string().regex(/^[a-zA-Z0-9-]*$/).max(50).default('')}).strict();

export function sanitize(v: unknown): unknown {
  if(Array.isArray(v)) return v.map(sanitize);
  if(v && typeof v==='object') return Object.fromEntries(Object.entries(v).map(([k,x])=>[k,/password|secret|token|authorization|credential|signedContent/i.test(k)?'[REDACTED]':sanitize(x)]));
  if(typeof v!=='string') return v;
  return v.replace(/https?:\/\/[^\s/@]+@/g,'https://[REDACTED]@')
    .replace(/([?&](?:sig|token|access_token|code)=)[^&\s]+/gi,'$1[REDACTED]')
    .replace(/\b(?:Bearer|Basic)\s+[A-Za-z0-9+/=._-]+/gi,'[REDACTED]')
    .replace(/((?:password|secret|token|authorization)\s*[=:]\s*)[^\s,;]+/gi,'$1[REDACTED]');
}
export async function command(file:string,args:string[],cwd?:string):Promise<string> {
  try {return (await promisify(execFile)(file,args,{cwd,windowsHide:true,timeout:90000,maxBuffer:12*1024*1024,
    env:{...process.env,PYTHONIOENCODING:'utf-8',AZURE_CORE_NO_COLOR:'true',GIT_TERMINAL_PROMPT:'0'}})).stdout;}
  catch(e) {const err=e as Error & {stderr?:string}; throw new Error(String(sanitize(err.stderr || err.message)));}
}
export class Azure {
  constructor(readonly config:Settings){}
  async call(area:string,resource:string,route:Obj={},query:Obj={},body?:Obj):Promise<unknown> {
    const args=['devops','invoke','--organization',this.config.organization,'--area',area,'--resource',resource,
      '--route-parameters',`project=${this.config.project}`,...Object.entries(route).map(([k,v])=>`${k}=${v}`),
      '--query-parameters','api-version=7.1',...Object.entries(query).map(([k,v])=>`${k}=${v}`),'--output','json'];
    let temp:string|undefined;
    try {
      if(body) {temp=await mkdtemp(path.join(os.tmpdir(),'engine-cap-'));const file=path.join(temp,'request.json');await writeFile(file,JSON.stringify(body),{mode:0o600});args.push('--http-method','POST','--in-file',file);}
      const python=this.config.azurePython || (process.platform==='win32'?'C:/Program Files/Microsoft SDKs/Azure/CLI2/python.exe':undefined);
      const text=await command(python || 'az',python?['-m','azure.cli',...args]:args);
      return JSON.parse(text.replace(/^\uFEFF/,''));
    } finally {if(temp) await rm(temp,{recursive:true,force:true});}
  }
  async item(repo:string,file:string,commit:string):Promise<string> {
    const result=object(await this.call('git','items',{repositoryId:repo},{path:file,includeContent:true,'versionDescriptor.version':commit,'versionDescriptor.versionType':'commit'}));
    if(typeof result.content!=='string') throw new Error(`Conteúdo ausente: ${file}`);return result.content;
  }
}
export async function projectRoot(config:Settings,input:string):Promise<string> {
  const target=await realpath(input);
  const roots=await Promise.all(config.roots.map(r=>realpath(r)));
  if(!roots.some(r=>{const rel=path.relative(r,target);return rel==='' || (!rel.startsWith('..')&&!path.isAbsolute(rel));})) throw new Error('Projeto fora das raízes configuradas.');
  return target;
}
export async function safeFile(root:string,file:string):Promise<string|null> {
  const candidate=path.join(root,file);if(!existsSync(candidate))return null;
  const actual=await realpath(candidate); const rel=path.relative(root,actual);
  if(rel.startsWith('..')||path.isAbsolute(rel))throw new Error('Symlink fora do projeto.');
  return readFile(actual,'utf8');
}
export async function inspect(config:Settings,input:string):Promise<Obj> {
  const root=await projectRoot(config,input); const pkg=JSON.parse(await safeFile(root,'package.json') || '{}');
  const files=['mta.yaml','azure-pipelines-ci.yml','azure-pipelines-cd.yml','azure-pipelines-security-scheduled.yml','server.js','CHANGELOG.md','.azuredevops/pull_request_template.md','test','approuter','app/router','pipeline-variables','db/undeploy.json'];
  const [revision,status]=await Promise.all([command('git',['rev-parse','HEAD'],root),command('git',['status','--porcelain'],root)]);
  const ci=await safeFile(root,'azure-pipelines-ci.yml'),cd=await safeFile(root,'azure-pipelines-cd.yml');
  return {root,revision:revision.trim(),dirty:!!status.trim(),name:pkg.name,version:pkg.version,engines:pkg.engines,
    dependencies:pkg.dependencies,scripts:pkg.scripts,mta:parse(await safeFile(root,'mta.yaml')||'{}'),
    files:Object.fromEntries(files.map(f=>[f,existsSync(path.join(root,f))])),pipelines:{ci:ci?parse(ci):null,cd:cd?parse(cd):null}};
}
export function audit(info:Obj):Obj[] {
  const findings:Obj[]=[];const files=object(info.files),scripts=object(info.scripts),mta=object(info.mta);
  if(mta.version!==info.version)findings.push({code:'VERSION_MISMATCH',severity:'error',evidence:['package.json','mta.yaml']});
  if(!scripts.test || /passWithNoTests/.test(String(scripts.test)))findings.push({code:'TESTS_NOT_ENFORCED',severity:'error',evidence:'package.json scripts.test'});
  for(const file of ['azure-pipelines-security-scheduled.yml','CHANGELOG.md','.azuredevops/pull_request_template.md','pipeline-variables'])if(!files[file])findings.push({code:'STANDARD_FILE_MISSING',severity:'warning',evidence:file});
  for(const [kind,pipeline] of Object.entries(object(info.pipelines))){
    for(const r of array(object(object(pipeline).resources).repositories))if(!String(object(r).ref).startsWith('refs/tags/'))findings.push({code:'FLOATING_TEMPLATE',severity:'warning',evidence:{kind,repository:object(r).name,ref:object(r).ref}});
  }
  if(info.dirty)findings.push({code:'DIRTY_WORKTREE',severity:'warning',evidence:'Preservar mudanças; implementar em checkout isolado.'});
  return findings;
}
export function assertDevOnly(yaml:string,environment:string,expected?:{api:string,org:string,space:'dev'}):Obj {
  const parsed=object(parse(yaml)); const stages=array(parsed.stages).map(object);
  if(!stages.length || stages.some(s=>!['VerifyArtifact','Deploy_DEV'].includes(String(s.stage))) || !stages.some(s=>s.stage==='Deploy_DEV'))throw new Error('Preview não contém exclusivamente VerifyArtifact/Deploy_DEV.');
  const jobs=stages.flatMap(s=>array(s.jobs).map(object));
  for(const job of jobs){if(job.environment){const env=typeof job.environment==='string'?job.environment:object(job.environment).name;if(env!==environment)throw new Error('Environment DEV divergente.');}}
  if(!jobs.some(j=>j.environment===environment || object(j.environment).name===environment))throw new Error('Environment DEV não comprovado.');
  if(/n8n|--version-rule\s+ALL|Deploy_(?:QA|PRD|HOTFIX)|cockpit-(?:qa|prd|hotfix)/i.test(yaml))throw new Error('Preview inclui promoção/notificação ou downgrade.');
  const nodes:Obj[]=[]; const visit=(v:unknown)=>{if(Array.isArray(v))v.forEach(visit);else if(v&&typeof v==='object'){nodes.push(object(v));Object.values(object(v)).forEach(visit);}}; visit(stages.find(s=>s.stage==='Deploy_DEV'));
  const steps=nodes.filter(n=>['script','bash','pwsh','powershell','task'].some(k=>k in n));
  const text=(s:Obj)=>['script','bash','pwsh','powershell'].map(k=>typeof s[k]==='string'?s[k]:'').join('\n');
  const deploys=steps.flatMap((s,i)=>Array.from(text(s).matchAll(/\bcf\s+deploy\b/gi),()=>({s,i})));
  const logins=steps.flatMap((s,i)=>Array.from(text(s).matchAll(/\bcf\s+login\b/gi),()=>({s,i})));
  const guards=steps.map((s,i)=>({s,i})).filter(x=>x.s.displayName==='engine-cap-mta-version-guard'&&/mta_version_guard\.py/i.test(text(x.s)));
  if(steps.some(s=>/\bcf\s+target\b[^\n]*(?:\s-(?:o|s|a)\b|--(?:organization|space|api-endpoint)\b)/i.test(text(s))))throw new Error('Mudança de target após login não é permitida.');
  if(deploys.length!==1||logins.length!==1||guards.length!==1||!(logins[0].i<guards[0].i&&guards[0].i<deploys[0].i))throw new Error('Sequência única login → guard → deploy não comprovada.');
  if(expected){const env=object(guards[0].s.env);if(env.EXPECTED_CF_API!==expected.api||env.EXPECTED_CF_ORG!==expected.org||env.EXPECTED_CF_SPACE!==expected.space||env.ENVIRONMENT!=='dev')throw new Error('Guard não recebeu o destino DEV esperado.');}
  return {stages:stages.map(s=>s.stage),environment};
}
export function assertVersion(candidate:string,deployed:string):void {
  if(!semver.valid(candidate)||!semver.valid(deployed))throw new Error('Versão MTA inválida.');
  if(semver.lt(candidate,deployed))throw new Error('DOWNGRADE_BLOCKED: incremente a versão; nunca force ALL.');
}
export class Journal {
  constructor(readonly dir:string){}
  async once(key:unknown,action:()=>Promise<unknown>,reconcile:(originalAt:string)=>Promise<unknown>,retryFailed=false):Promise<unknown> {
    await mkdir(this.dir,{recursive:true}); const id=createHash('sha256').update(JSON.stringify(key)).digest('hex');const file=path.join(this.dir,`${id}.json`);
    let at=new Date().toISOString(),attempt=1;
    try {await writeFile(file,JSON.stringify({state:'submitting',key,at,attempt}),{flag:'wx',mode:0o600});}
    catch(e){
      if((e as NodeJS.ErrnoException).code!=='EEXIST')throw e;const prior=JSON.parse(await readFile(file,'utf8'));const originalAt=String(prior.at);const reconciliation=await reconcile(originalAt);
      const exact=array(object(reconciliation).exact).map(object),failed=exact.length>0&&exact.every(x=>x.status==='completed'&&['failed','canceled'].includes(String(x.result)));
      if(!retryFailed||!failed||Number(prior.attempt||1)>=3)return {state:prior.state,previous:prior.result,reconciliation,repeated:false};
      attempt=Number(prior.attempt||1)+1;at=new Date().toISOString();await writeFile(file,JSON.stringify({state:'submitting',key,at,attempt,previous:prior.result}),{mode:0o600});
    }
    try {const result=await action();await writeFile(file,JSON.stringify({state:'submitted',key,at,attempt,result:sanitize(result)}),{mode:0o600});return result;}
    catch(e){await writeFile(file,JSON.stringify({state:'unknown',key,at,attempt,error:sanitize(String(e))}),{mode:0o600});return {state:'unknown',error:sanitize(String(e)),reconciliation:await reconcile(at),instruction:'Não repetir POST sem reconciliação exata por commit, branch e parâmetros.'};}
  }
}
