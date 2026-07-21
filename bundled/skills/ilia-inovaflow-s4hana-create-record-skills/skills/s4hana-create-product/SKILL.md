---
name: s4hana-create-product
description: Create product master records (materials) in SAP S/4HANA Cloud Public or on-prem private edition via OData V4 api_product/srvd_a2x/sap/product/0002 deep-insert. Use whenever the user wants to create, post, add, generate, seed, or onboard products / materials / SKUs — phrases like "create products in SAP", "seed material master", "add HAWA materials", "onboard FERT goods", "create a SERV record", "make a few demo products". Handles GET-first discovery of tenant's internal unit codes (the V4 vs V2 trap), deep-insert with explicit parent-key duplication in child description (the SADL framework trap), per-ProductType valid Product Group + Base Unit pools, idempotent bulk batches. Do NOT use this skill for SOAP MDM Replicate scenarios (different use case requiring sender business system registration) or for product extension (plant / valuation / sales / procurement views — separate entities on the same V4 service). For those, use the generic s4hana-create-record skill.
---

# s4hana-create-product

Create product master (material) records on SAP S/4HANA Cloud Public. **Verified production-ready against SAP S/4HANA Cloud Public Edition 2026-05-13 (10 products created via API: HAWA, FERT, SERV mix on `my438741`).**

## When to trigger
Verbs: create / post / add / generate / seed / onboard
Objects: product(s), material(s), SKU(s), HAWA / FERT / SERV / ROH / HALB record(s)
Counts: 1 to ~200 records.

## Hard rules (never violate)
1. **Use OData V4, not the SOAP `productmdmbulkreplicaterequest` service.** SOAP returns HTTP 202 but silently drops on Cloud Public tenants without MDG / sender-business-system registration. V4 is the supported create path.
2. **Always GET an existing product first** to discover the tenant's *internal* unit codes (e.g. `ST` for Stück, `LE` for Leistungseinheit). V2 ISO-translates these (`ST→PC`); V4 does not. Mismatched UoM → `MG/142 "value not allowed for MARM-MEINH"`.
3. **Deep-insert child must repeat parent's Product key** in each `_ProductDescription` entry. SAP's SADL framework rejects inheritance — without explicit `Product: <id>` in the child you get `CMD_PROD_RAP/003 "Property PRODUCT is a key and cannot be initial"`.
4. **One-record probe before bulk** (≥3 records).
5. Never invent unit codes or product groups — verify against existing tenant data via GET first.
6. Scripts go in `<cwd>/.s4hana-tmp/create-products-<YYYYMMDD-HHMM>/`. Never commit, never modify `.env`.
7. POSTs are sequential with 200ms delay; halt on 3 consecutive failures.

## Endpoint
- Service path: `/sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002`
- Entity sets: `Product`, `ProductDescription`, `ProductPlant`, `ProductSales`, plus 20+ extension entities
- Method: POST (deep-insert with `_ProductDescription` collection)
- Communication scenario: `SAP_COM_0009` — "Product Integration"

## Phase 0 — Setup check (MANDATORY, no exceptions)

**Before any API call, before any tool use, do this check. Even if you already know credentials from earlier in the conversation — IGNORE that knowledge and re-check from scratch each invocation.**

1. **Announce**: tell the user "Checking for SAP credentials in `<current cwd>`..."
2. **Check ONLY these two sources:**
   - A `.env` file at `./.env` (in the current working directory — NOT parent dirs, NOT `~/.env`, NOT any memory file)
   - Shell-exported env vars: `SAP_HOST` AND `SAP_AUTH_MODE` both present
3. **If neither**: auto-create `./.env` from the bundled template (curl from `https://raw.githubusercontent.com/ilia-inovaflow/s4hana-create-record-skills/main/.env.example`), append `.env` to `.gitignore` if not already there, tell the user clearly what to fill in (auth mode + host + creds), and **wait** for them to say "ready" before making any API call. Never overwrite an existing `.env`.
4. **If credentials are present**: report back to the user: "✓ Loaded credentials for `<host>` in `<auth-mode>` mode. Proceeding with [task]."

**Never use credentials from conversation memory, from another project's `.env`, or from any tenant the user previously worked with in a different session.** Each project gets its own `.env`. See [`shared/setup-check.md`](../../shared/setup-check.md) for the full rationale and edge cases.

## Phase 1 — Parse user intent
Determine: count, ProductType mix (HAWA goods / FERT finished / SERV services / ROH raw / HALB semi-finished), whether external IDs should be supplied or auto-generated (the V4 service requires explicit `Product` field — there is no auto-numbering via API).

Ask one consolidated question if ambiguous:
- How many products and what ProductType mix?
- Specific IDs / naming convention, or auto-generated (default: `<prefix><6-digit-seed>` like `H123456`)?
- Specific Base Unit pool, or pull from existing products of the same ProductType?
- Specific Product Group, or auto-pick from tenant defaults?

## Phase 2 — Discovery (cached per-tenant)
**Always do this before the first POST in any session, even if the user supplied all fields explicitly** — needed to confirm internal codes.

