# Known traps — fields that lie about success

These are the cases where PATCH returns HTTP 204 No Content (the OData "success" code) but the field's value doesn't actually change. Without GET-after-PATCH verification, you'd never know.

**This is why the skill MANDATES a verify step.**

## PIR `NetPriceAmount` on `A_PurgInfoRecdOrgPlantData`

```http
PATCH /sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV/A_PurgInfoRecdOrgPlantData(PurchasingInfoRecord='5300000130',PurchasingInfoRecordCategory='0',PurchasingOrganization='1010',Plant='1010')
{"NetPriceAmount": "299.99"}

Response: 204 No Content

GET .../A_PurgInfoRecdOrgPlantData(...)?$select=NetPriceAmount
→ "NetPriceAmount": "50.00"   // unchanged!
```

The PIR price is stored in **`to_PurInfoRecdPrcgCndnValidity`** (Pricing Condition Validity records), NOT on the org-plant entity. The `NetPriceAmount` field on org-plant is a derived/display value — SAP accepts PATCH gracefully but doesn't actually write anything.

**To actually update PIR price**: PATCH the related condition record:

```http
GET /sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV/A_PurgInfoRecdOrgPlantData(...)/to_PurInfoRecdPrcgCndnValidity?$format=json
→ list of condition records, each with its own keys

PATCH /sap/opu/odata/sap/API_INFORECORD_PROCESS_SRV/A_PurInfoRecdPrcgCndnValidity(<keys>)
{"ConditionRateValue": "299.99"}
```

(Untested end-to-end as of skill v1.5.0 — flag to user when they hit this case.)

## Other suspected silent-no-op fields

Worth verifying with GET-after-PATCH if you encounter:

| Field | Entity | Notes |
|---|---|---|
| `CompanyCodeCurrency`-derived amounts | Multiple | Currency-converted amounts are usually read-only |
| `GrossAmount`-style fields when item amounts differ | Invoice items | Computed from items, header value is display |
| `MaterialDocumentYear` | GR | Auto-derived from posting date |
| Status fields (`Status`, `ApprovalStatus`, `SESWorkflowStatus`) | SES, BP, others | Usually system-controlled, not directly settable |

## How the skill protects you

Phase 4 (Verify) does:
1. GET the same key fields again, including the ones we tried to update
2. Diff before vs after
3. If a field comes back unchanged when we asked to change it → report it as a **silent no-op**, NOT as success
4. Suggest possible alternatives (e.g. "this field looks read-only — the actual mutable record may be in a related nav property")

## The reverse trap

Just as important — some PATCHes look like FAILURE but actually succeed:
- HTTP 400 sometimes comes with `ERROR: Can delivery date be met?` warnings that are **non-blocking** — the actual change is rejected, but accompanying warnings can confuse parsing
- HTTP 200 with response body containing `errordetails` array — read the array carefully, some entries are warnings (severity 2) not errors (severity 3)

Always check the **post-PATCH GET** as ground truth, not just the response status.
