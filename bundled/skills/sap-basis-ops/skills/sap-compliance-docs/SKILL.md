---
name: sap-compliance-docs
description: >-
  Map an SAP landscape or subscription to the governance, certification and usage-rights
  documents that apply to it — the Trust Center Compliance Finder, the certification catalogue
  (ISO 27001/27017/27018/27701/42001, SOC 1/2 and bridge letters, C5, PCI DSS, CSA STAR, TISAX,
  GxP, FedRAMP, IRAP, NIS2), AI governance, ALM usage rights (Cloud ALM, Solution Manager,
  Focused Run, Tricentis), and the contract stack (order form, CSD/SDG, DPA, GTC, SLAs, TOMs).
  Use for "which ISO certificate covers my service", "SOC 2 report for", "compliance finder",
  "trust center", "do we need to license Focused Run", "service description guide", "SLA
  document", "DPA", "what did we actually buy". Locates authoritative documents — not legal or
  licensing advice.
---

# SAP Compliance, Certification & Usage-Rights Documents

Auditors, procurement and security reviews all ask the same question in different words: *"prove this SAP
service is certified / covered / licensed."* The answer is always **a specific document**, and the work is
knowing which one and where it lives.

> **Guardrail — this skill FINDS documents. It does not interpret them.**
> - **Never assert an entitlement, licence position, or compliance status from memory.** Produce the
>   document reference and quote it. If no document is found, say so.
> - **Never give legal, contractual or audit advice.** Certification scope, contract terms and audit
>   sufficiency are decisions for the customer's legal/compliance function and their **SAP account
>   executive / Customer Success Partner** — route them there explicitly.
> - **Licence questions go to SAP.** Usage rights (§6) summarise a published page; anything contested,
>   partner-specific, or money-adjacent goes to the account executive or SAP Order Management.
> - **Certificates are scoped and dated.** A certificate covering *SAP Enterprise Management* does **not**
>   automatically cover every SAP product you run. Always check the **Statement of Applicability (SoA)**
>   version and the **assessment period** — §2.
> - **Public vs entitled.** Some documents are public; others require sign-in and an entitlement. Don't
>   promise a customer a document you haven't confirmed they can obtain — §3.

Verification legend: **[V]** verified against the live source during authoring · **[G]** cited to a page or
Note.

---

## 1. The mental model: four dimensions, not a product lookup

The Trust Center's **Compliance Finder** is the authoritative index, and its own glossary defines the
dimensions: **[V, FIND]**

