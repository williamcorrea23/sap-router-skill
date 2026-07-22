---
name: abap-docs-reference
description: Use the enhanced ABAP keyword documentation corpus and its Markdown build pipeline from eduardocopat/abap-docs as an offline reference for ABAP language questions.
trigger:
  keywords: [abap docs, abap keyword documentation, abap syntax reference, eduardocopat, offline abap documentation]
  intent: Find or explain ABAP language syntax and semantics using the bundled documentation source
---
# ABAP Docs Reference

Use the pinned `eduardocopat/abap-docs` snapshot as a documentation corpus and build reference.

## Workflow

1. Search the snapshot under `bundled/skills/eduardocopat-abap-docs/` for the ABAP statement or concept.
2. Prefer exact keyword pages and examples over secondary summaries.
3. State the SAP release context when the source exposes it; do not assume modern syntax is available on older NetWeaver releases.
4. When the snapshot does not contain the generated page, use the router's configured documentation-search capability or official SAP documentation.
5. Cite the local source path or authoritative page used.

## Build pipeline

The upstream project downloads SAP documentation, parses it into Markdown, and builds a MkDocs site. Do not start the upstream download automatically: it is network-heavy and may take hours. Run it only when the user explicitly asks to rebuild the corpus and the upstream prerequisites are installed.

## Safety and licensing

Treat SAP documentation content as SAP-owned material. Summarize and quote sparingly. The upstream tooling is MIT-licensed; its `LICENSE.md` is preserved in the pinned snapshot.

## Verification

Check the syntax against the target ABAP release and distinguish documented behavior from recommendations or inferred behavior.
