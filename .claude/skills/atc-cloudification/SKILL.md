---
name: atc-cloudification
description: ATC cloudification and code quality — ABAP Test Cockpit check variants, custom ATC checks (SCI), ATC exemption management, CI/ATC in transport pipelines, central ATC system, S/4HANA custom code migration checks. Use when running ATC checks, configuring check variants, creating custom ATC checks, or setting up quality gates for ABAP transports.
trigger:
  keywords: [ATC, ABAP Test Cockpit, check variant, SCI, custom check, code quality, S/4HANA migration, exemption, quality gate, transport pipeline]
  intent: >-
    Run ABAP Test Cockpit checks, configure check variants, create custom SCI checks, manage exemptions, and set up quality gates for ABAP transports.
---

# ATC Cloudification

ABAP Test Cockpit (ATC) — static code analysis for ABAP quality and cloud readiness.

## ATC Check Types

| Check Category | Source | Example |
|---|---|---|
| SAP Standard | Built-in | SELECT * check, PERFORM check |
| Custom SCI Checks | Customer | Company-specific naming rules |
| Cloud Readiness | SAP | Non-released API usage |
| Security | SAP + Custom | SQL injection, auth checks |
| Performance | SAP + Custom | SELECT in loop detection |

## Check Variants

```
ATC Transaction (ATC):
  1. Create check variant: ZROUTER_QUALITY
  2. Select checks:
     ✓ Cloud Readiness (SAP)
     ✓ Security checks (SAP)
     ✓ Performance checks (SAP)
     ✓ Z_CL_CHECK_NAMING (custom)
  3. Assign to package: ZROUTER*
```

## Custom ATC Check

```abap
CLASS z_cl_atc_naming DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_ci_atc_check.

  PRIVATE SECTION.
    METHODS check_object_name
      IMPORTING io_object TYPE REF TO if_ci_atc_object.
ENDCLASS.

CLASS z_cl_atc_naming IMPLEMENTATION.
  METHOD if_ci_atc_check~run.
    LOOP AT io_check_set->get_objects( ) INTO DATA(lo_object).
      check_object_name( lo_object ).
    ENDLOOP.
  ENDMETHOD.

  METHOD check_object_name.
    DATA(lv_name) = io_object->get_name( ).
    IF lv_name NP 'Z*'.
      " Finding: object doesn't start with Z
      io_object->create_finding(
        iv_code = 'Z001'
        iv_text = |Object { lv_name } must start with Z|
        iv_priority = if_ci_atc_finding=>c_priority_medium ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

## ATC Exemption

When a check finding is accepted (false positive or accepted risk):
```
ATC Result → Right-click → Request Exemption
  → Reason: "External RFC call is via whitelisted destination"
  → Validity: 12 months
  → Approver: QA Lead
```

## Central ATC System

```
DEV System → Check run → Central ATC (SOLMAN/TMS)
  → Results aggregated across landscape
  → Quality gate in ChaRM / Focused Build
```

## CI/CD Pipeline Integration

```yaml
# .abapgit-ci.yml
atc:
  check_variant: ZROUTER_QUALITY
  fail_on_priority: [CRITICAL, ERROR]
  max_exemptions: 10
  block_transport_on_failure: true
```

## S/4HANA Custom Code Migration

ATC cloud readiness checks:
- Checks for non-released APIs
- Checks for deprecated function modules
- Checks for direct DB access
- Checks for Dynpro usage

```bash
# Run cloud readiness check from command line (via ADT)
# Use sap_router.py for routing
python scripts/sap_router.py route --action BASIS_CODE_ANALYSIS
# → ZROUTER RFC → TRINT_INSPECT_OBJECTS FM
```

## Gotchas

- **ATC check runs as current user** — auth-limited results if user can't see all objects
- **Exemptions must be reviewed** — automatic 12-month expiry
- **Central ATC needs RFC** — SOLMAN or separate ATC system
- **Custom checks are SCI classes** — implement if_ci_atc_check interface
