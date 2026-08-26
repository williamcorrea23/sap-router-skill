---
name: sap-system-lifecycle
description: >-
  Start, stop and restart a SAP NetWeaver / S/4HANA system in the correct order — database and the
  instance layer (ERS, ASCS/SCS, PAS, AAS, Web Dispatcher) — using SAPControl (and SAP MMC on Windows)
  on Linux, Windows and AIX. Use whenever the task is "start/stop/restart the SAP system", "bounce
  <SID>", "start the app servers", "shut down for maintenance", or ordering the DB relative to the SAP
  instances. Hands the database start/stop off to sap-db-command-reference. Every command cited to
  help.sap.com / SAP Notes.
---

# SAP System Lifecycle (start / stop / restart)

`sapcontrol` orchestrates the **SAP instances**; it does **not** start or stop the **database** —
the official SAPControl documentation states *"The database is not stopped by these commands. You have
to stop the database using database-specific tools or commands."* [V, L1] So a full system operation is
always **two layers**: the DB (via [sap-db-command-reference](../sap-db-command-reference/SKILL.md)) and
the instances (here).

> **`startsap` / `stopsap` are deprecated** — use SAPControl. (SAP Notes 1763593, 809477.) [V, L1]

## Guardrail contract (see repo README)

1. **Identify** — SID, hosts, instance numbers, DB type/OS, and the **topology** (§1) before acting.
2. **Classify** — PRD vs non-PRD; any stop against **PRD** needs an explicit typed confirmation.
3. **Preview** — show the exact command + blast radius. `StopSystem` has no dry-run.
4. **Execute** — via the user's shell/SSH MCP, **one layer/step at a time**, never chained across a stop.
5. **Verify** — `GetProcessList` / `GetSystemInstanceList` after each step (§5).

---

## 1. Identify the topology first

List every instance of the system, its host, ports, start priority and status: [G, L4]
```bash
# UNIX (host agent copy):
/usr/sap/hostctrl/exe/sapcontrol -nr <nr> -function GetSystemInstanceList
# Windows:
%ProgramFiles%\SAP\hostctrl\exe\sapcontrol.exe -nr <nr> -function GetSystemInstanceList
```
Output columns: `hostname, instanceNr, httpPort, httpsPort, startPriority, features, dispstatus`. [G, L4]
The `features` column tells you the instance type:

| `features` contains | Instance | `startPriority` |
|---------------------|----------|-----------------|
| `ENQREP` | **ERS** — Enqueue Replication Server | **0.5** (first) |
| `MESSAGESERVER, ENQUE` (no `ABAP`) | **ASCS** (ABAP) / **SCS** (Java) — Central Services | **1** |
| `ABAP, GATEWAY, ICMAN, IGS` (+ `MESSAGESERVER` on the CI) | **PAS / AAS** — application servers | **3** (last) |
| `HDB` | database instance (started separately — see DB reference) | — |
| Web Dispatcher / standalone GW | front-end / gateway | 3 |

---

## 2. Start order

Instances start in **ascending `startPriority`**; the DB must be up before the application servers. [G, L2/L3]

```
1. DATABASE            → via sap-db-command-reference (HDB start / startdb / db2start / …)
2. ERS      (prio 0.5) ┐
3. ASCS/SCS (prio 1)   ├─ sapcontrol StartSystem does steps 2–4 in the right order automatically
4. PAS then AAS (prio 3)┘   (ERS is started before ASCS by design)
```

**Operationally (two commands):**
```bash
# 1) start the DB first — see sap-db-command-reference for the exact command for your dbms_type
# 2) then start all SAP instances of the system in priority order:
/usr/sap/hostctrl/exe/sapcontrol -nr <nr> -function StartSystem        # UNIX  [V, L1]
```
```bat
%ProgramFiles%\SAP\hostctrl\exe\sapcontrol.exe -nr <nr> -function StartSystem   :: Windows
```
- `StartSystem` starts **every** instance of the system in the correct priority sequence. [V, L1]
- To start a **single** instance: `sapcontrol -nr <nr> -function Start`. [V, L1]
- **Remote** instance: add `-host <host> -user <sidadm> <password>`. [V, L1]
- **Windows GUI alternative:** the **SAP MMC** (start the system/instance node). [G, L1]

---

## 3. Stop order  ⚠️ destructive — no dry-run

Reverse of start: application servers first, Central Services last, **then the database**. [G, L2/L3]

```
1. PAS/AAS  (prio 3)   ┐
2. ASCS/SCS (prio 1)   ├─ sapcontrol StopSystem does these in reverse-priority order automatically
3. ERS      (prio 0.5) ┘   (ASCS is stopped before ERS)
4. DATABASE            → via sap-db-command-reference (HDB stop / stopdb / db2stop / …)
```

