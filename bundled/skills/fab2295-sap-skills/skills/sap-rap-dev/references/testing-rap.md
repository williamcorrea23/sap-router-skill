# Testing RAP business objects

RAP testing has three layers:

1. **Unit tests** for behavior pool methods using the RAP test double
   framework — fast, no DB.
2. **Integration tests** through the local service endpoint — slower, with
   the OData stack in the loop.
3. **Manual round-trips** via the service binding preview (Fiori Elements
   generic app).

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-rap/testing
> https://help.sap.com/docs/abap-cloud/abap-rap/behv-test-environment

---

## 1. ABAP Unit basics

RAP tests are ABAP Unit tests like any other ABAP class:

```abap
CLASS ltc_validate_dates DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    CLASS-DATA mr_cds_test_environment TYPE REF TO if_cds_test_environment.
    CLASS-DATA mr_test_environment     TYPE REF TO if_abap_behv_test_environment.

    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS       setup.
    METHODS       teardown.
    METHODS       end_date_before_begin_date FOR TESTING.

ENDCLASS.
```

`DURATION SHORT` + `RISK LEVEL HARMLESS` qualifies the test for any
tier — including CI on production-similar systems — because the RAP test
doubles don't touch the real DB.

---

## 2. The RAP test double framework

`cl_abap_behv_test_environment` and `cl_cds_test_environment` together
isolate the BO under test:

| Double                        | What it intercepts                                                      |
|-------------------------------|--------------------------------------------------------------------------|
| `cl_cds_test_environment`     | CDS view reads — staged with `insert_test_data`, no real DB hit.        |
| `cl_abap_behv_test_environment` | EML calls against the BO — routed through the real behavior pool with staged data. |

### 2.1 Setup pattern

```abap
CLASS ltc_validate_dates IMPLEMENTATION.

  METHOD class_setup.
    " Stage the CDS doubles for every view the handler reads from
    mr_cds_test_environment = cl_cds_test_environment=>create(
      i_for_entities = VALUE #(
        ( i_for_entity = 'I_Travel' )
        ( i_for_entity = 'I_Booking' )
        ( i_for_entity = 'I_Agency' )
        ( i_for_entity = 'I_Customer' )
      ) ).

    " Stage the BO double for the BO under test
    mr_test_environment = cl_abap_behv_test_environment=>create(
      handler_for_behavior_definitions = VALUE #( ( name = 'I_Travel' ) ) ).
  ENDMETHOD.

  METHOD class_teardown.
    mr_test_environment->destroy( ).
    mr_cds_test_environment->destroy( ).
  ENDMETHOD.

  METHOD setup.
    mr_test_environment->clear_doubles( ).
    mr_cds_test_environment->clear_doubles( ).
  ENDMETHOD.

ENDCLASS.
```

---

## 3. Testing a validation

```abap
METHOD end_date_before_begin_date.
  " 1. Stage a Travel row with begin > end (the invalid case)
  DATA travels TYPE STANDARD TABLE OF I_Travel.
  travels = VALUE #(
    ( TravelUUID    = '00000000000000000000000000000001'
      TravelID      = '00000001'
      AgencyID      = '70010'
      CustomerID    = '000001'
      BeginDate     = '20260601'
      EndDate       = '20260501'     " end < begin
      CurrencyCode  = 'EUR'
      OverallStatus = 'O' )
  ).
  mr_cds_test_environment->insert_test_data( travels ).

  " 2. Trigger the validation by updating a watched field, then commit
  MODIFY ENTITIES OF i_travel
    ENTITY Travel
      UPDATE FIELDS ( EndDate )
      WITH VALUE #( ( %tky = VALUE #( TravelUUID = '00000000000000000000000000000001' )
                      EndDate = '20260501' ) )
    FAILED DATA(failed) REPORTED DATA(reported) MAPPED DATA(mapped).

  COMMIT ENTITIES RESPONSE OF i_travel
    FAILED   failed
    REPORTED reported.

  " 3. Assert the row failed with the expected message
  cl_abap_unit_assert=>assert_not_initial( failed-travel ).
  cl_abap_unit_assert=>assert_not_initial( reported-travel ).

  READ TABLE reported-travel INTO DATA(msg)
    WITH KEY %state_area = 'VALIDATE_DATES'.
  cl_abap_unit_assert=>assert_subrc( exp = 0 ).
ENDMETHOD.
```

The pattern: stage → invoke → assert on `failed` / `reported`.

---

## 4. Testing a determination

```abap
METHOD total_price_recomputes_after_booking_fee.
  " Stage a Travel + Booking
  mr_cds_test_environment->insert_test_data( VALUE #( I_Travel = VALUE #(
    ( TravelUUID = uuid_travel
      BookingFee = '100.00'
      TotalPrice = '0.00'
      CurrencyCode = 'EUR' ) ) ) ).
  mr_cds_test_environment->insert_test_data( VALUE #( I_Booking = VALUE #(
    ( BookingUUID  = uuid_booking
      TravelUUID   = uuid_travel
      FlightPrice  = '500.00'
      CurrencyCode = 'EUR' ) ) ) ).

  " Modify BookingFee to trigger the determination
  MODIFY ENTITIES OF i_travel
    ENTITY Travel
      UPDATE FIELDS ( BookingFee )
      WITH VALUE #( ( %tky = VALUE #( TravelUUID = uuid_travel )
                      BookingFee = '120.00' ) )
    REPORTED DATA(reported).

  " Read back and assert
  READ ENTITIES OF i_travel
    ENTITY Travel
      FIELDS ( TotalPrice )
      WITH VALUE #( ( %tky = VALUE #( TravelUUID = uuid_travel ) ) )
    RESULT DATA(result).

  cl_abap_unit_assert=>assert_equals(
    exp = CONV /dmo/total_price( '620.00' )    " 120 + 500
    act = result[ 1 ]-TotalPrice ).
ENDMETHOD.
```

