# SAP ASE (Adaptive Server Enterprise / Sybase ASE) — Operational Commands

`dbms_type = syb`. SAP ASE is the database under SAP Business Suite / S/4-on-ASE landscapes. This
file covers **start, stop, connect, status and basic backup** at the OS/DB layer, for **Linux,
Windows and AIX**.

> **Guardrail reminder:** `shutdown` and `shutdown with nowait` have **no dry-run**. Always Identify →
> Preview → confirm (typed confirmation for PRD) → Execute one step → Verify. Only a System
> Administrator login (`sapsa`/`sa`) can shut ASE down. [S4]

Verification legend: **[V]** = verified against the live help.sap.com page during authoring · **[G]** =
cited to the official guide (confirm exact flags for your patch level).

---

## 0. Layout, users and environment

| Item | Linux / AIX (UNIX) | Windows |
|------|--------------------|---------|
| SAP admin OS user | `<sid>adm` | `<SID>adm` |
| ASE (database) OS user | `syb<sid>` | `syb<sid>` / service account `SAPService<SID>` |
| `$SYBASE` home (typical) | `/sybase/<SID>` | `<Drive>:\sybase\<SID>` |
| Env script to source | `. $SYBASE/SYBASE.sh` (bash/ksh) or `source $SYBASE/SYBASE.csh` (csh) | `%SYBASE%\SYBASE.bat` (set by installer; also in registry) |
| Client tools dir | `$SYBASE/$SYBASE_OCS/bin` [V, S2] | `%SYBASE%\%SYBASE_OCS%\bin` (`isql.exe`) [V, S2] |
| Server install dir | `$SYBASE/$SYBASE_ASE/install` [G, S3] | `%SYBASE%\%SYBASE_ASE%\install` |
| `interfaces` file | `$SYBASE/interfaces` (isql looks here if `-I` omitted) [V, S2] | `%SYBASE%\ini\sql.ini` |
| ASE error log | `$SYBASE/$SYBASE_ASE/install/<SERVER>.log` [G] | `%SYBASE%\%SYBASE_ASE%\install\<SERVER>.log` |

**SAP-specific logins** (default `sa` is normally locked in SAP installs): `sapsa` (System
Administrator) and `sapsso` (Security Officer). [G]

Server names in an SAP install: the dataserver is usually `<SID>` and the Backup Server `<SID>_BS`.

**AIX vs Linux:** the DB commands are identical (both UNIX). Differences are only the default shell
(AIX = `ksh`) and boot autostart wiring (see §5). Source `SYBASE.sh` on both.

---

## 1. Connect (isql)

`isql` is the interactive SQL client. Location and full syntax verified against the SAP ASE Utility
Guide. [V, S2]

**Linux / AIX:**
```bash
# as syb<sid> (or <sid>adm with SYBASE env sourced)
. $SYBASE/SYBASE.sh
isql -U sapsa -S <SID> -X            # -X encrypts the password over the wire; prompts for password
# non-interactive (avoid -P on the command line in shared shells — it shows in `ps`):
isql -U sapsa -S <SID> -X -w 999 -i script.sql -o out.log
```

**Windows:**
```bat
%SYBASE%\%SYBASE_OCS%\bin\isql.exe -U sapsa -S <SID> -X
```

Key parameters (verified list [V, S2]): `-U <user>`, `-S <server>`, `-P <password>` (omit to be
prompted), `-X` (encrypt password), `-D <database>`, `-I <interfaces>`, `-i <infile>`, `-o <outfile>`,
`-w <width>`. Commands are sent by typing `go` on its own line.

Quick health queries once connected:
```sql
select @@version                     -- server version / build
go
sp_who                               -- active connections
go
```

---

## 2. Start the database

ASE must be started **before** the SAP ABAP/Java instances. In an SAP system the normal path is the
SAP-integrated `startdb`; the DB-native path is `startserver`.

### 2a. SAP-integrated (preferred in an SAP system)

**Linux / AIX** — as `<sid>adm`:
```bash
startdb                              # starts the DB for this SID (calls ASE + Backup Server)
```
`startdb`/`stopdb` are the SAP wrapper scripts in the `<sid>adm` home. [G, S5]

