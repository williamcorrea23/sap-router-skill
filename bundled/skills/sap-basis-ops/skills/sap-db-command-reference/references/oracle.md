# Oracle Database (for SAP) — Operational Commands

`dbms_type = ora`. Oracle is the database under classic ECC / Business Suite and many older
NetWeaver landscapes. SAP administers Oracle through **BR\*Tools** on top of native `sqlplus`.
Supported on **Linux, Windows and AIX** (also Solaris/HP-UX historically) — genuine multi-OS.

> **Guardrail reminder:** `SHUTDOWN IMMEDIATE` / `brspace -f dbshut` stop a live production DB with no
> dry-run; `SHUTDOWN ABORT` is a crash-stop (instance recovery on next start). Identify → Preview →
> typed confirmation for PRD → one step → Verify. Prefer `SHUTDOWN IMMEDIATE` over `ABORT`.

Verification legend: **[V]** verified against the live help.sap.com page during authoring · **[G]**
cited to the official guide/Note (confirm exact flags for your Oracle release + BR\*Tools patch).

---

## 0. Layout, users and environment

| Item | Linux / AIX (UNIX) | Windows |
|------|--------------------|---------|
| Oracle software owner | `ora<sid>` | `<SID>adm` (+ Oracle services run as `LocalSystem`/service acct) |
| SAP admin user | `<sid>adm` | `<SID>adm` |
| `ORACLE_HOME` | e.g. `/oracle/<SID>/<version>` | e.g. `<Drive>:\oracle\<SID>\<version>` |
| `ORACLE_SID` | database SID (usually **upper-case** SID) | same |
| `SAPDATA_HOME` | `/oracle/<SID>` | `<Drive>:\oracle\<SID>` |
| BR\*Tools / sqlplus | `$ORACLE_HOME/bin` (`brtools`, `sqlplus`, `lsnrctl`) [G, O2] | `%ORACLE_HOME%\bin` (`brtools.exe`, `sqlplus.exe`) |
| DB config | `init<ORACLE_SID>.ora` / `spfile`, and SAP `init<ORACLE_SID>.sap` [G, O5] | same names under `%ORACLE_HOME%\database` |
| Listener | default port **1521**, controlled by `lsnrctl` | Windows service `OracleOra…TNSListener` |

**BR\*Tools package** = `brtools` (menu launcher) + `brbackup`, `brarchive`, `brrestore`,
`brrecover`, `brspace`, `brconnect`. Run as `<sid>adm` or `ora<sid>` (both may `CONNECT / AS SYSDBA`).
[G, O2] Log dirs under `$SAPDATA_HOME`: `sapbackup` (brbackup/brrestore/brrecover), `saparch`
(brarchive), `sapreorg` (brspace), `sapcheck` (brconnect). [G, O2]

**AIX vs Linux:** the Oracle CLI (`sqlplus`, `brtools`, `lsnrctl`) is identical on both UNIX platforms;
only paths/packaging differ. Windows differs materially (services + `oradim`) — see below.

---

## 1. Connect (sqlplus / brconnect)

**Linux / AIX** — as `ora<sid>` (or `<sid>adm` with the Oracle env sourced):
```bash
sqlplus / as sysdba                       # OS-authenticated SYSDBA (no password on the command line)
brconnect -u / -c -f check                # SAP DBA connect + standard checks
```
**Windows:**
```bat
sqlplus.exe / as sysdba
```
`/ as sysdba` uses OS authentication (member of the DBA/`ORA_DBA` group) — **avoid** typing
`sys/<password>` on shared shells. [G, O4]

Quick status once connected:
```sql
SELECT status, database_status, instance_name FROM v$instance;
SELECT name, open_mode FROM v$database;
```

---

## 2. Start the database

Start **before** the SAP application instances. Oracle starts in phases: **NOMOUNT → MOUNT → OPEN**.

### 2a. Native (sqlplus) — all OS
```sql
sqlplus / as sysdba
STARTUP;                 -- nomount → mount → open in one step
-- staged (only if you need it):  STARTUP NOMOUNT;  ALTER DATABASE MOUNT;  ALTER DATABASE OPEN;
```
Start the listener too (SAP work processes connect through it):
```bash
lsnrctl start            # UNIX; Windows: start the OracleOra…TNSListener service
```

### 2b. BR\*Tools — all OS
```bash
brspace -f dbstart       # menu path: Instance Management → Start up database  [G, O1]
```

### 2c. Windows service (instance runs as a service)
```bat
net start OracleService<SID>              :: starts the DB instance service
net start OracleOra<...>TNSListener       :: starts the listener service
:: oradim -startup -sid <SID>             :: alternative via the Oracle instance manager
```

**Verify start (all OS):**
```bash
lsnrctl status
ps -ef | grep "ora_pmon_<ORACLE_SID>"     # UNIX: pmon present = instance up
```
```sql
SELECT status FROM v$instance;            -- OPEN
```

---

## 3. Stop the database  ⚠️ destructive — no dry-run

Stop the SAP application instances **first**, then Oracle.

