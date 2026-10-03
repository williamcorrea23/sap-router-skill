# Version & platform support — checking OS / DB / kernel compatibility

Backup and recovery procedures are **version-gated**. Before quoting a command, establish three things:
the **DB version**, the **SAP kernel release**, and whether that combination is still **supported** on the
**OS** in question. This file is the method plus the per-DB support notes.

Marked **[V]** where retrieved from the SAP Note during authoring, **[G]** where cited to the Note/guide.

---

## 1. The Product Availability Matrix (PAM) is the authority

SAP's own documented procedure for checking a Product / Kernel / Database / OS combination: **[V, PAM]**

1. Open the **Product Availability Matrix (PAM)**.
2. Choose the installed **SAP application** (e.g. SAP NetWeaver 7.5).
3. **Technical Release Information** → **Database Platforms**.
4. Filter by **Kernel**, **Database**, **Operating System**.
5. Read the supported versions **and — critically — the "Supported until \<date\>" End of Maintenance date**
   under the *Database Version*, *Operating System* and *Scope* tabs.
6. Follow the additional information links on that page; they carry the exceptions.

> The PAM tells you what is *supported*. The per-DB notes below tell you what is *current* and when it goes
> out of support. You need both — a version can be supported by the PAM while already inside its
> end-of-support runway.

**SAP Note 3432900** documents this procedure (written for Db2, but the navigation is identical for every
database platform). **[V, PAM]**

---

## 2. Per-DB support and version notes

| DB | Supported-versions note | End-of-support note |
|---|---|---|
| **IBM Db2 LUW** | **101809** — *DB6: Supported Db2 Versions and Fix Pack Levels* | **1168456** — *DB6: Support Process and End of Support Dates for IBM Db2 LUW* **[V, PAM]** |
| **Oracle** | **1914631** — *Central Technical Note for Oracle Database 12c Release 1 (12.1)* (each release has its own central note) | **1174136** — *Oracle: End of Support Dates* **[V]** |
| **SAP HANA** | **1948334** — *SAP HANA Database Update Paths for SAP HANA Maintenance Revisions*; per-revision maintenance notes exist per SPS | revision strategy per SPS **[V]** |
| **SAP ASE** | **2162183** — *Important KBAs and SAP Notes — SAP ASE for Business Suite and Business Warehouse* (hub note) | **1941500** — *Certification information for Linux and other Operating Systems — SAP ASE* **[V]** |
| **MS SQL Server** | release-planning notes per version (e.g. **1076022** for SQL Server 2008/R2) | per release-planning note **[V]** |
| **SAP MaxDB** | see the MaxDB central notes | — |

> ⚠️ **Coverage is uneven and that is a fact about the search, not about SAP.** Notes searches for **ASE,
> MaxDB and SQL Server** return markedly less on this S-user than for HANA, Oracle and Db2 — an
> **entitlement limitation**, not evidence the notes are absent. Treat the thin rows as "look this up",
> not "nothing exists". Same limitation recorded in
> [sap-space-reclaim](../../sap-space-reclaim/references/db-diagnostic-files.md).

---

## 3. Establishing what you actually run

Before consulting any matrix, get the facts from the system rather than from the ticket:

```bash
# SAP kernel release + patch level
disp+work -version | head -20

# DB type as SAP sees it
echo $dbms_type                       # <sid>adm environment
```

| DB | Version query |
|---|---|
| **HANA** | `SELECT * FROM M_DATABASE;` → `VERSION` (e.g. `2.00.077`), plus `SELECT * FROM M_DATABASES;` for tenants |
| **Oracle** | `SELECT banner_full FROM v$version;` · `SELECT cdb FROM v$database;` ← **CDB check, see §4** |
| **Db2** | `db2level` |
| **ASE** | `select @@version` |
| **MaxDB** | `dbmcli -d <SID> -u … dbm_version` |
| **SQL Server** | `SELECT @@VERSION;` · `SERVERPROPERTY('ProductLevel')` |

Also record the **backup tool** version — for Oracle this matters more than the DB version (§4).

---

## 4. Where version actually changes the recovery procedure

These are the divergences that make a "correct" command wrong on a different version:

| DB | Divergence | Consequence |
|---|---|---|
| **Oracle** | **Multitenant (CDB/PDB), 12.1.0.2+** | Whole different recovery model. See [db-backup-recovery.md](db-backup-recovery.md) — and note the gate is the **BR\*Tools patch level**, not just the DB version **[V, MT]** |
| **HANA** | **1.0 vs 2.0**, and **single-container vs MDC (tenants)** | System DB vs tenant recovery are different operations; `RECOVER DATA` targets differ |
| **HANA** | **Local Secure Store (LSS)** active | Root-key backup/recovery uses different commands entirely — see [backup-encryption-keys.md](backup-encryption-keys.md) **[V]** |
| **ASE** | 15.7 → 16.0 | **Cumulative dumps** are a 16.0 feature |
| **Db2** | 10.x → 11.x | `RECOVER DATABASE` vs `RESTORE` + `ROLLFORWARD`; fix-pack-gated behaviour per Note 101809 |
| **SQL Server** | 2012 → 2022 | backup to URL, TDE handling, accelerated database recovery |

---

## 5. Sources

- **[PAM]** **SAP Note 3432900** — *How to check supported versions of Database/Kernel/OS in the Product
  Availability Matrix (PAM) for DB6* (BC-DB-DB6, v7, 2025-07-23). **[V]** Retrieved via the SAP Notes MCP
  during authoring. Source for the PAM navigation procedure and the instruction to note **End of
  Maintenance** dates. Cross-refers **101809** and **1168456**.
  https://me.sap.com/notes/3432900
- **[MT]** **SAP Note 2333995** — *BR\*Tools support for Oracle multitenant database* (BC-DB-ORA-DBA, v16,
  2026-07-13). **[V]** See [db-backup-recovery.md](db-backup-recovery.md) for the detail.
  https://me.sap.com/notes/2333995
- **SAP Note 1174136** — *Oracle: End of Support Dates* (BC-DB-ORA). **[V]**
- **SAP Note 1914631** — *Central Technical Note for Oracle Database 12c Release 1 (12.1)* (BC-DB-ORA). **[V]**
- **SAP Note 1948334** — *SAP HANA Database Update Paths for SAP HANA Maintenance Revisions* (HAN-DB). **[V]**
- **SAP Note 2162183** — *Important KBAs and SAP Notes — SAP ASE for Business Suite and Business
  Warehouse* (BC-DB-SYB). **[V]**
- **SAP Note 1941500** — *Certification information for Linux and other Operating Systems — SAP ASE*
  (BC-SYB-ASE). **[V]**
- **SAP Note 1076022** — *Release planning for Microsoft SQL Server 2008 (R2)* (BC-DB-MSS) — pattern
  example; find the release-planning note for your version. **[V]**
- **SAP Note 1656099** — *SAP Applications on AWS: Supported DB/OS and AWS EC2 products* — when the
  landscape is on AWS, this constrains the matrix further. **[V]**
- **SAP Note 2441698** — *How to check the product compatibility with the target platform during system
  copy* (BC-INS-MIG) — the same matrix question in a copy/refresh context. **[V]**
