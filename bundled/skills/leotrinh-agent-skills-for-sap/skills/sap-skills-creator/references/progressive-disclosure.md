# Progressive Disclosure

Load this file when deciding where each piece of skill content should
live. Progressive disclosure keeps the metadata short, the main
instructions focused, and the detailed material available on demand.

## Three Tiers

Every skill has three loading tiers.

### Tier 1 — Metadata

Loaded before the body of `SKILL.md`. Controls activation.

- `name`
- `description`
- `license`
- `compatibility`
- `metadata`

Keep this tier terse. Description quality dominates activation quality.

### Tier 2 — Main instructions

The body of `SKILL.md`. Loaded once the skill activates.

- Purpose.
- When to use, when not to use.
- Core principles.
- Operating modes.
- Workflow phases and stop conditions.
- Output contract.
- Completion checklist.
- Links into the resource tier.

Target 300–450 lines. Hard limit 500 lines. When a section grows past 60
lines it is usually a candidate for extraction.

### Tier 3 — Resources

Loaded on demand, only when the relevant phase runs.

- `references/*.md` — detailed technical documentation.
- `assets/*` — templates, schemas, examples, static files.
- `scripts/*` — deterministic operations.
- `resources/*` — non-instructional binary or media assets (rare).

## Deciding What Belongs Where

Use the following questions.

1. **Is the material required every time the skill runs?**
   - Yes → keep it in `SKILL.md`.
   - No → move it to a reference file loaded when needed.

2. **Is the material an instruction for the agent?**
   - Yes → reference file.
   - No → asset file (templates, checklists, examples).

3. **Is the material a deterministic operation the agent should not
   improvise?**
   - Yes → script file with clear CLI help.
   - No → keep it as prose.

4. **Is the material stable across invocations, or would it be recreated
   from a template every time?**
   - Stable → asset file.
   - Regenerated → describe the generation procedure in a reference.

## Reference File Guidelines

- One coherent topic per file.
- 100–300 lines is a healthy size.
- Split when a file exceeds 400 lines.
- Explain **when to load** the file at the top.
- Do not link to more than one or two other references from inside a
  reference.
- Do not create reference files that only link to more references.
- Use relative links from the skill root: `references/foo.md`.

## Asset File Guidelines

- Provide reusable templates, not project-specific data.
- Include placeholders (`<slug>`, `<user>`, `<transport>`), not real
  values.
- Do not include secrets, customer names, or private URLs.
- Keep templates short enough to be scanned on one screen.
- Include a header comment describing intended use.

## Script Guidelines

Load [`scripts-and-resources.md`](scripts-and-resources.md) for full
script rules.

- Add a script only for tasks the agent should not improvise.
- Standard library first. Extra dependencies must be justified.
- Include CLI help, input validation, deterministic exit codes.
- Never make network calls without documenting them.
- Never emit secret values.

## Linking Strategy

- Link every reference file from `SKILL.md`, or from a file already linked
  from `SKILL.md`. The validator warns on unlinked references.
- Prefer relative links over absolute paths.
- Do not link to the same reference from every section — link at the phase
  where it is actually needed.
- Include a short "Load ..." sentence in `SKILL.md` before each link so the
  agent knows when to consult the reference.

## Avoiding Reference Mazes

Signs of a bad reference structure:

- More than three levels of nesting (`SKILL.md → a.md → b.md → c.md`).
- Circular links between references.
- Reference files that repeat the same disclaimer as `SKILL.md`.
- Multiple references that cover the same topic slightly differently.

Fix by:

- Merging duplicate references.
- Promoting a shared subsection into a single reference.
- Removing links that add no value.
- Turning long tables into asset files instead of reference prose.

## When to Split `SKILL.md`

Consider extraction when any of the following is true:

- A single section exceeds 60 lines.
- A single section duplicates content from a reference file.
- The section describes tool syntax that changes independently from the
  workflow.
- The section contains dense tables the agent would only read during one
  specific phase.

The extracted content should stand alone with a self-contained heading
and a short "Load when ..." lead paragraph.

## Progressive Disclosure Checklist

- [ ] `SKILL.md` is between 300 and 450 lines (hard limit 500).
- [ ] Every reference is loaded exactly where it is needed.
- [ ] No reference file only links elsewhere.
- [ ] No circular references between files.
- [ ] Every asset has a header describing its use.
- [ ] No script contains secrets, unexplained network calls, or hidden
      side effects.
- [ ] The description in the metadata tier explains what activates the
      skill without duplicating the body of `SKILL.md`.
