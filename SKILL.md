# SAP Router Skill — moved

The master dispatch table now lives at the canonical skill source:

**[.agents/skills/sap-router-skill/SKILL.md](.agents/skills/sap-router-skill/SKILL.md)**

It was moved there so Claude Code actually registers it. Skills are only discovered under
`.claude/skills/*/SKILL.md`, and `.claude/skills` is generated from `.agents/skills` by
`scripts/generate_ide_assets.py`. At the repository root the file declared itself a skill but
was never registered anywhere, so `/sap-router-skill` did not exist.

**Edit the canonical file, never the mirrors** (`.claude/skills`, `.gemini/skills`) — they are
overwritten. After editing, run:

```bash
npm run ide:generate
```
