---
name: sap-client-copy-accelerator
description: >-
  Rescue an SAP client copy (SCC9 / SCCL / SCC7) that has stalled or is crawling on ONE huge
  table — ACDOCA, BSEG, FAGLFLEXA, MATDOC, COEP — by moving the rows database-natively instead:
  batched DELETE, then parallel INSERT...SELECT partitioned by fiscal year, on HANA (Smart Data
  Access) or Oracle (database link). Diagnoses FIRST and exhausts the supported levers before
  bypassing anything; gates cross-database access on explicit licence confirmation. Use for
  "client copy slow", "client copy stuck", "SCC9 stuck on ACDOCA", "SCCL stuck", "accelerate
  client copy", "client refresh running for days", "SDA table copy", "client copy ETA 13 hours"
  — even when the user only says the refresh will miss its window.
---

# SAP client-copy accelerator (HANA & Oracle)

**Field-proven.** Developed on a live S/4HANA QA refresh where ACDOCA (105 M rows) aborted twice in
the copy and would otherwise have taken ~13 h single-stream. Result: **~70 min remote** (cross-system
HANA SDA, ~1.59 M rows/min, ≈14× the copy) and **~6 min local** (same-tenant). Marks: **[V]** verified
against SAP documentation, **[F]** proven in the field on that refresh, **[G]** cited but not read in full.

> ## Why the copy is slow — the number that explains everything
>
> SAP's own guidance, **Note 2163425**: *"the database interface limits the throughput to
> **100 – 500 MB/hour**"*, producing *"a correspondingly longer runtime (**up to several weeks**) for
> productive clients."* **[V]**
>
> That is the copy **framework's** ceiling, not your database's. The copy ships rows through ABAP work
> processes and (for SCC9) RFC. A modern HANA or Oracle system will move the same rows one to two
> orders of magnitude faster when you let it do the work itself. **The table is not the problem; the
> transport mechanism is.**

**The one structural limit that makes this technique necessary:** the client copy parallelises
**across tables, not within one**. Once every other table is done, your last big table is a **single
stream** and no amount of extra work processes helps (Note 541311 Q4) **[V]**. That is why one table
can hold a whole refresh hostage.

---

## 0. Do these in order — do not skip to the bypass

Bypassing the framework is a legitimate expert technique, but it takes the copy's safety rails off.
Earn it:

| # | Step | Why |
|---|---|---|
| **1** | **Diagnose** — prove it is ABAP-side, not the DB (§1) | Bypassing a genuinely sick database makes things worse |
| **2** | **Exhaust the supported levers** (§2) | Faster, reversible, supported. Often enough on its own |
| **3** | **Get explicit licence confirmation** (§0a) | Cross-database access is a licence decision, and it is the user's to make |
| **4** | **Only then bypass** for the specific table (§3–§6) | Scoped to one table, with verification |

> ⚠️ **Never bypass a table you have not first proven is framework-bound.** A hung DB, a full
> filesystem, an archiver stuck, or a lock wait all *look* like "the copy is slow" and none of them
> is fixed by loading harder.

---

## 0a. Licence gate — STOP. Do not create a remote source or database link without explicit confirmation

> ## 🛑 This is a hard stop, not a caution
>
> **Do not create a remote source, a virtual table, or a database link — and do not run the bypass —
> until the user has explicitly confirmed, in their own words, that:**
>
> 1. **They are entitled** to use cross-database access on this system under its licence, and
> 2. **They understand the consequences** of being wrong — a licence audit finding, and potentially a
>    chargeable true-up.
>
> **Present the position in §0a first, then ask. Do not infer consent** from "go ahead", from the fact
> that they asked for the acceleration, or from the system being non-production. Licence exposure does
> not care which environment it happened in.
>
> **A usable form of the question:**
>
> > "This creates a `<remote source | database link>` from `<target>` to `<source>`, which is
> > cross-database access. Under **Note 581312** that is permitted for *system administration*, but
> > **not** for automated tooling, and **HANA entitlement is contractual** — it depends on your
> > Service Description Guide, which I cannot read. **Can you confirm you are entitled to do this on
> > this system, and that you accept the licence risk?** I will not create it until you do."
>
> **Record the answer** in the change record or ticket. If the user cannot confirm, that is a legitimate
> outcome: fall back to the supported levers in §2, or to export/import — **do not proceed anyway**.
>
> This mirrors the production-safety gate in the execution discipline below. The reasoning is the same:
> a decision with a cost the user carries is **theirs to make, explicitly, in advance**.

