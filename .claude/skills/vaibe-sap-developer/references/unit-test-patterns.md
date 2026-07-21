# ABAP Unit Test Patterns
Parent skill: vaibe-sap-developer
Load when: user requests test class, ABAP Unit, test double, coverage for generated code.

## Local Test Class Skeleton
```abap
CLASS ltc_processor DEFINITION FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    DATA cut TYPE REF TO lcl_processor.  " class under test

    METHODS:
      setup,
      execute_with_valid_data FOR TESTING,
      execute_with_empty_table FOR TESTING,
      execute_raises_on_invalid_amount FOR TESTING.
ENDCLASS.

CLASS ltc_processor IMPLEMENTATION.
  METHOD setup.
    cut = NEW lcl_processor( ).
  ENDMETHOD.

  METHOD execute_with_valid_data.
    DATA(lt_input) = VALUE ty_data_tab( ( id = 1 amount = '100.00' ) ).
    DATA(lt_result) = cut->execute( it_data = lt_input ).
    cl_abap_unit_assert=>assert_equals(
      act = lines( lt_result )
      exp = 1
      msg = 'Expected one processed record' ).
  ENDMETHOD.

  METHOD execute_with_empty_table.
    DATA(lt_result) = cut->execute( it_data = VALUE #( ) ).
    cl_abap_unit_assert=>assert_initial( lt_result ).
  ENDMETHOD.

  METHOD execute_raises_on_invalid_amount.
    DATA(lt_input) = VALUE ty_data_tab( ( id = 1 amount = '-5.00' ) ).
    TRY.
        cut->execute( it_data = lt_input ).
        cl_abap_unit_assert=>fail( 'Expected zcx_sales_order' ).
      CATCH zcx_sales_order.
        " expected
    ENDTRY.
  ENDMETHOD.
ENDCLASS.
```

## Test Doubles for DB Isolation
```abap
DATA lo_db_double TYPE REF TO if_os_ca_persistency.
lo_db_double = CAST #( cl_abap_testdouble=>create( 'if_os_ca_persistency' ) ).
cl_abap_testdouble=>configure_call( lo_db_double )->returning( lt_fake_data ).
lo_db_double->select_all( ).
```
Rule: never let a unit test hit a real DB table. Inject persistency via interface + test double, or use CDS test framework (`cl_cds_test_environment`) for CDS view unit tests.

## CDS View Unit Test Skeleton
```abap
CLASS ltc_cds_test DEFINITION FOR TESTING DURATION SHORT RISK LEVEL HARMLESS.
  PRIVATE SECTION.
    CLASS-DATA environment TYPE REF TO if_cds_test_environment.
    METHODS test_view_returns_active_orders FOR TESTING.
    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
ENDCLASS.

CLASS ltc_cds_test IMPLEMENTATION.
  METHOD class_setup.
    environment = cl_cds_test_environment=>create( i_for_entity = 'ZI_SalesOrder' ).
  ENDMETHOD.

  METHOD test_view_returns_active_orders.
    environment->insert_test_data( i_data = VALUE zsales_order_tab( ( order_id = '1' status = 'A' ) ) ).
    SELECT * FROM zi_salesorder INTO TABLE @DATA(lt_result).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_result ) exp = 1 ).
  ENDMETHOD.

  METHOD class_teardown.
    environment->destroy( ).
  ENDMETHOD.
ENDCLASS.
```

## Coverage Checklist (apply before returning generated test code)
- Happy path + empty input + boundary value + exception path — minimum 4 test methods per public method.
- `RISK LEVEL HARMLESS` + `DURATION SHORT` unless test genuinely needs DB/network (then justify why it's not mocked).
- No hardcoded dates/timestamps — use `cl_abap_testdouble` for `cl_abap_context_info` or inject time as a parameter.
