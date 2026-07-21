# Service definition

A **service definition** is the contract that lists which CDS entities a
service exposes. It's a pure CDS object — no behavior, no binding details.

The matching **service binding** (next file) decides *how* the service is
exposed (OData V4 / V2 / REST / SQL).

```
Service binding   →  ZUI_TRAVEL_O4 (OData V4 UI)            ← how
Service definition →  ZUI_TRAVEL    (define service)         ← what  ← THIS FILE
Projection view    →  R_Travel      (transactional_query)
Interface view     →  I_Travel
Table              →  ztravel
```

> **Anchored to**: https://help.sap.com/docs/abap-cloud/abap-rap/service-definition

---

## 1. Syntax

```abap
@EndUserText.label: 'Travel service'
define service ZUI_TRAVEL {
  expose R_Travel  as Travel;
  expose R_Booking as Booking;
  expose I_Agency  as Agency;
  expose I_Customer as Customer;
}
```

Building blocks:

| Element                         | Meaning                                                       |
|---------------------------------|---------------------------------------------------------------|
| `define service <NAME>`         | Service definition name (the object name in ADT).             |
| `expose <view> as <Alias>`      | Adds the view to the service under the given alias.           |
| `as <Alias>` (optional)         | If omitted, the view's CDS name is used.                      |
| `@EndUserText.label`            | Display label in ADT / catalogs.                              |

---

## 2. What can be exposed

- **Projection views** (`R_…` / `C_…`) — the most common case. The projection
  carries the `provider contract` and (for transactional services) is backed
  by a projection BDEF.
- **Interface views** (`I_…`) — fine for read-only reuse entities exposed as
  parameter or value-help sources. For writable entities, expose the
  projection.
- **CDS views with parameters** — exposable; the OData service will surface
  the parameters.

A service can expose entities backed by **different BOs** — there's no rule
that one service equals one BO. A common pattern is one service per Fiori
app, exposing the root BO + reuse entities the app needs (Agency,
Customer, currency value help, etc.).

---

## 3. One BO, multiple services

A single BO often backs more than one service:

```
I_Travel ─┬─ R_Travel_UI    (transactional_query)    → ZUI_TRAVEL    (OData V4 UI)
          ├─ R_Travel_API   (transactional_interface) → ZAPI_TRAVEL  (OData V4 Web API)
          └─ R_Travel_SQL   (no transactional BDEF)   → ZSQL_TRAVEL  (SQL service)
```

Each projection has its own annotations and BDEF — a UI service uses
`@UI.*` heavily; the Web API service usually does not.

---

## 4. Service annotations

A few annotations on the service definition affect generated OData metadata:

```abap
@EndUserText.label: 'Travel service'
@AbapCatalog.preserveKey: true   " keep field names as defined in CDS
define service ZUI_TRAVEL { … }
```

For entity-level OData metadata, use annotations on the projection view —
not on the service definition.

---

## 5. Service extension

A delivered service can be extended via `extend service`:

```abap
extend service API_SALES_ORDER
{
  expose I_SalesOrderAPI as SalesOrder;
}
```

Use this to surface new fields or actions added by a metadata / behavior
extension. The base service must be released for extension. See
[metadata-extension.md](metadata-extension.md).

---

## 6. Lifecycle

A service definition is **activated**, like any CDS object. ADT generates
the corresponding ABAP runtime artifacts. Activation alone doesn't expose
the service yet — a service binding is required.

A single service definition can back **multiple bindings** simultaneously
(one OData V4 UI binding, one OData V4 Web API binding, etc.). Each
binding is its own URL.

---

## 7. Common gotchas

- ❌ Mixing projections with mismatched provider contracts inside one
  service binding — e.g. exposing both an `analytical_query` and a
  `transactional_query` projection in a single OData V4 binding. Bindings
  expect a consistent contract across the surface.
- ❌ Exposing the interface view (`I_…`) when the service is meant for UI —
  you lose all `@UI.*` annotations because those live on the projection.
- ❌ Renaming the same view differently in two services — possible, but
  confusing for consumers reading the OData metadata.

---

## 8. Anchor references

- Service definition:
  https://help.sap.com/docs/abap-cloud/abap-rap/service-definition
- Service binding:
  https://help.sap.com/docs/abap-cloud/abap-rap/service-binding
- Extending services:
  https://help.sap.com/docs/abap-cloud/abap-rap/extending-services

Related skill files: [service-binding.md](service-binding.md),
[cds-projection-view.md](cds-projection-view.md),
[metadata-extension.md](metadata-extension.md).
