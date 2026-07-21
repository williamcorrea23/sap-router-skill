---
name: s4hana-create-business-partner
description: Create business partners (BPs) in SAP S/4HANA Cloud Public or on-prem private edition via OData V2 A_BusinessPartner deep-insert at API_BUSINESS_PARTNER. Supports suppliers (vendors with FLVN00/FLVN01 roles), customers (FLCU00/FLCU01 roles), AND combined customer+supplier BPs (sells AND buys) in a single POST. Use whenever the user wants to create, post, add, generate, seed, onboard, or clone business partners, suppliers, vendors, customers, debtors, creditors, or trading partners on S/4HANA — phrases like "create a supplier", "add a customer", "onboard vendor X", "make me a BP that's both a customer and supplier", "seed BP demo data", "clone these BPs from on-prem". Handles full BP + Address + Role + Supplier (PurchOrg + Company) + Customer (SalesArea + Company) deep-insert in one POST, master-data lookup (PurchOrg, SalesOrg, CompanyCode, recon accounts), and tenant-specific BP grouping/numbering (BP02 = internal, BP03 = external). Do NOT use for one-time vendors (CPDS grouping differs), employee BPs, or role extension on existing BPs (those need PATCH on A_BusinessPartnerRole).
---

# s4hana-create-business-partner

Create business partners on SAP S/4HANA — suppliers, customers, or combined. **Verified production-ready against SAP S/4HANA Cloud Public Edition 2026-05-12: BP 1000080 (supplier), 1000081 (customer), 1000082 (combined customer+supplier), plus 73 prior bulk-migrated suppliers.**

## Phase 0 — Setup check (MANDATORY, no exceptions)

**Before any API call, before any tool use, do this check. Even if you already know credentials from earlier in the conversation — IGNORE that knowledge and re-check from scratch each invocation.**

1. **Announce**: tell the user "Checking for SAP credentials in `<current cwd>`..."
2. **Check ONLY these two sources:**
   - A `.env` file at `./.env` (in the current working directory — NOT parent dirs, NOT `~/.env`, NOT any memory file)
   - Shell-exported env vars: `SAP_HOST` AND `SAP_AUTH_MODE` both present
3. **If neither**: auto-create `./.env` from the bundled template (curl from `https://raw.githubusercontent.com/ilia-inovaflow/s4hana-create-record-skills/main/.env.example`), append `.env` to `.gitignore` if not already there, tell the user clearly what to fill in (auth mode + host + creds), and **wait** for them to say "ready" before making any API call. Never overwrite an existing `.env`.
4. **If credentials are present**: report back to the user: "✓ Loaded credentials for `<host>` in `<auth-mode>` mode. Proceeding with [task]."

**Never use credentials from conversation memory, from another project's `.env`, or from any tenant the user previously worked with in a different session.** Each project gets its own `.env`. See [`shared/setup-check.md`](../../shared/setup-check.md) for the full rationale and edge cases.


## When to trigger
Verbs: create / post / add / generate / seed / onboard / clone
Objects: BP(s), business partner(s), supplier(s), vendor(s), customer(s), debtor(s), creditor(s), trading partner(s)
Counts: 1 to ~100 records.

## Hard rules (never violate)
1. Always do a 1-record live POST per BP type as a probe before bulk (≥3 records).
2. Never invent master data IDs — verify CompanyCode, PurchOrg, SalesOrg, recon accounts, GLAccount exist in target.
3. If a required field has no sensible default and the user didn't specify → **ask once**, then auto-pick.
4. Scripts go in `<cwd>/.s4hana-tmp/create-bps-<YYYYMMDD-HHMM>/`. Never commit, never modify `.env`.
5. POSTs are sequential with 200ms delay; halt on 3 consecutive failures.

## Endpoint
- Service path: `/sap/opu/odata/sap/API_BUSINESS_PARTNER/A_BusinessPartner`
- Method: POST (deep-insert with nested Address, Role, Customer, Supplier and their sub-entities)
- Communication scenario: `SAP_COM_0008` — "Business Partner Replication"

## Phases

### Phase 1 — Parse: what kind of BP?

| Want | Roles | Sub-entities |
|---|---|---|
| **Supplier only** | `FLVN00` (vendor) + `FLVN01` (vendor extended) | `to_Supplier` (with `to_SupplierPurchasingOrg` + `to_SupplierCompany`) |
| **Customer only** | `FLCU00` (FI customer) + `FLCU01` (extended) | `to_Customer` (with `to_CustomerSalesArea` + `to_CustomerCompany`) |
| **Combined** (sells AND buys) | All four roles | Both `to_Supplier` and `to_Customer` blocks |

User intent maps:
- "vendor" / "supplier" → supplier
- "customer" / "debtor" / "client" → customer
- "trading partner" / "both customer and supplier" → combined

### Phase 2 — Tenant defaults
Cache via tenant memory. For `<your-tenant>`:

