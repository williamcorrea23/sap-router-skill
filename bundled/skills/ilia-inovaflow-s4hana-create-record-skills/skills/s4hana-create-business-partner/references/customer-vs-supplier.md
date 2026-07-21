# Customer vs Supplier vs Combined BP — required fields side-by-side

All three start from the same base entity (A_BusinessPartner with category 2 = organization), then add different nav properties for the role-specific sub-entities.

## Base (every BP)

```json
{
  "BusinessPartnerCategory": "2",
  "BusinessPartnerGrouping": "BP02",
  "OrganizationBPName1": "<name>",
  "to_BusinessPartnerAddress": { "results": [{ ... }] },
  "to_BusinessPartnerRole": { "results": [{ ... }] }
}
```

| Field | Supplier | Customer | Combined |
|---|---|---|---|
| `BusinessPartnerCategory` | `2` | `2` | `2` |
| `BusinessPartnerGrouping` | `BP02` (internal) | `BP02` | `BP02` |
| `BusinessPartner` | omit (auto-assigned) | omit | omit |
| `OrganizationBPName1` | required | required | required |

## Address sub-entity (`to_BusinessPartnerAddress`)

| Field | Supplier | Customer | Combined |
|---|---|---|---|
| `Country` | required | required | required |
| `Language` | optional | **required** | **required** |
| `CityName`, `PostalCode`, `StreetName` | recommended | recommended | recommended |

If you omit `Language` on a BP that has a customer role, you'll get:
```
FSBP_ECC/030: Standard address doesn't have a language, needed for customer
```
Set `Language: "EN"` (or `"DE"`/etc.) to fix.

## Roles (`to_BusinessPartnerRole`)

| Want | Roles to include |
|---|---|
| Supplier | `FLVN00` + `FLVN01` |
| Customer | `FLCU00` + `FLCU01` |
| Combined | all four: `FLVN00`, `FLVN01`, `FLCU00`, `FLCU01` |

`FLVN00` / `FLCU00` are the "FI Vendor / Customer" roles (recon-account level). `FLVN01` / `FLCU01` add extended attributes like purchasing/sales org assignments. Including both is the safe default.

## Supplier sub-entity (`to_Supplier`)

Only when the BP is a supplier:

```json
"to_Supplier": {
  "to_SupplierPurchasingOrg": {
    "results": [{
      "PurchasingOrganization": "1010",
      "PurchaseOrderCurrency": "EUR",     // NOT "OrderCurrency" — common mistake
      "PaymentTerms": "0004"
    }]
  },
  "to_SupplierCompany": {
    "results": [{
      "CompanyCode": "1010",
      "ReconciliationAccount": "21100000",   // payables
      "PaymentTerms": "0004"
    }]
  }
}
```

Required:
- `PurchasingOrganization` + `PurchaseOrderCurrency` on `to_SupplierPurchasingOrg`
- `CompanyCode` + `ReconciliationAccount` on `to_SupplierCompany`

## Customer sub-entity (`to_Customer`)

Only when the BP is a customer:

```json
"to_Customer": {
  "to_CustomerSalesArea": {
    "results": [{
      "SalesOrganization": "1010",
      "DistributionChannel": "10",
      "Division": "00",
      "CustomerGroup": "01",
      "CustomerPaymentTerms": "0004",
      "Currency": "EUR"                       // required on customer
    }]
  },
  "to_CustomerCompany": {
    "results": [{
      "CompanyCode": "1010",
      "ReconciliationAccount": "12100000",    // receivables
      "PaymentTerms": "0004"
    }]
  }
}
```

Required:
- `SalesOrganization` + `DistributionChannel` + `Division` + `Currency` on `to_CustomerSalesArea`
- `CompanyCode` + `ReconciliationAccount` on `to_CustomerCompany`

Without `Currency` on the sales area:
```
CVI_API/003: Currency (KNVV-WAERS) is a required entry field
```

## Combined customer + supplier

Include BOTH `to_Supplier` AND `to_Customer` blocks in the same POST. All four FLCU/FLVN roles. Single transaction creates everything.

```json
{
  "BusinessPartnerCategory": "2",
  "BusinessPartnerGrouping": "BP02",
  "OrganizationBPName1": "Acme — Trading Partner",
  "to_BusinessPartnerAddress": {
    "results": [{ "Country": "DE", "Language": "EN", "CityName": "Munich", "PostalCode": "80331", "StreetName": "Marienplatz 1" }]
  },
  "to_BusinessPartnerRole": {
    "results": [
      { "BusinessPartnerRole": "FLCU00" }, { "BusinessPartnerRole": "FLCU01" },
      { "BusinessPartnerRole": "FLVN00" }, { "BusinessPartnerRole": "FLVN01" }
    ]
  },
  "to_Customer": {
    "to_CustomerSalesArea": { "results": [{ "SalesOrganization": "1010", "DistributionChannel": "10", "Division": "00", "CustomerGroup": "01", "CustomerPaymentTerms": "0004", "Currency": "EUR" }] },
    "to_CustomerCompany": { "results": [{ "CompanyCode": "1010", "ReconciliationAccount": "12100000", "PaymentTerms": "0004" }] }
  },
  "to_Supplier": {
    "to_SupplierPurchasingOrg": { "results": [{ "PurchasingOrganization": "1010", "PurchaseOrderCurrency": "EUR", "PaymentTerms": "0004" }] },
    "to_SupplierCompany": { "results": [{ "CompanyCode": "1010", "ReconciliationAccount": "21100000", "PaymentTerms": "0004" }] }
  }
}
```

This is the highest-coverage BP — sells and buys, gets both customer and supplier numbers (same BP ID for both).

## Field-name pitfalls

| Wrong | Correct | Where |
|---|---|---|
| `OrderCurrency` | `PurchaseOrderCurrency` | Supplier purchasing org |
| `AddressUsage` | (omit — not a field) | Address sub-entity on this tenant version |
| `to_PurchaseOrderAccountAssignment` | `to_AccountAssignment` | (Not a BP thing, but worth remembering across the collection) |

## BP grouping decision tree

| Want | Use | Numbering |
|---|---|---|
| System assigns the BP number for me (7-digit) | `BP02` | Internal — system picks next |
| Specific BP number (e.g. `20500001`) | `BP03` | External — supply `BusinessPartner` field |
| One-time vendor (no recurring relationship) | `CPDS` | Special grouping, different rules |

Default: BP02 unless user has a specific number in mind.
