---
description: Run all pre-flight checks on a Databricks share before registering it with SAP BDC
argument-hint: <share_name>
---

You are running the `/bdc-validate-share` command.

The user wants to validate the share whose name appears in `$ARGUMENTS`. If `$ARGUMENTS` is empty, ask the user for the share name and stop.

Run these tools from the `sap-bdc` MCP server in order and collect all results:

1. `validate_share_readiness` with `share_name=$ARGUMENTS, check_bdc_registration=true`
   — confirms the share exists, has tables, is granted to the recipient.

2. `get_share_details` with `share_name=$ARGUMENTS`
   — shows table list, owner, creation info.

3. `check_deletion_vectors` with `share_name=$ARGUMENTS`
   — pre-flight check for SAP Note 3706399 (Deletion Vectors break CSN publish).

Present a single consolidated verdict:

```
### Pre-flight validation for share: <name>

✅ / ❌ Existence & grants (validate_share_readiness)
✅ / ❌ Deletion Vectors (SAP Note 3706399)
ℹ️  Objects: <N> tables, latest added <timestamp>

### Verdict: READY / NOT READY

Blocking issues:
  - …

Recommended next step:
  <concrete tool call or SQL>
```

If any step fails unexpectedly, cite the error verbatim and suggest `/bdc-diagnose` with the error text as input.
