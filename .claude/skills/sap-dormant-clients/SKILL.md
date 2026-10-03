---
name: sap-dormant-clients
description: >-
  Assess whether a client is genuinely dormant and retire it safely — 000/001/066 and abandoned
  project/sandbox clients. Builds evidence from last logon (RSUSR200/SUIM), ST03N workload
  statistics, jobs (TBTCO/TBTCP), change documents and client-specific table volumes, then
  deletes with SCC5 (test run first) and handles what it leaves behind — TemSe, spool, T000,
  SAP*. Use for "can we delete client 001", "is client 066 still needed", "dormant client",
  "unused client", "SCC5", "client cleanup".
---

# Dormant Client Assessment & Retirement

Every client you keep must be secured, patched, user-maintained and audited — including the ones nobody
uses. Removing an unused client **reduces maintenance effort and increases security**, because unused
clients are where forgotten standard users (`SAP*`, `DDIC`, `EARLYWATCH`) keep their well-known
passwords. [G, RM]

> **Guardrail — client deletion is irreversible in practice.**
> - **Never delete on a hunch.** Dormancy is a *conclusion from evidence* (§2). "Nobody mentions it" is not
>   evidence. Present the evidence table and get explicit sign-off before §4.
> - **Client 001 is productive in some products.** SAP Solution Manager and BW commonly run production in
>   **001**. Confirm what the system *is* before assuming 001 is a leftover. [G, RM]
> - **Always run SCC5 in test mode first**, and always in **background** for a large client. [G, RM]
> - **PRD systems: typed confirmation naming the SID and client number**, and a current backup you have
>   verified is restorable — see [sap-backup-recovery](../sap-backup-recovery/SKILL.md). Recovery of a
>   wrongly deleted client is a restore, not an undo (SAP Note 31496). [G, REC]
> - **Deleting rows does not free disk.** Space returns only after a reorganization — §6.
> - Never re-create client **066** after removing it. [G, RM]

Verification legend: **[V]** verified during authoring · **[G]** cited to an SAP Note or guide.

---

## 1. The three install-time clients

| Client | What it is | Delete? |
|---|---|---|
| **000** | SAP reference/template client. Holds cross-client customizing reference data. | **No — never.** |
| **001** | A **copy of 000** made at installation, intended as a possible production client. | **Yes, if unused** — but **Solution Manager and BW usually use 001 productively**. [G, RM] |
| **066** | Created for **SAP Active Global Support EarlyWatch** delivery. **Obsolete.** Last shipped with **NetWeaver 7.40**; not delivered by newer installs/upgrades. | **Yes** — safe to remove, and **must not be re-created**. [G, RM, EW] |

> ⚠️ **Upgrade tooling used to demand 066.** Some SUM versions check for client 066 and **stop the upgrade**
> if it is missing (KBA 1874687, phase `EWIMPORT_UPG`). Workaround: re-create only the **T000 entry** via
> SCC4, run the upgrade, remove the entry after. **SUM 1.0 SP13 and later no longer ask.** [G, RM]

Beyond these, the usual dormancy candidates are abandoned **project / sandbox / training / "copy of PRD
for testing"** clients — often the biggest by far, and the least owned.

---

## 2. Build the dormancy evidence (all read-only)

Run every check. A client is dormant only when **all** signals agree; one active signal is enough to stop.

### 2.1 Inventory the clients

```abap
" Table T000 — client list, role, change options
SE16 → T000     " MANDT, MTEXT, ORT01, CCCATEGORY, CCCORACTIV, CCNOCLIIND
```
`SCC4` shows the same maintained. Record each client's **role** (`CCCATEGORY`: P production, T test,
C customizing, D demo, E training/education). [G, RM]

### 2.2 User activity — has anyone logged on?

| Check | How |
|---|---|
| Last logon per user | **`RSUSR200`** via **SUIM** — *Users by Complex Selection Criteria*, incl. *Users by Logon Date* [G, RM] |
| Raw last-logon data | table **`USR02`** — fields `TRDAT` (last logon date), `LTIME`, `UFLAG` (lock status) |
| Users that exist at all | **`USR02`** row count per `MANDT` |

Dormancy signal: **no non-`SAP*`/`DDIC` logon within your review window** (12 months is a common bar; state
whichever you use).

### 2.3 Workload statistics — was the client *used*?

**`ST03N`** → expert mode → **Analysis View "Settlement Statistics"** shows **which clients were used and by
which users**. This is the single most direct answer to "is anyone working in there". [G, RM]

Retention limits how far back you can see — check the workload collector's retention (§ `SWNCMONI`, SAP Note
2274315) before concluding "no activity" when you may simply be past the horizon.
**Absence of data beyond the retention window is not evidence of absence of use.**

### 2.4 Background jobs — is anything scheduled?

