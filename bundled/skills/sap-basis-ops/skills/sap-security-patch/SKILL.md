---
name: sap-security-patch
description: >-
  The monthly SAP Security Patch Day workflow — retrieve the current month's Security Notes from
  the Support Portal, narrow them to the subset that applies to THIS system (installed component
  versions + kernel), compare against what is already applied (System Recommendations / Focused
  Run / RSECNOTE), prioritize by CVSS/HotNews, and implement via SNOTE. Use for "check this
  month's SAP security notes", "which security notes apply to <SID>", "SAP patch day",
  "HotNews", "compare released notes vs applied".
---

# SAP Security Patch Day

SAP publishes Security Notes on the **second Tuesday of each month (~09:00 CET)**. This skill turns "the
month's notes" into "the prioritized subset that applies to *your* system and isn't applied yet." [P1]

> **Guardrail — patching is change management, not a shell command.**
> - **Never apply notes directly to PRD.** Path is **DEV → QAS → PRD** via the transport route.
> - **HotNews first:** CVSS **9.0–10.0** notes within your emergency-patch SLA; then High (7.0–8.9). [P2]
> - Take a **backup/snapshot** and check each note's **prerequisites, manual pre/post steps, and side
>   effects** before implementing (SNOTE shows dependencies).
> - This skill **produces the analysis and plan**; it does not auto-apply. Implementation is a human,
>   change-controlled action.

---

## 1. Cadence & priority model

- **When:** 2nd Tuesday monthly. Track it as a recurring task. [P1]
- **Priority (CVSS v3):** **HotNews** 9.0–10.0 · **High** 7.0–8.9 · **Medium** 4.0–6.9 · **Low** <4.0.
  HotNews = "very high" priority, patch fastest. [P2]
- **Note types:** ABAP **correction** notes (→ SNOTE), **kernel/SP** notes (→ SUM/SPAM, not SNOTE),
  **manual/config** notes (parameter or config change). Know which before planning (§5).

---

## 2. Retrieve the month's Security Notes (browse)

The authoritative source is the **SAP Support Portal → "SAP Security Notes"** (ONE Support Launchpad /
SAP for Me). It is **behind S-user authentication**, so retrieval needs an authenticated session: [P1]

- **Browser (authenticated):** open the SAP Security Notes / Patch Day page and read the current month's
  list — number, title, component, **CVSS/priority**, released-on. (Same authenticated-browser approach
  used elsewhere in this plugin for `me.sap.com`.)
  - SAP Security Patch Day: `https://support.sap.com/en/my-support/knowledge-base/security-notes-news.html`
  - Monthly list / filter: the **SAP Security Notes** app on `me.sap.com`.
- **SAP Notes MCP (once its content path is fixed):** the reverse-engineered `snogwsmynotes` search
  supports a document-type filter — filter to security notes and the month, then `fetch` each note's
  Header (CVSS/priority/component) + LongText. See the plugin's SAP Notes MCP notes.

Capture for each note: **Number, Title, Component, CVSS, Priority, affected software-component versions.**

---

## 3. Narrow to YOUR applicable subset

A note only applies if the system **has the affected software component at an affected version** (and, for
kernel notes, the affected kernel). Build the system's inventory, then intersect:

- **Installed component versions:** `System → Status → Component information` in SAP GUI, or **SM51** →
  release info, or table **`CVERS`** (e.g. `SAP_BASIS 758`, `SAP_ABA`, `SAP_UI`, `S4CORE`, …).
- **Kernel version:** `disp+work -version` (OS shell) or SM51 → kernel info.
- **Intersect:** keep only notes whose *affected component + version range* overlaps the system's. Drop
  notes for components you don't have installed. This intersection **is the "applicable subset."**

> Doing this by hand is error-prone at scale — **System Recommendations (§4) computes this subset
> automatically** from the managed system's real note/patch status. Use it as the source of truth; use the
> manual intersect above when SysRec/FRUN isn't available.

---

## 4. Compare against what's already applied

| Tool | What it does | Where |
|------|--------------|-------|
| **System Recommendations (SysRec)** | weekly, compares SAP's released notes against a **managed system's actual note status** and lists the ones to apply — including security notes each Patch Day | SAP Solution Manager (`/nSYSTEM_RECOMMENDATIONS` / SM work center) [P3] |
| **SAP Focused Run — CSA** | Configuration & Security Analytics; superior at-scale security-note validation across a landscape | SAP Focused Run [P4] |
| **`RSECNOTE`** | older report listing security-relevant notes and their implementation status | SE38 / directly on the system [P5] |
| **SNOTE** | per-note implementation **status** (New / Can be implemented / Completely implemented / Obsolete) | Note Assistant on the system [P5] |

The output you want: **notes in the applicable subset (§3) whose status is NOT "Completely implemented."**
Those are the action items.

---

## 5. Prioritize & plan

1. **HotNews (CVSS 9–10)** → emergency change, fastest SLA.
2. **High (7–8.9)** → next scheduled window.
3. Group by **implementation tool**: SNOTE (correction notes) vs **kernel/SP** (SUM/SPAM, need downtime)
   vs **manual/config**.
4. Note **prerequisites & sequence** (SNOTE resolves dependency notes; some require an SP first).
5. Record CVSS, affected component, and the change reference for each.

---

## 5a. Know what kind of correction the note carries — CI vs **TCI**

Before planning, determine **how** the note delivers its fix. This changes the effort, the prerequisites
and the downtime.

