---
name: sap-hana-system-replication
description: >-
  Configure, operate, monitor and take over HANA System Replication — the full hdbnsutil set
  (sr_enable, sr_register, sr_takeover, sr_unregister, sr_changeReplicationMode, sr_state),
  replication and operation modes, multitier and multitarget, Active/Active read-enabled,
  takeover with handshake, failback, and the systemReplicationStatus / getTakeoverRecommendation
  checks. Establishes the revision BEFORE quoting a command, since syntax and defaults differ
  across HANA 1.0 SPS09-12 and 2.0 SPS01-08. Covers HA/DR provider hooks and SAPHanaSR vs
  SAPHanaSR-angi. Use for "set up HANA replication", "register secondary", "HSR takeover",
  "failback", "replication is out of sync", "logreplay vs delta_datashipping", "multitarget
  replication", "Active/Active read enabled".
---

# SAP HANA System Replication (HSR)

**Sources.** Primary: *SAP HANA System Replication Guide*, SAP HANA Platform 2.0 SPS 08,
Document Version 1.0 – 2024-11-20 **[V]** — read directly. Secondary: **SAP Note 1999880 —
FAQ: SAP HANA System Replication**, version **297**, released **18.06.2026** **[V]** — 71 questions,
component HAN-DB-HA. Marks: **[V]** verified against the live source during authoring, **[G]** cited
to a guide or Note not re-read in full.

> ## ⚠️ Read this before you type any command
>
> **HSR syntax and capability are version-gated.** The same task uses different commands, different
> defaults, or is simply unavailable depending on revision. A command copied from a blog written for
> 2.0 SPS 05 can silently do the wrong thing on 1.0 SPS 12. Establish the revision **first** — §1 —
> then use §3's matrix to confirm the feature exists on it.
>
> **Two commands in this skill are destructive to availability:** `-sr_takeover` promotes a secondary
> and `-sr_unregister` breaks replication. Both are covered by the execution discipline at the end of
> this file. Neither runs without explicit confirmation naming the SID and site.

---

## 1. Establish the version BEFORE quoting anything

```bash
# as <sid>adm on the HANA host (HANA server is Linux-only)
HDB version                      # → e.g. "version: 2.00.077.00.1710409310"
hdbnsutil -sr_state              # role, mode, site name/id — read-only, safe on both sides
```

Map the revision to a capability line:

| Revision string | Generation | Notes |
|---|---|---|
| `1.00.xxx` | HANA 1.0 | `logreplay` only from **1.00.110** (SPS 11) **[V]** |
| `2.00.0xx` | HANA 2.0 | MDC always; SPS = digits 4–5 (`2.00.077` → SPS 07) |

**MDC vs single-container.** You **cannot** set up HSR between a HANA 1.0 *single container* and a
newly installed HANA 2.0 *MDC* system (SAP Note 2101244) — both sites must run the same generation.
**[V, Note 1999880 Q15]**

---

## 2. Prerequisites — the ones that actually bite

**[V, SR Guide §Prerequisites]**

1. **Same SID *and* same instance number** on primary and secondary. Not "should" — required.
   **On scale-out, the *topology* must be identical too** — worker/standby layout and host count, not
   just the count. Non-MDC cannot replicate to MDC. **[V, Note 1999880 Q52]** → [references/hsr-scale-out.md](references/hsr-scale-out.md)
2. **Copy the system PKI SSFS key and data file** from primary to secondary *before* registering
   (HANA 2.0):
   ```
   /usr/sap/<SID>/SYS/global/security/rsecssfs/data/SSFS_<SID>.DAT
   /usr/sap/<SID>/SYS/global/security/rsecssfs/key/SSFS_<SID>.KEY
   ```
   **If XS advanced is installed, also copy the XSA SSFS pair:**
   ```
   /usr/sap/<SID>/SYS/global/xsa/security/ssfs/data/SSFS_<SID>.DAT
   /usr/sap/<SID>/SYS/global/xsa/security/ssfs/key/SSFS_<SID>.KEY
   ```
   Skipping this is the single most common cause of a registration that fails with an obscure
   authentication error.
3. **A data backup must exist on the primary** before `-sr_enable`. Initialization from a *binary
   copy* (storage snapshot, or while the primary is stopped) is only possible **as of SPS 12**; up to
   SPS 11 the secondary can only be initialized by full data shipping from the primary.
   **[V, Note 1999880 Q7]**
4. **New tenants must be backed up** to join an already-running replication. If a takeover happens
   while that tenant's initial data shipping is still running, **the tenant is not operational after
   takeover** and must be recovered from backup. **[V]**
