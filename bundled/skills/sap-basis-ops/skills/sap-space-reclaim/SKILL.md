---
name: sap-space-reclaim
description: >-
  Landscape space-reclamation assessment — what can be deleted, what has a configurable
  retention, what is self-service vs change-controlled, and how much disk you actually get back.
  Covers ABAP technical tables (spool/TemSe, table logging, application log, job logs, dumps,
  IDoc/RFC queues, workload stats, change documents), the Security Audit Log archive/delete
  path, per-database diagnostic files and crash dumps across all six platforms, and OS-layer
  leftovers (work-directory traces, core dumps, old kernels, SUM directories, installation
  media). Honest that deleting rows does not shrink a database without reorganization. Use for
  "database is full", "reclaim disk", "what can we clean up", "retention settings", "core
  dumps", "db2diag", "adrci", "DBTABLOG huge", "TST03 huge".
---

# Space Reclamation Assessment

Two different jobs get confused here. **[sap-housekeeping](../sap-housekeeping/SKILL.md)** keeps a healthy
system healthy — the standard reorganization jobs that should already be running. **This** skill is the
*assessment and one-off reclamation project*: the system is already large, and someone needs a costed,
evidence-backed list of what can go.

> **Guardrail — measure, then propose, then delete.**
> - **Never delete before sizing.** Every candidate gets a *current size* and an *estimated reclaim* (§2),
>   because effort is only justified by the number.
> - **Deleting rows ≠ free disk.** On most databases the space stays inside the datafile/datavolume as
>   reusable space. **Reorganization is a separate, usually disruptive step** (§6). Say this out loud in
>   every estimate, or the reported "saving" is fiction.
> - **Retention is a setting, not a delete.** Where a retention parameter exists, *fixing the setting* is
>   the durable win; a one-off deletion just restarts the clock (§3, §4).
> - **Logs may be legally retained.** The Security Audit Log especially — archive and verify readability
>   *before* deletion, never delete immediately (§5). [G, SAL]
> - **PRD: typed confirmation per object**, and prefer the standard job/report over ad-hoc SQL always.
>   Never `DELETE`/`TRUNCATE` an SAP table directly unless a Note explicitly says so for that table.

Verification legend: **[V]** verified during authoring · **[G]** cited to an SAP Note or guide.

Full per-table catalogue: **[references/reclaimable-inventory.md](references/reclaimable-inventory.md)**

---

## 1. Scope the assessment

Work the four layers in this order — the answer is usually concentrated in one of them.

| Layer | Typical big-ticket items |
|---|---|
| **1. ABAP technical tables** | spool/TemSe, table logging, application log, job logs, IDocs, RFC queues, workload stats, change docs |
| **2. Application data** | archiving objects via **SARA** — out of scope here, needs business sign-off |
| **3. Database layer** | traces, audit files, dumps, old backups/archive logs, HANA audit log |
| **4. OS layer** | work-dir traces, core dumps, old kernel dirs, SUM dirs, extract/LSMW files |

**Dormant clients** are often the single largest line item and get their own skill —
[sap-dormant-clients](../sap-dormant-clients/SKILL.md).

---

## 2. Size it first — find where the space actually is

Never start from a list of "things you can clean". Start from **what is big in this system**.

**SAP-provided SQL to find the largest technical tables** — the fastest route: [G, TT]

| DB | Statement | Delivered in |
|---|---|---|
| **HANA** | `HANA_Tables_LargestTables` with `ONLY_TECHNICAL_TABLES 'X'` | **SAP Note 1969700** |
| **Oracle** | `Space_LargestTables` with `ONLY_BASIS_TABLES 'X'` | **SAP Note 1438410** |

> 📎 **Both statements are shipped as a ZIP attachment on those Notes, not as text in the Note body.**
> Verified by downloading and extracting them: 1969700 carries `SQLStatements_EarlierRevisions.zip`
> (1,684,928 B) containing **`HANA_Tables_LargestTables.txt`** plus `_1.00.120+` / `_2.00.030+` revision
> variants; 1438410 carries `20260614_SQLStatements.zip` (508,395 B, **338 files**) containing
> **`Space_LargestTables.txt`** and `Space_LargestTables_Fallback.txt`. Retrieve them with the MCP's
> **`fetch_attachment`** (or from the Note in a signed-in browser) — reading the Note text alone gives you
> **no SQL at all**. Pick the statement file matching your revision. **[V]**

Otherwise, per-DB size views: **`DB02`** / **`DBACOCKPIT`** → space → largest tables/segments. Per-database
specifics in [sap-db-command-reference](../sap-db-command-reference/SKILL.md).

**Then quantify what a retention cut-off would actually remove.** Use **`TAANA`** (table analysis) to count
rows grouped by a date field and/or `MANDT` — that converts "DBTABLOG is 300 GB" into "260 GB of it is older
than 2 years". [G, TT]

```
TAANA → create analysis variant on the date/client field → run in background → read the distribution
```