**Operationally (two commands):**
```bash
# 1) stop all SAP instances of the system (reverse priority order):
/usr/sap/hostctrl/exe/sapcontrol -nr <nr> -function StopSystem         # UNIX  ⚠️ [V, L1]
# 2) then stop the DB — see sap-db-command-reference
```
```bat
%ProgramFiles%\SAP\hostctrl\exe\sapcontrol.exe -nr <nr> -function StopSystem   :: Windows
```
- Stop a **single** instance: `sapcontrol -nr <nr> -function Stop`. [V, L1]
- `StopSystem` variants let you scope the stop (e.g. `StopSystem ALL` / dialog instances only); default
  stops the system's instances in reverse-priority order. Confirm scope before running on PRD. [G, L5]
- **Order matters:** never stop the DB before the SAP instances — app servers lose their DB connection
  ungracefully. Stop instances → verify down → stop DB.

---

## 4. Restart

```bash
sapcontrol -nr <nr> -function RestartSystem       # instances only; DB is untouched  [G, L5]
```
For a **full** DB+instance restart, do it as ordered steps, not one command: StopSystem → stop DB →
start DB → StartSystem, verifying between each. A restart "for maintenance" usually means: StopSystem →
(DB stays up or is stopped per the task) → do the work → StartSystem.

---

## 5. Verify (after every step)

```bash
# instances of the whole system + status:
sapcontrol -nr <nr> -function GetSystemInstanceList        # dispstatus GREEN = up  [G, L4]
# processes of one instance (disp+work, msg server, enqueue, ICM, …):
sapcontrol -nr <nr> -function GetProcessList               # all GREEN  [V, L1]
```
`GREEN` = running, `YELLOW` = starting/stopping, `GRAY` = stopped, `RED` = error. Only report a
start/stop "done" once the relevant instances show the expected colour.

---

## 6. The control layer (always running)

`sapstartsrv` (one per instance) and the **SAP Host Agent** (`saphostexec`, under
`/usr/sap/hostctrl/exe`) are the services SAPControl talks to — they run independently of whether the
SAP system is up. If `sapcontrol` can't reach an instance, check `sapstartsrv` / the host agent first
(`saphostexec -status`), and the boot wiring (§ references).

---

## Cross-references

- **Database start/stop commands** (the layer SAPControl doesn't touch):
  [sap-db-command-reference](../sap-db-command-reference/SKILL.md) — HANA/Oracle/ASE/Db2/MaxDB/SQL Server.
- **Is it healthy / first-response triage:** `sap-health-triage`.
- **Full `sapcontrol` function catalog, instance-type glossary, and per-OS boot wiring**
  (systemd / `/etc/inittab` sapinit / Windows services): [references/sapcontrol-and-order.md](references/sapcontrol-and-order.md).

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

- **[L1]** *Starting and Stopping SAP Systems Using SAPControl* — SAP NetWeaver 7.5 / ABAP Platform. **[V]**
  sapcontrol paths, `StartSystem`/`StopSystem`/`Start`/`Stop`, remote `-host/-user`, `startsap`/`stopsap`
  deprecated (SAP Notes 1763593, 809477), *"The database is not stopped by these commands."*
  https://help.sap.com/docs/ABAP_PLATFORM_NEW/30eef4341efd4a2c86f2f98f187eccb3/471d6feeff6e0d46e10000000a155369.html
- **[L2]** **SAP Note 897933** — *Start and stop sequence for SAP systems* (canonical sequence + priorities).
  https://me.sap.com/notes/897933
- **[L3]** Start/stop sequence and `startPriority` (ERS 0.5 → ASCS/SCS 1 → PAS/AAS 3; ERS before ASCS;
  ASCS stopped before ERS; PAS/AAS require a running DB) — SAP S/4HANA Technical Operation curriculum
  + Note 897933. [G]
- **[L4]** `GetSystemInstanceList` fields (`hostname, instanceNr, httpPort, httpsPort, startPriority,
  features, dispstatus`) — SAPControl documentation. [G]
- **[L5]** *Starting and Stopping SAP System Instances Using Commands* — SAP Help Portal (`RestartSystem`,
  `StopSystem` scope). https://help.sap.com/docs/PRODUCT_ID/00b4e4853ef3494da20ebcaceb181d5e/0a2f54809e064ee68b02fb9fb392bafd.html

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): SAP Note 897933 for the exact
priority table of your release, and SAP Note 1763593 for the `startsap`/`stopsap` deprecation details.
