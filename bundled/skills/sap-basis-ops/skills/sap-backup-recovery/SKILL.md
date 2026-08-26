---
name: sap-backup-recovery
description: >-
  Back up and (critically) recover the database under a SAP system — backup types (full/incremental/log),
  recovery types (most-recent / point-in-time / specific backup), log/recovery-mode prerequisites, and the
  per-DB restore commands for SAP HANA, Oracle, SAP ASE, IBM Db2, SAP MaxDB and MS SQL Server, on
  Linux/Windows/AIX. Use for "restore the database", "recover to point in time", "backup strategy", "test
  restore", "brrecover", "RECOVER DATA", "db2 rollforward", "RESTORE DATABASE". Cited to help.sap.com.
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
3. Prefer the Note over this file where they disagree, and say which Note you followed.

No MCP available? Look the Note up on `me.sap.com/notes/<id>` and say the check was skipped rather than
assuming this file is current.

## Sources

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
