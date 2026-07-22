# SAP Code Agents

Codebase analysis for SAP ABAP: answers three questions about any ingested custom
ABAP codebase, with every claim backed by verifiable evidence. (The product name
is a single constant in `lib/config.ts`.)

1. **What does our custom code actually do?** — auto-generated documentation per object
2. **What is still in use?** — usage stats + dependency graph → retirement list
3. **What breaks on S/4HANA?** — evidence-tiered incompatibility findings

Stack: Next.js (App Router, TypeScript) · Supabase (Postgres) · Anthropic API ·
[@abaplint/core](https://github.com/abaplint/abaplint) · deployed on Vercel.

## Core principles

- **No fabrication.** The agent only states what it retrieved via tools; unresolved
  object names are visibly marked.
- **Numbers come from SQL.** Every count/percentage is computed by the database,
  never by the LLM.
- **Evidence tiers.** Tier 1 = machine-verified by a deterministic validator,
  Tier 2 = evidence-linked (verbatim citation, interpretation needs expert review),
  Tier 3 = unverified observation (collapsed, never in headline numbers).
- **Simulated data is labeled** everywhere it appears.
- **Diagrams are computed** from graph edges, never narrated by the LLM.

## Setup

```bash
npm install
cp .env.example .env.local     # fill in keys — see .env.example comments
npm run migrate                # apply lib/db/migrations/*.sql (tracked in schema_migrations)
npm run seed-rules             # upsert the S/4HANA incompatibility rules (lib/rules/rules.json)
npm run seed -- --workspace abapGit --source https://github.com/abapGit/abapGit
npm run gen-usage              # regenerate fixtures/usage.csv (deterministic, fixed seed)
npm run seed -- --workspace example-manufacturer --source fixtures
npm run report                 # migration report batch job (both systems)
npm run dev                    # http://localhost:3000
```

Required env vars (see `.env.example`): `ANTHROPIC_API_KEY`, `DATABASE_URL`
(Postgres, full DDL rights), plus the Supabase keys for hosted deployments.
Never commit secrets. Verify with `npm test` (validators + seeder smoke test +
report-quality units), `npm run parse-proof` (parser gate), and
`npm run benchmark` (agent acceptance questions).

## Public release

This repository is public and has been cleaned for release: no API keys,
credentials, or connection strings exist in any tracked file or anywhere in the
git history, and `.env.local` was never committed (`.gitignore` blocks all env
files except `.env.example`, which contains placeholders only). Released as-is
under the MIT License (see `LICENSE`). It ships two example systems (the public
abapGit repo and a synthetic `example-manufacturer` fixture set) and needs no
proprietary SAP data
to run — copy `.env.example` to `.env.local`, supply your own Anthropic API key
and a Postgres/Supabase database, then follow the Setup steps above. All example
usage statistics are synthetic and labeled as such wherever they appear; no real
customer or SAP system data is included.

## Authentication & multi-tenancy

Every account belongs to exactly one **company**; all systems, chats,
reports and traces are company-scoped. Example systems are globally
readable (read-only, badged "example"); user-ingested systems are
company-private. There is **no self-registration** — accounts exist only
through invitations. Enforcement is two-layered: every API route checks
company membership server-side, and Row Level Security is ON for every table
(verified by `npm run test-tenancy`, which hits the API with two test users
and queries Postgres through the anon key as each of them).

### Operator: create a company

```bash
npm run create-company -- --name "<company name>" --admin-email admin@example.com
```

Prints an admin invite link (and attempts to send it via Supabase's mailer).
The invitee sets a password on the invite page and lands in the app; from
there, **Company settings** (sidebar footer → avatar menu, admins only) lets
them invite further members, revoke pending invitations, and remove members
(removal revokes access but keeps past chats). Roles: `admin` (invite/remove
members, delete systems), `member` (everything else).

### Supabase configuration

- Email auth **enabled**, self-signup **disabled** (`disable_signup: true`).
- Site URL `https://sap-code-agents.vercel.app`; redirect allowlist covers
  `/auth/callback`, `/invite/*`, `/reset-password` on production and
  `http://localhost:3000`.
- SMTP: not configured — Supabase's default mailer is heavily rate-limited,
  so invite emails may not arrive; the invite flow therefore always surfaces
  a **copyable invite link** in Company settings (and `create-company`
  prints it). Configure SMTP in Supabase → Auth → SMTP for real email
  delivery.
- The service-role key stays server-side only (seeder, background jobs,
  invitation acceptance); the browser only ever sees the anon key.

Password flows use Supabase Auth built-ins: forgot-password (neutral
confirmation, never reveals account existence), reset via emailed link, and
change-password in Profile settings (requires the current password).

## Ingesting a codebase

Two entrypoints share one pipeline (`lib/ingest/pipeline.ts`):

- **In-app**: the Connections page → Connect a system →
  paste a public HTTPS git URL. Ingestion runs as a chunked background job
  (`ingestion_jobs` table; clone → parse → graph → summaries) with a live
  progress screen; the clone uses isomorphic-git (no git binary needed on
  serverless). Guardrails: public HTTPS URLs only (no credentials), max
  3,000 ABAP files / 25 MB source (enforced before parsing), fewer than 5
  parseable ABAP files fails with "no ABAP sources found", one concurrent
  ingestion (further jobs queue), and a failed job persists nothing.
  Summaries are generated at ingestion time only for the first 800 objects
  by inbound-edge count; the rest are generated lazily on first access
  (search falls back to name matching meanwhile). User-ingested systems
  are badged with source URL + date and can be deleted (admin only).
- **CLI**:

```bash
npm run seed -- --workspace <name> --source <git-url-or-local-path>
```

Shipped systems:

- **abapGit** — the real [abapGit](https://github.com/abapGit/abapGit)
  repository (~1,900 files); no usage data (that state renders as
  "no usage data available").
- **example-manufacturer** — synthetic fixtures in [/fixtures](fixtures/) with a
  goods-movement narrative, dead objects, an enhancement, custom tables, and an
  RFC interface stub.

The seeder (`scripts/seed.ts`) parses every `.abap`/`.tabl.xml` file with
abaplint, extracts objects, call references (function / perform / class /
interface) and table accesses with verbatim evidence lines, then writes
everything to Postgres. Call targets that resolve to an object in the same
system get a `callee_id`; unresolved targets keep `callee_id = NULL` and stay
visibly marked. A traced Haiku pass (`claude-haiku-4-5-20251001`) writes one
summary per object into `objects.summary`, with token counts in `traces`.
Re-seeding under the same name replaces it (cascade delete + fresh insert). The
seeder prints a parse summary and this sanity block after every run (the
database schema and the `--workspace` seeder flag retain the original term
*workspace* for what the UI calls a system):

```sql
select count(*) from objects       where workspace_id = :ws;   -- objects
select count(*) from call_edges    where workspace_id = :ws;   -- edges (+ resolved)
select count(*) from table_accesses where workspace_id = :ws;  -- accesses
select count(*) from traces        where workspace_id = :ws and kind = 'summary';
```

## Synthetic usage model

Usage statistics for **example-manufacturer** are simulated and labeled as such on
every surface that shows them.

`npm run gen-usage` (`scripts/gen-usage.ts`) writes `fixtures/usage.csv`
deterministically — no hand-picked numbers:

```
call_count_24m = round( base(object_type) × (1 + 2 × inbound_edge_count) × (0.75 + 0.5 × rand) )
```

with `base(PROG) = 180`, `base(CLAS) = 900`, `rand` from a mulberry32 PRNG
seeded with `20260719 ⊕ hash(object_name)`, and `last_executed` a fixed-anchor
date (2026-07-18) minus a seeded 0–13 days. Objects marked `dead: true` in
`fixtures/manifest.json` are forced to `0` with no last-executed date;
non-executable types (INTF, TABL) get no row. Identical output on every run.

## Migration Risk Grade

Every object carries a deterministic **Migration Risk Grade**, derived exclusively from the persisted findings of the system's latest
finished report run by the SQL view `object_risk_grades` — recomputed
automatically per run, never stored, never LLM-assigned:

- **D** — at least one Tier-1 finding from a *severity-high* rule
- **C** — at least one Tier-1 finding, but none severity-high
- **B** — at least one Tier-2 finding and zero Tier-1 findings
- **A** — zero Tier-1 and Tier-2 findings
- **Ungraded** — the system has no finished report run yet (rendered as a
  muted "–", never as A)

Rule severity is seeded reference data in `lib/rules/rules.json`: **high** means
the construct is removed outright in S/4HANA (transaction, function module, or
functionality no longer available/filled — hard runtime failure or silently
wrong results); **medium** means the data model is replaced but compatibility
views cover transitional reads. This is not SAP's "Clean Core Level" or ATC —
it is a grade over this tool's own evidence-tiered findings.

## Hold-out fixture

Exactly one fixture object contains a *semantic* S/4HANA incompatibility that no
seeded regex validator matches (expected classification: Tier 2). To keep this an
honest test of whether the analysis generalizes beyond planted rule matches, that
fixture was authored only after the rules table and validators were frozen — it
is deliberately not covered by any rule written for it.

## Parse failures

Parser failures never block a seed run: the object is stored with
`parse_status='failed'` plus raw source, and the seeder prints a
parse-success-rate summary.

Current state for the shipped systems (see `docs/parse-failures.md`,
regenerated by `npm run parse-proof`): **abapGit 750/750 `.abap` files parse
(100%)**, and all 13 `example-manufacturer` fixture objects parse (the 13th is
the semantic hold-out object, authored after the rules freeze) — so both
shipped systems currently have zero failed objects. The failure path is still
exercised by unit tests.

## Architecture

Three layers per system:

1. **Ingestion & graph** (build-time, deterministic) — abaplint parse → objects,
   call edges, table accesses with evidence lines → Postgres; one traced Haiku
   summary pass per object.
2. **Agent** (runtime, selective) — Anthropic tool-use loop with four
   system-scoped tools (`search_objects`, `read_object`, `where_used`,
   `get_usage_stats`); max 10 tool calls per query; streamed to the UI.
3. **Deliverables** (runtime, exhaustive) — migration report batch job with a
   validator pass assigning evidence tiers; retirement list is pure SQL.

### Where live SAP extraction would plug in

Ingestion is file-based (git URL or local folder) by design. In a production
deployment, Layer 1 is where a live extraction path from an SAP system — e.g.,
RFC-based code retrieval — would replace the file-based source. Nothing else in
the system would change.

## Repository layout

```
/app             Next.js App Router pages & API routes
/components      shared UI components (shell, layout, primitives)
/lib             agent loop, ingest pipeline, validators, diagrams, db, parser
/scripts         CLI entrypoints (seeder, migrations, report job, benchmark)
/fixtures        example-manufacturer fixture objects + manifest.json + usage.csv
/benchmark       questions.json — agent acceptance questions
/tests           validator unit tests + seeder smoke test (vitest)
/docs            generated evidence (parse-failure report)
/design-guidance standalone UI scaffold: palette, components, layout reference
```

Each folder has its own `README.md` describing its contents in more detail.
