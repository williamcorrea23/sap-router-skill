---
name: bdc-troubleshooter
description: Use ONLY for SAP-Note symptom→fix lookup — i.e. when the user pastes a specific BDC/Databricks error message, cites an SAP Note number in the 34xxxxx–37xxxxx range, or describes a concrete failure (provisioning stuck, CSN publish errorCode 500, OIDC code exchange failure, duplicate hostname, orphan data product, SCIM "only one replace" error, Azure storage 403/AuthorizationFailure, metastore owner share error, negative dates from SAP, Business Name missing in Unity Catalog, HANA Cloud missing from Customer Landscape, CIS integration not configured). For "how do I..." / setup / configuration / conceptual questions, DEFER to the right skill instead — bdc-onboarding, bdc-core-admin, bdc-governance-catalog, bdc-connect-sharing, bdc-intelligent-apps, or sap-databricks. Trigger phrases include "BDC error", "errorCode 500", "AuthorizationFailure", "oidc_code_exchange_failure", "only one replace operation", "tenantHostName invalid", "orphan data product", "Business Name missing", "metastore owner", "HAR file Databricks".
---

# SAP BDC Troubleshooter (symptom-lookup only)

Narrow skill: given an error message or a described failure, return the matching SAP Note, the one-line cause, and concrete steps — nothing else. Curated against 22 SAP Notes (18 from the 2026-04-13 batch + 4 new from the 2026-04-15 batch) plus 4 procedural rules from the 2026-05-02 SAP help.sap.com batch.

## Scope rule

**In scope (use this skill):**
- User pastes an error message or stack trace
- User cites an SAP Note number
- User describes a failure whose symptom matches the tables below

**Out of scope (route elsewhere):**
- "How do I set up BDC?" → `bdc-onboarding`
- "How do I manage users / configure SCIM / monitor capacity?" → `bdc-core-admin`
- "How do I publish / enrich a catalog asset?" → `bdc-governance-catalog`
- "How does BDC Connect / Delta Sharing work?" → `bdc-connect-sharing`
- "How do I install an intelligent app?" → `bdc-intelligent-apps`
- "How do I work with SAP Databricks?" → `sap-databricks`

## Workflow

1. Identify the symptom in the tables below.
2. If an MCP tool matches (the `sap-bdc` server exposes `diagnose_share_error`, `validate_tenant_hostname`, `check_deletion_vectors`, `cleanup_orphaned_data_product`), call it first. Don't paraphrase — call the tool and cite its output.
3. Cite the SAP Note by number. Never invent note numbers.
4. Give the resolution as numbered steps, not prose.
5. Fallback: unknown symptoms → SAP Note 3653192 (main troubleshooting guide) + SAP Note 3568017 (how to file a support case).

## Symptom → SAP Note index

### Provisioning

| Symptom | SAP Note | Fix |
|---|---|---|
| BDC Core provisioning hangs indefinitely | 3652165 | `tenantHostName` must match `[a-z0-9-]+` — no uppercase, no leading/trailing hyphens. Delete failed instance, retry lowercase. Pre-check with `validate_tenant_hostname` MCP tool. |
| "The host name XXX is already being used" | 3705747 | Hostname taken in that region. Pick different. |
| SAC tenant stuck at "Processing" | 3605796 | SAC licenses not assigned. Go back and assign them. |
| Can't find BDC provisioning with BTPEA/CPEA | 3599696 | BDC does NOT use CPEA/BTPEA credits. Buy BDC offering separately; existing tenants can't migrate. |
| How do I provision SAP Datasphere? | 3459708 | BDC model: enable BDC Core first, then provision DS tenant. BTPEA/CPEA: separate flow. |

### SAP Databricks login & identity

| Symptom | SAP Note | Fix |
|---|---|---|
| "We've encountered an error logging you in" + `oidc_code_exchange_failure` | 3678584 | Client secret expired (6-month rotation). Exclude IAS tenant from "Integration with SAP Databricks" Formation, re-include, retry login. |
| "SAP Cloud Identity Service Integration Not Configured" | 3706392 | Wait up to 30 min after provisioning. If persistent, open case with component `BDC-DBX-CON`. |
| Second Databricks tenant with same CIS fails | 3694878 | One CIS can only join one formation. Use different CIS or new formation. |
| SCIM: "Only one replace operation is allowed" | 3738570 | Databricks SCIM limitation vs SAP IPS. Apply IPS transformation workaround in the note or provision users one at a time. |

### Delta Sharing / BDC Catalog / CSN

| Symptom | SAP Note | Fix |
|---|---|---|
| `create_or_update_share_csn` → "unable to serve your request" / errorCode 500 | 3706399, 3717031 | Run `check_deletion_vectors` MCP tool first. Verify grants, table existence, and that metastore admin hasn't changed. |
| **NEW 2026-04-15** Share CSN creation fails, metastore owner mismatch | **3665741** | Update metastore owner to proper UUID: `databricks metastores update <metastore-id> --owner <service-principal-id>`. |
| Orphan Data Product in BDC Catalog after Databricks share deleted | 3720724 | Recreate empty share with same name, grant to recipient, unpublish+delete via SDK. Or call `cleanup_orphaned_data_product` MCP tool. |
| "Business Name" missing in Unity Catalog for shared Data Products | 3725086 (v3, 09.04.2026) | Fixed by Databricks — ensure recent cluster runtime, re-mount if needed. |
| NULL SAP dates arrive as `-0001-11-30` or other negative dates in Databricks | 3736857 | Coerce SAP `00000000` → true SQL NULL in the Transformation Flow before date cast. |

