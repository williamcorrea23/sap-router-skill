# Extensibility & Authorization Objects
Parent skill: vaibe-sap-developer
Load when: (a) the user needs a *new* custom authorization object, not just an `AUTHORITY-CHECK` against an existing one, or (b) environment = Cloud Public Edition or BTP ABAP Environment and the request needs general key-user/developer extensibility guidance beyond a specific RAP/CDS/OData pattern already covered elsewhere.

## (a) Creating a new custom authorization object (SU21)
This is a Customizing/IMG activity, not generatable ABAP code — walk the user through it rather than producing a code artifact:
1. SU21 → create object class (if needed) → create authorization object (`Z_*`/`Y_*` namespace) with up to 10 fields, each backed by an existing data element with a values/check table (e.g. reuse `ACTVT` for activity-type fields).
2. Assign the new object to a role in PFCG and maintain field values there — this step happens outside ABAP entirely, in the role.
3. Reference the new object's exact name and field names back in the generated `AUTHORITY-CHECK` statement (see `references/anti-patterns.md` for the check pattern itself):
```abap
AUTHORITY-CHECK OBJECT 'Z_PO_APPR'
  ID 'ACTVT' FIELD '01'
  ID 'WERKS' FIELD ls_order-werks.
IF sy-subrc <> 0.
  " raise/report — see references/exception-patterns.md
ENDIF.
```
Rule: never invent field names for a custom auth object the user hasn't actually created yet — ask for the exact object name and field list if it already exists, or walk through the SU21 steps above if it doesn't.

## (b) Key-user & developer extensibility (Cloud Public Edition / BTP ABAP Environment)
Per `references/edition-legality.md`, custom development under these editions is restricted to the **released extensibility catalog** — nothing outside it is legal, regardless of how plausible it looks.

| Extension type | What it actually is | Where it's done |
|---|---|---|
| Custom Fields | Add a field to an existing app/CDS view via a guided wizard | "Custom Fields" Fiori app (key user), or a CDS extend-include for developer extensibility |
| Custom Logic | Implement one of SAP's pre-defined, released BAdIs for that app | "Custom Logic" Fiori app (key user) or BTP ABAP Environment-side implementation against the released BAdI interface |
| Custom Business Objects | A managed RAP BO built against released APIs only | Developer extensibility — see `references/rap-patterns.md` |
| Custom CDS Views | A CDS view consuming only released CDS entities | Developer extensibility |

Rule: before generating any "Custom Logic"/BAdI implementation for these editions, confirm the exact BAdI name is genuinely listed as released for that target app — check the SAP Business Accelerator Hub / extensibility catalog reference the user provides, don't assume one exists because it would make sense to. If the user hasn't confirmed it's released, say so plainly instead of generating a best-guess implementation.

## Anti-patterns
- Don't generate `AUTHORITY-CHECK` against a custom object name the user hasn't told you actually exists.
- Don't propose Custom Logic/BAdI implementations for Public Edition/BTP without the user confirming catalog availability first.
