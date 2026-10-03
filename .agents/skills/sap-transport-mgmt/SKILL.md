---
name: sap-transport-mgmt
description: >-
  Move SAP transport requests at the OS layer with tp and R3trans — add to the import buffer,
  import single requests or import all, check status, and understand the transport directory,
  unconditional modes and return codes, on Linux/Windows/AIX. STMS is the preferred front-end;
  this is the command-line layer beneath it. Use for "import a transport at OS level", "tp
  import", "tp addtobuffer / showbuffer", "R3trans", "transport won't import", "/usr/sap/trans",
  "unconditional mode".
---

# SAP Transport Management (tp / R3trans, OS layer)

`tp` is the transport control program; `R3trans` is the lower-level engine it calls. **STMS** (transaction)
is the preferred, controlled front-end — it sequences dependencies via *Import All*. Use the OS layer for
scripted buffer building, recovery, and when STMS is unavailable.

> **Guardrail — highest blast radius in the plugin.** Transports change **code, config and data** in the
> target (often PRD).
> - **Order matters** — imports must run in the buffer/release sequence; importing out of order corrupts
>   objects. Prefer STMS *Import All* (it resolves dependencies).
> - **Test through the route** (DEV → QAS → PRD); never import untested requests straight into PRD.
> - **Unconditional (`U`) modes bypass safety rules** (§4) — use only with a specific reason and approval.
> - Identify SID/host, classify PRD, **preview the buffer**, confirm (typed for PRD), import, verify RC.
> - Take a backup/snapshot before a large or unconditional import.

---

## 1. Transport directory & naming

Shared **transport directory** — UNIX `/usr/sap/trans` (NFS-shared across the domain); Windows a shared
folder (`TRANSDIR`, e.g. `\\<transhost>\sapmnt\trans`). [X3]

