---
name: sap-housekeeping
description: >-
  Keep a SAP NetWeaver / S/4HANA system's logs, traces, spool, job logs, ABAP dumps, audit logs and work
  directory from filling the filesystem — via the SAP standard reorganization jobs (RSBTCDEL2, RSPO1041,
  RSSNAPDL, RSBDCREO …) and safe OS-level cleanup, on Linux/Windows/AIX. Use for "clean up logs/traces",
  "/usr/sap is full", "reorg spool/jobs/dumps", "housekeeping jobs", "delete old work-dir files",
  "audit log cleanup". Hands DB log/trace cleanup to sap-db-command-reference. Cited to SAP Note 16083 +
  help.sap.com.
---

# SAP Housekeeping (logs / traces / spool / jobs / filesystem)

Two layers: **ABAP-side reorg jobs** (the correct, retention-aware way — §1) and **OS-side file cleanup**
(§3, for what the jobs don't cover). DB log/trace cleanup is delegated to
[sap-db-command-reference](../sap-db-command-reference/SKILL.md) (§6).

> **Guardrail — deletion is destructive and sometimes compliance-bound.**
> Identify SID/host → classify PRD → **preview what will be deleted and how far back** → confirm (typed
> for PRD) → delete → verify. Specific hazards, do NOT skip:
> - **Audit logs are often legally required** — check retention with security/auditors before deleting (§4).
> - **Never delete DB logs/archives that aren't backed up** — data-loss risk (§6).
> - **Prefer the standard reorg jobs** (they honour configured retention) over manual `rm`.
> - Never `rm` a **live** trace of a running instance.

---

## 1. The standard reorganization jobs (the right way) — SAP Note 16083 [G, K1]

Schedule these in **SM36** ("Standard jobs" button auto-creates them). They delete by **age/retention**,
not blindly. ABAP-side, so OS-independent.

| Job name | Report | Cleans | Frequency |
|----------|--------|--------|-----------|
| `SAP_REORG_JOBS` | `RSBTCDEL2` | old background **job logs** (SM37) | daily |
| `SAP_REORG_SPOOL` | `RSPO1041` (improved `RSPO0041`) | old **spool** requests (SP01) | daily |
| `SAP_REORG_ABAPDUMPS` | `RSSNAPDL` | old **ABAP short dumps** (ST22) | daily |
| `SAP_REORG_BATCHINPUT` | `RSBDCREO` | old **batch-input** sessions (SM35) | daily |
| `SAP_REORG_JOBSTATISTIC` | `RSBPSTDE` | old job **statistics** | monthly |
| `SAP_REORG_UPDATERECORDS` | `RSM13002` | old **update** records (SM13) | daily |
| `SAP_COLLECTOR_FOR_PERFMONITOR` | `RSCOLL00` | collects/reorgs performance stats (ST03) | hourly |
| `SAP_REORG_XMILOG` | `RSXMILOGREORG` | external management interface log | weekly/monthly |

- `RSBTCDEL2`: run by the **batch administrator** → reorganizes **all** clients; otherwise current client
  only. [K1]
- `RSPO1041`: set the retention/age in its variant. Also run spool/**TemSe** consistency regularly:
  `RSPO1043` (spool) and the TemSe check (SP12 / SAP Notes 48400, 130978). [K2]

---

## 2. Spool & TemSe consistency

```
SP12  → TemSe consistency check & reorg (temporary sequential objects)
RSPO1043 → spool consistency check
```
Inconsistent TemSe/spool is a common cause of a spool filesystem/table growing despite `RSPO1041`. [K2]

---

## 3. OS-level cleanup — the instance work directory

Work directory: `/usr/sap/<SID>/<INST><nr>/work/` (Windows: `…\work\`). Safe-to-remove candidates when a
filesystem is filling, **oldest first, and never the currently-active file**: [G, K4]

| Pattern | What it is | Safe to delete? |
|---------|-----------|-----------------|
| `*.OLD` | previous traces, re-created on each restart | ✅ yes |
| `core`, `core.<pid>` | crash core dumps | ✅ after capturing for analysis |
| old `dev_w*`, `dev_rfc*`, `dev_rd` | rotated work-process/RFC/gateway traces | ✅ old ones; not the active |
| `stderr<n>` | per-start stdout/stderr | ✅ old ones |
| `dev_disp`, `dev_ms`, `dev_icm` (current) | live dispatcher/msg/ICM traces | ⚠️ **reset via SM50/SMGW**, don't `rm` while running |

Reset traces cleanly from the app rather than deleting the active file: **SM50** (work process traces),
**SMGW** (gateway). Also check `/sapmnt/<SID>/global` for old `WF_LOG_*` workflow files.

## 4. Security audit log  ⚠️ retention/compliance

Audit log files (`*.AUD`) under `/usr/sap/<SID>/<INST><nr>/log/` (SM19/RSAU config, SM20 view). Delete
via **SM18** (or a scheduled reorg), **not** blind `rm`: [G, K3]
```
SM18 → reorganize/delete audit logs older than <retention>
```
> **Confirm the retention requirement with security/audit/compliance before deleting audit logs.** These
> are frequently required to be kept for a mandated period. This is the one cleanup that can create a
> compliance incident.

## 5. Orphaned IPC / shared memory (`cleanipc`)

After an instance crash, orphaned shared-memory/semaphore segments can block a restart. Clean them (UNIX):
```bash
cleanipc <nr> remove          # remove IPC resources of instance <nr>  ⚠️ only when the instance is DOWN
```
Run **only** when that instance is stopped — it wipes the instance's shared memory. [G, K4]

## 6. Database logs/traces → delegate

DB transaction/redo/archive logs and DB traces are cleaned with **DB tools**, not `rm`, and only **after a
successful backup**:
- see [sap-db-command-reference](../sap-db-command-reference/SKILL.md) per `dbms_type`;
- e.g. Oracle archived redo via `brarchive -sd` (after backup), Db2 archived logs, HANA log segments +
  backup-catalog housekeeping.
> **Never delete an un-backed-up transaction log** — it breaks point-in-time recovery. [G]

## 7. "Filesystem full" quick triage

```bash
df -h                                         # which FS: /usr/sap, /sapmnt, DB data, DB log, /oracle, /hana
du -sh /usr/sap/<SID>/<INST><nr>/work/* | sort -h | tail   # biggest offenders in work/
```
Then: §3 (work dir) for `/usr/sap`; §6 (DB, after backup) for the DB/log filesystems; §1 (reorg jobs) so
it doesn't refill. Cross-ref [sap-health-triage](../sap-health-triage/SKILL.md) — full FS is its #1
"won't start / hung" cause.

## Cross-references

- **DB-side log cleanup:** [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
- **What's filling it / is it healthy:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Full standard-jobs list + OS file-type map:** [references/cleanup-catalog.md](references/cleanup-catalog.md).

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

- **[K1]** **SAP Note 16083** — *Standard jobs, reorganization jobs* (the canonical list: `RSBTCDEL2`,
  `RSPO1041`, `RSSNAPDL`, `RSBDCREO`, `RSBPSTDE`, `RSM13002`, `RSCOLL00`, …). https://me.sap.com/notes/16083
- **[K2]** `RSPO1041`/`RSPO1043` spool + TemSe consistency — **SAP Notes 130978** (RSPO1041) and **48400**
  (TemSe/spool consistency). https://me.sap.com/notes/48400
- **[K3]** Security audit log housekeeping via **SM18** + retention — SAP Security Audit Log documentation
  (help.sap.com) and SM18/SM19/SM20.
- **[K4]** Work-directory / `*.OLD` / core files / `cleanipc` — SAP OS-file housekeeping (help.sap.com +
  SAP Basis operations).
- **[K5]** *Housekeeping for SAP HANA Platform* (DB-side, for `dbms_type = hdb`).
  https://help.sap.com/doc/f3dd8d9fb4ab407eb15ee4bf336ae42b/9.3/en-US/Housekeeping%20for%20SAP%20HANA.pdf

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): SAP Note 16083 for the full current
job list + report variants, and Note 48400 for the TemSe/spool consistency procedure.
