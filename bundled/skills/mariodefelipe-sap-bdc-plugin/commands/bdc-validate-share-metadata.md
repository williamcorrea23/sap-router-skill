---
description: Validate ORD metadata JSON before publishing a BDC data product
argument-hint: <ord_json_or_path>
---

You are running the `/bdc-validate-share-metadata` command.

The user wants to validate ORD (Open Resource Discovery) metadata before pushing it through `create_or_update_share`. The ORD payload to validate is in `$ARGUMENTS` — it may be either:
- An inline JSON object, e.g. `{"title": "...", ...}` or `{"@openResourceDiscoveryV1": {...}}`
- A path to a `.json` file on disk

If `$ARGUMENTS` is empty, ask the user to paste the ORD JSON or provide a file path, then stop.

## Steps

1. Resolve `$ARGUMENTS` into a Python dict — read from disk if it looks like a path, otherwise `json.loads()` it.
2. Call the `validate_ord_metadata` tool from the `sap-bdc` MCP server with the parsed object as `ord`.
3. Present the result in this exact shape:

```
### ORD metadata validation

Status: ✅ Valid  /  ❌ Invalid

Errors (block publish):
  - <each error>

Warnings (non-blocking):
  - <each warning>

Spec reference: https://sap.github.io/csn-interop-specification/

Source rules: SAP help.sap.com "Working with Data Products in SAP Databricks" (May 2026), pages 13–15.
```

4. If `valid=true`, suggest the next step: call `create_or_update_share` (which in v0.5.0+ will re-run this validator automatically; pass `skip_validation=true` only if you want to bypass).

5. If `valid=false`, do NOT call `create_or_update_share`. List the rules the ORD violates and propose a fix:
   - Required field missing → ask the user to supply it
   - `description` contains `shortDescription` → suggest a rewrite that doesn't quote shortDescription verbatim
   - Invalid enum (`visibility`, `releaseStatus`) → list the allowed values
   - Bad ISO 8601 date → show the expected format (`2026-12-19T15:47:04+00:00`)
   - sunsetDate < deprecationDate → call out which one to fix

Do NOT modify the user's ORD without confirmation. The goal is to surface validation failures *before* a round-trip to the SDK.
