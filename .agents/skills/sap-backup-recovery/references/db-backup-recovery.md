# Per-DB backup & recovery commands

Reference detail for [../SKILL.md](../SKILL.md). Connect/start-stop for each DB is in
[../../sap-db-command-reference/SKILL.md](../../sap-db-command-reference/SKILL.md). ⚠️ all restore/recover
commands are destructive on the target — confirm recovery point and target first.

## SAP HANA (`hdb`)

> **Establish two things first:** the revision (`SELECT VERSION FROM M_DATABASE;`) and whether this is
> **MDC** (tenants) or single-container — system-DB and tenant recovery are different operations. If
> **encryption or Local Secure Store (LSS)** is active, read
> [backup-encryption-keys.md](backup-encryption-keys.md) **before** restoring anywhere but the source host.

- **PITR prereq:** `log_mode = normal` + automatic log backups on.
- **Backup:** `BACKUP DATA USING FILE ('<prefix>')`; `BACKUP DATA FOR <TENANT> …` (from SYSTEMDB).
- **Recover** (via HANA Cockpit / Studio *Recover Database*, or SQL `RECOVER DATA`): [B1]
  - most recent state · to a **point in time** · to a **specific data backup**; system DB vs tenant.
  - the DB is stopped during recovery; recovery reads the **backup catalog** + log backups.
- **Verify:** DB returns to ONLINE (`M_DATABASES`); check `backup.log` / `nameserver_alert`.

**Version dimension — `SELECT VERSION FROM M_DATABASE;`**
- **1.0 vs 2.0**: 2.0 is **MDC by definition** (SYSTEMDB + tenants). On 2.0 you must state *which* database
  you are recovering — SYSTEMDB and each tenant are separate recovery operations with separate catalogs.
  Recovering SYSTEMDB does **not** recover the tenants. [G]
- **Tenant recovery** runs from SYSTEMDB (`RECOVER DATA FOR <tenant> …`); a tenant can be recovered while
  other tenants stay up. MDC background: **SAP Note 2101244**.
- **System replication** changes both backup and recovery planning — dedicated FAQ, **SAP Note 2165547**.
  Do not plan a recovery in an SR landscape from the standalone procedure.
- **Encryption / LSS**: if data, log or backup encryption is on, root keys are a separate asset and a
  cross-host recovery can fail at service start with a corruption-shaped error — see
  [backup-encryption-keys.md](backup-encryption-keys.md). **[V]**
- Hub note: **SAP Note 1642148** — *FAQ: SAP HANA Database Backup & Recovery*.

## Oracle (`ora`)

- **PITR prereq:** database in **ARCHIVELOG** mode; `brarchive` running.
- **Backup:** `brbackup -t online -m all`; `brarchive -sd` (logs). (or RMAN)
- **Restore/recover:** BR\*Tools — `brrestore` (restore files) then `brrecover` (guided): complete DB
  recovery, **point-in-time**, redo-log-only, whole-DB reset, or disaster recovery. RMAN equivalent:
  `RESTORE DATABASE; RECOVER DATABASE [UNTIL TIME '…']; ALTER DATABASE OPEN [RESETLOGS];`
- **Verify:** `SELECT status FROM v$instance;` OPEN; check `alert_<SID>.log`.

### ⚠️ Multitenant (CDB/PDB) changes the recovery model — check FIRST

```sql
SELECT cdb FROM v$database;      -- YES = container database, everything below applies
```

**The gate is the BR\*Tools patch level, not just the Oracle version.** BR\*Tools 7.40 supports
multitenant **as of Patch 24** (limited), and: **[V, MT]**

| BR\*Tools 7.40 patch | Adds |
|---|---|
| **24** | multitenant support, limited |
| **27** | **restore/recovery of individual PDBs**; **tablespace point-in-time recovery**; the `-rpd\|-recov_pdb` option |
| **30** | *Recreate database* and **Manage data encryption** (BRSPACE) |

Prerequisites: Oracle **12.1.0.2 or higher**, Oracle Client 12c on the DB server. **Multitenant RAC is not
released.** SAP states multitenant support is "to the best of our knowledge and ability" — no guaranteed
root-cause analysis or fix. **[V, MT]**

🚨 **The single most consequential option — `-rpd|-recov_pdb`:** **[V, MT]**

```
-v|-rpd|-recov_pdb <pdb_name>|<pdb_name_list>      # default: the ENTIRE container database
```

> **If `-rpd` is not specified, the entire container database with all pluggable databases is stopped at
> the start of the recovery.** On a container hosting three SAP systems, omitting one option takes down
> all three instead of one.

And the blast radius differs **by recovery type**, which is the part people miss: **[V, MT]**