5. **Local Secure Store (LSS):** primary and secondary need *completely independent* LSS
   installations with different file shares. If the primary has an active external KMS configuration,
   you may only register secondaries that also use LSS — not SSFS. **[V]**

**Ports.** HSR communicates on the **next instance number up**: instance `00` → the `01` port range.
A conflicting installation there yields `Address already in use ... NetworkChannelBase::bindLocal`.
**For MDC systems the port offset is 10000** (services shift from `3<nr>00` to `4<nr>00`), so **MDC
does not block instance+1**. See SAP Note 2477204. **[V, Note 1999880 Q29]**

---

## 3. Version matrix — what exists on which revision

**Check the row before you use the feature.** All **[V]** from Note 1999880 v297 / SR Guide SPS 08.

| Capability | Available from | Notes |
|---|---|---|
| `delta_datashipping` operation mode | HANA 1.0 (original) | **`preload` no longer available > 2.0 SPS 07** |
| `logreplay` operation mode | **1.00.110** (1.0 SPS 11) | Column store must generally be loaded |
| `logreplay_readaccess` | **> 2.00** | **Requires add-on licence**; restrictions in Note 2391079 |
| Log/data compression | 1.0 SPS 09 | `enable_log_compression` / `enable_data_compression`, default `false` |
| Init from binary copy / storage snapshot | **SPS 12** | Before that: full data shipping only |
| Auto-replicate parameters primary→secondary | 1.0 SPS 12 | Set on primary |
| Remote-site monitoring via `_SYS_SR_SITE_<name>` | 1.0 SPS 11 | Query from the primary |
| Active/Active (read enabled) | **HANA 2.0** | **Add-on licence** for productive use of the secondary |
| Multi-target replication (>1 secondary) | **2.0 SPS 03** | Up to 2.0 SPS 02: **one** secondary only |
| Four tiers | 2.0 SPS 03 | Used for near-zero-downtime upgrades |
| Interrupted full data shipment resumes | 2.0 SPS 03 | **< 2.0 SPS 03 restarts from scratch** |
| Invisible takeover | 2.0 SPS 03 | Default `false` on 2.0 SPS 03; **`true` > 2.0 SPS 04** |
| Secondary time travel | > 2.0 SPS 03 | `logreplay` / `logreplay_readaccess` only |
| `getTakeoverRecommendation.py` | 2.0 SPS 03 | Shipped with HANA |
| Replay backlog shown directly | > 2.0 SPS 02 | Below that it must be calculated |
| **Takeover with handshake** (`--suspendPrimary`) | **2.0 SPS 04** | Guards against split brain |
| Auto re-register secondaries to new primary | 2.0 SPS 04 | Multi-target |
| Remote-site statistics-server histories | 2.0 SPS 06 | **< 2.0 SPS 05: primary only** |

**Known defect.** On **2.00.080 – 2.00.088**, `logshipping_async_buffer_size` may not take effect and
the default is used (issue 350189). Workaround: set it again with `reconfigure`. **[V]**

---

## 4. Replication modes vs operation modes — they are orthogonal

People conflate these. They are set by different options and answer different questions.

**Replication mode** (`--replicationMode`) — *when does the primary consider a commit safe?* **[V]**

| Mode | Primary waits until | If the secondary is unavailable |
|---|---|---|
| `sync` | Secondary **received and persisted** to disk | Proceeds after an error, or after `logshipping_timeout` (default **30 s**) |
| `syncmem` | Secondary **received** (memory only) | As above |
| `sync` + **full sync** | Received and persisted | **Primary blocks** until the secondary returns |
| `async` | Does not wait | Proceeds without replicating |

> `logshipping_timeout` (`global.ini → [system_replication]`, default 30 s) is **both the check
> frequency and the threshold**, so the real timeout lands somewhere between 1× and 2× the value. **[V]**

**Full sync is an availability trade, not a tuning knob** — it guarantees no commit without shipping,
at the cost of halting the primary when the secondary is gone. Enable with
`hdbnsutil -sr_fullsync --enable` on the primary.

**Operation mode** (`--operationMode`) — *how is the secondary kept current?* See the §3 matrix. In
short: `delta_datashipping` = periodic delta data shipments (smaller secondary memory footprint,
history tables fully supported); `logreplay` = redo only (less network, **faster takeover**, no
propagation of on-disk logical corruption); `logreplay_readaccess` = `logreplay` plus read access on
the secondary (licence required).

---

## 5. The command reference — verbatim from the SR Guide **[V]**

