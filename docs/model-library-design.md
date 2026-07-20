# Model Library — Design

Status: **proposal** · Version: 0.1 · Scope: design only (no build yet)

## 1. Purpose

A **curated library of golden ABAP base objects** — classes, programs, function groups, DDIC
tables, RAP BOs, unit tests — kept as a versionable abapGit package. Each object is a
parameterized skeleton you clone, rename, fill, and deploy. It is the single source of truth
that the existing generators (`template_repo.py`, `xls_to_bapi.py`, `sap-rap-gen`) draw from.

### Why now

1. **Kills the duplication.** ZROUTER currently exists in 5 divergent copies under `deploy/`
   (`split` v4 incomplete, `split2` v5, `zrouter/split` uppercase dup, `zrouter_export` xml dup,
   plus single-object `abapgit`/`nugg`/`xml` demos). A canonical model library replaces
   "N hand-maintained copies" with "1 source, N generated instances".
2. **Golden templates carry the fixes.** Every base object is authored once with the correct
   pattern — BAPI commit ordering, `BAPIRET2` handling, nested-table deserialization,
   config-cache refresh — so new objects inherit correctness instead of re-introducing the
   v4 flaws documented in `zrouter-v4-analysis`.
3. **Closes the generator loop.** The scaffolding already half-exists (`template_repo.py` for
   JSON→code, `abap_serializer.py` for format conversion, `sap-rap-gen` for RAP). What's
   missing is the **curated source library** they consume.

### Non-goals

- Not a transport/promotion mechanism. abapGit delivers code to DEV; PRD promotion stays on
  CTS/TMS.
- Not a replacement for `deploy/split2` as the *live ZROUTER install set* — the model library
  is upstream of it (split2 becomes a generated instance).
- Not a runtime component. It ships no code to the ABAP server beyond the objects you generate
  from it.

## 2. Format decision

| | abapGit (primary) | .nugg (secondary) | ZDOWNLOAD-XML (legacy) |
|---|---|---|---|
| Git diff/merge | Yes — one file per object, plaintext | No — single XML blob | No |
| Modern objects (CDS/RAP/BDEF) | Yes | No (SAPlink abandoned) | No |
| Install on SAP | `ZABAPGIT` standalone report, no SDK | SAPlink report (dead) | ZDOWNLOAD/YDOWN report |
| Role here | **Source of truth** | Export target for legacy systems | Export target only |

**Decision: abapGit is the canonical on-disk format.** `.nugg` and ZDOWNLOAD-XML are produced
*on demand* from the abapGit source via the existing `abap_serializer.py generate --format ...`
for systems without abapGit installed. They are never edited by hand.

## 3. Package layout

Standard abapGit repository layout. Root `.abapgit.xml` declares `STARTING_FOLDER=/src/` and
`FOLDER_LOGIC=PREFIX`.

```
model-library/
├── .abapgit.xml                     # repo descriptor (starting folder, folder logic, ignores)
├── README.md                        # catalog + how-to-generate
├── manifest.json                    # template registry (tokens, category, module) — see §5
├── src/
│   ├── package.devc.xml             # $ZMODEL (or ZMODEL) package metadata
│   ├── core/
│   │   ├── zcx_tmpl.clas.abap                 + .clas.xml   exception (ZCX_STATIC_CHECK base)
│   │   ├── zif_tmpl_handler.intf.abap         + .intf.xml   handler contract
│   │   ├── zcl_tmpl_handler_abstract.clas.abap + .clas.xml  abstract dispatch base
│   │   └── zcl_tmpl_bapi_wrapper.clas.abap     + .clas.xml  BAPI call + BAPIRET2 + commit
│   ├── http/
│   │   └── zcl_tmpl_http_handler.clas.abap     + .clas.xml  IF_HTTP_EXTENSION skeleton
│   ├── module/
│   │   └── zcl_tmpl_handler.clas.abap          + .clas.xml  concrete handler (per-module model)
│   ├── report/
│   │   ├── ztmpl_alv_report.prog.abap          + .prog.xml  ALV OO report
│   │   └── ztmpl_bdc_program.prog.abap         + .prog.xml  BDC / call transaction
│   ├── function/
│   │   └── zfg_tmpl.fugr.abap                   + .fugr.xml  FUGR + RFC-enabled FM
│   ├── ddic/
│   │   ├── ztmpl_config.tabl.abap              + .tabl.xml   config-registry table pattern
│   │   └── ztmpl_log.tabl.abap                 + .tabl.xml   log table pattern
│   ├── rap/
│   │   └── zi_tmpl_entity.*                                  CDS + BDEF + behavior (managed)
│   └── test/
│       └── zcl_tmpl_unit_test.clas.abap        + .clas.xml  FOR TESTING skeleton
```

