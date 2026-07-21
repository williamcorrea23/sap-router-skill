# Released APIs — cloud-development eligibility

The **ABAP Cloud development model** restricts customer / partner code to
**released** APIs. This file explains what "released" means, how to check
it, and what to do when the API you want is not released.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud/abap-cloud-development-model
> https://help.sap.com/docs/abap-cloud/abap-cloud-development-model/released-objects

---

## 1. Why "released APIs only"

On ABAP Cloud (BTP ABAP Environment, S/4HANA Cloud public edition), SAP
commits to:

- The **shape** of released APIs across release upgrades.
- A **deprecation lifecycle** before removal.
- No silent breaking changes between releases.

In exchange, customer / partner code must:

- Only call released APIs.
- Compile cleanly under the cloud development model's strict syntax rules.
- Pass ATC (ABAP Test Cockpit) cloud-readiness checks.

This is the deal that makes ABAP Cloud upgradeable without breaking
customer code. Bypassing it (e.g. calling an internal class) means your
code may stop working on the next release — silently.

---

## 2. The `@AbapCatalog.releaseState` annotation

DDIC objects (tables, views, data elements) and CDS objects declare their
release state via `@AbapCatalog.releaseState`:

| Value                  | Meaning                                                              | Can customers use it? |
|------------------------|----------------------------------------------------------------------|----------------------|
| `'RELEASED'`           | Released for customer / partner use. Stable contract.                | ✅ Yes               |
| `'DEPRECATED'`         | Released but slated for removal. Use the replacement.                | ⚠️ Yes, but plan to migrate |
| `'NOT_RELEASED'`       | Default — not yet committed for customer use.                        | ❌ No                |
| `'NOT_TO_BE_RELEASED'` | Explicitly internal. Never will be released.                         | ❌ No                |

ABAP classes / interfaces / functions declare their release state via
ADT → API State on the object's properties tab. The same four values apply
in spirit.

---

## 3. How to check release state

### 3.1 In ADT (Eclipse)

Right-click any object → Properties → **API State** tab. Shows:

- Release state: `Released` / `Released for Use in Key User Apps` /
  `Released for Use in Cloud Development` / `Not Released`.
- Released for: which scope (cloud development, key user apps, both).
- Successor: if deprecated, the recommended replacement.

### 3.2 Released Objects view

In ADT → Window → Show View → Other → ABAP → **Released Objects**.

This view lists every released object in the connected system, filterable
by:

- Object type (CDS view, class, interface, data element, BAdI, …).
- Use case (Cloud Development, Key User Apps).
- Software component.

Use it as the catalog when you're looking for *the* released way to do
something.

### 3.3 ABAP Test Cockpit (ATC)

The check variant **`SAP_CLOUD_PLATFORM_ATC_DEFAULT`** (or
`SAP_CP_READINESS_REMOTE_*` for on-premise targeting BTP) flags any use of
non-released APIs as a Priority 1 / 2 finding.

Run ATC in ADT (right-click package → Run As → ABAP Test Cockpit With…).
A clean ATC run on the cloud variant is the gate for cloud-readiness.

---

## 4. Released alternatives — common substitutions

Some classic APIs you can't use on ABAP Cloud, and their released
counterparts:

| Classic / not released                      | Released replacement                                             |
|---------------------------------------------|-------------------------------------------------------------------|
| `CL_ABAP_UTL_ABAP_R3SYSTEM`                 | `cl_abap_context_info`                                            |
| `CL_SYSTEM_UUID` (instance methods)         | `cl_system_uuid=>create_uuid_*_static`                            |
| `SY-LANGU` direct read                      | `cl_abap_context_info=>get_user_language_id( )`                   |
| `SY-DATUM` / `SY-UZEIT` direct read         | `cl_abap_context_info=>get_system_date( )` / `get_system_time( )` |
| `CALL FUNCTION` for HTTP                    | `cl_web_http_client_manager` + `cl_http_destination_provider`     |
| `CALL FUNCTION 'GUID_CREATE'`               | `cl_system_uuid=>create_uuid_x16_static( )`                       |
| `EXEC SQL`                                  | Native SQL via `cl_sql_*` (released subset)                       |
| Classic ENQUEUE/DEQUEUE FM                  | RAP `lock master` (declarative) — no manual enqueue in handlers   |
| `MESSAGE … TYPE 'E'`                        | RAP `reported-<alias>` with `if_abap_behv_message=>severity-error` |
| `WRITE` / list output                       | Not available — produce an OData response, not classic output     |

The Released Objects view in ADT is the authoritative catalog — these are
common shortcuts.

---

## 5. When the released surface can't do what you need

The cloud development model does not (yet) cover every classic capability.
When you hit a wall:

1. **Check the latest release notes** — features land continuously; the
   replacement may have shipped recently.
2. **Search the Released Objects view** with broader keywords — the
   released variant often has a different name.
3. **Open an SAP Influence / Continuous Influence request** — SAP
   prioritizes released-API gaps reported by customers.
4. **Do not** call an unreleased API hoping it'll be allowed later — your
   code won't pass ATC and won't transport.

If the gap is on **S/4HANA Cloud, private edition** or **on-stack ABAP
Platform**, you have access to a wider classic API surface — but adopting
cloud-readiness now buys you portability later.

---

## 6. Customer-extension namespace rules

Customer code lives in:

- `Z*` / `Y*` for customer-namespace objects (S/4HANA on-premise + private
  edition).
- Reserved customer namespace (`/<NAMESPACE>/…`) for public-edition
  customers.
- Reserved partner namespace (`/<PARTNER>/…`) for partners.

The **`YY1_*` prefix** is the convention for customer-added fields on
SAP-delivered objects in S/4HANA Cloud, public edition. Stick to it — it
keeps customer fields visibly separated from SAP-delivered fields and
avoids collisions with future SAP deliveries.

---

## 7. Strict modes and the cloud development model

`strict ( N )` in a BDEF is independent of release state, but they
interact: the cloud development model enables only strict-mode-correct
code. Targeting `strict ( 2 )` for new code aligns with cloud-readiness.

See [release-support.md](release-support.md#5-choosing-a-strict-mode).

---

## 8. Common gotchas

- ❌ Using `CL_…` classes you happen to see in samples / blogs — many are
  not released. Always check API State.
- ❌ Calling `SY-LANGU` etc. as direct system fields — fails the cloud
  ATC variant. Use the `cl_abap_context_info` released wrappers.
- ❌ Importing a deprecated API and ignoring the warning — the warning
  becomes an error in a future release and breaks your transport.
- ❌ Marking a customer extension with `@AbapCatalog.releaseState:
  'RELEASED'` — only SAP marks objects released. Customer objects stay at
  the default state.

---

## 9. Anchor references

- ABAP Cloud development model overview:
  https://help.sap.com/docs/abap-cloud/abap-cloud-development-model
- Released objects:
  https://help.sap.com/docs/abap-cloud/abap-cloud-development-model/released-objects
- API state in ADT:
  https://help.sap.com/docs/abap-cloud/abap-development-tools-user-guide/api-state

Related skill files: [release-support.md](release-support.md),
[behavior-implementation.md](behavior-implementation.md),
[metadata-extension.md](metadata-extension.md).
