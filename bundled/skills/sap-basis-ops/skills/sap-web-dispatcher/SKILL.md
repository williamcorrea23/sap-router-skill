---
name: sap-web-dispatcher
description: >-
  Operate the SAP Web Dispatcher, the reverse proxy / load balancer in front of SAP HTTP(S)
  traffic — start, stop, status, ports, profile essentials and the admin UI, on
  Linux/Windows/AIX. Use for "start/stop/restart the web dispatcher", "webdisp is down", "web
  dispatcher ports/profile", "wdisp/system backend", "/sap/wdisp/admin".
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

- **[W1]** *Starting and Stopping Web Dispatcher* — SAP Help Portal (`sapwebdisp pf=…`; stop via `kill -2`
  / `sapntkill -INT` / service; options `-cleanup`/`-auto_restart`/`-f`/`-t`).
  https://help.sap.com/doc/329ac769552a411b97bc7adb991b6197/3.0.12/en-US/eae7d26b822e4b1facc275f25b4f03a2.html
- **[W2]** *Operating / Installing and Configuring the SAP Web Dispatcher* — SAP Help Portal (profile,
  `icm/server_port`, `wdisp/system`, `/sap/wdisp/admin`). SAP NetWeaver AS documentation.

**To confirm/deepen:** the SAP Web Dispatcher guide for your release (profile parameter reference) and, for
instance-based deployments, [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