Filenames follow abapGit convention exactly: `<objname>.<type>.abap` for source,
`<objname>.<type>.xml` for metadata. Classes may add `.clas.locals_def.abap`,
`.clas.locals_imp.abap`, `.clas.testclasses.abap` when needed. This matches the two-file output
`abap_serializer.py` already emits (`generate_abapgit`, envelope `serializer="LCL_OBJECT_CLAS"`).

## 4. Placeholder / naming convention

Two substitution mechanisms, chosen so **the library stays valid, lint-clean ABAP** (every base
object compiles and passes `abap:lint` as-is — that is what makes it a trustworthy reference).

### 4a. Identifier tokens (find/replace) — for object names and code identifiers

The literal token **`TMPL`** inside any identifier is the rename slot. It is valid ABAP, so the
raw template activates and lints.

| Template identifier | Generated (token `MM`) |
|---|---|
| `ZCL_TMPL_HANDLER` | `ZCL_MM_HANDLER` |
| `zif_tmpl_handler` | `zif_mm_handler` |
| `ZFG_TMPL` | `ZFG_MM` |

The generator does a **word-boundary, case-preserving** replace of `TMPL`/`tmpl` → the target
token across both filenames and file contents. Case preservation: `TMPL`→`MM`, `tmpl`→`mm`.

### 4b. Value slots (`{{TOKEN}}`) — for literals and config seeds only

`{{NAME}}` slots are used **only where the double brace does not break syntax** — inside string
literals, comments, and JSON/config seed files. This reuses the engine already in
`template_repo.py` (`PLACEHOLDER_RE = \{\{(\w+)\}\}`).

```abap
" valid ABAP — {{BAPI_NAME}} lives inside a string literal, lints clean
CALL FUNCTION '{{BAPI_NAME}}'          " default at gen time; e.g. BAPI_MATERIAL_SAVEDATA
```

Slots that must appear in *code position* (not a literal) are declared in the manifest as
find/replace pairs instead — never as `{{}}` in executable statements.

## 5. Manifest schema

`manifest.json` — one entry per template object. Consumed by the generator; validated in CI.

```json
{
  "version": "1.0",
  "templates": [
    {
      "id": "handler-concrete",
      "title": "Module dispatch handler",
      "category": "handler",
      "path": "src/module/zcl_tmpl_handler.clas.abap",
      "objectType": "CLAS",
      "rename_token": "TMPL",
      "requires": ["zif_tmpl_handler", "zcl_tmpl_handler_abstract", "zcx_tmpl"],
      "value_slots": [
        { "name": "MODULE",   "required": true,  "example": "MM" },
        { "name": "BAPI_NAME","required": false, "example": "BAPI_MATERIAL_SAVEDATA" }
      ],
      "golden_rules": ["commit-after-bapi-return", "bapiret2-full-scan"],
      "lint": "clean"
    }
  ]
}
```

`requires` drives dependency-ordered generation (same idea as `CREATE_ORDER` in
`zrouter_deploy_http.py` / `deploy_all.py`). `golden_rules` are checklist IDs asserted by
review, not code.

## 6. Golden-pattern rules baked into templates

Each base object is authored to satisfy these — the exact v4 flaws from `zrouter-v4-analysis`,
inverted:

| Rule ID | Rule | Where |
|---|---|---|
| `commit-after-bapi-return` | `COMMIT WORK`/`BAPI_TRANSACTION_COMMIT` runs **after** BAPIRET2 is checked, never in the logger | bapi_wrapper, handler_abstract |
| `bapiret2-full-scan` | Loop all `RETURN` rows for `E`/`A`, not just row 1 | bapi_wrapper |
| `nested-table-deser` | Deserialize into **DDIC structures**, not inline TYPES, so `/ui2/cl_json` fills nested tables | handler_abstract |
| `no-batch-double-commit` | Batch commits once; item handlers do not self-commit | handler_abstract, batch |
| `config-cache-refresh` | Config cache has an explicit invalidation, not `IS INITIAL`-only load | config |
| `auth-check-first` | `AUTHORITY-CHECK` before any work; documented auth object | http_handler |
| `no-eval-expression` | No `GENERATE SUBROUTINE POOL` / dynamic exec of request data | all |

