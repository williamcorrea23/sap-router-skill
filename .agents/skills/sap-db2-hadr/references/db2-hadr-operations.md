# Db2 HADR under SAP — operations

Companion to the parent skill. Monitoring, takeover runbooks, the full rolling Fix Pack sequence, and
Reads on Standby. SAP-specific statements are **[V]** from **SAP Note 1612105** v6; Db2 syntax is
**[G]** from IBM documentation.

---

## 1. Monitoring

```bash
# as db2<sid> — the fastest full picture
db2pd -db <SID> -hadr
```

```sql
-- the supported, scriptable interface (Db2 10.5+)
select HADR_ROLE, HADR_STATE, HADR_SYNCMODE, HADR_FLAGS,
       HADR_CONNECT_STATUS, HADR_CONNECT_STATUS_TIME,
       STANDBY_ID, PRIMARY_MEMBER_HOST, STANDBY_MEMBER_HOST,
       HADR_LOG_GAP, STANDBY_REPLAY_LOG_TIME, STANDBY_RECV_REPLAY_GAP
from   table(MON_GET_HADR(-2));
```

**What to read first:**

| Field | Healthy | Meaning when not |
|---|---|---|
| `HADR_STATE` | **`PEER`** | `REMOTE_CATCHUP`, `DISCONNECTED_PEER`, `LOCAL_CATCHUP` — not protecting you yet |
| `HADR_CONNECT_STATUS` | `CONNECTED` | `DISCONNECTED` / `CONGESTED` — network or standby down |
| **`HADR_FLAGS`** | *(empty)* | **Populated = a reason replication stopped** — see parent §5 |
| `HADR_LOG_GAP` | ~0 | Standby falling behind |
| `STANDBY_RECV_REPLAY_GAP` | small | Received but not replayed — an *apply* problem, not a network one |

> **`PEER` is the precondition for maintenance.** Every rolling procedure below assumes you verified
> peer state first. **[V]**

`HADR_FLAGS` is the field that turns a silent failure into a diagnosable one — which is exactly why
`DB2_FAIL_RECOVERY_ON_TABLESPACE_ERROR=YES` matters (parent §5).

---

## 2. Takeover

**Graceful (planned)** — roles swap, no data loss:

```sql
TAKEOVER HADR ON DATABASE <SID>
```

**By force (unplanned)** — primary is gone:

```sql
TAKEOVER HADR ON DATABASE <SID> BY FORCE
```

> ⚠️ **`BY FORCE` is the split-brain risk.** It promotes the standby without the old primary's
> agreement. If the old primary is actually alive and still reachable by application servers, you now
> have two primaries — and with **ACR** rather than a VIP, work processes will silently split between
> them and **the databases will diverge** (parent §2). Confirm the old primary is truly down, and
> prefer a VIP so the topology cannot split.

**Minimising SAP downtime:**

- **Graceful Maintenance Tool (GMT)**, SAP Note **1530812** — suspends the SAP system across a
  planned takeover so the application tier survives it. **[V]**
- With **SA MP**, `sapdb2cluster.sh switch` (Note **960843**) performs an automated cluster switch
  with graceful takeover. **[V]**

**After any role change** the application servers must be connected to the new primary — automatic
with a VIP, per-connection roulette with ACR.

---

## 3. Rolling Fix Pack update — full sequence **[V]**

Assumes peer state and a VIP or supported ACR setup.

1. Install the Fix Pack as a **new software copy** on **both** the standby and the primary server.
2. **Deactivate** the standby database and **stop** the standby instance.
3. Run **`db2iupdt`** on the standby to switch the instance to the new software copy.
4. **Start** the standby instance and **activate** the standby database.
5. **Take over** on the standby.
   - Use **GMT** (Note 1530812) to keep the SAP system up.
   - With SA MP, use **`sapdb2cluster.sh switch`** (Note 960843).
6. The HADR connection now shows **disconnected** — expected. **HADR allows the standby to run a
   newer Db2 level than the primary, never the reverse**, so the new standby (former primary, older
   level) is deactivated.
7. Repeat steps 2–4 on the new standby.
8. Optionally switch roles back to the original assignment.
9. Run **`db6_update_db.sh`** (Note **1365982**) on **both** databases. It may require an instance
   restart on both to accept new parameters — a **graceful** restart via GMT keeps users online.
10. Run **`db6_update_client.sh`** (Note 1365982).
11. **Restart application servers one by one** so they pick up the new Db2 client software.

> Steps 9–11 are the ones people skip. The database is updated but the SAP layer still runs the old
> client until the app servers are bounced.

---

## 4. Rolling configuration and OS changes **[V]**

Keep primary and standby **identically configured**; differences should exist only transiently
during the rolling change.

```
1. Verify HADR is in PEER state
2. Deactivate the database on the standby, stop the Db2 instance
3. Make the hardware / software / parameter change
4. Start the instance, activate the database
5. Verify PEER state again
6. Switch roles  (GMT to minimise end-user impact)
7. Repeat 1–5 on the new standby
8. Optionally switch back
```

**What can and cannot roll:**

| Change | Rolling |
|---|---|
| Operating system | ✅ |
| Dynamic Db2 parameters | ✅ (no special procedure) |
| Non-dynamic Db2 parameters (instance/DB restart) | ✅ |
| **Db2 HADR parameters** | 🚫 **They block HADR role changes — plan a database outage** |

That last row is the planning trap: changing `HADR_*` settings is *not* a rolling change, so it
cannot be slipped into a maintenance window that assumes a takeover is available.

---

## 5. Version upgrade

- **Db2 11.1 and higher:** standbys can be **rolled forward through the version upgrade** provided
  you start from certain **Db2 10.5 minimum Fix Pack levels**. SAP's Db2 11.1 upgrade guide has the
  levels — `help.sap.com/viewer/db6_upgrade_11_1`. **[V]**
- Otherwise the **standbys must be rebuilt** after the upgrade. **[V]**

Budget for the rebuild if you cannot meet the minimum Fix Pack level — it is a full restore from a
primary backup, not a catch-up.

---

## 6. Reads on Standby (RoS)

RoS lets the standby serve read-only work. Two SAP-relevant consequences:

- **RoS makes ACR unsupported.** SAP supports ACR only when `db2haicu`+SA MP is used **and RoS is not
  enabled**, because connections may land on the standby and be *"unusable for business transactions
  that do write operations."* **[V]** With RoS, use a **VIP**.
- Reporting-on-standby proposals should be checked against what the SAP application actually needs —
  an SAP work process expects a read-write connection.

---

## 7. Time-delayed replay

Note 1612105 lists time-delayed replay as a supported use *"to allow for faster recovery from
erroneous data changes."* **[V]** A deliberately lagging standby is a defence against logical
corruption — the standby has not yet replayed the bad transaction. Distinct from HA: it trades RPO
for a rewind window.

---

## 8. Boundaries

- **DPF and pureScale** are separate topics with their own support statement — **SAP Note 702175**
  **[G]**. Do not assume HADR guidance transfers to a pureScale landscape.
- **`DB6CONV` with non-recoverable load** requires a backup afterwards **and a rebuild of the HADR
  standbys from a primary backup** (Note 1513862). **[V]** Check before running conversions on an
  HADR-protected system.
- Supported Db2 features under SAP generally: **SAP Note 1555903** **[G]**.
