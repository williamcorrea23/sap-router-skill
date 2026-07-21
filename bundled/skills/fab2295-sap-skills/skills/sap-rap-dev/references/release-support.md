# Release support

RAP runs on multiple ABAP platforms. Features and language constructs are
introduced on a rolling basis; what compiles on a recent BTP ABAP
Environment may not yet be available on older S/4HANA on-premise stacks.

This file maps **major RAP capabilities to the platforms / releases** that
support them, and lists the **ABAP releases the skill targets**.

> **Anchored to**:
> https://help.sap.com/docs/abap-cloud
> https://help.sap.com/docs/abap-cloud/abap-rap/abap-rap.html

> **Disclaimer**: ABAP platform release cadences move continually. Numbers
> below reflect the state at this skill's `last_verified` date in the
> `SKILL.md` frontmatter. Always cross-check against the SAP Help Portal
> release notes for your specific target system before adopting a feature.

---

## 1. Supported platforms

| Platform                                            | RAP supported?      | ABAP Cloud development model? |
|-----------------------------------------------------|---------------------|--------------------------------|
| **SAP BTP, ABAP Environment** (Steampunk)           | Yes — RAP only      | Yes — strict                   |
| **S/4HANA Cloud, public edition** (Developer Extensibility) | Yes — extension + custom BO | Yes — strict                   |
| **S/4HANA Cloud, private edition** (Embedded Steampunk) | Yes                 | Yes — for new code             |
| **SAP S/4HANA** (on-premise, 1909+)                 | Yes                 | Optional — recommended         |
| **SAP NetWeaver AS ABAP** (7.5x, no S/4)            | Partial — early RAP only | No                         |

The skill defaults to the **ABAP Cloud development model** posture (released
APIs only). If your target is S/4HANA on-premise without ABAP Cloud, you
have access to a wider classic API surface, but adopting cloud-readiness
rules is still recommended.

---

## 2. Release timeline (high-level)

Release cadence on cloud platforms is biannual (e.g. `2308` = August 2023,
`2402` = February 2024). The on-premise releases (S/4HANA `2020`, `2021`,
`2022`, `2023`, …) ship annually and bundle the cloud features from the
prior cycle.

| Release window     | What landed (RAP-relevant highlights)                                                   |
|--------------------|------------------------------------------------------------------------------------------|
| Cloud `2105`–`2111`| Managed BO with draft GA, ETag handling, basic actions/validations/determinations.       |
| Cloud `2202`–`2208`| `strict( 2 )` introduced, unmanaged save scenarios mature, late numbering.               |
| Cloud `2302`–`2308`| Behavior extensions, metadata extensions broaden, `factory action`, advanced side effects. |
| Cloud `2402`–`2408`| CDS table entities mature, additional released APIs, expanded extensibility contracts.   |
| Cloud `2502`–`2508`| Continued maturity in extension scenarios, performance hints, expanded analytical RAP.   |

(See SAP Help Portal "What's New" for each release for the exhaustive list.
Numbers above are illustrative — confirm against the release notes.)

---

## 3. Feature support matrix

Approximate availability per platform / release. Where a checkmark is
parenthesized `(✓)`, the feature is available but with caveats noted in
the SAP release notes.

| RAP feature                                         | BTP ABAP Env  | S/4HC public  | S/4HC private | S/4 on-prem  |
|-----------------------------------------------------|---------------|---------------|---------------|--------------|
| Managed BO, no draft                                | ✓             | ✓             | ✓ (1909+)     | ✓ (1909+)    |
| Managed BO with draft                               | ✓             | ✓             | ✓ (2020+)     | ✓ (2020+)    |
| Unmanaged BO                                        | ✓             | ✓             | ✓ (2020+)     | ✓ (2020+)    |
| Managed-with-unmanaged-save                         | ✓             | ✓             | ✓ (2021+)     | ✓ (2021+)    |
| `strict( 2 )`                                       | ✓             | ✓             | ✓ (2022+)     | ✓ (2022+)    |
| Behavior extension                                  | ✓             | ✓             | ✓ (2022+)     | ✓ (2022+)    |
| Metadata extension                                  | ✓             | ✓             | ✓             | ✓            |
| CDS view entity (`define view entity`)              | ✓             | ✓             | ✓             | ✓ (2020+)    |
| CDS table entity (`define table entity`)            | ✓             | ✓             | ✓ (recent)    | (✓) (recent) |
| Late numbering                                      | ✓             | ✓             | ✓ (2021+)     | ✓ (2021+)    |
| Factory actions                                     | ✓             | ✓             | ✓             | ✓            |
| Side effects                                        | ✓             | ✓             | ✓             | ✓            |
| RAP test doubles (`cl_abap_behv_test_environment`)  | ✓             | ✓             | ✓ (2022+)     | ✓ (2022+)    |
| OData V4 UI binding                                 | ✓             | ✓             | ✓             | ✓ (2020+)    |
| OData V4 Web API binding                            | ✓             | ✓             | ✓             | ✓ (2020+)    |
| OData V2 UI binding                                 | ✓             | ✓             | ✓             | ✓            |
| REST binding                                        | ✓             | ✓             | ✓             | (✓)          |
| SQL binding                                         | ✓             | ✓             | ✓             | (✓)          |
| Analytical RAP                                      | ✓             | ✓             | ✓             | (✓)          |

If you target S/4HANA on-premise, **always cross-check the feature against
the SAP S/4HANA release notes for your installed stack** before adoption.
A feature listed as "supported" cloud-wide may have shipped to on-premise
later than expected.

---

## 4. ABAP Cloud development model — what it changes

When the **ABAP Cloud development model** is active (mandatory on BTP ABAP
Environment + S/4HANA Cloud public, optional on private/on-prem), the
following constraints apply:

- Only **released** APIs are usable in customer / partner code (see
  [released-apis.md](released-apis.md)).
- Classic frameworks (BOPF, FPM, Web Dynpro, Floorplan Manager, SAP GUI
  dynpros) are unavailable.
- `EXEC SQL`, `INSERT REPORT`, dynamic ABAP generation are forbidden in
  cloud-development packages.
- Foreign access to non-released DDIC objects is blocked at activation time.

The skill **assumes the ABAP Cloud development model is active**. If you
work on S/4HANA on-premise without it, you have more flexibility, but
cloud-readiness is still the recommended posture for future portability.

---

## 5. Choosing a strict mode

| `strict ( N )` | Use it when…                                                                          |
|----------------|-----------------------------------------------------------------------------------------|
| `strict ( 0 )` | Maintaining legacy code that hasn't been migrated yet. Don't author new BDEFs in this mode. |
| `strict ( 1 )` | The target release predates `strict ( 2 )` (older on-premise stack).                    |
| `strict ( 2 )` | Default for any new code on cloud or 2022+ on-prem.                                     |

Higher strict modes catch more bugs at activation. Always pick the highest
mode supported by your target release.

---

## 6. Versioning your services

For breaking-change evolution, version the service binding (`0001`,
`0002`, …) rather than mutating the existing one in place. See
[service-binding.md](service-binding.md#4-versioning). UI services
typically evolve in lockstep with the Fiori app and don't need versioning;
Web API services almost always do.

---

## 7. Anchor references

- ABAP Cloud overview:
  https://help.sap.com/docs/abap-cloud
- ABAP Cloud development model:
  https://help.sap.com/docs/abap-cloud/abap-cloud-development-model
- What's New (search per release):
  https://help.sap.com/whats-new/

Related skill files: [released-apis.md](released-apis.md),
[behavior-definition.md](behavior-definition.md),
[service-binding.md](service-binding.md).
