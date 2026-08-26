---
name: sap-db-command-reference
description: >-
  Database-specific operational commands for SAP systems — start, stop, connect, status and
  basic backup for the SAP-supported databases (SAP HANA, Oracle, SAP ASE/Sybase, IBM Db2,
  SAP MaxDB/liveCache, Microsoft SQL Server), with Linux / Windows / AIX variants. Use whenever
  a Basis/operations task needs the DB layer: "stop the database", "connect to HANA/ASE/Oracle",
  "is the DB up", "restart the database before/after the SAP instances", or when sap-system-lifecycle
  hands off DB start/stop. Every command is cited to help.sap.com / the official Administration Guide.
---

# SAP DB Command Reference

`sapcontrol`/`stopsap` stop the **SAP instances but not the database** — the official SAPControl
documentation states: *"The database is not stopped by these commands. You have to stop the
database using database-specific tools or commands."* This skill is that database-specific layer.

## How to use

1. **Identify the DB.** Determine which database the SID runs on before doing anything:
   - `cat /usr/sap/<SID>/SYS/profile/<SID>_*` → look at `dbms/type` / `dbs/<db>/…`, or
   - environment of `<sid>adm`: `echo $dbms_type` (values: `hdb`, `ora`, `syb`, `db6`, `ada`, `mss`).
2. **Open the matching reference file** below and follow its Identify → Preview → Execute → Verify flow.
3. **Respect the guardrail contract** (see repo README): confirm SID/host/OS, classify PRD, preview
   before any `shutdown`/stop, execute one step at a time via the user-supplied shell/SSH MCP, verify after.

## Database reference files

| DB | `dbms_type` | Reference | Status |
|----|-------------|-----------|--------|
| SAP ASE (Sybase) | `syb` | [references/sap-ase.md](references/sap-ase.md) | ✅ complete |
| SAP HANA | `hdb` | [references/sap-hana.md](references/sap-hana.md) | ✅ complete |
| Oracle Database | `ora` | [references/oracle.md](references/oracle.md) | ✅ complete |
| IBM Db2 (LUW) | `db6` | [references/ibm-db2.md](references/ibm-db2.md) | ✅ complete |
| SAP MaxDB / liveCache | `ada` | [references/sap-maxdb.md](references/sap-maxdb.md) | ✅ complete |
| Microsoft SQL Server | `mss` | [references/sql-server.md](references/sql-server.md) | ✅ complete |

## Cross-references

- **Start/stop ordering** (DB relative to ASCS/ERS/PAS/AAS) lives in `sap-system-lifecycle`.
- **DB log/trace cleanup** (backup catalog, transaction logs, DB traces) lives in `sap-housekeeping`;
  this file covers only the operational start/stop/connect/status commands.

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

See the Sources section at the end of each reference file for the exact help.sap.com pages and
SAP Notes used, and which commands were verified against the live page.
