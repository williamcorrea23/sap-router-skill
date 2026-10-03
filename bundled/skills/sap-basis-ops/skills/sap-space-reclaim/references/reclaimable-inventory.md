# Reclaimable data inventory

Extracted from **SAP Note 2388483** (*How-To: Data Management for Technical Tables*, HAN-DB, **v288**,
2026-07-27), retrieved and parsed via the SAP Notes MCP during authoring. **[V]**

That Note is the authoritative and continuously-updated source — entries are added most months. **Re-fetch
it at the start of every assessment**; this file is a Basis-focused extract, not a replacement.

Scope of the Note: tables with a *technical* background — communication, logging, tracing, administration,
analysis, metadata, staging, auditing. It explicitly **does not** cover application tables; for those, use
the Data Management Guide (Data Volume Management) and **SAP Note 3582156**. Valid for **all** databases.
It replaces the older SAP Note 706478.

---

## Finding the biggest offenders first

| DB | SAP-delivered statement | Note |
|---|---|---|
| SAP HANA | `HANA_Tables_LargestTables` with `ONLY_TECHNICAL_TABLES 'X'` | **1969700** |
| Oracle | `Space_LargestTables` with `ONLY_BASIS_TABLES 'X'` | **1438410** |

Otherwise `DB02` / `DBACOCKPIT` → space → largest tables. Then **`TAANA`** to get the distribution by date
and client, which is what converts a table size into an *estimated reclaim*.

---

## Catalogue — Basis / technical areas

Columns: **Tables** · **Area** · **SAP Notes** · **Clean with**

