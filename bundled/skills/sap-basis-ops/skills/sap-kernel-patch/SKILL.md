---
name: sap-kernel-patch
description: >-
  Patch the SAP kernel and update the SAP Host Agent on Linux/Windows/AIX — version assessment,
  the manual swap (stop → back up exe → SAPCAR extract SAPEXE/SAPEXEDB → saproot.sh → start →
  verify), Host Agent self-upgrade, rollback, and which archives you actually need:
  SAPEXE/SAPEXEDB exist only for SP Stack Kernels, everything between is a cumulative hotfix
  (DW.SAR, LIB_DBSL.SAR, TP.SAR). Covers Rolling Kernel Switch — the separate-ASCS prerequisite,
  StoC.xml, the mandatory cluster switch, no Java/dual-stack. Use for "patch the kernel",
  "kernel upgrade", "update disp+work", "update the host agent", "rolling kernel switch", "RKS",
  "SP Stack Kernel", "which DW.SAR do I need".
---

# SAP Kernel Patch & Host Agent Update

Two independent operations:
- **Kernel patch** — swap the SAP executables to a higher patch level (**requires instance downtime**).
- **Host Agent update** — update `/usr/sap/hostctrl` (SID-independent, **no SAP-system downtime**).

> **Guardrail — kernel swap is a controlled change with a rollback.**
> - **Right binary or it won't start:** match **kernel release + patch level + platform + Unicode + DB**
>   (the DB-dependent part). Wrong platform/Unicode = dead instance.
> - **Back up the current `exe` directory first** — that's your rollback.
> - **UNIX: run `saproot.sh <SID>` after extracting** — restores root/setuid bits; the instance won't
>   start without it. (The most-forgotten step.)
> - Downtime: stop the instance(s) before replacing files (they're locked while running).
> - Identify SID/host/OS/DB → classify PRD → preview → confirm (typed for PRD) → step → verify.
> - **Claude does not download** — the SAP Software Center login is yours; Claude tells you exactly which
>   `.SAR` files to get.

Verification legend: **[V]** verified against the live help.sap.com page during authoring · **[G]** cited
to the official guide/Note.

---

## 1. Assess current versions (read-only, safe)

```bash
disp+work -version            # kernel release, patch level, Unicode, DB client   [G, KP2]
# also: SM51 → Release info, or System → Status in SAP GUI
/usr/sap/hostctrl/exe/saphostexec -version    # Host Agent version                [V, HA1]
```

---

## 1a. Which files do you actually need?

**This is where most kernel work goes wrong**, and it is not about the swap procedure — it is about
picking archives. From **SAP Note 3628821 — *FAQ on Patching SAP Kernel*** (25.09.2025) **[V]**.

**Two words SAP uses precisely** — get them right and the rest follows **[V]**:

| Term | Meaning | Example |
|---|---|---|
| **Upgrade** | Change the kernel **release** | 7.53 → 7.54 |
| **Update** | Higher **patch level** within the same release | 7.54 PL 413 → PL 600 |

### SP Stack Kernel vs hotfix — the distinction that decides your files

> ## 🔑 `SAPEXE.SAR` / `SAPEXEDB.SAR` exist **only for SP Stack Kernels**
>
> *"installation files SAPEXE.SAR and SAPEXEDB.SAR are provided only for the SP Stack Kernel"* — e.g.
> PL 100, 200, 300. **[V]**
>
> Everything **between** stack kernels is a **hotfix**, shipped as smaller archives — `DW.SAR`,
> `SAPWEBGUI.SAR`, `LIB_DBSL.SAR`, `TP.SAR`. These *"correct a specific part of the kernel without
> touching the entire kernel installation and are therefore **safer to apply**."* **[V]**

**Consequences you will hit in practice** **[V]**:

- **You cannot upgrade directly to a hotfix patch level using SAP tools.** Go to the latest SP Stack
  Kernel first, *then* apply the hotfix on top. Wanting 7.93 PL 432 means: reach PL 400 (stack), then
  apply the PL 432 hotfix.
- **"The SAPEXE files for PL 416 are missing"** is not an error — they were never published. Only
  stack levels get them.
- **Only the *latest* hotfix patch level is downloadable**, because kernel patches are **cumulative**.
  If a correction note names PL 318 and only PL 326 is on offer, **take PL 326** — it contains PL 318's
  fix. **[V]**
- **`SAPWEBGUI.SAR` can only go on top of the latest SP Stack Kernel.** Need a WebGUI correction
  without a stack update? You must apply the **bigger `DW.SAR`** instead. **[V]**

### Database-dependent or not

| Archive | Kind | Where in Software Center **[V]** |
|---|---|---|
| `SAPEXE.SAR`, `DW.SAR` | **DB-independent** | Under *Database independent* for your OS — same for every DB |
| `SAPEXEDB.SAR`, `LIB_DBSL.SAR` | **DB-dependent** | Select your **database** alongside the OS |

### Reading a correction note

To fix a specific problem **[V]**: the note's **Support Package Patches** section gives the lowest
patch level containing the correction; its **Solution** section names the archive, e.g. *"This
correction is delivered with the following kernel archives: hotfix - file `dw.sar`"*. If the latest
**SP Stack Kernel** already includes that PL, take the stack kernel; otherwise take the latest hotfix.

> **Current SP Stack Kernel levels live in SAP Note 2083594** — *SAP Kernel Versions and SAP Kernel
> Patch Levels*. **[V]** Check it rather than guessing which PL is "latest".

**Upgrading a release may drag other components:** the **IGS** may need a compatible version
(SAP Note **1491848**) and occasionally the **Web Dispatcher** too (SAP Note **908097**). **[V]**

> **Finding and downloading these files is `sap-software-download`'s job** — it resolves a component
> to exact filenames, sizes and SHA-256 from the Software Center's own OData service, and can
> download with X.509 client-certificate auth. Use it rather than hand-navigating the catalogue.
> → [sap-software-download](../sap-software-download/SKILL.md)

---

## 2. Kernel patch — step by step

The kernel lives in the **central exe** dir — UNIX `/sapmnt/<SID>/exe/uc/<platform>` (e.g.
`linuxx86_64`, `rs6000_64` on AIX); Windows `\\<host>\sapmnt\<SID>\SYS\exe\uc\<platform>`. On start,
**`sapcpe`** copies it to each instance's local `exe`. It ships in two parts: **`SAPEXE.SAR`** (DB-independent)
and **`SAPEXEDB.SAR`** (DB-dependent, matched to your `dbms_type`). [G, KP1]

1. **Assess** — `disp+work -version` (note release/PL/Unicode/DB/platform).
2. **Acquire** — decide **stack kernel vs hotfix** first (§1a), then resolve exact filenames with
   [sap-software-download](../sap-software-download/SKILL.md). For a stack update:
   `SAPEXE_<PL>.SAR` + `SAPEXEDB_<PL>.SAR` matched to release/platform/DB, plus any add-on archives
   (`dw.sar`, `lib_dbsl.sar`, IGS). For a hotfix: the specific archive named in the correction note.
   SAP Notes **19466** (download procedure) and **3628821** (which file). [V]
3. **Stop** the instance(s): `sapcontrol -nr <nr> -function StopSystem`
   ([sap-system-lifecycle](../sap-system-lifecycle/SKILL.md)). DB can stay up.
4. **Back up** the current exe: `cp -pr <exe-dir> <exe-dir>.bak_<date>` (Windows: copy the folder). ← rollback.
5. **Extract** into the central exe with SAPCAR — DB-independent first, then DB-dependent, then the rest: [G, KP1]
   ```bash
   SAPCAR -xvf SAPEXE_<PL>.SAR   -R /sapmnt/<SID>/exe/uc/<platform>
   SAPCAR -xvf SAPEXEDB_<PL>.SAR -R /sapmnt/<SID>/exe/uc/<platform>
   # then any dw.sar / lib_dbsl.sar / igsexe.sar the same way
   ```
6. **UNIX only — fix ownership/permissions:** run `saproot.sh <SID>` from the exe dir (restores
   root-owned/setuid binaries). Windows: the service/installer handles this. [G, KP1]
   > ⚠️ **SAP on ASE:** replacing the kernel resets the **SUID bit on `sybctrl`**, and without it
   > `startdb` cannot switch to `syb<sid>` — so the database fails to start *after* an otherwise clean
   > patch. Either restore the SUID bit, or have the `syb<sid>` password in secure storage (kernel
   > **PL 327 for 7.20**+); note a `startdb` invoked from a **daemon**/start profile still needs the SUID
   > bit. **SAP Note 1796535** — see [sap-db-command-reference → ASE](../sap-db-command-reference/references/sap-ase.md). [V, KP4]
7. **Start:** `sapcontrol -nr <nr> -function StartSystem` — `sapcpe` refreshes each instance's local exe.
8. **Verify:** `disp+work -version` shows the new patch level; `GetProcessList` GREEN; scan `dev_disp`
   ([sap-health-triage](../sap-health-triage/SKILL.md)).

**Rollback:** stop → restore `<exe-dir>.bak_<date>` → `saproot.sh <SID>` (UNIX) → start → verify.

---

## 3. Host Agent update — step by step (no SAP downtime)

The Host Agent (`saphostexec`, `saphostctrl`, `sapstartsrv`) is one per host, runs as **root** (UNIX) /
the SAPHostExec service (Windows), independent of any SID.

**Recommended — self-upgrade (no manual extract):** run from the **existing** hostctrl dir: [V, HA1]
```bash
# UNIX (as root):
/usr/sap/hostctrl/saphostexec -upgrade -archive <path>/SAPHOSTAGENT<PL>.SAR -verify
# Windows:
%ProgramFiles%\SAP\hostctrl\saphostexec -upgrade -archive <path>\SAPHOSTAGENT<PL>.SAR -verify
```
`-verify` validates the package against SAP's digital signature. It stops itself, upgrades, and restarts. [V, HA1]

**Manual alternative:** `saphostexec -stop` → `SAPCAR -xvf SAPHOSTAGENT<PL>.SAR -R /usr/sap/hostctrl/exe`
→ `./saphostexec -install` → start. [G, HA2]

**Verify:** `/usr/sap/hostctrl/exe/saphostexec -version` and `saphostexec -status`. [V, HA1]

---

## 4. SAPCAR quick reference

```bash
SAPCAR -tvf <archive>.SAR                 # list contents (check before extracting)
SAPCAR -xvf <archive>.SAR -R <dest-dir>   # extract to <dest-dir>
SAPCAR -cvf <archive>.SAR <files>         # create
```
SAPCAR itself is a standalone executable (download the matching platform build).

---

## 4a. Rolling Kernel Switch (RKS) — patching without downtime

**Source: SAP Note 953653 — *Rolling Kernel Switch*** **[V]**, read directly.

The whole of §2 assumes downtime. **RKS is how you avoid it**: application servers are given the new
kernel **one after another** rather than all at once.

> ## 🛑 The prerequisite that disqualifies many systems
>
> *"For the RKS procedure to work, you must be able to stop each individual application server
> without the availability of the overall system being affected. **In the case of an application
> server instance with the central services enqueue and message server (conventional ABAP central
> instance), this prerequisite is not fulfilled.**"* **[V]**
>
> **You need a separate ASCS instance** — enqueue + message server in their own instance containing
> no application server. A classic central instance cannot do RKS. Check this before planning
> anything.

### Manual or automatic, by release **[V]**

| Release | Procedure |
|---|---|
| **7.2x** | **Manual** RKS, driven by a `StoC.xml` compatibility file |
| **7.4x and later** | **Automatic** RKS — triggered from SAP MMC, or `sapcontrol` `UpdateSystem` |

### RKS compatibility — the concept underneath

Because instances temporarily run **different kernel patch levels side by side**, those levels must be
**RKS-compatible**. **[V]**

- **7.4x+ automatic:** the procedure **checks compatibility itself** when switching patches.
- **7.2x manual:** compatibility is declared in **`StoC.xml`** (Statement of Compatibility), copied
  into the ASCS instance's `$DIR_HOME` — or pointed at with `ms/stoc_file_location` (which needs a
  message-server restart). The message server picks it up automatically.
  > ⚠️ **A StoC is only valid for about six months.** Download a current one if there is a long gap
  > between fetching the kernel and running the RKS. **[V]**
  > On **System z**, convert after copying: `chtag -t -c ISO8859-1 StoC.xml`. **[V]**

