---
description: Diagnose an SAP BDC or Databricks error message against the indexed SAP Notes
argument-hint: <paste error message>
---

You are running the `/bdc-diagnose` command.

The user is pasting an error message in `$ARGUMENTS`. If it is empty, ask them to paste the full error text (including error code, request ID, and timestamp if available) and stop.

Steps:

1. Call `diagnose_share_error` from the `sap-bdc` MCP server with `error_message=$ARGUMENTS`.

2. If the tool returns a matching SAP Note, present it in this shape:

   ```
   ### Matches SAP Note <NUMBER>: <title>

   **Cause:** <1–2 sentences>

   **Resolution:**
     1. …
     2. …

   **Related tool you can run right now:**
     <tool name and suggested args, if applicable>
   ```

3. If no note matches, activate the `bdc-troubleshooter` skill for a broader search across the 18 indexed notes. If still no match, advise the user to:
   - Check SAP Note 3653192 (main Databricks/BDC troubleshooting guide)
   - Prepare a support case per SAP Note 3568017, including request ID, tenant ID, and timestamp

Never invent SAP Note numbers or make up resolution steps. If the diagnosis is uncertain, say so and explain what further information would disambiguate.
