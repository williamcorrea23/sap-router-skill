---
name: sap-sqlserver-alwayson
description: >-
  SQL Server Always On Availability Groups under SAP NetWeaver — listener-based connection
  configuration (SAPDBHOST, dbs/mss/server, MSSQL_SERVER, MultiSubnetFailover and the
  case-sensitive JDBC parameter), why logins must be created by SWPM "Configure additional
  Always On Node" and never manually, the readable-secondary rules including the unsupported
  "Yes" setting, sync vs async and the latency guidance, WSFC without shared disks, and per-node
  failover verification. Also covers Database Mirroring. Use for "SQL Server AlwaysOn SAP",
  "availability group", "listener", "MultiSubnetFailover", "readable secondary", "SAP cannot
  connect after failover", "error 976".
---

# SQL Server Always On under SAP NetWeaver

**Source of record.** **SAP Note 1772688 — *SQL Server Always On Availability Groups and SAP
NetWeaver-based applications***, version **25**, released **21.01.2026**, component BC-DB-MSS
**[V]** — fetched and read directly.

> ## 🛑 This Note is the only supported source
>
> Note 1772688, verbatim: *"This SAP Note centralizes the setup and configuration details for
> AlwaysOn. **Only the procedures explained here in this SAP Note are supported** for SAP
> installations on AlwaysOn. As of July 2020, **please do not use external blogs, other SAP Notes, or
> outdated SAP installation and upgrade guides** when working with SAP NetWeaver on AlwaysOn."* **[V]**
>
> That is unusually strict, and it applies to this skill too. **Treat this file as a map to the Note,
> not a replacement for it** — read the live Note before executing a lifecycle procedure.

**Scope:** NetWeaver-based products only. For **non-NetWeaver** products (SAP BusinessObjects, SAP
Redwood) this Note does **not** apply — find the documentation for that application area. **[V]**

---

## 1. Support baseline

| | |
|---|---|
| **NetWeaver** | AlwaysOn supported from **7.0** and all later releases **[V]** |
| **SQL Server 2012+** | AlwaysOn — **strongly recommended** over Database Mirroring **[V]** |
| **SQL Server 2008 R2 or earlier** | Use **Database Mirroring** instead (SAP Note **965908**) **[V]** |
| **JDBC** | Automatic failover via the listener name needs **Microsoft JDBC 4.0 or later** **[V]** |

**WSFC is required, but shared disks are not.** AlwaysOn relies on the Windows Server Failover
Cluster framework for health detection and failover triggering rather than a third witness instance.
*"A cluster configuration without any shared disk would be sufficient."* **[V]**

---

## 2. Planning — two numbers worth memorising

**Distance.** *"Given the nature of SAP workload, any distance larger than **60 miles (96.5 km)**
between AlwaysOn nodes will add latency that impacts performance visibly."* **[V]** That is guidance
for **synchronous** replication. The Note also warns that the mileage rule blurs once a node sits in
a public or private cloud, because virtualization layers you cannot monitor sit underneath — so
**test throughput before deployment** rather than trusting the number.

**Transaction-log I/O latency on the secondary.** With synchronous replication the primary waits on
the secondary's log write, so *"an I/O latency of **5 milliseconds** for write actions significantly
impacts the primary replica and the SAP application compared to having just **1 millisecond**."*
**[V]** The secondary's log LUN is in your primary's commit path — size it accordingly.

---

## 3. Connection configuration — everything points at the listener

**ABAP profile parameters** **[V]**:

```
SAPDBHOST        = <listenername>            # or <listenername>,<static_port>
dbs/mss/server   = <listenername>            # or <listenername>,<static_port>
dbs/mss/conn_opts = MultiSubnetFailover=yes
```

In **`TP_DOMAIN_<SID>.PFL`**: set `<SID>/DBHOST` to the listener name (or `<listener>,<port>`).

**Environment variables for `<sid>adm`** **[V]**:

```
MSSQL_SERVER   = <listenername>
MSSQL_CONNOPTS = MultiSubnetFailover=yes
```

**DBCON (remote SQL Server in an availability group)** — add `CON_ENV` using the shorthand **[V]**:

```
;COP=MultiSubnetFailover=yes
```

**Java** **[V]**: set `SAPDBHOST`, `dbs/mss/server` and `j2ee/dbhost` to the listener name, and in the
config tool's secure store append to the connection URL:

```
jdbc:sqlserver://<Listenername>:<static_port>;databasename=<DB>;multiSubnetFailover=true
```

