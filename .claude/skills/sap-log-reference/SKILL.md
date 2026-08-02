---
name: sap-log-reference
description: >-
  Find and read the right log/trace for any SAP component or database. Maps where each layer writes —
  SAP instance/work-directory traces (dev_disp, dev_w*, dev_ms, dev_rd, dev_icm), ABAP logs (SM21, ST22,
  SM50, SLG1), standalone components (Web Dispatcher, SAProuter, Cloud Connector, Host Agent, IGS), and
  each database's own logs (HANA trace dir, Oracle alert log, Db2 db2diag, ASE errorlog, MaxDB KnlMsg,
  SQL Server ERRORLOG) — and how to read them from the OS shell or remotely via SAPControl. Use for
  "where is the log for X", "read the trace", "hunt down why <symptom>", "which log shows <error>". Cited
  to help.sap.com.
---

# SAP Log & Trace Reference (hunting + reading)

Different layer → different location. This is the **locator**: symptom → which log → where it lives →
how to read it. It complements [sap-health-triage](../sap-health-triage/SKILL.md) (which extracts logs via
SAPControl) and [sap-housekeeping](../sap-housekeeping/SKILL.md) (which cleans them up).

> **Guardrail note:** reading is non-destructive — but confirm the **SID/host** before reading another
> system's logs, and remember many SAPControl read methods are **protected** (`service/protectedwebmethods`
> — see health-triage §7). Raising trace **levels** (§ references) *does* change system behaviour/space —
> lower them again after diagnosis.

---

## 1. How to read a log

**OS shell (UNIX — Linux/AIX):**
```bash
tail -f <file>                 # follow live
less +G <file>                 # open at the end
grep -niE "ERROR|ORA-|\*\*\* ERROR|abort" <file>   # hunt for errors
```
**OS shell (Windows):**
```powershell
Get-Content <file> -Tail 100 -Wait          # follow live
Select-String -Path <file> -Pattern "ERROR|abort"
```
**Remotely / no shell — via SAPControl** (cross-ref [health-triage](../sap-health-triage/SKILL.md) §2):
```bash
sapcontrol -nr <nr> -function ListDeveloperTraces          # list the instance's dev_* files
sapcontrol -nr <nr> -function ReadDeveloperTrace dev_w0 0  # read one (size 0 = whole file)
sapcontrol -nr <nr> -function ReadLogFile <path> ''        # any instance log file
sapcontrol -nr <nr> -function ABAPReadSyslog               # SM21 system log
```

---

## 2. The SAP instance / application log map

