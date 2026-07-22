# /components

React components shared across the App Router pages. Styling follows
`design-guidance/` (warm minimal palette, orange `#F04E0D` for active/primary
only); components are copied from that scaffold rather than invented here.

## Layout and shell

- `AppShell.tsx` — fixed 56px icon sidebar + 56px top bar, content offset.
- `layout/Sidebar.tsx`, `layout/TopBar.tsx`, `layout/SectionSidebar.tsx`,
  `layout/AccountMenu.tsx` — the shell pieces; sidebar items come from
  `lib/navigation.ts` and icon names must match the `iconMap` in `Sidebar.tsx`.
- `WorkspaceSwitcher.tsx`, `LegacyWorkspaceRedirect.tsx` — workspace selection
  and resolution of pre-restructure deep links.

## Product-specific

- `RunSummary.tsx` — one run-summary block shared by the overview and report
  pages.
- `PipelineStages.tsx` / `ReportPipelineCard.tsx` — the horizontal stage view,
  used by both the ingestion progress screen and the report-run card.
- `MermaidDiagram.tsx` — renders Mermaid text computed server-side in
  `lib/diagram`; the LLM never writes diagram source.
- `Markdown.tsx` — markdown rendering (react-markdown + remark-gfm).
- `chat/ChatSidebar.tsx` — chat session list.

## UI primitives (`ui/`)

`Card.tsx`, `CollapsibleCard.tsx`, `DataTable.tsx`, `Select.tsx`,
`formStyles.ts`, plus `GradeBadge.tsx` and `GradeBar.tsx`, which only render
the Migration Risk Grade computed by the `object_risk_grades` SQL view.

## Hooks

`useWorkspace.ts`, `useProfile.ts`, `useReportRun.ts` (report-run polling and
stage state). `auth/form.tsx` holds the shared auth form.
