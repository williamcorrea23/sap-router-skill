# /scripts

Command-line entrypoints, all run through `tsx --env-file=.env.local` and all
thin wrappers around the shared logic in `lib/`.

## Contents

- `seed.ts` — workspace seeder: clone or read a source, parse every `.abap` and
  `.tabl.xml` file, write objects/edges/table accesses, then a summary pass.
  Re-seeding a workspace name replaces it.
- `migrate.ts` — applies `lib/db/migrations/*.sql` in filename order, each in
  its own transaction, tracked in `schema_migrations`.
- `seed-rules.ts` — idempotent upsert of `lib/rules/rules.json` into
  `incompatibility_rules`.
- `gen-usage.ts` — deterministic synthetic usage generator; CLI over
  `lib/ingest/simulated-usage.ts`.
- `report.ts` — migration report batch job; wrapper around `lib/report/job.ts`.
  Fails the process if a displayed Tier-1 finding does not re-validate against
  its cited evidence.
- `parse-proof.ts` — clones abapGit into `.seed-cache/`, parses every `.abap`
  file and reports the success rate (source of `docs/parse-failures.md`).
- `benchmark.ts` — runs `benchmark/questions.json` through the real agent loop
  and machine-checks the expected behaviour.
- `create-company.ts` — operator setup: create a company plus its first admin
  invitation, and print the invite link.
- `backfill-target-kind.ts` — one-off backfill of `call_edges.target_kind` for
  workspaces ingested before migration 018, re-derived from stored source.

## Commands

```bash
npm run migrate
npm run seed -- --workspace <name> --source <git-url-or-local-path>
npm run seed-rules
npm run gen-usage
npm run report
npm run parse-proof
npm run benchmark
npm run create-company -- --name "<company name>" --admin-email admin@example.com
npm run backfill-target-kind
```