> ⚠️ **After a kernel patch, `startdb` can fail on UNIX/Linux.** `startdb` runs as `<sid>adm` but the
> database must be started as **`syb<sid>`**, so `sybctrl` performs a user switch — which needs either the
> **SUID bit** on `sybctrl` (reset when kernel executables are replaced) or the `syb<sid>` password in
> **secure storage** (stored automatically by SWPM 1.0 SP01+; `sybctrl` prompts once and saves it
> otherwise; requires kernel **PL 327 for 7.20**). Note the limitation: if `startdb` is invoked from a
> **daemon** (e.g. from the start profile), the switch **still requires the SUID bit**.
> — **SAP Note 1796535** (see also 1796540 for changing passwords via `sybctrl`).
> Cross-ref [sap-kernel-patch](../../sap-kernel-patch/SKILL.md). [V, S7]

**Windows:** use the **SAP MMC** / **SAP Management Console** (start the DB node), or `sapcontrol`
(§2c). ASE itself runs as a **Windows service** (below).

### 2b. DB-native (startserver, UNIX)

**Linux / AIX** — as `syb<sid>`, ASE start-up uses a *runserver* file: [V/G, S3]
```bash
. $SYBASE/SYBASE.sh
# Start the dataserver:
startserver -f $SYBASE/$SYBASE_ASE/install/RUN_<SID>
# Start the Backup Server (needed for dump/load):
startserver -f $SYBASE/$SYBASE_ASE/install/RUN_<SID>_BS
```
`startserver -f RUN_<servername>` is the documented basic start-up command; the runserver file holds
the full `dataserver`/`backupserver` command line. [S3]

### 2c. Windows service / sapcontrol

- **Windows:** ASE and Backup Server run as services; their default start-up parameters are stored in
  the **Windows Registry** (not a RUN file). [G, S6] Start via SAP MMC, `Services.msc`, or:
  ```bat
  net start "SYBSQL_<SID>"           :: exact service name varies; check Services.msc
  ```
- **sapcontrol (any OS, if the DB is registered with the SAP Host Agent):**
  ```bash
  sapcontrol -nr <nr> -function StartDatabase
  ```
  Depends on Host Agent DB registration; if not registered, use `startdb`/`startserver`. [G, S1]

**Verify start (all OS):**
```bash
showserver                           # UNIX: lists running dataserver + backupserver [G]
ps -ef | egrep 'dataserver|backupserver' | grep <SID>   # UNIX
```
```sql
isql -U sapsa -S <SID> -X            -- if you can log in, the dataserver is up
select @@servername, @@version
go
```

---

## 3. Stop the database  ⚠️ destructive — no dry-run

Stop the SAP instances **first** (`sapcontrol … Stop` / `stopsap`), *then* the database.

### 3a. SAP-integrated

**Linux / AIX** — as `<sid>adm`:
```bash
stopdb                               # stops the DB for this SID [G, S5]
```
**Windows:** stop the DB node in SAP MMC, or `sapcontrol -nr <nr> -function StopDatabase`. [G, S1]

### 3b. DB-native (isql shutdown) — all OS

Connect as a System Administrator login and issue `shutdown`. [V/G, S4]
```sql
isql -U sapsa -S <SID> -X
-- graceful (default = "with wait": finishes running statements, checkpoints each DB, blocks new logins):
shutdown
go
```
Immediate stop (⚠️ **no checkpoint, no wait** — use only when graceful hangs):
```sql
shutdown with nowait
go
```
Stop the Backup Server specifically:
```sql
shutdown SYB_BACKUP
go
```
> Only a System Administrator can shut down ASE, and you must use `isql` to log in to an SA account. [S4]
> `shutdown with nowait` neither waits for executing statements nor checkpoints — recovery on next
> start will be longer. Prefer plain `shutdown`. [S4]

**Verify stop:**
```bash
showserver                           # UNIX: dataserver should no longer be listed
ps -ef | grep dataserver | grep <SID>
```

---

## 4. Basic backup (operational essentials)

Full backup/recovery is a separate skill (Phase 2); this is the minimum operational set. The
**Backup Server must be running** for any dump. [G]

```sql
isql -U sapsa -S <SID> -X
-- full database dump:
dump database <DBNAME> to '/backup/<DBNAME>_full.dmp'
go
-- transaction log dump:
dump transaction <DBNAME> to '/backup/<DBNAME>_log.trn'
go
```
In SAP landscapes, scheduled backups are usually driven from **DBA Cockpit (DB13)** / SAP tooling
rather than raw `dump`; use raw dumps for ad-hoc/pre-change safety copies. [G]

