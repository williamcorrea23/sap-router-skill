---
name: sap-abap-automated-documentation
description: Generate evidence-based functional and technical documentation for SAP ABAP developments, with object inventory, diagrams, optional SAP GUI screenshots, chapter rendering, and safe cleanup. Adapted from mario-andreschak/docs-sap-abap-automated-documentation-prompts.
trigger:
  keywords: [document abap object, automated abap documentation, sap screenshots, technical documentation, functional documentation, mermaid abap]
  intent: Produce or enhance comprehensive documentation for an SAP ABAP development object
---
# SAP ABAP Automated Documentation

Adapt the four-stage upstream prompt workflow to the router's registered capabilities.

## 1. Discover and plan

- Identify the root object, package, transactions, includes, classes, function groups, interfaces, tables, customizing, enhancements, and dependencies.
- Prefer ADT/code-search providers for source retrieval. Retrieve all relevant custom includes; do not recursively expand SAP-standard objects unless needed to explain an interface.
- Present an evidence-backed plan when scope or live-system interaction is material.

## 2. Write documentation

Cover overview, business context, user flow, inputs and outputs, examples, technical architecture, object details, data flow, structures, error handling, enhancements, full object inventory, and glossary.

Use tables for object and parameter inventories. Use Mermaid only when it clarifies relationships, and accompany every diagram or screenshot with explanatory text. Prefer concise significant snippets over full source listings.

For large deliverables, split chapters as `{OBJECT_NAME}_documentation_chapter_{N}.md`, then combine them in numeric order. Do not impose the upstream 4,000-character limit unless the active environment requires it.

## 3. Optional SAP GUI screenshots

- Use the configured SAP GUI provider only with an existing authorized session.
- Inspect and verify the screen before every interaction; keep navigation read-only unless the user explicitly authorizes a mutation.
- Capture only relevant screens, redact sensitive data, use descriptive filenames and alt text, and verify the resulting image.
- If reliable screen inspection is unavailable, stop screenshot automation and document the gap. Never guess click coordinates.

## 4. Render, combine, and clean up

Validate Mermaid syntax before rendering. Combine chapters only after each chapter passes review. Delete temporary chapters only after verifying the final document and only when cleanup is explicitly in scope; preserve images and the final output.

## Upstream assets

The original four prompts and MIT license are preserved in the pinned snapshot `bundled/skills/mario-andreschak-abap-documentation-prompts/`. They reference `mcp-abap-adt`, `mcp-sap-gui`, and image recognition; route those needs through the project's reviewed providers rather than assuming those exact server names are installed.

## Verification

Reconcile the appendix inventory with retrieved objects, ensure every material statement has source evidence, validate diagrams, check links and image alt text, and list unresolved gaps.
