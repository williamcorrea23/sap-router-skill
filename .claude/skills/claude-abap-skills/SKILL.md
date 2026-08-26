---
name: claude-abap-skills
description: Use the curated ABAP skill set for design, implementation, review, testing, and documentation tasks in Claude-compatible workflows.
---

# Claude ABAP Skills

Use this skill as the Claude-facing entry point for the canonical ABAP skills in `.agents/skills`.

## Workflow

1. Resolve `SAP_ROUTER_ROOT` and work from the canonical repository.
2. Discover the narrowest applicable skill with `python scripts/source_catalog.py search "<task>"`.
3. Prefer ADT/read-only evidence for source inspection and route writes through the approval gate.
4. Apply Karpathy wrapper and caveman compression: state the result, evidence, and next action compactly.
5. Verify with the relevant ABAP lint, unit, security, or catalog check before reporting completion.

Never invent SAP object metadata, bypass functional-write context, or request credentials in a skill response.
