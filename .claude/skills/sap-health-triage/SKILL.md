---
name: sap-health-triage
description: >-
  First-response health check and triage for a NetWeaver / S/4HANA system from the OS shell — is
  it up, is it healthy, and if not, why. Uses SAPControl read-only diagnostics (GetProcessList,
  ABAPReadSyslog for SM21, ABAPGetWPTable, dev traces, CCMS alerts), sappfpar, disp+work, dpmon
  and filesystem checks. Also the out-of-band fallback when the system is jammed: sapstartsrv is
  a separate process, so sapcontrol still returns SM50/SM66, the dispatcher queues and the
  syslog when SAP GUI will not log on and RFC hangs. Use for "is <SID> up/healthy?", "all work
  processes occupied", "cannot log on to SAP", "RFC hangs", "system jammed", "PRIV mode",
  "dispatcher queue full", "why won't it start", "check the syslog / traces / work processes".
---

# SAP Health Triage

The "is it up and healthy — and if not, why?" skill. Mostly **read-only** — safe to run — but confirm
the **SID** before pointing at a system, and note that several SAPControl methods are **protected** and
may need to be permitted/authenticated (§7).

## Guardrail note

Health checks don't change state, so the full stop/delete guardrails don't apply — but still:
**Identify** the SID/host/instance before running, and treat any command that *writes* (none here) with
the repo guardrails. Reading another system's syslog/traces is still accessing that system — confirm you
have the right SID.

---

## 0. When the system is jammed — the out-of-band path

**Read this first if SAP GUI will not log on, SM50/SM21 are unreachable, or RFC calls hang.**

> ## Why `sapcontrol` still answers when the system does not
>
> **`sapstartsrv` is a separate operating-system process.** It is not an ABAP work process, it does
> not queue behind the dispatcher, and it does not need a free dialog work process to serve a
> request. It reads the instance's **shared memory** and files directly and answers over its own
> SOAP/HTTP port (`5<nr>13` / `5<nr>14`).
>
> **That is the whole reason this path exists:** when every work process is occupied and the
> dispatcher queue is full, the ABAP stack cannot answer *anything* — but `sapcontrol` can still tell
> you the work-process table, the syslog and the queue depth. It is your **out-of-band** channel, the
> equivalent of a lights-out console.

### The escalation ladder

Work **down** this ladder. Each rung depends on less of the system than the one above it.

| # | Channel | Depends on | Still works when… |
|---|---|---|---|
| 1 | **SAP GUI** — SM50, SM21, SM66, ST22 | A free **dialog work process** | Normal operation |
| 2 | **RFC** from outside | A free work process + gateway | GUI is slow but the system runs |
| 3 | **`sapcontrol`** | Only **`sapstartsrv`** | 🔑 **All work processes jammed, GUI dead, RFC hanging** |
| 4 | **`dpmon`** | Only **shared memory** on the host | `sapstartsrv` itself is unresponsive |
| 5 | **OS**: `ps`, `ipcs`, dev traces on disk | Only the OS | The instance is wedged or half-dead |
| 6 | **`sapevt`** (out-of-band *action*) | `sapstartsrv`/profile | You must trigger work without logging in |

**Rungs 3–6 are `sap-health-triage` + `sap-os-executables`.** Treat them as the *verification and
recovery* path when the normal channels are gone — not as exotic tooling.

### Rung 3 — everything you need from `sapcontrol` with the ABAP stack jammed

```bash
# as <sid>adm. Add -host/-user only if running remotely.

# 1. Are the processes even alive? (disp+work, gwrd, icman, ms)
sapcontrol -nr <nr> -function GetProcessList

# 2. THE work-process table — this is SM50 without needing SM50
sapcontrol -nr <nr> -function ABAPGetWPTable

# 3. Across every instance in the system — this is SM66 without SM66
sapcontrol -nr <nr> -function ABAPGetSystemWPTable

# 4. How deep are the dispatcher queues? (a full DIA queue is the smoking gun)
sapcontrol -nr <nr> -function GetQueueStatistic

# 5. The syslog — this is SM21 without SM21
sapcontrol -nr <nr> -function ABAPReadSyslog

# 6. Traces, without needing a filesystem path
sapcontrol -nr <nr> -function ListDeveloperTraces
sapcontrol -nr <nr> -function ReadDeveloperTrace dev_disp 0     # 0 = whole file

# 7. CCMS alerts
sapcontrol -nr <nr> -function GetAlertTree
```