The bypass touches **cross-database plumbing**, which is where restricted-use database licences bite.
Neither mechanism costs an *extra option*, but both sit inside usage terms the user must own.

### Oracle — the terms are explicit, and the distinction is who is driving

**SAP Note 581312, *Oracle database: Licensing restrictions*** **[V]** quotes the SAP Price List
(§C.11.1) directly. Two clauses decide this:

> *"The customer shall only use the Oracle software **in connection with the SAP Software** and only
> for the purposes of its own internal data processing."*

> *"Direct access to the Oracle database is only allowed for tools from the areas of **system
> administration and monitoring**."* **[V]**

And then it lists, as **not allowed** for *other* software (its examples are reporting tools and
*"external tools to create automatic SAP system copies"*) **[V]**:

- Creating database users
- Creating database segments
- **Querying / changing / creating data in the database**
- Using ODBC or other SAP-external access methods

**Reading it honestly, both ways:**

| Doing this | Position |
|---|---|
| **You, the DBA, running `sqlplus` to refresh a QA client** | Sits squarely in *"system administration"* — the explicitly permitted category. This is the case the technique is for. |
| **`ABAP using database links`** | **Explicitly listed as a permitted interface** **[V]** |
| **A third-party or home-grown product that automates system copies via direct DB access** | The clause names this pattern as **not allowed**. Productising this skill into a tool is a different licence question from running it by hand. |
| **One-off migration** | *"The use of external software for database migration **is permitted**… as long as this is a **one-time process that will not be repeated**."* **[V]** |

> **Where the line actually falls:** a human administrator refreshing a system is administration; a
> repeatable automated pipeline that moves SAP data through direct DB access is closer to the
> prohibited pattern. If you intend to schedule this, get it in writing.

**No extra Oracle option is needed.** Note **740897** lists every option in the SAP-supplied Oracle
licence (Partitioning, Advanced Compression, Data Guard, ASM, RAC…) — **database links are not among
them because they are base Enterprise Edition** **[V]**. But watch the two that *are* chargeable and
that this method can tempt you into:

| Feature | SAP-supplied licence | Note |
|---|---|---|
| **Parallel query / parallel DML** | Included — base EE | **740897** **[V]** |
| **Database links** | Included — base EE | **740897** (absent from the options table) **[V]** |
| **Partitioning** | ✅ Included | **740897** **[V]** |
| **Advanced Compression** | ✅ Included | **740897** **[V]** |
| **RAC / Database Vault** | ⚠️ **Extra** — "Oracle Extended License Package" | **740897** **[V]** |
| **In-Memory** | ⚠️ **Extra** above 16 GB (free ≤16 GB from 19.8) | **740897** **[V]** |
| **Multitenant** | ⚠️ **Extra**, except **≤3 PDBs from 19c** | **740897** **[V]** |

> ⚠️ **If the customer bought Oracle direct from Oracle rather than through SAP, none of the above
> applies** — their own Oracle agreement governs, and they must check it with Oracle. Note 740897 is
> explicit that the SAP package *"always includes all of the options that are required for the SAP
> environment"*, which is a statement about the **SAP-resold** licence only. **[V]**

### HANA — contractual, not documented in a Note

Searching the Note database for a HANA licence restriction on **Smart Data Access** returns nothing,
and that is the answer: **HANA licensing is defined in the customer's contract**, not in SAP Notes.
**[V — verified by absence]**

What that means practically:

- **HANA runtime / "runtime edition for applications"** licences restrict the database to running
  **the licensed SAP application**. Using the same HANA as a general-purpose data platform is what
  the full-use / Enterprise licence is for.
