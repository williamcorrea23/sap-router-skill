# Authorization Roles (PFCG / Business Catalogs)
Parent skill: vaibe-sap-developer
Load when: the user needs guidance assembling a role around a custom authorization object or RAP BO — distinct from `references/extensibility-and-auth.md`, which covers *creating* the authorization object itself; this file covers assembling the *role* that carries it.

This is admin/Customizing work, not generatable ABAP — walk through the steps rather than producing code.

## On-Premise / Private Edition — classic PFCG
1. Single role (PFCG) → Menu tab: assign the transaction/Fiori app/OData service.
2. Authorizations tab: pull in the relevant objects (standard + your new custom one from `references/extensibility-and-auth.md`), maintain field values (activity, org-level fields).
3. Composite role: bundle single roles for a job function if the user needs more than one capability area together.
4. Generate the profile, then assign the role to users/positions.

Rule: never propose `ACTVT = *` (full wildcard) on a custom object as a shortcut — ask which specific activities (01 create, 02 change, 03 display, etc.) are actually needed.

## Cloud Public Edition — Business Catalogs / Business Roles
The model is different — there's no PFCG-style single-role authorization-object assembly for custom extensibility content:
1. **Business Catalog** — a pre-delivered grouping of related apps/permissions (e.g. a catalog covering a specific Fiori app). Custom RAP BOs you've built get their own auto-generated catalog when exposed via the Custom Business Object app.
2. **Business Role** — bundles one or more Business Catalogs, assigned to users via the "Maintain Business Roles" / "Maintain Business Users" apps.

Rule: don't propose classic PFCG steps for Public Edition — point to Business Catalog/Business Role assignment instead, and confirm the custom BO's generated catalog name with the user rather than guessing it.

## What this skill won't do
Role/catalog assignment to specific users is a security/Basis decision (segregation-of-duties, org-level restrictions) — flag the structural steps above, but don't decide *which* roles/catalogs a given user should get; that's a business call for the user's security team.

## Anti-patterns
- Don't generate ABAP code as a substitute for role assignment — that's not how authorization works (see the actual `AUTHORITY-CHECK` pattern in `references/extensibility-and-auth.md`).
- Don't propose full-wildcard activity values to "make it simpler."
