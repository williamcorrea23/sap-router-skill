---
name: sap-ase-hadr
description: >-
  SAP ASE (Sybase) HADR / Always-On built on SAP Replication Server — the RMA command surface
  (sap_status, sap_failover, sap_materialize), setuphadr, the Fault Manager, split-brain and
  when `force` is legitimate, sync vs async, the three-node DR topology. Use for "ASE HADR",
  "Sybase high availability", "Always-On", "ASE failover", "companion server", "split-brain
  ASE", "setuphadr". NOT HANA System Replication.
---

# SAP ASE HADR (Always-On)

**Source.** *SAP ASE HADR Users Guide*, **SAP Adaptive Server Enterprise 16.0 SP04**, Document
Version 1.0 – 2022-09-16 **[V]** — downloaded and read directly. Marks: **[V]** verified against the
live source, **[G]** cited but not re-read in full.

> ## ⚠️ This is not HANA System Replication
>
> ASE HADR and HANA HSR solve the same *problem* with entirely different *technology*. Nothing in
> `sap-hana-system-replication` transfers: there is no `hdbnsutil`, no `sr_register`, no operation
> mode. **ASE HADR is built on SAP Replication Server** and is driven through the **RMA (Replication
> Management Agent)** with `sap_*` commands. Do not carry HSR vocabulary across.

> **Licence gate.** The Always-On option that provides HADR **requires the `ASE_ALWAYS_ON`
> licence**. **[V]** Without it, none of this is available regardless of version.

---

## 1. Topology — and the version gate that decides it

**[V]**

| Version | Supported topology |
|---|---|
| Before **16.0 SP03 PL03** | **Single companion only** — one primary, one companion |
| **SP03 PL03 and later** | **Three-node**: primary + companion + **disaster-recovery (DR) node** |

The two-node pair provides HA (fast, optionally zero-data-loss failover); the third **DR node**
provides geographic DR. Check the PL level before promising a customer a DR node.

**Roles:**

- **Primary** — the member where user transaction processing is allowed.
- **Companion / Standby** — holds replicated copies, available to take over.
- **DR node** — third-site disaster recovery (SP03 PL03+).
- **Fault Manager** — separate component that detects failure and drives *automatic* failover.
  **Its host must be the same platform as the HADR nodes.** **[V]**

---

## 2. Replication mode — sync vs async, and the SSD requirement

**[V]**

| Mode | Behaviour |
|---|---|
| **Synchronous** | Primary and standby stay in sync with **zero data loss (ZDL)** |
| **Asynchronous** | Lower latency impact; a failover can lose in-flight transactions |

> ⚠️ **Synchronous mode requires an SSD or other fast storage device for Replication Server.** This
> is a documented requirement, not a tuning recommendation — the Replication Server queue is in the
> commit path. **[V]**

**Automatic failover with ZDL only happens from synchronous mode.** If Replication Server was in
synchronous mode when the primary failed, the Fault Manager initiates failover automatically with
zero data loss. **[V]** In asynchronous mode, do not assume ZDL.

**Stream Replication (also called Component Interface / CI) is the only supported replication mode
in HADR.** The Replication Agent inside the primary database ships transactions to the Replication
Server on the companion. **[V]**

---

## 3. Member modes and internal states — read both

This trips people up: every member has an **external mode** (visible to other members) *and* an
**internal state** (known only to itself). A status output showing "Primary" tells you nothing about
whether it is accepting work. **[V]**

**External modes:**

| Mode | Meaning |
|---|---|
| `Primary` | Active transaction processing by user applications is allowed |
| `Standby` | Holds replicated copies; available to take over |
| `Disabled` | HADR is disabled on this member |
| `Unreachable` | **The local member cannot reach this remote member** — says nothing about the remote's real state |
| `Starting` | Member is starting |

**Internal states:**

| State | Meaning |
|---|---|
| `Active` | Normal primary state, no restrictions. **A primary is always Active after restart — provided the split-brain check passed.** |
| `Inactive` | Unprivileged connections restricted; privileged connections unrestricted. **Standby members are always Inactive.** |
| `Deactivating` | Intermediate. Gracefully terminates unprivileged transactions; `sp_hadr_admin` `timeout` bounds it. On timeout it rolls **back to Active** or **forward to Inactive** depending on whether `force` was given. |

> **`force` on a deactivating server forcibly terminates transactions from *privileged and
> unprivileged* connections alike.** **[V]**

> **The internal state is not preserved across restarts; the external mode is saved.** **[V]** So a
> restarted server can present the same mode with a different state — check both.

---

## 4. The split-brain check — and the one flag that overrides it

**[V]** The check runs at start-up when the configuration file says to start as primary, or when you
run `sp_hadr_admin primary` to promote a standby.

It connects to and queries **each configured HADR member**. If any remote member is identified as an
existing primary, promotion is refused. **Generally you cannot override this.**

**The dangerous case:** if the check **cannot connect** to one or more remote members, it *assumes
an unreachable member may be primary* and refuses promotion. That is when people reach for:

```sql
sp_hadr_admin primary, force
```

> ⚠️ **Before using `force`, verify there is no other primary server present in the group.** **[V]**
> The check is refusing precisely because it cannot rule that out. `force` does not resolve the
> ambiguity — it discards it. Two primaries means the databases can no longer be synchronized.

This is the ASE analogue of the HSR handshake problem: see
[`sap-hana-system-replication`](../sap-hana-system-replication/SKILL.md) §5 on
`-sr_resumeSuspendedPrimary`, where SAP likewise provides no safeguard against multiple primaries.

---

