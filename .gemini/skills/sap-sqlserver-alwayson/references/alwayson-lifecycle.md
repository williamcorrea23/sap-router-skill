# SQL Server Always On under SAP — lifecycle sequences

Companion to the parent skill. All sequences **[V]** from **SAP Note 1772688** v25.

> **These are the Note's own high-level steps, in order.** Note 1772688 states that only its
> procedures are supported and that it deliberately omits per-customer detail. **Read the live Note
> before executing** — this file exists so you know what the shape is and what the tool boundaries
> are, not to substitute for it.

**Tool abbreviations used throughout:** **SWPM** = SAP Software Provisioning Manager (part of the SL
Toolset); **SSMS** = Microsoft SQL Server Management Studio.

---

## 1. Installing an SAP system on AlwaysOn

1. **SWPM** — install the ASCS/SCS instance (distributed) or first cluster node (HA).
2. **SWPM** — install the SAP system on the **primary replica**, using the *Database Instance* option.
3. **SWPM** — install the additional cluster node (HA).
4. **SSMS** — on each node, create a login for the other node(s) using the **FQDN appended with `$`**.
5. **SSMS** — back up the SAP database **and the transaction log** on the primary; restore both on
   the secondaries **`WITH NORECOVERY`**.
6. **SSMS** — create the availability group **with listener** and add the SAP database.
7. **SWPM** — install the primary application server instance.
8. Set the **profile parameters and environment variables** (parent skill §3).
9. **SWPM** — *Configure additional Always On Node* on every replica (parent skill §4).
10. **SWPM** — optionally install additional application server instances.
11. **SAP Host Agent** — if no SAP instance exists on a secondary, the Host Agent is **not installed
    automatically**. Install it manually (SAP Note **1031096**).

Step 11 is easy to miss and leaves a secondary invisible to SAP tooling.

---

## 2. System copy onto AlwaysOn

Same shape, with the source restore first:

1. **SSMS** — restore the source SAP database on the primary. *(Not required for R3load-based copy.)*
2. **SWPM** — ASCS/SCS or first cluster node.
3. **SWPM** — install on the primary replica (*Database Instance*).
4. **SSMS** — cross-node logins, FQDN + `$`.
5. **SSMS** — backup on primary, restore on secondaries **`WITH NORECOVERY`**.
6. **SSMS** — create the availability group with listener, add the database.
7. **SWPM** — additional cluster node.
8. **SWPM** — primary application server instance.
9. Profile parameters and environment variables.
10. **SWPM** — *Configure additional Always On Node* on the other replicas.
11. Optional additional app servers; manual **SAP Host Agent** where needed.

> **SAP Note 2446660** documents that *System Copy with HA does not set the AlwaysOn profile/env
> parameters* **[G]** — which is why step 9 is explicit rather than assumed.

---

## 3. Refresh / Move

1. **Stop all application servers**; keep the **message server service running**.
2. **SSMS** — depending on target:
   - **Same primary replica node:** remove the database from the AG and drop it on all secondaries —
     ```sql
     ALTER AVAILABILITY GROUP <group_name> REMOVE DATABASE <SID>
     ```
     then restore the source database on the primary.
   - **New primary replica node:** restore the source database on the new primary.

   *(Restore not required for R3load-based copy.)*
3. **SWPM** — *System Copy → Target System → Distributed System → (ABAP or Java) → **Refresh or Move
   Database Instance*** on the primary replica.
4. **SSMS** — back up database and log on the primary; restore on secondaries **`WITH NORECOVERY`**.
5. **SSMS** — re-add to the availability group:
   ```sql
   -- primary
   ALTER AVAILABILITY GROUP <group_name> ADD DATABASE <SID>
   -- each secondary
   ALTER DATABASE <SID> SET HADR AVAILABILITY GROUP = <group_name>
   ```
   Refresh both servers in SSMS and **confirm the `<SID>` database shows `SYNCHRONIZED`** on primary
   and secondary. *(For a new primary node: create the AG with listener instead.)*
6. Check profile parameters and environment variables.
7. **SWPM** — *Configure additional Always On Node* on the other replicas.
8. Start the application servers. Install **SAP Host Agent** manually where needed.

---

## 4. Refresh Database Content

1. Stop all application servers.
2. **SSMS** — remove from the AG and drop everywhere:
   ```sql
   ALTER AVAILABILITY GROUP <AvailabilityGroupName> REMOVE DATABASE <SID>
   DROP DATABASE <SID>   -- on primary and secondary replicas
   ```