> ## ⚠️ The Java parameter is case-sensitive — and fails silently
>
> Note 1772688: *"**Caution:** This is case-sensitive. Make sure the character case is exactly as
> shown here. **If it's not the exact same as indicated here, the Microsoft JDBC client ignores the
> parameter.**"* **[V]**
>
> `multiSubnetFailover=true` — lower-case `m`, capital `S`, capital `F`. Get it wrong and nothing
> errors; you simply lose automatic failover, and only discover it during a real failover.

Note the asymmetry: ABAP uses `MultiSubnetFailover=yes`, Java uses `multiSubnetFailover=true`.

---

## 4. Logins — never create them by hand

> ## 🛑 *"Do not create logins manually or using any tSQL script in the secondary replicas."* **[V]**

SWPM creates the login `<sid>` (ABAP) or `SAP<SID>DB` (Java) in the secondary replicas **with the
same globally unique security identifier (SID)** as the primary. A hand-made login has a different
SID and **breaks the connection after failover** — this is the documented root cause of the most
common AlwaysOn incident (§7).

**Correct procedure** **[V]**:

1. **Stop all SAP application server instances.**
2. Fail the availability group over to a secondary node.
3. On that node run SWPM → **Generic Options → MS SQL Server → Database Tools → Configure additional
   Always On Node**.
   > Choose the **local SQL Server instance name**, **not** the availability group listener name.
4. **Repeat for every node**, one at a time, failing over to each.
5. **Java only:** SWPM creates the Java login with the correct SID but a **random password**. Change
   it to match the original primary on **all** secondaries, then **restart the SQL Server instance**.
6. Start the application servers and test the connection **against every replica**.

Use SWPM from **NetWeaver 7.1 or higher media** — even when installing a system based on NetWeaver
7.0. **[V]**

---

## 5. Readable secondaries — one setting is unsupported

AlwaysOn offers three read-only settings per replica: **`No`**, **`Read-intent only`**, **`Yes`**.

> ## 🛑 Never set an SAP `<SID>` database secondary replica to **`Yes`**
>
> *"It's **not supported** to set any SAP NetWeaver SID database secondary replicas to 'Yes.'"* **[V]**
>
> `Yes` accepts **every** connection and makes them all read-only. **SAP work processes assume more
> than read-only access, and their behaviour cannot be customised.** If a work process connects
> accidentally, it fails the moment it tries to modify data. The local SAP `<SID>` database's
> secondaries may be **`No`** or **`Read-intent only`** — never `Yes`.

**Synchronous does not mean readable-and-current.** *"Synchronous data replication acknowledges the
successful writing into the transaction log… However, this doesn't mean that the changes transmitted
have already been applied to the actual data of the secondary replica."* **[V]** So even a
synchronous readable secondary can serve stale data while log records are still being applied.
Asynchronous is worse and unpredictable.

**Remote DBCONs: always connect to the primary.** The Note documents two real customer failures —
a process tuned against a synchronous remote secondary that degraded when the link was later changed
to asynchronous, and one that stopped meeting its time budget as the system grew. Conclusion:
*"always connect to the primary node of a remote SQL Server availability group replica."* **[V]**

> **A cautionary tale worth repeating to customers.** SAP Development Support saw a primary database
> reach **in four months the size projected for two years**. Cause: versioned records created by
> non-SAP processes running on readable secondaries, combined with poor I/O throughput that slowed
> the ghost-record cleanup. **[V]** If you enable readable secondaries, monitor database size and I/O
> throughput deliberately.

---

## 6. Verify by failing over — the step everyone skips

> *"Many customers don't test all nodes in their AlwaysOn landscape. When a failover emergency
> occurs, secondary nodes may not be configured properly. As a result, SAP NetWeaver can't start.
> **This issue affects many customers and leads to immediate production downtime and escalation.**"*
> **[V]**

**ABAP:** `DBACOCKPIT` → **Configuration → SQL Server Always On Check** — verifies logins and jobs
and reports configuration errors. **[V]**

**Java:** no tool exists. You must fail over to each node and confirm the Java application server
connects. **[V]**

**Both:** fail over to **each node, one at a time**, and log in after each. Then **[V]**:

- Keep the system running on the failover node for **at least 20 minutes**
- Verify **DBA Cockpit jobs and SQL Agent jobs** continue to run
- Compare performance between nodes — run business transactions and compare **ST03N** statistics

Do this after initial setup **and after any change** to the landscape.

---

## 7. The two documented failures

**1. SAP cannot connect after failover** (ABAP), or the Java config tool cannot scan the database.

