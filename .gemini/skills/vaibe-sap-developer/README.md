# vaibe-sap-developer

**Current version: 2.7**

Generates Clean Core-compliant SAP ABAP code — CDS, AMDP, RAP, OData/Fiori, IDoc/enhancements, Function Modules, BAdIs, classic ALV/Dynpro/WebDynpro (legacy), Forms, Workflow, background processing, web-service consumption, DDIC objects, BRFplus, and authorization/role guidance — gated by target environment edition (On-Premise / Cloud Private Edition / Cloud Public Edition / BTP ABAP Environment) so generated code is actually legal for the system it's headed to.

For how to *use* this skill day-to-day, see `USER_GUIDE.md`. This file is about what's in the package and how it's changed.

## File structure
```
vaibe-sap-developer/
├── SKILL.md                          — main instructions: elicitation flow, reference routing, validation
├── USER_GUIDE.md                     — end-user instructions
├── README.md                         — this file
└── references/
    ├── edition-legality.md           — cross-cutting matrix: what's legal per environment edition
    ├── hana-patterns.md              — AMDP & advanced CDS optimization
    ├── templates.md                  — baseline OO ABAP class skeleton
    ├── rap-patterns.md               — RAP BDEF, managed/unmanaged, draft, actions
    ├── odata-fiori.md                — OData V4 exposure, Fiori UI annotations
    ├── exception-patterns.md         — custom exceptions, message classes, RAP failed/reported
    ├── unit-test-patterns.md         — ABAP Unit test classes, test doubles
    ├── idoc-enhancement.md           — IDoc retrigger, BAdI skeletons (enhancement side)
    ├── ale-configuration.md          — ALE distribution model, partner profiles, IDoc type setup
    ├── function-modules.md           — RFC-enabled FMs, BAPI conventions
    ├── forms.md                      — Smart Forms, Adobe Forms, SAPscript
    ├── dynpro-webdynpro.md           — classic Dynpro screens, WebDynpro ABAP
    ├── workflow.md                   — Flexible Workflow, classic Business Workflow (SWF)
    ├── enhancement-framework.md      — general BAdIs/enhancement points (non-IDoc objects)
    ├── extensibility-and-auth.md     — new custom auth objects (SU21), cloud key-user extensibility
    ├── ddic-objects.md                — tables, structures, lock objects, number ranges, search helps
    ├── alv-patterns.md               — classic FM-based and OO ALV reporting
    ├── background-processing.md      — job scheduling, polling, parallel/async processing
    ├── web-service-consumption.md    — outbound HTTP/REST/SOAP, edition-correct client API
    ├── sap-query.md                  — SAP Query / ABAP Query (SQ01)
    ├── brfplus-patterns.md           — BRFplus decision tables/rules, ABAP call-side
    ├── pfcg-roles.md                 — PFCG roles, Business Catalog/Business Role model
    └── anti-patterns.md              — reject-list with before/after code
```
23 reference files total.

## How it works (brief)
1. **Phase 1 — Elicitation.** Choice-based questions run through the native `ask_user_input_v0` tappable-button widget, numbered as a single continuous "Question N of X" flow even when split across multiple calls. Free-text fields (namespace, requirement description, pasted code) run through a `visualize:show_widget` form with placeholders. Every question's relevance and option set is filtered against `edition-legality.md` using all answers collected so far, not just the immediately preceding one.
2. **Phase 2 — Routing.** Resolved artifact type routes to the matching reference file(s) above.
3. **Phase 3 — Validation.** Generated code is checked against `anti-patterns.md` and `edition-legality.md` before being returned.

## Changelog
- **2.7** — Added 8 reference files: `ddic-objects.md`, `ale-configuration.md`, `alv-patterns.md`, `background-processing.md`, `web-service-consumption.md`, `sap-query.md`, `brfplus-patterns.md`, `pfcg-roles.md`. Added BAPI conventions to `function-modules.md` and a message-class (SE91) creation walkthrough to `exception-patterns.md`.
- **2.6** — Added 6 reference files closing the original artifact-coverage gaps: `function-modules.md`, `forms.md`, `dynpro-webdynpro.md`, `workflow.md`, `enhancement-framework.md`, `extensibility-and-auth.md`. Phase 1 buckets/sub-types and Phase 2 routing updated to match.
- **2.5** — Step 3 free-text fields moved from a plain chat message to a `visualize:show_widget` elicitation-module form with placeholders (`ask_user_input_v0` has no text-input variant).
- **2.4** — Added `edition-legality.md`. Phase 1 queue-building now filters every question's relevance and option set against cumulative answer context, not just the immediately preceding answer.
- **2.3** — Fixed the Basis-release drop condition to also cover BTP ABAP Environment (previously only checked Cloud Public Edition).
- **2.2** — Elicitation runs as one continuous "Question N of X" numbered flow across multiple `ask_user_input_v0` calls instead of unlabeled separate steps.
- **2.1** — Elicitation moved from a custom `ElicitForm` React/HTML artifact to the native `ask_user_input_v0` widget. Deprecated and later deleted the `ElicitForm.tsx.ts` asset and all Vaibe branding/logo assets.
- **2.0** *(prior to this changelog)* — Six SAP reference files, modular conditional loading, elicitation form supporting S/4HANA Cloud Public/Private Edition split.

## Known scope boundary
This skill is ABAP-only. Non-ABAP BTP services — Integration Suite (CPI iFlows, Groovy), CAP (Node/Java), Event Mesh, SAP Build Process Automation — are explicitly out of scope.