Jobs are the classic thing that keeps a "dead" client alive:

```abap
SE16 → TBTCO    " job headers.  Selection field AUTHCKMAN = client
SE16 → TBTCP    " job steps.    AUTHCKNAM = the executing user
```
Table **`TBTCO`** carries the client; the **user** running each step is in **`TBTCP`**. Join both to get
client + user together. View **`V_OP`** does the same with `AUTHCKMAN`. [G, RM]

Also check **released/scheduled** status specifically, not just history.

### 2.5 Data footprint and last-changed evidence

Ask *when did data last change*, using client-dependent tables that every system has:

| Signal | Where |
|---|---|
| Change documents | **`CDHDR`** — `MANDANT`, `UDATE` (max date per client) |
| Application log | **`BALHDR`** — `MANDANT`, `ALDATE` |
| Spool requests | **`TSP01`** — `RQCLIENT`, `RQCRETIME` |
| Batch input | **`APQD`/`APQI`** — `MANDANT` |
| IDocs | **`EDIDC`** — `MANDT`, `CREDAT` |
| Update records | **`VBHDR`** — `MANDT` |
| Table logging | **`DBTABLOG`** — `LOGDATE`, client in the key |

Use **`TAANA`** (table analysis) to count rows grouped by `MANDT` and by year — that gives both the *last
activity date* and the *volume attributable to the client*, which feeds §6. [G, TT]

### 2.6 Security posture (why it matters even if dormant)

Run **`RSUSR003`** — it checks standard users and default passwords **per client**. A dormant client that
fails RSUSR003 is an active risk, which is the argument for removing it rather than leaving it. [G, RM]

---

## 3. Classify

Present a table per client and let the user decide. Recommended shape:

| Client | Role | Users w/ logon <12m | Jobs scheduled | Last data change | Est. size | Verdict |
|---|---|---|---|---|---|---|
| 066 | — | 0 | 0 | — | small | **Retire** (obsolete by design) |
| 001 | T | 0 | 0 | 2019-03 | 40 GB | **Candidate** — confirm not SolMan/BW prod |
| 250 | T | 3 | 2 | last week | 210 GB | **Active** — keep |

**Never** collapse this into "safe to delete" without showing the underlying evidence.

---

## 4. Pre-deletion checklist

Do all of these **before** SCC5. [G, RM]

1. **Client must not be classified productive** — `SCC4`, set the role away from *Production*.
   (SAP Note 2284180 covers changing the **066** role to TEST specifically.) [G, EW]
2. **Lock the users** in the client for an observation period — if nobody complains and nothing fails, the
   dormancy conclusion holds. Leave one administrative user unlocked. [G, RM]
3. **Confirm no scheduled jobs** remain (§2.4).
4. **Verify a restorable backup** exists — [sap-backup-recovery](../sap-backup-recovery/SKILL.md).
5. **Logon as `SAP*` may be required** — this needs profile parameter
   **`login/no_automatic_user_sapstar = 0`**. [G, RM]
6. If the client **was ever productive**, plan the **TemSe** cleanup — **SCC5 does not remove TemSe
   objects** (§5, SAP Note 934593). [G, RM]

---

## 5. Delete — and clean up what SCC5 leaves behind

**You must be logged on to the client you are deleting.** [G, RM]

| Step | Action |
|---|---|
| 1 | **`SCC5`** — select **"Delete entry from T000"**, run **test mode** first |
| 2 | **`SCC5`** in **background** for a large client (foreground is fine for 066) |
| 3 | **`SCC3`** — monitor the deletion log |
| 4 | **`SCC4`** — confirm no `T000` entry remains |
| 5 | **`RSUSR003`** — confirm `SAP*` access to that client is gone |
| 6 | Set **`login/no_automatic_user_sapstar = 1`** on **all** application servers |
| 7 | **TemSe** — delete the client's TemSe objects per **SAP Note 934593**; SCC5 does not do this |
| 8 | Reorganize the database (§6) |

For very large clients, SAP Note **365304** documents the deletion reports, and **70643** the client
deletion topic generally. **446485** covers copy options but carries deletion recommendations too. [G, RM]

---

## 6. Reclaiming the space — deletion alone does not shrink the database

This is where client retirement usually disappoints: SCC5 removes **rows**, and on most databases the
freed space stays inside the tablespace/datavolume as reusable-but-not-returned space.

- **Plan a reorganization** after deleting a large client. Search the reorganization Notes for your DB's
  component (`BC-DB-ORA`, `BC-DB-HDB`, `BC-DB-DB6`, `BC-DB-MSS`, `BC-DB-SDB`, `BC-DB-INF`). [G, RM]
- **Oracle** specifically: **SAP Note 646681** (*Reorganization of tables with BRSPACE*) and **SAP Note
  541538** (*FAQ: Reorganization*); *Segment Management with BR\*Tools* on help.sap.com. [G, RM]