| BRRECOVER function | Effect on PDBs *not* named in `-rpd` |
|---|---|
| **Complete (media) recovery** | **Unaffected** — if they were open they stay open and usable throughout |
| **Database point-in-time recovery** | **Plugged out** before restore, plugged back in after → **all PDBs unavailable for the whole recovery** |
| **Tablespace point-in-time recovery** | same — and `-rpd` **must** be set, to a single PDB |
| **Database reset** | same plug-out/plug-in behaviour |

Before a complete recovery, **the DBA must determine which PDBs are actually affected by the media
errors** — that determination is what makes `-rpd` correct. To cut downtime for uninvolved PDBs, they can
be plugged into another container on the same host/Oracle home (BRRECOVER generates the XML for it), then
plugged back later — skip the automatic plug-in if you do. Flashback applies **only to the whole CDB**. **[V, MT]**

Configuration that must exist in `init<DBSID>.sap`: **[V, MT]**

```
active_pdbs = all_pdbs | (<PDB>[:<SAPSID>],…)   # PDBs BR*Tools may administer; inactive ones are skipped by backups
primary_pdb = any_pdb | <PDB_NAME>              # recommended: set it — global ops and logs land here
```

Backups and archive-log backups are **global** operations (a full backup covers the CDB and *all* PDBs),
so they are scheduled **once**, under the `<sapsid>adm` tied to the primary PDB. `ORA_PDB_NAME` (or the
`-pdb` option) selects the *working* PDB for local operations. PDB-scoped partial backups:
`brbackup -m all:<pdb_name>` — **counts as a partial, not a full, backup**. **[V, MT]**

Users: BRBACKUP/BRARCHIVE connect as **SYSBACKUP** (new in 12c); `sapdba_role.sql` must be run **once for
the CDB and once per PDB**. **[V, MT]**

## SAP ASE / Sybase (`syb`)

- **PITR prereq:** `trunc log on chkpt = false`; regular `dump transaction`.
- **Backup:** `dump database <DB> to '<file>'`; `dump transaction <DB> to '<file>'`.
- **Restore/recover** (via `isql`):
  ```sql
  load database <DB> from '<full_dump>'
  load transaction <DB> from '<log_dump>'       -- repeat in order; PIT: ... with until_time = '<ts>'
  online database <DB>                            -- bring it back online
  ```
- **Verify:** `sp_helpdb <DB>`; errorlog `<SERVER>.log`.

**Version dimension — check before quoting:** `select @@version`
- **Cumulative dumps** (`dump database … cumulative`) are an **ASE 16.0** capability — not available on
  15.7. Confirm the exact SP for your release before planning a strategy around them. [G]
- **Dump compression** syntax and default levels differ across 15.7 / 16.0.
- **`load … with listonly`** to inspect a dump before loading it — do this when the dump's origin or level
  is uncertain; it is read-only.
- OS certification per release: **SAP Note 1941500**; hub note for ASE on Business Suite/BW: **2162183**.

## IBM Db2 for LUW (`db6`)

- **PITR prereq:** `LOGARCHMETH1 = DISK:/…` (archive logging).
- **Backup:** `db2 backup database <SID> online to <path>`.
- **Restore/recover:**
  ```bash
  db2 restore database <SID> from <path> taken at <timestamp> [replace existing]
  db2 rollforward database <SID> to end of logs and complete        # or: to <ts> using local time
  ```
- **Verify:** `db2 connect to <SID>`; `db2 rollforward database <SID> query status`.

**Version dimension — check with `db2level`:** **[V, DB6F]**
- **Backup compression**: Db2 **Version 8 and higher**. **Log archive compression**: Db2 **10.1 and higher**.
- **HADR standbys**: Db2 **8.2–9.7 support one** standby; **Db2 10.1 extended this to up to three**
  standbys with **spooling and delayed replay** — which changes both your DR options and what a "restore"
  even means in that landscape.
- **`DB2_ONLINERECOVERY`** is supported **with limitations** — do not assume online recovery behaves as the
  IBM docs describe without checking Note 1555903.
- **Native encryption** is a supported feature — key handling in
  [backup-encryption-keys.md](backup-encryption-keys.md).
- Supported versions and fix packs: **101809**. End of support dates: **1168456**. Feature support matrix:
  **1555903**. Admin guide: `help.sap.com/viewer/db6_admin`.

## SAP MaxDB / liveCache (`ada`)

- **PITR prereq:** log mode not `OVERWRITE`; automatic log backup on.
- **Backup:** `dbmcli … backup_start <template>` (data), `… backup_start <logtemplate>` (log).
- **Restore/recover:** put DB in **ADMIN**, then `dbmcli`:
  ```
  recover_start <template> DATA            # restore data backup
  recover_start <logtemplate> LOG          # then apply log(s); PIT via recovery-until options
  recover_replace / recover_config         # media/config-driven recovery
  ```
  (Database Studio has a Recovery Wizard for the same.) → then `db_online`.
