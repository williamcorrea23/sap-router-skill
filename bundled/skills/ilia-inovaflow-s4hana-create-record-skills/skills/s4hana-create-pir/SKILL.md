---
name: s4hana-create-pir
description: Create Purchasing Info Records (PIRs) in SAP S/4HANA Cloud Public or on-prem private edition via OData V2 A_PurchasingInfoRecord deep-insert at API_INFORECORD_PROCESS_SRV. Use whenever the user wants to create, post, add, generate, seed, onboard, or maintain purchasing info records — phrases like "create PIRs for supplier X", "add info records", "seed PIR demo data", "maintain prices for these materials", "onboard supplier-material pricing", "make me a few PIRs". Handles header + org-plant deep-insert in one POST, master-data lookup (eligible materials with ProcurementType=F, suppliers with PurchOrg setup), idempotent bulk batches, and known constraints (ProcurementType F only, supplier must have A_SupplierPurchasingOrg row for the target PurchOrg, StandardPurchaseOrderQuantity mandatory, PurchasingInfoRecordCategory lives on org-plant entity NOT header). Do NOT use for PIR price-condition updates (separate entity), PIR deletion, or category 1/2 (subcontracting/consignment) PIRs (untested).
---

# s4hana-create-pir

Create Purchasing Info Records on SAP S/4HANA Cloud Public. **Verified production-ready against SAP S/4HANA Cloud Public Edition 2026-05-12 (PIR 5300000130 created via API; 119 prior bulk-migrated PIRs from 2026-05-05).**

## When to trigger
Verbs: create / post / add / generate / seed / maintain / onboard
Objects: PIR(s), purchasing info record(s), info record(s), supplier-material pricing
Counts: 1 to ~200 records.

## Hard rules (never violate)
1. Always do a 1-record live POST as a probe before bulk (≥3 records).
2. Never invent IDs — verify Supplier exists on the target PurchOrg, Material has `ProcurementType=F`, both exist in the target Plant.
3. If a required field has no sensible default and the user didn't specify → **ask once**, then auto-pick.
4. Scripts go in `<cwd>/.s4hana-tmp/create-pirs-<YYYYMMDD-HHMM>/`. Never commit, never modify `.env`.
5. POSTs are sequential with 200ms delay; halt on 3 consecutive failures.

## Endpoint
- Service path: `/sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV`
- Entity sets: `A_PurchasingInfoRecord`, `A_PurgInfoRecdOrgPlantData`
- Method: POST (deep-insert with `to_PurgInfoRecdOrgPlantData`)
- Communication scenario: `SAP_COM_0102` — "Purchasing Info Record Integration"

## Phases

## Phase 0 — Setup check (MANDATORY, no exceptions)

**Before any API call, before any tool use, do this check. Even if you already know credentials from earlier in the conversation — IGNORE that knowledge and re-check from scratch each invocation.**

1. **Announce**: tell the user "Checking for SAP credentials in `<current cwd>`..."
2. **Check ONLY these two sources:**
   - A `.env` file at `./.env` (in the current working directory — NOT parent dirs, NOT `~/.env`, NOT any memory file)
   - Shell-exported env vars: `SAP_HOST` AND `SAP_AUTH_MODE` both present
3. **If neither**: auto-create `./.env` from the bundled template (curl from `https://raw.githubusercontent.com/ilia-inovaflow/s4hana-create-record-skills/main/.env.example`), append `.env` to `.gitignore` if not already there, tell the user clearly what to fill in (auth mode + host + creds), and **wait** for them to say "ready" before making any API call. Never overwrite an existing `.env`.
4. **If credentials are present**: report back to the user: "✓ Loaded credentials for `<host>` in `<auth-mode>` mode. Proceeding with [task]."

**Never use credentials from conversation memory, from another project's `.env`, or from any tenant the user previously worked with in a different session.** Each project gets its own `.env`. See [`shared/setup-check.md`](../../shared/setup-check.md) for the full rationale and edge cases.


## Cross-tenant migration notes
- Source PIR IDs do NOT carry forward — Cloud auto-assigns.
- For pair (supplier, material): both must exist in target with their PurchOrg/plant relationships established. If migrating from a source with different supplier/material pools, hash-pair them deterministically.
- 2026-05-05 migration: 109 PIRs created in one batch by hash-pairing 81+ SUPL suppliers against ~100 ProcurementType=F materials at plant 1010. Side-effect: 210 pricing condition records auto-generated.

## Known error catalog

| Code | Cause | Fix |
|---|---|---|
| `ME/083` | "Enter G/L Account" OR "Enter Standard Order Quantity" | The PIR variant: add `StandardPurchaseOrderQuantity` to org-plant entity |
| `ME/092` | Procurement type doesn't match (material is in-house `E`, but PIR needs `F` external) | Filter materials to `ProcurementType=F` only |
| `06/321` | Supplier does not exist in purchasing organization | Extend supplier with `A_SupplierPurchasingOrg` row for the target PurchOrg first |
| `Property X is invalid` | Header has fields that belong on org-plant (e.g. `PurchasingInfoRecordCategory`) | Move them into `to_PurgInfoRecdOrgPlantData` |
| `MM_PUR_PIR/xxx` generic | Check `innererror.errordetails` | Specific field will be named |

## Output structure
```
<cwd>/.s4hana-tmp/create-pirs-<YYYYMMDD-HHMM>/
├── eligible-pairs.json # (supplier, material) candidates after filtering
├── payloads.json
├── create-log.jsonl
├── results.json
└── verify-sample.json
```

## Reference files
- `references/envelope-template.md` — full schema with all optional fields
- `references/known-quirks.md` — header vs org-plant fields, ProcurementType filter, supplier-purchorg requirement, side-effects
- `scripts/bulk-pir-poster.mjs` — reference implementation