- Sizing before/after and the per-DB reclamation mechanics live in
  **[sap-space-reclaim](../sap-space-reclaim/SKILL.md)** — use it to quantify the win *before* you commit
  to the outage, and [sap-db-command-reference](../sap-db-command-reference/SKILL.md) for the DB commands.

---

## OS note

Client assessment and deletion are **OS-independent** — everything is ABAP-side (SCC4/SCC5/SCC3, SUIM,
ST03N, SE16). The OS/DB layer becomes relevant only at §6 (reorganization) and for the profile-parameter
change in §5 step 6, which must be applied to **every** application server's profile — see
[sap-health-triage](../sap-health-triage/SKILL.md) for reading profiles per platform.

---

## Cross-references

- **`sap-client-copy-accelerator`** — the reverse operation: filling a client fast rather than removing one.
- **`sap-space-reclaim`** — what deleting a client actually frees, and why the segment does not shrink on its own.
- **`sap-transport-mgmt`** — client-dependent customizing and the logical-system rename that follows a deletion.
- **`sap-backup-recovery`** — take a restore point before deleting any client.

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

- **[RM]** **SAP Note 1749142** — *How to remove unused clients including client 001 and 066* (BC-CTS-CCO,
  v6, 2023-11-29). **[V]** Retrieved via the SAP Notes MCP during authoring. Source for: the security
  rationale (unused clients still need `SAP*`/`DDIC`/`EARLYWATCH` secured); client **001** being a copy of
  000 and safely removable **unless** it is the productive client — *"an SAP Solution Manager System or an
  SAP Business Warehouse system usually uses client 001 as a productive client"*; client **066** being the
  obsolete AGS service client, last delivered with **NetWeaver 7.40**, with the explicit caution *"You must
  NOT re-create this client"*; the pre-check method — **`RSUSR200`** via **SUIM**, and **`ST03N`** Analysis
  View **"Settlement Statistics"** to see *"which clients had been used and which users have been used
  these clients"*; locking users before deletion; job checks via **`TBTCO`** (`AUTHCKMAN`) joined to
  **`TBTCP`** (`AUTHCKNAM`), or view `V_OP`; ensuring the client is not classified productive in **SCC4**;
  **`login/no_automatic_user_sapstar`** = 0 before / = 1 after; deletion via **`SCC5`** with the T000-entry
  option, background mode for large clients and a test-run mode; monitoring with **`SCC3`**; verification
  with **`SCC4`** and **`RSUSR003`**; the **SUM `EWIMPORT_UPG`** client-066 check (KBA 1874687) resolved in
  SUM 1.0 SP13; and the post-deletion reorganization advice incl. Oracle Notes 646681 / 541538.
  https://me.sap.com/notes/1749142
- **[EW]** **SAP Note 1897372** — *EarlyWatch Mandant 066 — Can Client 066 be deleted?* (SV-SMG-SER, v10,
  2026-04-17). **[V]** Confirms 066 is obsolete and points to 1749142 for the procedure. Related: **SAP Note
  2284180** — *To change the 066 Client role to TEST* (BC-CTS-CCO). https://me.sap.com/notes/1897372
- **[TEMSE]** **SAP Note 934593** — *Deletion of all objects of a client from TemSe* (BC-CCM-PRN-TMS).
  **SCC5 does not remove TemSe objects**; a formerly productive client needs this separately.
  https://me.sap.com/notes/934593
- **[REC]** **SAP Note 31496** — *CC-INFO: Client deleted by mistake* — recovery options. Related client
  deletion Notes: **70643** (*CC-TOPIC: Client Deletion (SCC5)*), **365304** (*CC-ADMIN: Reports for
  deleting tables* — useful for large clients), **446485** (*CC-ADMIN: Special copying options*), **2518306**
  (*Deleting an unused client*). https://me.sap.com/notes/31496
- **[TT]** **SAP Note 2388483** — *How-To: Data Management for Technical Tables* (HAN-DB, v288, 2026-07-27).
  **[V]** Used here for the technical-table signals and for **`TAANA`** table analysis
  (`ARDB_STAT*`, `TAAN_*`, SAP Note 2034063, report `TAAN_DELETE_ANALYSES`), and for the workload-collector
  retention caveat (`SWNCMONI`, SAP Note **2274315**, retention adjusted in **ST03**).
  See [sap-space-reclaim](../sap-space-reclaim/SKILL.md). https://me.sap.com/notes/2388483
- **[HELP]** *Deleting Clients* — SAP Help Portal, client copy/deletion documentation (linked from Note
  1749142). [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID):
**1749142** for the procedure, **934593** before deleting a formerly productive client, and the
reorganization Note for your database component before promising any disk saving.