**Estimated reclaim = rows outside the retention × average row size.** Get average row size from the DB's
own statistics (`DB02`/`DBACOCKPIT`), not by guessing.

> Record for each candidate: **current size**, **rows outside retention**, **estimated reclaim**, **method**,
> **retention setting available?**, **self-service or change-controlled?**. That table *is* the deliverable.

---

## 3. Layer 1 — ABAP technical tables

The authoritative, continuously-updated catalogue is **SAP Note 2388483** (*How-To: Data Management for
Technical Tables*) — it maps table → area → SAP Notes → the transaction/report that cleans it, for **all**
databases. Treat it as the source of truth and this section as the Basis-relevant extract. [G, TT]

The highest-yield Basis candidates, with how each is controlled: **[V, TT]**

| Data | Tables | Clean with | Retention configurable? |
|---|---|---|---|
| **Spool / TemSe** | `TSP01`, `TSP02`, `TST01`, `TST03`, `TSPADS`, `TSPEVJOB` | `RSPO0041`, `RSPO1041`, `RSPO1043`, `RSBTCDEL2`, `RSBDCREO` — Note 48400 | **Yes** — spool retention period per request |
| **Table logging** | `DBTABLOG`, `DBTABPRT` | **`SCU3`**, report **`RSTBPDEL`** — Notes 2335014, 2362854 | **Yes** — `rec/client` + per-table log flag |
| **Application log** | `BALDAT`, `BALHDR`, `BALC`, `BAL_INDX`, `BALM`, … | **`SLG2`**, `SBAL_DELETE`, `SBAL_DELETE_ORPHAN_MESSAGES`, `SBAL_STATISTICS` — Notes 195157, 2057897, 3039724, 3742661 | **Yes** — expiry date set by the writing application |
| **Job logs / jobs** | `TBTCO`, `TBTCP`, `TBTCS`, `TBTCJOBLOG*` | `RSBTCDEL2`, `RSBTCCNS` — Notes 16083, 666290, 1440439, 2360818 | Via job-log retention |
| **ABAP short dumps** | `SNAP` | **`RSSNAPDL`** — Note 11838 | **Yes** — `rdisp/max_snapshots`-style + job variant |
| **IDocs** | `EDIDC`, `EDID4`, `EDIDS`, `EDI30C`, `EDI40` | `RSEXARCA/B/D/L/R`, `RSETESTD` — Notes 40088, 1574016 | Archiving (SARA) |
| **RFC / qRFC queues** | `ARFCSDATA`, `ARFCRSTATE`, `ARFCSSTATE`, `TRFCQIN`, `TRFCQOUT`, `TRFCQDATA`, `TRFCQSTATE` | **`SM58`**, **`SMQ1`**, **`SMQ2`** — Note 375566 | No — these are *stuck entries*, investigate before deleting |
| **RFC logging** | `ARFCLOG` | `RSARFCLE`, `RSARFCLR` — Notes 802062, 2363550 | **Yes** |
| **Workload statistics** | `SWNCMONI`, `SWNCM_TIMES`, `SWNCM_*` | **`ST03`** — **adjustment of retention times** — Note 2274315 | **Yes — this is a pure retention setting** |
| **Change documents** | `CDHDR`, `CDPOS`, `CDPOS_STR`, `CDPOS_UID` | **`SARA`**, archiving object **`CHANGEDOCU`** — Note 3015823 | Archiving residence time |
| **Batch input** | `APQD`, `APQI` | **`SM35`**, `RSBDCREO` — Note 36781 | **Yes** |
| **SAPoffice** | `SOFFCONT1`, `SOC3`, `SOOD`, `SOST`, … | `RSBCS_REORG` — Notes 966854, 1641830 | **Yes** |
| **ALE change pointers** | `BDCP`, `BDCPS`, `BDCP2` | **`BD22`**, `RBDCPCLR` — Note 513454 | **Yes** |
| **Work items / workflow** | `SWWWIHEAD`, `SWWLOGHIST`, `SWW_CONT`, … | `RSWWHIDE`, `RSWWWIDE`, `RSWWWIDE_DEP` — Notes 49545, 1552169 | Archiving |
| **Object links** | `SRRELROLES`, `IDOCREL`, `SMW0REL` | `RSRLDREL` — Notes 493156, 505608 | No |
| **Table analysis results** | `TAAN_*`, `ARDB_STAT*` | `TAAN_DELETE_ANALYSES` — Note 2034063 | No — delete your own leftovers |
| **Snapshot monitor** | `/SDF/MON`, `/SDF/SMON_CLUST` | **`/SDF/SMON`** — Note 2651881 | **Yes** |
| **eCATT logs** | `ECLOG_*` | `RSECATTLOGDEL`, archiving object `ECATT_LOG` — Note 1052908 | **Yes** |
| **Enhancement logs** | `ENHLOG` | `ENH_SHRINK_ENHLOG` — Note 2229441 | No |
| **Buffer sync** | `DDLOG` | **TRUNCATE allowed — only while ABAP is stopped** — Note 36283 | n/a |

