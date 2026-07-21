# Backdating algorithm — seeded distribution

When the user asks to backdate POs (or invoices) across a date range, distribute them deterministically using FNV-1a hash on a stable seed (e.g., the source key like `PO-source-id` or `index`).

## Why deterministic
- Same seed → same dates on rerun → idempotency holds
- Spreads dates evenly across the range without RNG-induced clustering
- No need to persist a date map — the seed reproduces it

## Implementation

```js
function fnv1a(s) {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  return h;
}

function pickDate(seed, year, month) {
  // 1-based day of month. Replace with date range if multi-month needed.
  const daysInMonth = new Date(year, month, 0).getDate();
  const dayOffset = fnv1a(seed) % daysInMonth;
  return new Date(Date.UTC(year, month - 1, 1 + dayOffset));
}

const date = pickDate(`PO-${sourceId}`, 2025, 8); // August 2025
const dateISO = date.toISOString().slice(0, 10);
```

For multi-month spread:
```js
function pickDateInRange(seed, startISO, endISO) {
  const start = new Date(startISO).getTime();
  const end = new Date(endISO).getTime();
  const span = Math.floor((end - start) / 86400000); // days
  const dayOffset = fnv1a(seed) % (span + 1);
  return new Date(start + dayOffset * 86400000);
}
```

## Apply to PO field
```js
payload.PurchaseOrderDate = `/Date(${date.getTime()})/`;
```

OData V2 expects the `/Date(<ms-since-epoch>)/` format — not ISO 8601.

## Important caveat
- `PurchaseOrderDate` IS settable → backdating works for the document date.
- `CreationDate`, `LastChangeDateTime`, `CreatedByUser` are system-stamped at POST time → cannot be backdated. The audit trail will always show today's date.

If the demo target requires audit-trail backdating too, that's a tenant data-import via SAP Migration Cockpit — not the OData API.

## Posting period must be open
The chosen date MUST fall in an open posting period. Check via `M8/535` error message format if it fails:
```
Allowed posting periods: 08 2025 / 07 2025 / 12 2024 for company code 1010
```

Default open windows on Cloud Public Edition tenants are typically 1-3 months. Backdate into one of them, or open the current period via Fiori "Open and Close Posting Periods".
