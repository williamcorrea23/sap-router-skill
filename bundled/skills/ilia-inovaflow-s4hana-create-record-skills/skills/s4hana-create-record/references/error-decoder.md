# SAP error decoder — message classes you'll see during probes

SAP errors come in the format `<message-class>/<message-number>`, e.g. `M8/375`. The class tells you which SAP module emitted the error.

## Common message classes

| Class | Module | When to expect |
|---|---|---|
| `M8`, `M8_2` | MM Invoice Verification | Supplier invoice creation |
| `MEPO`, `06` | MM Purchasing | PO creation, PIR creation |
| `MEU` | MM Unit of Measure | UoM mismatches |
| `MIGO`, `M7` | MM Inventory / Goods Movements | GR posting |
| `F5`, `F5_2` | FI Document Posting | Doc-type, reference, posting period |
| `FICORE` | FI Core | Tax procedure, currency conversion |
| `FINS_ACDOC_CUST` | FI Document Customizing | Ledger / accounting principle config |
| `IVE_E_INVOICE` | A2X Inbound Invoice Service | SOAP envelope validation |
| `API_PRD_MSG` | Product API | Product master operations |
| `CI_DRAFTBP_MESSAGE` | Business Partner Draft | BP create/edit/delete |
| `BP`, `BPRR` | Business Partner | BP role and relationship |
| `/IWBEP/CM_MGW_RT` | OData V2 runtime | Generic OData errors (system query options, etc.) |
| `CX_NO_AUTHORIZATION` | Authorization framework | Comm user lacks scope |

## Reading error responses

**OData V2 JSON:**
```json
{
  "error": {
    "code": "M8/375",
    "message": { "value": "Fill in mandatory field 'X' (table parameter 'Y', row 000001)" },
    "innererror": {
      "errordetails": [...]   // sometimes contains additional related messages
    }
  }
}
```

**SOAP XML:**
```xml
<Log>
  <BusinessDocumentProcessingResultCode>5</BusinessDocumentProcessingResultCode>
  <Item>
    <TypeID>375(M8)</TypeID>      <!-- format: <number>(<class>) -->
    <SeverityCode>3</SeverityCode> <!-- 3 = error, 2 = warning, 1 = info -->
    <Note>Fill in mandatory field 'X'</Note>
  </Item>
</Log>
```

## Error categories — how to react

### Authorization errors (DON'T retry — escalate)
- `CX_NO_AUTHORIZATION` (HTTP 403)
- "User X has no authorization for Y"

→ Comm user lacks scope. Surface to user. Solution requires admin to extend the comm arrangement.

### Configuration errors (DON'T bulk — fix tenant first)
- `FINS_ACDOC_CUST/201` "Configuration settings need to be corrected"
- `FICORE/704` "Tax code X in procedure Y is invalid"
- `M8/535` "Allowed posting periods: ..."

→ Tenant config gap. STOP, surface to user, recommend fix path.

### Field validation (DO retry with fix)
- "Fill in mandatory field 'X'" → add field
- "Field 'X' value 'Y' not allowed" → try alternative values (sweep if value space is small)
- "Value 'X' too long for field 'Y' (max N chars)" → truncate or shorten

### Master-data errors (DON'T invent — verify first)
- "Supplier X does not exist"
- "Material X not maintained for plant Y"
- "Customer X is blocked"

→ GET the master record first to verify it exists. If missing, surface to user.

### System / lock errors (DO retry once)
- "Lock entry exists" — wait briefly, retry once
- "System busy, try later" — wait, retry once
- After 1 retry, halt and surface

### Unexpected (CAPTURE and report)
Anything not in the above categories — capture full response, surface to user, add to `references/known-entity-quirks.md` for future runs.

## Looking up unknown codes
1. SAP Help Portal: https://help.sap.com/docs/SAP_S4HANA_CLOUD search for `<class> <number>`
2. SAP Note search at https://launchpad.support.sap.com/ (requires SAP S-User)
3. SAP community forums often have the most practical workarounds

## Sweep technique (when valid values are unknown)
For fields where SAP rejects with "Value X not allowed" but doesn't tell you what's valid:
1. Build a small sweep script that POSTs the same payload with varying values for the disputed field
2. Try the obvious candidates: digit codes (1, 2, 3...), 2-digit (01, 02...), 3-digit (001...), single-char letters (A, B, M, S, H...), 3-letter mnemonics
3. The error message changes when SAP advances past the field — that's the sign you found a valid value
4. Once one value is known, document it in `known-entity-quirks.md`

This was used to discover `ProcessingTypeCode=M` for supplier invoice items — full sweep documented in the `s4hana-create-invoice` skill's known-error-codes.md.