**Every one of these runs as `<sid>adm`.** "System" = which side you run it on. Getting the
online/offline column wrong is the second most common failure after the SSFS copy.

| Command | Options | System | Online/Offline |
|---|---|---|---|
| `-sr_enable` | `[--name=<site alias>]` | **Primary** | Online |
| `-sr_disable` | — | **Primary** | Online |
| `-sr_register` | see below | **Secondary** | **Offline** |
| `-sr_unregister` | `[--id=<site id>｜--name=<site name>]` | Primary *or* Secondary | Secondary offline; primary online (to clear metadata) |
| `-sr_initialize` | `--database=<tenantDB>｜--volume=<id> [--force_full_replica]` | **Primary** | Online |
| `-sr_fullsync` | `--enable｜--disable` | **Primary** | Online and offline |
| `-sr_changeReplicationMode` | `--mode=sync｜syncmem｜async` | **Secondary** | Online and offline |
| `-sr_takeover` | `[--suspendPrimary｜--maxWriteTransactionWaitTime=<time_s>]` | **Secondary** | Online and offline |
| `-sr_resumeSuspendedPrimary` | — | **Primary** | — |
| `-sr_state` | — | Primary and Secondary | Online and offline |

**`-sr_enable`:** in **multitier and multitarget setups `--name=` is mandatory.** Run `-sr_enable` to
enable the source for *any further tier* added to the landscape. **[V]**

**`-sr_register` options** **[V]**:

```
hdbnsutil -sr_register \
  --remoteHost=<primary master host> \
  --remoteInstance=<primary instance id> \
  --replicationMode=sync|syncmem|async \
  --operationMode=delta_datashipping|logreplay|logreplay_readaccess \
  --name=<unique site name> \
  [--online]              # restart a running system automatically; irrelevant if already down
  [--force_full_replica]  # force full data shipping instead of attempting a delta
  [--withAllSecondaries]  # multitarget: re-attach a secondary to another source, keeping sub-trees
                          # — ALL sites must be online when this runs
```

> **`-sr_register` overwrites the previous register configuration.** It is also the command used to
> *change operation mode* (set `--operationMode` explicitly) and to re-sync a secondary that has
> fallen out of sync. **[V]**

**`-sr_unregister` — three legitimate scenarios only** (SAP Note 1945676) **[V]**:
1. Secondary is available but should be decoupled permanently (it becomes a normal HANA install).
2. Secondary is gone for good and the primary's metadata must be cleaned so a new one can register.
3. Restoring the original setup after a takeover in a multitier configuration.

**`-sr_takeover --suspendPrimary`** is the **takeover with handshake** (2.0 SPS 04+): it suspends the
primary to guard against data loss and split brain. `--maxWriteTransactionWaitTime=<s>` lets running
write transactions finish first (**default: no wait**). Afterwards, `-sr_resumeSuspendedPrimary`
unblocks it — **SAP HANA provides no safeguard against multiple active primaries at that point.** **[V]**

---

## 6. Monitoring — and the return codes people invert

```bash
cd /usr/sap/<SID>/HDB<nr>/exe/python_support
python systemReplicationStatus.py       # is the secondary in sync?
python landscapeHostConfiguration.py    # state of THIS database
python getTakeoverRecommendation.py     # 2.0 SPS 03+ — prefer this over reading the two above
```

**These two scripts use different, non-overlapping code ranges.** **[V]**

| `landscapeHostConfiguration.py` | | `systemReplicationStatus.py` | |
|---|---|---|---|
| `0` | Fatal — state undeterminable | `10` | No System Replication |
| `1` | **Error** — *takeover is only recommended at 1* | `11` | Error (see `REPLICATION_STATUS_DETAILS`) |
| `2` | Warning | `12` | Unknown — secondary never connected since primary restart |
| `3` | Info | `13` | **Initializing — secondary is not usable at all** |
| `4` | OK | `14` | Syncing (after connection loss or restart) |
| | | `15` | **Active** — no data loss in SYNC mode |

> SAP's own recommendation: rather than calling `landscapeHostConfiguration.py` and
> `systemReplicationStatus.py` and computing the action yourself, use
> **`getTakeoverRecommendation.py`**. **[V]**

`hdbnsutil -sr_state` is safe and read-only on both sides — it is the right first call in any triage.
**When a script consumes it, add `--sapcontrol=1`** for parseable `key=value` output instead of the
boxed layout. On multi-host and multitier systems it also prints the **host mapping**, plus
`active primary site` and `primary masters` on a secondary. **[V]**