> **SAP does not support long-term operation with mixed patch levels.** Get every instance to the
> same patch number **as soon as possible** — mixed operation is a transition state, not a
> configuration. **[V]**

### What RKS does *not* support **[V]**

| | |
|---|---|
| **Java and dual-stack** | *"The automated RKS procedure as of Release 7.4x does **not** support any Java or dual-stack systems."* A Java AS stores no version information when logging on to the message server, so runtime compatibility cannot be checked. Pure-Java/dual-stack instances *may* run mixed levels if RKS-compatible, but there is no automation and no safety net. |
| **Conventional central instance** | See the prerequisite above. |

### The ASCS instance itself

The ASCS is **unaffected** by the rolling pass over the application servers — patching it means
stopping and restarting it. **Because enqueue replication is in use, that happens without losing the
lock table**, so without downtime. **[V]**

> ⚠️ **Under an HA solution, stop and restart the ASCS via a *cluster switch*.** *"Otherwise, all
> entries in the enqueue lock table are lost when you stop and restart the instance on the same
> host."* **[V]** This is the single most damaging RKS mistake — it converts a zero-downtime
> operation into lost locks.

RKS does **not require** an HA solution to restart the ASCS, and **can** be used alongside an active
one *provided the HA solution has implemented RKS correctly* — SAP Note **2077934**. Platform
specifics: **2254173** (Linux/Pacemaker), **2199317** (Windows Failover Cluster), **2131873** (z/OS).

