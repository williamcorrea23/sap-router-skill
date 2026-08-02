# IBM Db2 for LUW (for SAP) — Operational Commands

`dbms_type = db6`. IBM Db2 for Linux, UNIX and Windows is the database under many NetWeaver / Business
Suite landscapes. SAP administers it through the native **Db2 CLP** (`db2…` commands) plus SAP's
**`brdb6brt`** and **DBA Cockpit**. Supported on **Linux, AIX and Windows** — genuine multi-OS.

> **Guardrail reminder:** `db2stop force` / `db2 force applications all` disconnect every session with no
> dry-run; stopping the instance takes the DB down. Identify → Preview → typed confirmation for PRD →
> one step → Verify. Prefer a clean `db2 quiesce`/`deactivate` over `force` where possible.

Verification legend: **[V]** verified against the live help.sap.com page during authoring · **[G]**
cited to the official guide/Note (confirm exact flags for your Db2 release + SAP DB6 tooling).

---

## 0. Layout, users and environment

| Item | Linux / AIX (UNIX) | Windows |
|------|--------------------|---------|
| Db2 **instance** owner | `db2<sid>` (= `DB2INSTANCE`) | `db2<sid>` (Db2 runs as a **Windows service**) |
| SAP admin user | `<sid>adm` | `<SID>adm` |
| SAP connect/schema user | `sap<sid>` / schema `SAP<SID>` | same |
| Instance home (`sqllib`) | `/db2/db2<sid>/sqllib` | `<Drive>:\db2\db2<sid>\sqllib` |
| Data path | `/db2/<SID>` | `<Drive>:\db2\<SID>` |
| Env to source | `. /db2/db2<sid>/sqllib/db2profile` | `db2cmd` opens a Db2-enabled shell |
| Instance TCP port | `SVCENAME` in `/etc/services` (`sapdb2<SID>`, e.g. 5912) | same, in the services file |

The **instance** (`db2<sid>`) hosts the **database** (`<SID>`). `db2stop` stops the instance (and thus
the DB); a database can also be **activated/deactivated** independently while the instance stays up.
DBA Cockpit uses a special admin connection **`+++DB6ADM`** — without valid admin credentials its
administrative actions are disabled. [G, D2]

**AIX vs Linux:** identical Db2 CLP and `db2profile` flow; only paths/packaging differ. Windows runs Db2
as a service and uses the `db2cmd` shell — see below.

---

## 1. Connect (Db2 CLP)

**Linux / AIX** — as `db2<sid>` (or `<sid>adm` with the profile sourced):
```bash
. /db2/db2<sid>/sqllib/db2profile          # source the instance environment first
db2 connect to <SID>                        # connect to the SAP database
db2 "SELECT ... FROM ..."                    # run SQL (quote statements for the shell)
db2level                                     # instance version/fixpack
```
**Windows** — from a `db2cmd` window:
```bat
db2 connect to <SID>
```

---

## 2. Start the database

Start **before** the SAP application instances.

### 2a. Native — all OS (run as `db2<sid>`)
```bash
db2start                                     # start the Db2 instance (database manager)
db2 activate database <SID>                  # optional: pre-activate (first SAP connect also activates)
```

### 2b. Windows service
```bat
net start "DB2 - DB2COPY1 - DB2<SID>-0"      :: exact service name varies — check Services.msc
:: db2start also works inside a db2cmd window
```

**Verify start (all OS):**
```bash
db2 list active databases                    # <SID> listed = up
ps -ef | grep db2sysc                        # UNIX: db2sysc engine process present
```

---

## 3. Stop the database  ⚠️ destructive — no dry-run

Stop the SAP application instances **first**, then Db2.

### 3a. Native — all OS (run as `db2<sid>`)
```bash
db2 force applications all                   # ⚠️ disconnect all sessions (do after SAP is down)
db2 deactivate database <SID>                # release the database (optional but clean)
db2stop                                       # stop the instance
db2stop force                                 # ⚠️ force-stop if a clean db2stop won't complete
```
If `db2stop` reports applications still connected, run `db2 force applications all` (and confirm SAP is
stopped), then retry. [G, D4]

### 3b. Windows service
```bat
net stop "DB2 - DB2COPY1 - DB2<SID>-0"        :: or db2stop from a db2cmd window
```

**Verify stop:** `db2 list active databases` errors / empty; `ps -ef | grep db2sysc` (UNIX) returns
nothing.

---

## 4. Basic backup (operational essentials)

Full backup/recovery is a separate skill (Phase 2). Native Db2 backup: [G, D3]
```bash
db2 backup database <SID> online to <path> compress    # online (needs LOGARCHMETH1 = archive logging)
db2 backup database <SID> to <path>                     # offline (no connections; deactivate first)
db2 list history backup all for <SID>                   # verify backup history
```
In SAP landscapes backups are usually scheduled from the **DBA Cockpit → DBA Planning Calendar**;
`brdb6brt` (SAP's Db2 admin tool) handles config/administration tasks from the command line. [G, D2]

---

## 5. Status & health checks

```bash
db2 list active databases                    # active DBs + connections
db2pd -db <SID> -                            # engine diagnostics snapshot
db2 get snapshot for database on <SID>       # DB-level snapshot
db2 get dbm cfg | grep -i svcename           # instance listener port
db2diag -H 1d                                 # last day of the diagnostic log (db2diag.log)
```

---

## 6. Boot-time autostart

| OS | Mechanism |
|----|-----------|
| **Linux / AIX** | Db2 instance autostart via `db2iauto -on db2<sid>`; SAP itself is brought up by the SAP start framework (`sapstartsrv`/`startdb` from `startsap`). [G] |
| **Windows** | The `DB2 - … - DB2<SID>` service is set to **Automatic** and starts on boot. [G] |

---

## Sources

- **[D1]** *Database Administration Guide for SAP on IBM Db2 for LUW* (BC-DB-DB6) — SAP Help Portal
  (CURRENT_VERSION PDF; canonical operations reference). Fetched during authoring (3.2 MB).
  https://help.sap.com/doc/7367f81b468e4480b3c550669b3534aa/CURRENT_VERSION/en-US/DB6_Admin_Guide.pdf
- **[D2]** *Database Administration Using the DBA Cockpit: IBM Db2 for LUW* — `+++DB6ADM` admin
  connection, DBA Planning Calendar, `brdb6brt`.
  https://help.sap.com/doc/8080298708d34d05a90b169e8442c39d/CURRENT_VERSION/en-US/dbacockpit_db6_en.pdf
- **[D3]** *Scheduling Database Backups* — SAP Help Portal, DB6.
  https://help.sap.com/docs/DB6/a212028be9ad489cbb8b6145effca9f7/45337d3d29a53446e10000000a155369.html
- **[D4]** `db2start` / `db2stop [force]` / `db2 force applications all` / `db2 backup` / `db2 activate` —
  IBM Db2 for LUW Command Reference (native, as used under SAP). [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the central SAP-on-Db2 notes
(component **BC-DB-DB6**) for your Db2 release, and the exact service name / `SVCENAME` for your install.