- **Creating a remote source to another SAP system's HANA to refresh an SAP client is application
  administration** — the same reading as Oracle's "system administration" carve-out — but SAP has
  not written that down for you in a Note.
- **Federating non-SAP sources, or leaving the remote source in place for ongoing reporting, is a
  different activity** and much more likely to need full-use terms.

**Where to actually check:** the **Service Description Guide** for your HANA entitlement and the
**Order Form** — the governing version is the one your order form references, not the latest
published. That is exactly what **`sap-compliance-docs`** is for.

> ## 🛑 The practical rule
>
> **Create the remote source / database link for the refresh, and drop it when the refresh is done.**
> A transient, administrator-driven, single-purpose connection is defensible under both licences. A
> **persistent** remote source that outlives the task starts to look like federation — which is a
> licensable capability, and a finding in an audit. §5's cleanup step is not just hygiene; it is part
> of staying inside the licence.
>
> **This skill is not legal advice.** Where money or an audit is on the line, confirm with your SAP
> account team and get the answer in writing.

---

## 1. Diagnose first — prove it is the framework, not the database

The instinct when a copy stalls on a huge table is "HANA ran out of memory" or "the DB timed out".
On the refresh this skill comes from, **both theories were wrong** and cost hours. **[F]**

### Read the database's own trace, at OS level

```bash
# HANA — as root on the HANA host, in the TENANT's trace directory
ls -lt /usr/sap/<SID>/HDB<nr>/<host>/trace/DB_<TENANT>/ | head -30
grep -icE 'OUT OF MEMORY|OOM|ROLLBACK|allocation failed' \
     /usr/sap/<SID>/HDB<nr>/<host>/trace/DB_<TENANT>/indexserver_*.trc
ls /usr/sap/<SID>/HDB<nr>/<host>/trace/DB_<TENANT>/ | grep -cE '^oom|rtedump'
```

**What "the database is fine" looks like** **[F]**: only routine ~5-minute **savepoints**, redo
growing steadily during the delete, **zero** OOM / rollback / allocation errors, **no** `oom*` or
`rtedump*` files, and a clean `nameserver_alert_*.trc`. If that is what you see, the DB is idling
while ABAP struggles — the framework is your bottleneck.

For Oracle, the equivalents are the alert log and any recent trace/incident:

```bash
# Oracle — as ora<sid>
adrci exec="show alert -tail 200"
adrci exec="show incident"
# undo pressure / long-running DML is the thing to look for, not "the DB is broken"
```

### Then prove it with a timed baseline

Run the *same* operation natively, outside ABAP, on a small slice — or on the real thing if you have
a window. On the source refresh, a standalone `hdbsql` DELETE removed **72 M rows in ~45 seconds**
while the copy's delete step had already aborted twice. **[F]** That single measurement is what
justifies everything after it.

> **`sap-health-triage` §0** is the wider version of this discipline: `sapcontrol` and the DB's own
> logs answer when the ABAP stack cannot. Use `ABAPGetWPTable` to see the copy's work process, and
> the tenant trace to clear the DB of suspicion.

---

## 2. Exhaust the supported levers first

All **[V]** from Note 2163425 unless marked. These are cheaper and safer than any bypass:

| Lever | What it does | Note |
|---|---|---|
| **RFC server group + parallel processes** | The single biggest win, and the most commonly broken | **541311** |
| **`RSCCEXPT` table exclusions** | Exclude big transient tables (WF logs, IDoc, spool, GOS, batch input); transport them separately with `R3TR TABU` if needed | **70290** |
| **Exclude from a *running* copy** | You can drop a table out of a copy already in flight — **try this before killing a work process** | **2459313** |
| **`SCC5` pre-delete of the target client** | Deleting before copying is often faster than copy-over-delete | **70643**, Oracle: **857973** |
| **Latest `tp` / `R3trans`, Note 2550545, the client-copy TCIs** | Consistency *and* performance fixes | **2201677**, **3281364**, **3652777** |
| **DB parameter check** | Oracle: **1888485** (12.1), **2470718** (12.2/18c/19c); HANA: **2555451**, **2761821** | — |
| **Consider a system copy instead** | *"A system copy can also be considered instead of a client copy for very large clients."* | **2163425** |

