---
name: sap-db2-hadr
description: >-
  IBM Db2 for LUW HADR under SAP — synchronization modes, multiple standbys and
  HADR_TARGET_LIST, VIP vs Automatic Client Reroute, cluster automation with SA MP or Pacemaker,
  takeover and the Graceful Maintenance Tool, rolling Fix Packs, Reads on Standby, and the
  non-logged operations that silently invalidate a standby. Use for "Db2 HADR", "DB6 HADR",
  "takeover", "standby database Db2", "HADR_SYNCMODE", "peer state", "automatic client reroute",
  "db2haicu", "rolling fix pack", "SQL1776N".
---

# Db2 for LUW — HADR under SAP

**Source of record.** **SAP Note 1612105 — *DB6: FAQ on Db2 High Availability Disaster Recovery
(HADR)***, version **6**, released **17.06.2025**, component BC-DB-DB6 **[V]** — fetched and read
directly. Marks: **[V]** verified, **[G]** cited but not read in full.

> **This skill is the SAP layer, not a Db2 tutorial.** Note 1612105 says so itself: *"This SAP Note
> is not an introduction to Db2 HADR. Read the IBM documentation first."* What follows is what
> changes **because it is SAP** — client connectivity, non-logged operations, maintenance procedures.

---

## 1. Synchronization modes

`HADR_SYNCMODE` takes one of four values. **[G — IBM]**

| Mode | Primary commits after logs are… |
|---|---|
| `SYNC` | written to disk on **both** primary and standby |
| `NEARSYNC` | written to disk on primary **and received into memory** on standby |
| `ASYNC` | written to local disk **and sent** to standby |
| `SUPERASYNC` | *(no wait — primary never blocks on replication)* |

`NEARSYNC` is the usual production choice: near-zero data loss without paying for the standby's disk
write in the commit path.

> **Multiple standbys change the mode silently.** With more than one standby, the configured
> `HADR_SYNCMODE` applies **only to the first (principal) standby** in `HADR_TARGET_LIST`.
> **Auxiliary standbys are `SUPERASYNC`** regardless of what you set. **[G]** Do not promise
> a customer NEARSYNC protection on standby #2 and #3.

**Standby count is version-gated:** Db2 **8.2–9.7 support one** standby; **10.1 raised this to
three**. **[G]** — see `sap-backup-recovery` §version matrix, where this is already recorded.

**Peer state** is the healthy steady state for SYNC/NEARSYNC and the precondition for several
procedures below — check it before any maintenance.

---

## 2. Client connectivity — the decision that causes data divergence

After **every** role switch the SAP application servers must reconnect to the **new** primary. There
are two ways, and SAP has a clear preference. **[V, Note 1612105]**

| | **Virtual IP (VIP)** — recommended | **Automatic Client Reroute (ACR)** |
|---|---|---|
| How | Primary binds a VIP; after takeover the VIP moves to the new primary | Db2 client knows both servers and retries the alternate |
| Behaviour | **One** destination for all connections | **Each connection decides independently** |
| Split brain | Safe — a VIP can only be bound to one server | 🛑 **Unsafe** |

> ## 🛑 Why SAP recommends VIP
>
> Note 1612105, on ACR: in a split-brain scenario where both databases accept connections, *"some
> work processes or threads might work with one database and others with the other, **causing the
> databases to no longer be consistent**."* **[V]**
>
> That is silent, per-work-process data divergence — far worse than an outage, because nothing fails
> loudly. **"With a VIP, this problem does not exist because the VIP can only be bound to one
> server."** **[V]**

**ACR is only supported by SAP when both hold** **[V]**:

1. the database server is set up using **`db2haicu` with SA MP**, **and**
2. **Reads on Standby (RoS) is not enabled.**

> **ACR + RoS is explicitly unsafe:** connections might accidentally land on the standby and *"become
> unusable for business transactions that do write operations."* **[V]** Known ACR limitations are
> collected in **SAP Note 1568539**.

---

## 3. HADR does not fail over by itself

**"HADR itself does not provide automated failover"** **[V]** — you need cluster software:

