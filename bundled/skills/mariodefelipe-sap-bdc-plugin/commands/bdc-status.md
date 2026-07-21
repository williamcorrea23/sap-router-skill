---
description: Show a status snapshot of the connected SAP BDC / Databricks environment
---

You are running the `/bdc-status` command.

Produce a concise status snapshot using the `sap-bdc` MCP server:

1. Call `list_shares` with `max_results: 20` to list the available Delta shares.
2. Call `list_recipients` to show configured Delta Sharing recipients.
3. For the recipient named in `DATABRICKS_RECIPIENT_NAME` (if set), highlight which shares are granted to it. If you cannot determine this from the list tools alone, skip it — do not fabricate.

Output format (markdown, terse):

```
### SAP BDC Environment Status

**Recipients:** <N>
- <name> (auth: <type>)

**Shares:** <N>
| Share | Owner | Created |
|---|---|---|
| … | … | … |

**Note:** <anything flagged as unusual, e.g. shares with zero objects, recipients with no grants>
```

Do not invent data. If a tool fails, report the error message and suggest checking the `.env` configuration — required vars are `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_RECIPIENT_NAME`, optionally `DATABRICKS_WAREHOUSE_ID`.