```http
GET /sap/opu/odata4/sap/api_product/srvd_a2x/sap/product/0002/Product
    ?$top=10
    &$select=Product,ProductType,BaseUnit,ProductGroup,IndustrySector
    &sap-client=<n>
```

From the result, build per-ProductType pools:
- **BaseUnit pool** — e.g. HAWA → `[ST, ...]`, SERV → `[LE, ...]`. V4 returns internal codes (NOT `PC` / `EA`).
- **ProductGroup pool** — common values per ProductType.
- **IndustrySector** — usually a single value tenant-wide (typically `M` for demo tenants).

Cache for the session. If empty (fresh tenant), use these conservative defaults: HAWA/FERT/ROH/HALB → BaseUnit `ST`, ProductGroup `A001`, IndustrySector `M`. SERV → BaseUnit `LE`, ProductGroup `A001`, IndustrySector `M`.

## Phase 3 — Build payload
Per record:
```json
{
  "Product": "<external-id, ≤18 chars uppercase>",
  "ProductType": "<HAWA|FERT|SERV|ROH|HALB>",
  "BaseUnit": "<internal-code from Phase 2>",
  "ProductGroup": "<from tenant pool>",
  "IndustrySector": "<usually M>",
  "_ProductDescription": [
    { "Product": "<SAME external-id>", "Language": "EN", "ProductDescription": "<≤40 chars>" }
  ]
}
```

ID generation: `<type-prefix><6-digit-seed>` (e.g. `H` for HAWA, `F` for FERT, `S` for SERV) keeps batches scannable.

## Phase 4 — CSRF + POST
1. `GET <base>/?sap-client=<n>` with `X-CSRF-Token: Fetch` — capture token + cookies.
2. `POST <base>/Product?sap-client=<n>` with the deep-insert payload above. Headers: `Authorization`, `Content-Type: application/json`, `Accept: application/json`, `X-CSRF-Token: <token>`, `Cookie: <captured>`.
3. Reuse token across batch; refresh on `403 CSRF token validation failed`.

Expected success: **HTTP 201** with full product entity in response body (including auto-populated `CreationDate`, `CreatedByUser`, `BaseISOUnit`, etc.).

## Phase 5 — Verify
After each POST: extract `Product` from the 201 response body and append `{ok, productID, productType, ts, error?}` to `create-log.jsonl`. After bulk completes, do a spot-check with `$expand=_ProductDescription`:

```http
GET /Product('<id>')?$expand=_ProductDescription&sap-client=<n>
```

Confirm `IsMarkedForDeletion=false` and the description was committed.

## Known error catalog

| Code | Cause | Fix |
|---|---|---|
| `CMD_PROD_RAP/003 "Property PRODUCT is a key and cannot be initial"` | Deep-insert child missing parent key | Add `"Product": "<same-id>"` to each `_ProductDescription` entry |
| `MG/142 "Value X not allowed for MARM-MEINH"` | Wrong unit code (used V2/ISO `PC` instead of V4 internal `ST`) | GET existing product to discover the tenant's actual code |
| `PMD_MSG/032 "Description of product X not maintained"` | Tried to POST Product without `_ProductDescription` | Description is mandatory at create — include it in deep-insert |
| `API_PRD_MSG/009 "Create operation not allowed on entity"` | Using OData V2 `API_PRODUCT_SRV` instead of V4 | Switch to V4 path — V2 is read-only for Product header |
| `M3/098 "Enter a material type"` | Missing `ProductType` | Required field, supply `HAWA`/`FERT`/etc. |
| `(none) "Enter an industry sector"` | Missing `IndustrySector` | Required even though Fiori's manual dialog doesn't ask for it |
| HTTP 202 + silent drop (SOAP path) | Used `productmdmbulkreplicaterequest` SOAP service | Switch to V4 — SOAP needs sender business system registration |

## Output structure
```
<cwd>/.s4hana-tmp/create-products-<YYYYMMDD-HHMM>/
├── tenant-discovery.json  # per-ProductType pools (BaseUnit, ProductGroup, IndustrySector)
├── payloads.json
├── create-log.jsonl
├── results.json
└── verify-sample.json
```

## Cross-tenant migration notes
- Source product IDs (MATNR) can be preserved on the target if they're ≤18 chars and the tenant allows external numbering. No internal numbering option exists via API.
- Unit codes do NOT carry across tenants — translate to the target tenant's internal codes via the Phase 2 discovery.
- Plant / sales / valuation / procurement views are SEPARATE entities (`ProductPlant`, `ProductSales`, etc.) on the same V4 service. The header create handled by this skill is sufficient for basic-data lookup but extending to a plant requires a second POST to `ProductPlant`.

## Reference files
- `references/v4-vs-soap.md` — why OData V4 and not the SOAP MDM Replicate service (decision matrix + the silent-drop trap)
- `references/field-reference.md` — complete Product entity field list with required vs optional, max lengths, deep-insert nav properties
- `scripts/bulk-product-poster.mjs` — reference implementation
