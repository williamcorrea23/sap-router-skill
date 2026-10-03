---
name: sap-maxdb-ha
description: >-
  SAP MaxDB, liveCache and Content Server HA/DR — the four mechanisms and when each is right:
  cluster failover (MSCS, UNIX agents, LifeKeeper), shadow/standby via log recovery, Hot Standby
  with a storage-vendor HSS library, and snapshot/split-mirror. Covers why SAP recommends a
  shadow database over Hot Standby for DR, the read-only Hot Standby constraint, hss_enable, the
  single-database limit in MSCS, and log-area mirroring rules. Use for "MaxDB high
  availability", "liveCache hot standby", "standby database MaxDB", "shadow database", "libHSS",
  "hss_enable", "MaxDB cluster", "APO liveCache HA".
---

# SAP MaxDB / liveCache — high availability

**Source of record.** **SAP Note 952783 — *FAQ: SAP MaxDB high availability***, version **21**,
released **01.11.2024**, component BC-DB-SDB **[V]** — fetched and read directly. Marks: **[V]**
verified, **[G]** cited but not read in full.

> **Scope note from the Note itself:** it *"describes options at database level. High availability
> concepts of the hardware and the operating systems are not a subject"* — and it says plainly
> *"The note is by no means complete."* **[V]** Treat the storage and OS layers as a separate
> conversation with the hardware partner.

**Where this still matters.** MaxDB is legacy for most NetWeaver stacks, but **liveCache** remains
the engine behind SAP SCM/APO planning, and MaxDB backs **Content Server**. Hot Standby exists
largely because liveCache in a mission-critical SCM scenario cannot tolerate a long restore.

---

## 1. Four mechanisms — pick by failure mode, not by sophistication

MaxDB does not have one HA feature. It has four, with genuinely different properties. **[V]**

| Mechanism | Automatic failover | Switch time | Protects against | Needs |
|---|---|---|---|---|
| **Backup / recovery** | ✗ | Restore duration | Physical **and logical** errors | Nothing extra |
| **Snapshot / split mirror** | ✗ | Very fast data recovery | Logical errors, fast rollback | **Disk storage system** |
| **Cluster for failover** | ✓ | Host-failover time | **Host** failure only | Cluster software, shared disk |
| **Shadow (standby) database** | **✗ — not without extra software** | Log-recovery delay | Disk **and** host failure, **logical errors (PITR)** | Second host + disk |
| **Hot Standby** | ✓ | **A few seconds** | Disk **and** host failure | **Storage system + vendor HSS library** |

**The two that get confused are Shadow and Hot Standby.** Both keep a second database. They differ
in *how* the standby learns about changes:

- **Shadow database** — redoes **transported log files** by log recovery. *"If a master fails, but
  the current log area is still available, the shadow database can take over the master operation
  **without data loss**."* It can also deliberately **lag**, replaying to an earlier point — which is
  what makes it a defence against logical corruption. **[V]**
- **Hot Standby** — reads log entries **immediately from the log area of the master** and redoes
  them. After takeover the former standby continues with the master's log. **[V]**

---

## 2. The design verdict people get backwards

> ## 🛑 For disaster recovery, SAP recommends the **shadow database**, not Hot Standby
>
> Note 952783, verbatim: *"For the protection against disaster recovery (for example, if the computer
> center breaks down), **a shadow database is generally more useful than Hot Standby**. If a Hot
> Standby database reads from a mirrored log area, **this mirror must be mirrored synchronously. As a
> result, performance may decrease in the master.** Downtimes of a few seconds do not have to be
> ensured for disaster recovery."* **[V]**

The reasoning is worth internalising, because it generalises: Hot Standby's few-seconds switch is
bought with **synchronous log mirroring**, and stretching that across a DR distance taxes the master
continuously — to buy an RTO that DR does not actually require. Hot Standby is a **local HA** tool.
Shadow database is the **DR** tool.

A landscape may legitimately run **both**: Hot Standby locally, shadow database remotely.

---

## 3. Hot Standby

**What it is** **[V]**: the standby runs on a second host with its **own separate data area**, reads
the master's log area directly and redoes it. A **cluster agent** monitors the master and switches
automatically. The standby's data area is **initialised automatically by flash copy or symclone**.