- **Verify:** `db_state` → ONLINE; `KnlMsg`.

**Version dimension — check with `dbmcli … dbm_version`:**
- MaxDB 7.8 vs 7.9 differ in `dbmcli` options and in Database Studio's recovery wizard. Confirm against the
  MaxDB documentation for **your** build before scripting a recovery. [G]
- ⚠️ **Coverage here is thinner than the other platforms.** SAP Notes searches on this S-user return
  markedly less for MaxDB, which is an **entitlement limitation, not an absence of documentation**. Treat
  the above as the shape of the procedure and verify specifics per release.

## Microsoft SQL Server (`mss`) — Windows only

- **PITR prereq:** database **FULL** recovery model + log backups.
- **Backup:** `BACKUP DATABASE [<SID>] TO DISK='…' WITH INIT`; `BACKUP LOG [<SID>] TO DISK='…'`.
- **Restore/recover:**
  ```sql
  RESTORE DATABASE [<SID>] FROM DISK='<full.bak>' WITH NORECOVERY, REPLACE;
  RESTORE LOG      [<SID>] FROM DISK='<log.trn>'  WITH RECOVERY [, STOPAT='<yyyy-mm-dd hh:mm:ss>'];
  ```
  (`NORECOVERY` on each restore until the last; `RECOVERY` on the final one to bring the DB online.)
- **Verify:** `SELECT state_desc FROM sys.databases WHERE name='<SID>';` ONLINE; `ERRORLOG`.

**Version dimension — check with `SELECT @@VERSION;` and `SERVERPROPERTY('ProductLevel')`:**
- **Backup to URL** (Azure Blob) availability and syntax differ by release — relevant for any cloud-hosted
  system. [G]
- **TDE with backup compression** behaviour changed across releases; see
  [backup-encryption-keys.md](backup-encryption-keys.md) — and note a TDE database **cannot** be restored
  elsewhere without the certificate and private key.
- **Accelerated Database Recovery (ADR)** changes recovery/rollback behaviour on newer releases.
- Find the **release-planning note for your version** (pattern: **1076022** for SQL Server 2008/R2) and the
  PAM entry — see [version-support-matrix.md](version-support-matrix.md). [G]

## Sources

Per DB, the admin/recovery guides cited in [../SKILL.md](../SKILL.md) §Sources ([B1]–[B6]) and the matching
files under sap-db-command-reference/references. In addition:

- **[MT]** **SAP Note 2333995** — *BR\*Tools support for Oracle multitenant database* (BC-DB-ORA-DBA, v16,
  2026-07-13). **[V]** Retrieved via the SAP Notes MCP during authoring. Source for the entire multitenant
  section: the BR\*Tools 7.40 patch gates (24 / 27 / 30), the Oracle 12.1.0.2 + Oracle Client 12c
  prerequisite, multitenant RAC not being released, the `-rpd|-recov_pdb` option and the fact that omitting
  it stops the **entire container database**, the per-recovery-type plug-out behaviour, `active_pdbs` /
  `primary_pdb`, `brbackup -m all:<pdb>` counting as a partial backup, SYSBACKUP, and `sapdba_role.sql` per
  PDB. Related: **2336881** (*Using Oracle Multitenant with SAP NetWeaver based Products*), **2335850**
  (transform an existing DB into a PDB), **134592** (`sapdba_role.sql`), **3654508** (BRSPACE RC 9999 with
  multitenant). https://me.sap.com/notes/2333995
- **SAP Note 1642148** — *FAQ: SAP HANA Database Backup & Recovery* (HAN-DB-BAC) — the HANA hub note. **[V]**
- **SAP Note 2165547** — *FAQ: … in an SAP HANA System Replication Landscape* (HAN-DB-BAC). **[V]**
- **SAP Note 2101244** — *FAQ: SAP HANA Multitenant Database Containers (MDC)* (HAN-DB). **[V]**
- **[DB6F]** **SAP Note 1555903** — *DB6: Supported IBM Db2 Database Features* (BC-DB-DB6, v64,
  2024-12-17). **[V]** Retrieved via the SAP Notes MCP during authoring. Source for the Db2 version gating:
  backup compression from V8, log archive compression from 10.1, HADR one standby in 8.2–9.7 versus up to
  three with spooling and delayed replay from 10.1, native encryption as supported, and
  `DB2_ONLINERECOVERY` as supported *with limitations*. Points at the release-independent *Database
  Administration Guide: SAP on IBM Db2 for LUW* (`help.sap.com/viewer/db6_admin`).
  https://me.sap.com/notes/1555903
- Version/support matrices and the PAM procedure: [version-support-matrix.md](version-support-matrix.md).
- Encryption and key management: [backup-encryption-keys.md](backup-encryption-keys.md).
