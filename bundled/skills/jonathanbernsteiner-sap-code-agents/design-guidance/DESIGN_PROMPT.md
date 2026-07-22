# Design guidance — handoff prompt

This folder is the design source of truth for the product's frontend. Paste the
block below to the AI/coding assistant in your new project. It tells it exactly
how the design works so it matches this scaffold when building pages.

---

You are building a web app on **Next.js (App Router) + Tailwind CSS**.
Follow this design system exactly. The base layout components already exist in
`components/` and `lib/navigation.ts` — reuse them, do not restyle them.

**Brand**
- Main / accent color: `#F04E0D` orange (used for active + hover states,
  primary buttons, key icons). Darker press state / small accent text:
  `#CC420B`.
- Sidebar background (dark rail) and tooltips: near-black `#171412`.
- App background: `#F6F4F1` / surface `#FAF8F5`; cards are white `#FFFFFF`.
  Warm cream tint `#FCEDE4` for subtle brand-tinted surfaces (dropzones,
  highlights) — use sparingly.
- Borders: `#E8E2DB`. Primary text `#1B1817`, secondary text `#6E6660`,
  muted `#A49C95`.
- The overall feel is warm and minimal: black + white + warm grays, orange
  only where it matters. **No blues or cool grays.**
- Font: **DM Sans** (already imported in `app/globals.css`).
- Corner radius: 8px for buttons/inputs, 12px for cards.

**Layout (fixed, do not change)**
- A **56px-wide icon sidebar** fixed on the left (`components/layout/Sidebar.tsx`),
  near-black. Nav items are icon-only 40×40 buttons that fill with `#F04E0D` on
  hover/active; a small dark tooltip label appears to the right on hover (200ms
  delay) and hides on mouse-leave.
- A **56px-tall top bar** fixed across the top (`components/layout/TopBar.tsx`):
  page title on the left, centered search box, avatar on the right.
- Page content sits inside `<AppShell>` with `margin-left: 56px; padding-top: 56px`.
- Sidebar items live in `lib/navigation.ts`. To add a page: add an entry there,
  add its icon to `iconMap` in `Sidebar.tsx`, and create `app/<path>/page.tsx`.

**Two-level (section) layout — used by Settings**
- Reuse `components/layout/SectionSidebar.tsx`: a 240px inner sidebar, warm-gray
  background, uppercase heading, active item = white card with a 2px `#F04E0D`
  left border + subtle shadow. Use this pattern for any page that needs sub-tabs.

**Components to reuse**
- `components/ui/Card.tsx` — white rounded card (radius 12, 1px `#E8E2DB` border).
- `components/ui/PagePlaceholder.tsx` — title + skeleton blocks; use for any page
  not yet built.
- `components/ui/Select.tsx` — dropdown. **Never use a native `<select>`** (the
  OS popup overlaps the trigger and uses system-blue highlights). This component
  opens a white panel *below* the trigger (radius 10, `#E8E2DB` border, soft
  shadow), full trigger width; the selected option shows an orange `#F04E0D`
  check, hover rows are `#F6F4F1`. Use it for every dropdown so they all look
  and behave the same.
- Icons: `lucide-react`.

**Rules**
- Match the existing spacing, colors, radii, and font. Do not introduce a
  component library (no shadcn/MUI) — keep the hand-rolled Tailwind + inline-style
  approach already used in `components/`.
- Every new page must render inside `<AppShell>` (it already wraps everything via
  `app/layout.tsx`).

Now build: **[describe the page or feature you want here]**.

---

## How to use this prompt

1. Copy everything between the two `---` lines above into your new project's AI.
2. Replace the last line's `[describe the page...]` with what you actually want,
   e.g. "Build the Overview page with 4 stat cards and a recent-activity list."
3. Because the layout components are already in the repo, the AI will slot new
   pages into the existing sidebar/topbar design instead of reinventing it.