| Dimension | What it means (SAP's wording) |
|---|---|
| **Compliance Offering** | *"the ISO, SOC, or one of the various other compliance offering type[s] needed"* |
| **Compliance Entity** | *"the list of cloud solutions from SAP and related SAP services or functions"* |
| **Assessment Period / Issue Date** | *"the period of the assessment or the issue date of the document"* |
| **Region / Country** | *"the country where the SAP data center is located"* |

> 🚨 **The single most common mistake: searching for your product name.** Certificates are issued to a
> **Compliance Entity**, which is usually a *group* of solutions. For example an ISO 27011 certificate on
> the finder covers *"SAP Integrated Business Planning, SAP Marketing Cloud and SAP S/4HANA Cloud Public
> Edition"* as one entity, and an ISO 22301 certificate covers *SAP Intelligent Spend and Business Network*
> including *"SAP Ariba Cloud, SAP Business Network, SAP Concur Travel & Expenses, and SAP Fieldglass"*.
> **Find the entity that contains your service, then filter by offering.** **[V, FIND]**

SAP's own advice: *"Using the 'Offering Type', 'Compliance Entity', and 'Assessment Period/Issue Date'
filters instead of the search bar is the recommended and best way to locate your compliance documents."*
**[V, FIND]**

---

## 2. Read the scope before you rely on a certificate

Every certificate entry carries scope wording — and that wording is the deliverable, not the certificate
logo. Real examples from the finder: **[V, FIND]**

- *"Operations and Development of the SAP SuccessFactors Human Capital Management (HCM), Employee Central
  Payroll and SuccessFactors Payroll cloud solutions as PII Controller and PII Processor, in accordance
  with the Statement of Applicability (SoA) Version 2.6 dated, October 15, 2025."*
- *"…in accordance with the Statement of Applicability (SoA), Version 2.4 dated, January 29th, 2026"*

Three things to extract every time:

1. **Which entity and which solutions** are named.
2. **Which SoA version and date** — the SoA defines which controls are in scope.
3. **The assessment period** — and whether a **bridge letter** is needed to cover the gap between the end
   of the report period and today (§4).

---

## 3. Where the documents actually live

| Source | Contains | Access |
|---|---|---|
| **Trust Center → Compliance Finder** | the public index — **376 documents** at time of authoring | Public browse; many documents are *"available for request on this page"* |
| **SAP for Me → Portfolio & Products** | *"the central access point and the go-to destination for existing SAP customers to download eligible compliance documents on demand"* | Sign-in; **entitlement-based** |
| **My Trust Center** (support.sap.com) | announcements, report calendars, enablement resources | S-user sign-in |
| Scheme registries | e.g. **TISAX** via ENX, **FedRAMP** Marketplace, **EU Cloud CoC** public register | Public, third-party |

**Compliance Finder:**
`https://www.sap.com/about/trust-center/certification-compliance/compliance-finder.html`

It accepts a deep-link tag per offering — useful for handing an auditor a precise link: **[V, FIND]**

```
…/compliance-finder.html?tag=compliance-document:compliance-offering/<offering>
```

Offering slugs verified live: `iso-42001`, `iso-9001`, `iso-27001`, `iso-27017`, `iso-27018`, `bs-10012`,
`iso-14001`, `iso-50001`, `iso-22301`, `soc-1`, `soc-2`, `soc-1-bridge-letter`, `soc-2-bridge-letter`,
`pci-dss`, `gxp`, `csa-star`, `c5`, `canadian-cloud-compliance`. **[V, FIND]**

Full catalogue and link table: **[references/compliance-catalogue.md](references/compliance-catalogue.md)**

---

## 4. SOC reports, bridge letters and timing

- **SOC 1** — controls relevant to a customer's **internal control over financial reporting**; follows
  **SSAE 18** and **ISAE 3402**; type I (design) / type II (design + effectiveness). [G, CERT]
- **SOC 2** — **security, availability, processing integrity, confidentiality, privacy**; follows
  **ISAE 3000** and **AT 101**, based on **AICPA trust service principles**. [G, CERT]
- **Bridge letters** *"inform customers of any significant changes to their controls environments from the
  end date of the most recently completed SOC report to the issue date of the bridge letter."* [G, CERT]

**Publication cadence** — SAP publishes a *SOC & C5 Performance Calendar*; at time of authoring it stated
SOC 1 reports are *targeted for publication within 90 days after each performance period*, and SOC 2
reports follow a *12-month audit cycle*. **Check the current calendar rather than quoting these dates.**
**[V, CERT]**

> ⚠️ **Report consolidation happens.** SAP announced **SAP Central Cloud Services** SOC 1, SOC 2 and C5
> reports that *"replace the previous SOC 1 SAP Business Technology Platform, SAP Cloud Infrastructure, and
> SAP Cell and Gene Therapy Orchestration and SAP Intelligent Clinical Supply Management reports."* If an
> auditor asks for a report by an old name, it may have been folded into a newer one. **[V, CERT]**

---

## 5. AI governance — the newest and fastest-moving area

| Item | What it is |
|---|---|
| **ISO/IEC 42001** | *"the first global standard for AI management systems"* — SAP is certified; *"a structured, independently audited AI management system"* **[V, CERT]** |
| **EU AI Act governance for Joule Agents** | SAP publishes how it governs its AI agents — *"auditability, regulatory compliance, and human oversight under the EU AI Act"* — in the **SAP Joule Agents Compliance Brief** **[V, CERT]** |

Because this area changes fastest, **always re-read the Trust Center AI section rather than relying on this
skill's summary**, and treat any statement about a specific Joule capability's regulatory classification as
something to confirm in the current brief.

---

## 5a. The contract document stack — where the **Service Description Guide** sits

Certification answers *"is it secure/compliant"*. The **contract documents** answer *"what did we actually
buy, and what is SAP obliged to deliver"*. Different question, different library.

**An SAP cloud contract has four building blocks** — SAP's own wording: **[V, AGR]**

| Block | Scope |
|---|---|
| **Order Form** | pricing, scope, key terms |
| **Cloud Service Description** | ***"a product-specific collection of documents"*** — this is where the **Service Description Guide (SDG)** lives |
| **Data Processing Agreement (DPA)** | applies where the service processes personal data; *"defines SAP's obligation to maintain applicable certifications"* |
| **General Terms and Conditions (GTC)** | usage rights, ownership of customer data, warranties, limitation of liability, confidentiality |

*"The order form, data processing agreement, and general terms and conditions apply to any cloud service on
SAP's pricelist while the cloud service description is a product-specific collection of documents."*
**[V, AGR]**

> 🔗 **The DPA is the bridge between §1–4 and this section.** It obliges SAP to *maintain applicable
> certifications* — so a certificate from the Compliance Finder is often the evidence that a DPA commitment
> is being met. Auditors frequently ask for both together.

### Finding the SDG for a service

```
https://www.sap.com/about/trust-center/agreements/cloud/cloud-services.html
    ?tag=agreements:product_use_and_support_terms/service-description-guides
```

Real entries at time of authoring — note the naming: **[V, AGR]**

| Document | Version |
|---|---|
| SAP Business Technology Platform Service Description Guide | `ENGLISH v.5-2026` |
| SAP Cloud ERP Private; RISE with SAP S/4HANA Cloud, private edition; SAP ERP, private cloud edition SDG | `ENGLISH v.7-2026` |
| SAP S/4HANA Cloud Public Edition and GROW with SAP — *Service Use Descriptions* | `ENGLISH v.7-2026` |
| SAP Business Data Cloud SDG · SAP Concur SDG | `ENGLISH v.8-2026` |
| SAP Service Description for SAP MaxAttention / ActiveAttention (on-premises) | `v.3-2026` |

> 🚨 **SDGs are versioned `LANGUAGE v.N-YEAR`, and the current one is probably not yours.** The version that
> governs is **the one referenced in the customer's order form**, not the newest on the site. Always confirm
> the version before quoting an obligation — and note that several products share one SDG (RISE / Cloud ERP
> Private / SAP ERP private cloud edition are covered by a single document). **[V, AGR]**

### The rest of the agreement library

All under `…/trust-center/agreements/cloud/cloud-services.html` with a tag or search: **[V, AGR]**

| Document type | What it settles |
|---|---|
| **Service Description Guides** | functional scope of the service |
| **Supplements** | *"additional product-specific terms … additional information on the usage metrics"* |
| **Service Level Agreements** | *"system availability … service credits in case SAP fails to meet the SLA … maintenance windows"* |
| **Support schedules** | support scope and response commitments |
| **Product development schedules** | roadmap/development commitments |
| **Data Processing Agreements** | personal-data processing |
| **Security measures (TOMs)** | technical & organisational measures **for DPA purposes** |
| **List of data centers** | where the service runs — pairs with the finder's *Region/Country* filter |
| **AI terms**, **AI Code of Conduct**, **AI third-party pass-through terms** | AI-specific contractual terms — the contractual counterpart to §5's ISO 42001 / EU AI Act material |

**Framework agreement:** the **Master Cloud Customer Agreement (MCCA)** is *"a framework agreement …
that apply[ies] across most of the SAP cloud services portfolio, eliminating the need to negotiate separate
terms for each service."* Samples of the MCCA, its order form and the professional services schedule are
published; customers can request to sign the standard MCCA through **SAP for Me**. **[V, AGR]**

**On-premise and services** have their own libraries: `…/agreements/on-premise/service-descriptions.html`,
`…/agreements/services/scope-documents.html`, and separate DPA/TOM documents for support and professional
services.

**Contract administration** — view, renew and terminate contracts in **SAP for Me → Finance and Legal
Dashboard**. [V, AGR]

---

## 6. ALM usage rights — Cloud ALM, Solution Manager, Focused Run

A different question from certification: *"are we entitled to run this, and does it cost extra?"* The
authoritative page is **support.sap.com → ALM → Usage Rights**; the following is verbatim-grounded but
**must be re-checked before you act on it** — terms and dates change. **[V, ALM]**

| Product | Entitlement | Key limits |
|---|---|---|
| **SAP Cloud ALM** | Included in **SAP Cloud Service subscriptions containing Enterprise Support, cloud editions**, in **SAP Enterprise Support**, and in **Product Support for Large Enterprises**. Entitles **one tenant** | Only for the customer's **own internal ALM processes**, and only for on-prem solutions **covered by their support agreement**. Baseline **24 GB HANA memory** and **24 GB monthly outbound API data transfer** |
| **SAP Solution Manager** | **Delivered as part of the support contract** — scope depends on the maintenance agreement and is **independent of the SolMan release**. **No need to license users** for standard usage | Includes **Focused Build** and **Focused Insights** *"at no additional costs"*. Includes **SAP ASE** and **SAP HANA** licences **strictly limited to SolMan** (no hardware or services) |
| **SAP Focused Run** | **"Sold by SAP Sales Organization"** — i.e. **licensed separately**; not part of the support contract | FRUN customers *"can manage their whole IT (including non-SAP Components)"* |
| **Tricentis Test Automation for SAP** | Term licence granted with Enterprise Support / PSLE. With **Cloud ALM** granted **until 31 Dec 2028**; with **Solution Manager** **until 31 Dec 2027** | With Cloud ALM: **5 named users, 500 test runs/month, 2.5 GB storage, 5 customer-managed execution agents, 12-month result retention**. **Not available for customers in China** |

**Enterprise Support vs Standard Support for Solution Manager** — the practical difference: **[V, ALM]**

- **Enterprise Support** customers *"can manage their whole IT (including non-SAP Components)"*;
  **Standard Support** customers *"solely manage their SAP components"*.
- Enterprise-only functional scope: **Custom Code Management, Business Process Change Analyzer, Scope and
  Effort Analyzer, Business Process Analytics, SAP Test Automation, SAP HANA Deployment best practices,
  End-User Experience Monitoring**. Standard Support has the full scope *except* those.

> ⚠️ **Two constraints that catch people out:** Test Suite / test management in **both** SolMan and Cloud
> ALM *"may not be used for automation of productive business processes"* — they are for testing and
> validating business processes only. And **SAP Partners may have different usage-rights definitions** —
> the page says to contact your SAP partner manager. **[V, ALM]**

The Enterprise Support scope also applies to **Product Support for Large Enterprises** and premium
engagements such as **SAP ActiveAttention**. **[V, ALM]**

---

## 7. Answering "which of these applies to us?"

A repeatable sequence — the deliverable is a **table of documents**, not an opinion:

1. **Inventory what is actually subscribed / deployed.** Cloud subscriptions from **SAP for Me →
   Portfolio & Products**; on-prem from the landscape ([sap-health-triage](../sap-health-triage/SKILL.md)
   for reading SIDs and releases).
2. **Map each service to its Compliance Entity** (§1) — this is the step people skip.
3. **Pick the offerings the requester actually needs** — an ISO 27001 certificate answers a different
   question from a SOC 2 Type II report or a C5 attestation.
4. **Check scope + SoA version + assessment period** (§2), and whether a **bridge letter** is required (§4).
5. **Confirm obtainability** — public on the finder, or entitled via SAP for Me (§3).
6. **Record the gaps honestly.** "No document found for X" is a valid, useful answer; inventing coverage is
   not.
7. **Route judgement calls** — scope adequacy, contractual terms, licence positions — to the account
   executive / Customer Success Partner and the customer's own compliance function.

Deliverable shape:

| Service | Compliance entity | Offering | Document + SoA/period | Source | Obtainable |
|---|---|---|---|---|---|
| SAP SuccessFactors HCM | SAP SuccessFactors | ISO 27701 | cert, SoA v2.6, 2025-10-15 | Compliance Finder | public |
| … | … | SOC 2 Type II | report + bridge letter | SAP for Me | entitled |

---

## OS note

**Not applicable — this skill is entirely OS-independent.** It concerns published documents and portal
navigation, with no commands on any platform. It is included in `sap-basis-ops` because the person asked
to produce audit evidence for a landscape is usually the same person who administers it.

---

## Cross-references

- **`sap-software-download`** — entitlement-gated downloads in SAP for Me; the same S-user and portal.
- **`sap-client-copy-accelerator`** — §0a: why a HANA Smart Data Access licence answer lives in the SDG, not in an SAP Note.
- **`sap-oracle-dataguard`** — Oracle option licensing (Notes 740897 / 581312) for the database layer.
- **`sap-sscr-keys`** — the other SAP for Me entitlement workflow.
- **`sap-support-case`** — the support entitlement behind what you may raise, and at what priority.

## Execution discipline (non-negotiable)

### The holy rule — nothing runs unbacked

**Every command executed must be traceable to one of exactly three things:**

1. an **official SAP source** — help.sap.com page / Operations or Administration Guide, or
2. an **SAP Note / KBA**, or
3. an **explicit instruction from the user**.

If a command is backed by none of those, **do not run it** — say what backing is missing and stop.
"It's probably fine", "this is standard", and "I recall the syntax" are not backing. When the backing is
a source, name it (page or Note number) alongside the command; when it is the user, quote the instruction.

### Ambiguity ⇒ stop and confirm, before any execution

If executing would require **assuming** anything the user did not state, you are **obliged** to confirm
first. Never fill a gap with a plausible default. Common gaps that force a stop:

- **client number**, SID, instance number, target host/node
- **read-only vs state-changing** — if it is not explicit which was wanted, ask
- **scope** — one instance vs the whole system, one tenant vs all, one client vs cross-client
- which **database / dbms_type**, which environment (**PRD vs non-PRD**)
- retention/age cut-offs, recovery points, target of a restore, transport target

A wrong assumption here is not a typo — it is the difference between reading a log and stopping production.

### But verify programmatically FIRST — *then* ask

**Asking the user for something the system can answer is a failure.** Before you raise a question, ask
the user to go and look, or request Computer Use / GUI access, you **must** first try to determine it
programmatically. Only what genuinely cannot be derived — intent, authorization, a business decision, a
value that exists only in the user's head — is a legitimate question.

| Determine programmatically (do NOT ask) | Ask the user (cannot be derived) |
|---|---|
| Which DB — `echo $dbms_type`, profile `dbms/type` | Which **client** to act on |
| SIDs / instances / hosts / ports — `sapcontrol … GetSystemInstanceList`, `ls /usr/sap` | Whether this system is in scope / approved |
| Is it up, is the DB up — `GetProcessList`, `R3trans -d` | PRD change approval, downtime window |
| Kernel / release / patch — `disp+work -version`, `saphostexec -version` | The intended recovery point or retention policy |
| Which clients **exist** — table `T000` | Which of those clients is **meant** |
| Free space, log locations, parameter values — `df -h`, `sappfpar`, profile | Business impact / urgency |

Order, always: **verify programmatically → ask only what remains → never assume.**

### Prefer programmatic over manual or GUI

**Work down this ladder. Take the highest rung that does the job — and within that rung, the lowest
privilege that suffices. Never skip a rung because you assume it is unavailable (see the burden of
proof below).**

| # | Path | Privilege | Notes |
|---|---|---|---|
| **1** | **REST / OData** — `GET` first | Narrowest. Scoped service user | Read-only by construction when you stay on `GET`. `$metadata` gives you the contract |
| **2** | **SOAP / web service** | Scoped service user | Typed contract via `?wsdl`. Client-cert auth where offered — no password in a script |
| **3** | **RFC / BAPI** (`creds exec`, JCo, `pyrfc`) | RFC user with `S_RFC` | **For ABAP *writes*, prefer this over 1–2**: BAPIs have real commit/rollback semantics and land in SM19/SM20 |
| **4** | **OS shell as the *correct* user** → **DB utility** | ⚠️ Escalates — see below | The chain matters more than the rung |
| **5** | **Browser automation** (headless or in-app) | Interactive user | Session-based UIs only. Fragile across releases |
| **6** | **Computer Use / screen driving** | Interactive user | **Last resort.** Not repeatable, not diffable, breaks on any UI change |

> ## ⚠️ Rung 4 is a chain, and each link widens the blast radius
>
> ```
> ssh <host>                    ← host access
>   → su - <sid>adm             ← SAP admin: can stop/start the system
>   → su - ora<sid> / syb<sid>  ← DB owner: can drop data
>   → sudo / root               ← everything
>        → hdbsql | isql | dbmcli | sqlplus | db2   ← the actual command
> ```
>
> **Stop at the least-privileged user that can run the command.** Most read-only checks need only
> `<sid>adm`; DB utilities usually need the DB owner; **root is almost never the right answer** and
> `saproot.sh` is the rare legitimate exception. Say which user you used and why.

> ## Two axes, and they do not agree
>
> The ladder ranks by **automation quality** — repeatable, reviewable, loggable, diffable. Privilege
> runs on a *different* axis and is **worst in the middle**: rung 4 (OS/root) can destroy a system,
> while rung 6 (Computer Use) is merely an interactive user clicking. So Computer Use ranks last for
> *reproducibility*, not because it is the most dangerous.
>
> **The practical rule: prefer the highest rung, but never escalate privilege to climb it.** A
> read-only OData call beats an RFC that needs a write-capable user; an `<sid>adm` shell beats a root
> shell. If climbing a rung requires more privilege than the task needs, stay where you are and say so.

> ## 🛑 You must **demonstrate** the absence of a programmatic path, not assume it
>
> "There is no API for this" is a **finding that requires evidence**, not a default. Before dropping to
> rung 5 or 6, actually probe:
>
> - **HTTP status codes tell you the access mode.** `401` → Basic auth works, **scriptable**.
>   `302` regardless of credentials → session UI, browser needed. `404` → not deployed. `503` →
>   deployed but stopped.
> - **Look for a contract**: append `?wsdl`, `$metadata`, `/api`, `?sap-client=` and see what answers.
> - **Ask the platform what it exposes**: `sapcontrol -function J2EEGetApplicationAliasList`,
>   `hdbcons help`, `btp --help`, `xs help`, `<tool> -h`.
> - **A Swing or WebDynpro *UI* being un-automatable does not mean the *objects* are.** The editor and
>   the API are different doors — check for the second before declaring the first is the only one.
>
> Programmatic execution is repeatable, reviewable, loggable and diffable; screen-driving is none of
> those. When you do drop to a lower rung, **say which rung you are on and what you probed** to rule
> out the higher ones — so the user can correct you if they know of a path you missed.

### Ask how output should be handled

Work that produces evidence (logs, traces, command output, screenshots, reports) has two reasonable
endings. **Ask which the user wants** rather than guessing:

- **(a) persist it** — write the output/logs/screenshots to a file, and say exactly where; or
- **(b) execute and report** — just run it and give a short final status summary.

Don't dump large output into the conversation unasked, and don't silently discard evidence either — for
troubleshooting and any change with a rollback, (a) is usually the right default to offer.

## Run as the correct OS user

**Identify the right OS user *before* running anything, and switch with a login shell.** Wrong-user
execution is a top cause of SAP failures, and the damage outlives the command: files created by `root`
under `/usr/sap`, `/sapmnt` or a DB directory break every later start by the real owner. A login shell
also matters because each user carries the environment the tools need (`SAPSYSTEMNAME`, `ORACLE_HOME`/
`ORACLE_SID`, `SYBASE`, `DB2INSTANCE`, library paths) — without it, commands fail or act on the wrong system.

| What you're operating | UNIX user | Windows |
|---|---|---|
| SAP instances — `sapcontrol`, `startsap`/`stopsap`, `tp`, `R3trans`, `disp+work`, `sappfpar`, `cleanipc` | **`<sid>adm`** (lower-case **SAP** SID) | `<SID>adm`; services run as `SAPService<SID>` |
| SAP HANA — `HDB`, `hdbsql`, `hdbnsutil` | **`<sid>adm` of the HANA SID** (e.g. `h10adm` — may differ from the SAP SID) | n/a (HANA server is Linux-only) |
| Oracle — `sqlplus`, `lsnrctl`, BR\*Tools | **`ora<dbsid>`** (BR\*Tools also runs as `<sid>adm`; generic installs may use `oracle`) | `<SID>adm`; DB runs as a service |
| SAP ASE — `isql`, `startserver`, Backup Server | **`syb<dbsid>`** | `syb<dbsid>` / `SAPService<SID>` |
| IBM Db2 — `db2start`/`db2stop`, `db2` CLP | **`db2<dbsid>`** (the instance owner = `DB2INSTANCE`) | same; Db2 runs as a service |
| SAP MaxDB / liveCache — `dbmcli`, `x_server` | **`sdb`** (software owner, group `sdba`) + a DBM operator at DB level | install/service account |
| MS SQL Server — `sqlcmd`, service control | n/a (Windows-only for SAP) | `<SID>adm` / the SQL Server service account |
| SAP Host Agent — `saphostexec`, `saphostctrl` | **`root`** | Administrator / `SAPHostExec` service |

**Rules**

- **Switch with a login shell:** `su - <user>` (the `-` is what loads the environment) or `sudo -iu <user>`.
  Windows: use the correct account, or an elevated shell only where documented.
- **`root` only where the procedure explicitly says so** — e.g. `saproot.sh` after a kernel extract, SAP Host
  Agent install/upgrade. Never as a shortcut around a permission error; that is how root-owned files get
  created and break the system later.
- **Verify before acting:** `whoami` / `id`, plus the env actually being set (`echo $SAPSYSTEMNAME`,
  `echo $ORACLE_SID`, `echo $DB2INSTANCE`, `echo $SYBASE`).
- **State the user in every command you hand over** (e.g. "as `<sid>adm`:"), and if the required user is not
  available, say so and stop — do not substitute another user.

## Staying current — check SAP Notes first

SAP Notes supersede this file. Landscapes differ by release, patch level, DB and OS, and SAP changes
procedures via Notes/KBAs between doc revisions.

**If the [SAP Notes MCP](https://github.com/marianfoo/sap-mcp-servers) is configured, use it before
acting on anything version-specific** — especially any destructive step, or when a command here doesn't
behave as documented:

1. `search` the topic (e.g. the component + symptom, or a Note number cited below).
2. `fetch` the promising Note IDs for the current text, validity (affected releases/components),
   prerequisites and side effects.
3. **Check the `attachments` array.** SAP routinely puts the actual deliverable *in an attachment* rather
   than the Note body — sizing guides, SQL script collections, configuration PDFs, spreadsheets. A Note
   whose text says "see the attached document" is not fully read until you have it.
4. Prefer the Note over this file where they disagree, and say which Note you followed.

**Downloading an attachment:** `fetch` returns `attachments[].url` **and `attachments[].filename`**;
**`fetch_attachment`** retrieves the bytes. Pass the URL verbatim — the URLs are opaque and cannot be
constructed. If your MCP build predates that tool, open the URL in a signed-in browser instead and say the
file was fetched manually.

> ⚠️ **Two ways a hand-rolled fetch goes wrong — both verified.**
> **1. Trusting the status code.** An unauthenticated request returns **HTTP 200 with a small HTML login
> stub**, not an error. Check the content type and magic bytes, or you save a JavaScript redirect page
> under a `.pdf` name.
> **2. Naming the file from the URL.** SAP serves many attachments from a *generic endpoint* —
> `…/services/attachment.htm?iv_key=…&iv_guid=…` — so the URL basename is `attachment.htm` even when the
> payload is a 24-page PDF. Take the name from **`attachments[].filename`** or the response's
> **`Content-Disposition`** header, never from the URL path.

No MCP available? Look the Note up on `me.sap.com/notes/<id>` and say the check was skipped rather than
assuming this file is current.

## Sources

- **[CERT]** **SAP Trust Center — Certifications and Compliance**. **[V]** Read live during authoring via a
  rendering browser. Source for: the global offering catalogue (ISO/IEC 42001, 9001, 27001, 27017, 27018,
  22301, 14001, 50001, BS 10012), the SOC 1 / SOC 2 / bridge-letter definitions and their auditing
  standards (**SSAE 18 / ISAE 3402** for SOC 1; **ISAE 3000 / AT 101** and AICPA trust service principles
  for SOC 2), the **SOC & C5 Performance Calendar** cadence, the **SAP Central Cloud Services** report
  consolidation, **ISO/IEC 42001** as *"the first global standard for AI management systems"*, **EU AI Act
  governance for Joule Agents**, the regional schemes (FedRAMP, CMMC/NS2, Canadian PBMM/PBHVA/CGP,
  KRITIS/NIS2), and the compliance FAQ.
  https://www.sap.com/about/trust-center/certification-compliance.html
- **[FIND]** **SAP Trust Center — Compliance Document Finder**. **[V]** Read live during authoring;
  **376 results** at that time. Source for the four filter dimensions and their glossary definitions
  (*Compliance Offering*, *Compliance Entity*, *Assessment Period/Issue Date*, *Region/Country*), SAP's own
  recommendation to *"[use] the 'Offering Type', 'Compliance Entity', and 'Assessment Period/Issue Date'
  filters instead of the search bar"*, the `?tag=compliance-document:compliance-offering/<slug>` deep-link
  pattern with the slugs listed in the catalogue, and the real scope/SoA wording quoted in §2 (SuccessFactors
  ISO 27701 SoA v2.6; ISO 27011 covering IBP + Marketing Cloud + S/4HANA Cloud Public Edition; ISO 22301
  covering SAP Ariba Cloud, SAP Business Network, SAP Concur and SAP Fieldglass).
  https://www.sap.com/about/trust-center/certification-compliance/compliance-finder.html
- **[ALM]** **SAP Support Portal — Application Lifecycle Management → Usage Rights**. **[V]** Read live
  during authoring. Source for all of §6: SAP Cloud ALM entitlement (Enterprise Support cloud editions /
  SAP Enterprise Support / Product Support for Large Enterprises, **one tenant**, internal ALM use only,
  **24 GB HANA memory** and **24 GB monthly outbound API data transfer** baselines); SAP Solution Manager
  being *"delivered as part of the support contract"* with scope *"independent of the SAP Solution Manager
  release"*, **Focused Build and Focused Insights at no additional cost**, included **SAP ASE / SAP HANA**
  licences *"strictly limited to SAP Solution Manager"*, and *"No need to license Users for standard
  usage"*; the Enterprise vs Standard Support split and the seven Enterprise-only functionalities; **SAP
  Focused Run** being *"sold by SAP Sales Organization"*; the Tricentis term-licence dates (**31 Dec 2028**
  with Cloud ALM, **31 Dec 2027** with Solution Manager) and metrics (5 named users, 500 test runs/month,
  2.5 GB storage, 5 execution agents, 12-month retention, **not available in China**); the prohibition on
  using test tooling *"for automation of productive business processes"*; and the footnotes that partners
  may have different usage-rights definitions and that Enterprise Support scope also covers Product Support
  for Large Enterprises and premium engagements such as SAP ActiveAttention.
  https://support.sap.com/en/alm/usage-rights.html
- **[AGR]** **SAP Trust Center — Agreements**, and the **Cloud Services** document finder. **[V]** Read live
  during authoring. Source for §5a: the four contract building blocks and the wording *"The order form, data
  processing agreement, and general terms and conditions apply to any cloud service on SAP's pricelist while
  the cloud service description is a product-specific collection of documents"*; the definitions of
  **supplement**, **SLA** and **DPA** (including that the DPA *"defines SAP's obligation to maintain
  applicable certifications"*) and **GTC**; the **MCCA** framework agreement and its published samples;
  contract administration via **SAP for Me → Finance and Legal Dashboard**; the deep-link tags for every
  agreement type including **Service Description Guides**, **AI terms**, **AI Code of Conduct**, **AI
  third-party pass-through terms** and **Security measures (TOMs)**; and the live SDG listing with its
  `LANGUAGE v.N-YEAR` versioning (e.g. *SAP Business Technology Platform Service Description Guide —
  ENGLISH v.5-2026*, *SAP Cloud ERP Private; RISE with SAP S/4HANA Cloud, private edition; SAP ERP, private
  cloud edition — ENGLISH v.7-2026*). https://www.sap.com/about/trust-center/agreements.html
- **[KBA]** **SAP KBA 2878553** — *SAP Solution Manager 7.2 Usage Rights*. The Note-form counterpart to the
  usage-rights page; fetch it with the SAP Notes MCP for the version current to your agreement.
- **[SFM]** **SAP for Me → Portfolio & Products** — *"the central access point and the go-to destination for
  existing SAP customers to download eligible compliance documents on demand"*, per the Trust Center. **[V]**
  Entitlement-gated. https://me.sap.com/

**To confirm/deepen** — this domain changes faster than any other in this repo. **Always re-read the
Compliance Finder and the Usage Rights page before quoting anything to a customer or auditor**; certificate
scopes, SoA versions, report consolidations and licence dates all move. For usage rights, also fetch
**KBA 2878553** via the SAP Notes MCP. And for anything contractual, the answer is the **account executive
or Customer Success Partner** — not this skill.
