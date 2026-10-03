---
name: sap-support-case
description: >-
  Raise an SAP support case (incident) properly — earn it first by exhausting the supported remedies,
  route it to the right component using SAP's own routing KBAs rather than the component name the
  error text happens to print, gather the IDs SAP will ask for (correlation ID, formation/job ID,
  troubleshooting key), set an honest priority against SAP's published definitions, and get the
  subject and description right BEFORE submitting — the case wizard buries them in an early step and
  will happily submit a stale description written before you fixed half the problem. Covers the
  multi-step case wizard's navigation traps, the business-impact fields that unlock at High, the
  troubleshooting key as a customer consent decision, and what to do when a case goes out wrong.
  Use this whenever raising, drafting, routing or correcting an SAP case or incident, and for
  "raise an SAP ticket", "open a case with SAP", "create SAP incident", "which component should I
  use", "case priority high or medium", "SAP wants a correlation ID", "troubleshooting key",
  "my case was rejected", "SAP bounced my ticket", "case has the wrong description", "submit case
  to SAP". Reach for it even when the user just says "let's log this with SAP".
---

# Raising an SAP support case

**Field-derived.** Built from a live BTP/Joule case raised on a customer landscape — including the
mistakes made while raising it. Marks: **[F]** observed in the field, **[V]** verified against SAP
documentation, **[G]** cited but not read in full.

> ## The one-line version
>
> **A case is a claim that SAP's product is at fault.** Everything before submitting is about earning
> the right to make that claim — and everything in the form is about making it **routable** and
> **honest**. Most bounced cases fail one of those two, not both.

---

## 1. Earn it — most "SAP bugs" are configuration

Before you open the form, three gates. On the field case, **the first one dissolved the original
problem entirely**. **[F]**

### Gate 1 — has the *supported automation* been tried?

