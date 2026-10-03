---
name: sap-housekeeping
description: >-
  Keep a SAP system's logs, traces, spool, job logs, ABAP dumps, audit logs and work directory
  from filling the filesystem — via the standard reorganization jobs (RSBTCDEL2, RSPO1041,
  RSSNAPDL, RSBDCREO …) and safe OS-level cleanup, on Linux/Windows/AIX. Use for "clean up
  logs/traces", "/usr/sap is full", "reorg spool/jobs/dumps", "housekeeping jobs", "delete old
  work-dir files", "audit log cleanup".
---

# SAP Housekeeping (logs / traces / spool / jobs / filesystem)

Two layers: **ABAP-side reorg jobs** (the correct, retention-aware way — §1) and **OS-side file cleanup**
(§3, for what the jobs don't cover). DB log/trace cleanup is delegated to
[sap-db-command-reference](../sap-db-command-reference/SKILL.md) (§6).

> **Guardrail — deletion is destructive and sometimes compliance-bound.**
> Identify SID/host → classify PRD → **preview what will be deleted and how far back** → confirm (typed
> for PRD) → delete → verify. Specific hazards, do NOT skip:
> - **Audit logs are often legally required** — check retention with security/auditors before deleting (§4).
> - **Never delete DB logs/archives that aren't backed up** — data-loss risk (§6).
> - **Prefer the standard reorg jobs** (they honour configured retention) over manual `rm`.
> - Never `rm` a **live** trace of a running instance.

---

## 1. The standard reorganization jobs (the right way) — SAP Note 16083 [G, K1]

Schedule these in **SM36** ("Standard jobs" button auto-creates them). They delete by **age/retention**,
not blindly. ABAP-side, so OS-independent.

| Job name | Report | Cleans | Frequency |
|----------|--------|--------|-----------|
| `SAP_REORG_JOBS` | `RSBTCDEL2` | old background **job logs** (SM37) | daily |
| `SAP_REORG_SPOOL` | `RSPO1041` (improved `RSPO0041`) | old **spool** requests (SP01) | daily |
| `SAP_REORG_ABAPDUMPS` | `RSSNAPDL` | old **ABAP short dumps** (ST22) | daily |
| `SAP_REORG_BATCHINPUT` | `RSBDCREO` | old **batch-input** sessions (SM35) | daily |
| `SAP_REORG_JOBSTATISTIC` | `RSBPSTDE` | old job **statistics** | monthly |
| `SAP_REORG_UPDATERECORDS` | `RSM13002` | old **update** records (SM13) | daily |
| `SAP_COLLECTOR_FOR_PERFMONITOR` | `RSCOLL00` | collects/reorgs performance stats (ST03) | hourly |
| `SAP_REORG_XMILOG` | `RSXMILOGREORG` | external management interface log | weekly/monthly |

- `RSBTCDEL2`: run by the **batch administrator** → reorganizes **all** clients; otherwise current client
  only. [K1]
- `RSPO1041`: set the retention/age in its variant. Also run spool/**TemSe** consistency regularly:
  `RSPO1043` (spool) and the TemSe check (SP12 / SAP Notes 48400, 130978). [K2]

---

## 2. Spool & TemSe consistency

```
SP12  → TemSe consistency check & reorg (temporary sequential objects)
RSPO1043 → spool consistency check
```
Inconsistent TemSe/spool is a common cause of a spool filesystem/table growing despite `RSPO1041`. [K2]

---

## 3. OS-level cleanup — the instance work directory

Work directory: `/usr/sap/<SID>/<INST><nr>/work/` (Windows: `…\work\`). Safe-to-remove candidates when a
filesystem is filling, **oldest first, and never the currently-active file**: [G, K4]

| Pattern | What it is | Safe to delete? |
|---------|-----------|-----------------|
| `*.OLD` | previous traces, re-created on each restart | ✅ yes |
| `core`, `core.<pid>` | crash core dumps | ✅ after capturing for analysis |
| old `dev_w*`, `dev_rfc*`, `dev_rd` | rotated work-process/RFC/gateway traces | ✅ old ones; not the active |
| `stderr<n>` | per-start stdout/stderr | ✅ old ones |
| `dev_disp`, `dev_ms`, `dev_icm` (current) | live dispatcher/msg/ICM traces | ⚠️ **reset via SM50/SMGW**, don't `rm` while running |

Reset traces cleanly from the app rather than deleting the active file: **SM50** (work process traces),
**SMGW** (gateway). Also check `/sapmnt/<SID>/global` for old `WF_LOG_*` workflow files.

## 4. Security audit log  ⚠️ retention/compliance

Audit data is held either as files (`*.AUD` under the `DIR_AUDIT`/`FN_AUDIT` path, typically
`/usr/sap/<SID>/<INST><nr>/log/`) **or in the database**. Delete via the SAL tools, **not** blind `rm`: [G, K3]
```
RSAU_ADMIN  → reorganize / archive the audit log (current, SAP_BASIS 7.50 SP03+)
SM18        → legacy equivalent on older releases
```
Configuration is `RSAU_CONFIG` (legacy SM19); reading is `RSAU_READ_LOG` (legacy SM20). SAP's own
retention/management recommendations are in **SAP Note 3500099**; file→database storage in **3667538**. [K6]
> **Confirm the retention requirement with security/audit/compliance before deleting audit logs.** These
> are frequently required to be kept for a mandated period. This is the one cleanup that can create a
> compliance incident.

## 5. Orphaned IPC / shared memory (`cleanipc`)

After an instance crash, orphaned shared-memory/semaphore segments can block a restart. Clean them (UNIX):
```bash
cleanipc <nr> remove          # remove IPC resources of instance <nr>  ⚠️ only when the instance is DOWN
```
Run **only** when that instance is stopped — it wipes the instance's shared memory. [G, K4]

## 6. Database logs/traces → delegate

DB transaction/redo/archive logs and DB traces are cleaned with **DB tools**, not `rm`, and only **after a
successful backup**:
- see [sap-db-command-reference](../sap-db-command-reference/SKILL.md) per `dbms_type`;
- e.g. Oracle archived redo via `brarchive -sd` (after backup), Db2 archived logs, HANA log segments +
  backup-catalog housekeeping.
> **Never delete an un-backed-up transaction log** — it breaks point-in-time recovery. [G]

## 7. "Filesystem full" quick triage

```bash
df -h                                         # which FS: /usr/sap, /sapmnt, DB data, DB log, /oracle, /hana
du -sh /usr/sap/<SID>/<INST><nr>/work/* | sort -h | tail   # biggest offenders in work/
```
Then: §3 (work dir) for `/usr/sap`; §6 (DB, after backup) for the DB/log filesystems; §1 (reorg jobs) so
it doesn't refill. Cross-ref [sap-health-triage](../sap-health-triage/SKILL.md) — full FS is its #1
"won't start / hung" cause.

## Cross-references

- **DB-side log cleanup:** [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
- **What's filling it / is it healthy:** [sap-health-triage](../sap-health-triage/SKILL.md).
- **Full standard-jobs list + OS file-type map:** [references/cleanup-catalog.md](references/cleanup-catalog.md).

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

- **[K1]** **SAP Note 16083** — *Standard jobs, reorganization jobs* (the canonical list: `RSBTCDEL2`,
  `RSPO1041`, `RSSNAPDL`, `RSBDCREO`, `RSBPSTDE`, `RSM13002`, `RSCOLL00`, …). https://me.sap.com/notes/16083
- **[K2]** `RSPO1041`/`RSPO1043` spool + TemSe consistency — **SAP Notes 130978** (RSPO1041) and **48400**
  (TemSe/spool consistency). https://me.sap.com/notes/48400
- **[K3]** Security Audit Log housekeeping — SAP Security Audit Log documentation (help.sap.com);
  `RSAU_ADMIN`/`RSAU_CONFIG`/`RSAU_READ_LOG` (legacy SM18/SM19/SM20).
- **[K6]** **SAP Note 2191612** — *FAQ | Use of Security Audit Log as of SAP NetWeaver 7.50*. **[V]**
  Current transactions as of SAP_BASIS 7.50 SP03, `DIR_AUDIT`/`FN_AUDIT`, log-table reorganize/archive in
  `RSAU_ADMIN`. Related: **3500099** (managing log data / retention), **3667538** (file → database).
  https://me.sap.com/notes/2191612
- **[K4]** Work-directory / `*.OLD` / core files / `cleanipc` — SAP OS-file housekeeping (help.sap.com +
  SAP Basis operations).
- **[K5]** *Housekeeping for SAP HANA Platform* (DB-side, for `dbms_type = hdb`).
  https://help.sap.com/doc/f3dd8d9fb4ab407eb15ee4bf336ae42b/9.3/en-US/Housekeeping%20for%20SAP%20HANA.pdf

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID): SAP Note 16083 for the full current
job list + report variants, and Note 48400 for the TemSe/spool consistency procedure.
