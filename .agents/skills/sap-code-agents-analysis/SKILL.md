---
name: sap-code-agents-analysis
description: Evidence-backed analysis of custom ABAP codebases, including object search, dependency and where-used analysis, usage evidence, migration findings, retirement candidates, and technical documentation. Adapted from jonathanbernsteiner/sap-code-agents.
trigger:
  keywords: [sap code agents, analyze abap codebase, abap evidence, migration assessment, retirement candidates, usage statistics, dependency graph]
  intent: Analyze an ingested or accessible custom ABAP codebase with traceable evidence for every claim
---
# SAP Code Agents Analysis

Use the evidence-first method adapted from `jonathanbernsteiner/sap-code-agents`.

## Routing

1. Discover objects with the registered ADT/code-search capability.
2. Read the complete source of every object used as evidence.
3. Resolve callers and dependencies with where-used and repository search.
4. Use runtime usage data only when an authorized source is available; otherwise label it unavailable.
5. Produce findings that cite object names and source line evidence. Never convert an inference into a fact.

For a local abapGit checkout, search and read the files directly. For a live system, prefer the router's ADT providers. Do not ask for credentials in chat and do not bypass the configured MCP approval policy.

## Deliverables

- Functional purpose per object, supported by retrieved source.
- Dependency and data-access map.
- Migration risks with explicit evidence tiers.
- Retirement candidates separated into `supported`, `inferred`, and `unresolved`.
- Open questions for missing source or usage telemetry.

## Evidence rules

- Attach at least one verifiable object/source reference to each material claim.
- Report parser or retrieval failures instead of silently omitting objects.
- Keep system/workspace scope on every query; never mix evidence across systems.
- Do not claim that unused code is safe to retire from static analysis alone.

## Upstream reference

The pinned snapshot is cataloged as `jonathanbernsteiner-sap-code-agents` under `bundled/skills/`. Its architecture and evidence model are described in its `README.md`; its application is not an MCP server.

## Verification

Confirm that object counts reconcile, all cited objects were retrieved, unresolved items are listed, and conclusions can be traced to source or authorized usage evidence.