**Reading `ABAPGetWPTable` when everything is jammed** — the columns that matter:

| What you see | What it means |
|---|---|
| Every **DIA** process `Running`, none `Waiting` | Genuinely saturated — find the long runners |
| Several in **`PRIV`** mode | Processes bound to a user and **not returned to the pool** — classic memory-driven jam |
| Status `Stopped`, reason **`CPIC`/`RFC`** | Blocked on an outbound call — often a dead partner system or SAProuter |
| A long-running process with the **same PID over successive calls** | A stuck process — candidate for termination |
| **`GetQueueStatistic`** DIA queue near max | Requests are piling up behind the jam |

> **`PRIV` mode is the pattern worth recognising.** A dialog process that exceeds its memory quota
> goes into private mode and stays bound to one user until the transaction ends. Enough of them and
> the instance has no usable dialog capacity while `GetProcessList` still reports everything
> "GREEN" — **the processes are running; they are just not available.** Never conclude "healthy" from
> `GetProcessList` alone during a jam.

### Rung 4 — `dpmon`, when even `sapstartsrv` will not answer

`dpmon` reads the dispatcher's **shared memory** on the host, so it does not need `sapstartsrv` at
all:

```bash
dpmon pf=/usr/sap/<SID>/SYS/profile/<SID>_<INSTANCE>_<host>
```

It is menu-driven; the work-process list and the queue statistics are the two screens that matter,
and they show the same picture as SM50/SM51 straight from memory.

> Use `dpmon` when `sapcontrol` times out or returns `DpAttachStartService failed` (SAP KBA
> **2368478**) — that error means the start service could not attach to the dispatcher, which is
> itself a finding.

### Recovery — and its guardrail

> ## 🛑 Terminating a work process is a data-affecting action
>
> Cancelling or killing a work process **rolls back whatever it was doing**, and can leave update
> records, locks or a background job in an inconsistent state. It is legitimate emergency practice,
> but it is **not** a diagnostic step.
>
> **Identify the process and capture evidence first** — `ABAPGetWPTable`, the queue statistic, and a
> trace of the offending process. Then get an explicit decision to terminate, naming the SID and the
> process. The execution discipline below applies in full: a jammed production system is exactly the
> situation where people skip confirmation and regret it.

Where the ABAP stack is reachable at all, prefer SM50 → *Cancel without core*. At OS level, killing
the PID from `ABAPGetWPTable`/`dpmon` is the blunt equivalent — the dispatcher will start a
replacement work process.

**Before you kill anything, rule out the cheap causes:**

- **Is the database up?** A hung DB looks exactly like a jammed application server. Check the DB
  layer first — `sap-db-command-reference`.
- **Is it an outbound dependency?** Work processes stuck in `CPIC`/`RFC` are waiting on *something
  else*; killing them locally fixes nothing and the jam returns.
- **Is the filesystem full?** `/usr/sap`, the DB log area, or `/tmp` filling up jams a system in ways
  that look like a work-process problem — `sap-space-reclaim`.
- **Is it a lock escalation?** Check enqueue via `GetQueueStatistic` and the enqueue log.

---

## 1. Is it up?

```bash
# UNIX (host agent copy); Windows: %ProgramFiles%\SAP\hostctrl\exe\sapcontrol.exe
/usr/sap/hostctrl/exe/sapcontrol -nr <nr> -function GetSystemInstanceList   # all instances + dispstatus
/usr/sap/hostctrl/exe/sapcontrol -nr <nr> -function GetProcessList          # this instance's processes
/usr/sap/hostctrl/exe/saphostexec -status                                   # host agent control layer
```
`dispstatus`/process colour: **GREEN** up · **YELLOW** starting/stopping · **GRAY** stopped · **RED**
error. A start is only "done" when the expected instances are GREEN. [G, T4]

---

## 2. Extract logs & traces (via SAPControl — no SAP GUI needed)