> ⚠️ **`DDLOG` is the exception that proves the rule.** It is one of the very few tables SAP permits you to
> truncate directly, **and only with the ABAP stack down**. Do not generalise from it. [G, TT]

**Self-service vs change-controlled** — a useful split when proposing work:

- **Self-service, low risk:** `RSSNAPDL`, `RSPO1041`/`RSPO0041`, `RSBTCDEL2`, `RSBDCREO`, `SBAL_DELETE`,
  `RSARFCLE`, `TAAN_DELETE_ANALYSES`, ST03 retention adjustment. These are the standard housekeeping jobs —
  if they are not scheduled, scheduling them per **SAP Note 16083** is the fix, not a one-off deletion.
- **Change-controlled:** anything using **SARA** (archiving — needs business sign-off and an archive store),
  table-logging scope changes (`rec/client`), and anything touching RFC queues (stuck entries may be
  business data in flight).

---

## 3a. The fastest first pass: volume vs. whether its cleanup job runs

Before sizing anything precisely, do this — it takes minutes and usually explains the whole problem.

**Check which cleanup reports are actually scheduled, then compare against table volume.** Job *names* vary
by system and by SJOBREPO version, so match on the **report name in `TBTCP-PROGNAME`**, not on `TBTCO-JOBNAME`:

```abap
SE16 → TBTCP    " PROGNAME = RSBTCDEL2 / RSPO1041 / SBAL_DELETE / RSSNAPDL / RBDCPCLR / RSTBPDEL / …
```

A table that is large **and** whose report is unscheduled is a confirmed finding, not a hypothesis — and
the fix is *schedule the job* (SAP Note 16083), not a one-off deletion.

**Verified on a live S/4HANA sandbox** (SAP_BASIS 757 on HANA) during authoring — of 14 standard cleanup
reports only **two** were scheduled, and the volumes tracked that exactly: **[V]**

| Table | Rows | Cleanup report | Scheduled? |
|---|---|---|---|
| `BALHDR` | > 1,000,000 | `SBAL_DELETE` | **no** |
| `BDCP2` | 198,116 | `RBDCPCLR` / `BD22` | **no** |
| `TBTCO` | > 100,000 | `RSBTCDEL2` | **no** |
| `TSP01` / `TST03` | > 10,000 each | `RSPO1041` | **no** |
| `SOFFCONT1` | 1,423 | `RSBCS_REORG` | **yes** |
| `SNAP` | 742 | `RSSNAPDL` | **yes** |

The only two small tables were the only two with a running cleanup job. That correlation is the argument
to put in front of whoever approves the work.

> On **S/4HANA**, check the **technical job repository** (`SJOBREPO`, SAP Note 2190119) before scheduling
> anything by hand — it manages many `SAP_*` jobs itself, and hand-scheduling duplicates them. In the
> system above SJOBREPO was clearly active (`SAP_AMC_LOG_REORG`, `SAP_ADS_SPOOL_CONSISTENCY_CHECK`, …) and
> **still** did not cover the classic reorg reports above. Presence of SJOBREPO is not coverage. **[V]**

### Assessing over RFC — what works, and what will mislead you

If you are driving the assessment through `RFC_READ_TABLE` rather than a GUI, four behaviours will produce
wrong answers. All observed live: **[V]**

| Behaviour | Consequence |
|---|---|
| **Only the logon client is visible** for client-dependent tables. Filtering on `MANDT` raises `OPTION_NOT_VALID`. | You cannot assess other clients' activity from one connection — you need a logon per client, or `ST03N`, or DB-level SQL. Client-**independent** tables (`T000`) are fine. |
| **No field list → `DATA_BUFFER_EXCEEDED`** on any table whose row exceeds 512 bytes | "Table missing" conclusions that are simply wrong. Always name a narrow field. |
| **Counting by paging `ROWSKIPS` is O(n) scans per page.** On a large table it can exhaust the work process — a real `DBTABLOG` probe returned *"No more memory available to add rows to an internal table"* | Do **not** count large tables over RFC. Use `DB02`/`DBACOCKPIT`, the DB-native SQL in §2, or `TAANA`. |
| **`LIKE 'SAP\_%'` (escaped underscore) silently returns zero rows** | Reads as "no standard jobs scheduled" when they exist. Use `SAP_%` and filter client-side. |

The first three are the reason §2 tells you to size at the **database** layer. RFC is good for *inventory
and existence*, poor for *volume*.

---

## 4. Retention settings worth fixing permanently

A one-off delete that isn't paired with a retention fix will be repeated next year.

| Area | Setting | Where |
|---|---|---|
| Table logging scope | **`rec/client`** (`OFF` / `ALL` / client list) + per-table *log data changes* flag | Profile + `SE13` / `SCU3` |
| Workload statistics | retention per aggregation level | **`ST03`** → workload collector settings — Note 2274315 |
| Spool | retention period, auto-delete of old requests | Spool admin + `RSPO1041` variant |
| Job logs | job-log retention | `RSBTCDEL2` variant |
| Short dumps | keep-days | `RSSNAPDL` variant |
| Security Audit Log | recording target + retention/archive mode | **`RSAU_CONFIG`** (§5) |
| HANA audit log | `ALTER AUDIT POLICY SET RETENTION` (HANA ≥ 2.0 SPS04) | HANA SQL — Notes 2159014, 2308083, 3084473 |

