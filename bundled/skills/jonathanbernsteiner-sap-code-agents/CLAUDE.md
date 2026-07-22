# Engineering conventions

Next.js (App Router, TypeScript) · Postgres (via `pg`) · @abaplint/core.

## Core principles (hard requirements)

- **No fabrication.** State only what tools/queries retrieved; mark unresolved
  object names visibly rather than guessing.
- **Numbers come from SQL**, never from the LLM.
- **Evidence tiers**: Tier 1 machine-verified by a deterministic validator,
  Tier 2 evidence-linked, Tier 3 collapsed and never in headline numbers.
- **Simulated data is labeled** everywhere it appears.
- **Diagrams are computed** from graph edges; the LLM never writes Mermaid.

## Commands

- `npm run dev` / `npm run build` / `npm test` (vitest) / `npm run lint`
- `npm run migrate` — apply `lib/db/migrations/*.sql` (tracked in `schema_migrations`)
- `npm run seed -- --workspace <name> --source <git-url-or-path>`

## Environment

- `.env.local` is the local source of truth (`ANTHROPIC_API_KEY`, Supabase keys,
  `DATABASE_URL`). Never commit it. Scripts load it via tsx `--env-file`.
- DB access: `pg` over `DATABASE_URL` (full DDL rights). Prefer direct SQL.

## UI

All frontend follows `design-guidance/` (palette: warm minimal, orange #F04E0D
accent only for active/primary, no blues/cool grays). Copy its components;
don't invent new styles.
