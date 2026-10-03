---
name: sap-backup-recovery
description: >-
  Back up and (critically) recover the database under a SAP system — backup and recovery types,
  log/recovery-mode prerequisites, and the per-DB restore commands for HANA, Oracle, ASE, Db2,
  MaxDB and SQL Server on Linux/Windows/AIX. Use for "restore the database", "recover to point
  in time", "backup strategy", "test restore", "brrecover", "RECOVER DATA", "db2 rollforward",
  "RESTORE DATABASE".
---

# SAP Backup & Recovery

Backup essentials live in each DB's file in [sap-db-command-reference](../sap-db-command-reference/SKILL.md);
this skill is the **recovery** side + strategy — the part you need when something has gone wrong.

> **Guardrail — recovery is the highest-stakes operation in the plugin.**
> - **The golden rule:** a backup you have **not test-restored** is not a backup. Prove restores on a
>   sandbox/copy on a schedule.
> - **Point-in-time recovery needs log/archive mode ON** and log backups running (Oracle ARCHIVELOG, SQL
>   Server FULL recovery model, Db2 archive logging, HANA log_mode=normal). Confirm *before* you rely on it.
> - **A production restore is a declared disaster procedure** — confirm scope, target, and the exact
>   recovery point with the owner (typed confirmation). Restoring the wrong backup/target is unrecoverable.
> - **Never delete logs/backups you might still need** to reach the recovery point (see
>   [sap-housekeeping](../sap-housekeeping/SKILL.md) §6).
> - Identify SID/host/DB/OS → classify PRD → preview the exact restore + recovery point → confirm → run →
>   verify the DB opens and the data is at the expected point.
> - **Version first, command second.** Establish DB version, kernel, OS — and for Oracle the **BR\*Tools
>   patch level** — before quoting anything (§3a). The same command is correct on one release and
>   destructive on another.
> - **Ask whether anything is encrypted before you promise a restore** (§3b). Keys are a separate asset;
>   without them the backup is unusable on any host but the original.

---

## 1. Backup types & the log-mode prerequisite

| Type | What | Needed for |
|------|------|-----------|
| **Full / data** | the whole database | the base of any restore |
| **Incremental / differential** | changes since last full/incremental | faster backups, shorter restore chains |
| **Log / redo / transaction** | the transaction log stream | **point-in-time recovery** |

Each DB has a "am I able to do PITR?" switch — verify it's on: Oracle **ARCHIVELOG**, SQL Server **FULL**
recovery model, Db2 **LOGARCHMETH1=archive**, HANA **log_mode=normal** + log backups, ASE **truncate log on
chkpt = off** + log dumps, MaxDB **log mode** (not overwrite/demo). Details per DB in
[references/db-backup-recovery.md](references/db-backup-recovery.md).

## 2. Recovery types (the decision before you run anything)

1. **To the most recent state** — restore last full + all logs to now (needs the log stream intact).
2. **To a point in time** — restore + roll forward/replay logs to a chosen timestamp (e.g. just before a
   bad change). Needs log/archive mode (§1).
3. **To a specific backup** — restore one full/data backup only (no roll-forward); loses changes after it.

Pick the type + recovery point **first**, then use the per-DB command (§3). SAP landscapes usually drive
scheduled backups from **DBA Cockpit (DB13)**; recovery is done with the DB-native tools below.

## 3. Per-DB restore/recover — dispatch

| DB (`dbms_type`) | Backup | Restore / recover entry point |
|------------------|--------|-------------------------------|
| **HANA** (`hdb`) | `BACKUP DATA …` | `RECOVER DATA …` / HANA Cockpit or Studio *Recover Database* (system vs tenant; most-recent / PIT / specific) [V, B1] |
| **Oracle** (`ora`) | `brbackup` / RMAN | `brrestore` + `brrecover` (complete / PIT / redo / disaster) or RMAN `restore`+`recover` |
| **ASE** (`syb`) | `dump database` / `dump transaction` | `load database` → `load transaction` → `online database` |
| **Db2** (`db6`) | `db2 backup database` | `db2 restore database …` → `db2 rollforward … to <ts>/end of logs` |
| **MaxDB** (`ada`) | `backup_start` | `dbmcli recover_start … / recover_replace` (Database Studio recovery wizard) |
| **SQL Server** (`mss`) | `BACKUP DATABASE`/`LOG` | `RESTORE DATABASE … WITH NORECOVERY` → `RESTORE LOG … WITH RECOVERY [STOPAT …]` |

Full commands, PITR syntax, and verify steps for each: **[references/db-backup-recovery.md](references/db-backup-recovery.md)**.

## 3a. Establish the version before quoting any command

**The same database name is not the same procedure.** Before producing commands, pin down three things —
all three, because the matrix is three-dimensional: **DB version**, **SAP kernel release**, **OS** — and
for Oracle a fourth, the **BR\*Tools patch level**, which gates more than the DB version does.

```bash
disp+work -version | head -20          # kernel release + patch level
echo $dbms_type                        # DB type as SAP sees it
```