## 5. The RMA command surface

Commands run through the **RMA**, reached with `isql`. Frequency in the guide is a fair proxy for how
central each one is **[V]**:

| Command | Purpose |
|---|---|
| **`sap_status`** | The workhorse. Sub-forms: `sap_status path` (is the whole HADR path healthy), `active_path`, `route`, `resource`, `spq_agent`, `synchronization`, `task` |
| **`sap_failover`** | Planned failover. `sap_failover_drain_to_er` drains to external replication first |
| **`sap_set`** / `sap_set_host` / `sap_set_replication_service` | Configuration |
| **`sap_materialize`** | Materialize / rematerialize a database into replication |
| **`sap_enable_replication`** / `sap_disable_replication` | Per-database replication control |
| **`sap_update_replication`** / `sap_delay_replication` | Adjust replication behaviour |
| **`sap_teardown`** | Remove the HADR configuration |
| **`sap_host_available`** | Host reachability |
| **`sap_tune_rs`** / `sap_configure_rs` / `sap_configure_rat` | Replication Server / Agent tuning |
| **`sap_upgrade_server`** | Rolling upgrade support |
| **`sap_send_trace`** / `sap_purge_trace` | Diagnostics |

**Start every investigation with `sap_status path`** — the guide uses it as the standard "is the
system healthy and is this database actually in replication" check. **[V]**

`setuphadr` is the installation utility (driven by a `setup_hadr.rs` response file). **The HADR
system is not actually created until the software is installed on the second node** — installing on
the first node only prepares ASE and Backup Server. **[V]**

---

## 6. What HADR does *not* support — check before designing

This list kills more designs than any other page in the guide. **[V]**

- **Not supported in process kernel mode**
- **Shared disk cluster**
- **In-memory databases**
- **Third-party HA platforms** — Veritas HA, Sun Cluster, HACMP, Service Guard, etc. **HADR replaces
  them; it does not layer on top of them**
- **Multi-path replication**
- **MSDTC transaction replication**
- **LDAP as the network security mechanism** — LDAP may still be used for *client* connections to
  ASE, just not within the HADR system
- **Kerberos authentication** — supported in stream replication, **but not in HADR yet**
- **`sp_setreplicate`** (deprecated)
- Stored procedures marked for replication via a *table* replication definition
- Request functions (applied-function replication of procedures *is* supported via
  `sp_setrepproc <procedure_name>, 'function'`)

> ⚠️ **Primary and companion must match on platform, page size, default language, character set and
> sort order.** A different character set on the companion is explicitly unsupported. **[V]** This is
> the ASE counterpart of HSR's identical-topology rule.

---

## 7. Where the rest lives

| Topic | File |
|---|---|
| Installation, Fault Manager, failover procedures, rolling upgrade, SSL, monitoring | [references/ase-hadr-operations.md](references/ase-hadr-operations.md) |

## Cross-references
- **`sap-db-command-reference`** — ASE start/stop, `isql`, `$SYBASE` environment, the `sybase`/`syb<sid>` OS user.
- **`sap-backup-recovery`** — ASE dump/load; loading from an external dump into an HADR system.
- **`sap-health-triage`** — is the instance up at all before you blame replication.

**The other five database HA/DR skills — different technologies, no commands transfer:**

- **`sap-hana-system-replication`** — HANA System Replication (`hdbnsutil`, HSR).
- **`sap-oracle-dataguard`** — Oracle Data Guard (physical standby, DGMGRL).
- **`sap-db2-hadr`** — Db2 HADR (`HADR_SYNCMODE`, SA MP / Pacemaker).
- **`sap-sqlserver-alwayson`** — SQL Server Always On (availability groups, listener).
- **`sap-maxdb-ha`** — MaxDB / liveCache (Hot Standby, shadow database, cluster failover).

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
| **[AH1]** | *SAP ASE HADR Users Guide*, **SAP Adaptive Server Enterprise 16.0 SP04**, Document Version 1.0 – 2022-09-16 — `help.sap.com/doc/dd91064bd45549dfbd85b270569b872f/16.0.4.3/en-US/SAP_ASE_HADR_Users_Guide_en.pdf` | **[V]** — modes/states §8.12, split-brain §8.10, unsupported features §2.7, RMA commands §12 |
| **[AH2]** | *HADR System with DR Node Users Guide*, ASE 16.0 SP04 — `help.sap.com/doc/f0a13ab3128b4eb0a5042281050c95d8/16.0.4.0/en-US/HADR_System_with_DR_Node_Users_Guide.pdf` | **[G]** — three-node topology |
| **[AH3]** | *SAP Replication Server Configuration Guide (UNIX)*, 16.0 SP03 | **[G]** |
| **[AH4]** | SAP Help Portal — *Configure Companion Servers for Failover* (ASE 16.0) | **[G]** — the **older** `enable HA` / `enable cis` / `enable xact coordination` companion-failover feature, distinct from HADR |

> **Version caveat.** [AH1] is the **SP04** edition and states plainly that HADR does not support the
> full functionality of ASE. Behaviour below SP03 PL03 differs materially — single-companion only.
> When working on an older PL, open the matching edition; the URL differs in the version segment
> (`/16.0.3.7/`, `/16.0.3.10/`, …).

> **Two different ASE HA features exist.** HADR/Always-On (this skill) is Replication-Server-based.
> The older **companion-server failover** (`sp_companion`, requiring `enable cis`,
> `enable xact coordination` and `enable HA`) is a separate, older mechanism — **[AH4]**, marked
> **[G]** because it was not read in full. Do not mix their commands.