3. **SSMS** — restore the source database on the primary.
4. **SWPM** — *Generic Options → MS SQL Server → SAP Library Installation and Update → **Refresh
   Database Content*** on the primary.
5. Check profile parameters and environment variables.
6. **SSMS** — backup on primary, restore on secondary **`WITH NORECOVERY`**.
7. **SSMS** — `ADD DATABASE` / `SET HADR AVAILABILITY GROUP` as in §3.5; confirm `SYNCHRONIZED`.
   The logins already exist on both replicas with the same SID.
8. **SWPM** — *Configure additional Always On Node* on the other replicas.
9. Start the application servers.

---

## 5. Dual-stack split

**Keep database option** (dual stack already on AlwaysOn) — afterwards:

1. Stop all application servers in **both** ABAP and Java stacks.
2. **SWPM** — for the newly installed Java system, *Configure additional Always On Node* on the other
   replicas.

**Move database option** — afterwards:

1. Stop all Java application servers.
2. **SSMS** — backup on primary, restore on secondary **`WITH NORECOVERY`**.
3. **SSMS** — `ADD DATABASE` / `SET HADR AVAILABILITY GROUP`; confirm `SYNCHRONIZED`.
4. **SWPM** — *Configure additional Always On Node*.
5. Start the Java application servers.

---

## 6. SUM upgrade

Use the SQL Server-specific SUM guide — *Updating SAP ABAP Systems on Windows: Microsoft SQL* on the
SAP Help Portal. **[V]**

> Pay particular attention to the ***Update Schedule Planning*** and ***Database-Specific Aspects***
> sections: they describe actions required **before** entering the downtime roadmap. **[V]** Finding
> that out mid-downtime is the failure mode.

---

## 7. Monitoring

```sql
-- replica roles and synchronization
select ag.name as ag_name, ar.replica_server_name,
       ars.role_desc, ars.synchronization_health_desc,
       ar.availability_mode_desc, ar.failover_mode_desc,
       ar.secondary_role_allow_connections_desc
from   sys.availability_groups ag
join   sys.availability_replicas ar  on ag.group_id = ar.group_id
join   sys.dm_hadr_availability_replica_states ars
         on ar.replica_id = ars.replica_id;

-- per-database state, queue sizes and rates
select dc.database_name, drs.synchronization_state_desc,
       drs.log_send_queue_size, drs.log_send_rate,
       drs.redo_queue_size, drs.redo_rate, drs.last_commit_time
from   sys.dm_hadr_database_replica_states drs
join   sys.availability_databases_cluster dc
         on drs.group_database_id = dc.group_database_id;

-- listener
select * from sys.availability_group_listeners;
```

**Reading the queues** — the same distinction as every other replication technology:

| `log_send_queue_size` | `redo_queue_size` | Meaning |
|---|---|---|
| High | Low | **Network / send** problem |
| Low | High | Received but not **redone** — apply-side problem on the secondary |
| Low | Low | Healthy |

`secondary_role_allow_connections_desc` is where you confirm no SAP `<SID>` secondary is set to
`ALL` (the unsupported "Yes" — parent skill §5).

**DBACOCKPIT caveat:** DB13 and DB12 have known issues with AlwaysOn and Mirroring — SAP Note
**2153963** **[G]**.

---

## 8. Database Mirroring — the predecessor

For **SQL Server 2008 R2 and earlier**, Database Mirroring is the recommended HA/DR mechanism
(SAP Note **965908**) **[G]**. From SQL Server 2012 onward SAP *"strongly recommended"* AlwaysOn
instead **[V]**. Mirroring still appears in older landscapes; note that Microsoft deprecated it long
ago, so any migration project should be moving toward AlwaysOn, not extending Mirroring.

`MSSQL_SERVER` / `MSSQL_CONNOPTS` handling for **both** mechanisms is covered by SAP Note **2137130**
**[G]**.

---

## 9. Removing AlwaysOn

SAP Note **3590454** — *How to remove 'SQL Server AlwaysOn' from an existing SAP NetWeaver system
installation* **[G]**. Relevant when decommissioning HA or consolidating a landscape; the profile
parameters and environment variables from the parent skill §3 must be reverted too, or the system
will keep trying to reach a listener that no longer exists.
