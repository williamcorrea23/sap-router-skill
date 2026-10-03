# engine-cap-devops

Local stdio MCP for the EngineBR CAP workflow. Reads Azure DevOps through the authenticated `az` CLI and returns compact evidence with sanitized secrets. Writes are disabled by default.

```powershell
Copy-Item config.example.json config.local.json
# edit only local paths and approved project metadata
npm ci
npm run build
node dist/index.js
```

Register in Codex after review:

```powershell
codex mcp add engine-cap-devops -- node C:/path/to/tools/engine-cap-devops/dist/index.js
```

The server never accepts shell commands, PAT values, or arbitrary URLs from tool inputs. `run_ci` and `deploy_dev` require immutable commit evidence; `deploy_dev` requires `DEV_ONLY`, target checks, an MTA guard, and a successful matching CI artifact. A journal reconciles uncertain writes.
