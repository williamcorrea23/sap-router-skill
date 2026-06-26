---
name: abap-unit-testing
description: ABAP Unit testing — test class structure (FOR TESTING), risk levels, test doubles (CL_ABAP_TESTDOUBLE), CDS Test Double Framework, RAP business object testing, coverage analyzer (SCOV), SQL testing isolation, ABAP Unit in CI/CD pipelines. Use when writing ABAP Unit tests, creating test doubles, measuring code coverage, or integrating ABAP tests in CI/CD.
---

# ABAP Unit Testing

Automated unit testing framework for ABAP — equivalent to JUnit/NUnit.

## Test Class Structure

```abap
CLASS ztc_material_handler DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    METHODS setup.
    METHODS teardown.
    METHODS create_material_ok FOR TESTING.
    METHODS create_material_duplicate FOR TESTING.
    METHODS create_material_fail FOR TESTING.
ENDCLASS.

CLASS ztc_material_handler IMPLEMENTATION.
  METHOD setup.
    " Initialize test doubles
  ENDMETHOD.

  METHOD create_material_ok.
    " Given
    DATA(lv_payload) = 'MAT001'.
    " When
    DATA(ls_result) = mo_handler->create_material( lv_payload ).
    " Then
    cl_abap_unit_assert=>assert_equals(
      act = ls_result-status
      exp = 'SUCCESS' ).
  ENDMETHOD.
ENDCLASS.
```

## Risk Levels

| Level | Use Case | Constraints |
|---|---|---|
| HARMLESS | No side effects, read-only | No commit, no RFC to other systems |
| DANGEROUS | May change data | Test data cleanup in teardown |
| CRITICAL | Changes customizing or production data | Requires explicit approval |

## Test Doubles

```abap
" Create test double for logger interface (ABAP 7.50+)
DATA(lo_logger_double) = cl_abap_testdouble=>create( 'ZIF_ZROUTER_LOGGER' ).

" Configure method call
cl_abap_testdouble=>configure_call( lo_logger_double
  )->returning( 'ABC123' )->for_method( 'LOG_ACTION' ).

" Inject into class under test
mo_handler = NEW zcl_material_handler( io_logger = lo_logger_double ).
```

## CDS Test Double Framework

```abap
" Replace CDS view with test data during unit test
" (available in ABAP 7.55+)

CLASS ztc_product_test DEFINITION FOR TESTING.
  PRIVATE SECTION.
    CLASS-DATA go_cds_test_environment TYPE REF TO if_cds_test_environment.
    CLASS-METHODS class_setup.
    CLASS-METHODS class_teardown.
    METHODS test_product_query FOR TESTING.
ENDCLASS.

CLASS ztc_product_test IMPLEMENTATION.
  METHOD class_setup.
    " Create CDS test double for Z_I_PRODUCT
    go_cds_test_environment = cl_cds_test_environment=>create(
      i_for_entities = VALUE #( ( 'Z_I_PRODUCT' ) ) ).
  ENDMETHOD.

  METHOD test_product_query.
    " Insert test data
    go_cds_test_environment->insert_test_data(
      i_data = VALUE #( ( matnr = 'TEST001' maktx = 'Test Product' ) ) ).
    " Execute test
    SELECT * FROM z_i_product INTO TABLE @DATA(lt_products).
    cl_abap_unit_assert=>assert_equals( act = lines( lt_products ) exp = 1 ).
  ENDMETHOD.
ENDCLASS.
```

## Coverage Analyzer (SCOV)

```
SCOV transaction → Profile → Start
  → Run ABAP Unit tests (Ctrl+Shift+F10)
    → SCOV → Stop → Display Coverage

Target: ≥ 80% statement coverage
```

## ABAP Unit in CI/CD

```yaml
# .abapgit-ci.yml
test:
  abap_unit:
    packages:
      - ZROUTER_MM
      - ZROUTER_SD
    coverage_threshold: 80
```

## Gotchas

- **FOR TESTING classes** are excluded from production ABAP loads
- **RISK LEVEL HARMLESS** classes skip SAP-internal checks (faster)
- **CDS Test Double** requires ABAP 7.55+ (S/4HANA 2020+)
- **Test isolation**: each test method gets fresh data via ROLLBACK WORK
