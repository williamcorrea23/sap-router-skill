# Playbook — Category 2: Structural (T2 → propose)

**Nature:** the access shape must change but the intent is preserved — a table whose data was
**folded into another table**, or a field **relocated** / **widened**. Not a blind rename; the
JOIN/target must be re-pointed. Human reads the proposal, but no deep intent question.

## Fix approach
- Re-point the read to the **released CDS view** (preferred, e.g. VBUK→`I_SalesOrder`) or the absorbing table from the catalog.
- Drop the obsolete join; move the read fields onto the new home table by document category.
- Emit `tier: T2`, `action: propose`, `category: structural`, with a concrete `replacement` and a
  one-paragraph `rationale`. Do NOT auto-apply (the join rewrite needs a human glance).

## Canonical cases
- **VBUK → VBAK** (header status folded in): drop the `INNER JOIN vbuk`; read GBSTK from VBAK
  (or LIKP/VBRK by doc category). Silent empty join if left as-is.
- **VBUP → VBAP** (item status folded in): read GBSTA from VBAP (or LIPS).
- **VBTYP → VBTYPL** (CHAR1 → CHAR4 widening): fix literal comparisons; verify on target release.

## Renamed fields live INSIDE this fix — a WIDENED field used in logic does not
A `SELECT gbstk vbtyp FROM vbuk` read is **one VBUK finding**; the `replacement` + `rationale` carry
the field moves (GBSTK→VBAK-GBSTK, VBTYP→VBAK-VBTYPL). BUT a length/value-CHANGED field used
**outside** the read — e.g. `IF vbtyp = 'C'` (VBTYP widened CHAR1→CHAR4) — is its OWN finding
(see `taxonomy.md` field-level detection).

## Escalation triggers (→ T3)
- A **write** to the folded table → `escalate` (`functional.md`).
- The status fields are consumed in logic whose correctness depends on the *old* data model
  (e.g. a status value compared to a literal that changed meaning) → `semantic.md`.

## Before → after
```abap
" before — header status via the abolished status table
SELECT vbak~vbeln vbuk~gbstk FROM vbak INNER JOIN vbuk ON vbuk~vbeln = vbak~vbeln INTO ...
" after  (T2 propose — status folded into VBAK)
SELECT vbeln gbstk FROM vbak INTO ...
```

## Per-object overrides
Defer to the catalog (`scripts/catalog.py <OBJECT>`) for `s4_replacement`, `cds_view`, `fix_pattern`.