| Option | SAP Note |
|---|---|
| **Tivoli System Automation for Multiplatforms (SA MP)** — integrated with Db2 | **960843** |
| **Pacemaker** | **3100330** |

**`sapdb2cluster.sh`** (attached to Note **960843**) performs an automated cluster switch with
graceful takeover — call it with the **`switch`** option. **[V]**

**Graceful Maintenance Tool (GMT)** — SAP Note **1530812** — suspends the SAP system during a planned
takeover so the application stays up. **[V]** This is the SAP-side lever that turns a takeover from
an outage into a pause; use it for planned work.

---

## 4. Non-logged operations — how a standby goes bad quietly

HADR replays logs, so anything **not logged** does not reach the standby. Note 1612105 works through
every case and concludes SAP applications **do not** perform non-logged operations harmful to
recovery **[V]** — with exceptions worth knowing:

| Operation | SAP relevance |
|---|---|
| `NOT LOGGED INITIALLY` | Not used for business data. **SAP BW** may use it for selected temporary tables (Note 1527970) — recoverability of business content is not impaired |
| **`NONRECOVERABLE LOAD`** | Not used in production — but **`DB6CONV` lets you select it for a table conversion**. If you do: take a backup afterwards **and rebuild the HADR standbys from a backup of the primary** (Note 1513862) |
| `NOT LOGGED` LOB columns | Only Db2 EXPLAIN tables — no permanent content |
| Index pages during index build | **Controlled by `LOGINDEXBUILD`** — see below |

> **Set `LOGINDEXBUILD = ON` if you use HADR.** SAP's explicit recommendation (Note 2113429) **[V]**.
> With it **OFF** the database is still recoverable, **but index objects are marked invalid during
> HADR replay or rollforward and must be rebuilt before use** — a takeover then lands you on a
> standby whose indexes need rebuilding, exactly when you need it working.

> **Do *not* set `BLOCKNONLOGGED = YES`.** Note 1612105 *"strongly recommend[s]"* against it, because
> legitimate non-logged operations occur on objects irrelevant to recovery (Note 1523227). **[V]**

---

## 5. Stopping a standby from failing silently

> **As of Db2 12.1**, `DB2_FAIL_RECOVERY_ON_TABLESPACE_ERROR=YES` is **included in
> `DB2_WORKLOAD=SAP`**. SAP recommends setting it **manually from Db2 11.5.4**. **[V]**

It makes HADR **stop** on a tablespace error and populate `HADR_FLAGS` with the reason, instead of
leaving replication quietly broken for that tablespace. On **11.5.4 → 12.1** this is a manual
setting you must add — a genuine version-gated action item, not background reading.

---

## 6. Maintenance — the one-way version rule

**Rolling Fix Pack update** is supported and is one of HADR's better payoffs. The trap: **[V]**

> **HADR supports the standby running a *newer* Db2 level than the primary — but not the reverse.**

So after you update the standby and take over, the **new** standby (the former primary) is on an
**older** level and is **deactivated** until you update it too. That is expected, not a fault.

Outline **[V]** — full sequence in [references/db2-hadr-operations.md](references/db2-hadr-operations.md):

1. Install the Fix Pack as a new software copy on **both** servers
2. Deactivate the standby database, stop the standby instance
3. `db2iupdt` on the standby to switch software copies
4. Start the instance, activate the database
5. **Takeover** — use GMT (Note 1530812) or `sapdb2cluster.sh switch` to protect the SAP system
6. Repeat 2–4 on the new standby (former primary)
7. Optionally switch roles back
8. Run **`db6_update_db.sh`** on both, then **`db6_update_client.sh`** (both from Note **1365982**),
   then restart application servers one by one to pick up the new client

**Configuration changes** — the rule that catches people **[V]**:

| Change | Rolling? |
|---|---|
| Operating system | ✅ Rolling |
| **Db2 HADR parameters** | 🚫 **Block HADR role changes — a database outage is required** |
| Dynamic Db2 parameters | ✅ No special procedure |
| Non-dynamic Db2 parameters | ✅ Rolling |

**Version upgrade:** from Db2 **11.1** onward you can **roll standbys forward through the upgrade**
if you start from certain Db2 10.5 minimum Fix Pack levels. Otherwise the standbys must be
**rebuilt** after the upgrade. **[V]**

