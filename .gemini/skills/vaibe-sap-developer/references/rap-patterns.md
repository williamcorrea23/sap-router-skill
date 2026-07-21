# RAP (RESTful ABAP Programming) Patterns
Parent skill: vaibe-sap-developer
Load when: user requests Business Object, BDEF, transactional app, managed/unmanaged RAP, draft handling.

## Managed RAP Skeleton
```abap
managed implementation in class zbp_i_sales_order unique;
managed save;

define behavior for ZI_SalesOrder alias SalesOrder
persistent table zsales_order
lock master
authorization master ( instance )
etag master LastChangedAt
{
  create;
  update;
  delete;

  field ( readonly ) OrderId;
  field ( mandatory ) CustomerId, NetAmount;

  determination setDefaults on create;
  validation validateAmount on save { create; update; }
  action setComplete result [1] $self;

  mapping for zsales_order
  {
    OrderId      = order_id;
    CustomerId   = customer_id;
    NetAmount    = net_amount;
  }
}
```

## Behavior Implementation Class
```abap
CLASS lhc_salesorder DEFINITION INHERITING FROM cl_abap_behavior_handler.
  PRIVATE SECTION.
    METHODS validateAmount FOR VALIDATE ON SAVE
      IMPORTING keys FOR SalesOrder~validateAmount.
    METHODS setDefaults FOR DETERMINE ON MODIFY
      IMPORTING keys FOR SalesOrder~setDefaults.
ENDCLASS.

CLASS lhc_salesorder IMPLEMENTATION.
  METHOD validateAmount.
    READ ENTITIES OF zi_salesorder IN LOCAL MODE
      ENTITY SalesOrder
      FIELDS ( NetAmount ) WITH CORRESPONDING #( keys )
      RESULT DATA(orders).

    LOOP AT orders INTO DATA(order) WHERE NetAmount <= 0.
      APPEND VALUE #( %tky = order-%tky ) TO failed-salesorder.
      APPEND VALUE #( %tky = order-%tky
                       %msg = NEW zcx_sales_order(
                         textid = zcx_sales_order=>amount_invalid ) )
        TO reported-salesorder.
    ENDLOOP.
  ENDMETHOD.

  METHOD setDefaults.
    " default field population
  ENDMETHOD.
ENDCLASS.
```

## Unmanaged vs Managed — Decision Rule
- **Managed**: standard CRUD on DB table, std framework handles save sequence. Default choice.
- **Unmanaged**: complex cross-table save logic, legacy function module wrapping, non-standard persistence. Avoid unless managed genuinely can't fit.

## Draft Handling
- Add `with draft;` to behavior definition for Fiori Elements edit flows.
- Draft table: `define draft table for behavior of <bo> ...`
- Draft actions (`Activate`, `Discard`, `Resume`, `Edit`) come free from framework — never hand-roll.

## Actions & Determinations Cheat Sheet
| Element | Trigger | Use for |
|---|---|---|
| `determination ... on create` | Instance created | Default values, derived fields |
| `determination ... on modify` | Any field change | Recalculation (e.g. totals) |
| `validation ... on save` | Before persist | Business rule checks, raises `failed`/`reported` |
| `action` | Explicit user/API call | State transitions (submit, approve, cancel) |

## Authorization in RAP
```abap
authorization master ( instance )
```
Pair with `AUTHORITY-CHECK` inside behavior class for field-level / instance-level checks — never rely on master auth alone for sensitive ops.

## Projection / Consumption Layer
- Expose interface CDS (`ZI_*`) via projection CDS (`ZC_*`) with `@OData.publish: true` only at consumption layer — never publish interface views directly.
- One projection per use case (UI, integration, analytics) — don't reuse a single projection across unrelated consumers.