### Operational details worth knowing **[V]**

- **Each instance needs its own `exe` directory** if instances with different patch numbers run on the
  same host (`/usr/sap/<SID>/<instance>/exe`). Profiles, scripts and environment variables must be
  adjusted — SAP Note **1104735**. With `sapcpe` this is the standard modern layout.
- **Use a soft shutdown** for each instance so logged-on users are not disrupted while it drains.
- **Monitor with SM51** — RKS status is displayed there (prerequisites in SAP Note **1655182**).
- **RKS can also switch DCK releases** on 7.4x+, not just patch levels — SAP Note **1872602**.
- **Testing trick:** RKS compatibility lets you run a new kernel on **one instance only** to try it
  before committing. SAP recommends doing so **for a short period only**. **[V]**

> ## ⚠️ While RKS is active, start `dpmon` from the *local instance* directory
>
> *"If the RKS is active, the monitoring tools that depend on the design of the shared memories (for
> example, `dpmon`) must be started from the **local instance directory**. This is not the case with
> standard settings because the environment variable `PATH` usually points to the central directory
> (`DIR_CT_RUN`)."* **[V]**
>
> A `dpmon` from the central `exe` may read shared memory with the *wrong* kernel's layout. Directly
> relevant to the out-of-band diagnostics in **`sap-health-triage` §0** — during an RKS, the fallback
> tool needs the right path.

