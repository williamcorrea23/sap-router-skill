# Promote-to-specific-skill checklist

When an entity has been successfully created multiple times via the generic skill, it's time to graduate it to a dedicated specific skill. This makes future runs faster (skip probe phase), more reliable (verified field shape), and easier to maintain.

## When to promote

Trigger promotion when ALL of these are true:
- ✅ ≥3 successful POSTs of the same entity type
- ✅ The working envelope/payload shape is stable (no field-shape changes between runs)
- ✅ User has confirmed the result is correct (not just that SAP returned 200)
- ✅ The entity is likely to be requested again (general utility, not a one-off)

## How to promote

1. Create folder: `skills/s4hana-create-<entity>/`
2. Copy `SKILL.md` template from one of the existing specific skills (`s4hana-create-invoice` is the most complete reference)
3. Fill in:
   - **Frontmatter `name` and `description`** — be specific about which entity, which API, and trigger phrases. Use the description budget (1024 chars) — it determines triggering accuracy.
   - **Endpoint** — service path, method, comm scenario (`SAP_COM_xxxx`)
   - **Phases** — adjust master-data resolution and payload-build steps for this entity
   - **Phase 0 — Setup check** — copy the standard block from any specific skill
4. Move discovered field values + quirks into the new skill's `references/`:
   - `envelope-template.md` — the working payload shape
   - `known-errors.md` (or `known-quirks.md`) — error codes encountered + fixes
5. Write a `scripts/bulk-<entity>-poster.mjs` reference implementation following the pattern in existing skills (`bulk-invoice-poster.mjs` is a good template).
6. Update the generic skill's "When to trigger" routing table to defer the entity to the new skill.
7. Update the generic skill's "Current Phase 2 candidates" list — strike through the promoted entity.
8. Update the repo README "What's inside" table and "Repo layout" tree.
9. Bump the plugin version (`plugin.json` + `marketplace.json`) — typically a minor version bump (e.g. 1.5 → 1.6).
10. Commit + push.

## What to keep in the generic skill after promotion

- Update the routing table to point at the new specific skill (so future triggers route correctly).
- Keep any historical learnings as references if they're useful for related future entities.

## Current promotion targets (not yet shipped)

Entities probed but not yet promoted to specific skills. These are realistic candidates for future versions of the plugin:

| Entity | Status | Notes |
|---|---|---|
| `s4hana-create-purchase-requisition` | Untested | Upstream of PO. Common in approval-workflow demos. Service: `API_PURCHASEREQ_PROCESS_SRV` |
| `s4hana-create-purchase-contract` | Untested | Long-term sourcing (outline agreement). Service: `API_PURCHASECONTRACT_PROCESS_SRV` |
| `s4hana-create-inbound-delivery` | Untested | Advance Shipping Notification (ASN). Service: `API_INBOUND_DELIVERY_SRV` |
| `s4hana-create-product-description` | Pattern verified via update-record | Description-only updates via `A_ProductDescription` PATCH. Already covered by `s4hana-update-record`; standalone create skill would be redundant. |
| `s4hana-create-asset-master` | Untested | Fixed asset master data |
| `s4hana-create-sales-order` | Untested | Outbound side — completes the procure-to-pay / order-to-cash demo loop |
| `s4hana-create-classification` | Untested | Classification / characteristic values for materials |

## Anti-patterns

- ❌ Don't promote on the first successful POST. SAP often has session-specific quirks that fail on the second one.
- ❌ Don't bundle multiple unrelated entities into one skill (e.g., "`s4hana-create-master-data`" covering supplier + product + customer). Keep one entity per skill for discoverability and trigger accuracy.
- ❌ Don't extract a skill for a one-off use case (e.g. "create-goods-receipt-with-special-cost-center"). Solve in conversation, capture the working payload to the generic skill, move on.
- ❌ Don't create an `s4hana-update-<entity>` skill just because you have an `s4hana-create-<entity>` one. The generic `s4hana-update-record` skill handles updates across all entities via OData V2 PATCH with GET-PATCH-GET verify — adding entity-specific update skills duplicates work.
