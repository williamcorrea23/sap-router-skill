# CDS table entity & DDIC table

A RAP managed BO needs a **persistent table**. There are two ways to
declare one:

1. **CDS table entity** (`define table entity`) — the modern, CDS-native
   way; introduced for cloud development.
2. **DDIC database table** (`define table`) — the classic ABAP DDIC table;
   still fully supported and common in samples.

For new RAP development in ABAP Cloud / BTP ABAP Environment, both are
usable; SAP samples use `define table` (DDIC) most often because it predates
table entities. This file covers both.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-table-entities
> https://help.sap.com/docs/abap-cloud/abap-dictionary

---

## 1. DDIC table (`define table`)

```abap
@EndUserText.label: 'Travel — active table'
@AbapCatalog.tableCategory: #TRANSPARENT
@AbapCatalog.deliveryClass: #A
@AbapCatalog.dataMaintenance: #LIMITED
define table ztravel {
  key client            : abap.clnt not null;
  key travel_uuid       : sysuuid_x16 not null;
  travel_id             : abap.numc(8);
  agency_id             : /dmo/agency_id;
  customer_id           : /dmo/customer_id;
  begin_date            : /dmo/begin_date;
  end_date              : /dmo/end_date;
  booking_fee           : /dmo/booking_fee;
  total_price           : /dmo/total_price;
  currency_code         : /dmo/currency_code;
  overall_status        : /dmo/overall_status;
  description           : /dmo/description;

  " standard RAP audit / draft / ETag fields
  created_by            : abp_creation_user;
  created_at            : abp_creation_tstmpl;
  last_changed_by       : abp_locinst_lastchange_user;
  last_changed_at       : abp_lastchange_tstmpl;
  local_last_changed_at : abp_locinst_lastchange_tstmpl;
}
```

### 1.1 Header annotations

| Annotation                                | Common values                                    | Meaning                                                          |
|-------------------------------------------|--------------------------------------------------|------------------------------------------------------------------|
| `@AbapCatalog.tableCategory`              | `#TRANSPARENT`                                   | The default — one physical DB table per CDS table.               |
| `@AbapCatalog.deliveryClass`              | `#A` (application), `#C` (customizing), `#L` (temporary), `#S` (system) | Drives transport and client-copy behavior.                       |
| `@AbapCatalog.dataMaintenance`            | `#LIMITED`, `#ALLOWED`, `#NOT_ALLOWED`           | Whether SE16-style maintenance is allowed.                       |
| `@EndUserText.label`                      | string                                           | Display label in ADT / catalogs.                                 |

### 1.2 Standard RAP audit fields (data elements)

| Data element                              | Purpose                                                  |
|-------------------------------------------|----------------------------------------------------------|
| `sysuuid_x16`                             | 16-byte raw UUID — typical primary key for managed BOs.  |
| `abp_creation_user`                       | Login of the creator (RAP fills this).                   |
| `abp_creation_tstmpl`                     | UTC timestamp of creation.                               |
| `abp_locinst_lastchange_user`             | Login of the last changer.                               |
| `abp_lastchange_tstmpl`                   | UTC timestamp of last change — used as **total ETag**.   |
| `abp_locinst_lastchange_tstmpl`           | Local instance last-change timestamp — **etag master**.  |

These are populated automatically by the RAP managed runtime when the
corresponding BDEF declarations are present (`lock master total etag …`,
`etag master …`, `field ( readonly )`).

### 1.3 Client field

`client : abap.clnt not null;` is **mandatory** for application tables in
the ABAP Cloud development model. RAP and CDS handle client implicitly —
you don't filter by client in your application code.

---

## 2. CDS table entity (`define table entity`)

The modern equivalent. Same semantics, CDS-native syntax:

