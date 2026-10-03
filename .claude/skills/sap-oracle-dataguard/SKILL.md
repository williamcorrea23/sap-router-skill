---
name: sap-oracle-dataguard
description: >-
  Oracle Data Guard under SAP — what SAP actually permits, which is narrower than Oracle's own
  documentation: physical standby only (logical is forbidden), the Broker, the three protection
  modes and the Maximum Protection trap that terminates the primary, Fast-Start Failover
  (permitted but unsupported), Active Data Guard and Far Sync licensing, and the read-only rule
  that blocks starting an SAP instance on a standby. Covers the DGMGRL command surface, BR*Tools
  interaction and standby backups. Use for "Oracle Data Guard SAP", "physical standby",
  "DGMGRL", "switchover", "failover", "Maximum Availability", "ORA-16724", "is Data Guard
  supported by SAP".
---

# Oracle Data Guard under SAP

**Source of record.** **SAP Note 105047 — *Support for Oracle functions in the SAP environment***,
version **247**, released **02.07.2026**, component BC-DB-ORA **[V]** — fetched and read directly.
This Note, not Oracle's documentation, decides what you may run under SAP.

> ## ⚠️ Oracle's docs describe more than SAP permits
>
> Data Guard is an Oracle feature, but SAP **restricts** it. Two of the most commonly deployed Data
> Guard configurations in the wider Oracle world are **forbidden or unsupported** under SAP. Read §1
> before designing anything, and quote Note 105047 — not an Oracle whitepaper — when a customer or
> an Oracle consultant proposes a topology.

---

## 1. What SAP permits — verbatim from Note 105047 **[V]**

| Feature | SAP position |
|---|---|
| **Physical Standby** | ✅ **"You can use"** |
| **Logical Standby** | 🚫 **"You cannot use"** — flat prohibition |
| **Data Guard Broker** | ✅ "You can use" |
| **Fast-Start Failover (FSFO)** | ⚠️ **"Allowed… but SAP Support is not provided"** |
| **Maximum Performance mode** | ✅ Permitted |
| **Maximum Availability mode** | ✅ Permitted — **"pay particular attention to a fast network connection"** |
| **Maximum Protection mode** | ✅ Permitted — **see the warning below** |
| **Data Guard Fast Sync (`SYNC NOAFFIRM`)** | ✅ "Use permitted" |
| **Active Data Guard Far Sync** | ✅ Permitted — **the Active Data Guard Option must be licensed** |
| **Active Data Guard** | ⚠️ Note 105047 directs interested customers to contact a named SAP representative — treat as **not self-service**; raise it commercially before assuming availability |

> ## 🛑 Maximum Protection terminates your primary
>
> Note 105047, verbatim: **"Maximum Protection causes the primary database to terminate if problems
> occur in the standby database."** **[V]**
>
> That is the *designed* behaviour — zero data loss is enforced by halting the primary rather than
> letting it run unprotected. Choosing Maximum Protection means accepting that a standby or network
> failure is a **production outage**. Most SAP landscapes want **Maximum Availability**, which
> degrades to asynchronous instead of stopping. Never set Maximum Protection without the customer
> explicitly accepting that trade in writing.

**Two more rules from the same Note that constrain Data Guard designs [V]:**

- **Read-only mode:** *"You can use a read-only database for administrative purposes only (for
  example, consistency check on standby side). **You cannot start an SAP instance on a read-only
  database.**"* (Note 817253) — so a plain physical standby **cannot serve an SAP application
  server**. Offloading real SAP workload needs Active Data Guard, with its licence and the
  commercial conversation above.
- **Enterprise Edition is mandatory:** *"SAP products always require Oracle Enterprise Edition (EE);
  use with Oracle Standard Edition (SE) is not permitted."* Data Guard is an EE feature anyway, but
  this closes the door on SE-based workarounds.

**Related, frequently conflated:** **RAC** is permitted per Note 527843, but **RAC One Node is not
allowed**. RAC is *not* DR — it is instance-level HA on shared storage. Data Guard is the DR layer.
Do not let one be sold as the other. **[V]**

---

## 2. Establish the version first

```bash
# as ora<sid> (or the Oracle owner)
sqlplus -s / as sysdba <<'SQL'
set lines 200 pages 50
select banner_full from v$version;
select database_role, open_mode, protection_mode, protection_level,
       switchover_status, db_unique_name from v$database;
SQL
```

`protection_mode` vs `protection_level` is the pair that matters: when they **differ**, the
configuration has degraded from its configured intent (e.g. configured MAXIMUM AVAILABILITY but
currently RESYNCHRONIZING). That divergence is the single most useful early warning in Data Guard.

Which Oracle releases SAP supports at all is a separate question — see `sap-backup-recovery`
§version matrix and the Oracle release notes in Note 105047's referenced notes.

---

## 3. The DGMGRL command surface

Broker is permitted, and it is the sane way to drive Data Guard. **[G — Oracle 19c Broker
documentation; SAP permits the tool, Oracle defines the syntax]**

```bash
dgmgrl sys@<db_unique_name>
```

| Command | Purpose |
|---|---|
| `SHOW CONFIGURATION` | Overall state — start here |
| `SHOW DATABASE <name>` | Per-database detail, including apply lag and transport lag |
| `VALIDATE CONFIGURATION` | **Readiness for switchover/failover** — run *before* you need it |
| `VALIDATE DATABASE <name>` | Validates redo transport and apply for one database |
| `SWITCHOVER TO <name>` | **Planned**, role reversal, no data loss |
| `FAILOVER TO <name>` | **Unplanned**, promotes a standby; the old primary is left behind |
| `REINSTATE DATABASE <name>` | Rebuild the old primary as a standby after a failover |
| `CONVERT DATABASE <name> TO SNAPSHOT STANDBY` / `TO PHYSICAL STANDBY` | Temporarily open a standby read-write for testing |

