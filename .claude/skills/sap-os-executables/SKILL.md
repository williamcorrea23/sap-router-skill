---
name: sap-os-executables
description: >-
  The SAP executables that cross the OS/ABAP boundary — sapevt to raise background-processing
  events from outside SAP (it needs no dialog work process, so it triggers work when nobody can
  log on), sapxpg as the controller behind SM49/SM69/DB13/SXPG_COMMAND_EXECUTE with its Y/Z
  privilege boundary and S_LOG_COM, and sapinst unattended with an inifile. Use for "sapevt",
  "raise SAP event from script", "trigger job when SAP GUI is down", "sapxpg", "SM49", "SM69",
  "external command failed", "SXPG_COMMAND_EXECUTE", "sapinst", "SWPM unattended".
  Linux/Windows/AIX.
---

# SAP executables at the OS boundary

Three tools, grouped because each one is where the **operating system and the SAP system meet** — and
each is therefore a **privilege boundary** worth treating carefully.

| Tool | Direction | What it is |
|---|---|---|
| **`sapevt`** | OS → SAP | Raise a background-processing **event** from outside the system |
| **`sapxpg`** | SAP → OS | The **external program controller** that actually runs SM49/SM69 commands |
| **`sapinst`** | — | The **installation engine** underneath SWPM |

Marks: **[V]** verified, **[G]** cited but not read in full.

---

## 0. These are also the fallback path when the system is jammed

Beyond their everyday use, two of these tools matter because they **do not need a free ABAP work
process**:

| Tool | Out-of-band role |
|---|---|
| **`sapevt`** | **Trigger work without logging in.** It talks to the message server / background scheduler, not to a dialog work process — so it can release a job when SAP GUI cannot log on |
| **`sapinst`** | Irrelevant during an incident — listed here only so the boundary is clear |
| **`sapxpg`** | ⚠️ **Not a fallback.** It is *driven by* the ABAP system (SM49/SM69/`SXPG_COMMAND_EXECUTE`), so a jammed ABAP stack means `sapxpg` cannot be invoked either |

> **Do not reach for `sapxpg` during a jam.** It is the SAP → OS direction and needs a working work
> process to start it. The out-of-band *diagnostic* channel is `sapcontrol` and `dpmon`
> (see **`sap-health-triage` §0**); `sapevt` is the out-of-band *action* channel.

**Practical use during an incident:** if the jam is caused by a flood of event-driven jobs, raising
further events with `sapevt` makes it worse — check SM37 before triggering. Conversely, if a job
*should* have started and did not, `sapevt` lets you release it without a dialog logon once capacity
is back.

---

## 1. `sapevt` — raising an event from a script

The standard way to let an external scheduler, a file arrival, or a shell script release an SAP
background job that is waiting on an event.

```bash
sapevt <EVENTID> [-p <EVENTPARM>] [-t] \
       pf=<profile>  |  name=<SID> nr=<instance_number>
```

**[G]** — SAP Help *Triggering Events from External Programs*.

```bash
# documented example
sapevt END_OF_FI_DATATRANS name=C11 nr=11
```

| Element | Meaning |
|---|---|
| `<EVENTID>` | The event name as defined in **SM62** |
| `-p <EVENTPARM>` | Optional event **parameter** — lets one event serve many jobs, each filtering on the parameter |
| `-t` | Write a trace (`dev_evt`) — the first thing to add when nothing happens |
| `pf=<profile>` | Address the system by **instance profile** path |
| `name=<SID> nr=<nr>` | Address by **SID + instance number** |

**How to think about it:** `sapevt` does not *run* anything. It raises an event; the **background
scheduler** then releases whichever jobs are defined as waiting on that event. If nothing happens the
question is usually "is a job actually scheduled *waiting for* this event?" (SM37, start condition
"After event"), not "did sapevt work?".

> ⚠️ **Anyone who can run `sapevt` on the host can trigger production background jobs.** It runs as an
> OS user, and it does **not** ask for SAP credentials. Treat shell access to `<sid>adm` accordingly —
> the event is raised with the authority of the *scheduled job*, not of the caller.

Run it as **`<sid>adm`**, so the SAP environment (profile, instance) resolves correctly.

---

## 2. `sapxpg` — the external program controller

`sapxpg` is the program the SAP system actually invokes when it needs to run something on the OS —
from **SM49** (execute), **SM69** (define), **DB13**, a job step of type "external command", or
**`SXPG_COMMAND_EXECUTE`** in ABAP. **[G]**

**Where the pieces live:**

| Piece | Where |
|---|---|
| Command definition | **SM69** (`Tools → CCMS → Configuration → External Commands`) |
| Execution | **SM49** |
| The executable | `sapxpg` in the kernel directory; started via the **SAP Host Agent / `sapstartsrv`** on the target host |
| ABAP entry point | `SXPG_COMMAND_EXECUTE` |

**Defining a command** **[G]**: a command is identified by a **name plus an operating-system type**.
Customer commands **must begin with `Y` or `Z`** — the SAP namespace is reserved and will be
overwritten by upgrades.