```abap
@EndUserText.label: 'Travel — active table'
define table entity Z_Travel
{
  key TravelUUID         : sysuuid_x16;
      TravelID           : abap.numc(8);
      AgencyID           : /dmo/agency_id;
      CustomerID         : /dmo/customer_id;
      BeginDate          : /dmo/begin_date;
      EndDate            : /dmo/end_date;
      BookingFee         : /dmo/booking_fee;
      TotalPrice         : /dmo/total_price;
      CurrencyCode       : /dmo/currency_code;
      OverallStatus      : /dmo/overall_status;
      Description        : /dmo/description;

      CreatedBy          : abp_creation_user;
      CreatedAt          : abp_creation_tstmpl;
      LastChangedBy      : abp_locinst_lastchange_user;
      LastChangedAt      : abp_lastchange_tstmpl;
      LocalLastChangedAt : abp_locinst_lastchange_tstmpl;
}
```

Notes:

- The client field is **implicit** in CDS table entities — don't declare it.
- Field naming follows CDS convention (CamelCase). The generated database
  column names are auto-derived.
- Mapping the CDS field name to a different DB column name uses
  `<field> : <data_element> @AbapCatalog.databaseColumn: 'CUSTOM_COL'`.

---

## 3. Picking between DDIC table and table entity

| Concern                        | DDIC `define table`            | CDS `define table entity`     |
|--------------------------------|--------------------------------|-------------------------------|
| New ABAP Cloud development     | Supported                      | Supported, preferred long-term|
| S/4HANA Cloud, public edition  | Supported (released)           | Supported                     |
| On-stack ABAP Platform         | Supported                      | Supported (recent releases)   |
| Field naming convention        | snake_case                     | CamelCase                     |
| Client column                  | Explicit (`client : abap.clnt`)| Implicit                      |
| Foreign keys                   | Domain-level                   | Declared on the field         |
| SAP samples                    | Predominant                    | Growing                       |

For greenfield projects starting today on ABAP Cloud, **either is fine**.
Match your team's existing style and the surrounding SAP-delivered objects.

---

## 4. Key strategies

### 4.1 GUID / UUID key (recommended for managed BOs)

```abap
key travel_uuid : sysuuid_x16 not null;   " 16-byte raw
```

RAP can generate the UUID via the BDEF clause:
`field ( numbering : managed, readonly ) TravelUUID;`. The UUID is opaque,
collision-free, and survives transports.

### 4.2 Number range key (managed late numbering)

```abap
key travel_id : abap.numc(8) not null;
```

In the BDEF: `field ( numbering : managed ) TravelID;` plus a number range
configuration in the saver phase. The key is assigned at save time, not on
draft create. Keeps the number range from being burned on discarded drafts.

### 4.3 Composite key

Common on child entities:

```abap
key client     : abap.clnt not null;
key booking_uuid : sysuuid_x16 not null;
key travel_uuid  : sysuuid_x16 not null;   " parent reference, part of key
```

---

## 5. Foreign keys and value helps

Foreign keys in DDIC tables are declared at the data-element / domain level:

```abap
@EndUserText.label: 'Currency Code'
@Semantics.currencyCode: true
domain currency_code : abap.cuky;          " links to T006 via fixed FK
```

For CDS-level value helps (the more flexible mechanism), see
[value-help.md](value-help.md).

---

## 6. Common gotchas

- ❌ Forgetting `client : abap.clnt not null;` in a DDIC table — fails ATC.
- ❌ Using `abap.uuid` instead of `sysuuid_x16` — `abap.uuid` is a 36-char
  string type; `sysuuid_x16` is the raw 16-byte form RAP works with.
- ❌ Declaring audit fields without the matching `field ( readonly )` in the
  BDEF — users can write to `LastChangedAt`, corrupting the ETag.
- ❌ Setting `@AbapCatalog.dataMaintenance: #ALLOWED` on a production table —
  enables SE16 maintenance, which bypasses RAP.
- ❌ Mixing `abp_creation_tstmpl` (UTC) and `abp_locinst_lastchange_tstmpl`
  (local instance) semantics — they exist for different RAP roles.

---

## 7. Anchor references

- DDIC database tables:
  https://help.sap.com/docs/abap-cloud/abap-dictionary/database-tables
- CDS table entity:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-table-entities
- RAP standard audit fields:
  https://help.sap.com/docs/abap-cloud/abap-rap/standard-rap-fields

Related skill files: [cds-view-entity.md](cds-view-entity.md),
[behavior-definition.md](behavior-definition.md).
