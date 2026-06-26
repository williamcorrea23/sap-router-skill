---
name: badi-enhancement
description: BAdI and enhancement patterns — classic BAdI (CL_EXITHANDLER), new Kernel BAdI (BADI_NAME), enhancement spots (ENHANCEMENT-SECTION), implicit enhancements, BAdI filters and conditions, fallback class, ENHANCEMENT-POINT, SAP standard modification via BAdI. Use when implementing BAdIs, creating enhancement spots, or finding the right BAdI for a customer exit.
---

# BAdI and Enhancement Patterns

SAP Business Add-Ins (BAdI) — sanctioned extension points for modifying SAP standard behavior.

## BAdI Types

| Type | ABAP Version | Defining Class | Key Feature |
|---|---|---|---|
| Classic BAdI | ≤ 7.0 | CL_EXITHANDLER | Filter-dependent. Deprecated. |
| Kernel BAdI | ≥ 7.0 | GET BADI | Improved performance, filter support |
| New BAdI | ≥ 7.40 | BADI name directly | Best: type-safe, filter UI, fallback |

## New Kernel BAdI Implementation

```abap
" BAdI Definition (SAP or customer namespace)
" SE18 → BAdI Definition → ZBADI_VALIDATE_MATERIAL

" BAdI Implementation
CLASS zcl_badi_material_validate DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES zif_badi_validate_material.
ENDCLASS.

CLASS zcl_badi_material_validate IMPLEMENTATION.
  METHOD zif_badi_validate_material~validate.
    IF iv_material_type = 'ZMAT' AND iv_description IS INITIAL.
      ct_return = VALUE #( BASE ct_return
        ( type = 'E' id = 'ZMM' number = '001'
          message_v1 = iv_material ) ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

## BAdI with Filter

```abap
" BAdI Definition with filter: COUNTRY
" Fallback class: zcl_badi_material_default

" Implementation 1: Filter COUNTRY = 'DE'
" Implementation 2: Filter COUNTRY = 'BR'
" No matching filter → fallback class is called
```

## Finding BAdIs

```abap
" Search for BAdI definitions (SE18)
" Or programmatic lookup:
SELECT name, descript FROM badi
  WHERE name LIKE '%MATERIAL%'
  INTO TABLE @DATA(lt_badis).

" Check existing implementations
SELECT badi_name, impl_name FROM badi_impl
  WHERE badi_name = 'BADI_MATERIAL_CHECK'
  INTO TABLE @DATA(lt_impls).
```

## Enhancement Spots

```abap
" Explicit enhancement section (defined by SAP)
ENHANCEMENT-SECTION Z_CUSTOM_VALIDATION SPOTS ZSPOT_MATERIAL.
  " Custom code here — survives upgrades
  DATA(lv_custom_check) = zcl_custom_validator=>check( lv_matnr ).
END-ENHANCEMENT-SECTION.

" Implicit enhancement at end of any method/FM
" Right-click → Enhance → Create Enhancement Implementation
```

## BAdI vs Enhancement Decision

| Criterion | BAdI | Enhancement Spot |
|---|---|---|
| Type safety | Yes (typed interface) | No |
| Multiple implementations | Yes (with filters) | No (single) |
| Upgrade safety | Yes (SAP contract) | Partial (may break) |
| SAP recommended | Yes | Only if no BAdI exists |
| Fallback | Yes (fallback class) | No |

## Gotchas

- **Classic BAdI (CL_EXITHANDLER)** — avoid for new code. Use Kernel BAdI
- **BAdI without fallback** — SAP may change interface; your implementation breaks
- **Never modify SAP standard code directly** — use BAdI or enhancement spot
- **BAdI filter is optional** — implementations without filter are always called