> **Put the program in the command, the arguments in the parameters.** SAP's guidance: enter the full
> path and name of the command (unless it is on `sapxpg`'s normal path) and **no other arguments**
> there — arguments belong in the *Parameters* field. Mixing them is a common cause of
> "command not found" style failures. **[G]**

### Why this is a security boundary

External commands run **on the OS with the rights of the SAP service user**. The authorization object
**`S_LOG_COM`** governs who may execute which command on which host — and "additional parameters"
allowed at runtime is effectively **arbitrary argument injection** unless constrained.

> ⚠️ **Treat SM69 definitions as privileged configuration.** A permissive external command plus
> `S_LOG_COM` is a route from an ABAP authorization to an OS shell. Review them the way you would
> review sudo rules — this is a standard finding in SAP security audits, and worth checking during
> the work in **`sap-security-patch`**.

### Common failures **[G]**

| Symptom | Usual cause |
|---|---|
| `Starting external program SAPXPG failed` | The target host's **`sapstartsrv` / SAP Host Agent** is not reachable or not running; or the host entry in the command is wrong |
| `Can't exec external program (No such file or directory)` | Path wrong, or arguments placed in the command field instead of Parameters; also a missing interpreter for a script |
| Wildcards behave unexpectedly | Wildcard handling in external commands is restrictive by design; see SAP KBA **1891781** *An error occurs when executing an external command* |
| Works interactively, fails from SAP | Environment difference — `sapxpg` does not inherit your login shell's profile |

The **SAPXPG - Technical and Typical issues** wiki page is the practical reference. **[G]**

---

## 3. `sapinst` — the engine under SWPM

**`sapinst`** is the executable; **SWPM** (Software Provisioning Manager) is the delivered package
that contains it. When documentation says "run SWPM", you are running `sapinst`. **[G]**

```bash
./sapinst                                          # starts the web UI on port 4237
./sapinst SAPINST_SKIP_DIALOGS=true \
          SAPINST_INPUT_PARAMETERS_URL=<inifile.xml> \
          SAPINST_EXECUTE_PRODUCT_ID=<product_id>   # unattended
```

| Thing to know | Detail |
|---|---|
| **UI** | Modern SWPM opens a **browser-based UI** (default port **4237**) rather than an X display — no `DISPLAY` needed |
| **`inifile.xml`** | Every run writes one into the install directory. It is the **reproducible record** of what was answered, and the input for an unattended re-run |
| **Install directory** | `/tmp/sapinst_instdir/...` by default — **on `/tmp`, so it can vanish on reboot.** Copy `inifile.xml` and the logs out before you lose them |
| **Logs** | `sapinst.log`, `sapinst_dev.log` in the install directory — `sapinst_dev.log` is the one with the real error |
| **Restart** | A failed step can usually be retried from the failure point rather than restarting the whole run |

> ⚠️ **`inifile.xml` can contain sensitive values.** Treat it as a credential-adjacent artefact:
> archive it deliberately, do not commit it to a repository, and do not paste it into a ticket
> unredacted.

Version currency for SWPM is covered by **`sap-software-download`** — always fetch the current SWPM
rather than reusing an old copy, because it carries the current product definitions.

---

## 4. Where the rest lives

| Topic | File |
|---|---|
| sapevt trace/diagnosis, SM69 definition detail and security review checklist, sapinst unattended flow | [references/os-executables-reference.md](references/os-executables-reference.md) |

## Cross-references

- **`sap-transport-mgmt`** — `tp` and `R3trans`, the other major OS-level SAP executables.
- **`sap-security-patch`** — review external command definitions as part of security work.
- **`sap-software-download`** — obtaining current SWPM/SAPCAR.
- **`sap-system-lifecycle`** — `sapcontrol`, `sapstartsrv`, and the Host Agent that `sapxpg` depends on.
- **`sap-log-reference`** — `dev_evt` and the work-directory traces these tools write.
- **`sap-health-triage`** — **§0 out-of-band path** when RFC/work processes are jammed; `sapcontrol` and `dpmon` are the diagnostic side of what this skill covers.

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
| **[OE1]** | SAP Help Portal — *Triggering Events from External Programs* (SAP NetWeaver) | **[G]** — `sapevt` syntax and the `pf=` / `name=` `nr=` forms |
| **[OE2]** | SAP Help Portal — *Defining External Commands* | **[G]** — the Y/Z namespace rule, command vs parameters separation |
| **[OE3]** | SAP Community Wiki — *SAPXPG - Technical and Typical issues* | **[G]** |
| **[OE4]** | **SAP KBA 1891781** — *An error occurs when executing an external command* | **[G]** |
| **[OE5]** | SAP Help Portal — Software Provisioning Manager / `sapinst` documentation; SWPM guides | **[G]** |
| **[OE6]** | Authorization object **`S_LOG_COM`** — SAP security documentation | **[G]** |

> **Coverage honesty.** This skill is **[G]** throughout, not **[V]**. `sapevt`, `sapxpg` and
> `sapinst` are documented across SAP Help pages, wiki articles and KBAs rather than in one
> authoritative command reference, and none was read end-to-end. The syntax shown is the commonly
> documented form — **confirm against the version on your host** (`sapevt` with no arguments prints
> usage) before putting it in a runbook.

> **The security framing in §2 is an operational judgement, not an SAP statement.** `S_LOG_COM` and
> the Y/Z rule are documented; treating SM69 definitions as sudo-equivalent is the conclusion this
> skill draws from them, and it is worth stating so you can weigh it yourself.
