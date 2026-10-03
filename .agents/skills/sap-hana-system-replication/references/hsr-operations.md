# HSR operations — setup, takeover, failback, multitier/multitarget

Sources as in `SKILL.md`: SR Guide **2.0 SPS 08** **[V]**, SAP Note **1999880** v297 **[V]**.
**Check the §3 version matrix in `SKILL.md` before using anything below.**

---

## 1. Initial setup — the order that works

```bash
# ── PRIMARY (as <sid>adm) ─────────────────────────────────────────
# 0. a data backup MUST exist first — see sap-backup-recovery
hdbnsutil -sr_enable --name=<SITE_A>          # --name mandatory for multitier/multitarget
hdbnsutil -sr_state                           # confirm: mode primary, site name set

# ── copy the PKI SSFS pair primary → secondary (HANA 2.0) ─────────
#   /usr/sap/<SID>/SYS/global/security/rsecssfs/data/SSFS_<SID>.DAT
#   /usr/sap/<SID>/SYS/global/security/rsecssfs/key/SSFS_<SID>.KEY
#   + the XSA pair under .../global/xsa/security/ssfs/ if XS advanced is installed

# ── SECONDARY (as <sid>adm) — MUST BE STOPPED ────────────────────
HDB stop
hdbnsutil -sr_register \
  --remoteHost=<primary_master_host> \
  --remoteInstance=<nn> \
  --replicationMode=sync \
  --operationMode=logreplay \
  --name=<SITE_B>
HDB start

# ── verify from the PRIMARY ───────────────────────────────────────
cd /usr/sap/<SID>/HDB<nr>/exe/python_support && python systemReplicationStatus.py
# want return code 15 (ACTIVE); 13 = still initializing, secondary NOT usable
```

**Initial sync time** — the rule of thumb from the FAQ **[V]**:

```
initial sync time  >  backup size / available network bandwidth
initial sync time  >  backup size × compression factor / available bandwidth   (with compression)
```

In **scale-out**, the total is the **maximum** of the per-host times, not the sum. **[V]**
**Scale-out has its own rules** — identical topology, host mapping, and a node-count ordering that
inverts between add and remove: [hsr-scale-out.md](hsr-scale-out.md).

---

## 2. Changing things on a running landscape

| Change | Command | Side |
|---|---|---|
| Replication mode | `hdbnsutil -sr_changeReplicationMode --mode=sync｜syncmem｜async` | Secondary |
| **Operation mode** | `hdbnsutil -sr_register … --operationMode=<mode>` (re-register) | Secondary |
| Enable/disable full sync | `hdbnsutil -sr_fullsync --enable｜--disable` | Primary |
| Re-init one tenant/volume | `hdbnsutil -sr_initialize --database=<db>｜--volume=<id> [--force_full_replica]` | Primary |

> **`-sr_register` overwrites the previous registration.** It is the same command used for initial
> setup, for changing operation mode, and for re-syncing — read the existing config with
> `-sr_state` before running it, or you will silently change more than you meant to. **[V]**

**There is no pause command.** HSR has **no generic pause**. It stops automatically when the
secondary is unreachable. To make some parameter changes effective you need a **reconnect from the
secondary**, not a restart. **[V, Q58/Q59]**

**Re-syncing without a full data shipment** — in `logreplay`, a disconnected secondary can catch up
from logs **only if every redo log since the disconnect is still retained on the primary**. That is
what `logshipping_max_retention_size` buys you; when it is exhausted, the next sync is a full one. **[V, Q62]**

---

## 3. Takeover

**Decide with the script, not by eye:**

```bash
cd /usr/sap/<SID>/HDB<nr>/exe/python_support
python getTakeoverRecommendation.py      # 2.0 SPS 03+ — SAP's own recommended entry point
```

**Planned takeover with handshake — 2.0 SPS 04+** **[V]**:

```bash
# on the SECONDARY
hdbnsutil -sr_takeover --suspendPrimary
# optionally let running write transactions drain first (DEFAULT IS NO WAIT):
hdbnsutil -sr_takeover --suspendPrimary --maxWriteTransactionWaitTime=<seconds>
```

