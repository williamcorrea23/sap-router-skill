# Per-DB backup & recovery commands

Reference detail for [../SKILL.md](../SKILL.md). Connect/start-stop for each DB is in
[../../sap-db-command-reference/SKILL.md](../../sap-db-command-reference/SKILL.md). ⚠️ all restore/recover
commands are destructive on the target — confirm recovery point and target first.

## SAP HANA (`hdb`)

- **PITR prereq:** `log_mode = normal` + automatic log backups on.
- **Backup:** `BACKUP DATA USING FILE ('<prefix>')`; `BACKUP DATA FOR <TENANT> …` (from SYSTEMDB).
- **Recover** (via HANA Cockpit / Studio *Recover Database*, or SQL `RECOVER DATA`): [B1]
  - most recent state · to a **point in time** · to a **specific data backup**; system DB vs tenant.
  - the DB is stopped during recovery; recovery reads the **backup catalog** + log backups.
- **Verify:** DB returns to ONLINE (`M_DATABASES`); check `backup.log` / `nameserver_alert`.

## Oracle (`ora`)

- **PITR prereq:** database in **ARCHIVELOG** mode; `brarchive` running.
- **Backup:** `brbackup -t online -m all`; `brarchive -sd` (logs). (or RMAN)
- **Restore/recover:** BR\*Tools — `brrestore` (restore files) then `brrecover` (guided): complete DB
  recovery, **point-in-time**, redo-log-only, whole-DB reset, or disaster recovery. RMAN equivalent:
  `RESTORE DATABASE; RECOVER DATABASE [UNTIL TIME '…']; ALTER DATABASE OPEN [RESETLOGS];`
- **Verify:** `SELECT status FROM v$instance;` OPEN; check `alert_<SID>.log`.

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

## IBM Db2 for LUW (`db6`)

- **PITR prereq:** `LOGARCHMETH1 = DISK:/…` (archive logging).
- **Backup:** `db2 backup database <SID> online to <path>`.
- **Restore/recover:**
  ```bash
  db2 restore database <SID> from <path> taken at <timestamp> [replace existing]
  db2 rollforward database <SID> to end of logs and complete        # or: to <ts> using local time
  ```
- **Verify:** `db2 connect to <SID>`; `db2 rollforward database <SID> query status`.

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

## Sources

Per DB, the admin/recovery guides cited in [../SKILL.md](../SKILL.md) §Sources ([B1]–[B6]) and the matching
files under sap-db-command-reference/references.
