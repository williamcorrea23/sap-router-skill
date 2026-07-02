---
name: badi-enhancement
description: >-
  SAP BAdI (Business Add-In) and Enhancement Spot patterns — classic BAdI
  (CL_EXITHANDLER), Kernel BAdI (GET BADI), new BAdI (direct reference),
  enhancement spots, implicit enhancements, BAdI filters, fallback classes.
  Use when implementing BAdIs, creating enhancement spots, or finding the
  right BAdI for a customer exit. Follows Karpathy: surgical changes,
  explicit assumptions, verifiable outcomes.
trigger:
  - BAdI
  - badi
  - enhancement spot
  - SE18
  - SE19
  - CL_EXITHANDLER
  - GET BADI
  - enhancement spot implementation
  - customer exit
  - implicit enhancement
  - ENHANCEMENT-SECTION
  - fallback class
  - BAdI filter
  - filtro BAdI
  - implementar BAdI
---

# BAdI and Enhancement Patterns

**Mental model:** A BAdI is an SAP-sanctioned extension contract — SAP defines
an interface at a specific call point; you implement the interface in a Z/Y
class. The SAP standard code calls your implementation via a dispatcher.
No standard code is modified. Upgrades preserve your logic because the contract
(interface) is stable.

## Prerequisites

- SAP system access (DEV client with developer key / S/4HANA Cloud ABAP)
- Transaction SE18 (BAdI definition) and SE19 (BAdI implementation)
- Object name in customer namespace (Z* or Y*)
- Transport request assigned (SE09/SE10)
- For new Kernel BAdI: ABAP ≥ 7.0 (GET BADI statement)
- For new BAdI syntax: ABAP ≥ 7.40 (BADI name directly in code)
- ADT/Eclipse recommended for class-based implementation

## BAdI Type Selection

- **Classic BAdI** (≤ 7.0): Uses `CL_EXITHANDLER=>GET_INSTANCE`. Deprecated — avoid for new development.
- **Kernel BAdI** (≥ 7.0): Uses `GET BADI` statement. Filter support, multiple-use.
- **New BAdI** (≥ 7.40): Direct `BADI_NAME` reference. Best: type-safe, filter UI, fallback class.

> **Rule:** Always prefer New/Kernel BAdI. Only touch classic BAdI when enhancing existing SAP code that already calls `CL_EXITHANDLER`.

## Step 1 — Find the Right BAdI

```abap
" Search BAdI definitions by keyword (SE18 or SQL)
SELECT name, descript FROM badi
  WHERE name LIKE '%MATERIAL%'
  INTO TABLE @DATA(lt_badis).

" Check existing implementations
SELECT badi_name, impl_name FROM badi_impl
  WHERE badi_name = 'BADI_MATERIAL_CHECK'
  INTO TABLE @DATA(lt_impls).
```

```bash
# SAP GUI: SE18 → BAdI Definition → enter name → Display
# Check interface methods and filter types
# SE19 → Create Implementation → enter BAdI name
```

## Step 2 — Implement New Kernel BAdI

```abap
" BAdI Definition: SE18 → ZBADI_VALIDATE_MATERIAL
" Interface: ZIF_BADI_VALIDATE_MATERIAL with method VALIDATE

" Implementation class (SE19 or ADT)
CLASS zcl_badi_material_validate DEFINITION PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES zif_badi_validate_material.
ENDCLASS.

CLASS zcl_badi_material_validate IMPLEMENTATION.
  METHOD zif_badi_validate_material~validate.
    " Surgical: only validate what the BAdI contract expects
    IF iv_material_type = 'ZMAT' AND iv_description IS INITIAL.
      ct_return = VALUE #( BASE ct_return
        ( type = 'E' id = 'ZMM' number = '001'
          message_v1 = iv_material ) ).
    ENDIF.
  ENDMETHOD.
ENDCLASS.
```

## Step 3 — BAdI with Filter

```abap
" BAdI Definition with filter: COUNTRY (type LAND1)
" Fallback class: ZCL_BADI_MATERIAL_DEFAULT
"   → implements same interface, called when no filter matches

" SE19 → Create Implementation:
"   Impl 1: ZCL_BADI_MAT_DE → Filter COUNTRY = 'DE'
"   Impl 2: ZCL_BADI_MAT_BR → Filter COUNTRY = 'BR'
"   No match → ZCL_BADI_MATERIAL_DEFAULT (fallback)

" Caller code (SAP standard or custom):
GET BADI mo_badi
  FILTERS country = lv_land1.

CALL BADI mo_badi->validate
  EXPORTING iv_material_type = lv_mtart
  CHANGING  ct_return         = lt_return.
```

## Step 4 — Enhancement Spots (Fallback When No BAdI Exists)

```abap
" Explicit enhancement section (SAP-defined insertion point)
ENHANCEMENT-SECTION Z_CUSTOM_VALIDATION SPOTS ZSPOT_MATERIAL.
  " Your code — survives upgrades if section is preserved
  DATA(lv_check) = zcl_validator=>check( lv_matnr ).
END-ENHANCEMENT-SECTION.

" Implicit enhancement: end of any method/FM
" SE38/ADT → Edit → Enhancement Operations → Create Implicit Enhancement
```

## BAdI vs Enhancement Spot — Decision

- **Type safety:** BAdI = yes (typed interface) | Enhancement = no
- **Multiple implementations:** BAdI = yes (filters) | Enhancement = single
- **Upgrade safety:** BAdI = SAP contract | Enhancement = partial risk
- **Fallback class:** BAdI = yes | Enhancement = no
- **SAP recommendation:** BAdI first; Enhancement only if no BAdI exists

## Pitfalls

- **Classic CL_EXITHANDLER** — deprecated, slower, no filter UI. Migrate to Kernel BAdI when SAP provides one.
- **No fallback class** — if no filter matches and no fallback exists, the BAdI call is a no-op. Always define a fallback.
- **Modifying SAP standard** — never edit standard code directly. Use BAdI, enhancement spot, or key-user extensibility (S/4HANA).
- **Filter without value** — implementations without filter are ALWAYS called. Unintended side effects.
- **COMMIT in BAdI** — BAdI runs in SAP standard LUW. Never call `COMMIT WORK` inside a BAdI method.
- **Unreleased interface** — check if BAdI interface is released (API state) before implementing in Cloud.
- **Multiple-use BAdI without filter** — all implementations fire; order is undefined. Use filters to control.

## Verification

```abap
" 1. Activate implementation in SE19 → status must be 'Active'
" 2. Set external breakpoint in implementation class
" 3. Trigger SAP standard transaction that calls the BAdI
" 4. Debugger must stop in your method → BAdI is wired correctly

" 5. Verify filter logic:
GET BADI mo_badi FILTERS country = 'DE'.
" → zcl_badi_mat_de called (not fallback)

GET BADI mo_badi FILTERS country = 'XX'.
" → zcl_badi_material_default called (fallback)

" 6. Check transport: SE09 → your impl object is in the request
" 7. ATC check: no priority 1/2 findings on implementation class
" 8. Unit test: call interface method directly with test doubles
```

```bash
# ADT: right-click implementation class → Run As → ABAP Unit Test
# SE19 → Implementation → Test (if BAdI provides test report)
# SE18 → BAdI → Where-used list to confirm call points
```