| Subdir | Contents |
|--------|----------|
| `bin` | **`TPPARAM`** / `TP_DOMAIN_<SID>.PFL` — the tp parameter file for all systems in the domain |
| `buffer` | per-system import buffers (what's queued for each SID) |
| `cofiles` | command/control files `K9xxxxx.<SID>` (control the import of the data file) |
| `data` | data files `R9xxxxx.<SID>` (the actual object content) |
| `log` | tp/import logs (`ALOG`, `SLOG`, `<TR>.<SID>`) |
| `tmp`, `sapnames`, `EPS`, `actlog` | temp / name / package / action logs |

Request naming: `<SID>K9xxxxx` (e.g. `DEVK900123`) → cofile `K900123.DEV`, data `R900123.DEV`.

Run tp/R3trans as **`<sid>adm`**. If tp reports `transdir not set`, `TRANS_DIR`/the profile isn't found —
pass `pf=`.

---

## 2. R3trans (the low-level engine)

```bash
R3trans -d                          # DB connect test — RC 0000 = database reachable (great health check)
R3trans -v <controlfile>            # verbose export/import per a control file
R3trans -w <logfile> <controlfile>  # write a log
```
`R3trans -d` is the fastest "can the kernel reach the DB?" check (used in triage too). tp calls R3trans
internally for the actual data movement. [X5]

---

## 3. tp — the buffer & import workflow

Always as `<sid>adm`; add `pf=<path>/TP_DOMAIN_<SID>.PFL` if the default profile isn't picked up.

```bash
# inspect the target's import buffer:
tp showbuffer <SID> pf=<TPPARAM>          # requests queued for <SID>            [X2]
tp count <SID> pf=<TPPARAM>               # how many are queued

# add a released request to the buffer (copies cofile+data if needed):
tp addtobuffer <SID>K9xxxxx <SID> pf=<TPPARAM>                                   [X2]

# import ONE request:
tp import <SID>K9xxxxx <TARGETSID> client=<nnn> pf=<TPPARAM>                     [V, X1]
#   example (from the SAP doc): tp import T11k904711 P11 U06

# import the WHOLE buffer in dependency order (what STMS Import All does):
tp import all <TARGETSID> client=<nnn> pf=<TPPARAM>                              [X1/X2]

# buffer maintenance:
tp delfrombuffer <SID>K9xxxxx <TARGETSID> pf=<TPPARAM>
tp cleanbuffer <TARGETSID> pf=<TPPARAM>
```
Windows: identical, `tp.exe` / `R3trans.exe`; the transport dir is the shared `TRANSDIR`.

> **Prefer STMS.** SAP's own guidance: build the buffer at OS level if you must, but let **STMS Import All**
> do the actual import so dependencies/sequence are handled. [X2]

---

## 4. Unconditional (`U`) modes  ⚠️

Append `U` + digit(s) to bypass specific CTS rules — powerful and dangerous. Verified meanings [V, X1]:

| Mode | Effect |
|------|--------|
| `U1` | ignore incorrect cofile status / that it was already imported (re-import) |
| `U2` | skip TADIR bracket expansion; **overwrite originals** |
| `U3` | overwrite system-dependent (originals) objects on import |
| `U6` | overwrite objects in **unconfirmed repairs** |
| `U8` | ignore table classification (delivery-class) restrictions |
| `U9` | bypass the system lock / transport-type restriction |

Combine as digits, e.g. `U126`. Use only for a known reason (e.g. re-importing after a failure) with change
approval — several of these **overwrite** or **re-import** and can damage the target if misused.

---

## 5. Return codes (check after every tp/import)  [G, X4]

| RC | Meaning | Action |
|----|---------|--------|
| **0** | OK | done |
| **4** | warnings (e.g. activation/generation warnings) | review the log; usually acceptable |
| **8** | errors (objects not imported / import errors) | inspect the import log; often needs a fix + re-import |
| **12** | fatal error (import aborted) | do not proceed; investigate |
| **16** | internal/tp error (environment, TPPARAM, transdir) | fix the tp environment |

Read the import log: `tp import` writes to `/usr/sap/trans/log/` (`SLOG`, `ALOG`, `<TR>.<SID>`); or STMS →
Import Monitor / import history. Cross-ref [sap-log-reference](../sap-log-reference/SKILL.md).

---

## 6. The transport daemon (RDDIMPDP)

Imports are driven on the target by the event-triggered background job **`RDDIMPDP`** (scheduled by
`RDDNEWPP`). If imports hang in "waiting", check/repair it:
```bash
tp checkimpdp <SID> pf=<TPPARAM>          # check the transport dispatcher on the target
```
In the system, re-schedule via **STMS → Import Overview** / report `RDDNEWPP` (SE38). [G]

---

## Cross-references

- **Import logs / where they live:** [sap-log-reference](../sap-log-reference/SKILL.md).
- **DB reachable? (`R3trans -d`) / won't-start triage:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Restart after kernel/transport-tool changes:** [sap-system-lifecycle](../sap-system-lifecycle/SKILL.md).
- **`sap-os-executables`** — `sapevt`, `sapxpg` and `sapinst`, the other OS-level SAP executables.
- **`sap-client-copy-accelerator`** — when a client copy stalls on one huge table; also covers `R3TR TABU` transports for RSCCEXPT-excluded tables.

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

- **[X1]** *tp Options* — SAP Change and Transport System. **[V]** `tp import <request> <SID>` (example
  `tp import T11k904711 P11 U06`), unconditional modes `U1/U2/U3/U6/U8/U9`, `client=`, `pf=`.
  https://help.sap.com/doc/saphelp_snc700_ehp01/7.0.1/en-US/3d/ad5b814ebc11d182bf0000e829fbfe/content.htm
- **[X2]** *Import Process* + `tp addtobuffer` / `showbuffer` / `count` / `import all`; STMS-preferred
  guidance — SAP S/4HANA Technical Operation curriculum + SAP Help Portal (Change and Transport System).
- **[X3]** Transport directory `/usr/sap/trans` structure + **TPPARAM** in `bin` — SAP CTS documentation
  (BC-CTS).
- **[X4]** tp/import **return codes** (0/4/8/12/16) — SAP Change and Transport System documentation.
- **[X5]** `R3trans` (`-d` connect test, control files) — SAP R3trans documentation.

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): the central CTS notes (component
**BC-CTS-TLS**) for your release, and the *tp / R3trans* reference for the full option list.
