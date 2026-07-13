# Peer review — prontidão para produto distribuível

**Data:** 2026-07-13  
**Escopo:** repositório SAP Router Skill, estado atual do worktree  
**Decisão:** **NO-GO para release produtivo**

## Resumo executivo

Há uma base funcional relevante: compilação Python passa, catálogo canônico passa, assets dos quatro IDEs passam e a auditoria de segredos não encontrou padrões ativos. O roteamento também respeita a proteção principal: uma escrita funcional sem `--functional` não dispara BAPI.

O produto ainda não é liberável porque os gates críticos não são confiáveis ou estão incompletos: não existe suíte de testes descoberta, o gate ABAP falha antes de analisar qualquer arquivo, o healthcheck estrito confirma estado degradado e há deploy paths com verificação TLS desabilitada.

## Evidências executadas

| Check | Resultado | Evidência |
|---|---|---|
| `python -m compileall -q scripts python` | PASS | Todos os módulos compilam |
| `python -m unittest discover -s . -p 'test*.py'` | FAIL | 0 testes; exit 5 (`NO TESTS RAN`) |
| `python scripts/validate_catalog.py --strict` | PASS | 30 capabilities, 10 servers, 38 profiles |
| `python scripts/generate_ide_assets.py check` | PASS | Claude/Gemini/Codex/Cursor sem diffs |
| `python scripts/secret_audit.py --strict` | PASS | 0 findings |
| `python scripts/healthcheck.py --strict` | FAIL/DEGRADED | exit 1; MCPs não prontos e SOAP com erro de certificado |
| `npm run abap:review` | FAIL | abaplint não encontra configuração/arquivos; 0 arquivos analisados |
| `git diff --check` | PASS | Sem erro de whitespace |
| rota sem contexto funcional | PASS | retorna `needs-functional-context` |
| rota com contexto funcional | PASS parcial | classifica BAPI/GUI, mas não há execução/verificação real |

## Achados bloqueadores

### P0 — Gate ABAP não analisa o código

`package.json` chama `abaplint templates/**/*.abap`, mas a versão instalada retorna “Specified abaplint configuration file does not exist” e “No files found”; o comando termina sem analisar templates. O `.abaplint.json` existente não está sendo aplicado pelo CLI atual.

**Impacto:** a documentação promete syntax/security/clean/transport gates, mas o release pode passar sem análise ABAP.

**Critério de correção:** comando versionado que localize explicitamente a configuração e os arquivos, gere relatório JSON/HTML válido e falhe se a quantidade analisada for zero; adicionar teste CI para esse caso.

### P0 — Ausência de testes automatizados

`unittest discover` encontra zero testes e retorna exit 5. Não há evidência equivalente de pytest, integração HTTP simulada ou testes de contratos CLI.

**Impacto:** roteamento, approval broker, fallback, healthcheck e clientes mutantes não têm regressão verificável.

**Critério de correção:** suíte mínima cobrindo classificação/precedência/fallback, fail-closed, approval/expiração/replay, clientes CPI/APIM com HTTP mockado, healthcheck JSON, códigos de saída e geração idempotente de assets.

### P1 — TLS desabilitado em caminhos de deploy

`scripts/zrouter_deploy_http.py` usa `ssl.CERT_NONE` permanentemente; `adt_deploy.py` e `deploy_all.py` aceitam `SAP_ALLOW_UNAUTHORIZED=true` e inserem `curl -k`.

**Impacto:** credenciais Basic/OAuth e payloads de deploy podem ser interceptados; isso é incompatível com produção por default.

**Critério de correção:** verificação TLS obrigatória por default, CA configurável por arquivo, override inseguro somente com confirmação explícita de ambiente não produtivo e alerta/telemetria; teste que bloqueie `CERT_NONE` em modo produtivo.

### P1 — Healthcheck estrito não é artefato JSON confiável

O modo `--json` imprime logs quando não está em `--quiet`; redirecionar stdout produz conteúdo que não pode ser carregado como JSON. O script também retorna exit 1 em estado degradado, enquanto o pacote não separa claramente “pacote instalável” de “integrações opcionais indisponíveis”.

**Impacto:** CI/monitoramento não consegue consumir o resultado de forma robusta e pode interpretar falso positivo/negativo.

**Critério de correção:** stdout JSON puro quando `--json`, logs em stderr, schema versionado, status por capability e contrato explícito para `PASS/DEGRADED/BLOCKED`.

### P1 — Promessas documentais excedem evidência operacional

README/SKILL anunciam “every action verified”, 42 MCPs, BAPI commit/verificação e pipeline completo, mas o ambiente estrito mostra apenas parte dos MCPs prontos, SOAP falha por certificado e não há testes que comprovem execução/verificação dessas ações.

**Impacto:** risco de uso indevido e expectativa incorreta de produção.

**Critério de correção:** distinguir claramente “offline implemented”, “configured”, “domain-ready”, “mutation-ready” e “homologated”; remover claims não comprovados ou anexar evidência reproduzível.

## Achados de robustez

- Worktree contém grande conjunto de alterações e arquivos novos da migração v6 sem pipeline de CI/release demonstrado; precisa de commit/revisão de escopo antes de publicar.
- Healthcheck registra MCPs `SKIPPED`, `NOT_INSTALLED` e SOAP com certificado inválido; isso deve bloquear apenas o que for obrigatório, mas ser visível por capability.
- Tokens CSRF são parcialmente impressos em stdout (`zrouter_deploy_http.py`); mesmo truncados, devem ser tratados como segredo operacional e nunca aparecer em logs.
- O roteamento funcional classifica corretamente, mas a saída “BAPI/GUI” não prova execução, commit, BAPIRET2, BAL ou verificação MM03/VA03.
- Há caminhos com `ssl.CERT_NONE` no SOAP opcional (`sap_router.py`), controlados por variável; o modo produtivo deve rejeitar essa configuração, não apenas emitir warning.

## O que está feito

- Registry/capability catalog validável em modo estrito.
- Geração e verificação de assets multi-IDE.
- Proteção contra disparo acidental de BAPI sem contexto funcional.
- Configuração de credenciais retirada de literals nos deploy scripts revisados.
- Auditoria automatizada de segredos.
- Compilação estática dos módulos Python.

## O que falta para ser produtivo

### Onda 1 — liberar o release gate

1. Corrigir invocação/configuração do abaplint e provar arquivos analisados.
2. Criar suíte de testes automatizados e executá-la em instalação limpa.
3. Tornar healthcheck JSON puro, versionado e consumível por CI.
4. Bloquear TLS inseguro por default e retirar impressão de tokens.
5. Adicionar CI com compile, testes, catálogo, assets, secret audit, lint e smoke tests offline.

### Onda 2 — robustez operacional

1. Testar approval broker, mutações CPI/APIM, retries, timeout, idempotência e respostas parciais.
2. Definir matriz de prontidão por MCP/capability e fallback fail-closed.
3. Validar instalação limpa, dependências, upgrade e rollback.
4. Alinhar README, AGENTS, SKILL, package metadata e registries.

### Onda 3 — homologação externa

1. Smoke test controlado em SAP/BTP/CPI/APIM por ambiente.
2. Evidenciar autorização, commit, logs, verificação de resultado e transport gate.
3. Definir observabilidade, rotação de credenciais, suporte e runbook de incidente.

## Critério final de GO

GO somente com zero P0/P1 aberto, lint analisando todos os templates, suíte automatizada verde, healthcheck estrito consumível, TLS seguro por default, CI reproduzível e claims documentais limitados ao que foi comprovado.