**Switchover vs failover is the distinction people blur:**

| | Switchover | Failover |
|---|---|---|
| Planned? | Yes | No |
| Data loss | None | Possible (depends on protection mode) |
| Old primary | Becomes standby automatically | **Left behind — needs `REINSTATE`** |

> **`REINSTATE DATABASE` requires Flashback Database** to be enabled on the old primary, otherwise
> you rebuild it from a backup instead. SAP **permits Flashback Database** (Note 966117) **[V]** —
> enabling it in advance is what turns a painful post-failover rebuild into one command.

**Snapshot standby restrictions** **[G]**: a physical standby **cannot** be converted to snapshot
standby while it is the target of fast-start failover (**ORA-16668**). A snapshot standby **cannot**
be the target of a switchover or an FSFO, though it can be the target of a *manual* failover when
FSFO is disabled.

---

## 4. Backups, BR*Tools and the standby

- **RMAN is permitted** for backup, restore and recovery; from **12c**, cross-platform
  backup/restore is permitted too. **[V, Note 105047]**
- **Online backups without `BEGIN BACKUP`** are only permitted with RMAN, or with tools meeting the
  requirements of Oracle metalink 604683.1. **[V]**
- **Block Change Tracking** is permitted (Note 964619) — relevant if you offload incremental backups
  to the standby. **[V]**
- Backing up from the standby is a standard reason to run Data Guard; see
  [references/dataguard-operations.md](references/dataguard-operations.md) and `sap-backup-recovery`
  for the BR*Tools side.

---

## 5. Known error worth recognising

**`ORA-16724: cannot resolve gap for one or more standby databases`** — SAP Note **2898813** **[G]**.
A redo gap the standby cannot close on its own, usually because the required archive logs have been
deleted on the primary before shipping. It is a *retention* failure as much as a Data Guard failure —
check the RMAN deletion policy accounts for the standby's needs.

**`ORA-03171`** when accessing a table on a **non**-Active Data Guard standby — SAP Note **2633327**
**[G]**. A reminder that a plain physical standby is not readable in the way people assume.

---

## 6. Where the rest lives

| Topic | File |
|---|---|
| Setup outline, protection-mode changes, switchover/failover runbooks, monitoring queries, standby backups | [references/dataguard-operations.md](references/dataguard-operations.md) |

## Cross-references
- **`sap-backup-recovery`** — RMAN, BR*Tools, Oracle version matrix, backup encryption/TDE keys.
- **`sap-db-command-reference`** — Oracle start/stop, `sqlplus`, `ora<sid>` / `<sid>adm` users.
  **Different technologies; no commands transfer.**
- **`sap-space-reclaim`** — Oracle ADR `cdump`, archive-log space, and the retention that causes ORA-16724.

**The other five database HA/DR skills — different technologies, no commands transfer:**

- **`sap-hana-system-replication`** — HANA System Replication (`hdbnsutil`, HSR).
- **`sap-ase-hadr`** — ASE HADR / Always-On (Replication Server, RMA `sap_*`).
- **`sap-db2-hadr`** — Db2 HADR (`HADR_SYNCMODE`, SA MP / Pacemaker).
- **`sap-sqlserver-alwayson`** — SQL Server Always On (availability groups, listener).
- **`sap-maxdb-ha`** — MaxDB / liveCache (Hot Standby, shadow database, cluster failover).
- **`sap-client-copy-accelerator`** — its Oracle path may reach for `NOLOGGING`, which `FORCE LOGGING` silently overrides on a Data Guard primary.

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
| **[DG1]** | **SAP Note 105047** — *Support for Oracle functions in the SAP environment*, v**247**, 02.07.2026, BC-DB-ORA | **[V]** — the Data Guard, Fast Sync, Far Sync, read-only, RAC, RMAN and Edition entries all read directly |
| **[DG2]** | **SAP Note 817253** — *FAQ: Open a Database Read only* | **[G]** |
| **[DG3]** | **SAP Note 966117** — *Oracle Flashback Database technology* (prerequisite for `REINSTATE`) | **[G]** |
| **[DG4]** | **SAP Note 527843** — *Oracle RAC support in the SAP environment* | **[G]** |
| **[DG5]** | **SAP Note 964619** — *RMAN: Incremental backups with block change tracking* | **[G]** |
| **[DG6]** | **SAP Note 2898813** — *ORA-16724: cannot resolve gap for one or more standby databases* | **[G]** |
| **[DG7]** | **SAP Note 2633327** — *ORA-03171 while accessing table in a Non Active Data Guard database* | **[G]** |
| **[DG8]** | **SAP Note 740897** / **581312** — Oracle licence scope and licensing restrictions | **[G]** |
| **[DG9]** | Oracle — *Data Guard Broker, Command-Line Interface Reference*, Database 19c | **[G]** — DGMGRL syntax; SAP permits the tool, Oracle defines the commands |
| **[DG10]** | SAP Help Portal — *Oracle Standby Databases* (SAP NetWeaver) | **[G]** |

> **Note 105047 is revised frequently** — v247 was released 02.07.2026. It is the single most
> important Oracle-under-SAP reference and its verdicts change. **Re-read the Data Guard row before
> committing to a design**; do not rely on this file's snapshot.

> **A contact detail was deliberately omitted.** Note 105047 routes Active Data Guard enquiries to a
> named individual's SAP e-mail address. That address is not reproduced here — this is a public
> repository. Read it from the live Note.
