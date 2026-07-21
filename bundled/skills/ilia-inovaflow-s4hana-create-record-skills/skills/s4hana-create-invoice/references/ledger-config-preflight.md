# Ledger-config preflight — `FINS_ACDOC_CUST/201`

If invoice POSTs return:
```
Configuration settings need to be corrected.
Message no. FINS_ACDOC_CUST/201
```

it is **NOT an authorization issue** with the comm user. It is a tenant FI customizing gap. Same error appears in the Fiori "Create Supplier Invoice" app to a fully-authorized named user, proving auth isn't the gate.

## Root cause

S/4HANA Cloud Public tenants ship with multiple standard ledgers (typically `0L` leading, `3L` extension, `4G` group valuation). Each ledger needs an Accounting Principle assignment — either:
- **Corp AccPr** (one global value for all company codes), OR
- **CoCode-level** entries (per-country local GAAPs).

If a ledger has NEITHER, FI document creation fails universally. Three more SAP consistency rules also apply:

| Message | Rule |
|---|---|
| `FINS_ACDOC_CUST/499` | Only ONE ledger may carry CoCode-level local APs |
| `FINS_ACDOC_CUST/558` | At least ONE ledger MUST carry CoCode-level entries |
| `FINS_ACDOC_CUST/557` | If a principle is assigned to several ledgers (counting both Corp and CoCode entries), the leading ledger 0L must also carry it as Corp AccPr |
| `FINS_ACDOC_CUST/537` | Companion of 557 — "assign this principle to the leading ledger as well" |

With 3 ledgers and 5 standard APs (`CZAP`, `DEAP`, `GBAP`, `USAP`, `USGP`), the ONLY configuration that satisfies all four rules simultaneously is:

| Ledger | Corp AccPr | CoCode entries |
|---|---|---|
| **0L** (leading) | `USGP` | none (auto-cascade) |
| **3L** | empty | `1010→DEAP, 1110→GBAP, 1710→USAP, 2010→CZAP` (the local-close ledger) |
| **4G** (group valuation) | `USGP` | none (auto-cascade) |

SAP also auto-creates a ledger group for the ledgers carrying USGP (`0L + 4G`) — you'll be prompted for a 2-char group ID. Pick any unique short code (e.g. `UG`).

## How to fix on Partner Demo Customizing tenants

Partner Demo tenants are CBC-managed. In-tenant config is locked.

1. Go to `https://cbc-pdms.cloud.sap` (or via SAP For Me → your project → "Open in CBC").
2. Configuration → search **"Assign Accounting Principles to Ledgers and Company Codes"** (SSCUI ID `103556`).
3. Open it. Set the 3-ledger pattern above.
4. Save → walk through any "Create new ledger group for USGP" prompts (pick `UG` or similar).
5. Walk through consistency dialogs — they auto-suggest the right additions.
6. Mark the activity **Status = Completed** in CBC.
7. Changes flow to the tenant the moment Save lands. The big "Deploy" button is for scope-level changes, not SSCUI tweaks.

## Standard (non-Partner-Demo) tenants

In-tenant Fiori: search **"Configure Your Solution"** or app **"Define Settings for Ledgers and Currency Types"**. Requires `SAP_BR_BPC_EXPERT` (Configuration Expert) role. Apply the same pattern.

## Important warning from SAP docs

> *"It is important that you make these settings before any postings are made in the system. As soon as postings exist, you cannot change the Corp AccPr entry anymore."*

On a fresh tenant, do this first. On a tenant that already has POs (but no FI postings yet), it still works — POs alone don't lock the Corp AccPr. Once invoices/GRs are posted, ledger config changes get progressively harder.

## Quick probe — is the tenant healthy?

Run `preflight-probe.mjs` (see `scripts/`). It posts a minimal envelope and reports:
- ✅ success or `FINS_ACDOC_CUST/201` (config gap — apply fix above)
- Other errors (different problem — check `known-error-codes.md`)

## What this is NOT

Do not chase these red herrings — they all turned out to be wrong diagnoses for `FINS_ACDOC_CUST/201`:
- "Comm user lacks FI/AP authorization" — wrong. Comm arrangement `SAP_COM_0057` grants what's needed.
- "OData V2 line items are read-only on Cloud (`creatable=false`)" — wrong. They ARE creatable post-ledger-fix (with a stricter field shape).
- "Need to assign business catalog `SAP_FIN_BC_AP_INV_PROC_PC` to the comm user" — wrong. Comm users on Cloud Public CANNOT carry business roles.
- "Need to grant `SAP_BR_AP_ACCOUNTANT` to <comm-user>" — wrong (and impossible per above).
