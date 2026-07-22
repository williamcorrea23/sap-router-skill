# /fixtures

Synthetic ABAP source for the `example-manufacturer` example workspace. Nothing
here comes from a real SAP system or a real customer: the objects, the
narrative and the usage numbers are all invented for demonstration and
regression testing, and the usage data is labeled as simulated on every surface
that displays it.

## Contents

- `manifest.json` — the workspace definition: the goods-movement narrative,
  and one entry per object with `name`, `category`
  (`abap` / `interface` / `enhancement` / `custom_table`), `dead` flag and a
  description.
- `src/` — 13 fixture files: `.abap` sources and `.tabl.xml` table definitions.
  They include a core movement service, an RFC inbound stub, reports over
  KONV/VBUK and BSID/BSAD, a user-exit include, two custom tables, and two
  legacy programs marked `dead: true`.
- `usage.csv` — generated, not hand-written: `object_name,call_count_24m,
  last_executed`. Objects marked dead are forced to `0` with no last-executed
  date; non-executable types (INTF, TABL) get no row.

`ZCL_GM_MATNR_COMPAT` is the hold-out object: it carries a semantic S/4HANA
incompatibility that no seeded regex validator matches, and was authored only
after the rules and validators were frozen (see the root README).

## Commands

```bash
npm run gen-usage                                             # regenerate usage.csv (deterministic, fixed seed)
npm run seed -- --workspace example-manufacturer --source fixtures
```

The generator model is documented under "Synthetic usage model" in the root
README and implemented in `lib/ingest/simulated-usage.ts`.
