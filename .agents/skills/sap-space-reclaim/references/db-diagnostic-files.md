# Database diagnostic files, traces and crash dumps

Every SAP database writes three broad classes of file that grow without bound and are **not** covered by
the ABAP standard jobs: **traces**, **alert/diagnostic logs**, and **crash/core dumps**. This file covers
where each lives, how to *discover* it rather than assume it, and what the retention mechanism is.

## The rule this file exists to enforce

> **Discover from configuration and file type — never from a filename you assumed.**
> Every database has a *parameter* that says where diagnostics go and a *view or CLI* that lists them.
> Read that, then act. A `find` for a guessed name is how you get both false positives and false
> negatives. See the OS-level version of this mistake in the parent skill's core-dump section.

**Citation status is stated per database.** Oracle and HANA were verified against SAP Notes during
authoring. Db2, ASE, MaxDB and SQL Server are given from vendor-documented mechanisms and are marked
**unverified here** — confirm against the current SAP Note for your platform before acting.

---

## SAP HANA — **[V]** (SAP Notes 2370780, 2399996)

| | |
|---|---|
| **Discover** | **`M_TRACEFILES`** system view — the authoritative inventory of every trace file |
| **Location** | `/usr/sap/<SID>/HDB<nr>/<host>/trace` (and `/hana/shared/<SID>/HDB<nr>/<host>/trace`) |
| **Crash artefacts** | **`*.crashdump.*.trc`**, **`*.rtedump.*.trc`** — *not* named `core` |
| **Remove** | `ALTER SYSTEM REMOVE TRACES (...)` · `ALTER SYSTEM CLEAR TRACES (...)` clears contents |
| **Audit log** | `ALTER SYSTEM CLEAR AUDIT LOG` · `ALTER AUDIT POLICY … SET RETENTION` (≥ 2.0 SPS 04) |
| **Automate** | **SAP HANACleaner** — SAP Note **2399996** |

**Safe to delete** (Note 2370780): `.py` (SQL/server traces), `.old` (previous restart), `.stat` (tiny
placeholders). `dev_webdisp` / `dev_icm_sec` / `icm_port_list` — only while the system is down.

**Must NOT be deleted:** `py.sap<SID>_HDB<nr>` and `hdb.sap<SID>_HDB<nr>` — these link to the Python
runtime and the `hdbdaemon` respectively.

> Note 2370780 states plainly it *"is not a confirmation to delete any file from the system"*. Confirm per
> file.

---

## Oracle — **[V]** (SAP Note 1431751)

Oracle 11g+ consolidates everything into the **Automatic Diagnostic Repository (ADR)**. The old
`USER_DUMP_DEST` / `BACKGROUND_DUMP_DEST` / `CORE_DUMP_DEST` parameters are **deprecated**.

| | |
|---|---|
| **Discover** | `SELECT * FROM V$DIAG_INFO;` — returns ADR Base, ADR Home, Diag Trace, Diag Alert, Diag Incident, Diag Cdump, Health Monitor. Also `show parameter diagnostic_dest`, and `adrci> SHOW HOMES` |
| **ADR base (SAP)** | `DIAGNOSTIC_DEST = $SAPDATA_HOME/saptrace` (Unix) · `%SAPDATA_HOME%\SAPTRACE` (Windows) |
| **ADR home** | `diag/rdbms/<db_name>/<ORACLE_SID>` — plus a separate home per listener, `diag/tnslsnr/<host>/<listener>` |

**Where each artefact lands** (old → ADR):

| Data | Old parameter | ADR location |
|---|---|---|
| **Core dumps** | `CORE_DUMP_DEST` | **`$ADR_HOME/cdump`** |
| Alert log (text) | `BACKGROUND_DUMP_DEST` | `$ADR_HOME/trace` |
| Alert log (XML) | — | `$ADR_HOME/alert` |
| Background process trace | `BACKGROUND_DUMP_DEST` | `$ADR_HOME/trace` |
| User process trace | `USER_DUMP_DEST` | `$ADR_HOME/trace` |
| Incidents | — | `$ADR_HOME/incident/incdir_<n>` |

Trace files are `.trc`, sometimes with a `.trm` trace-map companion — delete them together.

**Retention — already automatic, but check it:**

```
adrci> SHOW CONTROL                        -- current policy
adrci> SET CONTROL (SHORTP_POLICY = 360)   -- incident FILES and DUMPS, default 720h (30 days)
adrci> SET CONTROL (LONGP_POLICY  = 4380)  -- incident METADATA,        default 8760h (1 year)
```

