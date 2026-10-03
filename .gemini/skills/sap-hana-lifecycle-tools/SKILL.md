---
name: sap-hana-lifecycle-tools
description: >-
  The two HANA command-line tools outside SQL — hdblcm for install, update, add/remove hosts,
  host roles, internal network and SLD registration (resident vs media, --action, batch mode),
  and hdbcons for expert diagnostics when SQL is unavailable: runtime dumps, call stacks, memory
  analysis, savepoints, log release. Use for "hdblcm", "add host HANA", "update HANA revision
  command line", "hdbcons", "runtime dump", "HANA hangs SQL not possible", "call stack HANA",
  "mm ipmm", "log release", "cons.crashdump".
---

# SAP HANA lifecycle & console tools

Two very different tools, grouped because both are HANA command-line entry points that Basis uses
when the SQL layer is not the answer.

| Tool | Purpose | Risk |
|---|---|---|
| **`hdblcm`** | Lifecycle: install, update, add/remove hosts, host roles, network, SLD | Change-controlled |
| **`hdbcons`** | Expert diagnostics against a running (or hanging) HANA process | ⚠️ **Can destabilise a live database** |

---

## 1. `hdbcons` — read the warning before the commands

**Source.** **SAP Note 2222218 — *FAQ: SAP HANA Database Server Management Console (hdbcons)***,
version **122**, released **25.07.2026**, component HAN-DB **[V]** — fetched and read directly.

> ## 🛑 SAP's own framing, verbatim
>
> *"hdbcons is an **expert tool** delivered as part of the SAP HANA software. In normal cases it is
> **not required** to use it… As improper usage of hdbcons can have a **severe impact on SAP HANA**,
> you should **only run it under guidance of SAP** (e.g. if recommended in a SAP case or SAP Note)."*
> **[V]**
>
> *"Be aware that both the available commands and the structure of the hdbcons output **can change
> between SAP HANA Revisions without further notice**."* **[V]**
>
> Several documented commands have caused **indexserver crashes** on specific revisions (§4). This is
> not a tool to explore on a production system.

### When it is genuinely the right tool **[V]**

- Retrieving data from **secondary system replication sites** that cannot be reached via SQL
- Retrieving data from a **hanging HANA instance** no longer accessible via SQL
- Advanced **memory tracing and analysis**
- Functions with no SQL equivalent — acknowledging internal events, resetting SSFS consistency

### Starting it **[V]**

```bash
hdbcons                      # connects to the indexserver by default
hdbcons -p <pid>             # a specific process by PID
hdbcons -e hdbnameserver     # a specific process by name
hdbcons -d <tenant_db_name>  # SPS06+ — see below
```

> ## ⚠️ SPS 06 behaviour change that looks like an outage
>
> From **HANA 2.0 SPS 06**, calling `hdbcons` with no options **fails to connect** when the tenant
> name differs from the database system ID (issue 288374) **[V]**:
>
> ```
> exception 1: no.2050100 … System call failed [generic:111]: Connection refused
> ```
>
> **This is intended behaviour, not a fault.** Use the new **`-d <tenant_db_name>`** option.

**In multitenant systems, use hdbcons from the system database**, and reach tenants with
`distribute e <host>:<port> <command>` (SAP Note 2410143). The Studio console tab is deliberately not
shown for tenant connections. **[V]**

**Via SQL** — a subset of commands only **[V]**:

```sql
CALL MANAGEMENT_CONSOLE_PROC('<hdbcons_command>', '<host>:<port>', ?);
```

Gated by `global.ini → [customizable_functionalities] → builtinprocedure.management_console_proc`
(default `true`). Unsupported commands return
`exception 2120012: External command <x> not available in sql`. **[V]**

### The commands worth knowing **[V]**

```
help / help <command>        # server-side options;  hdbcons -?  for client-side
runtimedump dump [-f <file>] # the single most useful artefact for SAP support
context l -s [-f]            # call stacks for active (-f: also inactive) threads
replication i                # system replication overview when SQL is unavailable
mm ipmm -d                   # inter-process memory management + flight recorder
mm l -s -S -p                # heap allocator list, sorted by size, with peaks
mm poolallocator             # heap fragmentation
resman i                     # resource container overview
savepoint execute            # trigger a savepoint
log backup / log release     # force log backup / release free log segments
encryption status            # persistence encryption status
snapshot l / a / d           # list / analyse / delete snapshots
transaction c <id>           # cancel a transaction's active operation
connection c|d <conn_id>     # cancel / disconnect a connection
output l                     # list directories hdbcons is allowed to write to
```

> **`transaction c` does not cancel the transaction.** SAP is explicit: *"strictly speaking not the
> transactions themselves are cancelled. Instead only **active operations within** transactions are
> cancelled. So an active transaction without a currently active operation is left untouched."* **[V]**

### `dvol shrink` — and where it must never run

`dvol shrink -o <overhead_pct>` performs data-file defragmentation, comparable to
`ALTER SYSTEM RECLAIM DATAVOLUME`. Suggested value **120**, and only worthwhile if the space will
stay freed. **[V]**

> ⚠️ **Must not be executed on secondary system replication sites.** **[V]** See
> **`sap-hana-system-replication`**.

---

## 2. `hdbcons` failure modes SAP documents

| Symptom | Meaning **[V]** |
|---|---|
| `Could not open connection to server process` | Either a non-existent `-p <pid>`, or the indexserver cannot be contacted by socket — typically because **two indexservers were started on the same node**. Workaround: explicit `-p <pid>`; fix: stop HANA and restart a single indexserver |
| `[ERROR] Write access for file with name … is prohibited` | hdbcons may only write to permitted directories (e.g. `/tmp`, the HANA trace directories). Run **`output l`** to list them. Relative paths resolve against the trace directory; relative paths are broken on some revisions (issue 321727, fixed > 2.0 SPS 08) — use an absolute path |
| `cons.crashdump.<timestamp>.trc` appears | **hdbcons itself crashed**; see SAP Note 2177064 |