**Schedule the standard jobs.** SAP Note **16083** defines the standard reorganization job set; SAP Note
**2190119** covers the S/4HANA **technical job repository** (`SJOBREPO`), which schedules many of these for
you — verify it is active before hand-rolling jobs. [G, TT]

---

## 5. Security Audit Log — archive before you delete

SAL is the one that gets people into trouble, because it is both large and legally sensitive.

First establish **how it is recorded** — **`RSAU_CONFIG`** → *Parameters* → **Recording Target** and
**Recording Type**. The cleanup path depends entirely on this: [G, SAL]

| Recording target / type | Cleanup path |
|---|---|
| **File** | reorganize old audit **files** (`RSAU_ADMIN` → *Reorganize log files*) |
| **Database**, *Audit Log with Archive Interface* | **archive then delete** — the procedure below |
| **Database**, *Audit Log with Retention Management* | retention-driven; the archive procedure does **not** apply |
| **Database**, *Persistency in external system (API mode)* | may allow direct deletion; if reorganization is blocked, implement **SAP Note 3346306** |

**Archive-then-delete (DB + archive interface), tables `RSAU_BUF_DATA` / `RSAU_LOG`:** [G, SAL]

1. **`RSAU_ADMIN`** → *Reorganize log table* → **Archive** → opens **`SARA`** with archiving object **`BC_SAL`**.
2. In *Customizing → Archiving Object-Specific Customizing → Technical settings*, set delete jobs to
   **Not Scheduled** (recommended) so deletion stays manual.
3. Define a **write variant** (e.g. keep 1 year), set start date and spool parameters, schedule.
   Job **`ARV_BC_SAL_WRI*`** appears in `SM37`.
4. **The archive file exists but nothing is deleted yet.** Run the **Delete** step against the archive file
   — job **`ARV_BC_SAL_DEL*`**.

> 🔒 **Never delete immediately.** SAP's own guidance: audit logs carry legal retention obligations —
> **verify the archive file is complete and readable before deleting**. Use the **"Delete with Test
> Variant"** checkbox on `RSAU_ARCHIVE_WRITE` to preview exactly what would be removed. [G, SAL]

Requires **SAP_BASIS 7.50 SP03+** (the RSAU_* generation — see
[sap-security-patch](../sap-security-patch/SKILL.md) and
[sap-log-reference](../sap-log-reference/SKILL.md)). If `RSAU_ADMIN` shows the tables as empty while the DB
says otherwise, that is **SAP Note 3467895**. [G, SAL]

---

## 6. Making the space actually appear

**This is the step that turns a row count into free disk, and it is the step most often skipped.**

| DB | Why deleted rows don't free space | Reclamation |
|---|---|---|
| **Oracle** | space stays in the segment/tablespace as free extents | reorg with **BR\*Tools** — Notes **646681**, **541538**; *Segment Management with BR\*Tools* |
| **SAP HANA** | row-store needs reorg; column-store needs **delta merge** + compression; persistence needs a **data volume shrink** | merge/compress, then reclaim data volume |
| **IBM Db2** | space stays in the tablespace | `REORG` + `ALTER TABLESPACE … REDUCE` |
| **SAP ASE** | pages remain allocated | `reorg rebuild` / shrink |
| **SQL Server** | pages remain allocated | index rebuild / `DBCC SHRINKFILE` (with care) |
| **MaxDB** | | reorganize/compress |

Per-DB commands and their guardrails: [sap-db-command-reference](../sap-db-command-reference/SKILL.md).
Reorganization is **resource-intensive and usually needs a window** — plan it as its own change, and take a
backup first ([sap-backup-recovery](../sap-backup-recovery/SKILL.md)).

Search the reorganization Note for **your** DB component: `BC-DB-ORA`, `BC-DB-HDB`, `BC-DB-DB6`,
`BC-DB-MSS`, `BC-DB-SDB`, `BC-DB-INF`. [G, RM]

---

## 7. Layers 3 & 4 — database and OS files

These are often the quickest wins because they need no ABAP change and no archiving.

### Database-layer files

