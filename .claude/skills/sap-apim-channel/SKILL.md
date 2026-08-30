---
name: sap-apim-channel
description: >-
  This skill should be used to connect, configure and test SAP API Management (the API Management
  capability of SAP Integration Suite) from a workstation. It applies when enabling the capability,
  setting up API portal access or roles, listing or importing API proxies, attaching policies,
  building a proxy bundle, smoke-testing or debugging a deployed proxy, publishing products,
  transporting API content, or choosing between the OAuth service-key channel and the logged-in
  browser session fallback. It also carries the SAP API Policy scope rules and the MCP Gateway
  position that govern whether an agent may use these APIs at all.
trigger:
  - apim
  - api management
  - api proxy
  - api portal
  - apiportal
  - developer hub
  - api business hub enterprise
  - management.svc
  - apiportal-apiaccess
  - api policy
  - spike arrest
  - verify api key
  - api product
  - api provider
  - key value map
  - virtual host
  - mcp gateway
  - without service key
  - sem service key
---

# SAP API Management — connect, configure, test

Tooling: `apim-ui-mcp` (`scripts/web_ui_mcp_bridge.mjs --product apim`) and
`scripts/apim_proxy_packager.py`. Follow Think → Simplify → Surgical → Goal-Verify.

Target: the **API Management capability of SAP Integration Suite** (Cloud Foundry). Standalone/Neo
API Management is legacy; the references flag where it differs.

## Scope — read before the first call

This is **API lifecycle tooling**: proxies, providers, products, policies, key value maps, and the
tests that prove they work. It is **not** a business-data channel.

