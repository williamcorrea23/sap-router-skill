# Cleanup catalog — standard jobs, directory map, never-delete list

Reference detail for [../SKILL.md](../SKILL.md). ABAP jobs are OS-independent; file paths shown UNIX with
the Windows equivalent noted.

## Extended standard / reorg jobs (SAP Note 16083)

| Job | Report | Cleans / does | Typical freq |
|-----|--------|---------------|--------------|
| `SAP_REORG_JOBS` | `RSBTCDEL2` | delete old job logs (SM37) | daily |
| `SAP_REORG_SPOOL` | `RSPO1041` | delete old spool requests (SP01) | daily |
| `SAP_SPOOL_CONSISTENCY_CHECK` | `RSPO1043` | spool consistency | daily |
| `SAP_REORG_ABAPDUMPS` | `RSSNAPDL` | delete old ST22 dumps | daily |
| `SAP_REORG_BATCHINPUT` | `RSBDCREO` | delete old SM35 batch-input sessions | daily |
| `SAP_REORG_JOBSTATISTIC` | `RSBPSTDE` | delete old job statistics | monthly |
| `SAP_REORG_UPDATERECORDS` | `RSM13002` | delete old SM13 update records | daily |
| `SAP_COLLECTOR_FOR_PERFMONITOR` | `RSCOLL00` | collect + reorg ST03/ST06 perf data | hourly |
| `SAP_REORG_XMILOG` | `RSXMILOGREORG` | reorg external management interface log | weekly |
| `SAP_REORG_PRIPARAMS` | `RSBTCPRIDEL` | delete orphaned print parameters | monthly |
| (IDoc) | `RSETESTD` / `RSARFCEX` reorg | tRFC/qRFC + IDoc housekeeping (SM58/BD87) | per policy |

Retention is set in each job's **variant** (e.g. minimum age in days). Configure once; the jobs then run
retention-aware. SM65 checks background-processing consistency.

## Directory map (what lives where)

| Path (UNIX / `Windows`) | Contents | Cleanup |
|-------------------------|----------|---------|
| `/usr/sap/<SID>/<INST><nr>/work` (`…\work`) | `dev_*` traces, `stderr*`, `*.OLD`, `core*`, `sapstart.log`, `available.log` | §3 — old files; reset live via SM50/SMGW |
| `/usr/sap/<SID>/<INST><nr>/log` (`…\log`) | `*.AUD` security audit, instance logs | §4 — SM18 (audit ⚠️ retention) |
| `/sapmnt/<SID>/global` (`\\<host>\sapmnt\<SID>\SYS\global`) | `WF_LOG_*` workflow, shared global files | old `WF_LOG_*` deletable |
| `/usr/sap/trans/{cofiles,data,log}` | transport cofiles/data/logs | ⚠️ transport dir — reorg carefully, keep what QAS/PRD still need |
| DB dirs (`/oracle/<SID>`, `/hana/log`, `/db2/<SID>`) | redo/archive/log segments, DB traces | §6 — DB tools **after backup** only |
| OS `/tmp`, `/var/tmp` | transient SAP/install temp | old files, not active install/SUM temp |

## Never delete (without the right tool / confirmation)

- **Un-backed-up DB transaction/redo/archive logs** — breaks recovery. Use DB tools after backup.
- **Security audit `*.AUD`** within the mandated retention window — compliance. Use SM18 + policy.
- The **currently-active** `dev_disp` / `dev_ms` / `dev_icm` of a **running** instance — reset via
  SM50/SMGW instead.
- `/usr/sap/trans` cofiles/data still needed by downstream systems (QAS/PRD import queues).
- Live **SUM/upgrade** working directories during an in-flight upgrade.

## Sources

Same as [../SKILL.md](../SKILL.md) §Sources: SAP Note 16083 [K1], Notes 130978/48400 [K2], audit-log docs
[K3], OS-file housekeeping [K4], HANA housekeeping guide [K5].
