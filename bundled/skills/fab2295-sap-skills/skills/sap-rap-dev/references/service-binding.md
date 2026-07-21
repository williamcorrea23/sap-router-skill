# Service binding

A **service binding** publishes a service definition under a specific
protocol and shape. It produces the URL consumers actually call.

```
Consumer (Fiori app / API client)
    │
    │  HTTP — OData V4 / V2 / REST / SQL
    ▼
Service binding   →  ZUI_TRAVEL_O4   ← THIS FILE — the protocol + URL
    │
Service definition →  ZUI_TRAVEL
    │
Projection view    →  R_Travel
```

> **Anchored to**: https://help.sap.com/docs/abap-cloud/abap-rap/service-binding

---

## 1. Binding types

> **Default: always OData V4.** All recommendations, examples, and the
> SKILL.md decision tree assume an OData V4 binding. **OData V2 is opt-in
> only** — produce a V2 binding *only* when the user explicitly asks for
> V2 (typical reason: integrating with a legacy Fiori app or external
> consumer that hasn't migrated yet). Never propose V2 as the default and
> never silently mix V2/V4 in the same skill output.

ADT → New → Service Binding → pick the type:

| Binding type             | Default?       | Use case                                                          |
|--------------------------|----------------|-------------------------------------------------------------------|
| **OData V4 — UI**        | ✅ **Default for Fiori UIs** | Fiori Elements UI consuming the service. Draft-aware, V4 features (singletons, return types, lambda filters). |
| **OData V4 — Web API**   | ✅ **Default for APIs**      | Programmatic API for external consumers. No draft assumptions.    |
| **OData V2 — UI**        | ⚠️ Opt-in only — user must ask | Older Fiori apps still on V2. Don't use for greenfield. |
| **OData V2 — Web API**   | ⚠️ Opt-in only — user must ask | Legacy V2 API consumers.                              |
| **REST**                 | Specialized    | Non-OData REST consumers (custom endpoints).                      |
| **SQL**                  | Specialized    | Data warehouse / analytics consumption (e.g. SAC, BW/4HANA).      |

For a brand-new RAP UI: **OData V4 — UI**.
For a brand-new public API: **OData V4 — Web API**.
For OData V2 (UI or API): the skill produces this **only when the user has
explicitly requested V2** in the current request. Otherwise, output V4 and
note the V4 choice in the response.

---

## 2. Creating a binding

In ADT:

1. Right-click the service definition → New → Service Binding.
2. Name (suggested: `<SERVICEDEF>_O4` for V4, `_O2` for V2, `_REST`, `_SQL`).
3. Pick binding type.
4. (Optional) Set service version (`0001`, `0002`, …) — increments allow
   side-by-side coexistence of breaking-change versions.
5. Activate.

ADT shows the binding editor with:

- A tree of exposed entities.
- A **Local Service Endpoint** URL (the dev-system URL of the service).
- A **Service URL** field (for the published runtime endpoint).
- A **Preview** button per entity (launches a generic Fiori Elements app).

---

## 3. Preview

The **Service Binding Preview** launches a no-code Fiori Elements list
report / object page generated from your `@UI.*` annotations. Use it for:

- Smoke-testing CRUD round-trips during development.
- Verifying draft behavior (create → edit → save → reopen).
- Checking that selection fields, line items, facets render as expected.
- Reproducing UX bugs interactively.

Preview is **not** a substitute for automated tests (see
[testing-rap.md](testing-rap.md)). Treat it as an interactive smoke test.

---

## 4. Versioning

The service version (`0001`, `0002`, …) lets you publish multiple shapes of
the same service simultaneously:

```
ZUI_TRAVEL  v0001  →  binding ZUI_TRAVEL_O4_V1  →  /sap/opu/odata4/sap/…/0001/
ZUI_TRAVEL  v0002  →  binding ZUI_TRAVEL_O4_V2  →  /sap/opu/odata4/sap/…/0002/
```

V1 consumers keep working while V2 evolves. Mark V1 deprecated when V2 is
GA, and remove V1 at the end of a deprecation window.

For OData V4 Web API, versioning is the recommended approach for
contract-breaking changes. For OData V4 UI, version increments are less
common because the Fiori app and service usually evolve together.

---

## 5. Behaviors per binding type

Different binding types expose different facets of the BDEF:

| Capability               | OData V4 UI            | OData V4 Web API        | REST                | SQL              |
|--------------------------|------------------------|--------------------------|----------------------|------------------|
| Draft                    | First-class            | Not surfaced             | Not surfaced         | N/A              |
| `@UI.*` annotations      | Consumed               | Mostly ignored           | N/A                  | N/A              |
| Actions / functions      | Yes                    | Yes                      | Limited              | N/A              |
| OData lambdas, $apply    | Yes                    | Yes                      | N/A                  | N/A              |
| Search                   | $search                | $search                  | Query-string         | SQL `where`      |
| ETag / optimistic concurrency | Yes (If-Match)    | Yes (If-Match)           | Yes (If-Match)       | N/A              |

For a UI service that handles drafts, **OData V4 — UI** is the only correct
binding. OData V4 — Web API exposes the same CRUD but bypasses the draft
state by default (drafts won't be visible to API consumers).

---

## 6. Service URL anatomy

A typical OData V4 UI URL on BTP ABAP Environment:

```
https://<host>/sap/opu/odata4/sap/<service_namespace>/srvd/sap/zui_travel/0001/Travel
```

Components:

- `/sap/opu/odata4/` — the OData V4 dispatcher.
- `/sap/<namespace>/srvd/sap/<service_binding_name>/<version>/` — the
  binding-specific path.
- `Travel` — the entity alias from the service definition.

The exact host and middle path vary by system (cloud, on-stack) and
namespace. The binding editor shows you the concrete URL for your system.

---

## 7. Securing a binding

A service binding is exposed through standard ABAP authentication and
authorization:

- **BTP ABAP Environment** — IAM business catalogs + business roles. The
  binding is reachable when the user's role grants the relevant
  authorization object (typically generated from the BDEF's
  `authorization master`).
- **S/4HANA Cloud, public edition** — Business Catalogs + Business Roles
  via the *Maintain Business Roles* app.
- **On-stack ABAP** — PFCG roles with the relevant authorization objects.

The RAP authorization handler in the behavior pool (see
[behavior-implementation.md §7](behavior-implementation.md#7-authorization-handler))
enforces instance-level decisions.

---

## 8. Common gotchas

- ❌ Using an OData V4 Web API binding for a Fiori UI — drafts won't work,
  `@UI.*` annotations are dropped.
- ❌ Forgetting to activate the binding after a projection / BDEF change —
  the binding caches the model; activate it to refresh.
- ❌ Publishing a binding with mismatched provider contracts in the
  underlying projections — preview fails.
- ❌ Sharing one binding across versions instead of using `0001` / `0002` —
  forces all consumers to migrate together.

---

## 9. Anchor references

- Service binding:
  https://help.sap.com/docs/abap-cloud/abap-rap/service-binding
- Binding types overview:
  https://help.sap.com/docs/abap-cloud/abap-rap/binding-types
- Service binding preview:
  https://help.sap.com/docs/abap-cloud/abap-rap/service-binding-preview

Related skill files: [service-definition.md](service-definition.md),
[cds-projection-view.md](cds-projection-view.md),
[behavior-implementation.md](behavior-implementation.md).