**Enabling it** makes the database the master of the hot standby system **[G]**:

```
hss_enable node=<VIRTUAL_SERVER> lib=<hss_library>
```

> ## ⚠️ You cannot implement this alone
>
> Two hard prerequisites **[V]**:
> 1. **A disk storage system**, and
> 2. **a library implementation from the disk storage system provider** (the HSS library).
>
> Note 952783 lists under disadvantages: *"**Implementation must be carried out by hardware partners
> for HSS library**."* This is not a configuration task you complete from the SAP side. Current
> vendor solutions are tracked in **SAP Note 3534972**. Check that Note **before** promising a
> customer Hot Standby — approved storage is the gating constraint, and a storage system must be
> **approved for SAP MaxDB**.

**The standby is read-only** **[V]** — listed as an *advantage* (structure checks can run there
without touching the master), but it means Hot Standby is not a route to offloading write work.

**No performance penalty on the master** in the local case **[V]** — the caveat in §2 applies only
when the log area is synchronously mirrored over distance.

Two variants exist in the documentation: **with shared log area** and **no shared resources** **[G]**
(SAP Note **2097837** covers installation/upgrade of the shared-log-area variant).

---

## 4. Shadow / standby database

**Advantages** **[V]**: protects against disk *and* host failure; structure checks can run on the
standby; **protects against logical errors via point-in-time recovery**; the log-recovery delay you
choose sets the maximum downtime; **implementable without further partners**; no performance
disadvantage for the master.

**Disadvantages** **[V]**: **no automatic transfer without additional software**; needs an extra host
and disk.

> **From MaxDB 7.9.10.06, SAP offers an automated log recovery process** — SAP Note **3066314**.
> **[V]** A genuine version gate: below that level the log-shipping loop is yours to script.

Third-party options exist (Note 952783 names **Libelle DBShadow**), and SAP explicitly allows a
**script-based** shadow database. **[V]** The "HowTo — Standby System (Recovery from Log Backup)"
documentation is the starting point.

**The deliberate-lag trick.** *"The shadow database can also redo the log at a different time and can
be switched to the operational status ONLINE starting at an earlier point in time."* **[V]** A
standby held a few hours behind is a rewind window against logical corruption — the same idea as
Db2's time-delayed replay.

---

## 5. Cluster for failover

| Platform | Solution |
|---|---|
| **Windows** | **Microsoft Cluster (MSCS)** — modules are **already in the standard delivery** **[V]**; see SAP Note **1855747** |
| **UNIX** | Cluster agents from the **OS partner** — contact your hardware partner **[V]** |
| **Linux** | **LifeKeeper** (SteelEye), among others **[V]** |

> ## ⚠️ Two constraints that shape the design
>
> **Only one database per Microsoft cluster.** *"SAP MaxDB supports only the operation of a **single**
> SAP MaxDB/liveCache database in a Microsoft cluster."* **[V]** Consolidating several MaxDB/liveCache
> databases onto one MSCS cluster is not supported.
>
> **Shared disk means the data is not protected.** Note 952783 lists as a disadvantage: *"Shared disk
> approach; **data volumes are not protected**. Recovery for defect data hard disks required."* **[V]**
> A failover cluster survives a **host** failure, not a **disk** failure — it is not a substitute for
> the standby mechanisms above.

File and directory layout for UNIX failover clusters from MaxDB 7.9: SAP Note **1463606** **[G]**.

---

## 6. Baseline storage rules — before any HA mechanism

These are SAP's general database-availability recommendations, and they apply underneath everything
above. **[V]**

- **Under UNIX, use raw devices** — *"This is safer than using files in the file system."*
- **RAID for the data volumes**; mirroring gives the highest safety.
- **Log area:** use striping RAID levels **only if the storage system is big enough**.
- **Mirroring the log area is obligatory for server systems.**
- **Mirror at the OS or hardware level.** MaxDB *supports* log-area mirroring in the database, *"However,
  it usually leads to a deterioration in performance."* (SAP Note **869267**)
