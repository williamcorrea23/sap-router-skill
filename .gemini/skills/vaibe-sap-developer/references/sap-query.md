# SAP Query / ABAP Query (SQ01)
Parent skill: vaibe-sap-developer
Load when: the user asks for a quick ad-hoc reporting tool built via SQ01/SQ02/SQ03 rather than a custom ABAP report or CDS view.

This is almost entirely a Customizing/maintenance-tool activity, not generatable ABAP code — walk through the setup rather than producing a code artifact.

Edition check first — per `references/edition-legality.md`, SAP Query is a classic SAP GUI tool, **❌ not available** in Cloud Public Edition or BTP ABAP Environment. For those editions, redirect to a CDS-based custom analytical query or a Fiori-based "Manage Queries"-style app instead.

## Setup sequence (On-Premise / Private Edition)
1. **InfoSet (SQ02)** — define the data source: a single table, a join, or a logical database. This is where field selection and any calculated fields live.
2. **User group (SQ03)** — assign the InfoSet to a user group so the right people can build/run queries against it.
3. **Query (SQ01)** — build the actual query: selection screen fields, output list layout, sort/totals.

## When a calculated field needs ABAP
InfoSet extras can carry a small ABAP code snippet for a derived field:
```abap
IF vbap-netwr > 10000.
  zz_high_value = 'X'.
ELSE.
  zz_high_value = space.
ENDIF.
```
Rule: keep InfoSet code snippets trivial (simple derivations only) — anything with real branching/business logic belongs in a proper class method exposed via a CDS view instead; SAP Query isn't unit-testable.

## When NOT to recommend SAP Query
- Recurring, performance-sensitive, or programmatically-consumed reporting → a CDS view (`references/hana-patterns.md`) is the better fit; SAP Query output isn't consumable as an API.
- Anything needing authorization-object-level row filtering beyond what the InfoSet's logical database already provides.

## Anti-patterns
- Don't propose SAP Query for Cloud Public Edition or BTP ABAP Environment — it doesn't exist there.
- Don't put non-trivial business logic in an InfoSet's ABAP extras — that code can't be unit tested (see `references/unit-test-patterns.md`).
