# Changes

## 2026-02-23

### Fix: ValueError in playbook totals formatting

**File:** `app/core/playbook.py` (lines 68, 70)

**Problem:** `_format_totals_with_currency()` crashed with `ValueError: Unknown format code 'f' for object of type 'str'` when totals values (`CS_TRN_LC`, `CS_TRN_GC`) arrived from the database as strings instead of numbers. This broke streaming chat responses during the auto-chain investigation step.

**Fix:** Wrapped the values with `float()` before applying the `,.2f` format specifier:

```python
# Before
parts.append(f"LC: {totals['CS_TRN_LC']:,.2f} {lc_label}")

# After
parts.append(f"LC: {float(totals['CS_TRN_LC']):,.2f} {lc_label}")
```

Applied to both `CS_TRN_LC` and `CS_TRN_GC` formatting.