| Setting | Value |
|---|---|
| BP grouping (internal numbering, 7-digit IDs) | `BP02` |
| BP grouping (external numbering, manual ID required) | `BP03` |
| Supplier recon account | `21100000` (Payables Domestic) |
| Customer recon account | `12100000` (Receivables) |
| Default payment terms | `0004` |
| Customer Group | `01` |
| Sales Organization | `1010` · DistributionChannel `10` · Division `00` |
| Purchasing Organization | `1010` · PurchGroup `001` |
| Company Code | `1010` · GLAccount expense `11001040` |
| Languages on address | `EN` or `DE` |

**Use BP02 by default** — internal numbering means the system auto-assigns the BP number (next 7-digit ID like 1000083). If user wants a specific 8-digit ID like `20500001`, use BP03 and supply `BusinessPartner` explicitly.

### Phase 3 — Build payload

#### Supplier-only (verified)
```json
{
 "BusinessPartnerCategory": "2",
 "BusinessPartnerGrouping": "BP02",
 "OrganizationBPName1": "<name>",
 "to_BusinessPartnerAddress": {
 "results": [{ "Country": "DE", "CityName": "...", "PostalCode": "...", "StreetName": "..." }]
 },
 "to_BusinessPartnerRole": {
 "results": [{ "BusinessPartnerRole": "FLVN00" }, { "BusinessPartnerRole": "FLVN01" }]
 },
 "to_Supplier": {
 "to_SupplierPurchasingOrg": {
 "results": [{ "PurchasingOrganization": "1010", "PurchaseOrderCurrency": "EUR", "PaymentTerms": "0004" }]
 },
 "to_SupplierCompany": {
 "results": [{ "CompanyCode": "1010", "ReconciliationAccount": "21100000", "PaymentTerms": "0004" }]
 }
 }
}
```

#### Customer-only (verified)
```json
{
 "BusinessPartnerCategory": "2",
 "BusinessPartnerGrouping": "BP02",
 "OrganizationBPName1": "<name>",
 "to_BusinessPartnerAddress": {
 "results": [{ "Country": "DE", "Language": "EN", "CityName": "...", "PostalCode": "...", "StreetName": "..." }]
 },
 "to_BusinessPartnerRole": {
 "results": [{ "BusinessPartnerRole": "FLCU00" }, { "BusinessPartnerRole": "FLCU01" }]
 },
 "to_Customer": {
 "to_CustomerSalesArea": {
 "results": [{ "SalesOrganization": "1010", "DistributionChannel": "10", "Division": "00", "CustomerGroup": "01", "CustomerPaymentTerms": "0004", "Currency": "EUR" }]
 },
 "to_CustomerCompany": {
 "results": [{ "CompanyCode": "1010", "ReconciliationAccount": "12100000", "PaymentTerms": "0004" }]
 }
 }
}
```

**Customer-specific required fields you'd miss otherwise:**
- `Language` on `to_BusinessPartnerAddress` — error `FSBP_ECC/030: Standard address doesn't have a language, needed for customer`
- `Currency` on `to_CustomerSalesArea` — error `CVI_API/003: Currency (KNVV-WAERS) is a required entry field`

#### Combined customer + supplier (verified)
Same as customer-only but ALSO include the supplier blocks. Both deep-inserts go through in one POST.

### Phase 4 — POST
Standard CSRF flow — see `../s4hana-create-po/references/csrf-flow.md`. Single POST creates BP + Address + Roles + Customer + Supplier + their org/company assignments — typically 10-15 child entities in one transaction.

### Phase 5 — Verify
`$expand=to_BusinessPartnerAddress,to_BusinessPartnerRole,to_Customer,to_Supplier` on the new BP to confirm structure.

## Cross-tenant migration notes
- Source IDs do NOT carry forward — Cloud auto-assigns with BP02. Build a source-ID → target-ID mapping CSV.
- Country distribution and BP-name patterns can be preserved.
- For customers, propagate language preferences from source addresses.

## Cleanup quirks (Cloud-specific)
- `A_BusinessPartner DELETE` is **blocked** (`CI_DRAFTBP_MESSAGE/032`). To retire a test BP: PATCH `BusinessPartnerIsBlocked=true` + rename `OrganizationBPName1=_TEST_DELETE_ME`.
- `A_Product POST` is **blocked** on Cloud (`API_PRD_MSG/009`). For migrations involving new materials, reuse the existing HAWA/FERT/SERV pool — don't try to clone materials.

## Output structure
```
<cwd>/.s4hana-tmp/create-bps-<YYYYMMDD-HHMM>/
├── payloads.json
├── create-log.jsonl
├── results.json
├── source-target-mapping.csv # for cross-tenant migrations
└── verify-sample.json
```

## Reference files
- `references/bp-roles-and-groupings.md` — full role catalog (FLCU/FLVN/BUP/etc.), grouping conventions, numbering policies
- `references/customer-vs-supplier.md` — side-by-side comparison of required fields per role type
- `references/cross-tenant-migration.md` — the pattern for cloning BPs from on-prem to Cloud with ID remapping
- `scripts/bulk-bp-poster.mjs` — reference implementation