`--suspendPrimary` suspends the old primary to protect against data loss and split brain. Afterwards:

```bash
hdbnsutil -sr_resumeSuspendedPrimary      # on the OLD PRIMARY
```

> ⚠️ **Once the primary is resumed, SAP HANA no longer protects you against two active primaries.**
> The guide states this explicitly. Sequence the resume only after the new primary is confirmed. **[V]**

**Takeover time depends on the operation mode** **[V, Q23]**:

- `logreplay` / `logreplay_readaccess` — secondary is already up; usually fast. Exceptions: a large
  **log replay backlog**, or (read-access) eviction of a large **SQL cache** (Notes 2124112, 3616640).
- `delta_datashipping` — **significantly longer**: open persistence from the last savepoint, load the
  row store, then replay redo.

**Invisible takeover** (2.0 SPS 03+) avoids terminating active transactions. Default is `false` on
2.0 SPS 03 and **`true` above 2.0 SPS 04** — so behaviour changes across that boundary. **[V, Q54]**

---

## 4. Failback

**Failback is the takeover procedure run in the opposite direction** — same steps, roles swapped. **[V, Q24]**
There is no dedicated failback command. Expect to `-sr_register` the old primary as the new secondary,
which is why keeping its data intact matters.

---

## 5. Multitier and multitarget

| | |
|---|---|
| **Multitier** | A chain: A → B → C. Each tier registers to the one above. |
| **Multitarget** | A fans out to several secondaries. **2.0 SPS 03+**; up to 2.0 SPS 02 only one secondary was possible. **[V]** |
| **Four tiers** | 2.0 SPS 03+ — used for near-zero-downtime upgrades. **[V]** |

- `-sr_enable --name=` is **mandatory**, and must be run for **each further tier** added. **[V]**
- `-sr_register --withAllSecondaries` re-attaches a secondary to a different source while keeping its
  sub-trees. **All sites must be online.** **[V]**
- `alternative_sources` (secondary) pre-declares fallback sources: `SiteA,SiteB` or `SiteA:sync,SiteB:async`.

**Takeover in multitarget** — you may take over to **any** connected secondary. From **2.0 SPS 04**
the others can be **re-registered to the new primary automatically**, and can then catch up by **log
delta shipping instead of full** — but only when all of these hold **[V, Q61]**:

1. Replication status of the secondaries is **ACTIVE** before takeover;
2. the secondary issuing the takeover is in **`sync` or `syncmem`**;
3. the primary is **stopped or suspended** before the takeover is issued.

Miss any one and you are looking at full data shipping to every remaining site.

---

## 6. Active/Active (read enabled)

- **HANA 2.0+**, operation mode `logreplay_readaccess`, **requires an add-on licence** granting
  productive use rights on the secondary. **[V]**
- Restrictions: **SAP Note 2391079**.
- Trade: query load moves off the primary; takeover may be slower due to SQL-cache eviction.

---

## 7. Upgrades

You may stop both sites, upgrade both, restart both. To **minimise downtime**, upgrade the secondary
first and take over — the near-zero-downtime pattern, and the reason four tiers exist. **[V, Q16]**

Relevant constraints:
- Replication between **different HANA patch levels** is supported within documented bounds — check
  Q15 of Note 1999880 for the current statement before relying on it.
- On **> 2.0 SPS 03** you can keep a secondary as a **pre-upgrade fallback** rather than disabling
  replication for the maintenance window. **[V, Q50]**
- **Different operating systems** across sites: see Q57 — do not assume it is allowed.

---

## 8. Disabling replication

Order matters: **unregister the secondary, then disable the primary.**

```bash
# SECONDARY (offline)
hdbnsutil -sr_unregister
# or from the PRIMARY (online) when the secondary is gone:
hdbnsutil -sr_unregister --name=<SITE_B>     # or --id=<site id>

# PRIMARY
hdbnsutil -sr_disable
```

Only three scenarios justify `-sr_unregister` (SAP Note **1945676**): permanent decoupling, cleaning
up after a lost secondary, or restoring the original multitier setup after a takeover. **[V]**
