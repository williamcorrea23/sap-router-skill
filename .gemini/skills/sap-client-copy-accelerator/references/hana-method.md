# HANA variant — SDA remote source (cross-system) and column-list rewrite (local)

Companion to the parent skill. **[F]** = proven in the field on the S/4HANA QA refresh this skill
comes from; **[V]** = verified against SAP documentation; **[G]** = cited.

Two shapes, and they differ more than you would expect:

| Scenario | Mechanism | Client field |
|---|---|---|
| **Remote** — source system → target system (SCC9) | **Smart Data Access**: remote source + virtual table | unchanged, `SELECT *` works |
| **Local** — client → client in the *same* tenant (SCCL) | plain SQL, no SDA | **must be rewritten**, so `SELECT *` is impossible |

---

## A. Remote — cross-system via Smart Data Access

### A1. Create the remote source on the TARGET tenant

> ## 🛑 Licence gate applies here
>
> `CREATE REMOTE SOURCE` is the cross-database step. **Do not run it until the user has explicitly
> confirmed licence eligibility** — see the parent skill **§0a**. Asking afterwards is not a gate.


```sql
CREATE REMOTE SOURCE <SRC_NAME> ADAPTER "hanaodbc"
  CONFIGURATION 'ServerNode=<source_host>:<source_tenant_sql_port>'
  WITH CREDENTIAL TYPE 'PASSWORD'
  USING 'user=<SOURCE_SCHEMA_OWNER>;password=<pw>';
```

> ## 🛑 Connect as the SOURCE SCHEMA OWNER, not `SYSTEM`
>
> This is the trap that costs the most time. **[F]**
>
> `SYSTEM` has **no rights on the application schema** and **cannot grant them to itself** — a
> `GRANT SELECT ON <SCHEMA>.<TABLE> TO SYSTEM` executed as `SYSTEM` fails with
> **"grantor and grantee are identical"**. The grant has to be issued **by the owner**, from the
> *source* system's own credentials.
>
> The simple path is to make the remote source connect **as the schema owner** (typically
> `SAP<SID>`), which needs no grant at all.

**Privilege needed to create it:** `CREATE REMOTE SOURCE` — the tenant's `SYSTEM`/`DBADMIN`, not the
application-schema user. If you cannot get it, this route is closed; use export/import or the
supported levers instead. Do **not** reset a tenant `SYSTEM` password to force it.

**Find the source tenant's SQL port** (from the source system):

```sql
SELECT DATABASE_NAME, SERVICE_NAME, PORT, SQL_PORT
  FROM SYS_DATABASES.M_SERVICES WHERE SERVICE_NAME='indexserver';
```

### A2. Create the virtual table and grant it

```sql
CREATE VIRTUAL TABLE <LOCALSCHEMA>.V_<TABLE>_SRC
    AT <SRC_NAME>."<SOURCE_DB>"."<SOURCE_SCHEMA>"."<TABLE>";

GRANT SELECT ON <LOCALSCHEMA>.V_<TABLE>_SRC TO <TARGET_SCHEMA_OWNER>;
```

**Smoke-test before you load anything** — one cheap query proves the whole chain (network, ODBC,
credentials, grants):

```sql
SELECT COUNT(*) FROM <LOCALSCHEMA>.V_<TABLE>_SRC
 WHERE <CLIENTFLD>='<SRC_CLIENT>' AND <PARTKEY>='<one value>';
```

If that returns 0, try another partition value before assuming the chain is broken — an empty
fiscal year looks identical to a broken remote source.

### A3. Delete the target-client rows natively

```sql
-- ALWAYS look before you delete: which clients exist, and how big?
SELECT <CLIENTFLD>, COUNT(*) FROM <SCHEMA>.<TABLE> GROUP BY <CLIENTFLD>;

DELETE FROM <SCHEMA>.<TABLE> WHERE <CLIENTFLD>='<TGT_CLIENT>';
```

> ⚠️ **The `WHERE` clause is the entire safety mechanism.** A target system commonly holds another
> client whose data must survive. Run the `GROUP BY` first, every time, and read it.

Being outside a work process is the point: this is **immune to `rdisp/max_wprun_time`
softcancel**, which is what kept killing the copy's own delete step. **[F]** 72 M rows in ~45 s. **[F]**

### A4. Launch the parallel load

One `INSERT` per partition, throttled. Each partition is **one transaction**, so the row count jumps
in chunks as each commits — in-flight rows are invisible until then. Confirm streams are alive with
`M_ACTIVE_STATEMENTS`, not by watching `COUNT(*)`.

```sql
INSERT INTO <SCHEMA>.<TABLE>
SELECT * FROM <LOCALSCHEMA>.V_<TABLE>_SRC
 WHERE <CLIENTFLD>='<SRC_CLIENT>' AND <PARTKEY>='<value>';
```

**Windows launcher** (SAP app servers are often Windows; `hdbsql` lives in the client directory):

