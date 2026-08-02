# SAP HANA — Operational Commands

`dbms_type = hdb`. SAP HANA is the database under S/4HANA, BW/4HANA and Suite-on-HANA. This file
covers **start, stop, connect, tenant management, status and basic backup** at the OS/DB layer.

> **Platform reality (read first):** the **SAP HANA database server runs on Linux only** — SLES for
> SAP Applications or RHEL for SAP Solutions, on x86-64 or IBM Power (ppc64le). It is **not supported
> on Windows or AIX.** (Authoritative: SAP Note 2235581 + the Product Availability Matrix.) [H4]
> So all *server-side* commands below (`HDB`, `sapcontrol`, `hdbnsutil`) are **Linux-only** — there is
> no Windows/AIX variant. Only the **HANA client** (`hdbsql`) ships for Linux, Windows and AIX, so the
> *connect* section has all three; everything else is Linux.

> **Guardrail reminder:** `HDB stop` / `StopSystem` take a running production DB down with no dry-run,
> and in MDC **stopping SYSTEMDB stops every tenant.** Identify → Preview → typed confirmation for PRD
> → one step → Verify. Never put `-p <password>` on a shared command line — use `hdbuserstore` (§1).

Verification legend: **[V]** verified against the live help.sap.com page during authoring · **[G]**
cited to the official guide/Note (confirm exact flags for your revision).

---

## 0. Layout, users and environment (Linux)

| Item | Value |
|------|-------|
| OS admin user | `<sid>adm` (lower-case SID, e.g. `h10adm`) |
| Instance dir | `/usr/sap/<SID>/HDB<nr>/` (`<nr>` = 2-digit instance number) |
| Shared / data / log | `/hana/shared`, `/hana/data/<SID>`, `/hana/log/<SID>` |
| Server executables | `/usr/sap/<SID>/HDB<nr>/exe/` (`HDB`, `hdbnsutil`, `hdbsql`, …) |
| Client (separate install) | `/usr/sap/hdbclient/` (Linux) · `hdbsql.exe` under the HANA client dir (Windows) |
| `sapstartsrv` control ports | `5<nr>13` / `5<nr>14` |
| SQL ports (MDC) | SYSTEMDB `3<nr>13`; first tenant `3<nr>15` (then `+2` per tenant) |

Multitenant (MDC) is the norm: one **SYSTEMDB** plus one or more **tenant** databases. Starting
SYSTEMDB starts the tenants; tenants can also be managed individually. [V, H1]

---

## 1. Connect (hdbsql) — Linux / Windows / AIX (client)

`hdbsql` is the HANA CLI, shipped in the HANA client for all three OSes.

**Linux / AIX:**
```bash
# as <sid>adm (server) or from any host with the HANA client installed
hdbsql -i <nr> -d SYSTEMDB -u SYSTEM -p '<password>'     # SYSTEMDB (port 3<nr>13)
hdbsql -i <nr> -d <TENANT>  -u SYSTEM -p '<password>'    # a tenant (port 3<nr>15+)
hdbsql -n <host>:3<nr>13 -d SYSTEMDB -u SYSTEM           # explicit host:port; prompts for password
```

**Windows:**
```bat
hdbsql.exe -i <nr> -d SYSTEMDB -u SYSTEM -p "<password>"
```

**Avoid passwords on the command line** (they show in `ps`/history) — use the secure user store: [G, H5]
```bash
hdbuserstore SET <KEY> <host>:3<nr>13 <user> <password>   # one-time, per OS user
hdbsql -U <KEY> "SELECT * FROM M_DATABASES"               # then connect by key, no password
```
Key params [G, H5]: `-i <instance>`, `-n <host:port>`, `-d <database>`, `-u <user>`, `-p <password>`,
`-U <userkey>`, `-A` (autocommit off), `-I <file>` (run script), `-o <file>` (output).

Quick health once connected:
```sql
SELECT * FROM M_DATABASES;                 -- tenants + status (in SYSTEMDB)
SELECT * FROM M_SERVICES;                  -- service processes + state
```

---

## 2. Start the database (Linux only)

Start **before** the SAP application instances. Two options; both go through `sapstartsrv`. [V, H1]

### 2a. HDB script (single-host) — as `<sid>adm`
```bash
HDB start          # start this HANA instance
HDB info           # show running HANA processes (verify)
HDB version        # revision
```
`HDB` is a wrapper that calls `sapcontrol` underneath. **It cannot start/stop a distributed
(scale-out) system** — use `sapcontrol` on the master node for those. [G, H3]

### 2b. SAPControl (single- or multi-host) — as `<sid>adm`
```bash
/usr/sap/<SID>/HDB<nr>/exe/sapcontrol -nr <nr> -function StartSystem HDB
/usr/sap/<SID>/HDB<nr>/exe/sapcontrol -nr <nr> -function GetProcessList   # verify
```
`sapcontrol -nr <nr> -function <fn>` where `<nr>` is the 2-digit instance number; must be `<sid>adm`
or root. [G, H2]