A subscription failed twice with a hard error code, and a case looked justified. Then the **booster**
(SAP's own guided automation) completed it first try. Cause: the manual attempts used the **wrong
application and plan**; the booster picked the right pair. **[F]**

| | Application | Plan | Result |
|---|---|---|---|
| Manual attempts ×2 | `<app>-ias` | `default` | **Failed** |
| Booster | `<app>` | `foundation` | **Succeeded, first try** |

**No product defect existed.** A case would have consumed SAP's time and the customer's, and been
closed as configuration.

> **Generalise it:** if SAP ships a booster, a guided procedure, a wizard, or a "recommended
> configuration" path for what you are doing by hand — **run it before raising anything**. When it
> succeeds, compare what it chose against what you chose. That difference *is* your root cause.

### Gate 2 — has SAP's own prescribed remedy been run, and run *twice*?

Error panels frequently name the first step themselves (*Resynchronize*, *Retry*, *Repair*). Run it.
Then **run it again** — on the field case the first run cleared 2 of 3 failures and looked like
progress, but the second settled back to all three. **[F]**

That second run is what turns *"it didn't work"* into *"it reproducibly does not clear"* — which is
the difference between a case SAP can act on and one they bounce for more information.

### Gate 3 — can your own side be ruled out?

State explicitly why this is not yours. On the field case: the failing sync ran **entirely between
SAP-hosted tenants** and never traversed the Cloud Connector, so none of the customer's open
connectivity items could explain it. **[F]**

A case that says *"we have eliminated X, Y and Z because the failing path does not touch them"* is
triaged faster than one that says *"it doesn't work"*.

---

## 2. Route it — the component is where cases go to die

> ## 🛑 Do not trust the component name in the error text
>
> On the field case the error message said **raise a ticket to component `CA-JOULE-TA`** — while the
> panel header for the same error said **`CA-JOULE-PRV`**. They disagreed. **[F]**
>
> **SAP publishes routing KBAs that resolve exactly this**, and the routing rule was not "use the
> name in the message" — it routed by **which system returned the error**. By that rule all three
> failures pointed to **`-PRV` (Provisioning)**, not the `-TA` the text named. **[F]**
>
> Had the case gone to the component the error text printed, it would have been re-routed by SAP and
> lost a day.

**The routing procedure:**

1. **Read what the error actually says** — capture the component *and* the panel header, and note if
   they differ.
2. **Search for a routing KBA** for that product area before accepting either. Terms that work:
   `<product> which component`, `<product> routing`, `<error text> component`.
3. **Read the recommended KBAs the case form surfaces** as you type. The form suggests solutions
   based on your text — on the field case it surfaced two, one a **red herring** (covered a
   different error variant) and one **decisive** (the official routing table). **[F]** Read both;
   do not skim past them because you have already decided to raise.
4. **Verify the component exists** in the picker and that its description matches your problem
   (*"Joule > Tenant Administration"* vs *"Provisioning"* — the words matter).

> **A routing KBA beats an error string.** Error text is written once by a developer; routing KBAs
> are maintained by the support organisation that has to triage the result.

---

## 3. Gather the IDs before you open the form

SAP will ask for these, and hunting for them mid-form is how you end up submitting a half-finished
case. Collect them first. **[F]**

| Item | Why |
|---|---|
| **Correlation ID** | Ties your failure to SAP's own server-side trace. Usually in the technical-details panel |
| **Object ID** — formation / job / subscription / instance GUID | Lets SAP find the artefact without asking |
| **Troubleshooting key** | Grants SAP support access to diagnostics for that object — **see the consent gate below** |
| **Exact error text** | Verbatim, not paraphrased, including any codes |
| **Timestamps + timezone** | When it failed, and when you last retried |
| **What you already tried** | Gate 1–3 results, so SAP does not ask you to repeat them |

> ## 🛑 A troubleshooting key is a consent decision, not a technical step
>
> Generating one typically **grants SAP access to sensitive information** about the object. That is
> **the customer's call, not yours**. On the field case the dialog was **cancelled** and the question
> put to the user; only after explicit approval was the key generated. **[F]**
>
> Treat it exactly like the licence gate in `sap-client-copy-accelerator`: present what it grants,
> ask, wait for an explicit yes. Do not generate one to "have it ready".
>
> **And never paste a troubleshooting key into a chat transcript, commit, or shared doc** — it is an
> access grant with a lifetime. Put it in the case and nowhere else.

**Verify your own GUIDs before using them.** On the field case a polling loop ran for a while against
a **wrong subaccount GUID** — it returned "not found", which read as "nothing is happening" rather
than "you are looking in the wrong place". **[F]** Confirm every ID against the cockpit or CLI rather
than reusing one from earlier notes.

---

## 4. Priority — honest, and it costs you fields

Priority is set from **business impact**, and SAP publishes definitions (Note **67739**) **[G]**.
Claiming a level you cannot justify gets the case downgraded and delays it.

| Impact selected | Effect |
|---|---|
| *Seriously affected* | → **High** **[F]** |
| Choosing High | **Unlocks further required fields** — impact category and a business impact statement **[F]** |

**Category:** pick the honest one. On the field case, *"Go-live impacted"* was right because nothing
**productive** was down — a project milestone was at risk, not live business. **[F]**

> ## Leave what you do not know blank
>
> The form asks for **financial loss, go-live date, affected user counts, consultant counts**. On the
> field case these were **left blank deliberately** — the numbers were not known, and inventing them
> to make the form look complete would have put fiction into a contractual record. **[F]**
>
> An honest blank is better than a confident guess. If the customer knows the numbers, ask them; if
> they do not, submit without.

**The business impact statement** is the one free-text field that genuinely changes triage. Write
what *cannot happen* because of this, not how the error looks.

---

## 5. The wizard will let you submit a stale case — this is the real trap

> ## 🛑 What actually went wrong in the field
>
> The case was **submitted carrying a description written before the booster fixed half the
> problem**. It described an error that had already been resolved. **[F]**
>
> How: the wizard is multi-step, **subject and description live in an early step**, and the
> Continue-driven flow **skipped a step** on the way to Submit. The later steps show component,
> priority and contact — everything *except* the text that was stale — so the final review looked
> correct.

**The shape of the wizard** (labels vary by product, the structure does not) **[F]**:

| Step | Contains |
|---|---|
| **1** | System/product selection — **and the subject + description** |
| **2** | Scope: subaccount / org / space (BTP), or system details |
| **3** | Product/component detail, **SAP's recommended KBAs**, attachments |
| **4** | Primary contact |
| **5** | Review and **Submit** |

**Therefore, before clicking Submit:**

- [ ] **Navigate back to Step 1 and re-read the subject and description.** They were written earliest
      and are the most likely to be stale.
- [ ] Confirm the description reflects what is **still broken**, not what was broken when you started.
- [ ] Confirm the component matches your §2 routing conclusion — not an earlier guess.
- [ ] Confirm every ID from §3 is actually in the text.
- [ ] Confirm no step was skipped.

> **Navigation is hostile, and that is part of the trap.** On the field case the **left rail was not
> clickable**, so returning to an earlier step meant walking back with **Back** one step at a time;
> the Back button **overlapped a card**, so coordinate-clicking hit the wrong element and opened
> **stray tabs**. Using **element references instead of coordinates** fixed it. **[F]**
> See `sap-nw-java-pi` and the programmatic ladder — this is rung 5/6 work, and it is fiddly by nature.

---

## 6. When a case goes out wrong — correct it immediately

It happened in the field; it will happen again. **[F]**

1. **Say so at once**, to the user, before anything else.
2. **Post a reply on the case** with the corrected position — what has since been resolved, what
   remains, and the current error. A case's first customer reply is read during triage; a correction
   posted within minutes usually lands before a human picks it up.
3. **Do not open a second case.** Duplicates get merged and slow triage.
4. **Fix the component too** if the correction changes the routing — ask SAP to re-route in the same
   reply rather than assuming they will notice.
5. **Re-state the priority justification** if the resolved part was what justified the level. A case
   whose impact has shrunk should be downgraded by you, not discovered by SAP.

> A case is a **record**, not a message. Leaving a description standing that you know is wrong is the
> same failure as leaving a wrong claim in a change record.

---

## 7. Quick checklist

**Before the form**
- [ ] Supported automation (booster/wizard/guided procedure) tried — and its choices compared to yours
- [ ] SAP's prescribed remedy run **twice**, result reproducible
- [ ] Own side explicitly ruled out, with the reason
- [ ] Component determined from a **routing KBA**, not the error string
- [ ] Correlation ID, object ID, exact error text, timestamps collected
- [ ] Troubleshooting key: **asked the customer**, generated only on explicit approval

**In the form**
- [ ] Priority matches real business impact; unknown numbers left blank
- [ ] Business impact statement says what cannot happen
- [ ] Recommended KBAs actually read
- [ ] **Went back to Step 1 and re-read subject + description**
- [ ] No step skipped

**After**
- [ ] Case number recorded
- [ ] Anything stale corrected by reply immediately
- [ ] Troubleshooting key not left in chat, commits or shared docs

---

## Cross-references

- **`sap-security-patch`** — SAP Notes/KBA search is the same muscle; most cases should start as a Note search.
- **`sap-health-triage`** — gather the evidence a case needs before claiming a product fault.
- **`sap-client-copy-accelerator`** — §0a is the same consent-gate pattern used here for the troubleshooting key.
- **`sap-btp-cli`** — verifying GUIDs and subscription state from the CLI rather than trusting a stale note.
- **`sap-compliance-docs`** — the support entitlement behind what you may raise and at what priority.

---

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

| # | Source | Read |
|---|---|---|
| **[SC1]** | **Field record** — BTP/Joule case raised on a customer landscape, Sep 2026. Source of every **[F]** mark: the booster dissolving a case that looked justified, the component conflict between error text and panel header, the routing-KBA resolution, the troubleshooting-key consent gate, the priority field cascade, the skipped wizard step, and the case submitted with a stale description | **[F]** |
| **[SC2]** | **SAP Note 67739** — *Priorities of problem messages* (SAP's published priority definitions) | **[G]** — cited; the Notes service returned a stub rather than content when this skill was written, so the definitions here are **not** quoted. **Read it before arguing a priority.** |
| **[SC3]** | **Product routing KBAs** — SAP publishes per-area KBAs mapping an error to the correct component. Found by searching `<product> which component` / `<product> routing` / the error text | **[F]** — the mechanism is field-proven; the specific KBA number is product-dependent |
| **[SC4]** | SAP for Me → **Support Case** wizard; the in-form "recommended solutions" list | **[F]** — structure and navigation behaviour observed directly |

> **Why so much [F] and so little [V].** SAP documents the *case form*, but not the *judgement* —
> when a case is justified, how to resolve a component conflict, or that the wizard will let you
> submit stale text. Those came from doing it. Where SAP does publish something authoritative
> (priority definitions, routing KBAs), this skill points at it rather than paraphrasing.

> **Product specifics change.** Wizard step labels, field names and component IDs move between SAP
> for Me releases and product areas. The **sequence** — earn it, route it, gather IDs, price it
> honestly, verify the text before submitting — is what carries over.
