---
name: sap-crew-analysis
description: Dispatch small SAP code investigations, edits, and reviews to the repository's cavecrew workers with evidence and bounded scope.
---

# SAP Crew Analysis

Use for focused SAP repository work where one to two files are in scope.

## Workflow

1. Classify the request as investigator, builder, or reviewer.
2. Use `python scripts/sap_router.py crew-dispatch --help` and the canonical crew registry; do not invent worker names.
3. Keep investigators read-only, builders narrowly scoped, and reviewers severity-tagged.
4. Preserve user changes, show the exact evidence examined, and run the smallest relevant verification.

Escalate broad refactors, SAP functional writes, credentials, and production actions to the normal approval and routing gates.
