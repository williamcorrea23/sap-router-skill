# Database logs — location & reader per `dbms_type`

Reference detail for [../SKILL.md](../SKILL.md). Each DB logs in its own place and format, **outside** the
SAP work directory. Start/stop/connect for each DB is in
[../../sap-db-command-reference/SKILL.md](../../sap-db-command-reference/SKILL.md).

## SAP HANA (`hdb`) — Linux only

- **Trace directory:** `/usr/sap/<SID>/HDB<nr>/<host>/trace/`. MDC: `SYSTEMDB` and each tenant `DB_<SID>`
  has its own subdirectory. [G2]
- Key files: `indexserver_<host>.<pid>.<nnn>.trc`, `nameserver_*.trc`, `xsengine_*.trc`,
  `compileserver_*.trc`, `preprocessor_*.trc`, `daemon_*.trc`; **alerts** in `nameserver_alert_<host>.trc`;
  backups in `backup.log` / `backint_*.log`.
- **Read:** pager on the `.trc` files, or in SQL — `SELECT * FROM M_MERGED_TRACES`; alerts via
  `SELECT * FROM _SYS_STATISTICS.STATISTICS_ALERTS_BASE`; expensive SQL via `M_EXPENSIVE_STATEMENTS`.
  HANA cockpit → "Trace Files".
- **Trace config:** per-service ini (`indexserver.ini` etc.) `[trace]` section; or HANA cockpit.

## Oracle (`ora`) — Linux / Windows / AIX

- **Alert log (ADR):** `<ORACLE_BASE>/diag/rdbms/<db_unique_name>/<ORACLE_SID>/trace/alert_<ORACLE_SID>.log`
  (plus `.trc` trace files in the same `trace/` dir). Listener: `…/diag/tnslsnr/<host>/listener/trace/listener.log`.
- **Read:** pager, or `adrci` (`adrci> show alert`). BR\*Tools logs live under `$SAPDATA_HOME`:
  `sapbackup/` (brbackup/brrestore/brrecover), `saparch/` (brarchive), `sapreorg/` (brspace),
  `sapcheck/` (brconnect).

## SAP ASE / Sybase (`syb`) — Linux / Windows / AIX

- **Server errorlog:** `$SYBASE/$SYBASE_ASE/install/<SERVER>.log` (the dataserver errorlog; `<SERVER>`
  is usually `<SID>`). **Backup Server:** `<SERVER>_BS.log`.
- **Read:** pager; inside `isql`: `sp_who`, `sp_monitorconfig`, error 6xx/9xx patterns. Windows: same
  files under the ASE install dir.

## IBM Db2 for LUW (`db6`) — Linux / Windows / AIX

- **Diagnostic log:** `db2diag.log` in the **`DIAGPATH`** (`db2 get dbm cfg | grep -i diagpath`; default
  `/db2/<SID>/db2dump/` or `<instance home>/sqllib/db2dump/`). **Notification log:** `<instance>.nfy`.
- **Read:** `db2diag -H 1d` (last day), `db2diag -l error` (errors only); `db2pd -db <SID> -` for engine
  state. Windows: same `db2diag.log` under the instance diag path; also Windows Event Log.

## SAP MaxDB / liveCache (`ada`) — Linux / Windows / AIX

- **Run directory:** `/sapdb/data/wrk/<DBSID>/` — **`KnlMsg`** (kernel message file; older `knldiag`),
  **`dbm.prt`** (DBM server protocol), `backup.hist`. (Windows: `<sapdb>\data\wrk\<DBSID>\`.)
- **Read:** pager, or **Database Studio** / DBM (`dbmcli … show ...`), `dbmcli … dbm_getpath`.

## Microsoft SQL Server (`mss`) — Windows only

- **SQL Server error log:** `<instance dir>\MSSQL\Log\ERRORLOG` (+ `ERRORLOG.1 … .n`). **SQL Agent:**
  `SQLAGENT.OUT`. Plus the **Windows Event Log** (Application).
- **Read:** SSMS → Management → SQL Server Logs (Log File Viewer); or `EXEC xp_readerrorlog;` /
  `sqlcmd -Q "EXEC xp_readerrorlog"`. Cycle the log with `EXEC sp_cycle_errorlog;`.

## Sources

- **[G2]** SAP HANA trace/log directory + `M_MERGED_TRACES` — SAP HANA Administration Guide /
  Troubleshooting and Performance Analysis (help.sap.com).
- Oracle ADR alert log, `adrci`, BR\*Tools log dirs — SAP Database Administration: Oracle + Oracle DBA
  guide (see sap-db-command-reference/oracle.md §Sources).
- ASE errorlog, Db2 `db2diag.log`, MaxDB `KnlMsg`, SQL Server `ERRORLOG` — the respective SAP DB
  Administration guides (see the matching file under sap-db-command-reference/references).