```bash
# SM21 system log (the ABAP syslog) straight from the shell:
sapcontrol -nr <nr> -function ABAPReadSyslog                     # [V, T2]
# list all instance trace files in DIR_HOME (dev_disp, dev_w*, dev_ms, dev_rd, …):
sapcontrol -nr <nr> -function ListDeveloperTraces                # [V, T1]
# read one trace file (size=0 → whole file):
sapcontrol -nr <nr> -function ReadDeveloperTrace dev_w0 0        # [V, T1]
# read an arbitrary instance log file:
sapcontrol -nr <nr> -function ReadLogFile <path> ''             # [G, T5]
```
On the filesystem these live in the instance **work directory**
`/usr/sap/<SID>/<INST><nr>/work/` (`dev_*` traces, `stderr*`, `available.log`) — the first place to look
when an instance won't come up. Trace/work-dir **cleanup** is `sap-housekeeping`, not here.

---

## 3. Work processes, queues & locks

```bash
sapcontrol -nr <nr> -function ABAPGetWPTable        # work processes, like SM50 / SAP MC  [V, T1]
sapcontrol -nr <nr> -function GetQueueStatistic     # dispatcher request queues
sapcontrol -nr <nr> -function EnqGetStatistic       # enqueue (lock) server statistics (on ASCS/SCS)
```
Watch for: all WPs in status `running`/`stopped` (hung), a growing dispatcher queue, or enqueue
lock-table saturation.

---

## 4. CCMS alerts

```bash
sapcontrol -nr <nr> -function GetAlertTree           # CCMS alert tree (RZ20-style) from the shell  [G, T5]
```

---

## 5. Validate profiles & memory — `sappfpar`

`sappfpar` is a **SAP kernel tool** that checks the profile configuration, validates shared-memory
setup, and **estimates memory requirements** — usable **while the system is down**, so it's the key tool
for *"won't start"* and *post-change* validation. [V, T3]

```bash
# check a profile: validates parameters + shared memory + estimates memory need
sappfpar check pf=/usr/sap/<SID>/SYS/profile/<SID>_<INST><nr>_<host>      # [V, T3]
# dump every parameter the kernel knows + the effective value from the profile:
sappfpar all pf=/usr/sap/<SID>/SYS/profile/<SID>_<INST><nr>_<host>
# scope to an instance / system:
sappfpar check pf=<profile> nr=<nr> name=<SID>
```
Notes [V/G, T3]: displayed values are those that become **effective after the next startup**; the `SAP:`
column shows kernel **defaults**.

> ⚠️ **If `check` keeps reporting the same error after you fixed the parameter**, it probably never read
> your profile — look for `== Checking profile: <no_profile>` on the first line. Caused by a relative
> path, a **space after `pf=`**, or omitting `pf=`; the results are then **kernel defaults**, not your
> instance. Use the full path with no space: `sappfpar check pf=/usr/sap/<SID>/SYS/profile/<profile>`,
> and cross-check with `sapcontrol -nr <nr> -function ParameterValue <param>`. (SAP KBA 2733511) [V, T3] Run `sappfpar check` **after any profile change and before restarting**
— it catches bad parameter values and insufficient memory that would otherwise fail the start. (Same
binary/args on Linux, Windows and AIX.)

---

## 6. OS-level triage

```bash
disp+work -version                     # kernel release + patch level, DB client, unicode (all OS)
dpmon pf=<profile>                      # dispatcher/WP monitor from the shell — SM50 when you CAN'T log on
# UNIX resource checks:
df -h                                   # ⚠️ FILESYSTEM FULL is the #1 "won't start / hung" cause
ps -ef | grep -E "disp\+work|ms\.sap|sapstartsrv|enserver|enq"
free -m ; top                           # memory / load
saposcol -s                             # OS collector status — no saposcol => no ST06/CCMS/EWA data at all
```
> **`dpmon` is the fallback when SM50 is unreachable** (dispatcher up, logon impossible) — SAP documents
> it exactly that way. Menu keys: `m` work processes, `q` dispatcher queue, `t` show/set per-WP trace
> level. Trace levels are **0** none · **1** errors (default) · **2** trace messages (*negligible* cost —
> enough for most troubleshooting) · **3** full data blocks (*significant* cost, only when SAP asks).
> Prefer SM50 → *Trace → Active Components*; `rdisp/TRACE` in RZ11 changes **all** processes on the
> instance. Always lower it again. (SAP KBA 3149490, SAP Note 112) [V, T6]