```powershell
$hdbsql   = "E:\usr\sap\<SID>\hdbclient\hdbsql.exe"
$parts    = 2016..2026          # your partition values
$throttle = 6
New-Item -ItemType Directory -Force -Path C:\temp\load | Out-Null
foreach ($p in $parts) {
  while (@(Get-Process hdbsql -ErrorAction SilentlyContinue).Count -ge $throttle) { Start-Sleep 3 }
  $sql = "INSERT INTO <SCHEMA>.<TABLE> SELECT * FROM <LOCALSCHEMA>.V_<TABLE>_SRC " +
         "WHERE <CLIENTFLD>='<SRC_CLIENT>' AND <PARTKEY>='$p'"
  Start-Process -FilePath $hdbsql `
    -ArgumentList @("-U","DEFAULT","-A",$sql) `
    -RedirectStandardOutput "C:\temp\load\l_$p.out" `
    -RedirectStandardError  "C:\temp\load\l_$p.err" `
    -WindowStyle Hidden
  Write-Output "launched $p"
  Start-Sleep 1
}
Write-Output "all launched"
```

> ## 🛑 `Start-Job` does not work here — use `Start-Process`
>
> **PowerShell `Start-Job` runspaces cannot resolve the per-user `hdbuserstore` DEFAULT key.** Jobs
> fail silently and report **0 rows**, which looks exactly like "the query returned nothing". **[F]**
> `Start-Process` spawns real processes with the full user environment, so the key resolves.

> ## ⚠️ Two tells that save you an hour
>
> **"all launched" appears instantly** ⇒ every insert **errored immediately**. A real multi-million-row
> insert holds `hdbsql` busy and paces the throttle. Read `l_<part>.err`. **[F]**
>
> **Keep the launcher window open until "all launched" prints.** Already-launched `Start-Process`
> children are independent and survive, but **queued partitions only fire while the parent loop is
> alive**. Close it early and those partitions never start. **[F]**

On Linux the same logic is a `for` loop with `&` and a `wait`-based throttle; the `hdbuserstore`
caveat does not apply.

---

## B. Local — same tenant, client → client

No SDA, no network. But the client field **must change**, so you cannot `SELECT *` — you need an
explicit column list with the client column replaced by a literal.

### B1. Build the column list

```sql
SELECT COLUMN_NAME FROM SYS.TABLE_COLUMNS
 WHERE SCHEMA_NAME='<SCHEMA>' AND TABLE_NAME='<TABLE>'
   AND GENERATION_TYPE IS NULL
 ORDER BY POSITION;
```

**`GENERATION_TYPE IS NULL` excludes generated columns**, which cannot be inserted into. Omit it and
the insert fails. **[F]**

> ## ⚠️ `hdbsql -A` corrupts a column list
>
> `-A` is **aligned/bordered** output, so every value comes back as `| COLNAME |` and those pipes land
> in your SQL: **`257 sql syntax error near "|"`**. Use **`-x`** instead. **[F]**
>
> Even then the header alias row leaks, so filter it:
> ```powershell
> $cols = & $hdbsql -U DEFAULT -x $q |
>         Where-Object { $_ -match '^[A-Za-z0-9_]+$' -and $_ -ne 'COLUMN_NAME' }
> ```
> Note the asymmetry with the loader above, which *does* use `-A` — for a bulk `INSERT` the output
> formatting is irrelevant; for **capturing values** it is fatal.

### B2. Build the two lists and load

The insert list is the columns as-is; the select list is identical **except the client column becomes
a literal**:

```powershell
$insertCols = ($cols) -join ','
$selectCols = ($cols | ForEach-Object {
                 if ($_ -eq '<CLIENTFLD>') { "'<TGT_CLIENT>'" } else { $_ } }) -join ','
```

```sql
INSERT INTO <SCHEMA>.<TABLE> (<insertCols>)
SELECT <selectCols> FROM <SCHEMA>.<TABLE>
 WHERE <CLIENTFLD>='<SRC_CLIENT>' AND <PARTKEY>='<value>';
```

Same throttled `Start-Process` launcher as §A4. Local is dramatically faster — no network, no ODBC:
**~6 minutes** for 105 M rows versus ~70 minutes remote. **[F]**

> ⚠️ **The local delete can *decelerate*.** Deleting 85 M rows in one transaction ran at ~180 K/min
> and collapsed to ~18 K/min under single-transaction version-space pressure — ETA in **days**. **[F]**
> If you see the rate falling, kill it and delete in **committed batches** instead of one statement.

---

## C. Monitoring while it runs

```sql
-- are the streams actually live?
SELECT STATEMENT_STRING, EXECUTION_TIME FROM M_ACTIVE_STATEMENTS
 WHERE STATEMENT_STRING LIKE '%<TABLE>%';

-- progress (jumps per commit, does not climb smoothly)
SELECT <PARTKEY>, COUNT(*) FROM <SCHEMA>.<TABLE>
 WHERE <CLIENTFLD>='<TGT_CLIENT>' GROUP BY <PARTKEY> ORDER BY <PARTKEY>;
```

Watch **log volume** and **memory** on the target — and if the target is an **HSR primary**, the
secondary is receiving every row. Check lag and log-volume headroom there too
(`sap-hana-system-replication`).

---

## D. HANA-specific cleanup

```sql
DROP VIRTUAL TABLE <LOCALSCHEMA>.V_<TABLE>_SRC;
DROP REMOTE SOURCE <SRC_NAME>;              -- holds source credentials
REVOKE SELECT ON <SCHEMA>.<TABLE> FROM <USER>;   -- any temp grant on the SOURCE
DROP TABLE <SCHEMA>.<TABLE>_STG;            -- any staging table
```

```bash
hdbuserstore DELETE <TEMP_KEY>
```

**Rotate any password that appeared in a `CREATE REMOTE SOURCE`** — it was cleartext in the SQL text,
and therefore plausibly in shell history, `ps` output, and trace files. **[F]**