> ## 🛑 The parallel dialog silently falls back to one stream
>
> On the source refresh the copy ran **single-threaded for ~19 hours** before anyone noticed. **[F]**
> The cause: the parallel dialog's **RFC server group was a dead entry** — its RZ12 instance
> assignment was the *wrong case* (`hostname_SID_nr` vs `HOSTNAME_SID_nr`), no green status,
> unactivated resource allocation. Processes could not dispatch, so the copy quietly used one.
>
> **Check in RZ12 that the group is green, activated, and the instance name matches exactly.** Then
> confirm you actually got parallelism — several processes each on a *different* table.
>
> **A restart re-reads the server group** (Note 541311 Q10) **[V]**, so you can fix the group and
> restart in restart-mode **without losing copied data**. On the source refresh that recovered 133 M
> already-copied rows and parallelism engaged immediately. **[F]**

**Two expert-option traps** **[F]**:
- **`NATIVECOPY` is LOCAL-copy only** (Note 3019660) — it must be **off** for a remote copy.
- Reasonable remote set: `SINGLECOPY`, `SKIP_EMPTY`, `LARGEBLOCK`, `MAX_WPRUN` on; `NATIVECOPY`,
  `VERIFY_CNT` off.

---

## 3. The bypass — shape of the method

Once diagnosis says framework-bound and the supported levers are spent, move **that one table**
natively. Four steps, same shape on every database:

```
1. DELETE the target-client rows natively      ← outside ABAP, so no work-process timeout
2. INSERT ... SELECT in parallel, partitioned  ← by a natural key; ~6 streams
3. VERIFY per client AND per partition          ← exact target, not "about right"
4. CLEAN UP + rotate anything exposed           ← this step is not optional
```

**Pick the database variant:**

| Situation | Read |
|---|---|
| **SAP HANA** — cross-system (SCC9) or same-tenant (SCCL) | [references/hana-method.md](references/hana-method.md) |
| **Oracle** — cross-system (DB link) or same-database | [references/oracle-method.md](references/oracle-method.md) |

### Choosing the partition key

You need a column that **splits the table into chunks of roughly similar size** and is **cheap to
filter**. Fiscal year (`GJAHR`) is the natural choice for finance tables and gave 11 partitions of
6–14 M rows each. **[F]** Company code (`BUKRS`), ledger (`RLDNR`) or posting period also work.

**Validate the partitioning before you load** — the partition counts must **sum exactly to the
source total**. If they do not, your key has NULLs or values you did not enumerate, and you will
silently lose rows.

### Why ~6 streams

More is not better. Six was chosen to stay gentle on a **production source system**. **[F]** The
constraint is rarely target CPU — it is source I/O, network, and (for HANA SDA) the remote source's
patience. Start at 4–6, watch, and only raise it if the source is clearly idle.

> ⚠️ **The client field is not always `MANDT`.** ACDOCA uses **`RCLNT`**. Check before you write any
> `WHERE`:
> ```sql
> -- HANA
> SELECT COLUMN_NAME FROM SYS.TABLE_COLUMNS
>  WHERE SCHEMA_NAME='<SCHEMA>' AND TABLE_NAME='<TABLE>'
>    AND COLUMN_NAME IN ('MANDT','RCLNT');
> ```
> No match at all means the table is **client-independent** and must not be filtered by client.

---

## 4. Verify — exactly, not approximately

```sql
-- per client (the whole table, all clients)
SELECT <CLIENTFLD>, COUNT(*) FROM <SCHEMA>.<TABLE> GROUP BY <CLIENTFLD>;

-- per partition, target client only — must match the source partition-for-partition
SELECT <PARTKEY>, COUNT(*) FROM <SCHEMA>.<TABLE>
 WHERE <CLIENTFLD>='<TGT>' GROUP BY <PARTKEY> ORDER BY <PARTKEY>;
```

