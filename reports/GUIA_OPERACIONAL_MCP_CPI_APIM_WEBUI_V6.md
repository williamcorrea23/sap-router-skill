# Guia operacional MCP CPI/APIM/Web UI v6

Fonte canonica: `.agents/registries/mcps.json` + `.agents/registries/capabilities.json`.

## CPI deploy com PUT e fallback

1. Criar plano:

```powershell
python scripts\cpi_client.py deploy plan `
  --artifact-id MEU_IFLOW `
  --version active `
  --zip caminho\iflow.zip `
  --strategy auto `
  --runtime-deploy
```

2. Aprovar:

```powershell
python scripts\approval_broker.py approve <action_id>
```

3. Executar o `commit_command` retornado pelo plano.

`--strategy auto` tenta `PUT` primeiro. Se proxy/WAF/politica bloquear metodo, tenta `POST` com `X-HTTP-Method-Override: PUT`. O runtime deploy usa `POST /api/v1/DeployIntegrationDesigntimeArtifact`.

## CPI MCP stdio

Servidor:

```powershell
python scripts\sap_integration_mcp.py --product cpi
```

Ferramentas principais:

- `cpi_test_connection`
- `cpi_packages`
- `cpi_artifacts`
- `cpi_logs`
- `cpi_deploy_plan`
- `cpi_deploy_commit`

## APIM deploy/modify gated

1. Criar plano:

```powershell
python scripts\apim_client.py deploy plan `
  --bundle caminho\proxy-or-policy.zip `
  --target MEU_PROXY `
  --method PUT `
  --strategy auto
```

2. Aprovar:

```powershell
python scripts\approval_broker.py approve <action_id>
```

3. Executar o `commit_command`.

Use `--path` quando a API APIM alvo nao for o default `APIProxies('<target>')/$value`.

## APIM MCP stdio

Servidor:

```powershell
python scripts\sap_integration_mcp.py --product apim
```

Ferramentas principais:

- `apim_health`
- `apim_proxies`
- `apim_policy_validate`
- `apim_deploy_plan`
- `apim_deploy_execute`

## Web UI fallback com sessao logada

1. Iniciar Chrome com CDP:

```powershell
chrome.exe --remote-debugging-port=9222 --user-data-dir=%TEMP%\sap-router-chrome
```

2. Login manual no tenant CPI/APIM.

3. Configurar URL:

```powershell
$env:CPI_WEB_URL="https://<tenant>/itspaces"
$env:APIM_WEB_URL="https://<tenant>/apiportal"
```

4. Rodar probe:

```powershell
python scripts\browser_session_probe.py
```

5. Usar MCP:

```powershell
node scripts\web_ui_mcp_bridge.mjs --product cpi
node scripts\web_ui_mcp_bridge.mjs --product apim
```

Ferramentas:

- `<product>_webui_status`
- `<product>_webui_open`
- `<product>_webui_capture_evidence`
- `<product>_webui_plan_action`

O bridge nao aceita senha nem exporta cookies.

## Healthcheck v6

```powershell
python scripts\healthcheck.py --quiet --json --v6
python scripts\healthcheck.py --quiet --json --v6 --execute-v6
```

Estagios:

- `DECLARED`
- `INSTALLED`
- `CONFIGURED`
- `INITIALIZED`
- `DOMAIN_READY`
- `MUTATION_READY`

## Validacao local

```powershell
python scripts\validate_catalog.py --json
python scripts\mcp_probe.py probe --server sap-cpi-mcp --execute
python scripts\mcp_probe.py probe --server sap-apim-mcp --execute
python scripts\generate_ide_assets.py check
python .claude\skills\run-sap-router-skill\driver.py
```
