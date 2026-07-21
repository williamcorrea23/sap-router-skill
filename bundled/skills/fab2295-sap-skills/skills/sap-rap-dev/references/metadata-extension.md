# Metadata extension & behavior extension

Extensibility in RAP has two faces:

1. **Metadata extension (MDE)** — adds CDS annotations to an existing view
   without modifying it. The most common extension and the safest one.
2. **Behavior extension** — adds validations / determinations / actions to
   an existing BDEF.

Both require the base object to be **extensible** (released for extension
and gated by the right declarations).

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-cds-development-user/metadata-extensions
> https://help.sap.com/docs/abap-cloud/abap-rap/behavior-extension

---

## 1. Metadata extension (annotation-only)

### 1.1 Syntax

```abap
@Metadata.layer: #CUSTOMER
annotate entity C_SalesOrder
with
{
  @UI.lineItem: [ { position: 95, label: 'My custom field' } ]
  @UI.identification: [ { position: 95, label: 'My custom field' } ]
  YY1_MyCustomField;
}
```

Building blocks:

| Element                       | Meaning                                                  |
|-------------------------------|----------------------------------------------------------|
| `@Metadata.layer`             | Override layer — see §1.2.                               |
| `annotate entity <view>`      | The target view (must declare `@Metadata.allowExtensions: true`). |
| `with { … }`                  | Block of element-level annotation overrides.             |
| `<element>;`                  | A reference to an existing element on the target view.   |

### 1.2 Layer override order

Layers, lowest to highest priority:

```
#CORE  →  #LOCALIZATION  →  #INDUSTRY  →  #PARTNER  →  #CUSTOMER
(SAP-delivered)                            (partners)   (customers)
```

The highest layer wins. A `#CUSTOMER` MDE overrides annotations from
`#PARTNER`, `#INDUSTRY`, `#LOCALIZATION`, and `#CORE`. Within a layer,
multiple MDEs are merged by `position`.

### 1.3 What an MDE can do

- Add `@UI.lineItem`, `@UI.identification`, `@UI.facet`,
  `@UI.selectionField`, `@UI.fieldGroup` entries.
- Override `@EndUserText.label`, `@EndUserText.quickInfo`.
- Add `@Search.defaultSearchElement`, `@Search.fuzzinessThreshold`.
- Adjust `@Consumption.filter`, `@Consumption.valueHelpDefinition`.

### 1.4 What an MDE cannot do

- ❌ Add a new persistent field — that's a view extension (§2).
- ❌ Remove an existing field.
- ❌ Change the data type / domain of a field.
- ❌ Add or change behavior — that's a behavior extension (§3).

### 1.5 Gate annotations on the target

For the MDE to compile, the target view must declare:

```abap
@Metadata.allowExtensions: true
define root view entity C_SalesOrder { … }
```

If the base view doesn't declare this gate, the MDE simply fails to
activate. That's intentional — extensibility is opt-in per object.

---

## 2. CDS view extension (structural)

Add a new persistent field to an SAP-delivered view.

```abap
@EndUserText.label: 'Custom fields for Sales Order'
extend view entity I_SalesOrder
with
{
  @EndUserText.label: 'My custom field'
  yy1_my_custom_field as YY1_MyCustomField
}
```

The target view must declare an **enhancement category**:

```abap
@AbapCatalog.viewEnhancementCategory: [#PROJECTION_LIST]
```

Common categories:

| Category                          | What you can append                                            |
|-----------------------------------|----------------------------------------------------------------|
| `#NONE`                           | Nothing — sealed.                                              |
| `#PROJECTION_LIST`                | Elements (fields) added to the SELECT list.                    |
| `#JOIN_HIERARCHY`                 | Additional join clauses (e.g. left outer join).                |
| `#UNION`                          | Union legs in a UNION-based view.                              |
| `#GROUP_BY`                       | New aggregate / non-aggregate items in a GROUP BY view.        |
| `#PROJECTION_LIST_OR_PARAMETERS`  | Elements and / or input parameters.                            |

Field extensions on cloud-delivered SAP views usually land in the
**customer-extension include** (a customer-namespace structure
preconfigured by SAP) — ADT generates the boilerplate.

---

## 3. Behavior extension

Add validations / determinations / actions to an SAP-delivered BO.

```abap
extension;
strict ( 2 );

extend behavior for I_SalesOrder
{
  determination computeYY1_DerivedField on modify
    { field YY1_BaseField; }

  validation validateYY1_CustomRule on save
    { field YY1_MyCustomField; create; update; }

  action ( features : instance ) YY1_MyCustomAction result [1] $self;
}
```