| DB | Discover it with | Crash artefacts are called | Retention mechanism |
|---|---|---|---|
| **HANA** | **`M_TRACEFILES`** view | `*.crashdump.*.trc`, `*.rtedump.*.trc` | `ALTER SYSTEM REMOVE TRACES`; **HANACleaner** (Note 2399996) [G, HCLEAN] |
| **Oracle** | **`V$DIAG_INFO`**, `adrci> SHOW HOMES` | **`$ADR_HOME/cdump`** (was `CORE_DUMP_DEST`) | ADR auto-purge — `SHORTP_POLICY` 720h files/dumps, `LONGP_POLICY` 8760h metadata; **SAP says keep Oracle defaults** [G, ORA] |
| **Db2** | `db2 get dbm cfg` → **`DIAGPATH`** | trap files, dumps, **`FODC_*` directories** | **`DIAGSIZE`** (rotating `db2diag.log`); `db2diag -A` |
| **SAP ASE** | the **`-e`** flag in `RUN_<SERVER>` | shared-memory dumps, `dataserver` cores | none built in — cycle the errorlog on a schedule |
| **MaxDB** | run directory, typically `/sapdb/data/wrk/<SID>` | `rtedump`, kernel cores | `KnlMsg` size parameter + prune `KnlMsgArchive` |
| **SQL Server** | `-e` startup parameter / `SERVERPROPERTY('ErrorLogFileName')` | **`SQLDump####.mdmp`** / `.txt` | `sp_cycle_errorlog` + configured number of generations |

**Per-database detail — paths, commands, what must never be deleted, and citation status for each:
[references/db-diagnostic-files.md](references/db-diagnostic-files.md).**

> ⚠️ **Only Oracle has a directory called `cdump`. Nobody else uses the word "core".** That is the whole
> reason a filename search fails: the artefact you want is called `crashdump`, `FODC_*`, `SQLDump*.mdmp`
> or `rtedump` depending on the platform. **Read the DB's diagnostic-path parameter, then list via its own
> inventory view.** [G, ORA] **[V]** for the HANA row.

> 📦 **Package before you purge.** With an open SAP/Oracle message, build the incident package first
> (Oracle: `adrci> IPS CREATE PACKAGE INCIDENT <n>` → `IPS GENERATE PACKAGE`) — purging first destroys the
> evidence the message depends on. [G, ORA]

> 🚨 **Archive/transaction logs are not housekeeping.** Never delete them on space pressure alone — they are
> deletable only once a **verified** backup includes them. This is the single most common self-inflicted
> data-loss incident in Basis. See [sap-backup-recovery](../sap-backup-recovery/SKILL.md).

> 🧠 **"Core dump" is not one thing, and on SAP hosts it is usually not a file called `core`.** Three
> distinct artefact families, discovered three different ways: **[V]**
>
> | Family | Where / how to find it | Remove with |
> |---|---|---|
> | **OS process cores** | governed by `/proc/sys/kernel/core_pattern`. A leading `\|` means the kernel **pipes** the core to a handler and no `core*` file is ever written | `coredumpctl` (systemd), or delete the confirmed file |
> | **HANA crash / runtime dumps** | `*.crashdump.*.trc`, `*.rtedump.*.trc` in the HANA trace directory — **never named "core"**. Inventory them from the **`M_TRACEFILES`** system view | **`ALTER SYSTEM REMOVE TRACES`**; `ALTER SYSTEM CLEAR TRACES` clears contents [G, HDIAG] |
> | **ABAP work-process cores** | the instance `work` directory, only when `core_pattern` is a plain filename | delete the confirmed file |
>
> **HANA diagnosis-file rules** — `.py` (SQL/server traces) and `.old` (previous restart) are safe to remove;
> `.stat` are tiny placeholders; but **`py.sap<SID>_HDB<nr>` and `hdb.sap<SID>_HDB<nr>` must NOT be removed**
> — they link to the Python runtime and the `hdbdaemon`. `dev_webdisp` / `dev_icm_sec` / `icm_port_list` are
> removable only while the system is down. **SAP Note 2370780** is explicit that it *"is not a confirmation
> to delete any file"* — confirm per file. [G, HDIAG]
>
> **Automate it rather than repeating it:** **SAP HANACleaner** (**SAP Note 2399996**) is the supported way to
> put HANA diagnosis-file cleanup on a retention schedule — the HANA-side equivalent of the ABAP standard
> jobs in SAP Note 16083. [G, HCLEAN]

### OS-layer files

| Item | Where | Notes |
|---|---|---|
| **Work-directory traces** | `/usr/sap/<SID>/<INST>/work` — `dev_w*`, `dev_disp`, `dev_rfc*`, `stderr*` | Covered by [sap-housekeeping](../sap-housekeeping/SKILL.md); safe when the instance is stopped, or use the documented rotation |
| **Core dumps** | same work dir, plus DB dirs — `core`, `core.<pid>` | Often gigabytes each. **Keep one** if you have an open SAP incident about the crash; otherwise delete |
| **Old kernel directories** | `/usr/sap/<SID>/SYS/exe/...` backups taken during patching | Keep the last known-good rollback only — [sap-kernel-patch](../sap-kernel-patch/SKILL.md) |
| **Leftover installation media** | wherever the installer staged it — e.g. `/hana/dl`, `/sapcd`, `/install` | **Frequently the largest single item on the box.** Both the downloaded `.ZIP`/`.SAR` set *and* its extraction are typically retained after go-live. Archive off-box, then remove |
| **SUM / upgrade directories** | `/usr/sap/<SID>/SUM`, `/usr/sap/<SID>/EHPI` | Only after the upgrade is closed and the evaluation/log archive is kept |
| **Transport leftovers** | `/usr/sap/trans/data`, `/cofiles`, `/log`, old `EPS/in` `.PAT` files | See [sap-transport-mgmt](../sap-transport-mgmt/SKILL.md); keep what the buffer still references |
| **LSMW / data-migration extract files** | project-defined paths on the app server, often under `/usr/sap/<SID>/...` or a custom `/interface` mount | **Find them, don't assume the path** — read the LSMW project's file definitions, or `find` for the configured extension. These are frequently multi-GB one-off conversion files left after a go-live |
| **Interface in/out directories** | custom mounts used by `OPEN DATASET` / file interfaces | Owned by applications — confirm the owner before deleting |

