# Oracle Data Guard under SAP — operations

Companion to the parent skill. Monitoring queries, protection-mode changes, switchover/failover
runbooks and standby backups. SAP's *permission* boundary is in the parent skill (**SAP Note
105047**, **[V]**); Oracle's *syntax* below is **[G]** from Oracle 19c documentation unless noted.

---

## 1. Monitoring — the queries that actually tell you something

```sql
-- role, mode, and whether the configured intent is being met
select database_role, open_mode, protection_mode, protection_level,
       switchover_status, db_unique_name, force_logging, flashback_on
from   v$database;
```

> **`protection_mode` ≠ `protection_level` means you are degraded.** Configured intent vs current
> reality. A configuration set to MAXIMUM AVAILABILITY sitting at RESYNCHRONIZING is not protecting
> you, and nothing else in the output says so as directly.

```sql
-- transport vs apply lag — distinguishes a network problem from an apply problem
select name, value, time_computed, datum_time
from   v$dataguard_stats
where  name in ('transport lag','apply lag','apply finish time');

-- redo apply / MRP running?
select process, status, thread#, sequence#, block#, blocks
from   v$managed_standby;

-- archive gaps
select * from v$archive_gap;

-- broker/DG messages, newest first
select timestamp, severity, error_code, message
from   v$dataguard_status
order  by timestamp desc
fetch  first 30 rows only;
```

**Reading the two lags together:**

| transport lag | apply lag | Likely cause |
|---|---|---|
| High | High | Network / redo shipping — look at the link, `LOG_ARCHIVE_DEST_n` state |
| ~0 | High | Redo arriving but not applying — MRP stopped, apply performance, standby I/O |
| ~0 | ~0 | Healthy |

From the broker: `SHOW CONFIGURATION;` then `SHOW DATABASE <name>;` gives the same picture with the
broker's own health verdict, and `VALIDATE DATABASE <name>;` is the pre-flight check.

---

## 2. Changing protection mode

Order matters — you cannot jump straight to a stricter mode without the right redo transport
attributes in place.

| Mode | Requires | Behaviour on standby failure |
|---|---|---|
| Maximum Performance | `ASYNC` | Primary continues; possible data loss |
| Maximum Availability | `SYNC` (or `SYNC NOAFFIRM` = Fast Sync, **SAP-permitted** **[V]**) | Primary continues, **degrades** to async, resynchronises later |
| **Maximum Protection** | `SYNC AFFIRM`, ≥1 standby | **Primary TERMINATES** **[V, Note 105047]** |

```sql
-- via SQL*Plus (broker: EDIT CONFIGURATION SET PROTECTION MODE AS MAXAVAILABILITY;)
alter database set standby database to maximize availability;
```

> **Maximum Availability is the right default for almost every SAP landscape.** It gives you zero
> data loss while the link is healthy and degrades gracefully when it is not. Maximum Protection
> converts a DR component failure into a production outage — see the parent skill's warning.

**Fast Sync (`SYNC NOAFFIRM`)** is explicitly permitted by SAP **[V]** and reduces the commit-latency
penalty of Maximum Availability by not waiting for the standby's disk write. Worth knowing when
Maximum Availability is rejected on performance grounds.

---

## 3. Planned switchover

```
DGMGRL> VALIDATE CONFIGURATION;          -- do this FIRST
DGMGRL> VALIDATE DATABASE '<standby>';
DGMGRL> SWITCHOVER TO '<standby>';
```

Before you start:

1. **Stop the SAP application servers** — a switchover is a role reversal, not transparent to SAP.
   See `sap-system-lifecycle` for stop ordering.
2. Confirm `switchover_status` on the primary reads `TO STANDBY` or `SESSIONS ACTIVE`.
3. Confirm apply lag is ~0.
4. Afterwards, repoint the SAP connection (`tnsnames.ora` / connect string) and restart the
   application tier.

Switchover is **lossless** and the old primary becomes a standby **automatically** — no `REINSTATE`
needed.

---

## 4. Unplanned failover

```
DGMGRL> FAILOVER TO '<standby>';
```

Then, to bring the old primary back as a standby:

```
DGMGRL> REINSTATE DATABASE '<old_primary>';
```

> **`REINSTATE` needs Flashback Database enabled on the old primary.** SAP permits Flashback Database
> (Note 966117) **[V]**. Without it, the old primary must be rebuilt from a backup — hours instead of
> minutes. **Enable it before you need it**; it cannot be enabled retroactively for an event that
> already happened.

```sql
-- check before you rely on it
select flashback_on from v$database;
```

**Fast-Start Failover (FSFO)** automates this with an **observer** process. SAP **allows FSFO but
provides no support for it** **[V, Note 105047]** — so if it misbehaves, SAP will not help. Weigh
that against the automation benefit, and make sure the customer knows the support position before it
is switched on.

---

## 5. Testing the standby without breaking it

```
DGMGRL> CONVERT DATABASE '<standby>' TO SNAPSHOT STANDBY;
-- ... open read-write, run the test ...
DGMGRL> CONVERT DATABASE '<standby>' TO PHYSICAL STANDBY;
```

A snapshot standby is open read-write and discards changes on conversion back — the clean way to
test DR without a rebuild. Redo continues to arrive while it is a snapshot; it is applied on
conversion back. **[G]**

**Restrictions [G]:** cannot convert while the standby is the FSFO target (**ORA-16668**); a snapshot
standby cannot be a switchover or FSFO target, though it can be a *manual* failover target when FSFO
is disabled.

> Do **not** confuse this with running SAP on the standby. Note 105047 is explicit: **you cannot
> start an SAP instance on a read-only database** **[V]**. Snapshot standby is for database-level
> testing, not for standing up an SAP system.

---

## 6. Backups from the standby

Offloading backups is one of the better reasons to run Data Guard. Points that matter under SAP:

- **RMAN is permitted** for backup/restore/recovery; cross-platform backup/restore from **12c**. **[V]**
- **Block Change Tracking** is permitted (Note 964619) **[V]** — makes standby-side incrementals worthwhile.
- **Archive-log retention must account for the standby.** An RMAN deletion policy that removes logs
  the standby has not yet applied produces **ORA-16724** (Note 2898813). Configure the deletion
  policy as `APPLIED ON ALL STANDBY` (or equivalent) rather than a bare retention window.
- BR*Tools integration and the SAP-side backup workflow live in `sap-backup-recovery`.

---

## 7. Setup outline

Full setup is Oracle-documented and site-specific; the SAP-relevant checkpoints are:

1. **Physical standby only** — logical standby is prohibited by SAP **[V]**.
2. Primary in `ARCHIVELOG` with `FORCE LOGGING`.
3. **Enable Flashback Database** on both sides (permitted by SAP, and the prerequisite for
   `REINSTATE`).
4. Standby redo logs on **both** databases — sized to match, one more group than the online redo.
5. `DB_UNIQUE_NAME` distinct per database; `LOG_ARCHIVE_CONFIG` listing both.
6. Configure the **broker** (`DG_BROKER_START=TRUE`) — SAP permits it and it removes most manual error.
7. Choose the protection mode deliberately — default to **Maximum Availability**.
8. `VALIDATE CONFIGURATION` before declaring it done, and **rehearse a switchover** before relying on it.

> The SAP-specific installation and system-copy implications (SID, connection strings, `tnsnames`)
> are outside Data Guard itself — see `sap-db-command-reference` and SAP's Oracle installation guides.