> ⚠️ **An empty host-mapping block does not mean replication is broken.** On an offline HANA no
> mapping is shown at all, and on secondaries it cannot be shown while the database is down
> (SAP Note 2315257). Check the database is up before diagnosing the replication. **[V]**

---

## 7. Where the rest lives

| Topic | File |
|---|---|
| Full parameter reference, tuning, log retention, alerts | [references/hsr-parameters.md](references/hsr-parameters.md) |
| Multitier / multitarget, takeover, failback, upgrades, Active/Active | [references/hsr-operations.md](references/hsr-operations.md) |
| HA/DR provider hooks, SAPHanaSR vs SAPHanaSR-angi, cluster integration | [references/hsr-cluster-integration.md](references/hsr-cluster-integration.md) |
| **Scale-out**: identical-topology rule, host mapping, node-count ordering, majority maker | [references/hsr-scale-out.md](references/hsr-scale-out.md) |

## Cross-references
- **`sap-backup-recovery`** — the data backup that must precede `-sr_enable`; root-key handling
  (`hdbnsutil -backupRootKeysAndSettings`) when LSS or a KMS is in play.
- **`sap-db-command-reference`** — `HDB start/stop`, `hdbsql`, HANA paths and the `<sid>adm` rules.
- **`sap-health-triage`** — is the system up at all, before you blame replication.
- **`sap-space-reclaim`** — HANA crashdump/rtedump files, and log volumes filled by retained segments.

**The other five database HA/DR skills — different technologies, no commands transfer:**

- **`sap-ase-hadr`** — ASE HADR / Always-On (Replication Server, RMA `sap_*`).
- **`sap-oracle-dataguard`** — Oracle Data Guard (physical standby, DGMGRL).
- **`sap-db2-hadr`** — Db2 HADR (`HADR_SYNCMODE`, SA MP / Pacemaker).
- **`sap-sqlserver-alwayson`** — SQL Server Always On (availability groups, listener).
- **`sap-maxdb-ha`** — MaxDB / liveCache (Hot Standby, shadow database, cluster failover).
- **`sap-hana-xsa`** — XSA cannot be installed from scratch into an existing HSR setup, and app updates go to the primary only.
- **`sap-client-copy-accelerator`** — a bulk native load into an HSR primary replicates every row; watch secondary lag and log volume.

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
| **[SR1]** | *SAP HANA System Replication Guide*, SAP HANA Platform **2.0 SPS 08**, Document Version 1.0 – 2024-11-20 — `help.sap.com/doc/c81e9406d08046c0a118c8bef71f6bdc/2.0.08/en-US/SAP_HANA_System_Replication_Guide_en.pdf` | **[V]** — command reference §3.9, parameters §3.8, prerequisites, monitoring return codes |
| **[SR2]** | **SAP Note 1999880** — *FAQ: SAP HANA System Replication*, v**297**, 18.06.2026, component HAN-DB-HA | **[V]** — 71 questions; source of every version gate in §3 |
| **[SR3]** | **SAP Note 1945676** — correct use of `-sr_unregister` | **[G]** |
| **[SR4]** | **SAP Note 2477204** — additional ports used by system replication | **[G]** |
| **[SR5]** | **SAP Note 2101244** — HANA 1.0 single container ↔ 2.0 MDC replication restriction | **[G]** |
| **[SR6]** | **SAP Note 2391079** — restrictions for Active/Active (read enabled) | **[G]** |
| **[SR7]** | **SAP Note 2480889** — history table restrictions under `logreplay` | **[G]** |
| **[SR8]** | **SAP Note 2980989** — How-To: full data shipment for a single volume/service | **[G]** |
| **[SR9]** | **SAP Note 2400007** — log retention / `logshipping_max_retention_size`; also SAP HANA runtime dumps | **[G]** |
| **[SR12]** | **SAP Note 2315257** — no host mapping from `-sr_state` on an offline HANA | **[G]** |
| **[SR10]** | SUSE — *What is SAPHanaSR-angi?* and *How to upgrade to SAPHanaSR-angi*, `suse.com/c/` | **[V]** — angi vs classic differences |
| **[SR11]** | Red Hat — *Upgrading SAP HANA HA setup to the new generation of resource agents*, RHEL for SAP Solutions 9 | **[G]** |

> **Guide version caveat.** [SR1] is the **SPS 08** edition. Behaviour described there is not
> guaranteed for older revisions — that is exactly what §3 exists to gate. When working on a system
> below SPS 08, open the matching edition: the URL differs only in the version segment
> (`/2.0.05/`, `/2.0.07/`, …).
