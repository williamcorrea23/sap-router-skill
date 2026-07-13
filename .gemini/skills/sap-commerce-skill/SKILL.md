---
name: sap-commerce-skill
description: SAP Commerce Cloud development skill (Emenowicz/sap-commerce-skill). Reference for Hybris, composable storefront, OCC APIs, and commerce integrations.
trigger:
  keywords: [hybris, commerce cloud, occ api, spartacus, composable storefront, impex, flexiblesearch, ccv2, hac, occ v2]
  intent: Developing, querying, or integrating SAP Commerce Cloud (Hybris) — OCC v2 REST APIs, ImpEx data loads, FlexibleSearch queries, Spartacus/composable storefront setup, and CCv2 builds/deploys
prerequisites:
  - Access to a SAP Commerce instance (local Hybris, or CCv2 environment endpoint)
  - OAuth2 client registered in Backoffice (OAuthClientDetails) for OCC API calls
  - HAC access (https://<host>:9002/hac) for ImpEx and FlexibleSearch
  - For CCv2 — SAP Commerce Cloud Portal access (portal.commerce.ondemand.com)
  - For Spartacus — Node.js LTS + Angular CLI
---

# SAP Commerce Cloud (Hybris) Reference

Standalone domain reference — no local MCP covers Commerce in this repo. All calls go direct to the Commerce instance.

## 1. OCC v2 REST API

Base URL pattern: `https://<host>/occ/v2/{baseSiteId}/...` (baseSiteId e.g. `electronics-spa`).

Get an OAuth2 token (client_credentials):

```bash
curl -X POST "https://<host>/authorizationserver/oauth/token" \
  -d "grant_type=client_credentials&client_id=<client>&client_secret=<secret>"
# Response: {"access_token":"...","token_type":"bearer","expires_in":43199}
```

Key endpoints (send `Authorization: Bearer <token>`):

```bash
# Product search + detail
curl "https://<host>/occ/v2/electronics-spa/products/search?query=camera&fields=DEFAULT"
curl "https://<host>/occ/v2/electronics-spa/products/1934793?fields=FULL"

# Anonymous cart: create, add entry
curl -X POST "https://<host>/occ/v2/electronics-spa/users/anonymous/carts"
curl -X POST "https://<host>/occ/v2/electronics-spa/users/anonymous/carts/<cartGuid>/entries" \
  -H "Content-Type: application/json" -d '{"product":{"code":"1934793"},"quantity":1}'

# Registered user: orders and profile (needs password or client with trusted scope)
curl -H "Authorization: Bearer <token>" \
  "https://<host>/occ/v2/electronics-spa/users/<userId>/orders?fields=FULL"
curl -H "Authorization: Bearer <token>" \
  "https://<host>/occ/v2/electronics-spa/users/<userId>"
```

`fields=BASIC|DEFAULT|FULL` controls response verbosity. Swagger UI at `https://<host>/occ/v2/swagger-ui/index.html`.

## 2. ImpEx essentials

Run via HAC → Console → ImpEx Import, or Backoffice → System → Tools → ImpEx.

```impex
# Header sets catalog version context — REQUIRED for catalog-aware types
$catalogVersion = catalogVersion(catalog(id[default='electronicsProductCatalog']), version[default='Staged'])[unique=true, default='electronicsProductCatalog:Staged']

INSERT_UPDATE Product; code[unique=true]; name[lang=en]; unit(code); $catalogVersion; approvalStatus(code)
; MY-SKU-001 ; My Test Product ; pieces ; ; approved
; MY-SKU-002 ; Second Product  ; pieces ; ; approved

# Document ID (&ref) links rows within the same import
INSERT_UPDATE Category; code[unique=true]; $catalogVersion; &catRef
; my-category ; ; catRef1
INSERT_UPDATE CategoryProductRelation; source(&catRef); target(code, $catalogVersion)
; catRef1 ; MY-SKU-001
```

Rules:

- Every type needs its `[unique=true]` key columns; without them INSERT_UPDATE cannot resolve existing rows and duplicates or fails.
- Catalog-aware items (Product, Category, CMS) require catalogVersion in the header or rows silently mismatch Staged vs Online.
- `&ref` document IDs are import-local; they do not persist between separate imports.
- After loading Staged, run a catalog synchronization (Staged → Online) for storefront visibility.

## 3. FlexibleSearch

Run via HAC → Console → FlexibleSearch:

```sql
SELECT {p.code}, {p.name} FROM {Product AS p}
WHERE {p.code} LIKE 'MY-SKU%'

-- Join with catalog version restriction
SELECT {p.code} FROM {Product AS p JOIN CatalogVersion AS cv ON {p.catalogVersion} = {cv.pk}}
WHERE {cv.version} = 'Online'

-- Count by type
SELECT COUNT({pk}) FROM {Order}
```

Attribute names inside `{}` are case-sensitive against the type system (`{p.code}` not `{p.CODE}`). Use `?param` placeholders and fill values in the HAC parameter table for reusable queries.

## 4. Composable storefront (Spartacus)

```bash
# New Angular app + Spartacus schematics (check Spartacus release notes for the matching Angular major)
npx @angular/cli new mystore --style=scss --routing=false
cd mystore
ng add @spartacus/schematics --base-url=https://<occ-host> --base-site=electronics-spa
npm start   # http://localhost:4200
```

Runtime config lives in `spartacus-configuration.module.ts`:

```typescript
provideConfig({
  backend: { occ: { baseUrl: 'https://<occ-host>', prefix: '/occ/v2/' } },
  context: { baseSite: ['electronics-spa'], currency: ['USD'], language: ['en'] },
})
```

The OCC client used by Spartacus must allow CORS — configure `corsfilter.ycommercewebservices.*` properties (allowedOrigins, allowedMethods) on the Commerce side.

## 5. CCv2 (SAP Commerce Cloud in the Public Cloud)

Repo root must contain `manifest.json` describing the build:

```json
{
  "commerceSuiteVersion": "2211",
  "extensions": ["myextension"],
  "useConfig": {
    "properties": [{ "location": "config/local.properties" }],
    "extensions": { "location": "config/localextensions.xml", "exclude": [] }
  },
  "aspects": [
    { "name": "accstorefront", "webapps": [{ "name": "myextension", "contextPath": "" }] },
    { "name": "backoffice" },
    { "name": "api" }
  ]
}
```

Deploy flow: Cloud Portal → Builds → create build from branch → Deploy to environment (choose migration mode: none / initialize / migrate). Environment endpoints (API, Backoffice, HAC, storefront) are listed per environment in the Portal under Environments → your environment → Public Endpoints. Hostnames are tenant-generated — always copy the exact URLs shown in the Portal.

## 6. Integration with S/4HANA via SCPI

Standard pattern: SAP Commerce ↔ Cloud Integration (CPI/Integration Suite) ↔ S/4HANA.

- Outbound: Commerce ODataIntegrationService / outboundsync sends orders, customers (B2B/B2C) to CPI iFlows which map to SOAP/IDoc/OData for S/4.
- Inbound: product, price, stock replicated from S/4 into Commerce via Inbound OData (`/odata2webservices/<IntegrationObject>`).
- Define Integration Objects in Backoffice (Integration UI Tool) and expose them; authenticate CPI → Commerce with an OAuth client or basic auth inbound user.
This repo has CPI tooling — see Related for the CPI skills that build/deploy those iFlows.

## Pitfalls

- **OCC returns 401** → Cause: wrong OAuth client, expired token, or client lacks required scope/authority for the endpoint (e.g. accessing another user's cart with a basic client). Solution: re-request token, verify client in Backoffice → OAuthClientDetails, use `users/anonymous` for guest flows and trusted_client only server-side.
- **ImpEx rows silently skipped** → Cause: missing/mismatched catalogVersion or missing unique key columns; ImpEx logs a warning but continues. Solution: always declare `$catalogVersion` header for catalog-aware types, check the HAC import log for "unresolved" lines, re-run with "Enable code execution" off and validation strict.
- **FlexibleSearch returns nothing but data exists** → Cause: attribute case wrong inside `{}`, or search restrictions (session catalog versions) filtering rows. Solution: match type-system casing exactly; in HAC tick "Disable restrictions" to query across catalog versions.
- **CCv2 build fails at manifest stage** → Cause: extension named in `manifest.json` `extensions`/`localextensions.xml` not present in repo, or commerceSuiteVersion incompatible with extension pack. Solution: keep manifest extension list in sync with actual folders, pin versions per SAP release matrix, read the build log's first FAILURE line in Cloud Portal.
- **Spartacus blank page / CORS errors** → Cause: OCC CORS filter not configured for the storefront origin. Solution: set `corsfilter.ycommercewebservices.allowedOrigins` (space-separated) and redeploy or set via HAC configuration.

## Verification

```bash
# 1. Token round-trip works
curl -s -X POST "https://<host>/authorizationserver/oauth/token" \
  -d "grant_type=client_credentials&client_id=<client>&client_secret=<secret>" | grep access_token

# 2. OCC serves the base site
curl -s "https://<host>/occ/v2/electronics-spa/products/search?query=&pageSize=1" | grep totalResults

# 3. ImpEx load visible via FlexibleSearch (HAC)
#    SELECT {code} FROM {Product} WHERE {code} = 'MY-SKU-001'

# 4. Spartacus local dev renders product list at http://localhost:4200
# 5. CCv2: Cloud Portal build status = SUCCESS and deploy shows green on target environment
```

## Related

- **btp-integration-suite** — Integration Suite / CPI landscape for Commerce ↔ S/4HANA message flows
- **cpi-iflow-development** — build and deploy the CPI iFlows used by Commerce integration objects
- **sap-api-style / sap-api-policy** — API design and API Management policies when fronting OCC with APIM
- **odata** — OData semantics shared by Commerce Integration Objects inbound/outbound services