- **Cause:** the `<sid>` / `SAP<SID>DB` login was **created manually** in the secondary replicas. **[V]**
- **Fix:** delete the login, then run SWPM **Configure additional Always On Node** (§4).
- *Temporary* workaround: re-run that SWPM option after every failover — a symptom-level patch,
  not the fix.
- Related: SAP Note **1907868**.

**2. SWPM "Configure additional Always On Node" fails** with
`Creation of a new database is not allowed` / `MDB-05702`.

- **Cause:** SWPM changes SQL Server settings and restarts it, which **triggers a failover** to a
  different replica mid-run. **[V]**
- **Fix:** fail the availability group **back** to the replica where SWPM is running, then **repeat
  from the error phase** — no need to restart SWPM from the beginning.

---

## 8. Where the rest lives

| Topic | File |
|---|---|
| Install / system copy / refresh / dual-stack split / SUM upgrade sequences, monitoring, Database Mirroring | [references/alwayson-lifecycle.md](references/alwayson-lifecycle.md) |

## Cross-references
- **`sap-backup-recovery`** — SQL Server backup/restore; the `NORECOVERY` restores that seed replicas.
- **`sap-db-command-reference`** — SQL Server service control, `sqlcmd`, Windows specifics.
- **`sap-system-lifecycle`** — stopping application servers before AlwaysOn node configuration.

**The other five database HA/DR skills — different technologies, no commands transfer:**

- **`sap-hana-system-replication`** — HANA System Replication (`hdbnsutil`, HSR).
- **`sap-ase-hadr`** — ASE HADR / Always-On (Replication Server, RMA `sap_*`).
- **`sap-oracle-dataguard`** — Oracle Data Guard (physical standby, DGMGRL).
- **`sap-db2-hadr`** — Db2 HADR (`HADR_SYNCMODE`, SA MP / Pacemaker).
- **`sap-maxdb-ha`** — MaxDB / liveCache (Hot Standby, shadow database, cluster failover).

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
| **[AO1]** | **SAP Note 1772688** — *SQL Server Always On Availability Groups and SAP NetWeaver-based applications*, v**25**, 21.01.2026, BC-DB-MSS | **[V]** — planning, lifecycle sequences, profile/env parameters, login procedure, restrictions and troubleshooting all read directly |
| **[AO2]** | **SAP Note 965908** — *SQL Server Database Mirroring and SAP Applications* (the pre-2012 predecessor) | **[G]** |
| **[AO3]** | **SAP Note 2137130** — *How to set MSSQL_SERVER and MSSQL_CONNOPTS for SQL Server AlwaysOn and Mirroring* | **[G]** |
| **[AO4]** | **SAP Note 1907868** — *SAP system cannot connect to SQL Server after AlwaysOn/Mirroring failover* | **[G]** |
| **[AO5]** | **SAP Note 3679673** — *"The target database … is participating in an availability group and is currently not accessible for queries." Logon Error: 976* | **[G]** |
| **[AO6]** | **SAP Note 2153963** — *DBACOCKPIT (DB13 and DB12) not working correctly with SQL Server AlwaysOn and Mirroring* | **[G]** |
| **[AO7]** | **SAP Note 3590454** — *How to remove 'SQL Server AlwaysOn' from an existing SAP NetWeaver system installation* | **[G]** |
| **[AO8]** | **SAP Note 2446660** — *System Copy with HA does not set AlwaysOn profile/env parameters* | **[G]** — explains a common post-copy failure |
| **[AO9]** | **SAP Note 1031096** — *Installing Package SAPHostagent* (needed manually on secondaries with no SAP instance) | **[G]** |
| **[AO10]** | **SAP Note 2303398** — *SAP on SQL Server in Microsoft Azure Virtual Machines*; **2116801** — Performance Monitor for AlwaysOn | **[G]** |
| **[AO11]** | SAP Help Portal — *Updating SAP ABAP Systems on Windows: Microsoft SQL* (SUM guide; see *Update Schedule Planning* and *Database-Specific Aspects*) | **[G]** |
| **[AO12]** | Microsoft Learn — *SQL Server Azure Virtual Machines DBMS deployment for SAP workload*; *Configure read-only access to a secondary replica*; *Offload read-only workload to secondary replica* | **[G]** |

> **Currency.** v25 was released 21.01.2026 and the Note is actively maintained — SAP explicitly
> centralised this material in 2020 and asks that nothing else be used. **Re-read it before any
> lifecycle action**; this file records what v25 said, not a standing truth.

> **Azure-specific features** (Distributed Network Names / DNN, and other cloud specifics) are
> deliberately out of scope here — Note 1772688 routes them to Microsoft's documentation and the
> *SAP on Azure* blog. **[V]**
