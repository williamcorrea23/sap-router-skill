# Model Library

A versionable abapGit package of **golden ABAP base objects** — parameterized skeletons you
clone, rename, fill, and deploy. Design rationale: [../docs/model-library-design.md](../docs/model-library-design.md).

This is a prototype (design doc §11). It ships a self-contained, lint-clean starter set of
three templates plus the tooling to convert the existing v5 ZROUTER objects into abapGit layout.

## Layout

```
model-library/
├── .abapgit.xml                     abapGit repo descriptor (STARTING_FOLDER=/src/)
├── manifest.json                    template registry (tokens, deps, golden rules)
├── README.md
└── src/
    ├── package.devc.xml             $ZMODEL package
    ├── zcx_tmpl.clas.abap + .xml    exception (CX_STATIC_CHECK base)
    ├── zif_tmpl_handler.intf.abap + .xml   handler contract
    └── zcl_tmpl_handler.clas.abap + .xml   concrete handler, golden BAPI pattern
```

## Placeholder convention

Two substitution mechanisms, chosen so every template stays valid, activatable ABAP:

- **`TMPL` in identifiers** — the rename slot. `ZCL_TMPL_HANDLER` → `ZCL_MM_HANDLER`.
  Case-preserving find/replace (`TMPL`→`MM`, `tmpl`→`mm`).
- **`{{TOKEN}}` in literals/comments only** — value slots (`{{MODULE}}`, `{{ENTITY}}`,
  `{{BAPI_NAME}}`). Never placed in executable code position, so `{{}}` never breaks syntax.

## Generate a concrete instance

```bash
python scripts/build_model_library.py generate \
  --template handler-concrete --token MM \
  --set MODULE=MM --set ENTITY=MATERIAL --set BAPI_NAME=BAPI_MATERIAL_SAVEDATA
# -> deploy/generated/mm/  (zcl_mm_handler.clas.abap, zif_mm_handler.intf.abap, zcx_mm.clas.abap)
```

The generator renames `TMPL`→`MM` across filenames and source, fills the `{{...}}` value slots,
and stamps the template plus its declared dependencies.

## Convert the existing v5 ZROUTER objects to abapGit

```bash
python scripts/build_model_library.py convert-split2
# -> deploy/abapgit_full/  (.abapgit.xml + src/ with .clas/.intf/.prog + .xml sidecars)
```

Classes, interfaces, and programs are auto-converted. DDIC tables (`.tabl`) and function groups
(`.fugr`) are reported as deferred — they need object-specific metadata (DD03P field lists,
FUGR includes) and are the next conversion pass.

## Install on SAP

1. `ZABAPGIT` → new online (or offline ZIP) repo pointing at this folder.
2. Pull → objects created in package `$ZMODEL`.
3. Activate. `$ZMODEL` is a local package, so no transport request is required on locked systems.

For systems without abapGit, export to `.nugg` / ZDOWNLOAD-XML:

```bash
python scripts/abap_serializer.py generate \
  --source model-library/src/zcl_tmpl_handler.clas.abap \
  --name ZCL_TMPL_HANDLER --type CLAS --format nugg --output deploy/nugg
```

## Golden rules baked into `handler-concrete`

The concrete handler is authored to satisfy the correctness rules that the v4 ZROUTER violated
(see design doc §6): `commit-after-bapi-return`, `bapiret2-full-scan`, `no-batch-double-commit`,
`no-eval-expression`. New handlers generated from it inherit the correct pattern by default.

## Validate

```bash
python scripts/build_model_library.py validate    # manifest <-> files, sidecar convention
```