---

## 5. Testing an action

```abap
METHOD accept_travel_sets_status_a.
  mr_cds_test_environment->insert_test_data( VALUE #( I_Travel = VALUE #(
    ( TravelUUID = uuid OverallStatus = 'O' ) ) ) ).

  MODIFY ENTITIES OF i_travel
    ENTITY Travel
      EXECUTE acceptTravel
      FROM VALUE #( ( %tky = VALUE #( TravelUUID = uuid ) ) )
    RESULT DATA(result) FAILED DATA(failed) REPORTED DATA(reported).

  cl_abap_unit_assert=>assert_initial( failed-travel ).
  cl_abap_unit_assert=>assert_equals(
    exp = 'A'
    act = result[ 1 ]-%param-OverallStatus ).
ENDMETHOD.
```

---

## 6. Testing feature controls

```abap
METHOD accept_disabled_when_status_x.
  mr_cds_test_environment->insert_test_data( VALUE #( I_Travel = VALUE #(
    ( TravelUUID = uuid OverallStatus = 'X' ) ) ) ).

  READ ENTITIES OF i_travel
    ENTITY Travel
      REQUEST FEATURES ( %action-acceptTravel )
      WITH VALUE #( ( %tky = VALUE #( TravelUUID = uuid ) ) )
    RESULT DATA(features).

  cl_abap_unit_assert=>assert_equals(
    exp = if_abap_behv=>fc-o-disabled
    act = features[ 1 ]-%action-acceptTravel ).
ENDMETHOD.
```

---

## 7. Integration tests via the local service endpoint

For end-to-end verification through the OData stack, you can call the
local service endpoint via `cl_web_http_client_manager`. This exercises
the binding, the OData runtime, authorization, and the BO together.

```abap
" The actual URL comes from the active service binding's Local Service
" Endpoint field in ADT — replace the placeholder before running.
DATA(http_destination) = cl_http_destination_provider=>create_by_url(
                           i_url = '<replace-with-local-service-endpoint-url-from-ADT>' ).
DATA(http_client)      = cl_web_http_client_manager=>create_by_http_destination(
                           i_destination = http_destination ).

DATA(request) = http_client->get_http_request( ).
request->set_method( if_web_http_client=>get ).
request->set_uri( '/Travel' ).
request->set_header_field( i_name = 'Accept' i_value = 'application/json' ).

DATA(response) = http_client->execute( i_method = if_web_http_client=>get ).
cl_abap_unit_assert=>assert_equals(
  exp = 200
  act = response->get_status( )-code ).
```

Integration tests are slower and depend on system state, but catch issues
the unit tests miss (annotation rendering, binding-level behavior,
authorization).

---

## 8. Service binding preview (manual)

Every active service binding has a **Service Binding Preview** button.
Use it to:

- Smoke-test CRUD round-trips during development.
- Verify draft handling end-to-end (create → edit → leave → resume → save).
- Check that `@UI.*` annotations render as expected.
- Reproduce user-reported issues interactively.

Not a substitute for automated tests.

---

## 9. ATC — static checks

ABAP Test Cockpit (ATC) runs static checks against RAP code. Useful
variants:

- `SAP_CP_READINESS_REMOTE_*` — cloud readiness (released APIs only,
  cloud-allowed syntax).
- `SAP_CLOUD_PLATFORM_ATC_DEFAULT` — default ATC variant for BTP ABAP.
- `PERFORMANCE_DB` — SQL / CDS performance.

Run ATC in ADT (right-click package → Run As → ABAP Test Cockpit With…)
and gate CI on Priority 1 / 2 findings.

---

## 10. Common gotchas

- ❌ Forgetting to stage *every* CDS view the handler reads — the handler
  reads from `I_Travel` and `I_Booking`; both must be in the doubles set.
- ❌ Reusing the same `class_setup` doubles across tests without
  `clear_doubles` in `setup` — test bleeds into test.
- ❌ Testing without `COMMIT ENTITIES` — `validations on save` only run on
  commit, so without it, you can't see save-phase failures.
- ❌ Mixing real DB writes (a stray `INSERT INTO ztravel`) with doubles —
  the doubles ignore real DB state; the assertion logic gets confused.
- ❌ Marking tests `RISK LEVEL CRITICAL` because of legacy habits — RAP
  tests with doubles are `HARMLESS`; the wrong risk level may exclude them
  from CI.

---

## 11. Anchor references

- RAP testing overview:
  https://help.sap.com/docs/abap-cloud/abap-rap/testing
- `cl_abap_behv_test_environment`:
  https://help.sap.com/docs/abap-cloud/abap-rap/behv-test-environment
- CDS test doubles:
  https://help.sap.com/docs/abap-cloud/abap-cds-development-user/cds-test-doubles
- ABAP Unit:
  https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/abap-unit

Related skill files: [behavior-implementation.md](behavior-implementation.md),
[eml.md](eml.md).
