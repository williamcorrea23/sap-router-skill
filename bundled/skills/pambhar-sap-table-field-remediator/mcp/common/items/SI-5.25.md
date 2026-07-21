---
item_id: SI-5.25
title: "5.25 S4TWL - Performance Optimization of Risk Analytics CDS Views"
pages: 216-218
sap_notes: [3327638]
components: [LO-CMM-BF, LO-CMM-ANL]
objects: []
---
Application Components:LO-CMM-BF, LO-CMM-ANL

Related Notes:

| Note Type       |   Note Number | Note Description                                                                         |
|-----------------|---------------|------------------------------------------------------------------------------------------|
| Business Impact |       3327638 | S4TWL - CM Replacement of Risk Analytics CDS Views by new performance optimized versions |

## Symptom

With S4 HANA 2021 new CDS views for Commodity Risk Analytics have been delivered having multiple performance optimizations compared to the CDS views delivered in lower versions.

As some of these changes require a data migration in underlying risk information tables (like table CMM_VLOGP), the optimization have been shipped in new views.

From S4HANA 2023 FP0 upwards the old CDS views are deprecated and usage should be removed as they will be deleted in a future Release.

## Reason and Prerequisites

You are upgrading to S4HANA 2023 FP0 or higher.

Your are using CDS views which will get obsolete in subsequent Releases.

## Solution

Requied Data migration is happening with Silent Data Migration (SDMI) when upgrading to 2021 FP0 or higher.

If using SAP Standard Queries listed below as deprecated, use the new Query delivered as replacement as per belows list.

If having an own Query on top of a Cube listed below as deprecated, adapt your Query to use the new Cube.

| Obsolete                   | to be replaced by              | Descriptio n             |
|----------------------------|--------------------------------|--------------------------|
| Queries                    |                                |                          |
| C_CMMDTYMTMLOGEODQRY       | C_CMMDTYMTMLOGENDOFDAYQRY_2    | MtM end- of-day          |
| C_CMMDTYMTMLOGDODQRY       | C_CMMDTYMTMLOGDAYOVERDAYQRY _2 | MtM day- over-day        |
| C_CMMDTYMTMLOGCURQRY       | C_CMMDTYMTMLOGCURRENTDAYQRY _2 | MTM Current Day          |
| C_CMMDTYMTMSTKEODQRY       | C_CMMDTYSTOCKENDOFDAYQRY       | MtM stock day-over- day  |
| C_CMMDTYBPPNLVALUE_QUERY   | C_CMMDTYBEGINPOSPNLVALQRY      | Beginning Position (P/L) |
| C_CMMDTYNAPNLVALUE_QUERY   | C_CMMDTYNEWACTPNLVALQRY        | New Activity (P/L)       |
| C_CMMDTYPOSENDOFDAYQRY     | C_CMMDTYPOSENDOFDAYQRY_2       | Position end of day      |
| C_CMMDTYPOSCURRENTDATEQR Y | C_CMMDTYPOSCURRENTDATEQRY_2    | Position current day     |
| C_CMMDTYPOSDAYOVERDAYQRY   | C_CMMDTYPOSDAYOVERDAYQRY_2     | Position Day Over Day    |
| C_CMMDTYMTMENDOFDAYQRY     | C_CMMDTYMTMENDOFDAYQRY_2       | Union MtM End-of- Day    |

| C_CMMDTYMTMDAYOVERDAYQRY      | C_CMMDTYMTMDAYOVERDAYQRY_2      | Union MtM Day over Day                    |
|-------------------------------|---------------------------------|-------------------------------------------|
| C_CMMDTYMTMCURRENTDATEQR Y    | C_CMMDTYMTMCURRENTDATEQRY_2     | Union MtM Current Value                   |
| C_CMMDTYPOSVALUEATRISKQRY     | C_CMMDTYPOSVALUEATRISKQRY_2     | Commodit y Position EoD Interface - Query |
| Cubes                         |                                 |                                           |
| I_CMMDTYMTMVALUECUBE          | I_CMMDTYMTMVALUECUBE_2          | MTM Cube                                  |
| I_CMMDTYMTMVALUECUBE          | I_CMMDTYSTOCKVALUECUBE          | MTM Stock Cube                            |
| I_CMMDTYMTMLOGFINVALCUBE      | I_CMMDTYMTMLOGFINVALCUBE_2      | UNION MTM Cube                            |
| I_CMMDTYBPPNLVALUE_CUBE       | I_CMMDTYBEGINPOSPNLVALCUBE      | Beginning Position (P/L) Cube             |
| I_CMMDTYNAPNLVALUE_CUBE       | I_CMMDTYNEWACTPNLVALCUBE        | New Activity (P/L) Cub e                  |
| I_CMMDTYPOSITIONREPQTYCUBE    | I_CMMDTYPOSITIONREPQTYCUBE_2    | Position CUbe                             |
| I_CMMDTYPOSVALUEATRISKCUBE    | I_CMMDTYPOSVALATRISKCUBE_2      | Commodit y Position Interface - Cube      |
| Other Public I-Views          |                                 |                                           |
| I_CMMDTYBPPNLVALUE            | I_CMMDTYBEGINPOSPNLVALUE        | PnL Value for Beginning Position          |
| I_CMMDTYNAPNLVALUE            | I_CMMDTYNEWACTPNLVALUE          | Commodit y PnL Value New activity         |
| I_CMMDTYPOSVALUEATRISKCNVR SN | I_CMMDTYPOSVALUEATRISKCNVRSN_ 2 | Conversio n of quantity                   |

fields