CI gate (`abap:lint` + ATC via `abap-code-review`) runs against `model-library/src/**` so the
library can never regress to non-compiling or flawed templates.

## 7. Generator workflow

```
1. select template        manifest.json → pick id (e.g. handler-concrete) + its requires[]
2. resolve tokens         rename TMPL → MODULE token (§4a); fill {{value_slots}} (§4b)
3. write instance         emit abapGit files into a target package (e.g. deploy/split2/ or a new pkg)
4. (optional) export      abap_serializer.py generate --format nugg   # legacy systems
5. install                ZABAPGIT pull  (or deploy_all.py via ADT REST for objects it supports)
6. seed + wire            create ZROUTER_CONFIG rows; SICF/SU21/PFCG per install runbook
```

Steps 1–4 are offline and scriptable (extend `template_repo.py`). Steps 5–6 touch the SAP
system and stay manual/gated.

## 8. Consolidation plan (migration)

1. **Promote** `deploy/split2` (the complete v5 set) to seed the library: rename its `ZROUTER`/
   module identifiers to `TMPL` tokens where they are meant to be parameterized; keep concrete
   ZROUTER objects generatable from the templates.
2. **Fold in** the 4 loose `templates/*.abap` (repl, code_search, db_tables, dispatch) as model
   objects under the right `src/` subfolder, or drop if superseded.
3. **Retire** `deploy/split` (v4, incomplete), `deploy/zrouter` (uppercase dup),
   `deploy/zrouter_export` (xml dup) → move to `deploy/legacy_v4/` (non-destructive) then delete
   after the library reproduces them.
4. **Regenerate** `deploy/{abapgit,nugg,xml}` demos from the library instead of hand-maintaining.
5. **Add the missing DDIC** `ztmpl_config` / `ztmpl_log` templates — these are the tables the
   live ZROUTER runtime needs and that no copy currently defines (see peer-review finding A/§ DDIC).

## 9. abapGit metadata specifics

- Root `.abapgit.xml`: `STARTING_FOLDER=/src/`, `FOLDER_LOGIC=PREFIX`, `MASTER_LANGUAGE=E`, with
  an `IGNORE` list for non-object files (`manifest.json`, `README.md`, docs).
- Per-object `.xml`: `abapGit version="v1.0.0" serializer="LCL_OBJECT_<TYPE>"` envelope with the
  object's `VSEO*`/`PROGDIR`/`DD02V` metadata block — the shape `abap_serializer.py._abapgit_meta_xml`
  already generates. The serializer's output is a valid approximation; before first real
  `ZABAPGIT` pull, one round-trip test per object type confirms the metadata is accepted.
- Package `package.devc.xml`: declares `$ZMODEL` (local/`$TMP`-safe) or `ZMODEL` (transportable).
  Default `$ZMODEL` so the library imports without a transport request on locked systems.

## 10. Open decisions

1. **Package namespace:** `$ZMODEL` (local, no transport, matches the `$TMP` safety restriction in
   `zrouter-deployment-pipeline`) vs `ZMODEL` (transportable). Recommend `$ZMODEL` for the library
   itself; generated instances go to the caller's real package.
2. **Repo boundary:** keep `model-library/` inside this repo, or split to its own git repo that
   `ZABAPGIT` points at directly. In-repo first; extract later if it grows.
3. **Coverage depth for v1:** minimum viable set = core (exception, interface, abstract,
   bapi_wrapper) + one concrete handler + http_handler + config/log DDIC + unit test. RAP/ALV/BDC
   templates in a later pass.

## 11. Verification (once built)

- `abap:lint` and `python scripts/abap_serializer.py extract` round-trip on every `src/` object.
- Generate one concrete module (e.g. MM) from templates; diff against `deploy/split2` — should be
  functionally equivalent.
- `ZABAPGIT` dry-run pull on a sandbox client; confirm all object types serialize/deserialize.
- `python scripts/validate_catalog.py` extended to validate `manifest.json` ↔ `src/` consistency.
