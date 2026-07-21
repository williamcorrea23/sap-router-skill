# Playbook — Category 4: Functional (T3 → escalate, triage — do NOT auto-fix)

**Nature:** the **capability is gone** — a cluster removed, an info structure abolished, or a
write that is now forbidden. There is **no mechanical target**; the code must be redesigned onto a
different mechanism, or the requirement re-scoped. The skill's job is a clear **triage write-up +
hand-off**, never an auto-fix.

## Fix approach
1. State that the object is removed and there is **no 1:1 replacement**.
2. Name the redesign direction from the catalog (`s4_replacement`): a released API, the Universal
   Journal, FSCM, Embedded Analytics — or "redesign required".
3. Emit a triage `intent_question`: what business capability does this serve, and which target /
   owner should it move to? **Emit and STOP.**
4. Emit `tier: T3`, `action: escalate`, `category: functional`. Leave `patch: null`.

## Canonical cases
- **RFBLG (FI cluster) / IMPORT FROM DATABASE rfblg**: cluster gone; data in ACDOCA. Direct
  cluster IMPORT/EXPORT is impossible → redesign the read.
- **PCL2 (HR payroll cluster)**: declustered to transparent tables per cluster-ID/infotype; no flat
  map → redesign. *(note-unverified — kept out of the headline metric.)*
- **S001 / S061 (LIS info structures)**: abolished; no 1:1 — stand up Embedded Analytics / a
  released CDS analytic view. Often reached via a **dynamic table name** (`S` + `061`).
- **KONV write** (`UPDATE konv`, incl. dynamic `UPDATE (lv_tabname)`): pricing writes are
  forbidden → use the pricing API. This is *why* a KONV write escalates while a KONV read is T1.

## Why these never auto_apply
A removed capability has no safe mechanical edit. **guard.py** guarantees it: any `auto_apply` on a
write, a non-T1 baseline, or an escalated statement is downgraded to `escalate` — structurally,
regardless of what the model proposed.

## Before → after
```abap
" before — forbidden write to abolished pricing cluster (dynamic target)
lv_tabname = 'KONV'.  UPDATE (lv_tabname) SET kbetr = @lv WHERE (lv_where).
" after — NO auto-fix; triage:
"   intent_question: "Pricing condition writes are forbidden in S/4 (KONV abolished).
"   Should this move to the pricing API / condition technique? Owner?"
```

## Per-object overrides
Catalog (`scripts/catalog.py <OBJECT>`): `s4_replacement` is the redesign direction, `sap_note`
the S4TWL reference. `note_unverified` objects (PCL2) stay out of the headline metric.