| | **Classic CI** (correction instruction) | **TCI** (Transport-Based Correction Instruction) |
|---|---|---|
| Delivery | Correction instructions embedded in the note; SNOTE patches existing objects | A **transport** (package downloaded from SAP), imported into the system |
| Used when | changes to **existing** repository objects | the fix needs **new objects** (new tables, DDIC, function modules) that a classic CI cannot create |
| Applied via | **SNOTE** | **SNOTE** with TCI enabled — needs a minimum **SPAM/SAINT** level and one-time setup [P6] |
| Effort | usually low | higher: transport import, prerequisites, more caution |

**Structure worth internalising:** a correction instruction is bound to a **software component *and* a
release range**. A note with 11 corrections typically has **one CI per release** — e.g. SAP Note 3096734
carries 11 CIs for SAP_BASIS 700, 701, 702, 731, 740, 750… Only the CI matching *your* component version
applies. That's why "does this note apply to my stack" is answered by the correction/validity ranges, not
by the note title.

**How to tell them apart:**
- In SAP for Me: a TCI note says so in its text and its correction row carries a **download link** for the
  transport package; a classic CI has none.
- **Via the SAP Notes MCP** (`fetch(id, includeCorrections=true)`): each entry in `correctionDetails`
  carries `softwareComponent` + `versionFrom`/`versionTo`, and **`downloadUrl` is present only for TCI**
  — a structural check, no text parsing. (Contributed upstream; see the plugin README's MCP section.)
- In the system: **SNOTE** shows the implementation type and will tell you if TCI support is missing
  (errors **TN835 / TN872** — SAP Note 2499947). [P6]

> ⚠️ **TCI is a transport import, not just a note.** Treat it with transport-level care
> ([sap-transport-mgmt](../sap-transport-mgmt/SKILL.md)): DEV → QAS → PRD, backup first, and confirm the
> SPAM/SAINT prerequisite *before* the change window — discovering it mid-window is the classic failure.

## 6. Implement & verify (change-controlled)

- **SNOTE** (Note Assistant): download + implement in **DEV**, run the automatic activities, resolve
  prerequisites, test → **transport to QAS → PRD**. [P5]
- **TCI notes:** ensure SPAM/SAINT meets the minimum and TCI is enabled, then implement via SNOTE, which
  imports the transport. Follow **SAP Note 2543372** for the procedure. [P6]
- **Kernel / SP notes:** apply the patched kernel or Support Package via **SUM / SPAM/SAINT** in a
  maintenance window (OS-specific kernel per platform — Linux/Windows/AIX download from the SAP Software
  Center). Cross-ref a future `sap-kernel-patch` skill.
- **Manual/config notes:** apply the documented parameter/config change; some need a restart
  ([sap-system-lifecycle](../sap-system-lifecycle/SKILL.md)).
- **Verify:** re-run **System Recommendations / RSECNOTE** → the note now shows implemented; confirm no new
  ST22 dumps ([sap-health-triage](../sap-health-triage/SKILL.md)).

---

## OS note

The analysis (portal, SysRec, SNOTE) is **OS-independent**. Only **kernel** security patches are
OS-specific — download the correct kernel for the system's platform (Linux/Windows/AIX) from the SAP
Software Center.

## Cross-references

- **Restart after config/kernel notes:** [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
- **Post-patch health / new dumps:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **SAP Notes MCP** (retrieval): see the plugin's SAP Notes MCP notes (content path fix pending).
- **`sap-support-case`** — when a Note search does not resolve it and a case is genuinely justified; routing, priority and the wizard traps.

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

- **[P1]** *SAP Security Patch Day* — SAP Support Portal (2nd Tuesday monthly; the **SAP Security Notes**
  app). https://support.sap.com/en/my-support/knowledge-base/security-notes-news.html
- **[P2]** SAP Note priority / **CVSS v3** model (HotNews 9.0–10.0, High 7.0–8.9, Medium 4.0–6.9, Low <4.0)
  — SAP security notes classification.
- **[P3]** *System Recommendations* — SAP Solution Manager; weekly comparison of released notes vs a
  managed system's note status, incl. Patch Day security notes. help.sap.com (Solution Manager).
- **[P4]** *Configuration & Security Analytics (CSA)* — SAP Focused Run, landscape-scale security-note
  validation. help.sap.com (Focused Run).
- **[P5]** **SNOTE** (Note Assistant) + **`RSECNOTE`** — implement/track security notes on the system.
  help.sap.com (Note Assistant).
- **[P6]** **Transport-Based Correction Instructions (TCI)** — **SAP Note 2187425** (*Information about
  SAP Note Transport based Correction Instructions*; the Note's entire Solution section reads *"See the
  attached PDF for further information"* — the substance is the attachment **`TCI_for_Customer.pdf`**
  (878,422 B, 24 pages). Fetch it with the MCP's `fetch_attachment`; the Note text alone tells you almost
  nothing **[V]**),
  **2543372** (*How to implement TCI*; also carries attachments), **2499947**
  (*TN835 or TN872: the transport based correction of SAP Note is not available*), **2576306** (TCI for
  download of digitally signed SAP Notes). Component BC-UPG-NA.
  https://me.sap.com/notes/2187425 · https://me.sap.com/notes/2543372
- **[P7]** CI/TCI structure verified directly against the SAP for Me backend during authoring: one
  correction instruction per software component **and release range**; the correction row's
  `DownloadURL` is populated **only** for TCI. Sampled 3096734 / 2168979 / 2961006 (classic CI, no
  download URL) vs 3195213 / 3275780 / 3401735 (TCI, download URL present). **[V]**

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the current SAP Security Notes FAQ
note and the System Recommendations setup guide for your Solution Manager / Focused Run release.
