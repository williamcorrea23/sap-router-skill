# Anti-Patterns — Reject These (Before / After)
Parent skill: vaibe-sap-developer
Load when: validating generated code in Phase 3, or when user's request risks legacy patterns.

## 1. Legacy DB Access vs Open SQL Array
**Reject:**
```abap
SELECT * FROM zsales_order INTO TABLE lt_orders.
LOOP AT lt_orders INTO ls_order.
  SELECT SINGLE * FROM zcustomer INTO ls_customer WHERE id = ls_order-customer_id.
ENDLOOP.
```
**Use instead:**
```abap
SELECT order_id, customer_id, net_amount
  FROM zsales_order
  INTO TABLE @DATA(lt_orders).

SELECT customer_id, name
  FROM zcustomer
  FOR ALL ENTRIES IN @lt_orders
  WHERE customer_id = @lt_orders-customer_id
  INTO TABLE @DATA(lt_customers).
```
Reason: SELECT-in-LOOP = N+1 DB roundtrips. Push joins/set-based reads to DB tier.

## 2. Missing AUTHORITY-CHECK
**Reject:**
```abap
METHOD delete_order.
  DELETE FROM zsales_order WHERE order_id = iv_order_id.
ENDMETHOD.
```
**Use instead:**
```abap
METHOD delete_order.
  AUTHORITY-CHECK OBJECT 'Z_SALESORD' ID 'ACTVT' FIELD '06'.
  IF sy-subrc <> 0.
    RAISE EXCEPTION NEW zcx_sales_order( textid = zcx_sales_order=>no_authority ).
  ENDIF.
  DELETE FROM zsales_order WHERE order_id = @iv_order_id.
ENDMETHOD.
```
Reason: every mutating op on an application object needs an explicit check — never assume caller is pre-authorized.

## 3. Empty CATCH Block
**Reject:**
```abap
TRY.
    lo_service->call( ).
  CATCH cx_root.
ENDTRY.
```
**Use instead:**
```abap
TRY.
    lo_service->call( ).
  CATCH cx_root INTO DATA(lx_error).
    RAISE EXCEPTION NEW zcx_application( previous = lx_error ).
ENDTRY.
```
Reason: swallowed exceptions hide failures from monitoring and from the caller — always log/re-raise.

## 4. Publishing Interface CDS Directly to OData
**Reject:**
```abap
@OData.publish: true
define root view entity ZI_SalesOrder ...
```
**Use instead:**
```abap
@OData.publish: true
define root view entity ZC_SalesOrder
  as projection on ZI_SalesOrder { ... }
```
Reason: interface views are the reuse layer — UI/integration concerns leak into every future consumer if published directly.

## 5. RAISE EXCEPTION Inside RAP Validation
**Reject:**
```abap
METHOD validateAmount.
  IF amount <= 0.
    RAISE EXCEPTION TYPE zcx_sales_order.
  ENDIF.
ENDMETHOD.
```
**Use instead:** see `exception-patterns.md` — populate `failed`/`reported`, never throw inside a behavior handler method.
Reason: RAP framework expects structured failure reporting, not exceptions, from validation/determination methods — a thrown exception here dumps the transaction instead of surfacing a field-level message.

## 6. Hardcoded Client/Language in AMDP
**Reject:**
```sql
SELECT * FROM zsales_order WHERE mandt = '100';
```
**Use instead:** let `$session.client` handle it implicitly per `hana-patterns.md` — never hardcode client in AMDP SQL.
Reason: breaks portability across clients/systems, defeats clean-core multi-tenancy assumptions.
