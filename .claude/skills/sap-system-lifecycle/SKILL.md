---
name: sap-system-lifecycle
description: >-
  Start, stop and restart a NetWeaver / S/4HANA system in the correct order — database and the
  instance layer (ERS, ASCS/SCS, PAS, AAS, Web Dispatcher) — using SAPControl and SAP MMC on
  Windows, on Linux/Windows/AIX. Use for "start/stop/restart the SAP system", "bounce <SID>",
  "start the app servers", "shut down for maintenance", or ordering the DB relative to the SAP
  instances. Hands DB start/stop to sap-db-command-reference.
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
- **`sap-health-triage` §0** — if the system will not respond at all, use the out-of-band ladder before deciding to restart.

## Execution discipline (non-negotiable)

### The holy rule — nothing runs unbacked

**Every command executed must be traceable to one of exactly three things:**

1. an **official SAP source** — help.sap.com page / Operations or Administration Guide, or
2. an **SAP Note / KBA**, or
3. an **explicit instruction from the user**.

If a command is backed by none of those, **do not run it** — say what backing is missing and stop.
"It's probably fine", "this is standard", and "I recall the syntax" are not backing. When the backing is
a source, name it (page or Note number) alongside the command; when it is the user, quote the instruction.

### Ambiguity ⇒ stop and confirm, before any execution

If executing would require **assuming** anything the user did not state, you are **obliged** to confirm
first. Never fill a gap with a plausible default. Common gaps that force a stop:

- **client number**, SID, instance number, target host/node
- **read-only vs state-changing** — if it is not explicit which was wanted, ask
- **scope** — one instance vs the whole system, one tenant vs all, one client vs cross-client
- which **database / dbms_type**, which environment (**PRD vs non-PRD**)
- retention/age cut-offs, recovery points, target of a restore, transport target

A wrong assumption here is not a typo — it is the difference between reading a log and stopping production.

### But verify programmatically FIRST — *then* ask

**Asking the user for something the system can answer is a failure.** Before you raise a question, ask
the user to go and look, or request Computer Use / GUI access, you **must** first try to determine it
programmatically. Only what genuinely cannot be derived — intent, authorization, a business decision, a
value that exists only in the user's head — is a legitimate question.

| Determine programmatically (do NOT ask) | Ask the user (cannot be derived) |
|---|---|
| Which DB — `echo $dbms_type`, profile `dbms/type` | Which **client** to act on |
| SIDs / instances / hosts / ports — `sapcontrol … GetSystemInstanceList`, `ls /usr/sap` | Whether this system is in scope / approved |
| Is it up, is the DB up — `GetProcessList`, `R3trans -d` | PRD change approval, downtime window |
| Kernel / release / patch — `disp+work -version`, `saphostexec -version` | The intended recovery point or retention policy |
| Which clients **exist** — table `T000` | Which of those clients is **meant** |
| Free space, log locations, parameter values — `df -h`, `sappfpar`, profile | Business impact / urgency |

Order, always: **verify programmatically → ask only what remains → never assume.**

### Prefer programmatic over manual or GUI

**Work down this ladder. Take the highest rung that does the job — and within that rung, the lowest
privilege that suffices. Never skip a rung because you assume it is unavailable (see the burden of
proof below).**

| # | Path | Privilege | Notes |
|---|---|---|---|
| **1** | **REST / OData** — `GET` first | Narrowest. Scoped service user | Read-only by construction when you stay on `GET`. `$metadata` gives you the contract |
| **2** | **SOAP / web service** | Scoped service user | Typed contract via `?wsdl`. Client-cert auth where offered — no password in a script |
| **3** | **RFC / BAPI** (`creds exec`, JCo, `pyrfc`) | RFC user with `S_RFC` | **For ABAP *writes*, prefer this over 1–2**: BAPIs have real commit/rollback semantics and land in SM19/SM20 |
| **4** | **OS shell as the *correct* user** → **DB utility** | ⚠️ Escalates — see below | The chain matters more than the rung |
| **5** | **Browser automation** (headless or in-app) | Interactive user | Session-based UIs only. Fragile across releases |
| **6** | **Computer Use / screen driving** | Interactive user | **Last resort.** Not repeatable, not diffable, breaks on any UI change |