The behavior pool for the extension is its own class:

```abap
CLASS zbp_extension_so DEFINITION
  PUBLIC ABSTRACT FINAL
  FOR BEHAVIOR OF I_SalesOrder.
ENDCLASS.

CLASS zbp_extension_so IMPLEMENTATION.
ENDCLASS.

CLASS lhc_extension_so DEFINITION
  INHERITING FROM cl_abap_behavior_handler.

  PRIVATE SECTION.
    METHODS validateyy1_customrule FOR VALIDATE ON SAVE
      IMPORTING keys FOR SalesOrder~validateYY1_CustomRule.

ENDCLASS.

CLASS lhc_extension_so IMPLEMENTATION.
  METHOD validateyy1_customrule.
    " ...
  ENDMETHOD.
ENDCLASS.
```

### 3.1 Naming conventions

- Customer fields use the `YY1_` / `YY2_` prefix (S/4HANA Cloud convention).
- Partners use their reserved namespace (`/<NAMESPACE>/…`).
- Avoid generic names like `MyAction` — extensions live alongside SAP
  deliveries and may collide with future deliveries.

### 3.2 What a behavior extension cannot do

- ❌ Remove or override an existing validation / determination / action.
- ❌ Change the BDEF header (`managed`, `lock master`, etc.).
- ❌ Disable a delivered operation (`create`, `update`, `delete`).
- ❌ Use unreleased APIs in the handler implementation.

---

## 4. Service extension

If the new field / action should appear in the delivered service, extend
the service definition:

```abap
extend service API_SALES_ORDER
{
  expose I_SalesOrderAPI as SalesOrder;
}
```

In practice, delivered services for cloud extensibility already expose the
extensible projection — the new field appears automatically once the view
extension is active. Custom actions in extensions may require regenerating
the affected service binding to surface them on the metadata.

---

## 5. Cloud-readiness rules

Every extension on ABAP Cloud / S/4HANA Cloud, public edition must:

1. Only extend **released** objects (see [released-apis.md](released-apis.md)).
2. Only use **released** APIs in the behavior pool / handler code.
3. Stay inside the customer / partner namespace (no SAP-object modification).
4. Compile under `strict( N )` matching the target release.
5. Pass ATC (ABAP Test Cockpit) cloud-readiness checks.

ATC is the gate: extensions that use unreleased APIs will not pass and
will not transport to production.

---

## 6. Key-user vs. developer extensibility

| Concern                       | Key-user (Custom Fields, Adapt UI)    | Developer (ADT)               |
|-------------------------------|---------------------------------------|-------------------------------|
| Audience                      | Business users / functional consultants | Developers                   |
| Tools                         | Fiori adaptation apps                 | Eclipse + ADT                 |
| Scope                         | Field additions, UI adaptations       | Anything the contract allows  |
| Where extensions live         | Tenant DB (managed by adaptation)     | Transportable ABAP package    |
| Suitable for                  | Simple field-level additions          | Complex logic, custom BOs     |

Behind the scenes, key-user extensions in S/4HANA Cloud, public edition
generate CDS extensions managed by the Fiori adaptation runtime. They end
up in the same metadata model — the entry point is just different.

---

## 7. Common gotchas

- ❌ Forgetting `@Metadata.allowExtensions: true` on a view you want
  customers to extend with annotations — the MDE won't activate.
- ❌ Using `@Metadata.layer: #CUSTOMER` from a partner extension — you'll
  conflict with the customer layer. Partners use `#PARTNER`.
- ❌ Adding fields with non-namespace-prefixed names (`MyField`) — risks
  collision with future SAP deliveries; always use `YY1_*` or partner
  namespace.
- ❌ Putting custom actions on the projection BDEF instead of the interface
  BDEF — `use` exposes existing operations; new operations live where the
  interface BDEF lives (or in an extension on the interface BDEF).

---

## 8. Anchor references

- Extensibility overview:
  https://help.sap.com/docs/abap-cloud/abap-rap/extensibility
- Metadata extensions:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/metadata-extensions
- View enhancement:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-view-enhancement
- Behavior extension:
  https://help.sap.com/docs/abap-cloud/abap-rap/behavior-extension
- Extending services:
  https://help.sap.com/docs/abap-cloud/abap-rap/extending-services

Related skill files: [behavior-definition.md](behavior-definition.md),
[behavior-implementation.md](behavior-implementation.md),
[released-apis.md](released-apis.md).
