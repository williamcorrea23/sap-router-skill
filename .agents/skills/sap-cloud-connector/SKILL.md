---
name: sap-cloud-connector
description: >-
  Operate the SAP Cloud Connector (SCC) — the secure on-premise agent that links SAP BTP to on-prem
  systems — start, stop, restart, the admin UI (port 8443), Master/Shadow high availability, ports and
  auto-restart, on Linux, Windows and macOS (not AIX). Use for "start/stop/restart cloud connector", "scc
  is down", "cloud connector admin UI 8443", "SCC high availability master shadow". Logs (ljs_trace.log)
  in sap-log-reference. Cited to help.sap.com / SAP KBAs.
---

# SAP Cloud Connector (SCC)

SCC is a Java agent that establishes an **outbound TLS tunnel** from your network to an SAP BTP subaccount,
exposing selected on-prem systems to cloud apps under fine-grained access control. It runs on its own JVM
(not an SAP kernel instance).

> **Platform note:** SCC runs on **Linux, Windows and macOS** — **not AIX** (unlike the SAP kernel
> components). If the on-prem hosts are AIX, SCC still runs on a separate Linux/Windows host. [C2]

> **Guardrail:** SCC is the **single bridge** between BTP and on-prem — stopping it **breaks all
> cloud→on-prem connectivity** (cloud Fiori, integration flows, RFC/HTTP to the backend). Use the
> **Shadow** for zero-downtime; confirm before stopping a Master. Access-control changes expose/hide
> internal systems — treat as security-sensitive.

---

## 1. Start / stop / restart  [C1]

**Linux** — as the SCC/OS admin:
```bash
# systemd distributions:
systemctl start|stop|restart scc_daemon
# System V distributions:
service scc_daemon start|stop|restart
```
**Windows:** the Cloud Connector is a **Windows service** (auto-start after install) — start/stop via
`Services.msc` or `net start|stop <SCC service>`.

**macOS / portable install:** the `<scc>/` install dir scripts (`go.sh` / daemon control).

The daemon **auto-restarts** on host reboot by default (disable per **KBA 3474163** if required). [C1]

---

## 2. Admin UI & first login

```
https://<host>:8443        # default admin UI port; default user "Administrator"
```
- First login forces a password change. [C2]
- Change the admin UI port per **KBA 2955431** (e.g. behind a reverse proxy). [C3]
- The UI is where you do everything else: add subaccounts, define **access control** (map a *virtual*
  host/port to an *internal* system), configure **service channels**, and view **Log And Trace Files**.

---

## 3. Ports

| Purpose | Port |
|---------|------|
| Administration UI (HTTPS) | **8443** (default; changeable — KBA 2955431) |
| Outbound tunnel to BTP region | **443** (TLS, outbound only — no inbound firewall opening) |
| Exposed backend systems | the *virtual* host/port you define per access-control mapping |

---

## 4. High availability (Master / Shadow)

- **Master** — the standard, fully-functional installation.
- **Shadow** — a second SCC configured as backup; it takes over if the Master fails, giving HA. Configure
  the Shadow to point at the Master; failover keeps the BTP tunnel available. [C2]

Check state and trigger/monitor failover from the admin UI (Master/Shadow status).

---

## 5. Logs

`ljs_trace.log` (main Java trace, rotates ~20×50 MB), plus `scc_*` and audit logs, in the SCC `log/`
directory — downloadable from the admin UI (Log And Trace Files). Details in
[sap-log-reference](../sap-log-reference/SKILL.md).

## Cross-references

- Traces: [sap-log-reference](../sap-log-reference/SKILL.md).
- Other connectivity front-ends: `sap-web-dispatcher` (HTTP reverse proxy), `sap-saprouter` (NI proxy).

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

- **[C1]** **SAP KBA 2485510** — *How to start/stop/restart SAP Cloud Connector (SCC)*
  (`systemctl`/`service scc_daemon`, Windows service). https://me.sap.com/notes/2485510
- **[C2]** *SAP Cloud Connector* documentation — SAP BTP Connectivity (install, admin UI 8443,
  Master/Shadow high availability, supported platforms). help.sap.com (SAP BTP Connectivity → Cloud
  Connector).
- **[C3]** **SAP KBA 2955431** — *How to change the default admin UI port of SAP Cloud Connector*.
  https://me.sap.com/notes/2955431
- Auto-restart control: **SAP KBA 3474163** (disable auto-restart on Linux). https://me.sap.com/notes/3474163

**To confirm/deepen:** the SAP Cloud Connector documentation for your version (system requirements +
Master/Shadow setup) and KBA 2485510 for the exact service/daemon names on your OS.