---

## 5. Boot-time autostart (OS-specific)

| OS | Mechanism |
|----|-----------|
| **Linux** | SAP start framework via **systemd** — `sapinit` / `saphostexec` unit; `/usr/sap/sapservices` lists the `sapstartsrv` entries. The DB comes up through `startdb`/Host Agent, not a standalone ASE unit. [G] |
| **AIX** | SAP start framework via **`/etc/inittab`** entry that launches `sapinit` (`/usr/sap/sapservices`). Same `startdb`/`startserver` underneath. [G] |
| **Windows** | ASE + Backup Server + `SAPService<SID>` run as **Windows Services** (Automatic start); managed via `Services.msc` / SAP MMC. [G, S6] |

---

## Sources

- **[S1]** *Starting and Stopping SAP Systems Using SAPControl* — SAP NetWeaver 7.5, Function-Oriented
  View. **[V]** Quotes the deprecation of `startsap`/`stopsap` (SAP Notes 1763593, 809477) and
  *"The database is not stopped by these commands."*
  https://help.sap.com/docs/SAP_NETWEAVER_750/ff18034f08af4d7bb33894c2047c3b71/471d6feeff6e0d46e10000000a155369.html
- **[S2]** *isql* — SAP Adaptive Server Enterprise **Utility Guide 16.1**. **[V]** Tool location and full
  parameter syntax.
  https://help.sap.com/docs/SAP_ASE/da6c1d172bef4597a78dc5e81a9bb947/a7f55bd0bc2b1014a288bf54a6a7c877.html
- **[S3]** *startserver / Using the startserver Command* — SAP ASE Utility Guide (16.0 SP04 PDF).
  `startserver -f RUN_<servername>`, path `$SYBASE/$SYBASE_ASE/install/RUN_<servername>`.
  https://help.sap.com/doc/a61873ebbc2b10148a2dd8b5b0a886fc/16.0.4.7/en-US/SAP_ASE_Utility_Guide_en.pdf
- **[S4]** *Stopping SAP ASE* (`shutdown` / `shutdown with nowait`; SA-only) — SAP ASE System
  Administration Guide.
  https://infocenter.sybase.com/help/topic/com.sybase.infocenter.dc35823.1600/doc/html/san1334282768547.html
- **[S5]** *Database Administration for SAP ASE* (SAP-system context: `startdb`/`stopdb`) — SAP
  NetWeaver 7.4 Library.
  https://help.sap.com/doc/saphelp_nw74/7.4.16/en-US/14/95bd14c0564c19bf1fd94c01920c32/content.htm
- **[S6]** *Start and Stop Servers* (Windows startup parameters in the Registry) — SAP ASE
  Configuration Guide.
  https://infocenter.sybase.com/help/topic/com.sybase.infocenter.dc38421.1600/doc/html/san1335472535811.html
- **[S7]** **SAP Note 1796535** — *SYB: Start and stop database without SUID bit for sybctrl*
  (BC-DB-SYB). **[V]** Retrieved via the SAP Notes MCP: *"After changing the kernel executables, it is
  required to set the SUID bit for sybctrl. Otherwise the startdb command will not work correctly. This
  applies to UNIX/Linux only."* / *"A user switch to the operating system user syb&lt;sid&gt; is required on
  Linux and UNIX platforms."* https://me.sap.com/notes/1796535

### Related SAP Notes

Cross-referenced from the verified SAPControl page [S1]; their purpose is quoted from [S1]:

- **SAP Note 1763593** — `startsap`/`stopsap` are deprecated; use SAPControl / SAP MMC instead.
  https://me.sap.com/notes/1763593
- **SAP Note 809477** — Central Note on starting/stopping SAP systems.
  https://me.sap.com/notes/809477

**To confirm/deepen** — with the SAP Notes MCP, `fetch` the two Notes above for their current wording,
and `search` the `SYB:` note series (component **BC-DB-SYB**) — the authoritative source for SAP-on-ASE
operations — for release-specific `startdb`/`stopdb` behaviour, plus the SAP ASE Administration Guide
for your S/4 release.