| DB | Version query | The divergence that matters |
|---|---|---|
| **HANA** | `SELECT VERSION FROM M_DATABASE;` | 1.0 vs 2.0; **MDC tenants vs single-container**; **LSS** active |
| **Oracle** | `SELECT banner_full FROM v$version;` **+ `SELECT cdb FROM v$database;`** | **CDB/PDB multitenant** — different recovery model entirely |
| **Db2** | `db2level` | 10.x vs 11.x; fix-pack-gated behaviour |
| **ASE** | `select @@version` | cumulative dumps are **16.0+** |
| **MaxDB** | `dbmcli … dbm_version` | — |
| **SQL Server** | `SELECT @@VERSION;` | backup-to-URL, TDE, ADR differ by release |

**Then check it is a supported combination** — the **Product Availability Matrix**, per SAP Note **3432900**:
PAM → application → *Technical Release Information* → *Database Platforms* → filter Kernel / Database / OS,
and read the **"Supported until" End of Maintenance date**, not just the tick. [G, PAM]

Method, per-DB support notes and the full divergence list:
**[references/version-support-matrix.md](references/version-support-matrix.md)**

---

## 3b. Encryption — the backup you cannot decrypt

If **any** of data volume, log volume or backup stream is encrypted, the keys are a **separate asset with a
separate lifecycle**, and a restore onto a different host will fail without them — often with an error that
looks like data corruption rather than a key problem.

> 🚨 **HANA with LSS active:** an LSS key backup taken on one server and recovered on another, with volume
> encryption on both, produces a database that **will not start**, reporting
> `invalid checksum algorithm 6` and `Could not read AnchorPage`. That is a key mismatch, **not**
> corruption. `hdbnsutil -backupRootKeysAndSettings` also covers **all** root key types at once — you
> cannot back up just one. [V, LSS]

> **Oracle TDE:** BR\*Tools only gained *Manage data encryption* at **7.40 Patch 30**. **SQL Server TDE:**
> the certificate **and private key** must be restored into `master` on the target *before* the database
> restore. **Db2:** the keystore and master key label must exist on the target first.

Full treatment — the four questions to ask on any platform, per-DB key commands, and the only restore test
that actually proves key management works:
**[references/backup-encryption-keys.md](references/backup-encryption-keys.md)**

---

## 4. Test-restore discipline

- Restore to a **sandbox / different SID or host**, not over the source, to validate a backup.
- After any recovery: confirm the DB **opens**, the SAP instances start
  ([sap-system-lifecycle](../sap-system-lifecycle/SKILL.md)), and spot-check the data reaches the expected
  recovery point. `R3trans -d` ([sap-health-triage](../sap-health-triage/SKILL.md)) confirms the kernel can
  reach the DB again.

## Cross-references

- **Connect / start-stop the DB (needed around a restore):** [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
- **Log/archive housekeeping (only after a good backup):** [sap-housekeeping](../sap-housekeeping/SKILL.md).
- **DB logs to diagnose a failed restore:** [sap-log-reference](../sap-log-reference/SKILL.md) → db-logs.
- **`sap-client-copy-accelerator`** — take a restore point before a native bypass load; `NOLOGGING` breaks recoverability of the loaded segments.

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

- **[PAM]** **SAP Note 3432900** — *How to check supported versions of Database/Kernel/OS in the Product
  Availability Matrix (PAM)* (BC-DB-DB6). **[V]** The PAM navigation procedure used in §3a.
- **[MT]** **SAP Note 2333995** — *BR\*Tools support for Oracle multitenant database* (BC-DB-ORA-DBA,
  v16). **[V]** The BR\*Tools patch gates and `-rpd|-recov_pdb` behaviour behind §3a and the Oracle section
  of [references/db-backup-recovery.md](references/db-backup-recovery.md).
- **[LSS]** **SAP Note 3756303** — *How to backup and recover SAP HANA Root Keys when Local Secure Store
  (LSS) is active* (HAN-DB-SEC, v2). **[V]** Behind §3b and
  [references/backup-encryption-keys.md](references/backup-encryption-keys.md).
- **SAP Note 1642148** — *FAQ: SAP HANA Database Backup & Recovery*; **2444090** — *FAQ: SAP HANA Backup
  Encryption*; **2165547** — *… System Replication Landscape*; **2101244** — *FAQ: MDC*. **[V]**
- **SAP Note 1174136** (Oracle end-of-support dates), **101809** / **1168456** (Db2 supported versions and
  end of support), **1948334** (HANA update paths), **2162183** / **1941500** (ASE), **1076022**
  (SQL Server release planning). **[V]**

- **[B1]** *Recover a Database* / *RECOVER DATA Statement* — SAP HANA Administration Guide (HANA Cockpit /
  Studio; most-recent / point-in-time / specific backup; system vs tenant; backup catalog). **[V]**
  https://help.sap.com/docs/SAP_HANA_PLATFORM/4fe29514fd584807ac9f2a04f6754767/93637a07e3b544398aa02de1541b903c.html
- **[B2]** Oracle `brrestore`/`brrecover` (+ RMAN) — SAP Database Administration: Oracle (BC-DB-ORA).
- **[B3]** ASE `load database`/`load transaction`/`online database` — SAP ASE System Administration Guide.
- **[B4]** Db2 `restore` + `rollforward` — SAP on IBM Db2 for LUW Administration Guide (BC-DB-DB6).
- **[B5]** MaxDB `recover_start`/`recover_replace` — SAP MaxDB Database Administration.
- **[B6]** SQL Server `RESTORE DATABASE`/`RESTORE LOG … STOPAT` — MS SQL Server docs + SAP DBOS.

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): each DB's current
backup/recovery guide and your landscape's DB13 backup schedule + retention policy.
