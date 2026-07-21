# Known error codes — A_ServiceEntrySheet create

Standard OData V2 JSON error shape:
```json
{ "error": { "code": "MM_PUR_SES/119", "message": { "value": "..." }, "innererror": { "errordetails": [...] } } }
```

## Common errors and fixes

| Code | Meaning | Cause | Fix |
|---|---|---|---|
| `MM_PUR_SES/006` | "Enter a valid purchase order item. 00020 is not valid." | Referenced PO line is the LIMIT item (cat A), not the service line | Reference the cat-0 SERVICE line instead (typically item 10) |
| `MM_PUR_SES/015` | "Enter a valid performance period for purchase order item 00010 (DD/MM/YYYY - DD/MM/YYYY)" | `ServicePerformanceDate` outside PO line's allowed window | Use today (or PO creation date forward). Error message contains the allowed range. |
| `MM_PUR_SES/119` | "Purchase order X is not released." | Transient backend async — PO was just created and SES API cache hasn't refreshed | Wait 2 seconds, retry. PO IS released; this is a known timing issue. Auto-retry once before reporting failure. |
| `MM_PUR_SES/128` | "Service Entry Sheet accounting lines are not numbered consecutively" | `to_AccountAssignment` deep-insert with bad numbering | Either skip `to_AccountAssignment` entirely (auto-inherit from PO) OR use sequential numbering: "01", "02", "03" |
| `M7/053` | "Posting only possible in periods YYYY/MM and YYYY/MM in company code N" | `PostingDate` outside open MM posting periods | Backdate to an open period (typically 2-3 months back) OR open current period via Fiori "Open and Close Posting Periods" |
| `CVI_API/003` | Currency required | Missing currency on header | Header `Currency` must match PO |
| `FSBP_ECC/030` | Standard address language missing | (Not from SES; this is a customer BP creation error — wrong skill) | Use `s4hana-create-business-partner` |
| `403 HTML` | "Application Server Error" page | Comm arrangement missing `SAP_COM_0146` | Add the SES communication arrangement to the comm user in Fiori or CBC |
| `MM_PUR_SES/000` (generic) | Unspecified business error | Read `innererror.errordetails` for specifics | The full message there usually pinpoints the field |

## On the `MM_PUR_SES/119` retry pattern

This is the most common "false failure" — fires on first attempt against a brand-new PO, succeeds on second attempt seconds later. The retry algorithm:

```js
async function postSesWithRetry(envelope) {
  let result = await postSes(envelope);
  if (result.error?.code === 'MM_PUR_SES/119' || /not released/i.test(result.error?.message?.value || '')) {
    await new Promise((r) => setTimeout(r, 2000));
    result = await postSes(envelope);
  }
  return result;
}
```

Do not log the first failure as a real error if the retry succeeds. Do log if BOTH attempts fail (then it's a real issue — release strategy genuinely blocking, or PO has structural problems).

## On the `M7/053` posting period

The MM posting period is SEPARATE from FI invoice posting. Both have their own variant + period. To find what's open:

1. Try a SES post with today's date — error message lists allowed periods.
2. Or query via the dedicated posting-period app in Fiori.

Open the current period via Fiori app **"Open and Close Posting Periods"** (catalog `SAP_FIN_BC_GL_PERIOD_CLOSE_PC`, role `SAP_BR_GL_ACCOUNTANT`). The MM variant is usually the same as the company code (`1010`).

## On the comm-arrangement gap (`403 HTML`)

If all SES endpoints return HTML 403 (not OData JSON errors), the comm user doesn't have the SES scenario in its arrangements. Add `SAP_COM_0146 — Service Entry Sheet Integration` to the user's arrangement (in Fiori → Communication Arrangements → New, or in CBC).

After adding, both V2 (`API_SERVICE_ENTRY_SHEET_SRV`) and V4 (`api_serviceentrysheet/srvd_a2x/...`) endpoints become reachable. Lean Services flavor.