**Verify start:**
```bash
HDB info                                              # hdbnameserver/hdbindexserver/… running
sapcontrol -nr <nr> -function GetProcessList          # all GREEN
```

---

## 3. Stop the database (Linux only)  ⚠️ destructive — no dry-run

Stop the SAP application instances **first**, then HANA.

### 3a. HDB script — as `<sid>adm`
```bash
HDB stop           # graceful shutdown of this instance
```
Hard/emergency stop (kills processes — recovery on next start is longer, use only if graceful hangs):
```bash
HDB kill-9         # sends SIGKILL to HANA processes  ⚠️
```

### 3b. SAPControl (soft vs hard) — as `<sid>adm`
```bash
sapcontrol -nr <nr> -function StopSystem HDB          # controlled stop of the whole system
```
SAPControl/cockpit offer **soft** shutdown (waits for active sessions to finish) vs **hard** shutdown
(kills and rolls back open transactions). [G, H2]

> **MDC:** `StopSystem HDB` / `HDB stop` stops **SYSTEMDB and all tenants**. To stop just one tenant,
> use §4.

**Verify stop:** `HDB info` shows no HANA processes; `GetProcessList` returns nothing running.

---

## 4. Tenant (MDC) start/stop — SQL on SYSTEMDB

Connect to **SYSTEMDB** and manage individual tenants without touching the whole system: [G, H1]
```sql
-- as SYSTEM in SYSTEMDB:
ALTER SYSTEM STOP  DATABASE <TENANT>;      -- ⚠️ stops one tenant only
ALTER SYSTEM START DATABASE <TENANT>;
SELECT DATABASE_NAME, ACTIVE_STATUS FROM M_DATABASES;   -- verify
```

---

## 5. Status & health checks (Linux)

```bash
HDB info                                    # process list for this host
sapcontrol -nr <nr> -function GetProcessList
hdbnsutil -sr_state                         # read-only: system replication role/status (if HSR configured)
```
```sql
SELECT * FROM M_DATABASES;                  -- tenant states (SYSTEMDB)
SELECT * FROM M_SERVICES;                   -- per-service coordinator/status
SELECT * FROM M_HOST_INFORMATION;           -- host/landscape
```

---

## 6. Basic backup (operational essentials)

Full backup/recovery is a separate skill (Phase 2). Backups are triggered by SQL (per database): [G]
```sql
-- run in the target database (SYSTEMDB or tenant):
BACKUP DATA USING FILE ('<prefix>');                        -- complete data backup
BACKUP DATA FOR <TENANT> USING FILE ('<prefix>');           -- a tenant, issued from SYSTEMDB
SELECT * FROM M_BACKUP_CATALOG ORDER BY SYS_START_TIME DESC; -- verify
```
In SAP landscapes these are usually scheduled from **DBA Cockpit (DB13)** / HANA cockpit / Backint;
use raw `BACKUP DATA` for ad-hoc pre-change safety copies. Ensure `log_mode = normal` and log backups
are running before relying on point-in-time recovery. [G]

---

## 7. Boot-time autostart (Linux)

The SAP start framework brings HANA up via **systemd** (`sapinit` / `saphostexec`); `/usr/sap/sapservices`
lists the `sapstartsrv` entries. Per-instance autostart is controlled by the `Autostart` parameter in
the instance profile `/usr/sap/<SID>/SYS/profile/<SID>_HDB<nr>_<host>`. (No Windows/AIX equivalent — HANA
server is Linux-only.) [G]

---

## Sources

- **[H1]** *Starting and Stopping SAP HANA Systems* — SAP HANA Administration Guide, SAP HANA Platform
  2.0 SPS08. **[V]** `<sid>adm`, cockpit/studio/SAPControl options, MDC (SYSTEMDB starts tenants).
  https://help.sap.com/docs/SAP_HANA_PLATFORM/6b94445c94ae495c83a19646e7c3fd56/19d7e465008045afb996c61a804e76f0.html
- **[H2]** *Starting and Stopping Systems with SAPControl* — same guide. `sapcontrol -nr <nr> -function
  Start/Stop/StartSystem/StopSystem/GetProcessList`; `<sid>adm`/root; soft vs hard shutdown. [G]
- **[H3]** *HDB* command (`HDB start|stop|info|version|kill-9`; cannot start a distributed system — use
  sapcontrol on the master node) — SAP HANA Administration Guide. [G]
- **[H4]** **SAP Note 2235581** — *SAP HANA: Supported Operating Systems* (SLES / RHEL only; x86-64 /
  IBM Power). Authoritative platform source alongside the SAP HANA PAM. https://me.sap.com/notes/2235581 [G]
- **[H5]** *hdbsql* / *hdbuserstore* — SAP HANA Client / SQL Reference. Connect syntax and secure store. [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): pull SAP Note 2235581 for the exact
OS/revision matrix, and the SAP HANA Administration Guide revision matching your installed HANA 2.0 SPS.