Finding the big ones, per platform:

```bash
# Linux / AIX — as <sid>adm; largest files under the SAP mounts
du -xh --max-depth=2 /usr/sap 2>/dev/null | sort -rh | head -30      # Linux
du -xg /usr/sap | sort -rn | head -30                                # AIX (GB)
find /usr/sap -xdev -type f -size +500M -exec ls -lh {} \; 2>/dev/null

# core dumps — DO NOT guess the filename. Ask the kernel what it produces:
cat /proc/sys/kernel/core_pattern      # '|/usr/lib/systemd/...' = piped to a handler, NOT a core* file
cat /proc/sys/kernel/core_uses_pid     # 1 appends .<pid>
ulimit -c                              # 0 = no cores produced at all

# (a) piped to systemd-coredump  -> they are NOT in the work dir under any name
coredumpctl list --no-pager 2>/dev/null | tail -20
du -sh /var/lib/systemd/coredump 2>/dev/null      # core.<comm>.<uid>.<boot>.<pid>.<time>.zst

# (b) plain core_pattern -> confirm by TYPE, never by name
find / -xdev -type f -size +10M \
     -exec sh -c 'file -b "$1" | grep -q "core file" && ls -lh "$1"' _ {} \; 2>/dev/null

# leftover installation media — usually the single biggest OS-layer win
du -xsh /hana/dl /sapdb /sapcd /install /stage 2>/dev/null | sort -rh
find / -xdev -type f \( -name '*.ZIP' -o -name '*.SAR' \) -size +1G \
     -printf '%10.1f GB  %TY-%Tm-%Td  %p\n' 2>/dev/null | sort -rn | head -20
```
```powershell
# Windows
Get-ChildItem -Path E:\usr\sap -Recurse -File -ErrorAction SilentlyContinue |
  Sort-Object Length -Descending | Select-Object -First 30 FullName,@{n='GB';e={[math]::Round($_.Length/1GB,2)}}
```

> **Read-only first.** Everything above is discovery. Deleting comes after the sized proposal is approved,
> and never with a wildcard on a path you have not listed first.

---

## 8. The deliverable

A space-reclamation assessment is not a list of transactions — it is a **costed table**:

| Candidate | Current | Est. reclaim | Method | Retention fix | Risk | Needs reorg? |
|---|---|---|---|---|---|---|
| `DBTABLOG` | 310 GB | 265 GB | `RSTBPDEL` + fix `rec/client` | yes | low | yes |
| `TST03` (TemSe) | 90 GB | 80 GB | `RSPO1041` + spool retention | yes | low | yes |
| Client 001 | 40 GB | 40 GB | `SCC5` | n/a | medium | yes |
| core dumps | 22 GB | 22 GB | OS delete | n/a | low | **no — immediate** |

Note the last column: **OS-layer deletions return space immediately; database deletions do not.** Lead the
proposal with the OS-layer wins for that reason, then the retention fixes, then anything needing a
reorganization window.

---

## OS note

Layers 1–3 are **OS-independent** (ABAP transactions and DB commands). Layer 4 is where platform matters —
the discovery commands above are given for **Linux, AIX and Windows**, and `du` differs between Linux
(`--max-depth`, `-h`) and AIX (`-g`, no `--max-depth`). Path layout is identical in shape
(`/usr/sap/<SID>/<INST>/work`) with Windows using a drive letter and UNC paths for `sapmnt`.

---

## Cross-references

- **`sap-housekeeping`** — the scheduled standard reorganization jobs that prevent most of this.
- **`sap-backup-recovery`** — log and archive space, and why a delete without a backup plan is risky.
- **`sap-client-copy-accelerator`** — a bulk delete/load leaves space that needs reclaiming afterwards.
- **`sap-db-command-reference`** — the per-database utilities used for reclaim operations.

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

