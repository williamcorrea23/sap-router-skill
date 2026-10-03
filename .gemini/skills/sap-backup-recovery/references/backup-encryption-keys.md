# Backup encryption and key management

> **The rule this file exists to enforce:**
> **An encrypted backup you cannot decrypt is not a backup.** The keys are a *separate* asset with a
> *separate* lifecycle, and they must be backed up, stored apart from the data backup, and **proven to
> restore** before you need them. Every DB below can produce a backup that restores perfectly on the
> source host and is worthless on a rebuilt one.

Marked **[V]** where retrieved from the SAP Note during authoring · **[G]** cited to the Note/guide.

---

## The four questions, for every platform

Ask these before accepting any encrypted-backup arrangement:

1. **What is encrypted?** Data volumes, log volumes, the backup stream, or all three — they are often
   separate settings with separate keys.
2. **Where does the key live, and is it inside the thing being backed up?** A key stored only in the
   database is worthless once the database is gone.
3. **Is the key backed up, separately, and where is *that* stored?** Same tape/share as the data backup
   defeats the purpose.
4. **Has a restore been proven on a *different host*?** This is where key arrangements fail — see the HANA
   cross-server case below, which fails at service start with a corruption-shaped error.

---

## SAP HANA

Three independently encryptable areas: **data volume**, **log volume**, **backup**. Root keys exist per
area. **[G]**

**FAQ:** SAP Note **2444090** — *FAQ: SAP HANA Backup Encryption*. **[V]**

### When Local Secure Store (LSS) is active — HANA 2.0+

Root-key handling changes completely, and the commands are `hdbnsutil`, not SQL: **[V, LSS]**

```bash
# back up root keys and settings (ALL types at once)
hdbnsutil -backupRootKeysAndSettings <filename>.rkb --dbid<dbid>

# recover them
hdbnsutil -recoverRootKeysAndSettings <path>/<filename>.rkb --database_name<db> --password<pwd>
```

Two constraints from the Note, both load-bearing: **[V, LSS]**

- **All-in-one.** `-backupRootKeysAndSettings` backs up **Persistence, Log and Backup** root keys
  *simultaneously*. **You cannot back up or recover a single key type.**
- 🚨 **Cross-server recovery is a trap.** Taking an LSS backup on **Server A** and recovering it on
  **Server B**, with volume encryption enabled on both, produces a database that **will not start** —
  because the persistence and log layers cannot decrypt.

**The failure signature is misleading — it looks like corruption, not a key problem:** **[V, LSS]**

```
Savepoint SavepointImpl.cpp : Invalid ChecksumAlgorithm or Checksum on AnchorPage 0
    checkSumAlg <invalid checksum algorithm 6>
PersistenceManager::prepareOpen failed ... no.3000284
    Could not read AnchorPage, none of 2 found copies contains valid data
indexserver: startup failed
```

If you see `invalid checksum algorithm 6` and `Could not read AnchorPage` after a restore or a key
recovery, **stop treating it as data corruption** and check whether LSS keys were moved between hosts.

Get the `dbid` for the command per SAP Note **3756453** (*How to determine the SAP HANA Database ID (dbid)
via SQL*). **[V, LSS]**

### Practical HANA checklist

- Record whether **data**, **log** and **backup** encryption are each on — they are separate.
- Back up root keys **whenever encryption configuration changes**, not only at install.
- Store the `.rkb` **off** the backup destination.
- For a system-replication landscape, backup/recovery has its own FAQ: SAP Note **2165547**. **[V]**

---

## Oracle — Transparent Data Encryption (TDE)

The keystore/wallet is the asset. A `brrestore` of datafiles without the wallet leaves you with files
Oracle cannot open.

- **BR\*Tools gained "Manage data encryption" (BRSPACE) only as of BR\*Tools 7.40 Patch 30** — before that
  patch the tooling does not manage TDE for multitenant databases at all. **[V, MT]**
- Treat the **wallet/keystore** as part of the backup set, backed up separately, with its password held in
  your normal secret store — not next to the wallet.
- On a restore to a **new host**, the wallet must be present and openable *before* `RECOVER`.

---

## Microsoft SQL Server — TDE