**Work directory** — `/usr/sap/<SID>/<INST><nr>/work/` (Windows `…\work\`). The per-process traces:

| File | Component | Read when |
|------|-----------|-----------|
| `dev_disp` | **Dispatcher** | instance won't start; overall instance issues |
| `dev_w0`…`dev_w<n>` | **Work processes** | short dumps, DB connect errors, WP hangs |
| `dev_ms` | **Message Server** (ASCS/SCS) | logon/load-balancing, instance registration |
| `dev_rd` | **Gateway** | RFC/registered-program failures |
| `dev_icm` | **ICM** (Internet Communication Manager) | HTTP/HTTPS, Fiori, web errors |
| `dev_rfc*`, `dev_rfc.trc` | **RFC** client/server calls | RFC connection failures |
| `dev_enq*`, `enserver`/`enq*` logs | **Enqueue Server** | lock / enqueue problems |
| `dev_sapstartsrv`, `sapstartsrv.log` | **sapstartsrv** control service | SAPControl can't reach the instance |
| `stderr0/1/2…`, `available.log`, `sapstart.log` | start-service | startup failures |

**ABAP application logs (via SAP GUI / SAPControl):**

| Where | Content | Shell equivalent |
|-------|---------|-----------------|
| **SM21** | system log (syslog) | `sapcontrol … ABAPReadSyslog` |
| **ST22** | ABAP short dumps (runtime errors) | (dump text) |
| **SM50 / SM66** | work-process overview + traces | `sapcontrol … ABAPGetWPTable` |
| **SLG1** | application log (BAL) | — |
| **ST11** | error-log files / developer traces | the `dev_*` files above |
| **SM13** | update-request errors | `dev_w*` (update WP) |
| **SMGW** | gateway monitor + logging | `dev_rd` |
| **SM19 / SM20 / RSAU** | security audit log (`*.AUD`) | `…/<INST>/log/*.AUD` |

---

## 3. Symptom → which log (hunting)

| Symptom | Look here first |
|---------|-----------------|
| Instance won't start | `dev_disp` → `stderr*` → `sapstart.log`; then `sappfpar check` (health-triage) |
| "Database not available" / connect fails | `dev_w0` (WP that connects) **+ the DB's own log** (§5) |
| RFC / registered program fails | `dev_rd` (gateway) + `dev_rfc*`; SMGW |
| HTTP / Fiori / web error | `dev_icm`; ICM trace (raise via `icm/trace_level`) |
| Logon load balancing / message server | `dev_ms`; SMMS |
| Enqueue / lock issues | `dev_enq*` / `enserver`; SM12 |
| Random short dumps | ST22 + the referenced `dev_w<n>` |
| Slow / performance | ST03, ST04 (DB), the DB's expensive-statement log (§5) |
| Web Dispatcher / SAProuter / Cloud Connector | that component's own log (§4) |

---

## 4. Standalone components

Each ships its own trace, separate from any SAP instance — full map in
[references/app-and-component-logs.md](references/app-and-component-logs.md):

| Component | Primary log | Notes |
|-----------|-------------|-------|
| **SAP Web Dispatcher** | `dev_webdisp`, `dev_webdisp_log` in the Web Disp dir | ICM-based; raise via `icm/trace_level` [G3] |
| **SAProuter** | `-T <tracefile>` (level-2 trace) / `-L <logfile>` | enable per SAP KBA 3570238 [G5] |
| **SAP Cloud Connector** | `ljs_trace.log` (+ `scc_*`), rotates 20×50 MB | in the SCC install `log/` dir [G4] |
| **SAP Host Agent** | `dev_saphostexec`, host-agent logs under `/usr/sap/hostctrl/work` | control-layer issues |
| **IGS** (graphics) | `dev_igs*` | chart/graphics rendering |

---

## 5. Database logs (different per DB)

DB engines log **outside** the SAP work directory, each in its own place and format. Full per-DB map +
readers in [references/db-logs.md](references/db-logs.md):

| DB (`dbms_type`) | Primary log | Read with |
|------------------|-------------|-----------|
| **HANA** (`hdb`) | `/usr/sap/<SID>/HDB<nr>/<host>/trace/` — `indexserver_*.trc`, `nameserver_*.trc`, `*_alert_*.trc` | pager / HANA cockpit / `M_MERGED_TRACES` [G2] |
| **Oracle** (`ora`) | ADR `…/diag/rdbms/<db>/<SID>/trace/alert_<SID>.log`; `listener.log` | `adrci` / pager |
| **ASE** (`syb`) | `$SYBASE/$SYBASE_ASE/install/<SERVER>.log` (errorlog); `<SERVER>_BS.log` (Backup Server) | pager |
| **Db2** (`db6`) | `db2diag.log` in `DIAGPATH` (`db2 get dbm cfg`) | `db2diag -H 1d` |
| **MaxDB** (`ada`) | `KnlMsg` / `knldiag`, `dbm.prt` in the run directory | Database Studio / pager |
| **SQL Server** (`mss`) | `…\MSSQL\Log\ERRORLOG`; SQL Agent `SQLAGENT.OUT`; Windows Event Log | SSMS Log Viewer / `xp_readerrorlog` |

Cross-ref [sap-db-command-reference](../sap-db-command-reference/SKILL.md) for how to start/stop/connect
each of these.

## Cross-references

- **Extract logs via SAPControl (protected methods, dev-trace file map):**
  [sap-health-triage](../sap-health-triage/SKILL.md).
- **Clean up / rotate these logs:** [sap-housekeeping](../sap-housekeeping/SKILL.md).
- **DB start/stop/connect:** [sap-db-command-reference](../sap-db-command-reference/SKILL.md).

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

- **[G1]** *Log and Traces — Transactions* — SAP Support Content (ABAP transaction → log map).
  https://help.sap.com/docs/SUPPORT_CONTENT/basis/3354611259.html
- **[G2]** SAP HANA trace/log directory `/usr/sap/<SID>/HDB<nr>/<host>/trace/` (indexserver/nameserver/alert;
  MDC SYSTEMDB + tenant subdirs) — SAP HANA Administration Guide / Troubleshooting & Performance Analysis.
- **[G3]** *Traces and Trace Configuration for (Internal) Web Dispatcher* — SAP Help Portal.
  https://help.sap.com/docs/r/e8d0ddfb84094942a9f90288cd6c05d3/2.11.0.0/en-US/79ad6205a5a948dfa2e474cabdef53b6.html
- **[G4]** SAP Cloud Connector logging (`ljs_trace.log`, rotation) — SAP BTP Connectivity / Cloud Connector
  documentation (help.sap.com).
- **[G5]** **SAP KBA 3570238** — *How to collect SAPRouter level 2 trace and enable logging*.
  https://me.sap.com/notes/3570238

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): KBA 3570238 for the exact SAProuter
trace flags, and each DB's admin/troubleshooting guide for the current log paths on your release.
