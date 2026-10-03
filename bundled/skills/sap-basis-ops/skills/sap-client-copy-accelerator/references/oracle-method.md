# Oracle variant — database link (cross-system) and CTAS / parallel DML

Companion to the parent skill. **[V]** = read directly from SAP documentation; **[G]** = cited but
not read in full; **[A]** = analogue of the field-proven HANA method, adapted to Oracle mechanics and
not itself field-tested on the source refresh — treat as a design, verify on a test system first.

> ## This is not an invention — SAP documents it
>
> **SAP Note 857973, *"Deleting clients efficiently using Oracle"*** describes exactly this class of
> technique, including **`CREATE TABLE ... NOLOGGING PARALLEL <degree> AS SELECT`**, `TRUNCATE`,
> and dropping indexes before a large delete. **[V]**
>
> SAP's own framing, verbatim: *"only experts who can evaluate their effects may execute these
> procedures. SAP does not accept any responsibility for problems that may occur"*, and *"a
> prerequisite for all of the measures described below is that you **do not use the relevant clients
> in parallel**."* **[V]**
>
> So: sanctioned, but explicitly at your risk and only with the client quiesced.

**Where Oracle differs from HANA, and it matters:**

| Concern | HANA | Oracle |
|---|---|---|
| Cross-system read | SDA remote source + virtual table | **Database link** — `table@dblink` |
| Big delete cost | Version space | **UNDO** — `ORA-30036`, `ORA-01555` |
| Bulk insert | Plain `INSERT ... SELECT` | **Direct-path** `/*+ APPEND */`, optional `NOLOGGING` |
| Parallelism | N client processes | Either N sessions **or** native parallel DML |
| After the load | — | **Re-gather statistics**, rebuild indexes |

---

## A. Decide the strategy from the data shape

Note 857973's key insight: **if the client you are removing is most of the table, deleting row-by-row
is the wrong tool.** **[V]**

```sql
-- how much of the table is NOT the target client?
SELECT <CLIENTFLD>, COUNT(*) FROM <SCHEMA>.<TABLE> GROUP BY <CLIENTFLD>;
```

| Result | Strategy |
|---|---|
| Table contains **only** the target client | **`TRUNCATE TABLE`** — instant. Note 857973 gives the exact check **[V]** |
| Target client is **most** rows, a little else | **CTAS the keepers**, drop, rename (§B) **[V]** |
| Target client is a **minority** | **Batched DELETE** (§C) |

Note 857973's own single-client test **[V]**:

```sql
SELECT /*+ INDEX(<table> "<primary_index>") */ <client_field>, COUNT(*)
  FROM <table>
 WHERE <client_field> < '<deleted_client>' OR <client_field> > '<deleted_client>'
 GROUP BY <client_field>;
-- no rows returned  ⇒  safe to TRUNCATE TABLE <table>;
```

---

## B. CTAS + swap — SAP's documented fast path **[V]**

Best when the rows to **keep** are few relative to the rows to remove.

```sql
CREATE TABLE <TABLE>_TMP [NOLOGGING] [PARALLEL <degree>] AS
SELECT /*+ INDEX(<table> "<primary_index>") */ *
  FROM <TABLE>
 WHERE <client_field> < '<tgt>' OR <client_field> > '<tgt>';

DROP TABLE <TABLE>;
ALTER TABLE <TABLE>_TMP RENAME TO <TABLE>;
```

> ⚠️ **`CREATE AS SELECT` drops column defaults.** Note 857973 is explicit — you must restore them:
> ```sql
> ALTER TABLE <TABLE> MODIFY (<column> DEFAULT <default>);
> ```
> **[V]** You must also **recreate indexes and CBO statistics**. Forgetting either leaves the table
> functionally wrong or catastrophically slow.
>
> The note offers a variant that avoids the defaults problem — CTAS to a temp table, `TRUNCATE` the
> original, `INSERT` back, drop the temp — at the cost of copying the data **twice**. **[V]**

