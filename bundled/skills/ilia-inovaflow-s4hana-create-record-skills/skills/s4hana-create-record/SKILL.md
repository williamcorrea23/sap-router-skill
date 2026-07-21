---
name: s4hana-create-record
description: Generic create-record fallback for SAP S/4HANA Cloud Public or on-prem private edition. Use when the user wants to create / post / add / generate / seed a record type that does NOT have a dedicated specific skill — for example fixed asset masters, purchase requisitions, purchase contracts / outline agreements, inbound deliveries, sales orders, billing documents, work centers, classification data, etc. Triggers on phrases like "create an asset master", "make a purchase requisition", "post an inbound delivery", "add a work center", "create classification" — anything that ends with writing to S/4HANA AND isn't covered by an existing specific skill. Researches the API on the fly via $metadata + minimal-payload probing, surfaces gaps before bulk, and warns "⚠️ unverified path — confirm before bulk." If the request matches an entity covered by a specific skill (invoice, PO, business-partner, service-entry-sheet, PIR, goods-receipt, PO-confirmation), defer to that skill. Also defer to s4hana-update-record for any update/change/modify intent. Do NOT use for read/search operations.
---

# s4hana-create-record (generic create fallback)

Research-on-the-go creator for any SAP S/4HANA entity that doesn't have a dedicated specific skill yet. **⚠️ Unverified path — every record type encountered here should be probed once and confirmed by the user before bulk creation.**

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

Use this skill ONLY when a more specific skill doesn't match. Defer to specific skills first:

| User intent | Use this generic skill? |
|---|---|
| "Create supplier invoice" | ❌ → `s4hana-create-invoice` |
| "Create PO" / "create purchase order" | ❌ → `s4hana-create-po` |
| "Create supplier / vendor / customer / BP" | ❌ → `s4hana-create-business-partner` |
| "Create service entry sheet" | ❌ → `s4hana-create-service-entry-sheet` |
| "Create PIR / purchasing info record" | ❌ → `s4hana-create-pir` |
| "Create goods receipt / material document" | ❌ → `s4hana-create-goods-receipt` |
| "Create PO confirmation / supplier confirmation" | ❌ → `s4hana-create-po-confirmation` |
| "Update / change / modify any existing record" | ❌ → `s4hana-update-record` |
| "Create asset master / fixed asset" | ✅ |
| "Create purchase requisition" | ✅ |
| "Create purchase contract / outline agreement" | ✅ |
| "Create inbound delivery / ASN" | ✅ |
| "Create sales order" | ✅ |
| "Create billing document" | ✅ |
| "Create production order / work center / classification" | ✅ |
| Anything else creatable on S/4HANA not in the deferred list above | ✅ |

## Hard rules

1. ⚠️ **Always warn the user**: "Unverified path — confirm before bulk." Even after a successful 1-record probe, don't run >5 records without explicit confirmation.
2. Always do a 1-record live POST as a probe before bulk (≥3 records).
3. Never invent master-data IDs — check tenant for existence first.
4. If a required field has no sensible default and the user didn't specify → ask once, then auto-pick.
5. Scripts go in a per-session temp folder under the user's current working directory (e.g. `<cwd>/.s4hana-tmp/create-<entity>-<YYYYMMDD-HHMM>/`). Never commit, never modify `.env`.
6. POSTs are sequential with 200ms delay; halt on 3 consecutive failures.

## Phases

### Phase 1 — Identify the right service & entity

For a user request "create X":

1. Search SAP API Hub or the tenant `/sap/opu/odata/sap/` for services whose name contains relevant keywords.
2. Common patterns:
   - `API_<DOMAIN>_PROCESS_SRV` for process-driven entities (PR, contract, etc.)
   - `API_<MASTER>` for master data (e.g. `API_FIXEDASSET`, `API_PURCHASEREQ_PROCESS_SRV`)
   - Some entities use SOAP A2X instead of OData V2 — check the comm arrangement scenario in Fiori
3. If unsure which service, ask the user — don't guess.

