import { readFile } from 'node:fs/promises';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { Config, Azure, Journal, inspect, audit, sanitize, object, array, sha, quickParams, assertDevOnly, type Obj } from './core.js';

const config=Config.parse(JSON.parse(await readFile(process.env.ENGINE_CAP_CONFIG || new URL('../config.local.json',import.meta.url),'utf8')));
const azure=new Azure(config), journal=new Journal(config.stateDir);
const server=new McpServer({name:'engine-cap-devops',version:'0.1.0'});
function output(value:unknown){const data=object(sanitize({observedAt:new Date().toISOString(),source:config.organization,project:config.project,data:value}));return {content:[{type:'text' as const,text:JSON.stringify(data)}],structuredContent:data};}
function register<T extends z.ZodRawShape>(name:string,description:string,schema:z.ZodObject<T>,write:boolean,fn:(p:z.infer<z.ZodObject<T>>)=>Promise<unknown>){
  server.registerTool<z.ZodRawShape,z.ZodRawShape>(name,{description,inputSchema:schema.shape,annotations:{readOnlyHint:!write,destructiveHint:write,idempotentHint:!write,openWorldHint:true}},async (...args:unknown[])=>{
    try {if(write&&!config.allowWrites)throw new Error('Escritas desabilitadas na configuração local.');return output(await fn(schema.parse(args[0])));}
    catch(e){return {...output({state:'blocked',error:sanitize(String(e))}),isError:true};}
  });
}
const projectInput=z.object({path:z.string().min(1)}).strict();
register('inspect_project','Inventariar CAP local, revisão Git e pipelines. Não modifica arquivos.',projectInput,false,p=>inspect(config,p.path));
register('audit_project','Auditar estrutura CAP sem assumir HANA, HDI ou AppRouter obrigatórios. Templates externos exigem preview.',projectInput,false,async p=>{const info=await inspect(config,p.path);return {revision:info.revision,findings:audit(info),pending:['Executar preview remoto para resolver templates e variáveis.']};});
register('plan_project_changes','Propor adequações com evidências, sem sobrescrever código ou gerar commits.',projectInput,false,async p=>{
  const info=await inspect(config,p.path);return {revision:info.revision,findings:audit(info),steps:['Criar checkout isolado do commit remoto','Preservar contratos e testes existentes','Adicionar DEV_ONLY e engineCapManaged','Validar, revisar PR e integrar pelas políticas existentes'],optional:['HANA/HDI apenas com persistência requerida','AppRouter conforme topologia','Regras por empresa exigem especificação funcional']};
});
const runInput=z.object({pipelineId:z.number().int().positive(),commit:sha,branch:z.string().regex(/^refs\/heads\/[a-zA-Z0-9/_-]+$/).default('refs/heads/dev'),parameters:z.record(z.union([z.string(),z.boolean(),z.number()])).default({}),ciRunId:z.number().int().positive().optional()}).strict();
function request(p:z.infer<typeof runInput>):Obj {return {resources:{repositories:{self:{refName:p.branch,version:p.commit}},...(p.ciRunId?{pipelines:{ci:{version:String(p.ciRunId)}}}:{})},templateParameters:p.parameters};}
async function preview(id:number,body:Obj):Promise<string>{const result=object(await azure.call('pipelines','runs',{pipelineId:id},{},{...body,previewRun:true}));if(typeof result.finalYaml!=='string')throw new Error('Azure não retornou finalYaml.');return result.finalYaml;}
async function freeze(id:number,body:Obj):Promise<{body:Obj,yaml:string}> {
  const expanded=object(await azure.call('pipelines','runs',{pipelineId:id},{},{...body,previewRun:true}));
  if(typeof expanded.finalYaml!=='string')throw new Error('Preview indisponível.');
  // Azure returns resolved repository versions; the exact versions must accompany the POST.
  const resolved=object(object(expanded.resources).repositories),requested=object(object(body.resources).repositories),frozen:Obj={};
  const aliases=Object.keys(resolved); if(!aliases.includes('self'))throw new Error('Azure não resolveu o repositório self.');
  for(const alias of aliases){
    const r=object(resolved[alias]);
    if(typeof r.version!=='string'||!/^[a-f0-9]{40}$/.test(r.version))throw new Error(`Azure não resolveu revisão imutável para ${alias}.`);
    frozen[alias]={...object(requested[alias]),version:r.version,refName:r.refName};
  }
  return {body:{...body,resources:{...object(body.resources),repositories:frozen}},yaml:expanded.finalYaml};
}
register('preview_pipeline','Expandir YAML no Azure com previewRun=true; não inicia pipeline.',runInput,false,async p=>{
  const frozen=await freeze(p.pipelineId,request(p));return {revision:p.commit,resources:object(frozen.body.resources).repositories,finalYaml:frozen.yaml};
});
async function reconcile(pipelineId:number,commit:string,body:Obj,after:string):Promise<unknown>{
  const data=object(await azure.call('build','builds',{}, {definitions:pipelineId,'$top':30,queryOrder:'queueTimeDescending'}));
  const branch=object(object(object(body.resources).repositories).self).refName;
  const candidates=array(data.value).map(object).filter(r=>r.sourceVersion===commit&&r.sourceBranch===branch&&Date.parse(String(r.queueTime))>=Date.parse(after)-5000);
  const checked=[];for(const build of candidates){const run=object(await azure.call('pipelines','runs',{pipelineId,runId:build.id}));const sameParameters=JSON.stringify(object(run.templateParameters))===JSON.stringify(object(body.templateParameters));checked.push({id:build.id,status:build.status,result:build.result,sourceVersion:build.sourceVersion,sourceBranch:build.sourceBranch,queueTime:build.queueTime,sameParameters});}
  return {exact:checked.filter(x=>x.sameParameters),unconfirmed:checked.filter(x=>!x.sameParameters)};
}
async function submit(id:number,body:Obj,commit:string,retryFailed=false):Promise<unknown>{return journal.once({pipeline:id,body},()=>azure.call('pipelines','runs',{pipelineId:id},{},body),at=>reconcile(id,commit,body,at),retryFailed);}
register('run_ci','Executar CI configurado para commit fixo. Exige engineCapManaged, sem trigger CD nem notificações no preview.',runInput.omit({parameters:true,ciRunId:true}),true,async p=>{
  if(!config.projects.some(x=>x.ci===p.pipelineId))throw new Error('CI fora da lista configurada.');
  const frozen=await freeze(p.pipelineId,request({...p,parameters:{engineCapManaged:true}}));
  if(/build\.addbuildtag[^\n]*artifact-published|n8n/i.test(frozen.yaml))throw new Error('CI pode acionar CD/notificações; adequar engineCapManaged antes de executar.');
  if(!frozen.yaml.includes('engine-cap-managed-ci'))throw new Error('Contrato engineCapManaged não comprovado.');
  const target=config.projects.find(x=>x.ci===p.pipelineId); if(target){const cd=await freeze(target.cd,request({pipelineId:target.cd,commit:p.commit,branch:p.branch,parameters:{engineCapMode:'DEV_ONLY'}})); assertDevOnly(cd.yaml,target.devEnvironment,{api:target.devApi,org:target.devOrg,space:target.devSpace});}
  return submit(p.pipelineId,frozen.body,p.commit);
});
register('deploy_dev','Implantar artefato de CI aprovado apenas em DEV; exige CD DEV_ONLY, target conferido e guard MTA no pipeline.',z.object({pipelineId:z.number().int().positive(),commit:sha,ciRunId:z.number().int().positive()}).strict(),true,async p=>{
  const target=config.projects.find(x=>x.cd===p.pipelineId);if(!target)throw new Error('CD fora da lista configurada.');
  const ci=object(await azure.call('build','builds',{buildId:p.ciRunId}));
  if(ci.status!=='completed'||ci.result!=='succeeded'||object(ci.definition).id!==target.ci||object(ci.repository).name!==target.repository||ci.sourceVersion!==p.commit||ci.sourceBranch!=='refs/heads/dev')throw new Error('CI/repositório/commit/branch não corresponde ao alvo aprovado.');
  const artifacts=object(await azure.call('build','artifacts',{buildId:p.ciRunId}));
  if(!array(artifacts.value).some(a=>['mta-drop',ci.buildNumber].includes(object(a).name as string)))throw new Error('Artefato de deploy ausente.');
  const frozen=await freeze(p.pipelineId,request({...p,branch:'refs/heads/dev',parameters:{engineCapMode:'DEV_ONLY'}}));
  const checked=assertDevOnly(frozen.yaml,target.devEnvironment,{api:target.devApi,org:target.devOrg,space:target.devSpace});
  return {checked,submission:await submit(p.pipelineId,frozen.body,p.commit)};
});
register('start_quickstart','Criar CAP pelo QuickStart endurecido; revisão fixa, parâmetros validados e sem execução inicial de CI/CD.',z.object({commit:sha,parameters:quickParams}).strict(),true,async p=>{
  const repos=object(await azure.call('git','repositories'));const existing=array(repos.value).map(object).find(r=>String(r.name).toLowerCase()===p.parameters.REPOSITORY_NAME.toLowerCase());
  if(existing){
    const refs=array(object(await azure.call('git','refs',{repositoryId:existing.id},{filter:'heads/'})).value).map(object);
    if(refs.length){
      const names=new Set(refs.map(r=>r.name));if(names.size!==3||!['dev','qas','main'].every(b=>names.has(`refs/heads/${b}`)))throw new Error('Repositório homônimo existe em estado parcial não reconhecido.');
      const main=refs.find(r=>r.name==='refs/heads/main');const raw=await azure.item(String(existing.id),'/engine-cap-provenance.json',String(main?.objectId));
      const provenance=object(JSON.parse(raw));if(provenance.repository!==p.parameters.REPOSITORY_NAME||provenance.application!==p.parameters.APP_NAME||String(provenance.featureId||'')!==String(p.parameters.FEATURE_ID||''))throw new Error('Repositório homônimo possui proveniência diferente.');
      const definitions=array(object(await azure.call('build','definitions',{}, {repositoryId:existing.id,repositoryType:'TfsGit'})).value).map(object);
      const policies=array(object(await azure.call('policy','configurations',{}, {'$top':1000})).value).map(object).filter(r=>array(object(r.settings).scope).some(s=>object(s).repositoryId===existing.id));
      const pipelineNames=new Set(definitions.map(d=>d.name));const ci=definitions.find(d=>d.name===`${p.parameters.REPOSITORY_NAME}-ci`);
      const expectedPolicies:Record<string,boolean>={'fa4e907d-c16b-4a4c-9dfa-4906e5d171dd':true,'c6a1889d-b943-4856-b76f-9e46bb6b0df2':true,'fd2167ab-b0be-447a-8ec8-39368250530e':false,'0609b952-1397-4640-95ec-e00a01b2c241':true};
      const policyComplete=!!ci&&['dev','qas','main'].every(branch=>Object.entries(expectedPolicies).every(([type,blocking])=>policies.filter(x=>object(x.type).id===type&&x.isEnabled===true&&x.isBlocking===blocking&&array(object(x.settings).scope).some(s=>object(s).repositoryId===existing.id&&object(s).refName===`refs/heads/${branch}`&&object(s).matchKind==='Exact')&&(type!=='0609b952-1397-4640-95ec-e00a01b2c241'||object(x.settings).buildDefinitionId===ci.id)).length===1));
      if([`${p.parameters.REPOSITORY_NAME}-ci`,`${p.parameters.REPOSITORY_NAME}-cd`,`${p.parameters.REPOSITORY_NAME}-security`].every(n=>pipelineNames.has(n))&&policyComplete)return {state:'no_op',repository:existing.id,pipelines:definitions.map(d=>({id:d.id,name:d.name})),policies:12};
    }
  }
  const body=request({pipelineId:config.quickstartId,commit:p.commit,branch:'refs/heads/main',parameters:{...p.parameters,OWNER_EMAIL2:p.parameters.OWNER_EMAIL2||p.parameters.OWNER_EMAIL,FEATURE_ID:p.parameters.FEATURE_ID||' ',PROJECT_NAME:config.project}});
  const frozen=await freeze(config.quickstartId,body);
  if(!frozen.yaml.includes('engine_quickstart.py')||!frozen.yaml.includes('SCAFFOLD_COMMIT'))throw new Error('QuickStart remoto ainda não contém validação segura e scaffold fixado.');
  return submit(config.quickstartId,frozen.body,p.commit,true);
});
register('get_run_diagnostics','Consultar execução, estágios e erros; opcionalmente verificar 12 políticas e pipelines do repositório criado.',z.object({runId:z.number().int().positive(),repository:z.string().regex(/^[a-z0-9-]+$/).optional(),includeLogs:z.boolean().default(false)}).strict(),false,async p=>{
  const [build,timeline]=await Promise.all([azure.call('build','builds',{buildId:p.runId}),azure.call('build','timeline',{buildId:p.runId})]);
  const b=object(build), records=array(object(timeline).records).map(object);const evidence:Obj={id:b.id,status:b.status,result:b.result,revision:b.sourceVersion,stages:records.filter(r=>r.type==='Stage'||r.result==='failed').map(r=>({name:r.name,state:r.state,result:r.result,issues:r.issues}))};
  if(p.includeLogs){evidence.logs=[];for(const r of records.filter(r=>r.type==='Task'&&r.result==='failed').slice(0,3)){const data=await azure.call('build','logs',{buildId:p.runId,logId:object(r.log).id});const text=typeof data==='string'?data:array(object(data).value).join('\n');(evidence.logs as unknown[]).push({name:r.name,errors:text.split('\n').filter(l=>/error|fail|version|quota/i.test(l)).slice(-20).map(l=>l.slice(0,1000))});}}
  if(p.repository){const repos=array(object(await azure.call('git','repositories')).value).map(object);const repo=repos.find(r=>r.name===p.repository);if(!repo)throw new Error('Repositório criado não encontrado.');
    const policies=array(object(await azure.call('policy','configurations',{}, {'$top':1000})).value).map(object).filter(r=>array(object(r.settings).scope).some(s=>object(s).repositoryId===repo.id));
    const definitions=array(object(await azure.call('build','definitions',{}, {repositoryId:repo.id,repositoryType:'TfsGit'})).value).map(object);
    const expected={
      'Minimum number of reviewers':true,
      'Comment requirements':true,
      'Work item linking':false,
      'Build':true,
    } as Record<string,boolean>;
    const scopes=policies.flatMap(r=>array(object(r.settings).scope).map(s=>({type:object(r.type).displayName,enabled:r.isEnabled,blocking:r.isBlocking,refName:object(s).refName,repositoryId:object(s).repositoryId,settings:r.settings})));
    const requiredScopes=['dev','qas','main'].flatMap(b=>Object.entries(expected).map(([type,blocking])=>({branch:`refs/heads/${b}`,type,blocking})));
    const complete=definitions.length>=3&&requiredScopes.every(req=>scopes.filter(s=>s.refName===req.branch&&s.type===req.type&&s.enabled===true&&s.blocking===req.blocking).length===1)
      &&scopes.filter(s=>s.type==='Build'&&object(s.settings).buildDefinitionId===config.projects.find(x=>x.repository===p.repository)?.ci).length===3;
    evidence.created={repository:repo.id,pipelines:definitions.map(d=>({id:d.id,name:d.name})),policies:scopes,pending:complete?[]:['Recursos incompletos: conferir tipo, escopo, bloqueio, branch e CI.']};
  }
  return evidence;
});
await server.connect(new StdioServerTransport());
