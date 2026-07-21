# s4hana-create-record-skills

> **Agent skills for creating AND updating records in SAP S/4HANA Cloud Public and on-prem private editions** — products (materials), supplier invoices, purchase orders, business partners (supplier/customer/combined), service entry sheets, purchasing info records, goods receipts, PO confirmations, communication management / integration setup (comm users, systems, OAuth2 arrangements), plus generic create + update fallbacks.

Verified production-ready against SAP S/4HANA Cloud Public Edition and on-prem private edition. Works with Claude Code, Cursor, Codex, OpenCode, and any agent that supports the [open agent skills format](https://skills.sh).

## Install

```bash
npx skills add ilia-inovaflow/s4hana-create-record-skills --skill '*'
```

The CLI prompts for scope (project / global) and agent. Restart your agent session afterwards.

Update later: `npx skills update` (updates all installed skills).

## Setup — SAP credentials

The first time you invoke any skill, it **creates a `.env` template in your current directory** (and adds it to `.gitignore`), then waits for you to fill it in. Edit the file with values matching your tenant + auth mode, then tell the agent you're ready.

### What goes in `.env`

| Variable | Meaning |
|---|---|
| `SAP_HOST` | Tenant URL — e.g. `https://<your-tenant>-api.s4hana.cloud.sap` (Cloud Public) or `https://s4hana.yourdomain.com` (on-prem) |
| `SAP_CLIENT` | SAP client number — typically `100` for production tenants, `200` for sandbox |
| `SAP_AUTH_MODE` | Pick one: `basic`, `cc`, or `oauth` — see table below |
| Mode-specific creds | See the column for your chosen mode |

### Three auth modes

| Mode | When to use | What you fill in |
|---|---|---|
| **`basic`** | Cloud Public Edition with a Communication User (the common case for `my<id>.s4hana.cloud.sap` tenants) | `SAP_USERNAME` + `SAP_PASSWORD` |
| **`cc`** | On-prem / Private Edition with OAuth 2.0 client credentials (technical user) | `SAP_TOKEN_URL` + `SAP_CLIENT_ID` + `SAP_CLIENT_SECRET` |
| **`oauth`** | Cloud Public with a named-user bearer token (Auth Code + PKCE flow) — less common | Nothing long-lived in `.env`; supply token at runtime |

For Cloud Public tenants, you also need Communication Arrangements added in Fiori for each scenario you'll use: `SAP_COM_0009` (products), `SAP_COM_0057` (invoices), `SAP_COM_0053` (POs), `SAP_COM_0008` (BPs), `SAP_COM_0146` (SES), `SAP_COM_0108` (GR), `SAP_COM_0827` (PO confirmations), `SAP_COM_0102` (PIRs).

**Never commit `.env`.** The skills add it to `.gitignore` automatically.

## What's inside

| Skill | Endpoint |
|---|---|
| `s4hana-create-product` | OData V4 `api_product/srvd_a2x/sap/product/0002` deep-insert |
| `s4hana-create-invoice` | SOAP A2X `SupplierInvoiceERPCreateRequest_sync` |
| `s4hana-create-po` | OData V2 `A_PurchaseOrder` deep-insert (goods + service POs) |
| `s4hana-create-business-partner` | OData V2 `A_BusinessPartner` deep-insert (supplier / customer / combined) |
| `s4hana-create-service-entry-sheet` | OData V2 `A_ServiceEntrySheet` (Lean Services) |
| `s4hana-create-pir` | OData V2 `A_PurchasingInfoRecord` |
| `s4hana-create-goods-receipt` | OData V2 `A_MaterialDocumentHeader` |
| `s4hana-create-po-confirmation` | SOAP A2X `SupplierConfirmationRequest_In` (WS-Addressing) |
| `s4hana-update-record` | OData V2 PATCH on any entity, with GET-PATCH-GET verify |
| `s4hana-comm-management` | Communication Management (`SAP_COM_0A48`) OData V4 A2X — comm users, systems (OAuth2 + redirect URI) & arrangements; the admin layer that wires inbound API access. **Cloud Public only.** |
| `s4hana-create-record` | Generic create fallback — researches `$metadata`, probes minimal payloads |

Each skill handles CSRF tokens, master-data lookup, idempotent bulk batches, transient retry, and known SAP quirks per entity.

## Manage skills

```bash
npx skills list # what's installed
npx skills update                              # pull latest for all
npx skills remove                              # uninstall (interactive)
```

## Compatibility

- **SAP S/4HANA Cloud Public Edition**
- **SAP S/4HANA Cloud Private Edition / on-prem**
- **SAP S/4HANA Cloud Partner Demo Customizing** tenants (CBC-managed config)
- **Any agent** that supports the [open agent skills format](https://skills.sh) — Claude Code, Cursor, Codex, OpenCode, and 50+ more

## License & contributing

MIT licensed. Issues + PRs welcome — especially new verified entity skills, additional error codes, and tenant-specific quirks. Open an issue if you hit an SAP error the decoder doesn't cover; full response payload helps the next person.
