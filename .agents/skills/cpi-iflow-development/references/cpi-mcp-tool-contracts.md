# Canonical CPI MCP tool contracts

Server id: `sap-cpi-mcp`. Transport: local stdio. API/CLI first; browser UI fallback
only when background access is blocked. Tool annotations are UX hints, never access
control.

## Environment

Required for tenant API calls:

- `CPI_BASE_URL`
- `CPI_OAUTH_TOKEN_URL`
- `CPI_OAUTH_CLIENT_ID`
- `CPI_OAUTH_CLIENT_SECRET`

Optional local tooling:

- `CPI_TOOL_WORKSPACE` — root allowed for all tool file paths; defaults to router root.
- `CPILINT_CMD` — separately installed cpilint command.
- `CPI_SYNC_CMD` — separately installed CPI/Git synchronization adapter.
- `CPI_STEAMPIPE_CMD` — Steampipe executable with CPI plugin configured.
- `CPI_IFLOW_PLOTTER_CMD` — separately installed iFlow plotter.
- `CPI_MAPPING_TEST_CMD` — separately installed mapping-test adapter.

Commands are split into executable and arguments and run with `shell=false`, bounded
timeout, workspace confinement, and truncated output. Missing commands return
`UNAVAILABLE`; they are never installed automatically.

## Read-only tools

| Tool | Purpose |
|---|---|
| `cpi_test_connection` | Verify OAuth and Integration Content API without returning secrets |
| `cpi_packages` | Package list/exact read with `query`, `limit`, `offset` |
| `cpi_artifacts` | Integration flows, value mappings, message mappings, or script collections |
| `cpi_artifact_get` | One design-time artifact by id/version/type |
| `cpi_runtime_artifacts` | Runtime list with status/query filters |
| `cpi_logs` | MPL list with status, flow, log-level, time and pagination filters |
| `cpi_message_details` | One MPL plus optional adapter attributes, custom headers, and trace |
| `cpi_quality_check` | Built-in ZIP validation plus optional cpilint |
| `cpi_external_tools_status` | Configuration/availability of all optional adapters |
| `cpi_steampipe_query` | One SELECT statement; semicolons and mutating keywords rejected |
| `cpi_mapping_test` | Run configured mapping-test adapter on workspace files |

Collection tools default to 50 items and reject limits outside 1-200. Their
`structuredContent` uses:

```json
{
  "items": [],
  "count": 0,
  "total_count": null,
  "offset": 0,
  "limit": 50,
  "has_more": false,
  "next_offset": null,
  "source": "cpi:EntitySet",
  "truncated": false
}
```

Responses above 25,000 characters are reduced by whole items and return guidance to
continue with `next_offset` or narrower filters.

## Approved mutation tools

| Plan tool | Commit tool | Effect |
|---|---|---|
| `cpi_deploy_plan` | `cpi_deploy_commit` | Tenant upload/deploy, mutating |
| `cpi_undeploy_plan` | `cpi_undeploy_commit` | Runtime undeploy, destructive |
| `cpi_generate_iflow_plan` | `cpi_generate_iflow_commit` | Local ZIP write; destructive when overwriting |
| `cpi_plot_iflow_plan` | `cpi_plot_iflow_commit` | Local diagram write; destructive when overwriting |
| `cpi_sync_plan` | `cpi_sync_commit` | External CPI/Git synchronization |

Workflow:

1. Call only the plan tool. Inspect target, effect, arguments, preconditions, expiry,
   and hashes.
2. Obtain independent human approval through `approval_broker.py` or the local portal.
   For destructive actions, the confirmation text must equal the plan target.
3. Call commit with `action_id`, `plan_hash`, `argument_hash`, and
   `precondition_hash` unchanged.
4. Treat the approval as one-time. Re-plan after rejection, expiration, consumption,
   changed arguments, or changed preconditions.

Action-shaped `structuredContent`:

```json
{
  "action_id": "uuid",
  "status": "PENDING",
  "expires_at": "ISO-8601",
  "plan_hash": "sha256",
  "argument_hash": "sha256",
  "precondition_hash": "sha256",
  "summary": "operation summary",
  "target": "immutable target",
  "effect": "mutating"
}
```

Operational failures are MCP tool results with `isError: true` and actionable text.
JSON-RPC errors are reserved for malformed/unsupported protocol requests.
