# /lib

Shared server-side logic (plus a few client-safe helpers). Everything the app,
the CLI scripts and the tests have in common lives here — one code path,
several entrypoints.

- `agent/` — Anthropic tool-use loop, the four workspace-scoped tools, system prompt
- `validators/` — one deterministic validator per Tier-1-eligible incompatibility rule
- `diagram/` — deterministic edges → Mermaid conversion; the LLM never writes Mermaid
- `db/` — Supabase client, schema SQL, query helpers
- `parser/` — abaplint-based object/call/table-access extraction, shared by seeder
- `ingest/` — the shared ingestion pipeline used by both `scripts/seed.ts` and the
  in-app background job: `pipeline.ts`, `jobs.ts`, `git.ts` (isomorphic-git clone),
  `worker-auth.ts`, `simulated-usage.ts` (the deterministic usage model)
- `report/` — the migration report job and its quality pipeline: `job.ts`,
  `data.ts`, `dedupe.ts`, `claims.ts`, `suppress.ts`, `summary.ts`,
  `methodology.ts`, `finding-title.ts`, `render.ts` (Markdown/CSV), `pdf.ts`
- `rules/rules.json` — the seeded S/4HANA incompatibility rules with severities
- `auth/` — Supabase auth helpers (`server.ts`, `client.ts`, `admin.ts`)
- `chat/store.ts` — persistent, workspace-scoped chat sessions and messages

Root-level modules:

- `config.ts` — product name/description, single source of truth
- `grade-scale.ts` — Migration Risk Grade palette and meanings, shared by the UI
  components and the server-side PDF renderer
- `empty-values.ts` — the distinct tokens for values the product does not have,
  so a number that could not be computed is never rendered as a real one
- `source-links.ts` — provenance links back to a workspace's public git source
- `navigation.ts` — sidebar items (icon names must exist in the `iconMap` in
  `components/layout/Sidebar.tsx`)

`db/migrations/*.sql` is applied in filename order by `npm run migrate` and
tracked in `schema_migrations`; `npm run seed-rules` upserts `rules/rules.json`.
