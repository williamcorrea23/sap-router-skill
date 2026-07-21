# CLAUDE.md — Anthropic skill spec, distilled

This file loads into Claude's context on every turn in this repo. It captures the parts of Anthropic's *Complete Guide to Building Skills for Claude* you need to follow when editing `skills/sap-table-field-remediator/`. Read it once to learn the spec, then use it as a reference.

## How skills load — the 3-level model

This is the one mental model that makes the rest of the rules click. Claude reads a skill in three progressive levels:

1. **YAML frontmatter** — always loaded into the system prompt. Used by Claude to decide whether to load the rest. Must be tight.
2. **`SKILL.md` body** — loaded only when Claude judges the skill relevant to the user's task. Under 5,000 words.
3. **Linked files** in `scripts/`, `references/`, `assets/` — loaded only when Claude follows a link.

Push detail to level 3. The body orients; it doesn't exhaust.

## Skill folder (hard requirements)

- Lives at `skills/sap-table-field-remediator/`.
- Folder name is kebab-case and must match the `name:` field in `SKILL.md`. No spaces, underscores, or capitals.
- Allowed inside: **only** `SKILL.md` (required) plus optional `scripts/`, `references/`, `assets/`. **No `README.md`, no `CLAUDE.md`, no dotfiles** — they break the upload flow and clutter the distributable unit.

## YAML frontmatter (hard requirements)

- Wrap with `---` delimiters above and below.
- `name`: kebab-case. Cannot start with `claude` or `anthropic` (reserved).
- `description`: structure as **`[what it does] + [when to use it] + [trigger phrases a user would actually type]`**, under 1024 characters. This is the only thing Claude uses to decide whether to load your skill — get it right.
- **No XML angle brackets (`< >`) anywhere in frontmatter** — security restriction.

## Body content

- Be specific and actionable. ❌ "Validate the data." ✅ "Run `python scripts/validate.py --input {filename}`; if it fails, common causes are missing fields or invalid date formats."
- Use markdown headers, not prose paragraphs. Claude parses structure faster than prose.
- Include error handling for likely failures.
- When a section grows past a few hundred words, move detail into `references/` and link to it from the body. That's the 3-level model at work.

## Going deeper

- Anthropic skills docs: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Reference skills (read these — best teacher): https://github.com/anthropics/skills
- The `skill-creator` skill (in Claude Code) — interactively builds and reviews skills with you.
