# SAP compliance offering catalogue & document locations

Captured from the **SAP Trust Center** during authoring. **[V]** where read directly from the live pages.

> **Re-verify before use.** This area changes continuously — new standards (ISO 42001 appeared recently),
> reports get consolidated, and regional schemes evolve. Treat this as a map, not a snapshot of truth.

Base URLs (the regional prefix such as `/sea/` is optional — omit it for the global page):

```
Trust Center            https://www.sap.com/about/trust-center.html
Certification overview  https://www.sap.com/about/trust-center/certification-compliance.html
Compliance Finder       https://www.sap.com/about/trust-center/certification-compliance/compliance-finder.html
Data protection/privacy https://www.sap.com/about/trust-center/data-privacy.html
Agreements              https://www.sap.com/about/trust-center/agreements.html
Cloud status            https://www.sap.com/about/trust-center/cloud-service-status.html
Data centers            https://www.sap.com/about/trust-center/data-center.html
Security                https://www.sap.com/about/trust-center/security.html
  incident management   https://www.sap.com/about/trust-center/security/incident-management.html
  cloud ERP security    https://www.sap.com/about/trust-center/security/cloud-erp-security.html
```

---

## Deep-link pattern

```
https://www.sap.com/about/trust-center/certification-compliance/compliance-finder.html
    ?tag=compliance-document:compliance-offering/<slug>
```

Optionally add `&sort=latest_desc`.

| Offering | Slug | What it evidences |
|---|---|---|
| **ISO/IEC 27001** | `iso-27001` | Information security management system — the baseline security ask |
| **ISO/IEC 27017** | `iso-27017` | Cloud-specific information security controls (supports 27001) |
| **ISO/IEC 27018** | `iso-27018` | Protection of PII in public clouds (supports 27001) |
| **ISO/IEC 27701** | *(via entity search)* | Privacy information management; PII controller/processor scope |
| **ISO/IEC 42001** | `iso-42001` | **AI management system** — audit requirements for responsible AI governance |
| **ISO 9001** | `iso-9001` | Quality management (SAP has held this since 1998) |
| **ISO 22301** | `iso-22301` | Business continuity management |
| **ISO 14001** | `iso-14001` | Environmental management (multisite; appendix lists covered sites) |
| **ISO 50001** | `iso-50001` | Energy management (some sites) |
| **BS 10012** | `bs-10012` | Personal information management system |
| **SOC 1** | `soc-1` | Controls relevant to customers' **financial reporting** (SSAE 18 / ISAE 3402) |
| **SOC 2** | `soc-2` | Security, availability, processing integrity, confidentiality, privacy (ISAE 3000 / AT 101) |
| **SOC 1 bridge letter** | `soc-1-bridge-letter` | Covers the gap from report end date to letter issue date |
| **SOC 2 bridge letter** | `soc-2-bridge-letter` | As above |
| **BSI C5** | `c5` | German Cloud Computing Compliance Criteria Catalogue |
| **PCI DSS** | `pci-dss` | Payment card data handling attestations |
| **CSA STAR** | `csa-star` | Cloud Security Alliance registry certification |
| **GxP** | `gxp` | Life-sciences regulated-use documents |
| **Canadian cloud compliance** | `canadian-cloud-compliance` | PBMM / CCCS assessment summaries |

**Not on the finder — obtained elsewhere:**

| Scheme | Where |
|---|---|
| **TISAX** (automotive) | ENX portal — `https://enx.com/en-US/TISAX/` (sign-in) |
| **FedRAMP** | FedRAMP Marketplace, under **SAP National Security Services (SAP NS2)** |
| **EU Cloud Code of Conduct** | Public register at `https://eucoc.cloud` — entries carry a **Verification-ID** |
| **PS 880** | `https://help.sap.com/docs/Certificates` |
| **Accessibility (ACR/VPAT)** | Request via `accessibility@sap.com` |
| **Controlled Goods Program (Canada)** | Public CGP registry; SAP publishes its certificate |

---

## Regional / sector schemes

| Region | Scheme | Notes captured live **[V]** |
|---|---|---|
| **US** | **FedRAMP** | Standardized assessment/authorization for cloud products for government agencies; SAP's authorizations are listed under **SAP NS2** |
| **US** | **CMMC** | DoD certification for handlers of **FCI / CUI**. **CUI scenarios (typically CMMC Level 2 and 3) are supported only through SAP NS2 environments.** *"Customers remain responsible for determining their own CMMC scope, implementing required controls, and obtaining applicable certification or assessment."* |
| **Canada** | **PBMM**, **PBHVA**, **CGP** | Assessed against **Protected B / Medium Integrity / Medium Availability**; **SAP Sovereign Cloud for Canada** also against the **Protected B High Value Asset** overlay; CCCS Cloud Assessment Summary Reports available on request |
| **Germany / EU** | **C5**, **KRITIS**, **NIS2 / CER** | C5 attestations on the finder; SAP publishes a **NIS2 and CER FAQ** and an NIS2 brochure |
| **Automotive** | **TISAX** | Via ENX |