> ## 🛑 `NOLOGGING` is not free, and Data Guard ignores it
>
> `NOLOGGING` skips redo for the load, which is the bulk of the speed-up — and it means **the loaded
> data is not recoverable from archive logs**. Any restore through that window leaves the segments
> corrupt/unrecoverable until you reload.
>
> **On a Data Guard primary, `FORCE LOGGING` is normally enabled and silently overrides `NOLOGGING`** —
> you get the recoverability but not the speed. Check before you plan around it:
> ```sql
> SELECT force_logging FROM v$database;
> ```
> See **`sap-oracle-dataguard`**. And take a backup/restore point first either way
> (`sap-backup-recovery`). **[A]**

---

## C. Batched DELETE — when the keepers are the majority

One monolithic `DELETE` of tens of millions of rows will exhaust UNDO (`ORA-30036`) or run long
enough to hit `ORA-01555`. Delete in **committed batches**:

```sql
BEGIN
  LOOP
    DELETE FROM <SCHEMA>.<TABLE> WHERE <CLIENTFLD> = '<TGT>' AND ROWNUM <= 500000;
    EXIT WHEN SQL%ROWCOUNT = 0;
    COMMIT;
  END LOOP;
END;
/
```

Note 857973 documents SAP's own report-based equivalents and, usefully, **their trade-offs** **[V]**:

| Report | Behaviour | Cost |
|---|---|---|
| `YKDELCLS` | Single transaction to COMMIT | Needs UNDO big enough for the **whole** delete |
| `ZTABDELE` | SELECT-then-delete in blocks | **SELECTs get slower as it progresses** — each rescans the deleted area. Use the largest `NROWS` you can, and rebuild/coalesce the index periodically |
| `ZSDELCUR` | Keeps the cursor open across commits | Avoids the slowdown, but **higher `ORA-01555` risk** |
| `ZSDELDIS` | Groups by the second key field | Smaller commits, but **not suitable for all tables** |

Reports themselves are in Note **365304** **[G]**.

**Dropping indexes first** is documented and effective — it removes index maintenance from the
delete — but only when *"there is no risk of performance problems or duplicate keys"*, i.e. the
system is genuinely quiesced. Rebuild afterwards. **[V]**

---

## D. Cross-system load via database link

### D1. Create the link

> ## 🛑 Licence gate applies here
>
> `CREATE DATABASE LINK` is the cross-database step. **Do not run it until the user has explicitly
> confirmed licence eligibility** — see the parent skill **§0a**, and Note 581312 on why direct DB
> access is bounded to *system administration*.


```sql
CREATE DATABASE LINK <LINK_NAME>
  CONNECT TO <SOURCE_SCHEMA_OWNER> IDENTIFIED BY "<pw>"
  USING '<tns_alias_or_easy_connect>';

SELECT COUNT(*) FROM <TABLE>@<LINK_NAME> WHERE ROWNUM <= 1;   -- smoke test
```

Same ownership logic as the HANA variant: **connect as the schema owner**, not a privileged account
with no rights on the application schema.

> ## Licence and support: two different questions, both answered
>
> **Licence — Note 581312** quotes SAP Price List §C.11.1 and is unusually specific **[V]**:
> - Direct DB access is permitted for *"tools from the areas of **system administration and
>   monitoring**"* — which is what a DBA refreshing a system is doing.
> - **`ABAP using database links` is named as a permitted interface.**
> - **Not** permitted: *"external tools to create automatic SAP system copies"* performing
>   *"querying/changing/creating data in the database"*. **Automating this into a product is the
>   prohibited pattern; running it by hand as an administrator is not.**
> - *"The use of external software for database migration is permitted… as long as this is a
>   **one-time process that will not be repeated**."*
>
> **No extra option licence.** Note **740897**'s option table (Partitioning, Advanced Compression,
> RAC, Data Guard, In-Memory, Multitenant…) **does not list database links or parallel DML** —
> they are base Enterprise Edition, which SAP requires anyway. **[V]**
>
> **Support — Note 105047**: *"Distributed Transactions: Use permitted, but no SAP support"*;
> *"Oracle Gateway: Can be used, but no SAP support"* **[V]**. So if the link itself misbehaves,
> that is an Oracle conversation, not an SAP one.
>
> ⚠️ **If the customer licensed Oracle directly from Oracle rather than through SAP, none of the
> above governs** — their own Oracle agreement does. **[V, 740897]**

