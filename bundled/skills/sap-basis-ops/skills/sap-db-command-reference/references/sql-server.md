# Microsoft SQL Server (for SAP) — Operational Commands

`dbms_type = mss`. Microsoft SQL Server is the database under NetWeaver / Business Suite landscapes on
Windows. Managed via **SQL Server Configuration Manager**, **SSMS**, `net start/stop`, and `sqlcmd`.

> **Platform reality (read first):** **SAP on SQL Server is Windows-only.** SQL Server 2017+ can run on
> Linux, but SAP does **not** support SAP-on-SQL-Server-on-Linux, and SQL Server has never run on AIX.
> So there is **no Linux/AIX variant** for this database under SAP — everything below is Windows. (This
> is the mirror of SAP HANA being Linux-only.) [G, S2]

> **Guardrail reminder:** stopping the SQL Server service takes the DB down with no dry-run. Identify →
> Preview → typed confirmation for PRD → one step → Verify. **Never use "Pause"** on the server — it
> blocks new connections and causes SAP errors (see §2). [V, S1]

Verification legend: **[V]** verified against the live help.sap.com page during authoring · **[G]**
cited to the official guide/Note.

---

## 0. Layout, users, services and environment (Windows)

| Item | Value |
|------|-------|
| SAP admin / service users | `<SID>adm`, `SAPService<SID>` |
| DB engine service | **default instance:** `MSSQLSERVER` · **named:** `MSSQL$<INSTANCE>` (process `sqlservr.exe`) [V, S1] |
| Agent service (jobs/backups) | **default:** `SQLSERVERAGENT` · **named:** `SQLAgent$<INSTANCE>` (process `sqlagent.exe`) [V, S1] |
| SAP database | the `<SID>` database inside the instance |
| TCP port | default instance **1433**; named instances use dynamic ports via **SQL Browser** (UDP 1434) |
| Tools | `sqlcmd.exe`, SQL Server Configuration Manager, SQL Server Management Studio (SSMS) |

The **SQL Server Agent must be running** for scheduled SAP DBA tasks/backups. [V, S1]

---

## 1. Connect (sqlcmd)

```bat
sqlcmd -S <host>\<INSTANCE> -E                       :: -E = trusted (Windows) auth — no password on the line
sqlcmd -S <host> -E -Q "SELECT @@VERSION"            :: one-shot query
```
Use **`-E` (Windows authentication)** rather than `-U <user> -P <password>` on shared shells. SSMS is
the GUI equivalent.

---

## 2. Start the database

Start **before** the SAP application instances. Preferred: **SQL Server Configuration Manager** or SSMS
(right-click the instance → Start). [V, S1] Command line:

```bat
:: default instance:
net start MSSQLSERVER
net start SQLSERVERAGENT
:: named instance <INSTANCE>:
net start "MSSQL$<INSTANCE>"
net start "SQLAgent$<INSTANCE>"
```

> Note: **you cannot start a stopped instance with `sqlcmd`** — it needs a running engine to connect to.
> Use the service (`net start` / Configuration Manager). For recovery/maintenance, the engine can be
> launched from the command line via `sqlservr.exe` (e.g. `sqlservr.exe -m` for single-user mode) from
> the instance `Binn` directory. [G, S4]

> ⚠️ **Never use "Pause."** It prevents new connections and causes SAP errors — use Start/Stop only. [V, S1]

**Verify start:**
```bat
sc query MSSQLSERVER                                 :: STATE : 4 RUNNING
sqlcmd -S <host>\<INSTANCE> -E -Q "SELECT name, state_desc FROM sys.databases"
```

---

## 3. Stop the database  ⚠️ destructive — no dry-run

Stop the SAP application instances **first**, then SQL Server. Stopping the engine also stops the Agent.

```bat
:: default instance:
net stop MSSQLSERVER
:: named instance:
net stop "MSSQL$<INSTANCE>"
```
Or SQL Server Configuration Manager / SSMS → right-click the instance → **Stop** (a controlled
checkpoint + shutdown). [V, S1]