---

## 7. Errors worth recognising

| Error | Note |
|---|---|
| **`SQL1776N`** — *"The command cannot be issued on an HADR database"*, with a reason code | **2921425** **[G]** — usually an attempt to run something on a standby that only the primary accepts |
| Generic **HADR error codes** | **3522866** **[G]** |

---

## 8. Where the rest lives

| Topic | File |
|---|---|
| Takeover runbooks, monitoring (`db2pd -hadr`, `MON_GET_HADR`), rolling procedures, RoS, DPF/pureScale boundary | [references/db2-hadr-operations.md](references/db2-hadr-operations.md) |

## Cross-references
- **`sap-backup-recovery`** — Db2 backup/restore, log archiving, and the standby-count version matrix.
- **`sap-db-command-reference`** — `db2start`/`db2stop`, `db2` CLP, the `db2<sid>` OS user.
  **Different technologies; no commands transfer.**
- **`sap-space-reclaim`** — Db2 `FODC_*` diagnostic directories and log-archive space.

**The other five database HA/DR skills — different technologies, no commands transfer:**

- **`sap-hana-system-replication`** — HANA System Replication (`hdbnsutil`, HSR).
- **`sap-ase-hadr`** — ASE HADR / Always-On (Replication Server, RMA `sap_*`).
- **`sap-oracle-dataguard`** — Oracle Data Guard (physical standby, DGMGRL).
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
| **[D1]** | **SAP Note 1612105** — *DB6: FAQ on Db2 High Availability Disaster Recovery (HADR)*, v**6**, 17.06.2025, BC-DB-DB6 | **[V]** — VIP/ACR, non-logged operations, LOGINDEXBUILD, rolling Fix Pack, config-change rules all read directly |
| **[D2]** | **SAP Note 1568539** — *DB6: HADR - Virtual IP or Automatic Client Reroute* | **[G]** — known ACR limitations |
| **[D3]** | **SAP Note 960843** — *DB6: High Availability for DB2 using SA MP* (source of `sapdb2cluster.sh`) | **[G]** |
| **[D4]** | **SAP Note 3100330** — *DB6: Using Db2 HADR with Pacemaker Cluster Software* | **[G]** |
| **[D5]** | **SAP Note 1530812** — *DB6: Graceful Maintenance Tool* | **[G]** |
| **[D6]** | **SAP Note 2113429** — *DB6: How to set the LOGINDEXBUILD parameter* | **[G]** |
| **[D7]** | **SAP Note 1523227** — *DB6: Use of BLOCKNONLOGGED database configuration parameter* | **[G]** |
| **[D8]** | **SAP Note 1365982** — `db6_update_client` / `db6_update_db` scripts | **[G]** |
| **[D9]** | **SAP Note 1555903** — *DB6: Supported IBM Db2 Database Features* (the Db2 analogue of Oracle's Note 105047) | **[G]** |
| **[D10]** | **SAP Note 2921425** (`SQL1776N`), **3522866** (generic HADR error codes), **1513862** (DB6CONV), **1527970** (BW non-logged) | **[G]** |
| **[D11]** | **SAP Note 702175** — *DB6: Support of DB2 DPF and DB2 pureScale* | **[G]** |
| **[D12]** | IBM — Db2 HADR wiki and Db2 Knowledge Center (`hadr_syncmode`, `HADR_TARGET_LIST`, peer state) | **[G]** — IBM defines the feature; SAP Note 1612105 governs its use under SAP |

> **Note 1612105 is the entry point, not the whole story.** It explicitly defers to IBM
> documentation for the feature itself and carries only the SAP-specific deltas. For anything
> structural (log shipping internals, `db2pd -hadr` field meanings) read IBM's docs; for anything
> about *SAP under HADR*, this Note wins.

> **Version currency.** v6 was released 17.06.2025. The `DB2_FAIL_RECOVERY_ON_TABLESPACE_ERROR`
> guidance in §5 is tied to Db2 **11.5.4** and **12.1** — re-read the Note before applying it to a
> newer Db2 level.