**Load balancing:** `lg/rks_strategy=prefer_restarted` makes the Web Dispatcher favour already-restarted
instances during an RKS — SAP Note **1939311**.

---

## 5. For larger updates → SUM / SPAM (pointer)

This skill is the **standalone kernel/Host-Agent swap**. For bigger, orchestrated changes use SAP's tools —
this skill does not reimplement them:

| Tool | Use for |
|------|---------|
| **SUM** (Software Update Manager) | Support Package Stacks, EHP/release upgrades, combined **kernel + SP**, and **DMO** (update + DB migration, e.g. to HANA) — the orchestrated path, handles downtime phases |
| **SPAM / SAINT** | ABAP **Support Packages** / **Add-Ons** inside the system (uses `tp`/`R3trans` underneath — see [sap-transport-mgmt](../sap-transport-mgmt/SKILL.md)); update SPAM first |

Use a standalone kernel swap (this skill) for a quick kernel patch; use **SUM** when the change is an SP
stack / upgrade / DB migration.

## Cross-references

- **Stop/start & order:** [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
- **Verify / troubleshoot after patch:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Kernel directory & `sapcpe` layout + SAR file map:** [references/kernel-layout.md](references/kernel-layout.md).
- **Find & download the archives:** [sap-software-download](../sap-software-download/SKILL.md) —
  resolves exact filenames, sizes and SHA-256; supports scripted download with certificate auth.
- **RKS diagnostics & the jammed-system fallback:** [sap-health-triage](../sap-health-triage/SKILL.md) §0
  — note the `dpmon` path caveat during an RKS.
- **HA context for RKS** (ASCS/ERS, cluster switch): the six database HA/DR skills, and
  [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md) for ERS start/stop ordering.

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
**Added for file selection and RKS** (fetched and read during this update):

| # | Source | Read |
|---|---|---|
| **[KP5]** | **SAP Note 3628821** — *FAQ on Patching SAP Kernel*, v1, 25.09.2025, BC-CST | **[V]** — SP Stack Kernel vs hotfix, why SAPEXE/SAPEXEDB are absent for non-stack levels, cumulative hotfixes, DB-dependent vs independent, upgrade vs update |
| **[KP6]** | **SAP Note 953653** — *Rolling Kernel Switch*, v19, BC-CST | **[V]** — ASCS prerequisite, manual 7.2x vs automatic 7.4x, StoC.xml and its 6-month validity, Java/dual-stack exclusion, cluster-switch rule, dpmon path caveat |
| **[KP7]** | **SAP Note 2083594** — *SAP Kernel Versions and SAP Kernel Patch Levels* (current SP Stack Kernels) | **[G]** |
| **[KP8]** | **SAP Note 2077934** — RKS in HA environments; **2254173** (Linux/Pacemaker), **2199317** (Windows Failover Cluster), **2131873** (z/OS) | **[G]** |
| **[KP9]** | **SAP Note 1104735** — instance-specific `exe` directory; **1655182** — SM51 RKS status; **1872602** — RKS across DCK releases; **1939311** — `lg/rks_strategy` | **[G]** |
| **[KP10]** | **SAP Note 1491848** — IGS version compatibility; **908097** — Web Dispatcher releases/patches | **[G]** |

> **Note 3628821 is version 1 (Sept 2025)** and SAP invites additions — re-read it before a complex
> patch decision. **Note 953653 is version 19 (2016)**: the RKS *concept* is stable, but check the
> platform-specific HA notes **[KP8]**, which are far newer, for how RKS behaves in your cluster.


- **[KP1]** SAP kernel structure (`SAPEXE.SAR` DB-independent + `SAPEXEDB.SAR` DB-dependent), `SAPCAR -xvf …
  -R <exe>`, and post-extract `saproot.sh <SID>` — SAP kernel patching process; download per **SAP Note
  19466** (*Downloading SAP kernel patches*). https://me.sap.com/notes/19466
- **[KP2]** `disp+work -version` / SM51 / System → Status — kernel version verification (help.sap.com).
- **[HA1]** *Upgrading SAP Host Agent Without Extracting the SAPHOSTAGENT Archive* — SAP Help Portal. **[V]**
  `saphostexec -upgrade -archive <SAPHOSTAGENT<PL>.SAR> -verify` from the hostctrl dir; `saphostexec -version`.
  https://help.sap.com/docs/host-agent/sap-host-agent-doc/upgrading-sap-host-agent-without-extracting-saphostagent-archive
- **[HA2]** *Manually Upgrading SAP Host Agent on UNIX / Windows* — SAP Help Portal (stop → SAPCAR extract →
  `saphostexec -install`).
- **[HA3]** **SAP Note 1031096** — *Installing / upgrading Package SAPHOSTAGENT*. https://me.sap.com/notes/1031096
- **[KP4]** **SAP Note 1796535** — *SYB: Start and stop database without SUID bit for sybctrl*. **[V]**
  *"After changing the kernel executables, it is required to set the SUID bit for sybctrl. Otherwise the
  startdb command will not work correctly."* https://me.sap.com/notes/1796535
- **[SUM]** *Software Update Manager (SUM)* and *SPAM/SAINT* — SAP Software Logistics documentation
  (help.sap.com).

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): SAP Note 19466 for the current download
paths, the kernel release note for your target patch level, and SAP Note 1031096 for Host Agent specifics.