- **[TT]** **SAP Note 2388483** — *How-To: Data Management for Technical Tables* (HAN-DB, v288,
  2026-07-27). **[V]** Retrieved and parsed via the SAP Notes MCP during authoring; it is the authoritative,
  continuously-updated table → area → Notes → report/transaction catalogue, **valid for all databases**, and
  the source for essentially every row of §3 and the retention items in §4. It also supplies the sizing
  entry points used in §2 — `HANA_Tables_LargestTables` with `ONLY_TECHNICAL_TABLES 'X'` (**SAP Note
  1969700**) and `Space_LargestTables` with `ONLY_BASIS_TABLES 'X'` (**SAP Note 1438410**) — states that it
  replaces SAP Note 706478, and cross-refers **SAP Note 16083** (standard/reorganization jobs), **SAP Note
  2190119** (S/4HANA technical job repository) and **SAP Note 3582156** (Data Management Guide / Data Volume
  Management). Individual per-area Notes cited inline in §3 (48400 spool/TemSe; 2335014 + 2362854 table
  logging; 195157 / 2057897 / 3039724 / 3742661 application log; 11838 short dumps; 40088 + 1574016 IDoc;
  375566 RFC queues; 802062 + 2363550 RFC logging; 2274315 workload collector; 3015823 change documents;
  36781 batch input; 966854 + 1641830 SAPoffice; 513454 ALE change pointers; 49545 + 1552169 work items;
  493156 + 505608 object links; 2034063 TAANA; 2651881 /SDF/SMON; 1052908 eCATT; 2229441 enhancement logs;
  36283 DDLOG) all come from this Note. https://me.sap.com/notes/2388483
