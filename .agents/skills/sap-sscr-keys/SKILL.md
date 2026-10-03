---
name: sap-sscr-keys
description: >-
  SAP Software Change Registration (SSCR) — developer keys and object keys. Decide whether the
  system even needs them (S/4HANA, BW/4HANA and AS ABAP 7.51+ do not; NetWeaver 7.50 and below
  do), gather the parameters a key binds to, request them in SAP for Me, handle the 14-day
  post-upgrade SPAU grace window, and reassign/restore keys with RS_SSCR_KEY_UPLOAD. Covers
  DEVACCESS and ADIRACCESS and why you must never edit them by hand. Use for "developer key",
  "object key", "access key", "SSCR", "key required to modify SAP object", "register developer",
  "SPAU asking for object keys".
---

# SSCR — Developer Keys & Object Keys

**SSCR (SAP Software Change Registration)** registers manual changes to SAP-delivered sources and Dictionary
objects. When a developer changes SAP standard, the system demands two different keys: **[G, FAQ]**

- a **developer key** — registers *a person* as a developer. Entered **once** per user.
- an **object key** — authorises changing *one specific SAP object*. One key **per object**.

> **Guardrail — the first question is whether you need a key at all.**
> - **Most modern systems don't.** S/4HANA, BW/4HANA and AS ABAP **7.51+** do not implement SSCR (§1).
>   Requesting keys for those is wasted work; being *asked* for one is a **bug** with a known Note.
> - **Never delete rows from `DEVACCESS` or `ADIRACCESS` by hand.** SAP states plainly it is not
>   responsible for these tables and ships no deletion programs. Use the SAP for Me application. **[G, FAQ]**
> - **A key is bound to the installation number.** Change the installation number (some license changes,
>   system copies, reassignments) and every existing key stops working (§6).
> - **Keys are not a security control.** They are a licensing artefact. Control development with the
>   system change option (SE06), client settings (SCC4) and `S_DEVELOP`/`S_TRANSPRT` authorizations (§1).
> - **No mass registration exists.** Keys are generated one at a time from accurate parameters. **[G, FAQ]**

Verification legend: **[V]** verified against the live service / system during authoring · **[G]** cited to
an SAP Note or guide.

---

## 1. Does this system need SSCR keys at all?

Check this **before** anything else — it decides whether the rest of the skill applies.

| Target system | SSCR keys? | Source |
|---|---|---|
| **SAP S/4HANA** (on-prem, 1511 and later, all variants) | **No** — not implemented | [G, S4] |
| **SAP BW/4HANA** (all variants) | **No** — not implemented | [G, S4] |
| **AS ABAP 7.51 and higher** as target version | **No** — no longer required | [G, SPAU] |
| **NetWeaver AS ABAP ≤ 7.50**, ECC, older releases | **Yes** | [G, FAQ] |

Determine the release programmatically rather than asking — `System → Status`, or `disp+work -version`,
or table `CVERS` for `SAP_BASIS`. See [sap-health-triage](../sap-health-triage/SKILL.md).

> ⚠️ **The exception that wastes an afternoon.** An S/4HANA system **can** still demand SSCR keys — that is
> a defect, not policy. It affects `SAP_BASIS` **750 up to SP24**, **751 up to SP14**, **752 up to SP10**,
> and is fixed by **SAP Note 3191095**. That Note needs a **manual pre-implementation step in every system
> before the correction is imported** (repair of include `LSKEYF00` per **SAP Note 37900**). If an S/4HANA
> system asks for a key, patch it — don't request keys. **[G, BUG]**

**If SSCR does not apply, control development this way instead** — this is SAP's own answer to "then what
stops people changing SAP code?": **[G, S4]**

| Control | Where |
|---|---|
| System change option (global + per software component) | **SE06** → *System Change Option* |
| Client-specific changeability | **SCC4** |
| Developer authorizations — scope by `DEVCLASS`, `OBJTYPE`, `OBJNAME`, `P_GROUP`, `ACTVT` | `S_DEVELOP`, `S_TRANSPRT` |
| **What SAP code was actually modified** | **SE95** (Modification Browser) |

Blocked developers get message **TR852** depending on those settings. SSCR keys never were the control —
they are a licensing feature. **[G, S4]**

---

## 2. What each key is bound to

Getting this wrong is the usual reason a key "doesn't work".

| | **Developer key** | **Object key** |
|---|---|---|
| Depends on | **installation number** + **user name** | **installation number** + **object name** |
| Release-specific? | No | **Yes**, as of Release 4.0 |
| How often | once per developer | once per object, per release |
| Stored in table | **`DEVACCESS`** | **`ADIRACCESS`** |
| Client-specific? | **No** — client-independent, survives client copy | **No** |

