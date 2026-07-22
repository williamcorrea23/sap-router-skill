# /tests

Required by §12:

- Validator unit tests: per Tier-1-eligible rule, ≥1 positive fixture
  snippet and ≥1 near-miss negative snippet.
- Seeder smoke test.

UI tests are explicitly not required. Run with `npm test` (vitest).

## Files

- `validators.test.ts` — the per-rule validator suite described above.
- `seeder.test.ts` — seeder smoke test.
- `report-quality.test.ts` — units for the report quality pipeline
  (dedupe, claim-evidence check, suppression).
- `dependency-classification.test.ts` — call-edge classification.
- `derive-category.test.ts` — object category derivation.
- `ingest-name.test.ts` — object naming during ingestion.
- `source-links.test.ts` — provenance link construction.
- `tenancy.test.ts` — two-layer tenancy check: hits the API with two test users
  and queries Postgres through the anon key as each of them, verifying Row
  Level Security. Needs a live database and the Supabase keys.

## Commands

```bash
npm test              # vitest run over tests/**/*.test.ts
npm run test-tenancy  # tenancy.test.ts only
```

Config is `vitest.config.ts` at the repository root.
