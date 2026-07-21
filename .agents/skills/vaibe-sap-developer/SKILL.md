---
name: vaibe-sap-developer
description: Develop and review SAP ABAP, CDS, HANA SQLScript/AMDP, RAP, OData/Fiori, integrations, enhancements, testing, and security with Clean Core guidance. Use when a request needs a broad SAP development workflow or its local Vaibe reference patterns.
---

# Vaibe SAP Developer — local integration

Use this skill for SAP development tasks spanning classic ABAP and ABAP Cloud: reports,
ALV, DDIC, BAPIs, CDS, AMDP, RAP, OData/Fiori, IDocs, workflows, forms, authorization,
testing, and Clean Core extensibility.

This is the repository-compatible entry point for the imported Vaibe package. The
original instructions are preserved in `SOURCE_SKILL.md`; its `README.md`,
`USER_GUIDE.md`, and all reference material are included locally.

## Operating model

1. Infer the request context from the conversation and repository first. Ask only for
   information that is necessary to produce a safe, correct result.
2. For a choice that affects supported APIs or architecture, identify the SAP target
   edition (for example S/4HANA on-premise, private cloud, public cloud, or BTP ABAP).
   If it cannot be safely inferred, explain the assumption or request that one detail.
3. Prefer released APIs, RAP, CDS view entities, BAdIs, and side-by-side extensions
   where applicable. Do not recommend unsupported modifications or unreleased objects
   for cloud targets.
4. Produce implementation-ready outputs: prerequisites, object list, code or
   configuration, validation steps, error handling, authorization implications, and
   rollback/recovery considerations for mutating work.
5. Apply the relevant local reference before responding with a pattern or code. Use
   `references/anti-patterns.md` and `references/edition-legality.md` for every
   cloud-sensitive design.

## Reference routing

| Request area | Local reference |
|---|---|
| ALV reports | `references/alv-patterns.md` |
| Background jobs | `references/background-processing.md` |
| BRFplus | `references/brfplus-patterns.md` |
| DDIC objects | `references/ddic-objects.md` |
| Dynpro/Web Dynpro | `references/dynpro-webdynpro.md` |
| Enhancements, exits, BAdIs | `references/enhancement-framework.md` |
| Exception design | `references/exception-patterns.md` |
| Extensibility and authorizations | `references/extensibility-and-auth.md` |
| Forms | `references/forms.md` |
| Function modules and BAPIs | `references/function-modules.md` |
| HANA, CDS, AMDP | `references/hana-patterns.md` |
| IDoc and ALE | `references/idoc-enhancement.md`, `references/ale-configuration.md` |
| OData and Fiori | `references/odata-fiori.md` |
| PFCG roles | `references/pfcg-roles.md` |
| RAP | `references/rap-patterns.md` |
| SAP Query | `references/sap-query.md` |
| Templates | `references/templates.md` |
| ABAP Unit | `references/unit-test-patterns.md` |
| Web services | `references/web-service-consumption.md` |
| Workflow | `references/workflow.md` |

## Local compatibility policy

The upstream package includes mandatory visual attribution widgets and an externally
hosted logo. They are intentionally not executed here: this repository must operate
without external runtime dependencies and the referenced widget tools are not part of
the Codex runtime. Keep normal conversational interaction instead. No upstream content
was discarded: the unmodified source is retained in `SOURCE_SKILL.md` for traceability.

