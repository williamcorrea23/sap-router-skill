# Governance

SAP transport releases affect real production systems. The governance layer in this server
is a financial control, not a convenience feature.

---

## Enforced Rules

| Rule | Enforced by | Consequence |
|------|-------------|-------------|
| DRY_RUN blocks all writes | `config/policy.ts` | PolicyViolation thrown before any SAP call |
| Description ≥ 10 chars | `config/policy.ts` | Blocked at create time |
| Cannot release empty transport | `config/policy.ts` | Object count checked before release API call |
| Cannot delete released transport | `config/policy.ts` | Status read before delete API call |
| Release is irreversible | `CLAUDE.md` | Claude must show objects + get user confirmation |
| Audit log on every write | `config/policy.ts` | JSON entry emitted to stderr |

---

## Audit Log Format

Every write emits a JSON record to stderr:

```json
{
  "timestamp": "2026-05-26T14:30:00.000Z",
  "audit": true,
  "toolName": "transport_release_request",
  "systemId": "DEV",
  "transportNumber": "DEVK900123",
  "objectCount": 5,
  "targetSystem": "QA1",
  "result": "success",
  "detail": "Transport DEVK900123 released successfully..."
}
```

Replace `console.error` in `config/policy.ts` `auditLog()` with your real sink:
Splunk, CloudWatch, SAP audit trail API, etc.

---

## Adding New Policy Rules

Add rules to `enforceWritePolicy()` in `config/policy.ts`:

```ts
// Example: restrict releases to business hours (UTC)
const hour = new Date().getUTCHours();
if (ctx.toolName === "transport_release_request" && (hour < 6 || hour > 18)) {
  throw new PolicyViolation("BUSINESS_HOURS", "Releases only allowed 06:00–18:00 UTC");
}
```

---

## SAP Authorization Objects Required

The SAP user configured in `.env` must have:

| Authorization Object | Field | Value |
|---------------------|-------|-------|
| S_ADT_RES | ADT_TOOL | CTS |
| S_CTS_ADMI | CTS_ADMFCT | RELE (for release) |
| S_CTS_ADMI | CTS_ADMFCT | DELE (for delete) |
| S_TRANSPRT | ACTVT | 01 (create), 06 (delete) |
| S_TRANSPRT | TTYPE | K, W (workbench, customizing) |

---

## Incident Response

If a write causes an unintended change:
1. Set `DRY_RUN=true` immediately — blocks further writes
2. Use `transport_get_request` to assess current state
3. For a bad release: contact SAP Basis team — they can re-import the previous state or delete the request from the import queue
4. SAP does not auto-rollback transport releases