### 3a. Native (sqlplus) — all OS
```sql
sqlplus / as sysdba
SHUTDOWN IMMEDIATE;      -- graceful: rolls back open txns, disconnects, closes cleanly (preferred)
-- SHUTDOWN;            -- "normal": waits for all sessions to disconnect (can hang)
-- SHUTDOWN ABORT;      -- ⚠️ crash-stop: instance recovery required on next start; last resort
```
Stop the listener too when taking the whole DB layer down (the DB can also be stopped with the listener
left running — it just refuses new connections):
```bash
lsnrctl stop            # UNIX; Windows: stop the OracleOra…TNSListener service
```

### 3b. BR\*Tools — all OS  **[V, O1]**
```bash
brspace -f dbshut                         # menu path: Instance Management → Shut down database
brspace -f dbshut -f                      # force instant shutdown (abort-style)  ⚠️
brspace -f dbshut -i all_inst             # RAC: stop all instances
```
Verified options [V, O1]: `-i <instance>`, `-m <mode>`, `-f` (force), `-u <user>`, `-p <profile>`.

### 3c. Windows service
```bat
net stop OracleService<SID>               :: stops the instance (respects the service shutdown mode)
```

**Verify stop:** `lsnrctl status` shows no instance; `ps -ef | grep pmon` (UNIX) returns nothing;
`v$instance` unreachable.

---

## 4. Basic backup (operational essentials)

Full backup/recovery is a separate skill (Phase 2). SAP-native Oracle backups use BR\*Tools: [G, O3]
```bash
brbackup  -u / -c -t online -m all -p init<ORACLE_SID>.sap   # online full data backup
brarchive -u / -c -sd                                        # back up + delete archived redo logs
brbackup -u / -c -t offline ...                              # offline backup (DB must be down/mounted)
```
Verify: check the summary log under `$SAPDATA_HOME/sapbackup` (brbackup) / `saparch` (brarchive), or
`brconnect -f check`. In SAP landscapes these run scheduled from **DBA Cockpit (DB13)**; use ad-hoc
`brbackup` for pre-change safety copies. Ensure the DB is in **ARCHIVELOG** mode for online backups. [G]

---

## 5. Status & health checks

```bash
lsnrctl status                                  # listener + registered instances
brconnect -u / -c -f check                      # SAP standard DB health checks
ps -ef | grep "ora_pmon_<ORACLE_SID>"           # UNIX
```
```sql
SELECT status, logins, database_status FROM v$instance;
SELECT log_mode FROM v$database;                -- ARCHIVELOG?
SELECT tablespace_name, status FROM dba_tablespaces;
```

---

## 6. Boot-time autostart

| OS | Mechanism |
|----|-----------|
| **Linux / AIX** | SAP start framework (`sapstartsrv` / `startdb` called by `startsap`); native Oracle `/etc/oratab` `Y` flag + `dbstart`/`dbshut` also exist but SAP landscapes drive it through the SAP layer. [G] |
| **Windows** | `OracleService<SID>` and the listener service set to **Automatic**; the SAP DB service starts on boot. [G] |

---

## Sources

- **[O1]** *Shutting Down the Database with BR\*Tools* — SAP Database Administration: Oracle (BC-DB-ORA),
  SAP NetWeaver 7.4 Library. **[V]** `brspace -f dbshut` (+ `-i/-m/-f/-u/-p`, RAC `-i all_inst`), menu
  *Instance Management → Shut down database*; start is the symmetric `brspace -f dbstart`.
  https://help.sap.com/doc/saphelp_nw74/7.4.16/en-us/47/136ded2c1721bfe10000000a114a6b/content.htm
- **[O2]** *BR\*Tools for Oracle DBA* — same library. BR\*Tools composition, `ora<sid>`/`<sid>adm` users,
  `CONNECT / AS SYSDBA`, `init<ORACLE_SID>.sap`, log directories under `$SAPDATA_HOME`.
  https://help.sap.com/doc/saphelp_nw74/7.4.16/en-US/46/e42438f63966c6e10000000a1553f7/content.htm
- **[O3]** *Common Features of BRBACKUP and BRARCHIVE* — SAP NetWeaver Database Administration for Oracle.
  https://help.sap.com/docs/SAP_NETWEAVER_DBOS/3ef1b95cacbf4f77a066797285371bb9/471daf3d8ffa2c7ae10000000a114a6b.html
- **[O4]** `STARTUP` / `SHUTDOWN [IMMEDIATE|ABORT]`, `sqlplus / as sysdba` — Oracle Database
  Administrator's Guide (native), as used under SAP. [G]
- **[O5]** Environment (`ORACLE_HOME`, `ORACLE_SID`, `SAPDATA_HOME`) and config (`init<ORACLE_SID>.sap`) —
  SAP Database Administration: Oracle. [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the central SAP-on-Oracle notes
(component **BC-DB-ORA**) for your Oracle release (e.g. 19c) and the matching BR\*Tools patch level, plus
the current *SAP Database Guide: Oracle* for exact `brbackup`/`brspace` options.
