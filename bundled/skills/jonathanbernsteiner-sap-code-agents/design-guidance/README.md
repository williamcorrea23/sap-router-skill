# Design Guidance — portal scaffold

**This folder is the single source of truth for frontend design.** Any UI built
for this product should follow the colors, layout, spacing, and components
defined here. It's a self-contained Next.js (App Router) + Tailwind scaffold —
everything is design/layout only; pages are placeholders you fill in later.

When building a new frontend, copy the components/palette from here (or paste
`DESIGN_PROMPT.md` into your AI assistant) instead of inventing new styles.

## Relationship to the rest of the repository

This folder is a **standalone reference scaffold**, not part of the application
build. It has its own `package.json`, `tsconfig.json`, `tailwind.config.ts`,
`postcss.config.js` and `next.config.js`, its own (older) Next/React versions,
and its own `node_modules` when installed. The root project excludes it from
TypeScript (`tsconfig.json`), linting (`eslint.config.mjs`) and tests
(`vitest.config.ts`), so nothing here ships to production. The real application
lives in `/app`, `/components` and `/lib`, which follow the rules below.

## Brand palette

| Role | Hex |
|---|---|
| Accent (active states, fills, key icons) | `#F04E0D` |
| Accent pressed / small accent text | `#CC420B` |
| Ink — sidebar rail, tooltips, emphasis | `#171412` |
| Primary text | `#1B1817` |
| Secondary text | `#6E6660` |
| Muted text / icons | `#A49C95` |
| Borders | `#E8E2DB` |
| App background | `#F6F4F1` |
| Surface (search box, inputs) | `#FAF8F5` |
| Brand cream tint (dropzones, subtle highlights) | `#FCEDE4` |
| Cards | `#FFFFFF` |

The look is warm and minimal: black + white + warm grays everywhere, orange
only where it matters (active nav, key icons, primary actions). Don't
introduce blues or cool grays.

## What's inside

- **Icon sidebar** — fixed, 56px wide, near-black (`#171412`). Icon buttons
  highlight in the accent orange on hover/active and a **tooltip label appears
  on hover** (200ms delay) and disappears when you move away.
- **Top bar** — fixed, 56px tall, page title + centered search box + avatar.
- **Pages** — Overview (homepage), Page Two, Page Three, Upload, Settings.
- **Settings** — two-level layout: a 240px section sidebar with tabs, each
  showing placeholder content.
- **Brand color** — `#F04E0D` (change once in `tailwind.config.ts` +
  the components that use it inline; see "Change the brand color" below).

## Run it

```bash
npm install
npm run dev
# open http://localhost:3000  → redirects to /overview
```

## File map

```
app/
  layout.tsx          # wraps every page in <AppShell>
  page.tsx            # "/" redirects to /overview
  overview/page.tsx   # homepage (placeholder)
  page-two/page.tsx   # placeholder
  page-three/page.tsx # placeholder
  upload/page.tsx     # placeholder drop zone
  settings/page.tsx   # renders <SettingsShell>
  globals.css         # fonts + scrollbar
components/
  AppShell.tsx            # sidebar + topbar + content offset
  layout/Sidebar.tsx      # the 56px icon rail + hover tooltips
  layout/TopBar.tsx       # top bar
  layout/SectionSidebar.tsx # reusable 2nd-level sidebar
  layout/SettingsShell.tsx  # settings tabs + placeholder content
  ui/Card.tsx
  ui/PagePlaceholder.tsx  # reusable "title + skeleton blocks" body
lib/
  navigation.ts       # <-- edit sidebar items here
```

## Add / rename a sidebar page

1. Add an entry to `lib/navigation.ts` (`key`, `label`, `path`, `icon`).
2. If you used a new icon name, import it and add it to `iconMap` in
   `components/layout/Sidebar.tsx`.
3. Create `app/<path>/page.tsx`.

## Change the brand color

The brand color `#F04E0D` lives in:
- `tailwind.config.ts` → `colors.accent` (plus `accent-deep`, `ink`, `cream`)
- inline in `components/layout/Sidebar.tsx` (active/hover background, logo)
- inline in `components/layout/SectionSidebar.tsx` (active left border)
- inline in `app/upload/page.tsx` and `components/layout/SettingsShell.tsx`

Find/replace `#F04E0D` across the project to change it everywhere.
