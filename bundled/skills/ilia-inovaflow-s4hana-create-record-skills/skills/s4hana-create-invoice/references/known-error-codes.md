# Known error codes — Supplier Invoice ERP Create

Error format in SOAP response: `<TypeID>{message-number}({message-class})</TypeID>` with `<Note>{message text}</Note>`. Severity 3 = error, 2 = warning.

| Code | Meaning | Cause | Fix |
|---|---|---|---|
| `FINS_ACDOC_CUST/201` | "Configuration settings need to be corrected." | Tenant FI customizing gap — ledger missing AP assignment | See `ledger-config-preflight.md`. Apply via CBC. |
| `FINS_ACDOC_CUST/499` | "Only one ledger can have local acctg principles on CoCode level assigned." | Trying to set CoCode-level APs on multiple ledgers | Set CoCode-level on only ONE ledger; others use Corp AccPr |
| `FINS_ACDOC_CUST/537` | "Assign this accounting principle to the leading ledger as well." | A principle is on multiple ledgers, but not on 0L | Either remove from one, or also set 0L Corp = same |
| `FINS_ACDOC_CUST/557` | "USGP that is assigned to several ledgers must be assigned to 0L as Corp AccPr." | Same as 537, specific message | Set 0L Corp AccPr to the principle in question |
| `FINS_ACDOC_CUST/558` | "You tried to save your ledger settings without assigning APs on CoCode level." | No ledger has CoCode-level entries | Pick ONE ledger (typically 3L) to be the local-close ledger with per-CC APs |
| `IVE_E_INVOICE/052` | "ProcessingTypeCode X not allowed." | Item.ProcessingTypeCode is an unsupported value | Use `M` (Material). `S` for G/L items (needs different shape). |
| `IVE_E_INVOICE/026` | "Data loss while processing field ProcessingTypeCode of node SupplierInvoice." | Header ProcessingTypeCode value too long or invalid | Omit it (optional field) |
| `M8/375` | "Fill in mandatory field 'X' (table parameter 'Y', row 000001)." | Required field missing | Read the field name from message, add to envelope. Common ones: `TaxationCharacteristicsCode`, `Product-InternalID`, `ReferenceDocument-FiscalYear-Item` (OData V2 only) |
| `M8/535` | "Allowed posting periods: MM YYYY / MM YYYY / MM YYYY for company code X and date DD/MM/YYYY." | Posting date outside open periods | Either backdate to an open period or open the current period via Fiori "Open and Close Posting Periods" |
| `M8/607` | "System error: Error in routine MRM_FRSEG_CHECK FRSEG-LFBNR." | Internal SAP error, typically downstream of M8/375 | Fix the M8/375 first |
| `M8_2/057` | "Supplier invoice status X is not allowed." | `CompletenessAndValidationStatusCode` value rejected | Use `5` (Post) or `A` (Parked). Codes are alphanumeric, not 1/2/3. |
| `M8_2/806` | "References only supported for statuses: A(Parked) and D(Entered and Held)." | `HeaderReferences` set with status=5 | Omit `HeaderReferences` for posted invoices |
| `M8_2/832` | "Time-dependent taxes active: Fill Tax Determ. Date in invoice header." | `TaxDeterminationDate` missing | Add header `TaxCalculation/TaxDeterminationDate` |
| `FICORE/704` | "Tax code X in procedure Y is invalid." | Tax code not defined in procedure | Use `V0` for Cloud Public tax procedure `0TXD` (only valid 0%-input code) |
| `F5/480` | "For document type RE, an entry is required in field Reference." | `BillFromID` missing | Set header `BillFromID` to supplier's invoice ref (NOT `SupplierInvoiceReference` — that's for cancellation refs) |
| `06/321` | "Supplier X does not exist in purchasing organization Y." | Supplier missing PurchOrg assignment | Extend supplier master data via `A_SupplierPurchasingOrg` |
| `ME/083` | "Field StandardPurchaseOrderQuantity required." | Only fires on PIR creation, not invoice | (Out of scope for invoice skill) |
| `406 / Wrong unit of measure` | "No measurement unit is assigned to ISO code X." | `unitCode` attribute on `<Quantity>` uses SAP-internal code | Use ISO code (`PCE` for piece, `KGM` for kilogram, etc.) |

## When you see an error not in this table

1. Quote the full `<TypeID>` and `<Note>` to the user.
2. Search SAP Help Portal for `<message-class>/<message-number>` (e.g., `M8/375`).
3. Add the new code + fix to this table once resolved.

## On `FINS_ACDOC_CUST/201` specifically

This error is **the most common false-flag in SAP API debugging**. Multiple SAP forum threads attribute it to authorization issues — those threads are wrong for the supplier-invoice case. Don't chase comm-user role assignments. Always check ledger AP config first via `ledger-config-preflight.md`.

## Cross-API consistency

The same `FINS_ACDOC_CUST/201` will also block OData V2 `A_SupplierInvoice` POST and Fiori "Create Supplier Invoice" app. If you can reproduce in Fiori (with a named user who has `SAP_BR_AP_ACCOUNTANT`), it's definitively a config issue — not API auth.