**More rows than the source means duplicates, not success.** The usual cause is **two writers**: the
copy's own work process for that table was still running while you loaded. **[F]**

> ⚠️ **Do not use `EM_GET_NUMBER_OF_ENTRIES` or `RFC_READ_TABLE` to verify.** **[F]**
> `EM_GET_NUMBER_OF_ENTRIES` counts **all clients**, and `RFC_READ_TABLE` returns fields in **DDIC
> offset order** (not the order you asked for), so it is easy to read the wrong column and conclude
> the wrong thing. Count natively with `hdbsql` / `sqlplus`.

**Also verify the other clients are untouched.** A target system often holds a second client that
must not be disturbed — on the source refresh, client 200 held 85 M rows that had to survive
intact. **[F]** Capture its count before you start and re-check it after.

---

## 5. Cleanup and security — treat as part of the task

Bypassing creates privileged, temporary objects. Leaving them is a real finding.

| Item | Action |
|---|---|
| **Remote source / database link** | `DROP` it — it holds **credentials for the source system** |
| **Virtual / staging tables** | `DROP` |
| **Temporary grants** | `REVOKE` the `SELECT` you granted on the app schema |
| **Temporary secure-store keys** | Delete (`hdbuserstore DELETE <KEY>`) |
| **Any password that touched a command line** | **Rotate it.** A `CREATE REMOTE SOURCE` carries the password in cleartext in SQL — assume shell history, `ps`, and logs captured it |
| **`rdisp/max_wprun_time`** | Restore the original value if you raised it |
| **Client logon lock** | Release it — see below |
| **Statistics** | Re-gather on the loaded table (Oracle especially) |

> ## Release the logon lock after an aborted copy
>
> A client copy sets a logon lock (**`CCTEMPLOCK`** in `T000`) and clears it on clean completion. An
> **aborted** copy can leave the target client locked out. Clear it with **`SCC4`**, or via the
> client-copy tools — do not leave users unable to log on and call it done. **[G]**

> **`sap-crypto-pse` / `sap-oracle-dataguard` cross-check:** if you disabled logging or archiving to
> speed the load, put it back, and confirm any standby is still valid (§Oracle).

---

## 6. When the copy itself will not let go

If the copy's work process for that table is still holding it:

1. **First try the supported route** — **exclude the table from the running copy** (Note **2459313**)
   **[V]**. Cleaner than killing anything.
2. If that is not possible, **SM50 → Cancel without core** on that specific work process. The table
   is marked in error, **every other table finishes normally**, and the copy ends with
   `STATUS='A'` — cosmetic, given you are loading that table yourself. **[F]**
3. **Check for orphaned enqueue locks.** On the source refresh, finalisation hung ~20 min on a stale
   `RSTABLE` lock left by a finished parallel process (Note 541311 Q6) **[V]**. **SM12-delete the
   orphaned lock** — do **not** cancel via SCC3, which rolls the table back. **[F]**

---

## Cross-references

