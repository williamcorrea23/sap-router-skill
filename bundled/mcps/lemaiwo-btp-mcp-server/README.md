# BTP MCP Server

An MCP (Model Context Protocol) server for SAP BTP administration, powered by [odata-mcp-proxy](https://www.npmjs.com/package/odata-mcp-proxy). It exposes BTP Core Services APIs as MCP tools, allowing AI assistants like Claude to manage your BTP landscape through natural language.

The entire server is defined through a single JSON config file -- no custom code required.

## How It Works

This project uses the `odata-mcp-proxy` npm package, which maps OData/REST services to MCP tools based on a configuration file. You provide a config describing your APIs and entity sets, and the proxy generates the corresponding MCP tools automatically.

```
AI Assistant (Claude, Cursor, etc.)
        |
        | MCP Protocol (HTTP or stdio)
        v
  odata-mcp-proxy
        |
        | REST + OAuth2 (via BTP Destination Service)
        v
  BTP Core Services APIs
```

Think of it like the [SAP Application Router](https://www.npmjs.com/package/@sap/approuter) -- a ready-made runtime you configure, not code you write.

## Exposed BTP APIs

The config file (`btp-admin-api-config.json`) defines three BTP Core Services and the XSUAA Authorization API:

### Account Management

| Tool | Operations | Description |
|------|-----------|-------------|
| `GlobalAccount` | list | View global account details |
| `Subaccounts` | list, get, create, update, delete | Manage subaccounts |
| `Directories` | list, get, create, update, delete | Organize subaccounts into directories |

### Entitlements

| Tool | Operations | Description |
|------|-----------|-------------|
| `Assignments` | list, update | Manage service plan entitlement assignments |
| `AllowedDataCenters` | list | View available data centers |

### Provisioning

| Tool | Operations | Description |
|------|-----------|-------------|
| `EnvironmentInstances` | list, get, create, delete | Manage runtime environments (e.g. Cloud Foundry orgs) |
| `AvailableEnvironments` | list | View environment types available for provisioning |

### Authorization (XSUAA)

| Tool | Operations | Description |
|------|-----------|-------------|
| `Applications` | list, get | View XSUAA application registrations |
| `RoleCollections` | list, get, create, update, delete | Manage role collections |
| `Roles` | list, get, create, delete | Manage roles derived from role templates |
| `RoleTemplates` | list, get | View role templates defined by applications |

All `_list` tools support OData query parameters: `$filter`, `$select`, `$expand`, `$orderby`, `$top`, `$skip`.

## Claude Code Skill

The repository ships a [Claude Code skill](https://code.claude.com/docs/en/skills) at `.claude/skills/btp-admin/SKILL.md` that teaches Claude how to use these tools efficiently:

- **Tool selection** -- maps common admin tasks ("entitle a service", "create a CF org") to the right tool on the first try
- **Token discipline** -- always use `$select`, `$filter`, and `$top` so verbose BTP list responses stay small
- **Payload shapes** -- documents request bodies the JSON schemas can't fully express (entitlement `amount` vs `enable`, environment instance `parameters`, role keys)
- **Workflows and pitfalls** -- multi-step recipes (subaccount onboarding) and async-operation handling

Skills use progressive disclosure: only the name and description are loaded into context until a BTP admin task triggers the full skill, so the standing cost is a few dozen tokens. Anyone cloning this repository and using Claude Code gets it automatically; it also works when the repo is added as a project in claude.ai.

## Prerequisites

- **Node.js** 18+ (20+ recommended)
- **SAP BTP account** with a Cloud Foundry environment
- **BTP Destinations** configured for the CIS APIs (Accounts, Entitlements, Provisioning) with OAuth2 authentication
- **Cloud Foundry CLI** (`cf`) and **MBT Build Tool** (`mbt`) for deployment

## Project Structure

```
btp-mcp-server/
├── package.json                # Start script + odata-mcp-proxy dependency
├── btp-admin-api-config.json   # API configuration (defines all MCP tools)
├── .claude/skills/btp-admin/   # Claude Code skill: tool selection + token-usage guidance
├── mta.yaml                    # BTP Cloud Foundry deployment descriptor
├── xs-security.json            # XSUAA OAuth2 configuration
├── default-env.json            # Local dev credentials (gitignored)
└── LICENSE
```

## Getting Started

### 1. Install dependencies

```bash
npm install
```

### 2. Configure BTP destinations

Create three BTP Destinations pointing to the CIS APIs:

| Destination | URL |
|-------------|-----|
| `BTP_ACCOUNTS_SERVICE` | `https://accounts-service.cfapps.<region>.hana.ondemand.com` |
| `BTP_ENTITLEMENTS_SERVICE` | `https://entitlements-service.cfapps.<region>.hana.ondemand.com` |
| `BTP_PROVISIONING_SERVICE` | `https://provisioning-service.cfapps.<region>.hana.ondemand.com` |

Each destination should use OAuth2 client credentials authentication.

### 3. Local development

Create a `default-env.json` with your BTP service bindings (XSUAA, Destination, Connectivity) to run locally:

```bash
npm start
```

This runs `odata-mcp-proxy --config btp-admin-api-config.json`.

### 4. Deploy to BTP

```bash
npm run build:btp     # Build MTA archive
npm run deploy:btp    # Deploy to Cloud Foundry
```

The MTA deployment provisions three service instances:
- **Destination** (lite) -- resolves API endpoints and manages OAuth2 tokens
- **Connectivity** (lite) -- enables secure backend connectivity
- **XSUAA** (application) -- handles OAuth2 authentication with role-based access control

## Security

The XSUAA configuration (`xs-security.json`) defines three role templates:

| Role | Scopes | Description |
|------|--------|-------------|
| `MCPViewer` | read | Read-only access |
| `MCPEditor` | read, write | Read and write access |
| `MCPAdmin` | read, write, admin | Full administrative access |

OAuth2 redirect URIs are pre-configured for Claude.ai, Cursor, Microsoft Teams, and local development.

## Creating Your Own MCP Server

This project demonstrates how easy it is to create a custom MCP server using `odata-mcp-proxy`. To build your own:

1. Create a new project and install the dependency:
   ```bash
   mkdir my-mcp-server && cd my-mcp-server
   npm init -y
   npm install odata-mcp-proxy
   ```

2. Add a start script to `package.json`:
   ```json
   {
     "scripts": {
       "start": "odata-mcp-proxy --config my-api-config.json"
     }
   }
   ```

3. Define your APIs in a config file (`my-api-config.json`):
   ```json
   {
     "server": {
       "name": "my-mcp-server",
       "version": "1.0.0",
       "description": "My custom MCP server"
     },
     "apis": [
       {
         "name": "my-api",
         "destination": "MY_BTP_DESTINATION",
         "pathPrefix": "/api/v1",
         "csrfProtected": true,
         "entitySets": [
           {
             "entitySet": "Products",
             "description": "Product catalog",
             "category": "master-data",
             "keys": [{ "name": "Id", "type": "string" }],
             "operations": { "list": true, "get": true, "create": false, "update": false, "delete": false }
           }
         ]
       }
     ]
   }
   ```

4. Add your `mta.yaml`, `xs-security.json`, and BTP Destinations, then deploy. That's it -- no code to write.

## License

MIT
