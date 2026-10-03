# Complete SAP log & trace inventory — every source, by layer

Reference detail for [../SKILL.md](../SKILL.md). The point of this file is **completeness**: when
troubleshooting, enumerate the sources for every layer in the request path *before* concluding
"there's nothing in the logs." Most missed root causes are in a log nobody opened.

> **Not all of these exist in every landscape.** ABAP-only systems have no Java stack; a system without
> PI/PO has no `SXMB_MONI`. Check what applies, and say which sources you checked and which you skipped.

---

## 1. ABAP — core runtime & errors

| Where | What it holds | Notes |
|-------|---------------|-------|
| **SM21** | System log (syslog) — the system's own event log | Shell: `sapcontrol … ABAPReadSyslog`. Instance-local unless you switch to "all remote instances" |
| **ST22** | ABAP short dumps (runtime errors) | The single richest artefact: stack, variables, user, program |
| **SM50 / SM66** | Work processes, local / system-wide | Hung/long-running WPs, "in-use" DB actions |
| **SM12** | Lock entries (enqueue) | Orphaned locks after a crash |
| **SM13** | Update records | Failed/pending updates — errors here are invisible in SM21 |
| **SM37 / SMX** | Background jobs + job logs | Job log ≠ spool; check both |
| **SP01 / SP02**, **SPAD**, **SP12** | Spool requests, spool admin, TemSe | Output problems, TemSe inconsistency |
| **SLG1 / SLG2** | **Application Log (BAL)** — display / delete | Where *applications* write. Huge blind spot: object/subobject per app |
| **ST11** | Developer trace files (the `dev_*` set) from inside the system | Same files as the work directory |
| **SM51** | Instances / servers | Where to go look next |
| **AL08 / SM04** | Logged-on users / sessions | |

## 2. ABAP — tracing (switch on deliberately, then switch off)

| Where | Traces | Notes |
|-------|--------|-------|
| **ST01** | System trace: authorization, kernel, DB access, RFC, lock ops | Classic, instance-local, high overhead |
| **STAUTHTRACE** | **Authorization trace** (system-wide) | Preferred over ST01 for auth issues |
| **SU53** | Last failed authorization check *for a user* | First stop for "no authorization" reports |
| **ST05** | Performance trace: **SQL**, RFC, enqueue, HTTP, buffer | The tool for "slow" / "wrong data" |
| **SAT** (was SE30) | ABAP runtime analysis (where time is spent in code) | |
| **ST12** | Single-transaction analysis (SAT + ST05 combined) | Needs ST-A/PI add-on |
| **STAD** | Business transaction statistics (per dialog step) | Retrospective — no need to pre-enable |
| **ST03 / ST03N** | Workload statistics, aggregated | Trends, top transactions |

> ⚠️ Traces cost performance and disk. **Raise → reproduce → lower.** Never leave ST01/ST05 running.

## 3. ABAP — security & audit

| Where | What | Currency |
|-------|------|----------|
| **RSAU_CONFIG** | Security Audit Log (SAL) configuration | **Current** as of SAP_BASIS **7.50 SP03+** [A1] |
| **RSAU_READ_LOG** | Read/evaluate SAL | **Current** (replaces SM20) |
| **RSAU_ADMIN** | SAL administration — reorganize/archive log table, integrity-protection format | **Current** (replaces SM18) |
| SM19 / SM20 / SM18 | Legacy SAL config / read / delete | Legacy; **SM19 may be display-only** on newer releases [A2] |
| **Storage** | Audit files per `DIR_AUDIT` + `FN_AUDIT` profile params — **or the database** | File→DB switch: SAP Note 3667538 [A1] |
| **SCU3** / `DBTABLOG` | Table change logs (needs `rec/client` + table logging) | Who changed customizing |
| **CDHDR / CDPOS** | Change documents (business object level) | |
| **SUIM** | User/role/authorization reporting | |

> Audit-log retention is frequently a **compliance** obligation — see [sap-housekeeping](../../sap-housekeeping/SKILL.md)
> before deleting anything. Management recommendations: SAP Note 3500099. [A1]

## 4. ABAP — interfaces (the most under-checked layer)

| Where | Interface |
|-------|-----------|
| **SM58** | tRFC — transactional RFC error log |
| **SMQ1 / SMQ2** | qRFC outbound / inbound queues (stuck queues) |
| **SMQR / SMQS** | qRFC registration / scheduler |
| **SBGRFCMON** | bgRFC monitor (the modern successor) |
| **SM59** | RFC destinations — connection test + trace |
| **SMGW** | Gateway monitor + gateway logging (`gw/logging`) |
| **WE02 / WE05 / WE09**, **BD87** | IDoc display / search / status monitor + reprocess |
| **SXMB_MONI** | PI/PO Integration Engine message monitor |
| **/IWFND/ERROR_LOG** | **SAP Gateway (frontend/hub) error log** — OData/Fiori errors |
| **/IWBEP/ERROR_LOG** | **SAP Gateway (backend) error log** |
| **/IWFND/TRACES**, **/IWBEP/TRACES** | Gateway payload/performance traces |
| **SRT_UTIL** | Web service (SOAP runtime) error log & traces |
| **SRT_MONI** | Web service message monitor |
| **SOAMANAGER** | Web service configuration + logs |
| **SMICM** | ICM monitor, HTTP trace + HTTP access log |
| **SICF** | ICF service tree — inactive service = HTTP 403/404 |
| **SCOT / SOST** | Mail/SMTP send requests |

