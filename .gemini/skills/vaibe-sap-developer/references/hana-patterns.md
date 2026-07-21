# SAP HANA Design & Pushdown Patterns
This reference details optimization criteria for direct database layer acceleration.
Parent skill: vaibe-sap-developer

## AMDP (ABAP Managed Database Procedures)
- Always declare database languages explicitly (`OPTIONS READ-ONLY USING`).
- Avoid mapping redundant client handling parameters; let the runtime container process variables natively via `$session.client`.

## Advanced CDS View Optimization
- Use explicit inner joins rather than outer associations if cardinality allows.
- Leverage analytical annotations (`@Analytics.dataCategory`) for multidimensional extraction rules.
- Push text conversions and unit rules completely to the database tier.