[SAP API Policy v.4.2026a](https://help.sap.com/doc/sap-api-policy/latest/en-US/API_Policy_latest.pdf)
§2.2.2 restricts APIs used by "(semi-)autonomous or generative AI systems that plan, select, or
execute sequences of API calls", pointing such use at SAP-endorsed pathways: Joule, the Integration
Suite **MCP Gateway**, SAP Business Data Cloud, and Agent Gateway/A2A. A human-directed proxy
deployment behind an approval gate is ordinary documented use of the management API; an agent
freely chaining calls against the business APIs those proxies front is what the policy targets.

When the goal is agent access to business data, run `apim_mcp_gateway_probe` and take that route.
The probe reads the management API's metadata for MCP-named entities; because the Gateway is
surfaced in the portal UI and the management API is not documented to advertise it, the probe
returns `ENTITIES_FOUND` or `UNKNOWN` — never a claim that the Gateway is absent. Confirm in the
portal.

## Two channels

| Channel | Auth | SAP-documented | Use for |
|---|---|---|---|
| `oauth` | `client_credentials` against an `apiportal-apiaccess` service key | **Yes** | Everything, including gated configuration changes |
| `session` | The tenant login already open in the operator's Chrome, reached over CDP | No | Reads and tests when no service key can be created |

`auto` (the default) picks `oauth` whenever a service key is configured. Every result carries the
`channel` it used and a `sanctioned` flag — quote both when reporting.

The session channel runs `fetch()` **inside the logged-in page**, so cookies stay in the browser and
are never read, stored or forwarded. Safe, but still an undocumented interface: prefer a service key
wherever one can be created, and say so when falling back. Never ask for a password — the point of
that channel is that credentials stay with the person who owns them.

### Set up the OAuth channel

1. BTP cockpit → Space → *Service Marketplace* → **API Management, API portal** → *Create* → plan
   **`apiportal-apiaccess`**.
2. Role parameter, as JSON: `{"role":"APIPortal.Administrator"}` for full CRUD,
   `{"role":"APIPortal.Guest"}` for read-only, `{"role":"APIManagement.SelfService.Administrator"}`
   for virtual-host configuration.
3. *Create Service Key* — credential type `binding-secret` (default) or `x509` (certificate-bound,
   higher security, rotate before `validity` expires). The key yields `url`, `tokenUrl`, `clientId`,
   `clientSecret`.
4. Point the repo at the downloaded JSON: `APIM_SERVICE_KEY_FILE=/secure/path/apim-service-key.json`

Discrete variables also work: `APIM_API_URL`, `APIM_TOKEN_URL`, `APIM_CLIENT_ID`,
`APIM_CLIENT_SECRET`. The file carries a client secret — `*service-key*.json` is already git-ignored;
keep it that way.

Source: [Accessing API Management APIs Programmatically](https://help.sap.com/docs/integration-suite/sap-integration-suite/api-access-plan-for-api-portal).

### Set up the session fallback

```bash
npm run apim:connect
```

Starts Chrome with remote debugging, opens `APIM_WEB_URL`, and waits while the operator completes
the tenant login themselves.

## Decision tree

```
Need API Management access
        |
        v
apim_session_status  ──► READY on channel "oauth"?  ──► use it, everything is available
        |                        no
        v
READY on channel "session"?  ──► reads and tests only; warn it is unsanctioned
        |                no
        v
BLOCKED  ──► neither a service key nor a logged-in tab
             surface the `fix` field verbatim rather than guessing
```

## Runbook

### 1. Connect

```bash
npm run apim:session
```

`READY` names the channel. `DEGRADED`/`BLOCKED` carry a `fix` field — pass it through unchanged.

### 2. Explore

- `apim_list_proxies` — proxies with base path and state; renders an interactive picker where the
  host supports MCP app widgets, plain JSON everywhere else.
- `apim_search_actions` — find an operation across proxies, products, providers, applications and
  key value maps; returns each action's id, parameters and whether it mutates.
- `apim_execute_action` — run a read-only action by id.
- `apim_api_call` — raw GET under `/apiportal/`, for paths the catalogue does not cover.

The management API is OData at `<url>/apiportal/api/1.0/Management.svc/` — `APIProxies`,
`APIProducts`, `Applications`, `KeyMapEntries`, `APIProviders`. Writes use standard OData `$batch`
multipart changesets.

### 3. Build a bundle offline

```bash
npm run apim:template -- --kind echo --name ZROUTER_SMOKE --output scratch/apim/echo.zip
npm run apim:validate -- scratch/apim/echo.zip
```

| Kind | Target | Policies | Use |
|---|---|---|---|
| `echo` | public echo service | Spike-Arrest, Add-Trace-Header, Add-CORS | Smoke-test with no backend at hand |
| `backend` | `--backend-url` supplied by the operator | Verify-API-Key, Quota, Spike-Arrest, Add-CORS | A real backend, secured |

`validate` runs offline: layout, XML well-formedness, and flow steps whose policy file is missing.
For the bundle layout, endpoint XML and the four portal creation paths, read
`references/proxy-bundle.md`. For policy shapes and their pitfalls, read `references/policies.md`.

### 4. Configure (gated)

Configuration never lands in one step:

```
apim_configure_plan                 writes a plan, changes nothing
  → python scripts/approval_broker.py approve <action_id>
    → apim_configure_commit          applies it
```

`apim_configure_plan` refuses read-only actions and `apim_execute_action` refuses mutating ones —
the split is deliberate, so an agent cannot mutate the tenant by reaching for the read tool. The
plan's `approve_command` and `commit_tool` fields carry the exact next step; pass them through
rather than paraphrasing.

The commit verifies the approval, applies the change, and only then spends it, so a failed mutation
leaves the approval usable. Read the `approval` field on every commit result:

| `approval` | Meaning |
|---|---|
| `spent` | Change applied, approval consumed. Done. |
| `still-open` | Change did **not** apply. Retry the commit, or reject the approval. |
| `applied-but-not-spent` | Change applied but the approval is still live — reject it so it cannot be replayed. |

### 5. Test and debug

```bash
npm run apim:test
```

Needs `APIM_TEST_PROXY_URL` set to the deployed proxy's runtime URL; without it the command reports
`PARTIAL` and runs only the offline checks. From an agent, `apim_test_proxy` does the same and
returns status, latency, headers and body — rendered as a request/response console where widgets are
supported.

`apim_test_proxy` is fenced twice, because testing a proxy executes whatever sits behind it:

- **Only this tenant's hosts.** Runtime traffic leaves through the virtual host, which shares no
  domain with the portal, so declare it in `APIM_RUNTIME_HOSTS` (comma-separated). With nothing
  declared the tool refuses every target. Loopback, link-local and private ranges are always
  refused, allowlist or not.
- **Only `GET`/`HEAD`/`OPTIONS`.** Write verbs are refused. To exercise a write path, drive it from
  the portal's Test Console, where a human issues the request.

The portal's own **Test Console** (`Test → APIs`) calls that same runtime endpoint, so a proxy that
answers `apim_test_proxy` answers the console too. For live traffic inspection use the portal's
**Debug** view (`Configure → APIs → <proxy> → Debug`): it captures **20 request/response
transactions per message processor** and **stops after 10 minutes**, showing per-policy execution
and which flow variables were read or assigned.

## Verify before reporting done

- `npm run apim:session` returns `READY` and names the expected channel.
- `npm run apim:validate -- <bundle>` returns `OK` for any generated bundle.
- After a deployment, the proxy appears in `apim_list_proxies` and `apim_test_proxy` returns 2xx.
- `python scripts/validate_catalog.py --json` reports no new errors.

## References

Load these as the task requires; none are needed for a routine read or test.

| File | Read it when |
|---|---|
| `references/tenant-setup.md` | Enabling the capability, fixing an authorization error, locating something in the portal, configuring virtual hosts or a custom domain |
| `references/proxy-bundle.md` | Creating a proxy, building or validating a bundle, diagnosing a rejected import |
| `references/policies.md` | Attaching, authoring or debugging a policy |
| `references/products-and-transport.md` | Publishing products, managing API keys, using key value maps, transporting content, wiring CI/CD |

## Related skills

- `sap-api-policy` — policy design and governance patterns for the proxies themselves.
- `sap-cpi-flowpilot` — the CPI-side equivalent, same plan/approve/commit governance.
- `sap-apim-mcp` — the older basic-auth bridge (`scripts/apim_client.py`); still present, but the
  OAuth channel above is the documented path.
