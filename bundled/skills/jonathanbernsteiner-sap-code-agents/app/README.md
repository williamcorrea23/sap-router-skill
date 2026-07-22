# /app

The Next.js App Router tree: all pages and all HTTP API routes. Server
Components fetch through `lib/`; there is no separate backend service.

## Route groups

- `(app)/` — the authenticated application. `layout.tsx` wraps everything in
  `components/AppShell` (icon sidebar + top bar). Contains the workspace-scoped
  section `w/[id]/` (workspace home, `objects`, `overview`, `report`), the
  chat page, `workspaces/` and `workspaces/new`, `rules/`, `connections/`,
  `ingest/[id]/` (live ingestion progress), and `settings/` including
  `settings/company`. The top-level `overview/`, `objects/` and `report/`
  pages serve pre-restructure deep links and resolve to a workspace.
- `(auth)/` — unauthenticated pages, rendered without the app shell:
  `login`, `invite/[token]`, `forgot-password`, `reset-password`.
- `auth/callback/route.ts` — Supabase auth code exchange.

## API routes (`app/api/`)

- `chat/` — streamed agent responses (`route.ts`) plus session CRUD under
  `chat/sessions/`.
- `report/` — report data, `report/run` (start a run), `report/export`.
- `ingest/` — start an ingestion, poll `ingest/jobs/[id]`, and the chunked
  worker endpoint `ingest/process`.
- `objects/`, `object/`, `overview/`, `workspaces/`, `rules/` — read endpoints
  backing the pages.
- `company/*`, `invitations/*`, `profile/*` — tenancy, invitations, profile.

Every API route checks company membership server-side; Row Level Security is
the second layer (see the root README). Also here:
`layout.tsx` (root layout) and `globals.css`; session routing lives in
`middleware.ts` at the repository root.

## Commands

```bash
npm run dev      # next dev
npm run build    # next build
npm run lint     # eslint .
```