### BDC Connect on Azure (firewall / networking) — NEW 2026-04-15

| Symptom | SAP Note | Fix |
|---|---|---|
| `AuthorizationFailure` 403 when consuming from firewall-protected Azure Databricks | **3718680** | Add SAP Datasphere VNet subnet ID or public IP to Azure Storage firewall allowlist. Region-specific subnets in note 3726123. |
| `AuthorizationFailure` 403 on parquet read from Azure Storage behind firewall | **3726123** | Allowlist the SAP Datasphere HANA Database VNet subnet (or public IP) in Azure Storage firewall. Region-specific subnet table is in the note itself. |

### Databricks Data Products / ORD validation — NEW 2026-05-02

| Symptom | Source | Fix |
|---|---|---|
| Share dialog rejects the asset / asset missing from "Add Table (File)" picker in SAP Databricks | help.sap.com "Working with Data Products in SAP Databricks" (May 2026), p.9 | Asset is a **Materialized View** — unsupported for Delta Sharing in SAP Databricks. Re-expose as a regular view, or persist as a Delta table. Run `list_unsupported_share_assets` MCP tool to scan a catalog/schema. |
| Confusion: SAP Note 3706399 says "disable deletion vectors" but the new derived-DP guide says "enable" them | help.sap.com derived-DP guide (May 2026) p.7–9 vs SAP Note 3706399 | These are **different sides of the share**. 3706399 is about *consuming* an inbound share where deletion vectors break the consume side. The new derived-DP guide is about *producing* tables in your own SAP Databricks workspace, where `delta.enableDeletionVectors=true` and `delta.enableChangeDataFeed=true` are recommended. |
| `create_or_update_share` fails with vague SDK error | ORD validation rule, May 2026 doc p.14 | ORD `description` must NOT contain the `shortDescription` value. Run `validate_ord_metadata` MCP tool (or let `create_or_update_share` v0.5.0+ auto-validate) to catch this before the SDK round-trip. |
| Metastore privilege errors when sharing Delta Shares | help.sap.com derived-DP guide p.3 | Principal needs all 6 metastore privileges: CREATE CATALOG, CREATE SHARE, SET SHARE PERMISSION, USE PROVIDER, USE RECIPIENT, USE SHARE. Run `validate_databricks_privileges` MCP tool to pre-flight, then grant via *Catalog → Manage → Metastore → Permissions → Grant*. |

### HANA Cloud & admin

| Symptom | SAP Note | Fix |
|---|---|---|
| HANA Cloud instance not listed in BDC Customer Landscape | 3731036 | Ensure HANA Cloud Central is running in the subaccount — it's the Data Product gateway. |
| How do I create a support user for BDC? | 3568907 | BDC Cockpit → Administration → System Configuration → Allow SAP support user creation. Also KBAs 3200458 (SAC) and 2891554 (DS). |
| How do I file a good BDC support case? | 3568017 | Check System Availability, distinguish technical vs consulting, include request ID + timestamps. |
| **NEW 2026-04-15** Need network trace for a Databricks UI issue | **3600390** | Generate a browser HAR file per SAP Note 2969368 procedure; attach to the case. |

## Response shape

When the user pastes an error:

```
Matches SAP Note XXXXXXX: <title>

Cause: <1–2 sentences>

Resolution:
  1. …
  2. …
  3. …

Related MCP tool: <tool_name>(args)   ← if applicable
```

Tight. Do not paraphrase note content at length — cite the number and give the steps.

## Reference files

22 SAP Notes in `references/`. Load a specific PDF only when the summary above is insufficient or the user asks for full text.

**Core 18 (2026-04-13 batch):**
- 3459708, 3568017, 3568907, 3599696, 3605796, 3652165, 3653192, 3678584, 3694878, 3705747, 3706392, 3706399, 3717031, 3720724, 3725086, 3731036, 3736857, 3738570

**New 4 (2026-04-15 batch):**
- `references/3600390_E_20260415.pdf` — HAR file generation for Databricks UI issues
- `references/3665741_E_20260415.pdf` — Updating metastore owner to resolve share CSN creation errors
- `references/3718680_E_20260415.pdf` — AuthorizationFailure sharing from Enterprise Databricks on Azure
- `references/3726123_E_20260415.pdf` — BDC Connect for Databricks: firewall-protected Azure Storage

**Refreshed 3** (newer versions from 2026-04-15 batch — prefer these over 04-13 copies):
- 3653192_E_20260415 (main troubleshooting guide)
- 3678584_E_20260415 (OIDC code exchange failure)
- 3725086_E_20260415 (Business Name missing in UC — now v3)
