# Tenant setup, roles and portal layout

Read this when enabling the capability on a fresh subaccount, when a call fails with an
authorization error, or when locating something in the portal UI.

## Enabling the capability

Requires role collection `Integration_Provisioner`. Integration Suite → *Capabilities* →
*Add Capabilities* → **Manage APIs** → optionally Developer Hub and API Composition → *Activate*.

First-time API Management setup, under *Settings → Runtimes → Configure*:

1. **Account Type** — `Non-Production` or `Production`. **Fixed at creation**; changing it means
   tearing down and recreating the tenant. Confirm intent before the operator commits.
2. **Virtual Host** alias (≤63 chars) — proxies then resolve at
   `https://<virtualHost>.apimanagement.hana.ondemand.com`.
3. Notification contact email, and the *Make `<User>` API Portal administrator* checkbox.
4. *Activate* → *Confirm* → asynchronous provisioning, retried 3× on failure
   (incident component `OPU-API-OD-DT`).
5. **Log out and back in** — the *Connections* tab only appears afterwards.

Two coexistence rules that block onboarding:

- An Integration Suite subaccount holding a *starter plan* instance cannot host the API Management
  capability.
- The capability cannot coexist with the standalone *API Management, API portal* tile in the same
  subaccount.

Source: [Setting Up API Management](https://help.sap.com/docs/integration-suite/sap-integration-suite/setting-up-api-management-f34e86c).

## Role collections

| Role collection | Grants |
|---|---|
| `Integration_Provisioner` | Activate capabilities |
| `APIManagement.Selfservice.Administrator` | Onboarding, *Settings* page, additional virtual hosts |
| `APIPortal.Administrator` | Full CRUD: proxies, products, providers, certificates, KVMs, API Designer |
| `APIPortal.Configurator` | View/edit providers, certificates, rate plans — no proxy edit |
| `APIPortal.Developer` | CRUD on proxies, policy templates, products; read-only elsewhere |
| `APIPortal.Tester` | Test and debug proxies only |
| `APIPortal.Guest` | Read-only |

Developer Hub: `AuthGroup.SelfService.Admin` (onboarding), `AuthGroup.API.Admin` (approve
developers, create apps on their behalf), `AuthGroup.API.ApplicationDeveloper` (self-service apps),
`AuthGroup.Content.Admin`, `AuthGroup.Site.Admin`.

`APIPortal.Service.CatalogIntegration` and `AuthGroup.ContentAuthor` are **internal** — never
assign them to users or custom role collections.

Source: [Role Collections in API Management](https://help.sap.com/docs/integration-suite/sap-integration-suite/role-collections-in-api-management-7010b58).

## Object model

Account → **API Provider** (backend system) → **API proxy** → **Product** (bundle of proxies)
→ **Application** (developer-created consumer, holds key + secret) → Developer.

## Portal layout

| Portal area | Purpose |
|---|---|
| *Configure → APIs* | Create/import proxies, API providers, Key Value Maps |
| *Configure → APIs → Policy Templates* | Reusable policy bundles |
| *Engage → Products* | Bundle proxies into products, publish |
| *Engage → Applications* | Developer applications and their keys |
| *Test → APIs* | API Test Console |
| *Monitor* | API Analytics — usage, latency |
| *Settings → Runtimes* | Onboarding, virtual hosts, connections |

Two URLs, easy to confuse:

- The capability lives inside the Integration Suite shell at
  `https://<subaccount>.integrationsuite.cfapps.<region>.hana.ondemand.com` — this is where a human
  logs in, and what `APIM_WEB_URL` points at.
- The provisioned API portal app sits at `https://<apiportal-app>.cfapps.sap.hana.ondemand.com` —
  this is the service key's `url`, used for API calls, never for interactive login.

## Virtual hosts and custom domains

Up to **11 virtual hosts** per tenant (`Monitor → Integrations and APIs → Runtime: Integration Cell
→ Virtual Host → Add`): host alias ≤22 chars, alphanumeric plus hyphen, client-certificate auth
Optional/Mandatory/Disabled. `Default` is reserved.

A genuine custom domain additionally needs the BTP Custom Domain Service, a SaaS route mapping, and
**an SAP support incident on component `OPU-API-OD-OPS`** — the final routing step is performed by
SAP operations, not self-service. State that upfront rather than letting the operator expect a
self-service flow.
