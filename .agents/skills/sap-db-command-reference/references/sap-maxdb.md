# SAP MaxDB / liveCache — Operational Commands

`dbms_type = ada`. SAP MaxDB is the database under some NetWeaver / Content Server / Business Suite
installs; the same engine runs **SAP liveCache** (SCM/APO). The admin tool is **`dbmcli`** (Database
Manager CLI). Supported on **Linux, AIX and Windows** (also Solaris/HP-UX) — genuine multi-OS.

> **Guardrail reminder:** `db_offline` stops a live production DB (no dry-run); `db_stop` is a **hard**
> stop — only when `db_offline` won't complete. Identify → Preview → typed confirmation for PRD → one
> step → Verify. Do not put the DBM password in shared shell history (see §1).

Verification legend: **[V]** verified against the live SAP MaxDB doc during authoring · **[G]** cited to
the official guide/Note (confirm exact syntax for your MaxDB version).

---

## 0. Layout, users, states and environment

| Item | Linux / AIX (UNIX) | Windows |
|------|--------------------|---------|
| Software owner (OS) | `sdb` (group `sdba`) | install/service account |
| SAP admin user | `<sid>adm` | `<SID>adm` |
| DBM operator (DB-level) | e.g. `CONTROL` / `SUPERDBA` (the `-u <dbmuser>,<pwd>` pair) | same |
| Independent program path | `/sapdb/programs` (`bin/dbmcli`, `x_server`) | `<Drive>:\sapdb\programs` |
| Instance data | `/sapdb/<DBSID>/` | `<Drive>:\sapdb\<DBSID>` |
| Global listener (comm server) | **X_Server**, default port **7200** | X_Server runs as a **Windows service** |

**Operational states:** `OFFLINE` (stopped) → `ADMIN` (cold; admin tasks, offline backup, no user
access) → `ONLINE` (warm; normal operation). [V, M1] The **X_Server must be running** before the
database can go ONLINE.

**AIX vs Linux:** `dbmcli`/`x_server` are identical across UNIX; only paths differ. Windows runs the
DB and X_Server as **services** — see below.

---

## 1. Connect / DBM session (dbmcli)

**Linux / AIX / Windows** (`dbmcli` is identical; `.exe` on Windows):
```bash
dbmcli -d <DBSID> -u <dbmuser>,<password>        # opens an interactive DBM session
# then enter DBM commands, e.g.:  db_state   quit
# one-shot form (avoid real passwords in shared history):
dbmcli -d <DBSID> -U <userkey> db_state          # -U uses an XUSER key instead of -u user,pwd
```
Use the **XUSER** key store instead of `-u user,pwd` on shared shells:
```bash
xuser set -U <KEY> -d <DBSID> -n <host> -u <dbmuser>,<password>   # one-time
```
SQL (not DBM) is run with `sqlcli -d <DBSID> -u <sqluser>,<pwd>`.

---

## 2. Start the database (→ ONLINE / warm)

Start **before** the SAP application instances. Ensure X_Server is up first.

```bash
x_server start                                   # UNIX: start the global comm server (if not running)
dbmcli -d <DBSID> -u <dbmuser>,<password> db_online     # OFFLINE/ADMIN → ONLINE   [V, M1]
```
Admin (cold) state instead of full online (for offline backup / admin tasks):
```bash
dbmcli -d <DBSID> -u <dbmuser>,<password> db_admin      # → ADMIN   [G, M2]
```
**Windows:** start the **X_Server** and the MaxDB instance **services** (Services.msc), or run the same
`dbmcli … db_online`.

**Verify start:**
```bash
dbmcli -d <DBSID> -u <dbmuser>,<password> db_state      # expect: ONLINE   [V, M1]
x_server status
```

---

## 3. Stop the database  ⚠️ destructive — no dry-run

Stop the SAP application instances **first**, then MaxDB.

```bash
dbmcli -d <DBSID> -u <dbmuser>,<password> db_offline     # graceful stop → OFFLINE   [V, M1]
```
Hard stop — **only** if a normal `db_offline` hangs (⚠️ abrupt, longer restart):
```bash
dbmcli -d <DBSID> -u <dbmuser>,<password> db_stop        # HARD stop — last resort   [G, M2]
```
Stopping the X_Server (only if shutting the whole MaxDB software down; it may serve other instances):
```bash
x_server stop
```
**Windows:** stop the instance service (and X_Server service if required).

**Verify stop:** `db_state` → `OFFLINE`.

---

## 4. Basic backup (operational essentials)

Full backup/recovery is a separate skill (Phase 2). MaxDB backups run through `dbmcli` using a
**backup template**; the DB must be **ONLINE** (online backup) or **ADMIN** (offline backup): [G, M3]
```bash
dbmcli -d <DBSID> -u <dbmuser>,<password>
  backup_template_create DAILYDATA to FILE /backup/DAT CONTENT DATA
  backup_start DAILYDATA                          # run the data backup
  backup_start LOGTEMPLATE AUTO                    # automatic log backup (if configured)
```
In SAP landscapes backups are usually scheduled from **DBA Cockpit / DB13**; use ad-hoc `backup_start`
for pre-change safety copies. [G]

---

## 5. Status & health checks

```bash
dbmcli -d <DBSID> -u <dbmuser>,<password> db_state        # OFFLINE / ADMIN / ONLINE   [V, M1]
dbmcli db_enum                                            # list instances on this host + their states
dbmcli -d <DBSID> -u <dbmuser>,<password> dbm_version     # version
x_server status                                          # comm server up?
```

---

## 6. SAP liveCache (SCM/APO)

liveCache uses the **same MaxDB engine and `dbmcli`**, with the same OFFLINE/ADMIN/ONLINE states.
Operationally it is normally managed from transaction **LC10** in the SCM system, but the same
`dbmcli … db_online` / `db_offline` apply at the OS level; liveCache going ONLINE also loads its data
into memory (warm-up). Treat start/stop with the same guardrails as above. [G, M4]

---

## 7. Boot-time autostart

| OS | Mechanism |
|----|-----------|
| **Linux / AIX** | X_Server auto-start + `Autostart`/`AutoRestart` DB parameter; SAP itself is brought up by the SAP start framework (`sapstartsrv`/`startdb` from `startsap`). [G] |
| **Windows** | The MaxDB instance and **X_Server** services are set to **Automatic** and start on boot. [G] |

---

## Sources

- **[M1]** *Starting and Stopping a Database* — SAP MaxDB documentation (7.7). **[V]** `dbmcli -u
  <DBM>,<pwd> -d <DB> db_online | db_offline | db_state`; states OFFLINE / ADMIN / ONLINE.
  https://maxdb.sap.com/doc/7_7/44/eabea8f85b2950e10000000a11466f/content.htm
- **[M2]** DBM command reference (`db_admin`, `db_stop` hard stop; state prerequisites) — SAP MaxDB
  Database Administration. [G]
- **[M3]** *HowTo — SAP MaxDB Backup with Database Manager CLI* (`backup_template_create`,
  `backup_start`) — SAP Help Portal. https://help.sap.com/docs/SUPPORT_CONTENT/maxdb/3362174112.html
- **[M4]** `dbmcli`, `x_server`, XUSER, OS users (`sdb`, DBM operator) and liveCache (LC10 + same engine)
  — SAP MaxDB / liveCache documentation. [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the central SAP MaxDB notes
(component **BC-DB-SDB**) for your version, and the exact DBM user name your install uses (`CONTROL`
vs `SUPERDBA`) plus the X_Server port if changed from 7200.
