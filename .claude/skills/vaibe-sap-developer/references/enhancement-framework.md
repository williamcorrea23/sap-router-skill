# Enhancement Framework (General — any standard object)
Parent skill: vaibe-sap-developer
Load when: user needs to enhance standard SAP behavior on an object/transaction that is *not* IDoc processing. For IDoc-specific enhancement/retrigger logic, use `references/idoc-enhancement.md` instead — this file covers the general case (a standard class, transaction, or report that isn't IDoc-related).

Edition check first — per `references/edition-legality.md`, classic BAdIs, user-exits, and implicit enhancements are **❌ not available** in Cloud Public Edition or BTP ABAP Environment; only **released BAdIs** from the extensibility catalog are legal there, and only the ones SAP has explicitly released for that exact app. Never invent a plausible-looking BAdI name for those editions — verify it's actually in the catalog (see `references/extensibility-and-auth.md` for how key-user/developer extensibility works there) before generating an implementation.

## Priority order (On-Premise / Private Edition)
1. **Enhancement Spot / classic BAdI (SE18/SE19)** — preferred. Upgrade-safe, multiple implementations can coexist.
2. **Explicit Enhancement Point/Section** — acceptable when SAP ships one at the exact spot needed and no BAdI exists.
3. **Implicit Enhancement** — last resort only; breaks more easily on upgrade since it's not a declared extension point. Flag this choice explicitly to the user rather than defaulting to it silently.
4. **User-exit (CMOD/SMOD)** — legacy fallback, only when the object predates the Enhancement Framework and no BAdI/spot exists for it.

## Skeleton — implementing a classic BAdI
```abap
CLASS zcl_im_my_badi_impl DEFINITION
  PUBLIC FINAL CREATE PUBLIC.
  PUBLIC SECTION.
    INTERFACES if_ex_badi_name.
ENDCLASS.

CLASS zcl_im_my_badi_impl IMPLEMENTATION.
  METHOD if_ex_badi_name~check_something.
    " keep this thin — delegate to a testable class, don't put full logic here
    rv_result = zcl_my_check_logic=>evaluate( is_data = is_data ).
  ENDMETHOD.
ENDCLASS.
```
Rule: same testability principle as Function Modules (`references/function-modules.md`) — the BAdI implementation class is a thin adapter; the actual logic lives in a separately unit-testable class.

## Filter-dependent BAdIs
If the BAdI is filter-dependent, confirm the filter value with the user (e.g. company code, document type) before generating the implementation — a missing or wrong filter is a common cause of "my enhancement never fires."

## Anti-patterns
- Don't propose an implicit enhancement when an Enhancement Spot/BAdI exists at the same location — check first.
- Don't generate enhancement code at all for Public Edition/BTP without confirming the exact BAdI name is in that tenant's released extensibility catalog.
- Don't put `SELECT`/commit logic directly in the BAdI method — same Open SQL and exception rules apply as everywhere else (`references/anti-patterns.md`, `references/exception-patterns.md`).