Restoring a TDE-protected database onto another instance requires the **certificate and its private key**
restored into `master` on the target *first*. Without it the restore fails outright.

- Back up the certificate **and** private key, separately from the database backup.
- Note the differing behaviour across versions (backup to URL, TDE-with-backup-compression) — check the
  release-planning note for your version, see
  [version-support-matrix.md](version-support-matrix.md).

---

## IBM Db2 LUW — native encryption

- The **keystore** (local keystore file) and the **master key label** are required to restore.
- Keystore and its stash/password must exist on the target before `RESTORE`.
- Db2 version and fix-pack level gate the encryption features — SAP Note **101809**.

---

## SAP ASE — database / column encryption

- ASE encrypts at **database** and **column** level; the **encryption keys live in the database**, which is
  precisely the trap in question 2 — a dump of an encrypted database is useless without the key material.
- The **master key** / key copies and their passwords must be recoverable independently of the dump.
- After `load database` onto another server, keys must be re-established before data is readable.
- Verify the specifics for your release (15.7 vs 16.0) — see hub note **2162183**. [G]

## SAP MaxDB

- MaxDB supports encrypted backups; the key material is held with the database instance configuration.
- A `recover_start` on a rebuilt host needs that configuration restored first.
- Verify per build against the MaxDB documentation. [G]

> ⚠️ **ASE and MaxDB coverage is thinner than HANA/Oracle/Db2 and is marked [G] throughout.** SAP Notes
> searches on this S-user return substantially less for these platforms — an **entitlement limitation, not
> an absence of documentation**. Treat the above as the questions to answer, not as a verified procedure,
> and record what you confirm.

---

## The test that actually proves it

A restore test on the **source host** proves almost nothing about key management, because every key is
already in place. The meaningful test is:

1. Restore to a **different host** (or a rebuilt one),
2. using **only** the artefacts your runbook says are retained — data backup **plus** key backup,
3. with **no** access to the original system's key store,
4. and confirm the database **opens** and data is readable.

Anything less leaves the key question untested. Record the date of the last such test alongside the
backup schedule — see the test-restore discipline in [../SKILL.md](../SKILL.md).

---

## Sources

- **[LSS]** **SAP Note 3756303** — *How to backup and recover SAP HANA Root Keys when Local Secure Store
  (LSS) is active* (HAN-DB-SEC, v2, 2026-05-21). **[V]** Retrieved via the SAP Notes MCP during authoring.
  Environment: SAP HANA Platform 2.0 or higher, LSS enabled, data/log/backup volume encryption active.
  Source for the `hdbnsutil -backupRootKeysAndSettings` / `-recoverRootKeysAndSettings` syntax, the
  all-key-types-at-once constraint, the cross-server recovery failure, and the
  `invalid checksum algorithm 6` / `Could not read AnchorPage` signature. Cross-refers **3756453** for
  obtaining the `dbid`, and the SAP HANA Security Guide sections *Data and Log Volume Encryption*,
  *Backup Encryption* and *Local Secure Store (LSS)*. https://me.sap.com/notes/3756303
- **SAP Note 2444090** — *FAQ: SAP HANA Backup Encryption* (HAN-DB-BAC). **[V]**
- **SAP Note 1642148** — *FAQ: SAP HANA Database Backup & Recovery* (HAN-DB-BAC). **[V]**
- **SAP Note 2165547** — *FAQ: SAP HANA Database Backup & Recovery in an SAP HANA System Replication
  Landscape* (HAN-DB-BAC). **[V]**
- **SAP Note 2159014** — *FAQ: SAP HANA Security* (HAN-DB-SEC). **[V]**
- **[MT]** **SAP Note 2333995** — *BR\*Tools support for Oracle multitenant database* — source for
  "Manage data encryption" (BRSPACE) arriving in **BR\*Tools 7.40 Patch 30**. **[V]**
- **SAP Note 101809** — *DB6: Supported Db2 Versions and Fix Pack Levels* — gates Db2 encryption features
  by version/fix pack. **[G]**

**To confirm/deepen** — fetch **3756303** and **2444090** with the SAP Notes MCP before any encrypted
restore, and **check the attachments** on those Notes: SAP frequently ships the detailed procedure as an
attached PDF rather than in the Note body.