> ## ⚠️ Rung 4 is a chain, and each link widens the blast radius
>
> ```
> ssh <host>                    ← host access
>   → su - <sid>adm             ← SAP admin: can stop/start the system
>   → su - ora<sid> / syb<sid>  ← DB owner: can drop data
>   → sudo / root               ← everything
>        → hdbsql | isql | dbmcli | sqlplus | db2   ← the actual command
> ```
>
> **Stop at the least-privileged user that can run the command.** Most read-only checks need only
> `<sid>adm`; DB utilities usually need the DB owner; **root is almost never the right answer** and
> `saproot.sh` is the rare legitimate exception. Say which user you used and why.

> ## Two axes, and they do not agree
>
> The ladder ranks by **automation quality** — repeatable, reviewable, loggable, diffable. Privilege
> runs on a *different* axis and is **worst in the middle**: rung 4 (OS/root) can destroy a system,
> while rung 6 (Computer Use) is merely an interactive user clicking. So Computer Use ranks last for
> *reproducibility*, not because it is the most dangerous.
>
> **The practical rule: prefer the highest rung, but never escalate privilege to climb it.** A
> read-only OData call beats an RFC that needs a write-capable user; an `<sid>adm` shell beats a root
> shell. If climbing a rung requires more privilege than the task needs, stay where you are and say so.

> ## 🛑 You must **demonstrate** the absence of a programmatic path, not assume it
>
> "There is no API for this" is a **finding that requires evidence**, not a default. Before dropping to
> rung 5 or 6, actually probe:
>
> - **HTTP status codes tell you the access mode.** `401` → Basic auth works, **scriptable**.
>   `302` regardless of credentials → session UI, browser needed. `404` → not deployed. `503` →
>   deployed but stopped.
> - **Look for a contract**: append `?wsdl`, `$metadata`, `/api`, `?sap-client=` and see what answers.
> - **Ask the platform what it exposes**: `sapcontrol -function J2EEGetApplicationAliasList`,
>   `hdbcons help`, `btp --help`, `xs help`, `<tool> -h`.
> - **A Swing or WebDynpro *UI* being un-automatable does not mean the *objects* are.** The editor and
>   the API are different doors — check for the second before declaring the first is the only one.
>
> Programmatic execution is repeatable, reviewable, loggable and diffable; screen-driving is none of
> those. When you do drop to a lower rung, **say which rung you are on and what you probed** to rule
> out the higher ones — so the user can correct you if they know of a path you missed.

### Ask how output should be handled

Work that produces evidence (logs, traces, command output, screenshots, reports) has two reasonable
endings. **Ask which the user wants** rather than guessing:

- **(a) persist it** — write the output/logs/screenshots to a file, and say exactly where; or
- **(b) execute and report** — just run it and give a short final status summary.

Don't dump large output into the conversation unasked, and don't silently discard evidence either — for
troubleshooting and any change with a rollback, (a) is usually the right default to offer.

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
3. **Check the `attachments` array.** SAP routinely puts the actual deliverable *in an attachment* rather
   than the Note body — sizing guides, SQL script collections, configuration PDFs, spreadsheets. A Note
   whose text says "see the attached document" is not fully read until you have it.
4. Prefer the Note over this file where they disagree, and say which Note you followed.

**Downloading an attachment:** `fetch` returns `attachments[].url` **and `attachments[].filename`**;
**`fetch_attachment`** retrieves the bytes. Pass the URL verbatim — the URLs are opaque and cannot be
constructed. If your MCP build predates that tool, open the URL in a signed-in browser instead and say the
file was fetched manually.

> ⚠️ **Two ways a hand-rolled fetch goes wrong — both verified.**
> **1. Trusting the status code.** An unauthenticated request returns **HTTP 200 with a small HTML login
> stub**, not an error. Check the content type and magic bytes, or you save a JavaScript redirect page
> under a `.pdf` name.
> **2. Naming the file from the URL.** SAP serves many attachments from a *generic endpoint* —
> `…/services/attachment.htm?iv_key=…&iv_guid=…` — so the URL basename is `attachment.htm` even when the
> payload is a 24-page PDF. Take the name from **`attachments[].filename`** or the response's
> **`Content-Disposition`** header, never from the URL path.

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