Consequences worth internalising: **[G, FAQ]**

- **Rename a developer → the old key is dead.** Request a new one under the new name. Deleting the old row
  from `DEVACCESS` does *not* undo modifications that user already made.
- **License change is usually fine** — as long as the **installation number is retained**. Historically,
  swapping a demo licence for a full one changed the installation number and invalidated every key.
- **Matchcodes and tuning measures** (database indexes, buffer settings) are **excluded** from registration.
- Cost: developer keys are **normally free of charge and unlimited in number**, but SAP reserves the right
  to query inconsistencies — e.g. one licensed developer against 100+ generated keys. **[G, COST]**

---

## 3. Gather the parameters before you open the portal

An object key needs the object's full identity. Read it from the system rather than transcribing from a
screenshot — the request will silently produce an unusable key if any part is wrong.

| Parameter | Example | Where to get it |
|---|---|---|
| **Installation number** | 10-digit | `System → Status`, or SAP for Me `InstallationSet` (§4) |
| **PGMID** | `R3TR`, `LIMU` | The key prompt, or `TADIR` |
| **Object type** | `CLAS`, `PROG`, `TABL`, `FUGR`, `DOMA` | `TADIR-OBJECT` |
| **Object name** | `CL_CI_S4H_COMMON` | `TADIR-OBJ_NAME` |
| **SAP release** | `752` | `System → Status` (`SAP_BASIS` release) |
| **Advanced correction?** | flag | Informational only — no effect on the registration itself **[G, FAQ]** |

*Advanced correction* means SAP supplied a fix ahead of a regular patch/release. Ticking the box is for
your own records; it does not change anything about the key. **[G, FAQ]**

For a developer key you only need the **installation number** and the **user name** (the ABAP user, e.g.
`ADAM`).

---

## 4. Request and review keys in SAP for Me

**UI:** `https://me.sap.com/sscr` (route `/app/sscr`; the app component is `sap.me.apps.systemeudpsscr`).
Your S-user needs the **Register Object and Developer Keys** authorization — or at minimum *Register Object
Keys*. Without it the application loads but registration is refused. **[G, REQ]**

**Service:** the application is a UI5 component (no iframe), backed by an OData service reachable with your
logged-in session: **[V]**

```
https://me.sap.com/backend/raw/core/W7LegacyProxyVerticle/odata/sfm/sscrsrv/
```

Entity sets: `DeveloperSet`, `ObjectSet`, `InstallationSet`, `ReleaseSet`, `PgmIdSet`, `ObjectTypeSet`,
`ValueHelpSet`, `ColumnSettingSet`, `KeysCountSet`. **[V]**

Reading your existing registrations is a plain GET — useful for auditing who has been registered and which
objects are modified across the estate: **[V]**

```
GET /backend/raw/core/W7LegacyProxyVerticle/odata/sfm/sscrsrv/DeveloperSet?$format=json
GET /backend/raw/core/W7LegacyProxyVerticle/odata/sfm/sscrsrv/ObjectSet?$format=json
GET /backend/raw/core/W7LegacyProxyVerticle/odata/sfm/sscrsrv/InstallationSet?$format=json
```

Field shapes — note how exactly they mirror §2: **[V]**

| `DeveloperSet` | `ObjectSet` | `InstallationSet` |
|---|---|---|
| `key` (the 20-char SSCR key) | `key` | `insnr` |
| `name` (ABAP user) | `pgmid`, `object`, `obj_name` | `insname` |
| `inst_nbr`, `insname` | `saprel` (**release-specific**) | `kunnr`, `kuname` |
| `kunnr` | `inst_nbr`, `insname`, `kunnr` | `type` |
| `date`, `type`, `auth` | `adv_corr`, `default`, `date`, `auth` | |
| `reg_by_userid`, `reg_by_name` | `reg_by_userid`, `reg_by_name` | |

`reg_by_userid` / `reg_by_name` record **which S-user registered the key** — the audit trail for "who
authorised this modification".

> 🔐 **Treat `key` values as licence material.** Don't paste them into tickets, chat logs or commit
> messages. When scripting against this service, mask the `key` field in any output you keep.

> **No batch registration.** SAP states mass/batch SSCR registration is not supported — one key at a time
> from accurate parameters. Automate the *gathering* and the *auditing*, not the issuing. **[G, FAQ]**

---

## 5. Upgrades — the 14-day SPAU grace window

The single most useful operational fact in this whole area: **[G, SPAU]**

