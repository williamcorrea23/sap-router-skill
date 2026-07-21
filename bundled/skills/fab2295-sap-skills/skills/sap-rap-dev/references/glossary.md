# Glossary — RAP terms

Compact definitions for the RAP vocabulary, cross-linked to the artifact
file where each concept is implemented.

| Term                        | Definition                                                                                                       | Where implemented |
|-----------------------------|------------------------------------------------------------------------------------------------------------------|--------------------|
| **BO** (Business Object)    | A root entity plus zero or more composition children, sharing behavior, lock, draft, ETag, authorization.        | [learn.md](learn.md) |
| **Interface view**          | The CDS view (`I_…`) that defines the BO's stable internal shape. Behavior is attached to the interface view.    | [cds-view-entity.md](cds-view-entity.md) |
| **Projection view**         | The CDS view (`R_…` / `C_…`) that exposes a tailored shape to a service, with `@UI.*` annotations.                | [cds-projection-view.md](cds-projection-view.md) |
| **Provider contract**       | Clause on a projection view declaring its purpose (`transactional_query`, `transactional_interface`, `analytical_*`). | [cds-projection-view.md](cds-projection-view.md) |
| **BDEF** (Behavior Definition) | Declarative DSL describing the BO's operations, validations, determinations, actions, draft, locking.         | [behavior-definition.md](behavior-definition.md) |
| **Behavior pool**           | The ABAP class hosting handlers for the BDEF's declared artifacts (`FOR BEHAVIOR OF I_<view>`).                    | [behavior-implementation.md](behavior-implementation.md) |
| **Local handler class**     | Class inside the behavior pool inheriting from `cl_abap_behavior_handler` — implements determinations, validations, actions, features. | [behavior-implementation.md](behavior-implementation.md) |
| **Saver class**             | Class inheriting from `cl_abap_behavior_saver` — implements `save_modified`, `cleanup`, `cleanup_finalize`; runs the save sequence. | [behavior-implementation.md](behavior-implementation.md) |
| **EML** (Entity Manipulation Language) | ABAP DSL (`READ ENTITIES`, `MODIFY ENTITIES`, `COMMIT ENTITIES`) for accessing RAP BOs from ABAP code.    | [eml.md](eml.md) |
| **MDE** (Metadata Extension)| A `annotate entity` block that adds CDS annotations to an existing view without modifying it.                     | [metadata-extension.md](metadata-extension.md) |
| **ETag**                    | Entity tag — concurrency token. Client sends what version it last read; RAP rejects if stale.                     | [behavior-definition.md](behavior-definition.md#1-header) |
| **Total ETag**              | ETag aggregated across the composition tree; declared via `lock master total etag <field>`.                       | [behavior-definition.md](behavior-definition.md#1-header) |
| **Draft**                   | Persisted, user-private edit state of a BO instance; resumable across sessions.                                   | [behavior-definition.md](behavior-definition.md#9-draft-block) |
| **Determination**           | Server-side computation triggered at a defined lifecycle point (`on modify`, `on save`); modifies data.            | [behavior-definition.md §6](behavior-definition.md#6-determinations) |
| **Validation**              | Server-side check at a defined lifecycle point; can mark an instance invalid via `failed-<alias>`.                 | [behavior-definition.md §5](behavior-definition.md#5-validations) |
| **Side effect**             | UI hint declaring which fields/entities to refresh after a change. Not a server-side action.                       | [behavior-definition.md §8](behavior-definition.md#8-side-effects) |
| **Action**                  | Typed, named non-CRUD operation that modifies data.                                                                | [behavior-definition.md §7](behavior-definition.md#7-actions-and-functions) |
| **Factory action**          | Action that produces a new instance (templated create).                                                            | [behavior-definition.md §7](behavior-definition.md#7-actions-and-functions) |
| **Static action**           | Action not tied to a specific instance.                                                                            | [behavior-definition.md §7](behavior-definition.md#7-actions-and-functions) |
| **Function**                | Read-only counterpart to an action.                                                                                | [behavior-definition.md §7](behavior-definition.md#7-actions-and-functions) |
| **Internal action**         | Callable only via EML from sibling BOs; not exposed on the service.                                                | [behavior-definition.md §7](behavior-definition.md#7-actions-and-functions) |
| **Feature control**         | Per-instance enable/disable of an operation or action; computed by a `FOR INSTANCE FEATURES` handler.              | [behavior-implementation.md §6](behavior-implementation.md#6-feature-control-handler) |
| **Numbering**               | Strategy for assigning keys: managed/unmanaged × early/late.                                                       | [behavior-definition.md §3](behavior-definition.md#3-field-controls) |
| **Lock master**             | The BO that owns the persistent lock for a composition tree. Children are `lock dependent by _Parent`.             | [behavior-definition.md §1.2](behavior-definition.md#12-header-clauses) |
| **Authorization master**    | The BO that owns the authorization decisions for a composition tree.                                               | [behavior-definition.md §1.2](behavior-definition.md#12-header-clauses) |
| **Service definition**      | CDS object listing the exposed entities of a service (`define service { expose … }`).                              | [service-definition.md](service-definition.md) |
| **Service binding**         | Runtime exposure of a service definition under a specific protocol (OData V4 / V2 / REST / SQL).                   | [service-binding.md](service-binding.md) |
| **Local service endpoint**  | The dev-system URL of a service binding, used for preview and integration tests.                                   | [service-binding.md §6](service-binding.md#6-service-url-anatomy) |
| **Service binding preview** | No-code Fiori Elements app generated from `@UI.*` annotations, launched from the binding editor.                   | [service-binding.md §3](service-binding.md#3-preview) |
| **%key**                    | Primary key fields of an entity instance.                                                                          | [behavior-implementation.md §10](behavior-implementation.md#10-working-with-tky-cid-key) |
| **%is_draft**               | `'01'` = draft instance, `'00'` = active instance.                                                                  | [behavior-implementation.md §10](behavior-implementation.md#10-working-with-tky-cid-key) |
| **%tky** (transactional key)| `%key` + `%is_draft`; the default key in handler code.                                                              | [behavior-implementation.md §10](behavior-implementation.md#10-working-with-tky-cid-key) |
| **%cid** (client ID)        | Caller-set ID for a not-yet-persisted instance, used to reference it before `%key` exists.                          | [eml.md §3](eml.md#3-modify-entities--create) |
| **%cid_ref**                | References a parent's `%cid` when creating a child under a not-yet-persisted parent.                                | [eml.md §3.1](eml.md#31-create-child-via-composition) |
| **`reported`**              | Output table of messages emitted by a handler (errors, warnings, info).                                            | [behavior-implementation.md §11](behavior-implementation.md#11-the-standard-tables-in-every-handler) |
| **`failed`**                | Output table identifying rows the handler rejected; the save aborts for those rows.                                | [behavior-implementation.md §11](behavior-implementation.md#11-the-standard-tables-in-every-handler) |
| **`mapped`**                | Output table from a create handler: `%cid` → `%key` mapping for newly persisted rows.                              | [behavior-implementation.md §11](behavior-implementation.md#11-the-standard-tables-in-every-handler) |
| **%state_area**             | Stable identifier for a validation; RAP clears prior messages with the same state area when the validation re-runs and passes. | [behavior-implementation.md §4](behavior-implementation.md#4-validation-handler) |
| **DCL** (Data Control Language) | CDS-side language for declaring data-level access rules; bound to a view via the file name.                    | [released-apis.md](released-apis.md) |
| **ATC** (ABAP Test Cockpit) | Static-analysis tool; cloud-readiness variant gates customer code on cloud-allowed APIs and syntax.                | [released-apis.md §3.3](released-apis.md#33-abap-test-cockpit-atc) |
| **Released API**            | API SAP commits to keep stable; usable in customer / partner code on ABAP Cloud and S/4HANA Cloud public.          | [released-apis.md](released-apis.md) |
| **Strict mode**             | BDEF compile-time check level (`strict( 0 )` → `strict( 2 )`). Higher = more checks.                                | [behavior-definition.md §13](behavior-definition.md#13-strict-modes) |
| **ABAP Cloud development model** | Posture restricting customer code to released APIs and cloud-allowed syntax.                                  | [released-apis.md](released-apis.md), [release-support.md](release-support.md) |

> See also: [learn.md](learn.md) for the conceptual overview,
> [release-support.md](release-support.md) for the platform matrix.
