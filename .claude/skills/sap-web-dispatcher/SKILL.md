---
name: sap-web-dispatcher
description: >-
  Operate the SAP Web Dispatcher (the reverse proxy / load balancer in front of SAP HTTP(S) traffic) —
  start, stop, status, ports, profile essentials and the admin UI — on Linux, Windows and AIX. Use for
  "start/stop/restart the web dispatcher", "webdisp is down", "web dispatcher ports/profile", "wdisp/system
  backend", "/sap/wdisp/admin". Logs are in sap-log-reference. Cited to help.sap.com.
---

# SAP Web Dispatcher

The Web Dispatcher terminates/forwards HTTP(S) to the SAP back-end (message-server load balancing + SSL).
Two deployment shapes:
- **Instance-based** (modern S/4): a real SAP instance `W<nr>` with `sapstartsrv` — driven by **SAPControl**
  exactly like any instance ([sap-system-lifecycle](../sap-system-lifecycle/SKILL.md)).
- **Standalone binary**: the `sapwebdisp` executable + a profile, started/stopped directly.

> **Guardrail:** it's internet-/user-facing — a stop **drops all active HTTP sessions**. Identify SID/host,
> classify PRD, confirm before bouncing. `saprouttab`-style access and SSL config are security-sensitive.

---

## 1. Start / stop / status

### Instance-based (has `sapstartsrv`)
```bash
sapcontrol -nr <nr> -function Start          # start;  Stop / RestartSystem to stop / restart
sapcontrol -nr <nr> -function GetProcessList # status — the WEBDISP/ICMAN process GREEN
```

### Standalone binary
```bash
# start (UNIX/Windows) — profile holds ports + backend systems:
sapwebdisp pf=<path>/sapwebdisp.pfl          # Windows: sapwebdisp.exe pf=…   [G, W1]
# stop — send SIGINT to the PID:
kill -2 <pid>            # UNIX (graceful)                                     [G, W1]
sapntkill -INT <pid>     # Windows                                            [G, W1]
# or, if installed as a Windows service: Services.msc → stop "sapwebdisp"
```
Useful start options [G, W1]: `-f <tracefile>`, `-t <tracelevel>`, `-cleanup` (release shared memory),
`-auto_restart`, `-shm_attach_mode`, `-version`.

**Status also via the admin UI:** `https://<host>:<https_port>/sap/wdisp/admin` (see §3).

---

## 2. Ports

| Purpose | Profile parameter | Typical |
|---------|-------------------|---------|
| HTTP listener | `icm/server_port_<n> = PROT=HTTP,PORT=80<nr>` | `80<nr>` |
| HTTPS listener | `icm/server_port_<n> = PROT=HTTPS,PORT=443<nr>` | `443<nr>` |
| Admin UI | under `icm/HTTP/admin_<n>` / a dedicated port | e.g. `4<nr>xx` |

---

## 3. Profile essentials & admin UI

Minimum config in `sapwebdisp.pfl` / the instance profile: [G, W2]
```
SAPSYSTEMNAME = <SID>
icm/server_port_0 = PROT=HTTP,PORT=8000
icm/server_port_1 = PROT=HTTPS,PORT=44300
wdisp/system_0 = SID=<backendSID>, MSHOST=<msg-server-host>, MSPORT=81<nr>, SRCSRV=*:*, SRCURL=/
wdisp/ssl_encrypt = 1
icm/HTTP/admin_0 = PREFIX=/sap/wdisp/admin, DOCROOT=..., AUTHFILE=...
```
- `wdisp/system_<n>` defines each back-end system (message-server host/port for load balancing).
- **Admin UI:** `/sap/wdisp/admin` — status, back-end groups, trace level, restart. Protect with `AUTHFILE`.

---

## 4. Logs

`dev_webdisp` (main trace), `dev_webdisp_log` (start/stop/config), ICM-style HTTP access logs — details and
trace levels (`icm/trace_level`, `icm/HTTP/logging_<n>`) in
[sap-log-reference](../sap-log-reference/SKILL.md) → app-and-component-logs.

## Cross-references

- Instance-style start/stop & order: [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
- Health/status detail: [sap-health-triage](../sap-health-triage/SKILL.md).
- Traces: [sap-log-reference](../sap-log-reference/SKILL.md).

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

- **[W1]** *Starting and Stopping Web Dispatcher* — SAP Help Portal (`sapwebdisp pf=…`; stop via `kill -2`
  / `sapntkill -INT` / service; options `-cleanup`/`-auto_restart`/`-f`/`-t`).
  https://help.sap.com/doc/329ac769552a411b97bc7adb991b6197/3.0.12/en-US/eae7d26b822e4b1facc275f25b4f03a2.html
- **[W2]** *Operating / Installing and Configuring the SAP Web Dispatcher* — SAP Help Portal (profile,
  `icm/server_port`, `wdisp/system`, `/sap/wdisp/admin`). SAP NetWeaver AS documentation.

**To confirm/deepen:** the SAP Web Dispatcher guide for your release (profile parameter reference) and, for
instance-based deployments, [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
