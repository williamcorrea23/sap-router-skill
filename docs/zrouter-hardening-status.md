# ZROUTER v5 — Hardening Status

Tracks the v4 architectural flaws (from the `zrouter-v4-analysis` review) against the v5
`deploy/split2` source, and records the fixes applied in this pass.

## Fixed in this pass

| Flaw | Status | Change |
|---|---|---|
| Insecure `evaluate_expression` (blocklist over `GENERATE SUBROUTINE POOL` of request text) | **Removed** | `zcl_zrouter_handler_abstract` — method dropped; dynamic execution of caller input is a code-injection risk a blocklist cannot close. No external callers existed. |
| `RESULT` reserved DDIC field name on older NetWeaver | **Fixed** | `zrouter_log.tabl.ddl` column is `ZRESULT`; `zcl_zrouter_logger` reads it back with `zresult AS result`, so the `ty_log_entry` contract keeps `RESULT`. |
| Missing config/log DDIC tables (runtime blocker) | **Fixed** | Added `zrouter_config.tabl.ddl` + `zrouter_log.tabl.ddl`, wired into `scripts/deploy_all.py`. |
| Empty config registry (runtime blocker) | **Fixed** | `zrouter_seed_config.prog.abap` seeds 38 rows (29 actions + PING) from the handler CASE branches. |
| Shallow deserialization — nested BAPI tables never populated | **Reference fix** | `zcl_zrouter_handler_mm->create_material` now deserializes a composite request (header + client/plant views + X-flags + description table). Pattern to replicate; see below. |

## Already correct in v5 (no change needed)

| Flaw | Finding |
|---|---|
| Logger commits before BAPI commit | v5 logger does **no** `COMMIT WORK`; comment states the caller owns the LUW. Correct. |
| Config cache never refreshes | Mitigated in the HTTP path: `zcl_zrouter_http` instantiates `NEW zcl_zrouter_config( )` per request, so the cache is per-request. Only a concern for long-lived reused instances. |
| Error handling checks only first RETURN row | MM/SD/FI/PP/QM/WM/CO/HCM handlers use `ls_ret-type CA 'EA' OR line_exists( lt_ret[ type = 'E' ] )` — full-table scan. `change_order` (SD) still reads only `INDEX 1` — see below. |

## Nested-table deserialization — fixed and remaining

### Fixed (composite request applied)

| Handler / action | Fix |
|---|---|
| MM `create_material` | header + client/plant views + X-flags + description table |
| MM `create_po` | header + header-X + `poitem` + `poitemx`; full RETURN scan |
| MM `change_po` | **PO number** (was never set -> BAPI always failed) + header + header-X + items; full scan |
| SD `create_order` | header + header-X + `order_items_in` + `order_items_inx` + `order_partners` |
| SD `change_order` | full RETURN scan (INDEX 1 -> any E/A row). Type/INX caveat below. |
| FI `post_document` | header + GL/AP/AR line items + **currencyamount** (was missing entirely); full scan |

### Already correct (payload deserialized into the right shape)

- SD `create_delivery` / `create_invoice` — the whole payload maps to the item/billing table directly.
- PP `create_prod_order` — `BAPI_PRODORD_CREATE` takes a single `orderdata` structure, no tables.
- CO `create_internal_order` — single `i_master_data` structure.
- WM `goods_movement` / `create_to`, QM `create_inspection_lot`, CO `activity_alloc`,
  HCM `create_infotype` — use flat params structs and build a single item; functional for
  single-line requests.

### Remaining — needs live-system verification, not fixed blind

| Handler / action | Gap | Why not fixed here |
|---|---|---|
| SD `change_order` | header-X and item tables still not populated | `BAPI_SALESORDER_CHANGE` uses `BAPISDH1`/`BAPISDH1X` (not the CREATE types the code declares); correcting the types needs a live signature check. Only the safe RETURN-scan fix was applied. |
| PP `confirm_order` | only the order number is set on one timeticket | Yield/activity fields are confirmation-specific; needs the real `BAPI_PP_TIMETICKET` layout verified. |
| QM `record_results` | no characteristic-result table passed | Results table shape is inspection-plan specific. |
| HCM `create_infotype` | key fields only; the `PNNNN` record body is not filled | Infotype record structure is per-infotype. |

Pattern applied (from MM `create_material`):

```abap
TYPES: BEGIN OF ty_req,
         header  TYPE <bapi-header-structure>,
         headerx TYPE <bapi-header-x-structure>,
         items   TYPE STANDARD TABLE OF <bapi-item-structure> WITH DEFAULT KEY,
         " ...additional tables...
       END OF ty_req.
DATA ls_req TYPE ty_req.
/ui2/cl_json=>deserialize( EXPORTING json = iv_payload CHANGING data = ls_req ).
" pass ls_req-header / ls_req-items / ... to the BAPI
```

## Batch atomicity (design tradeoff, not a bug)

Each action handler commits its own LUW, then `zcl_zrouter_batch` issues a final
`BAPI_TRANSACTION_COMMIT`. A batch is therefore **not** all-or-nothing — a later item failing
does not roll back earlier committed items. This is acceptable for idempotent/independent
actions but must be documented for callers who expect transactional batches. Changing it to
all-or-nothing means deferring every per-handler commit to the batch driver.

## abapGit metadata coverage

`scripts/build_model_library.py convert-split2` now emits `.tabl.xml` for DDIC tables (parsed
from their `.tabl.ddl`). Function groups (`.fugr`) remain deferred — abapGit represents a FUGR
as a decomposed folder of includes and per-FM files, which is a separate generation pass. The
validated DDIC/FUGR deploy path for this repo stays DDL/ADT via `deploy_all.py`; the generated
`.tabl.xml` should be confirmed with one ZABAPGIT round-trip before being relied on.
