# MaxDB / liveCache HA — choosing and operating

Companion to the parent skill. The full advantage/disadvantage lists from **SAP Note 952783** v21
**[V]**, plus snapshot/split-mirror detail and maintenance.

---

## 1. Start from the requirement, not the technology

Note 952783 opens with the point most HA conversations skip **[V]**:

> *"In general, the more comprehensive the protection against downtime, the more expensive the
> solution. For this reason, **you should first specify your requirements**."*

Two numbers decide everything:

1. **Maximum unplanned downtime in a period** (availability target)
2. **Maximum length of an individual downtime** (RTO)

> *"For databases, the maximum length for an individual downtime is very important. **If this time is
> shorter than the longest estimated time for the restore, you require additional protection
> mechanisms.**"* **[V]**

That is the whole test. Estimate your restore time honestly; if it exceeds the tolerable single
outage, backup/recovery alone is not enough — and *which* mechanism you add depends on whether you
fear a host, a disk, a site, or a logical error.

---

## 2. The full trade-off tables **[V]**

### Backup / recovery

| Advantages | Disadvantages |
|---|---|
| Simple implementation | **Downtime for recovery may be long** |
| No periodic tests required — backups can be checked ONLINE | I/O workload during backup |
| **Protects against physical *and* logical errors** | |

### File system snapshots

| Advantages | Disadvantages |
|---|---|
| Very fast data recovery | A disk storage system is required |
| No synchronization required at creation | I/O workload for backups in the storage system |
| Usable **without a log** for system copies | **Structure check not possible on a read-only snapshot** |
| Can provide consistent versions of whole landscapes | **Does not protect against damaged hard disks** |

> ⚠️ **A snapshot is not a backup** *"as long as the data was not copied to a second medium."* **[V]**

### Split mirror / snapshot with copy (flash copy, symclone)

| Advantages | Disadvantages |
|---|---|
| Very fast data recovery | A disk storage system is required |
| No synchronization required at creation | **The storage system must guarantee I/O consistency across *all* data volumes for the duration of the split** |
| **MaxDB data backups possible on the mirror** | Merge of the mirror back into the master |
| **Structure checks possible on the mirror** | Additional disk space for full mirrors |
| Consistent landscape versions | |

See SAP Notes **371247** and **1928060** **[G]**.

### Cluster for failover

| Advantages | Disadvantages |
|---|---|
| Automatic, quick transfer on host problems | **Shared disk approach — data volumes are NOT protected** |
| Cluster agents available for all platforms | **Recovery required for defective data disks** |
| | I/O workload for backup |

### Shadow (standby) database

| Advantages | Disadvantages |
|---|---|
| Protects against **disk and host** failures | **No automatic transfer without additional software** |
| Structure checks possible on the standby | Additional host and disk space |
| **Protects against logical errors (PITR)** | |
| **The log-recovery delay you choose sets max downtime** | |
| **Implementable without further partners** | |
| No performance disadvantage for the master | |

### Hot Standby

| Advantages | Disadvantages |
|---|---|
| Protects against **disk and host** failures | **A disk storage system is required** |
| **Automatic transfer** on host or database failure | **Implementation must be done by hardware partners for the HSS library** |
| **Transfer lasts only a few seconds** | Additional host and disk space |
| Structure check possible on the standby | |
| **Standby is read only** | |
| No performance disadvantage for the master | |

---

## 3. Decision shortcuts

| If you fear… | Reach for |
|---|---|
| A **host** crash, nothing else | Cluster for failover |
| **Host or disk**, seconds of RTO, budget for storage + vendor | **Hot Standby** |
| **Site loss** (computer centre) | **Shadow database** — see parent §2 |
| **Logical corruption** (bad transaction, wrong delete) | **Shadow database with deliberate lag**, or backup/recovery PITR |
| Long restore times generally | Large log area + incremental backups + parallel media |

**Hot Standby and shadow database are not alternatives at landscape scale** — Hot Standby locally for
RTO, shadow database remotely for DR, is a coherent design.

---

## 4. Speeding up recovery **[V]**

- **Incremental backups** *"can speed up the recovery of a database considerably."*
- **Make the log area large.** If the log-recovery start point is still in the current log, *"you can
  carry out a restart immediately"* after the data restore — no archived log files needed. This is
  the cheapest RTO improvement available and it is a sizing decision, not a licence purchase.
- **Backup media access is usually the bottleneck.** Use parallel backup media and ensure a fast
  connection to backup servers.

---

## 5. Maintenance in an HA environment

**SAP Note 2113981** — *SAP MaxDB / liveCache / Content Server Maintenance in High Availability
System Environment* **[G]** — is the reference for patching and upgrading without dismantling the HA
setup. Read it before an upgrade; the sequence differs from a standalone system.

For Hot Standby specifically, **SAP Note 2097837** covers **installation and upgrade of a hot standby
system with shared log area** **[G]**.

---

## 6. Cloud

**SAP Note 3318338** — *SAP MaxDB/liveCache high availability in cloud environment* **[G]**.

Worth a specific check, because both Hot Standby and split-mirror depend on **storage-system
features** (flash copy, symclone, guaranteed cross-volume I/O consistency) that may not exist, or may
behave differently, on cloud block storage. Do not assume an on-premise Hot Standby design lifts
into IaaS.

---

## 7. Storage approval

**SAP Note 912905** — *FAQ: Storage systems used with SAP MaxDB* **[G]**.

A hot standby system suitable for **production** requires the cluster software **and** a storage
solution **approved for SAP MaxDB**. The approved list, and the vendor HSS solutions in **SAP Note
3534972**, are the two gates to check before committing to a Hot Standby design — not after.