---

## Related governance material

| Topic | Where |
|---|---|
| **Global Code of Ethics and Business Conduct** | Trust Center → compliance resources |
| **Sustainability policies, codes and commitments** | `https://www.sap.com/products/sustainability/our-approach/reporting-and-policies.html` — ESG commitments and reporting, distinct from the ISO 14001/50001 certificates. **Note: "SDG" in an SAP contract context means *Service Description Guide*, not Sustainable Development Goals — see the agreements table below** |
| **EU AI Act / Joule Agents** | *SAP Joule Agents Compliance Brief*, linked from the certification page |
| **Agreements** (contract documents, DPA, supplements) | Trust Center → **Agreements** |
| **Data protection & privacy** | Trust Center → **Data Protection and Privacy** |

---

## Agreement & contract documents (distinct from certificates)

Base: `https://www.sap.com/about/trust-center/agreements.html`

Cloud library — `…/about/trust-center/agreements/cloud/cloud-services.html` plus a tag or search: **[V]**

| Document type | Query fragment |
|---|---|
| **Service Description Guides (SDG)** | `?tag=agreements:product_use_and_support_terms/service-description-guides` |
| Supplemental terms and conditions | `?tag=language:english&search=Supplement` |
| Service-level agreements | `?search=Service Level Agreement` |
| Support schedules | `?search=Support` |
| Product development schedules | `?tag=agreements:product-development-schedule/product-development-schedule` |
| General terms and conditions | `?search=General Terms and Conditions` |
| **AI terms** | `?tag=agreements:general-terms-and-conditions/ai` |
| **AI Code of Conduct** | `?search=AI%20Code%20of%20Conduct` |
| **AI third-party pass-through terms** | `?tag=agreements:general-terms-and-conditions/ait/ai-third-party-pass-through-terms` |
| Data processing agreements | `?search=Data%20Processing` |
| **Security measures (TOMs for DPA purposes)** | `?tag=agreements:security-measures/security-measures-for-cloud-services` |
| List of data centers | `?search=Data Centers` |

Other libraries:

| Library | URL |
|---|---|
| On-premise service descriptions | `…/agreements/on-premise/service-descriptions.html` |
| On-premise DPAs and TOMs | `…/agreements/on-premise/data-processing-agreements.html` |
| Scope documents (incl. Success Plan) | `…/agreements/services/scope-documents.html` |
| SAP professional services GTC | `…/agreements/services/sap-professional-services.html` |
| Consulting services supplements | `…/agreements/cloud/consulting-services.html` |
| SAP cloud product policies (information only) | `https://www.sap.com/about/agreements/policies.html` |

**SDG naming/versioning:** documents are listed as `LANGUAGE v.N-YEAR` (e.g. *SAP Business Technology
Platform Service Description Guide — ENGLISH v.5-2026*). **The governing version is the one referenced in
the customer's order form**, not the latest published. Several products can share one SDG — e.g. *SAP Cloud
ERP Private; RISE with SAP S/4HANA Cloud, private edition; SAP ERP, private cloud edition* are one
document. **[V]**

**Contract structure** — four building blocks: **Order Form**, **Cloud Service Description** (the
product-specific collection containing the SDG), **Data Processing Agreement**, **General Terms and
Conditions**. The first, third and fourth apply to any cloud service on SAP's pricelist; the Cloud Service
Description is product-specific. The **Master Cloud Customer Agreement (MCCA)** is the framework agreement
across most of the portfolio. Contracts are administered in **SAP for Me → Finance and Legal Dashboard**. **[V]**

---

## Compliance FAQ points worth knowing **[V]**

The certification page's own FAQ answers several recurring questions — read them before escalating:

- *"Is SAP ISO certified?"* — ISO 9001 **since 1998**; also certified to **ISO 27001, ISO 22301 and
  BS 10012**; *"All locations worldwide work according to one common process framework."*
- *"What is the difference between a SOC 1 and SOC 2 report?"*
- *"How can I request a bridge (gap) letter?"*
- *"What compliance alignments and frameworks does SAP adhere to?"*
- *"What is the EU Artificial Intelligence Act (EU AI Act)?"*

---

## Practical retrieval notes

- **`www.sap.com` returns HTTP 403 to plain HTTP fetchers.** Use a real browser session to read these
  pages; scripted `curl`/fetch will fail. **[V]**
- The finder is a **JavaScript app** — deep-link tags work, but scraping the result list requires a
  rendering browser.
- Regional offerings are behind **tabs** (Americas / Europe / Asia Pacific); the text is not all present in
  the initial DOM.
- Prefer **SAP for Me → Portfolio & Products** for anything a customer needs to *download under
  entitlement*, and the public finder for *identifying* what exists.