> Fiori/OData failures almost always need **three** places: `/IWFND/ERROR_LOG` (hub),
> `/IWBEP/ERROR_LOG` (backend) and **ST22** — the dump is often only on the backend.

## 5. ABAP — change, transport & upgrade

| Where | What |
|-------|------|
| **STMS** → Import Monitor / history | Transport imports |
| `/usr/sap/trans/log` | `SLOG`, `ALOG`, `<TR>.<SID>` — the OS-level import logs |
| **SE01 / SE09 / SE10** | Transport Organizer — object lists + logs |
| **SNOTE** | SAP Note implementation log |
| **SPAM / SAINT** | Support Package / Add-On import logs |
| **SPDD / SPAU** | Modification adjustment |
| **SCC3** | Client copy/import logs |
| **SUM** | `/usr/sap/<SID>/SUM/abap/log/` — upgrade/update logs (OS side) |

## 6. ABAP — workflow & background frameworks

**SWI1** (work items), **SWI2_FREQ/SWI2_DURA**, **SWEL / SWELS** (event trace), **SWU3** (workflow
customizing check), **SWUD** (diagnosis). Many applications also log to **SLG1**.

## 7. AS Java stack (only if AS Java / PI-PO / EP is installed)

| Where | What |
|-------|------|
| **NWA → Log Viewer** (`/nwa`) | Central Java log/trace UI |
| `defaultTrace.<n>.trc` | Main Java trace — `/usr/sap/<SID>/J<nr>/j2ee/cluster/server<n>/log/` |
| `applications.<n>.log`, `security.<n>.log`, `system_<...>.log` | Category logs, same directory |
| `dev_jcontrol`, `dev_server<n>`, `dev_bootstrap`, `std_server<n>.out` | Java node control/stdout — instance **work** dir |
| **NWA → Log Configuration** | Raise/lower Java trace severity per location |

## 8. Kernel / OS (instance work directory)

Full file map in [app-and-component-logs.md](app-and-component-logs.md): `dev_disp`, `dev_w*`, `dev_ms`,
`dev_rd`, `dev_icm`, `dev_rfc*`, `dev_enq*`, `stderr*`, `sapstart.log`, `available.log`.

Plus the host itself:
- **Linux:** `journalctl -u ...`, `/var/log/messages`, `dmesg` (OOM-killer!), `/var/log/audit`
- **AIX:** `errpt -a`, `/var/adm/ras/`
- **Windows:** Event Viewer (System / Application)
- **saposcol** / **ST06** — OS-level CPU, memory, disk, network history
- **SAP Host Agent:** `/usr/sap/hostctrl/work/` (`dev_saphostexec`)

> `dmesg`/OOM-killer and a full filesystem (`df -h`) explain a large share of "the system just died"
> cases that show nothing in SM21.

## 9. Standalone components

Web Dispatcher (`dev_webdisp`), SAProuter (`-T` trace, `-G` log), Cloud Connector (`ljs_trace.log`),
IGS (`dev_igs*`) — see [app-and-component-logs.md](app-and-component-logs.md).

## 10. Database

Per-engine log locations and readers (HANA trace dir + alert, Oracle `alert_<SID>.log` + ADR, ASE
errorlog, Db2 `db2diag.log`, MaxDB `KnlMsg`, SQL Server `ERRORLOG`) — see [db-logs.md](db-logs.md).
From inside SAP: **ST04 / DBACOCKPIT** (DB monitor), **DB02** (space), **DB12** (backup logs),
**DB13** (DBA calendar job logs).

## 11. Monitoring & aggregation (often the fastest path to "when did it start?")

**RZ20** (CCMS alert monitor) · **RZ21** · **SAP Solution Manager** technical monitoring / E2E trace ·
**SAP Focused Run** (system + real-user monitoring, ICM) · **SAP Cloud ALM** · SAP Host Agent metrics.

---

## Sources

- **[A1]** **SAP Note 2191612** — *FAQ | Use of Security Audit Log as of SAP NetWeaver 7.50*. **[V]**
  Retrieved via the SAP Notes MCP (v108, 2026-07-01): confirms `RSAU_CONFIG` / `RSAU_READ_LOG` /
  `RSAU_ADMIN` as of SAP_BASIS 7.50 SP03, the `DIR_AUDIT` / `FN_AUDIT` profile parameters, integrity
  protection and log-table reorganization in `RSAU_ADMIN`. Related: **539404** (< 7.50 SP03),
  **2676384** (best practice on-prem/private cloud), **3500099** (managing log data),
  **3667538** (switch file storage → database), **2903873** (public cloud).
  https://me.sap.com/notes/2191612
- **[A2]** **SAP Note 3571619** — *SM19 transaction became display and only RSAU_CONFIG is working*;
  and **3556947** — *Can SM19 be used along with RSAU_CONFIG…*. https://me.sap.com/notes/3571619
- Transaction roles otherwise per the SAP Help Portal *Log and Traces* map (see [../SKILL.md](../SKILL.md) §Sources [G1])
  and the component guides referenced there.