| Tables | Area | Notes | Clean with |
|---|---|---|---|
| `TSP01`, `TSP02`, `TST01`, `TST03`, `TSPADS`, `TSPEVJOB` | ABAP TemSe / spool | 48400 | `RSPO0041`, `RSPO1041`, `RSPO1043`, `RSBTCDEL2`, `RSBDCREO` |
| `DBTABLOG`, `DBTABPRT` | ABAP table logging | 2335014, 2362854 | **`SCU3`**, report `RSTBPDEL`; `S_AUT_ARCH_STXL_CLEAN` for orphan STXL |
| `BALC`, `BALDAT`, `BALHDR`, `BALHDRP`, `BAL_INDX`, `BALM`, `BALMP` | ABAP application log | 195157, 2057897, 3039724, 3742661 | **`SLG2`**, `SBAL_DELETE`, `SBAL_DELETE_ORPHAN_MESSAGES`, `SBAL_STATISTICS` |
| `SNAP` | ABAP short dumps | 11838 | `RSSNAPDL` |
| `BTCJOBEPP`, `TBTCCNTXT`, `TBTCO`, `TBTCP`, `TBTCS`, `TBTC_TASK` | ABAP jobs | 16083, 666290, 1440439 | `RSBTCDEL2`, `RSBTCCNS`, `RSTS0024` |
| `TBTCJOBLOG`, `TBTCJOBLOG0`–`TBTCJOBLOG9` | ABAP job logs | 666290, 1440439, 2360818 | `RSBTCDEL2`, `RSBTCCNS` |
| `EDI30C`, `EDI40`, `EDID4`, `EDIDC`, `EDIDOC`, `EDIDS` | ABAP IDoc | 40088, 1574016 | `RSEXARCA`, `RSEXARCB`, `RSEXARCD`, `RSEXARCL`, `RSEXARCR`, `RSETESTD` |
| `ARFCRSTATE`, `ARFCSDATA`, `ARFCSSTATE`, `TRFCQDATA`, `TRFCQIN`, `TRFCQOUT`, `TRFCQSTATE` | ABAP RFC / qRFC | 375566 | **`SMQ1`**, **`SMQ2`**, **`SM58`** |
| `ARFCLOG` | ABAP RFC logging | 802062, 2363550 | `RSARFCLE`, `RSARFCLR` |
| `SWNCMONI`, `SWNCM_TIMES`, `SWNCM_*` | ABAP workload collector | 2274315 | **`ST03`** — *adjustment of retention times* |
| `CDHDR`, `CDPOS`, `CDPOS_STR`, `CDPOS_UID` | ABAP change documents | 3015823 | **`SARA`** — archiving object `CHANGEDOCU` |
| `APQD` (+`APQI`) | ABAP batch input | 36781 | **`SM35`**, `RSBDCREO` |
| `BCST_CAM`, `BCST_SR`, `SOC3`, `SOC3N`, `SOFFCONT1`, `SOFM`, `SOOD`, `SOOS`, `SOST` | ABAP SAPoffice | 966854, 1641830 | `RSBCS_REORG` |
| `BDCP`, `BDCPS`, `BDCP2` | ABAP ALE change pointers | 513454 | **`BD22`**, `RBDCPCLR` |
| `SWWWIHEAD`, `SWWLOGHIST`, `SWWLOGPARA`, `SWW_CONT`, `SWW_CONTOB`, `SWWUSERWI`, `SWW_WI2OBJ`, … | ABAP work items | 49545, 1552169 | `RSWWHIDE`, `RSWWWIDE`, `RSWWWIDE_DEP` |
| `SWN_NOTIF`, `SWN_NOTIFTSTMP`, `SWN_SENDLOG` | ABAP workflow notifications | 722840 | `RSWNNOTIFDEL` |
| `SWF_TRC_CONT` | ABAP workflow default trace | 2847116 | `SWF_TRC` |
| `SRRELROLES`, `IDOCREL`, `SMW0REL` | ABAP object links | 493156, 505608 | `RSRLDREL` |
| `ARDB_STAT0/1/2`, `TAAN_DATA`, `TAAN_FLDS`, `TAAN_HEAD` | ABAP table analysis | 2034063 | **`TAANA`**, `TAAN_DELETE_ANALYSES` |
| `RSAU_BUF_DATA`, `RSAU_LOG` | ABAP security audit log | — (see 3137004) | `RSAU_ADMIN` → archive `BC_SAL` → delete |
| `/SDF/MON`, `/SDF/SMON_CLUST`, `/SDF/SMON_WPINFO` | ABAP snapshot monitor | 2651881 | **`/SDF/SMON`** |
| `SQLMD`, `/SDF/ZQLMD` | ABAP SQL monitor | 1885926 | **`SQLM`** |
| `ECLOG_*` (`ECLOG_CALL`, `ECLOG_DATA`, `ECLOG_HEAD`, …) | ABAP eCATT | 1052908 | `RSECATTLOGDEL`, archiving object `ECATT_LOG` |
| `ENHLOG` | ABAP enhancement logs | 2229441 | `ENH_SHRINK_ENHLOG` |
| `DDLOG` | ABAP buffer synchronization | 36283 | **TRUNCATE possible — only while ABAP is stopped** |
| `DDPRS` | ABAP dictionary logs | 370475 | `RADPROTA`, `RADPROTB` |
| `D010INC`, `D010TAB`, `REPOLOAD`, `REPOSRC` | ABAP repository | 1918229, 2610985 | `RS_LOAD_FORMAT_ADM`, `SFW5` |
| `INDX` | ABAP binary data export | 3992 | — |
| `IDOCTRACE` | ABAP ALE trace | 2994833 | `WEIDOCTRACE` |
| `TXMILOGRAW`, `SPEVDEV` | ABAP XMI interface | 182963 | `RSXMILOGREORG` |
| `BGRFC_IUNIT_HIST` | ABAP bgRFC unit histories | 2689595 | `RS_BGRFC_DEL_UNIT_HISTORY`, `CL_BGRFC_UNIT_HISTORY→DELETE_UNITS_I_MAX_BY_DEST` |
| `CCTABCONTSLDATA` | ABAP client copy data | 3072781 | **`SCC3_ADMIN`** |
| `UASE16N_CD_DATA`, `UASE16N_CD_KEY` | ABAP SE16N change log | 2339105 | `ZUASE16N_CD_DELETE` |
| `AQLDB` | ABAP SAP query lists | 2336268 | `RSAQQLRE_MASS` |
| `ESH_EX_CPOINTER` | ABAP enterprise search change pointers | 2790191, 2786189 | `ESH_DELETE_CHANGEPOINTERS` |
| `FEH_MESS_PERS` | ABAP postprocessing orders | 3477098 | `/SAPPO/DELETE_OR…` |
| `SPAF_ERR_LOG_MSG`, `SPAF_ERR_MSG` | ABAP PAF error logs | — | `SPAF_PIP_DELETE_PIIE` |
| `SRTM_*`, `SRTMP_*` | ABAP runtime monitor | 2548106 | `SQLM_UPDATE_DATA` / `SCHEDULE` |
| `RSDDSTAT*` (`RSDDSTATHEADER`, `RSDDSTATINFO`, …) | BW statistics | 934848, 1018114 | **`RSDDSTAT`**, `RSDDSTAT_DATA_DELETE` |
| `DYNPSOURCE`, `DYNPLOAD` | BW ABAP screens | 1953628 | `RSDQ_DYNP_GP_CLEAN` |
| `/BI0/0*` | BW temporary data | 449891, 1139396, 2353663 | `SAP_DROP_TMPTABLES`, `RSDU_DROP_TMPTABLES_HDB` |
| `AUDIT_LOG_*` | **HANA audit log** | 2159014, 2308083, 2599832, 2676016, 3084473 | `ALTER SYSTEM CLEAR AUDIT LOG`; `ALTER AUDIT POLICY … SET RETENTION` (≥ 2.0 SPS 04) |
| `INIFILE_CONTENT_HISTORY_*` | HANA parameter change history | 2186744 | `ALTER SYSTEM CLEAR INIFILE CONTENT HISTORY [UNTIL '…']` |
| `DB2DB02*` (`DB2DB02TSSIZE`, …) | ABAP DBACOCKPIT Db2 histories | — | DBACOCKPIT history retention |
| `SMOHQUEUE`, `SMW3_BDOCQ`, `SMWT_TRC` | CRM middleware | 206439, 536414 | `SMO6_REORG`, `SMO6_REORG2` |
| `DSVAS*` | Solution Manager session data | 1300107, 2075483 | `RDSMOPREDUCEDATA` |
| `E2EREP_MAPPING` | Solution Manager reporting mappings | 1908700 | `E2EREP_MAPPING_CLEANUP` |

---

## Reading the Note yourself

The Note's body is a long HTML table preceded by a substantial **change history** — the history is *not*
the catalogue, so skip past it. A quick way to pull the current entry for a table:

```bash
# via the SAP Notes MCP: fetch 2388483, then search the content for the table name.
# Row shape is:  TABLE1, TABLE2  <area><topic><note numbers>  <transaction/report>
```

Because the Note carries no stable per-row anchors, always quote **both** the table name and the SAP Note
number(s) from the row when proposing a cleanup, so the recommendation can be re-verified later.