- After an upgrade/update **performed with SUM**, there is a **14-day period** in which **SPAU adjustments
  need no object keys at all**.
- The window **cannot be extended**. Miss it and you need an object key for **every** object you adjust.
- It applies **only** to SUM upgrades/updates. **A SPAM import always requires an object key.**
- It does **not** restrict resetting SAP Notes, or adjusting Notes where **SNOTE** is called from SPAU —
  those work without a key regardless.
- Moot for **S/4HANA or AS ABAP 7.51+ targets** — no SSCR key is required at all (§1).

**Plan the adjustment inside the window.** Treat "SPAU complete" as part of the upgrade, not as follow-up
work — see [sap-kernel-patch](../sap-kernel-patch/SKILL.md) and
[sap-transport-mgmt](../sap-transport-mgmt/SKILL.md) for the surrounding change flow.

---

## 6. Reassignment, restore, delete — and the upload report

**Reassigning keys to a different installation number** (system copy, licence restructure) does not move
rows — SAP for Me **creates new keys referencing the new installation number**. The system will not see
them until you bring them across: **[G, FAQ]**

1. **Download** the SSCR keys from the SAP for Me SSCR application.
2. **Upload** into the system with report **`RS_SSCR_KEY_UPLOAD`** (SE38/SA38). **[G, UPLOAD]**

That two-step is the answer to *"I reassigned the keys but the system still asks for one."*

| Task | Route |
|---|---|
| Reassign keys to another installation number | SAP for Me self-service — **SAP Note 2632375** |
| Download reassigned keys + upload to the system | **`RS_SSCR_KEY_UPLOAD`** — **SAP Note 1856748** |
| Delete object/developer keys | SAP for Me — **SAP Note 1710320** (**not** by editing tables) |
| Restore deleted keys | SAP for Me — **SAP Note 1869240** |
| Prevent SAP from registering keys on your behalf | **SAP Note 1990193** |

---

## 7. Troubleshooting "the key doesn't work"

Work down this list — it's ordered by how often each is the actual cause:

1. **Should there be a key at all?** S/4HANA / BW/4HANA / 7.51+ → §1, and check the `LSKEYF00` defect.
2. **Installation number mismatch** — the commonest cause. Key was issued for a different installation
   number than the system reports (`System → Status`). Reassign + upload (§6).
3. **Release mismatch on an object key** — object keys are release-specific; after an upgrade a key issued
   for the old release does not apply. **SAP Note 2640978** covers exactly this. **[G, UPG]**
4. **Object identity wrong** — PGMID / object type / object name must match `TADIR` exactly (§3).
5. **Developer renamed** — old developer key is invalid; request under the new user name (§2).
6. **Reassigned but not uploaded** — run `RS_SSCR_KEY_UPLOAD` (§6).
7. **Still stuck** — **SAP Note 40850** (*SSCR key does not work*) and **SAP Note 2509738**
   (troubleshooting). Missing installation in the app: **SAP Note 2489468**.

---

## OS note

SSCR is **entirely OS-independent** — it lives in the ABAP layer (tables `DEVACCESS` / `ADIRACCESS`,
transactions SE06/SCC4/SE95/SE38) and in the SAP for Me portal. There are no Linux/Windows/AIX variants of
any step here. The only platform-adjacent action is reading the release with `disp+work -version` at the OS
shell, which [sap-health-triage](../sap-health-triage/SKILL.md) covers per platform.

---

## Cross-references

- **`sap-transport-mgmt`** — where object keys surface in practice: SPAU/SPDD after an upgrade.
- **`sap-software-download`** — the sibling SAP for Me OData service and the same authentication chain.
- **`sap-compliance-docs`** — the entitlement context for SAP for Me self-service.
- **`sap-security-patch`** — SNOTE work that can prompt a developer-key request.

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

- **[FAQ]** **SAP Note 2501703** — *Frequently asked questions about SAP Software Change Registration
  (SSCR)* (XX-SER-FORME, v10, 2025-01-08). **[V]** Retrieved via the SAP Notes MCP during authoring.
  Source for: the two key types and what each binds to (installation number + user name / installation
  number + object name); object-key assignment being **release-specific as of Release 4.0**; storage in
  **`DEVACCESS`** and **`ADIRACCESS`** with the explicit caution *"Never manually delete the keys from these
  tables"*; client-independence; matchcodes and tuning measures being excluded; developer-rename behaviour;
  licence-change/installation-number behaviour; the *advanced correction* flag being informational only;
  the required **Register Object and Developer Keys** S-user authorization; the download-then-upload step
  after reassignment; and *"mass SSCR keys registration is not supported"*.
  https://me.sap.com/notes/2501703