**Native T-SQL stop via `sqlcmd`** (the equivalent of `isql … shutdown` / `sqlplus … shutdown` on the
other databases; requires the `sysadmin` or `serveradmin` role): [G, S4]
```bat
sqlcmd -S <host>\<INSTANCE> -E -Q "SHUTDOWN"                :: checkpoints each DB, then stops the engine
sqlcmd -S <host>\<INSTANCE> -E -Q "SHUTDOWN WITH NOWAIT"    :: ⚠️ immediate — no checkpoint; recovery on next start
```
Prefer plain `SHUTDOWN` (or `net stop`) over `WITH NOWAIT`. Note the engine also stops the Agent.

**Verify stop:** `sc query MSSQLSERVER` → `STATE : 1 STOPPED`.

---

## 4. Basic backup (operational essentials)

Full backup/recovery is a separate skill (Phase 2). Native T-SQL via `sqlcmd`/SSMS: [G, S3]
```sql
BACKUP DATABASE [<SID>] TO DISK = 'X:\backup\<SID>_full.bak' WITH COMPRESSION, CHECKSUM, INIT;
BACKUP LOG      [<SID>] TO DISK = 'X:\backup\<SID>_log.trn';        -- requires FULL recovery model
RESTORE VERIFYONLY FROM DISK = 'X:\backup\<SID>_full.bak';         -- verify
```
In SAP landscapes backups are usually scheduled from **DBA Cockpit / DB13** (or SSMS maintenance plans);
use ad-hoc `BACKUP DATABASE` for pre-change safety copies. Log backups + point-in-time recovery need the
**FULL** recovery model. [G, S3]

---

## 5. Status & health checks

```bat
sc query MSSQLSERVER                                 :: service state
net start                                            :: lists running services (find SQL Server / Agent)
```
```sql
SELECT @@VERSION;
SELECT name, state_desc, recovery_model_desc FROM sys.databases;      -- DB online? recovery model?
SELECT session_id, status, login_name FROM sys.dm_exec_sessions;      -- active sessions
```

---

## 6. Boot-time autostart

Set the **SQL Server** and **SQL Server Agent** services to **Automatic** in SQL Server Configuration
Manager / Windows Services so they start on boot; the SAP layer is brought up by the SAP start framework
(`sapstartsrv`) via the SAP MMC / `sapcontrol`. [V/G, S1]

---

## Sources

- **[S1]** *Starting and Stopping the SQL Server* — SAP Database Administration in CCMS (SAP NetWeaver
  7.31). **[V]** Configuration Manager/SSMS; two services **SQL Server (MSSQLServer)** + **SQL Server
  Agent**; processes `sqlservr.exe` / `sqlagent.exe`; *"Never use Pause for a server … may cause SAP
  errors."*
  https://help.sap.com/doc/saphelp_nw73ehp1/7.31.19/en-US/4d/0abf226dc25c4be10000000a42189e/content.htm
- **[S2]** *Database Administration for Microsoft SQL Server* — SAP Help Portal (BC-DB-MSS). Windows
  platform for SAP.
  https://help.sap.com/doc/saphelp_nw73ehp1/7.31.19/en-US/48/bb2361cf555295e10000000a42189b/content.htm
- **[S3]** *Database Backup* / *Backup Configuration* — SAP NetWeaver Database Administration for MS SQL
  Server. https://help.sap.com/docs/SAP_NETWEAVER_DBOS/a1db6ee881e749c586d634862df93992/4d0904aebd79606be10000000a42189e.html
- **[S4]** `net start`/`net stop`, `sqlcmd`, `BACKUP DATABASE`/`BACKUP LOG` — Microsoft SQL Server
  documentation (native, as used under SAP). [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the central SAP-on-SQL-Server notes
(component **BC-DB-MSS**) for your SQL Server version, and your instance name (default `MSSQLSERVER` vs a
named `MSSQL$<INSTANCE>`).