**Windows** equivalents: Task Manager / `Get-Service SAP*` / `wmic logicaldisk get name,freespace` for
disk, and the **SAP MMC** for the process view. `disp+work -version` and `dpmon` are identical.

---

## 7. "Won't start" triage checklist

Work top-down; each line is the check and the tool:

1. **Control layer down?** `saphostexec -status`; `sapcontrol … GetProcessList` unreachable → start
   `sapstartsrv` / the host agent first.
2. **Filesystem full?** `df -h` on `/usr/sap`, `/sapmnt`, the DB and log filesystems — full `work`/log
   dirs block startup. → `sap-housekeeping`.
3. **Database down?** app servers (PAS/AAS) need the DB → check via
   [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
4. **Bad profile / not enough memory?** `sappfpar check pf=<profile>` (§5).
5. **Ports in use / wrong?** dispatcher `32<nr>`, gateway `33<nr>`, ICM `8xxx`, message server `36<nr>` —
   `netstat`/`ss` for conflicts.
6. **What does the trace say?** `ReadDeveloperTrace dev_disp 0` / `dev_w0` (§2), or the work dir directly.
7. **Kernel mismatch after a patch?** `disp+work -version`.

---

## 8. Security: protected web methods

Many SAPControl methods (`ABAPReadSyslog`, `ABAPGetWPTable`, `ReadDeveloperTrace`, …) are **protected**
by default and governed by the profile parameter **`service/protectedwebmethods`** (SAP Note 1439348).
Protected methods require an authenticated call (e.g. `-user <sidadm> <password>`), or must be explicitly
allow-listed for monitoring. Check with:
```bash
sapcontrol -nr <nr> -function AccessCheck <FunctionName>     # is this method permitted?
```

## Cross-references

- **Start/stop the system** (and the order): [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
- **Database up/health:** [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
- **Clean up full work/trace/log dirs** found here: `sap-housekeeping`.
- **Full `sapcontrol -function` list** (how to get the definitive per-kernel set via `--help`, plus the
  category map marking which functions are read-only vs state-changing), the read-only diagnostic
  catalog and the `service/protectedwebmethods` detail:
  [references/diagnostics-catalog.md](references/diagnostics-catalog.md).
- **`sap-kernel-patch`** — during a Rolling Kernel Switch, `dpmon` must be started from the **local instance** directory, not the central `exe`.
- **`sap-nw-java-pi`** — the AS Java counterpart of §0: `J2EEGetProcessList2` (GetProcessList GREEN is not "Java is up"), jcmon, and the telnet shell on `5<nr>08`.
- **`sap-client-copy-accelerator`** — the same diagnose-the-DB-before-blaming-it discipline, applied to a stalled client copy.
- **`sap-support-case`** — gather the evidence here first; a case that shows what was ruled out is triaged far faster.

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

- **[T1]** *Log and Trace Information for System Start and Stop* — SAP S/4HANA Technical Operation
  curriculum. **[V]** `ABAPGetWPTable` (=SM50), `ListDeveloperTraces` (trace files in `DIR_HOME`),
  `ReadDeveloperTrace <file> <size>` (size 0 = whole file).
  https://learning.sap.com/courses/technical-implementation-and-operation-i-of-sap-s-4hana-and-sap-business-suite/log-and-trace-information-for-system-start-and-stop
- **[T2]** `ABAPReadSyslog` (SM21 syslog) + restriction via `service/protectedwebmethods` — **SAP Note
  1439348** (protected web methods of sapstartsrv). https://me.sap.com/notes/1439348
- **[T3]** `sappfpar` (`check pf=<profile>`, `all`, `nr=`/`name=`; validates params + shared memory +
  memory estimate; usable while the system is down) — SAP kernel tool; **SAP KBA 2733511**.
  https://me.sap.com/notes/2733511
- **[T4]** `GetProcessList` / `GetSystemInstanceList` / status colours — *Starting and Stopping SAP
  Systems Using SAPControl* (see sap-system-lifecycle §Sources).
- **[T5]** *How to use the SAPControl Web Service Interface* — SAP NetWeaver Server Infrastructure
  (function reference: `GetAlertTree`, `ReadLogFile`, `GetQueueStatistic`, `EnqGetStatistic`, …). [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): SAP Note 1439348 for the exact
`service/protectedwebmethods` default list and syntax, and KBA 2733511 for `sappfpar check` behaviour.