### Phase 2 — Fetch metadata

```
GET <host>/sap/opu/odata/sap/<SERVICE>/$metadata?sap-client=<n>
```

Parse the EntityType definition for the target entity:

- Required fields (`Nullable=false` and not auto-generated)
- Field types (Edm.String / Edm.Decimal / Edm.DateTime — affects format)
- Navigation properties (for deep-insert candidates)
- Annotations like `sap:creatable=false` (creation blocked on this entity)

If `creatable=false` on the entity → STOP. Surface to user. Likely needs a different endpoint (SOAP A2X) or a different entity.

### Phase 3 — Build minimal payload

Start with ONLY the fields marked Required + the user's specified values. Skip optional fields. SAP error messages are descriptive — let SAP tell you what else is needed.

For dates: OData V2 uses `/Date(<ms-since-epoch>)/` not ISO 8601.
For amounts: typically string-decimal in JSON.

### Phase 4 — Probe POST + iterate on errors

1. CSRF flow if writing via OData V2 (see `../s4hana-create-po/references/csrf-flow.md` for the verified pattern).
2. POST minimal payload.
3. Read error message:
   - "Fill in mandatory field 'X'" → add X, retry
   - "Field 'X' value 'Y' not allowed" → check valid values via `references/error-decoder.md` (sweep technique)
   - "Configuration settings need to be corrected" → tenant config gap. STOP and report. Do NOT bulk.
   - 403 / authorization errors → comm user lacks scope. STOP and report.
4. Repeat until success or unsolvable. Cap at ~10 iterations — beyond that, the entity needs research.

### Phase 5 — Confirm with user before bulk

Once probe succeeds:

- Show the user: target ID, key fields, response summary
- Ask: "Probe succeeded. Want me to also save the working envelope template to disk and run the full bulk batch?"
- Only proceed to bulk after explicit yes.
- If user requests bulk before probe-confirmation, refuse politely and explain why.

### Phase 6 — Bulk + log

Same idempotency pattern as the specific skills (`create-log.jsonl`).

### Phase 7 — Promote to specific skill (suggest)

After successfully posting ≥3 records of an entity type, suggest to the user:

> "This entity is now verified. Consider extracting a dedicated `s4hana-create-<entity>` skill so future runs skip the probe phase."

The user can then ask for skill extraction → see [`references/promote-checklist.md`](references/promote-checklist.md) for the steps.

## Output structure

```
<cwd>/.s4hana-tmp/create-<entity>-<YYYYMMDD-HHMM>/
├── metadata-snippet.xml      # the EntityType definition
├── probe-attempts.jsonl      # iterations of minimal payloads + errors
├── working-envelope.json     # the successful payload shape
├── create-log.jsonl          # bulk run log
└── results.json              # final summary
```

## Reference files

- [`references/error-decoder.md`](references/error-decoder.md) — common SAP message classes and how to interpret them
- [`references/promote-checklist.md`](references/promote-checklist.md) — when and how to graduate an entity from generic to specific skill

## Current Phase 2 candidates (not yet promoted)

Track which generic-handled entities have been verified ≥3 times. Realistic candidates for future promotion (entities common in procurement / finance demos but not yet covered by a specific skill):

- `s4hana-create-purchase-requisition` (upstream of PO — `API_PURCHASEREQ_PROCESS_SRV`)
- `s4hana-create-purchase-contract` (outline agreements — `API_PURCHASECONTRACT_PROCESS_SRV`)
- `s4hana-create-inbound-delivery` (ASN — `API_INBOUND_DELIVERY_SRV`)
- `s4hana-create-product-description` (master-data overrides; `A_ProductDescription` PATCH — also covered by `s4hana-update-record`)
- `s4hana-create-asset-master` (fixed asset master)
- `s4hana-create-sales-order` (outbound side of order management)

Note: `s4hana-create-pricing-condition` is unlikely to need its own skill — PIRs auto-generate pricing condition records as a side-effect (documented in `s4hana-create-pir`).