- **[SAL]** **SAP Note 3137004** — *How to archive and delete audit log from DB* (BC-SEC-SAL, v17,
  2025-11-25). **[V]** Environment **SAP_BASIS 7.50 SP03 or higher**. Source for the whole of §5: checking
  **Recording Target**/**Recording Type** in **`RSAU_CONFIG`**; that the procedure applies to *Record in
  Database* + *Audit Log with Archive Interface* and **not** to *Retention Management* or *API mode*;
  **`RSAU_ADMIN`** → *Reorganize log table* → **Archive** → **`SARA`** with archiving object **`BC_SAL`**;
  setting delete jobs to **Not Scheduled**; jobs **`ARV_BC_SAL_WRI*`** / **`ARV_BC_SAL_DEL*`**; the
  **"Delete with Test Variant"** checkbox on **`RSAU_ARCHIVE_WRITE`**; tables **`RSAU_BUF_DATA`** /
  **`RSAU_LOG`**; and the explicit warning that *"Immediate deletion is not recommended … Due to legal
  regulation regarding the handling of audit logs, ensure that the archiving of the data was successful and
  that the data can be read BEFORE deleting"*. Related: **SAP Note 3346306** (reorganization blocked in API
  mode), **SAP Note 3467895** (tables appear empty in RSAU_ADMIN but occupy space), **SAP Note 3481355**
  (technical-settings permission error), **SAP Note 2191612** (*FAQ | Use of Security Audit Log as of SAP
  NetWeaver 7.50*). https://me.sap.com/notes/3137004
- **[RM]** **SAP Note 1749142** — *How to remove unused clients including client 001 and 066* (BC-CTS-CCO).
  **[V]** Used here for the post-deletion reorganization guidance and the DB-component pointers
  (`BC-DB-ORA`, `BC-DB-HDB`, `BC-DB-INF`, `BC-DB-MSS`, `BC-DB-SDB`), incl. Oracle **Note 646681**
  (*Reorganization of tables with BRSPACE*) and **Note 541538** (*FAQ: Reorganization*). Client assessment
  itself lives in [sap-dormant-clients](../sap-dormant-clients/SKILL.md).
  https://me.sap.com/notes/1749142
- **[HANA-AUD]** SAP HANA audit log management — `ALTER SYSTEM CLEAR AUDIT LOG`, and
  `ALTER AUDIT POLICY … SET RETENTION` from **SAP HANA 2.0 SPS 04** — SAP Notes **2159014**, **2308083**,
  **2599832**, **2676016**, **3084473**, as catalogued in SAP Note 2388483. **[V]**
- **[TEST]** Live validation during authoring **[V]** — assessment run read-only against an S/4HANA
  sandbox (SAP_BASIS **757**, kernel 789, HANA, client 100) over RFC. Findings that shaped §3a: only
  `RSSNAPDL` and `RSBCS_REORG` of 14 standard cleanup reports were scheduled (matched on
  `TBTCP-PROGNAME`), and the two tables they clean were the only small ones, while `BALHDR` (>1M),
  `BDCP2` (198,116), `TBTCO` (>100k) and `TSP01`/`TST03` (>10k each) had no scheduled cleanup. SJOBREPO was
  active yet did not cover those reports. Also established the four `RFC_READ_TABLE` limitations in §3a —
  logon-client-only visibility (`OPTION_NOT_VALID` when filtering `MANDT`), `DATA_BUFFER_EXCEEDED` without
  a field list, `ROWSKIPS` paging exhausting the work process on `DBTABLOG`, and `LIKE 'SAP\_%'` silently
  matching nothing.
- **[TEST-OS]** Live OS-layer validation **[V]** — same S/4HANA sandbox, root over SSH (SLES 15-SP3,
  single-host app+HANA). Findings that changed §7: **leftover installation media dominated everything** —
  `/hana/dl` held **351 GB** dated Sep–Oct 2023, being five install `.ZIP` files (~187 GB) *plus* the
  extracted `FAA/` media (~176 GB) *plus* SWPM — i.e. both the archive and its extraction retained after
  go-live, on a 1 TB filesystem sitting at 71 %. By contrast HANA trace was 2.7 GB (285 files) and the D00
  work directory 1.7 GB. **The `find -name 'core*'` command previously given in §7 was wrong**: it matched
  `core.py`, `core.so` and `core.rb`, reporting 39 "core dumps" totalling 0.7 MB where a `file`-type check
  confirmed **zero** real ELF core dumps. The pattern now requires a `file -b … | grep 'core file'`
  confirmation, and installation media is called out as its own row.
- **[HDIAG]** **SAP Note 2370780** — *How-To: Delete old HANA diagnosis files* (HAN-DB, v6, 2023-12-28).
  **[V]** Source for the per-extension rules (`.py`, `.old`, `.stat` removable; **`py.sap<SID>_HDB<nr>` and
  `hdb.sap<SID>_HDB<nr>` must not be** — they link to the Python runtime and `hdbdaemon`), for
  `dev_webdisp`/`dev_icm_sec`/`icm_port_list` being removable only while down, for **`M_TRACEFILES`** as the
  inventory view, and for **`ALTER SYSTEM REMOVE TRACES`** / **`ALTER SYSTEM CLEAR TRACES`**. Carries the
  explicit caveat that it *"is not a confirmation to delete any file from the system"*.
  https://me.sap.com/notes/2370780
- **[HCLEAN]** **SAP Note 2399996** — *How-To: Configuring automatic SAP HANA Cleanup with SAP HANACleaner*
  — the supported retention/automation path for HANA diagnosis files. https://me.sap.com/notes/2399996
- **[CORE]** Core-dump taxonomy **[V]** — established live: the test host's
  `/proc/sys/kernel/core_pattern` was `|/usr/lib/systemd/systemd-coredump …`, i.e. cores are **piped to a
  handler and never written as `core*` files**, so *any* filename-based search finds nothing regardless of
  pattern. The same host held 16 HANA `*.crashdump.*.trc` / `*.rtedump.*.trc` files (largest ~15 MB,
  indexserver, 2022) which no `core` pattern would ever match. `ulimit -c` was `unlimited`.
- **[ORA]** **SAP Note 1431751** — *Quick Reference for ADRCI and ADR* (BC-DB-ORA, v6). **[V]** Retrieved
  via the SAP Notes MCP during authoring. Source for: ADR replacing the deprecated `USER_DUMP_DEST` /
  `BACKGROUND_DUMP_DEST` / `CORE_DUMP_DEST`; the SAP-specific ADR base
  `DIAGNOSTIC_DEST = $SAPDATA_HOME/saptrace`; the ADR home layout `diag/rdbms/<db_name>/<ORACLE_SID>` with
  `trace` / `alert` / `incident` / **`cdump`** / `hm`; **`V$DIAG_INFO`** as the discovery view; the
  retention policy **`SHORTP_POLICY` 720 h (incident files and dumps)** and **`LONGP_POLICY` 8760 h
  (metadata)** purged automatically by `MMON`, with *"For SAP the recommendation is to use the Oracle
  Default settings"*; and the IPS packaging sequence. Alert-log trimming: **SAP Note 786032**.
  https://me.sap.com/notes/1431751
- **[DBOTHER]** Db2, SAP ASE, MaxDB and SQL Server diagnostic-file handling in
  [references/db-diagnostic-files.md](references/db-diagnostic-files.md) is given from **vendor-documented
  mechanisms and is explicitly marked unverified** — SAP Note searches for those platforms returned only
  CR lists for this S-user, which is an entitlement limitation rather than evidence the Notes do not
  exist. Confirm against the current SAP Note for your platform before acting. [G]
- **[JOBS]** **SAP Note 16083** — *Standard jobs, reorganization jobs* — the recurring-job baseline. If the
  standard jobs are not scheduled, scheduling them is the durable fix rather than a one-off deletion; see
  [sap-housekeeping](../sap-housekeeping/SKILL.md). **SAP Note 2190119** covers the S/4HANA technical job
  repository (`SJOBREPO`). [G]
- **[OS]** OS- and DB-layer file locations (`/usr/sap/<SID>/<INST>/work`, Oracle `saptrace`/`adump`, HANA
  `trace`) follow the layouts documented in
  [sap-log-reference](../sap-log-reference/SKILL.md) and
  [sap-housekeeping](../sap-housekeeping/SKILL.md); the `du`/`find`/PowerShell discovery commands here are
  standard platform tooling, not SAP-specific, and are read-only. [G]

**To confirm/deepen** — check current SAP Notes with the SAP Notes MCP (`search`, then `fetch` the note ID):
**2388483** before every assessment (it changes often — v288 at time of writing, with entries added
monthly), **3137004** before touching the Security Audit Log, **16083** to confirm the standard job
baseline, and the **reorganization Note for your database component** before promising any figure in the
"Est. reclaim" column.