- **`sap-transport-mgmt`** — `R3TR TABU` transports for the RSCCEXPT-excluded tables; `tp`/`R3trans` currency.
- **`sap-health-triage`** — §0 out-of-band diagnosis; `ABAPGetWPTable` to see the copy's work process.
- **`sap-hana-system-replication`** — a target on HSR replicates every row you load; check log volume and secondary lag.
- **`sap-oracle-dataguard`** — **`NOLOGGING` is silently ignored under `FORCE LOGGING`**, which Data Guard requires. Read before reaching for it.
- **`sap-backup-recovery`** — take a restore point before a bypass; `NOLOGGING` breaks recoverability of the loaded segments.
- **`sap-db-command-reference`** — `hdbsql`, `sqlplus`, and the correct OS user per database.
- **`sap-space-reclaim`** — a large delete leaves space that needs reclaiming, and log/undo growth during the load.
- **`sap-compliance-docs`** — the Service Description Guide that actually governs your HANA entitlement; §0a explains why the licence answer lives there and not in an SAP Note.
- **`sap-support-case`** — same consent-gate pattern (§0a here, troubleshooting key there), and where to go if the copy framework really is defective.

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
| **[CC1]** | **SAP Note 2163425** — *Recommendations for client copy performance improvement*, v31, 08.05.2026, BC-CTS-CCO | **[V]** — the 100–500 MB/hour DB-interface ceiling, the supported-lever list, and the per-database note map |
| **[CC2]** | **SAP Note 857973** — *Deleting clients efficiently using Oracle*, BC-DB-ORA | **[V]** — CTAS + `NOLOGGING`/`PARALLEL`, `TRUNCATE` test, index dropping, the YKDELCLS/ZTABDELE/ZSDELCUR/ZSDELDIS trade-offs, and SAP's own risk framing |
| **[CC3]** | **SAP Note 541311** — *CC-INFO: Parallel processes FAQ* | **[V]** — Q4 parallelism is across tables not within one; Q6 orphaned `RSTABLE` locks; Q10 restart re-reads the server group |
| **[CC4]** | **SAP Note 70290** — *CC-INFO: Exclude tables with RSCCEXPT*; **2459313** — *Excluding tables from a running client copy* | **[G]** |
| **[CC5]** | **SAP Note 2953662** — remote client copy performance in S/4HANA; **489690** / **67205** — copying large production clients | **[G]** |
| **[CC6]** | **SAP Note 2555451** / **2761821** — client-copy performance on HANA; **2000000** — HANA performance optimization | **[G]** |
| **[CC7]** | **SAP Note 1888485** (Oracle 12.1), **2470718** (12.2/18c/19c), **1431798** (11.2) — DB parameters; **838725** — statistics; **1171650** — parameter check | **[G]** |
| **[CC8]** | **SAP Note 105047** — *Support for Oracle functions in the SAP environment* | **[V]** — distributed transactions and Oracle Gateway are "permitted, no SAP support"; database links between SAP databases are not addressed explicitly |
| **[CC11]** | **SAP Note 581312** — *Oracle database: Licensing restrictions*, BC-DB-ORA | **[V]** — quotes SAP Price List §C.11.1: direct DB access is for "system administration and monitoring" only; "ABAP using database links" is a permitted interface; automated system-copy tooling via direct access is not; one-time migration is permitted |
| **[CC12]** | **SAP Note 740897** — *Info about the scope of the Oracle license; required Oracle options*, v37 | **[V]** — the full option table for the SAP-resold Oracle licence. Database links and parallel DML are absent because they are base Enterprise Edition; RAC/Database Vault/In-Memory/Multitenant are the chargeable extras |
| **[CC13]** | **HANA licensing** — no SAP Note governs Smart Data Access usage rights | **[V — by absence]** — HANA entitlement is contractual; check the **Service Description Guide** referenced by your Order Form. See `sap-compliance-docs` |
| **[CC9]** | **SAP Note 365304** (deletion reports), **70643** (SCC5 client deletion), **3019660** (`NATIVECOPY` is local-only), **2550545**, **3281364**/**3652777** (client-copy TCIs), **2201677** (tp/R3trans currency) | **[G]** |
| **[CC10]** | **Field record** — S/4HANA QA refresh, Sep 2026: ACDOCA 105,062,507 rows. Remote SDA 6-way ≈1.59 M rows/min (~70 min); local column-list ≈6 min; native DELETE 72 M rows in ~45 s; 19 h lost to a dead RFC server group | **[F]** |

> **The Oracle variant is marked [A] where it is an adaptation, not a field result.** The HANA path
> in this skill was executed end-to-end on a live refresh; the Oracle path is built on SAP's own
> Note 857973 plus standard Oracle mechanics, and has **not** been run on that refresh. Rehearse it
> on a test system before a production-adjacent window, and say which of the two you are on.

> **Currency.** Note 2163425 is actively maintained (v31, May 2026) and carries the per-database note
> map — re-read it before a refresh rather than trusting this snapshot. Note 857973 is old (2005) but
> the Oracle mechanics it describes are unchanged; the *parameter* notes it predates are in [CC7].