`MMON` purges expired ADR data automatically. **SAP's recommendation is to keep the Oracle defaults** —
so if ADR is growing, the question is usually "what is generating incidents", not "why is purge off".

**Inventory and triage without deleting:**

```
adrci> SHOW HOMES              adrci> SHOW PROBLEM
adrci> SHOW TRACEFILE -RT      adrci> SHOW INCIDENT -MODE BRIEF
```

> ⚠️ **Package before you purge.** If there is an open SAP/Oracle message, build the incident package
> first — `adrci> IPS CREATE PACKAGE INCIDENT <n>` then `IPS GENERATE PACKAGE <p> IN <dir>` — otherwise
> purging destroys the evidence the message depends on.

Alert log growing unbounded: **SAP Note 786032** (*How to trim Oracle Alert log file*).

---

## IBM Db2 — *mechanism from vendor documentation; **not** verified against an SAP Note here*

| | |
|---|---|
| **Discover** | `db2 get dbm cfg` → **`DIAGPATH`** (and `ALT_DIAGPATH`). Never assume `~/sqllib/db2dump` |
| **Main log** | `db2diag.log`, plus the administration notification log `<inst>.nfy` |
| **Crash artefacts** | trap files `t<pid>.<node>`, dump files, core files, and **`FODC_*` directories** (First Occurrence Data Capture) — FODC dirs are frequently the largest item |
| **Retention** | **`DIAGSIZE`** in dbm cfg enables rotating `db2diag.log` files; `db2diag -A` archives the current log |

Discovery-first sequence: read `DIAGPATH`, then size that directory, then look specifically for `FODC_*`
subdirectories before anything else.

---

## SAP ASE (Sybase) — *vendor mechanism; **not** verified against an SAP Note here*

| | |
|---|---|
| **Discover** | the errorlog path is the **`-e`** argument in the server's `RUN_<SERVER>` start script under `$SYBASE/$SYBASE_ASE/install` |
| **Main logs** | ASE errorlog `<SERVER>.log`, Backup Server errorlog, Job Scheduler agent log |
| **Crash artefacts** | shared-memory dumps produced by `sybdumptran`/config, plus OS core files of the `dataserver` process |
| **Retention** | no built-in rotation — the errorlog grows until you cycle it; rotate on a schedule while the server is down, or via the documented online procedure for your ASE version |

---

## SAP MaxDB / liveCache — *vendor mechanism; **not** verified against an SAP Note here*

| | |
|---|---|
| **Discover** | `dbmcli -d <SID> -u <user>,<pw> param_directgetall` / the run directory, typically `/sapdb/data/wrk/<SID>` |
| **Main logs** | `KnlMsg` (kernel message file) and its rollover `KnlMsgArchive`; older releases `knldiag`, `knldiag.err` |
| **Crash artefacts** | `rtedump`, kernel core files in the run directory |
| **Retention** | kernel message file size is a parameter; archived copies accumulate and are the thing to prune |

---

## Microsoft SQL Server — *vendor mechanism; **not** verified against an SAP Note here*

| | |
|---|---|
| **Discover** | the `-e` startup parameter gives the ERRORLOG path (SQL Server Configuration Manager, or `SERVERPROPERTY('ErrorLogFileName')`) |
| **Main logs** | `ERRORLOG` plus numbered generations `ERRORLOG.1` … `ERRORLOG.n` |
| **Crash artefacts** | **`SQLDump####.mdmp`** (minidump) and **`SQLDump####.txt`** — the SQL Server equivalent of a core dump, in the same LOG directory |
| **Other** | default-trace `.trc` files, Extended Events `.xel` files |
| **Retention** | `sp_cycle_errorlog` rolls the log; the **number of generations kept is configurable** (registry / SSMS → *Configure SQL Server Error Logs*). Cycling on a schedule is what bounds it |

---

## Cross-database checklist

1. **Read the parameter that defines the diagnostic path** — do not assume the default.
2. **List via the DB's own inventory** (`M_TRACEFILES`, `V$DIAG_INFO` + `adrci`, `DIAGPATH` listing…).
3. **Identify crash artefacts by their real names** — `*.crashdump.*.trc`, `cdump/`, `FODC_*`,
   `SQLDump*.mdmp`. Only Oracle puts anything in a directory called `cdump`; nobody else uses the word
   "core".
4. **Package anything attached to an open support message before purging.**
5. **Set or confirm the retention mechanism** so the cleanup is not a recurring manual job.
6. **Archive logs and transaction logs are not diagnostics** — never delete them for space; they go only
   after a verified backup. See [sap-backup-recovery](../../sap-backup-recovery/SKILL.md).
