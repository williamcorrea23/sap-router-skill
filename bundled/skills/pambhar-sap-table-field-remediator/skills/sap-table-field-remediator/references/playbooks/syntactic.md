# Playbook — Category 1: Syntactic (T1 → auto_apply)

**Nature:** mechanical 1:1 change — a table renamed to a transparent equivalent with identical
fields, or a pure field rename. No semantics change. ATC-class finding; the cheapest path.

## Fix approach
- Swap the obsolete name for its catalog `s4_replacement` (identical field set).
- In `apply` mode, edit the `FROM`/target token only; leave the field list and WHERE untouched.
- Emit `tier: T1`, `action: auto_apply`, `category: syntactic`, `replacement: <s4_replacement>`.

## Canonical case
- **KONV → PRCD_ELEMENTS** on a **READ** (`SELECT ... FROM konv`). Same field names (KNUMV, KPOSN,
  KSCHL, KBETR…). A 1:1 rename.

## Escalation triggers — when this is NOT T1 (ratchet UP, never auto_apply)
- **Any write** to the object (`INSERT/UPDATE/MODIFY/DELETE`, including dynamic `UPDATE (var)` and
  native). KONV **writes are forbidden** in S/4 → T3 `escalate` → see `functional.md`.
- The catalog `baseline_tier` is > T1.
- Detection flagged the statement as escalated (offset-parsed, unresolved-dynamic).
- **guard.py enforces all of the above** — it is the structural backstop, not a suggestion.

## Before → after
```abap
" before
SELECT SINGLE kbetr FROM konv  WHERE knumv = @iv AND kposn = @ip INTO @lv.
" after  (T1 auto_apply — identical fields)
SELECT SINGLE kbetr FROM prcd_elements WHERE knumv = @iv AND kposn = @ip INTO @lv.
```

## Per-object overrides
Always defer to the catalog entry (`scripts/catalog.py <OBJECT>`): `baseline_tier`,
`s4_replacement`, `fix_pattern`. The catalog is truth; this playbook is the procedure.