### D2. Load in parallel, partitioned

**Option 1 — N sessions, one per partition** (mirrors the HANA method; simplest to throttle and to
restart a single failed partition):

```sql
ALTER SESSION ENABLE PARALLEL DML;
INSERT /*+ APPEND */ INTO <SCHEMA>.<TABLE>
SELECT * FROM <TABLE>@<LINK_NAME>
 WHERE <CLIENTFLD>='<SRC>' AND <PARTKEY>='<value>';
COMMIT;
```

```bash
# throttled launcher, one sqlplus per partition
for P in 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026; do
  while [ "$(pgrep -c sqlplus)" -ge 6 ]; do sleep 3; done
  sqlplus -s /@<TNS_ALIAS> @load_part.sql "$P" > "/tmp/load/l_$P.out" 2>&1 &
  echo "launched $P"
done
wait
```

**Option 2 — native parallel DML**, one statement:

```sql
ALTER SESSION ENABLE PARALLEL DML;
INSERT /*+ APPEND PARALLEL(t,6) */ INTO <SCHEMA>.<TABLE> t
SELECT * FROM <TABLE>@<LINK_NAME> WHERE <CLIENTFLD>='<SRC>';
COMMIT;
```

Simpler, but **all-or-nothing** — a failure at 90 % rolls back everything, whereas per-partition
sessions lose only one partition. For a long load into a refresh window, **prefer Option 1**. **[A]**

> ⚠️ **Direct-path (`/*+ APPEND */`) locks the table exclusively** and the data is **not readable in
> the same transaction until you `COMMIT`**. Do not interleave verification queries inside the
> session. Also note parallel DML **ends the transaction** — plan your commits deliberately. **[A]**

### D3. Local variant — rewriting the client column

Same constraint as HANA: you cannot `SELECT *` when the client value must change. Build the column
list from the data dictionary, excluding virtual columns:

```sql
SELECT column_name
  FROM all_tab_columns
 WHERE owner='<SCHEMA>' AND table_name='<TABLE>'
   AND virtual_column='NO'
 ORDER BY column_id;
```

Then substitute a literal for the client column in the select list, exactly as in the HANA §B2
pattern. **[A]**

---

## E. Oracle-specific cleanup

```sql
DROP DATABASE LINK <LINK_NAME>;          -- holds source credentials
DROP TABLE <TABLE>_TMP;                  -- any CTAS temp table
-- recreate indexes if you dropped them, then:
EXEC DBMS_STATS.GATHER_TABLE_STATS('<SCHEMA>','<TABLE>', degree=>8, cascade=>TRUE);
```

- **Re-gather statistics.** A freshly loaded table with stale or missing stats produces terrible
  plans — and unlike HANA, Oracle will not recover on its own. Note **838725** covers SAP's
  dictionary/system statistics expectations **[G]**.
- **Rotate the password** used in `CREATE DATABASE LINK` — cleartext in the DDL.
- **Restore `FORCE LOGGING` / archiving** if you changed it, and confirm any **standby is still
  valid**. If you loaded with `NOLOGGING` on a primary that was *not* force-logging, the standby now
  has unrecoverable blocks and needs those datafiles refreshed — see `sap-oracle-dataguard`. **[A]**
- **Reclaim space** after a large delete — the segment is not smaller just because the rows are gone
  (`sap-space-reclaim`).

---

## F. Oracle client-copy tuning worth doing first

Before any bypass, the supported parameter route (parent skill §2):

| Oracle version | Parameter note |
|---|---|
| 12.1 | **1888485** |
| 12.2 / 18c / 19c | **2470718** |
| 11.2 | **1431798** |

Plus **838725** (dictionary and system statistics) and **1171650** (automated parameter check).
All **[G]**, all referenced from Note **2163425** **[V]**.
