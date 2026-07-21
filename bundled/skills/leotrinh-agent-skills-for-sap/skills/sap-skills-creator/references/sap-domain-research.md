# SAP Domain Research

Load this file during the Research phase, and again whenever a phase
mentions verifying a SAP fact.

The creator skill does not carry broad SAP product knowledge. Every
SAP-specific claim in a generated skill must be backed by a verifiable
source at the time the skill is designed.

## Source Preference Order

1. **Official SAP product documentation.** SAP Help Portal, product-family
   pages, release notes, migration guides.
2. **Official SAP API documentation.** SAP API Business Hub, product
   OpenAPI or EDMX specifications, ADT REST reference material.
3. **Official SAP developer resources.** SAP Developers site, SAP GitHub
   organisations (`SAP`, `SAP-samples`, `SAP-docs`), officially maintained
   tutorials.
4. **SAP Community content authored by SAP employees or credited MVPs.**
   Treat as strong but secondary.
5. **Third-party technical writing.** Use only for orientation; verify the
   underlying claim against an official source before encoding it into a
   skill.
6. **Team knowledge (runbooks, code, tickets).** Authoritative for the
   local convention, not for product behaviour.

Prefer stable canonical URLs over search-result snapshots. Record the
version, release, or last-updated date whenever the source exposes one.

## Categorising a Fact

Before writing an SAP claim into a skill, tag it as one of:

- **Official product behaviour.** Documented by SAP for a specific
  version.
- **Community convention.** Widely adopted but not part of the official
  contract.
- **Repository convention.** Enforced by the current codebase or team
  style guide.
- **Inference.** A reasoned guess based on adjacent facts.

Include the category in the reference material for the generated skill so
future maintainers can re-evaluate the fact.

## What Not to Invent

Never fabricate:

- SAP endpoints, URLs, or REST paths.
- Authorization objects, authorization fields, or role templates.
- CDS entities, associations, or annotations.
- BTP service plans, quotas, or entitlements.
- Destination properties or additional-properties keys.
- ADT REST commands or query parameters.
- CAP APIs, CAP model annotations, or CAP configuration keys.
- Fiori elements annotations or UI adaptation flexibility keys.
- Integration Suite iFlow components, adapter names, or content
  modifiers.

When an SAP fact is uncertain, mark the placeholder in the generated
skill and stop. Do not fill in a plausible guess.

## Version Sensitivity

SAP behaviour changes across releases. Document at minimum:

- The product name (for example, "SAP S/4HANA on-premise").
- The release train and edition when applicable (for example, "2023").
- The specific service or component version when known.
- The last verified date of the underlying documentation.

State the range of releases the skill is expected to work with in the
`compatibility` frontmatter field, and repeat it in `README.md` for human
readers.

## Handling Conflicting Sources

When two official sources disagree:

1. Prefer the newer of the two if both cover the same release.
2. If they cover different releases, keep both facts and mark the version
   range for each.
3. If they cover the same release and the same feature, stop and report
   the conflict to the user. Do not encode either fact until the conflict
   is resolved.

## Avoiding Copyright and Confidentiality Issues

- Do not copy large sections of SAP documentation verbatim.
- Summarise verified behaviour in your own words.
- Link to the official source in `README.md` when the source is public.
- Do not link to internal SAP documentation or customer-restricted
  material from a public skill.
- Do not embed proprietary customer designs, incident details, or
  architecture diagrams in a public skill.

## Local Encoding vs Live Lookup

Prefer to encode stable, well-documented behaviour directly into the
skill's reference files. Rely on a live lookup only when the underlying
material genuinely changes often (for example, current SAP AI Skills
Library submission form fields).

For live lookups, document:

- The URL used.
- The exact information sought.
- The fallback path when the site is offline or has changed.

Never make a live network call from within a script without documenting
it and providing a graceful failure path.

## SAP AI Skills Library and Related Requirements

When designing an SAP AI Skills Library-ready skill, verify at
design-time:

- Whether the bring-your-own-repository model is still in use.
- The current registration form fields and required checklists.
- Any additional constraints (public repository, discoverable via the
  Skills CLI, disclaimers about non-affiliation).

Load [`sap-library-submission.md`](sap-library-submission.md) for the
current submission workflow.

## Reporting Research Results

At the end of the Research phase, produce a short table for the design
notes:

| Claim | Category | Source | Verified date | Version scope |
|-------|----------|--------|---------------|----------------|

Attach the table to the requirements file described in
[`../assets/skill-requirements-template.md`](../assets/skill-requirements-template.md).
Missing rows are stop conditions until the user provides the source.