- **[S4]** **SAP Note 2309060** — *The SSCR license key procedure is not supported in SAP S/4 HANA*
  (BC-DWB-TOO, Consulting, v13, 2022-02-11; validity S4CORE 100+, SAP_BASIS 750–752+). **[V]** *"The SSCR
  license key procedure is not implemented in S/4HANA or BW/4HANA"*, applying to **S/4HANA 1511 onwards**
  and all BW/4HANA variants. Also the replacement controls — **SE06** system change option, **SCC4**,
  `S_DEVELOP`/`S_TRANSPRT` scoped by DEVCLASS/OBJTYPE/OBJNAME/P_GROUP/ACTVT, message **TR852**, and **SE95**
  to see what SAP code was changed. https://me.sap.com/notes/2309060
- **[BUG]** **SAP Note 3191095** — *Although S4HANA system, SSCR registration keys are required*
  (BC-DWB-TOO, Program error, v2, 2023-11-16; validity SAP_BASIS 750–752). **[V]** Fixed until
  `SAPK-75024INSAPBASIS` / `SAPK-75114INSAPBASIS` / `SAPK-75210INSAPBASIS`. Requires a **manual
  pre-implementation step in each system before importing the Note**, repairing include `LSKEYF00` per
  **SAP Note 37900**. https://me.sap.com/notes/3191095
- **[SPAU]** **SAP Note 1705730** — *SPAU adjustment after the 14-day period post upgrade* (BC-UPG-TLS-TLA,
  v9, 2026-02-12). **[V]** The 14-day key-free SPAU window after a **SUM** upgrade/update; *"The 14-day
  period cannot be extended"*; **a SPAM import always requires an object key**; resetting/adjusting SAP
  Notes via SNOTE needs no key; and *"For SAP S/4HANA systems or systems based on SAP NetWeaver AS for ABAP
  7.51 and higher as the target version, no SSCR key is required anymore"*.
  https://me.sap.com/notes/1705730
- **[COST]** **SAP Note 2098954** — *Limitation and costs for SAP Object and Developer Keys* (XX-SER-FORME,
  v8, 2023-07-06). **[V]** *"There is no limit on registering SSCR developer keys. In general they are
  normally free of charge"*, with SAP reserving the right to query inconsistencies.
  https://me.sap.com/notes/2098954
- **[REQ]** **SAP Note 2453897** — *How to request Object and/or Developer Keys (SSCR) for On-premise — SAP
  for Me* (XX-SER-FORME, 2025-03-13). The request procedure and the S-user authorization requirement.
  https://me.sap.com/notes/2453897
- **[UPLOAD]** **SAP Note 1856748** — *How to download reassigned SSCR keys and upload them into the system*
  (BC-DWB-TOO, 2025-10-31) — the `RS_SSCR_KEY_UPLOAD` procedure. Related: **SAP Note 1821969** (*Upload
  function for developer and object keys*). https://me.sap.com/notes/1856748
- **[UPG]** **SAP Note 2640978** — *SAP Object key does not work after Release upgrade — SSCR Keys*
  (XX-SER-FORME, 2024-06-21). https://me.sap.com/notes/2640978
- **[TS]** Troubleshooting set: **SAP Note 2509738** (*SAP Object and Developer (SSCR) key issue
  troubleshooting*), **SAP Note 40850** (*SSCR key does not work*), **SAP Note 2489468** (*Installation
  number is missing from the SSCR application*), **SAP Note 2632375** (*How to reassign SSCR Object and
  Developer Keys to a different installation number using self-service*), **SAP Note 1710320** (*How to
  delete SSCR Object and/or Developer Keys*), **SAP Note 1869240** (*How to restore deleted SSCR Object
  and/or Developer keys*), **SAP Note 1990193** (*How to restrict SAP from registering SSCR keys*).
- **[SVC]** SAP for Me **SSCR application** — route `/app/sscr` at `https://me.sap.com/sscr`, UI5 component
  `sap.me.apps.systemeudpsscr`, backed by
  `https://me.sap.com/backend/raw/core/W7LegacyProxyVerticle/odata/sfm/sscrsrv/`. **Entity sets and field
  lists verified live against the service during authoring**, and read back against a real S-user's
  registrations (installations, one developer key, twelve object keys incl. `R3TR CLAS CL_CI_S4H_COMMON`
  at `saprel` 752 — confirming that object keys carry a release). **[V]**

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID):
**2501703** for the FAQ, **2309060** and **1705730** for the current applicability boundary (this is the part
most likely to move as SAP retires SSCR further), and **3191095** if an S/4HANA system unexpectedly demands
a key.