**Known crash-inducing commands** — check your revision before using **[V]**:

| Command | Crashes on |
|---|---|
| `mm bl`, `mm cg`, `mm top` | HANA < 1.00.122.15, < 2.00.012.04, < 2.00.023 (Note 2599979) |
| `statreg print -h` | HANA 2.00.040 – 2.00.042 (Note 2845208) |
| `pageaccess a` | HANA < 1.00.122.15 (Note 2616088) |
| `log release` | Nameserver crash (Note 2781933) |
| `jexec logclear` while a rolling log is running | Indexserver crash (issue 341295) — `logstop` first |

**Who called hdbcons, and when?** From **HANA 2.0 SPS 03** a dedicated trace records every call with
parameters, timestamp and duration **[V]**:

```
<service>_<host>.<port>.hdbcons.trc
```

Useful in a post-incident review — and a reason to assume your hdbcons use is auditable.

---

## 3. `hdblcm` — the lifecycle manager

Two forms, and picking the wrong one is the usual stumble:

| Form | Path | Use for |
|---|---|---|
| **Media** `hdblcm` | On the extracted installation medium | **Installing** a new system; updating from media |
| **Resident** `hdblcm` | **`/hana/shared/<SID>/hdblcm/hdblcm`** | Post-installation changes to an **existing** system |

**If the resident hdblcm is missing**, SAP Note **2651885** covers installing it from the media
**[G]**.

```bash
./hdblcm --help                       # authoritative for your version — always start here
./hdblcm --action=<action> [options]  # command-line (non-interactive) form
./hdblcm --list_systems
```

**Documented actions** include **[G]**: `install`, `update_components`, `add_hosts`, `remove_hosts`,
`add_host_roles`, `configure_internal_network`, `register_rename_system`, `unregister_system`,
`print_component_list`, `check_installation`.

```bash
# configure a dedicated internal network on a distributed system
/hana/shared/<SID>/hdblcm/hdblcm --action=configure_internal_network \
   --listen_interface=internal --internal_address=10.66.8/21
```

**Batch / unattended:** `--batch` with a **configuration file** (`--configfile=<file>`, generated via
`--dump_configfile_template`) is the reproducible way to run hdblcm, and the right approach for a
change record. Passwords can be supplied via `--read_password_from_stdin=xml` rather than the command
line — **do not put passwords in arguments**, they land in the process table and shell history.

**Adding hosts** can go through the **SAP Host Agent** rather than requiring root everywhere — see
SAP Help *Add Hosts Using SAP Host Agent* **[G]**.

> **Known issues live in SAP Note 2082466** — *Known Issues in SAP HANA Platform Lifecycle Management
> (HDBLCM)* **[G]**, updated frequently. Check it before an update, not after one fails.

---

## 4. Where the rest lives

| Topic | File |
|---|---|
| Full hdbcons command table by category, hdblcm action/option detail, worked diagnostics | [references/hana-tools-reference.md](references/hana-tools-reference.md) |

## Cross-references

- **`sap-hana-system-replication`** — `replication i`; and why `dvol shrink` is forbidden on secondaries.
- **`sap-db-command-reference`** — `HDB`, `hdbsql`, `hdbuserstore`, HANA paths and the `<sid>adm` rule.
- **`sap-space-reclaim`** — HANA crashdump/rtedump files; data-volume reclaim.
- **`sap-health-triage`** — do the ordinary checks before reaching for an expert tool.
- **`sap-troubleshooting`** — runtime dumps as an SAP-support artefact.
- **`sap-hana-xsa`** — XS Advanced operations; `hdblcm` is what installs and updates it.

---

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

| # | Source | Read |
|---|---|---|
| **[HL1]** | **SAP Note 2222218** — *FAQ: SAP HANA Database Server Management Console (hdbcons)*, v**122**, 25.07.2026, HAN-DB | **[V]** — every hdbcons statement here, including the SPS06 `-d` change, the output-directory restriction and the crash-inducing command list |
| **[HL2]** | **SAP Note 2082466** — *Known Issues in SAP HANA Platform Lifecycle Management (HDBLCM)* | **[G]** — actively maintained |
| **[HL3]** | **SAP Note 2651885** — *How to install HDBLCM from installation media when resident HDBLCM does not exist* | **[G]** |
| **[HL4]** | **SAP Note 3469115** — *SAP HANA upgrade media is not found by hdblcm*; **2876433** — `canUpgradeComponent` exception during upgrade; **2808905** — SLD registration via HDBLCM | **[G]** |
| **[HL5]** | SAP Help Portal — *Add Hosts Using the Command-Line Interface*, *Add Host Roles Using the Command-Line Interface*, *Update an SAP HANA System Using the Command-Line Interface*, *Configuring the Network for Multiple Hosts* | **[G]** |
| **[HL6]** | **SAP Notes 2410143** (`distribute e` in MDC), **2400007** (runtime dumps), **1813020** (how to generate a runtime dump), **2177064** (service restarts and crashes), **1999020** (troubleshooting when the DB is inaccessible) | **[G]** |
| **[HL7]** | Crash-related: **2599979**, **2845208**, **2616088**, **2781933** | **[G]** |

> **hdbcons output is not a stable interface.** SAP states commands *and* output structure can change
> between revisions without notice **[V]**. Never build monitoring that parses hdbcons output — use
> SQL monitoring views for anything recurring.

> **hdblcm syntax is version-specific.** `./hdblcm --help` on the actual binary is the only
> authoritative reference for your release; the actions listed here are the commonly available set.