- **Run database structure checks regularly** (`CHECK DATA` / `VERIFY`) — SAP Note **940420**.

**Speeding up recovery** **[V]**: incremental backups help considerably; a **large log area** means
the restore may not need archived log files at all — if the log-recovery start point is still in the
current log, you can restart immediately after the data restore. Backup media access is usually the
bottleneck, so use parallel media and a fast connection to backup servers.

---

## 7. Where the rest lives

| Topic | File |
|---|---|
| Choosing between the four, snapshot/split-mirror detail, maintenance in an HA environment, cloud | [references/maxdb-ha-options.md](references/maxdb-ha-options.md) |

## Cross-references
- **`sap-backup-recovery`** — MaxDB backup/recovery, the baseline every mechanism here sits on.
- **`sap-db-command-reference`** — MaxDB start/stop, `dbmcli`, the `sdb` / `<sid>adm` users.
- **`sap-space-reclaim`** — MaxDB diagnostic files and log-area sizing.

**The other five database HA/DR skills — different technologies, no commands transfer:**

- **`sap-hana-system-replication`** — HANA System Replication (`hdbnsutil`, HSR).
- **`sap-ase-hadr`** — ASE HADR / Always-On (Replication Server, RMA `sap_*`).
- **`sap-oracle-dataguard`** — Oracle Data Guard (physical standby, DGMGRL).
- **`sap-db2-hadr`** — Db2 HADR (`HADR_SYNCMODE`, SA MP / Pacemaker).
- **`sap-sqlserver-alwayson`** — SQL Server Always On (availability groups, listener).

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
| **[MX1]** | **SAP Note 952783** — *FAQ: SAP MaxDB high availability*, v**21**, 01.11.2024, BC-DB-SDB | **[V]** — the four mechanisms, their advantage/disadvantage lists, the DR verdict, cluster and storage rules all read directly |
| **[MX2]** | **SAP Note 3534972** — *SAP MaxDB/liveCache Hot Standby solutions* | **[G]** — **the current list of vendor HSS solutions; check before promising Hot Standby** |
| **[MX3]** | **SAP Note 3066314** — *SAP MaxDB: Introduction of automatic log recovery function* (from 7.9.10.06) | **[G]** |
| **[MX4]** | **SAP Note 2097837** — *Installation/upgrade of hot standby system (with shared log area)* | **[G]** |
| **[MX5]** | **SAP Note 1855747** — MaxDB/liveCache in Microsoft Cluster | **[G]** |
| **[MX6]** | **SAP Note 1463606** — *SAP MaxDB as of 7.9: Directories and Files in Unix Cluster for Failover* | **[G]** |
| **[MX7]** | **SAP Note 869267** — *FAQ: SAP MaxDB Log area* | **[G]** |
| **[MX8]** | **SAP Note 940420** — *FAQ: Database structure check (CHECK DATA/VERIFY)* | **[G]** |
| **[MX9]** | **SAP Note 371247** — *SAP MaxDB and split-mirror techniques*; **1928060** — *Data backup and recovery with file system backup* | **[G]** |
| **[MX10]** | **SAP Note 912905** — *FAQ: Storage systems used with SAP MaxDB* | **[G]** — approved storage |
| **[MX11]** | **SAP Note 3318338** — *SAP MaxDB/liveCache high availability in cloud environment* | **[G]** |
| **[MX12]** | **SAP Note 2113981** — *SAP MaxDB / liveCache / Content Server Maintenance in High Availability System Environment* | **[G]** |
| **[MX13]** | **SAP Note 820824** — *FAQ: SAP MaxDB/liveCache technology*; **846890** — *FAQ: SAP MaxDB database management*; **767598** — where to find MaxDB documentation | **[G]** |

> **Note 952783 says of itself: *"The note is by no means complete."*** **[V]** It is a decision guide,
> not an implementation manual. For Hot Standby in particular the real implementation detail sits
> with the storage vendor and **Note 3534972**.

> **Currency.** v21 dates from 01.11.2024, and several referenced Notes are newer — **3534972** and
> **3318338** especially. Vendor HSS support and cloud HA options move faster than this FAQ; re-read
> those two before designing.
