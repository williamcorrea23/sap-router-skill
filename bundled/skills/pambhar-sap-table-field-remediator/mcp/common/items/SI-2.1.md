---
item_id: SI-2.1
title: "2.1 ABAPTWL - Visualization of SAP Business Workflow Metadata"
pages: 33-38
sap_notes: [1829697, 2862972, 2862992, 2865890, 2886479, 2896183, 2926680, 2926764]
components: [BC-BMT-WFM]
objects: []
---
## Application Components:BC-BMT-WFM

Related Notes:

| Note Type       |   Note Number | Note Description                                          |
|-----------------|---------------|-----------------------------------------------------------|
| Business Impact |       2896183 | ABAPTWL - visualization of SAP Business Workflow metadata |

## Symptom

With the upgrade or system conversion to SAP S/4HANA 2020, all SWFVISU settings are overwritten with the delivery data. Customer-specific workflow tasks may respond differently at runtime or are not displayed as usual.

## Reason and Prerequisites

For technical reasons, the delivery class of SWFVISU tables had to be changed from type "G" to "E". With type "G", customers could only add data records delivered by SAP. Existing settings were not overwritten. Type "E" also allows changing contents.

## Solution

## Description

You make the settings for displaying tasks and object types using SWFVISU or SWFVMD1.

SWFVISU saves the settings for all clients and is used by SAP to deliver the data.

SWFVMD1 saves the data client-dependently (customizing) and should be used by customers to enter own settings or overwrite data delivered by SAP.

Up to now, SWFVISU settings were not overwritten on the customer side. Only data that was newly delivered by SAP was added.

Business-Process-Related Information If you have entered your own settings in SWFVISU or have adjusted delivered data, the appearance or response of individual work items in MyInbox may change.

## Required and Recommended Action(s)

Transfer your settings manually to SWFVMD1 before the upgrade or conversion.

Call transaction SWFVISU.

Call transaction SWFVMD1 in a second window.

Transfer only your changed settings to SWFVMD1 and save them.

To be on the safe side, you can export the entire content of SWFVISU to a Microsoft Excel file. This file serves only documentation purposes and cannot be imported automatically.

## Other Terms

IMG activity: Visualization of SAP Business Workflow Metadata

## 2.2 ABAP4TWL - Removal of Tagging Framework

Application Components:BC-SRV-TFW

Related Notes:

| Note Type       |   Note Number | Note Description                          |
|-----------------|---------------|-------------------------------------------|
| Business Impact |       2865890 | Package STFW and Sub-Packages are missing |

## Symptom

The packages STFW and its sub-packages STFW_* of re-use component Tagging Framework are missing.

## Reason and Prerequisites

Tagging Framework functionality has been withdrawn.

## Solution

The functionality has been withdrawn without replacement.

## Other Terms

STFW

## 2.3 ABAP4TWL - Removal LT Check ATC Adapter

Application Components:BC-CUS-TOL-LT

Related Notes:

| Note Type       |   Note Number | Note Description                  |
|-----------------|---------------|-----------------------------------|
| Business Impact |       2862972 | Package S_CHECK_SAP_LT is missing |

## Symptom

Package S_CHECK_SAP_LT containing checks for consistency of long text are deleted in ABAP Platform.

## Reason and Prerequisites

The checks belong to an SAP internal use case and have been withdrawn.

## Solution

There is no substitution for programmatic usage.

All checks relevant for quality assurance of ABAP programs are part of the ABAP Test Cockpit test content.

## Other Terms

CL_ATC_ADP_LT_CDOC_CHECK, CL_CHK_LT_CDOC_CHECK, CL_ATC_ADP_LT_FIELD_CHECK, CL_CHK_LT_FIELD_CHECK

## 2.4 ABAP4TWL - Removal of ILM Store Monitoring GUI

Application Components:BC-ILM-STO

Related Notes:

| Note Type       |   Note Number | Note Description                                                       |
|-----------------|---------------|------------------------------------------------------------------------|
| Business Impact |       2926764 | Packages S_ILM_STOR_MONITOR_CSV and S_ILM_STOR_MONITOR_GUI are missing |

## Symptom

Package S_ILM_STOR_MONITOR_CSV and S_ILM_STOR_MONITOR_GUI of solution management are missing.

## Reason and Prerequisites

The functionality is replaced by other functionality in SAP Solution Manager. There is no direct recommendation to replace the deleted code, because functionality is tailored differently.

## Solution

The functionality has been withdrawn without without replacement.

## Other Terms

Package S_ILM_STOR_MONITOR_CSV

Package S_ILM_STOR_MONITOR_GUI are missing

## 2.5 ABAP4TWL - Removal of Drag and Relate Workplace Plugin

Application Components:CA

Related Notes:

| Note Type       |   Note Number | Note Description                                                    |
|-----------------|---------------|---------------------------------------------------------------------|
| Business Impact |       2862992 | Packages DRSCENARIOS, POR4, PORX and PORX_COMPATIBILITY are missing |

## Symptom

The packages DRSCENARIOS, POR4, PORX and PORX_COMPATIBILITY of Workplace Plug-in 3.0 and Workplace Plug-in 4.0 are missing.

## Reason and Prerequisites

"Drag & Relate" functionality has been withdrawn, see also SAP Note 1829697.

## Solution

The functionality has been withdrawn without replacement.

## Other Terms

Business Object Type DRDYNFIELD

Function Groups SDW4, SDWP, SDWZ, SPR4, SPRT

Transaction SPO0, SPO1, SPO4, SPO4_DISP, SPO5

## 2.6 ABAP4TWL - Removal of Package SCMO

Application Components:SV-SMG-SDD

Related Notes:

| Note Type       |   Note Number | Note Description        |
|-----------------|---------------|-------------------------|
| Business Impact |       2926680 | Package SCMO is missing |

## Symptom

The package SCMO covering CRM Service Data download functionality is missing

## Reason and Prerequisites

The functionality is replaced by other business functionality. There is no direct recommendation to replace the deleted code, because business functionality is tailored differently.

## Solution

The functionality has been withdrawn without replacement.

## Other Terms

Package SCMO, Function Group CMON

## 2.7 ABAP4TWL - Removal of ByDesign Config Framework Services

## Application Components:BC-CFG-RT

Related Notes:

| Note Type       |   Note Number | Note Description                                    |
|-----------------|---------------|-----------------------------------------------------|
| Business Impact |       2886479 | Package C2_SERVER and its sub- packages are missing |

## Symptom

The package C2_SERVER and its sub-packages are missing.

## Reason and Prerequisites

Configuration framework used in older cloud products of SAP has been removed from latest product versions of SAP CP ABAP Environment, S/4HANA CE, S/4HANA OP and similar.

## Solution

There is no replacement of the functionality.

## Other Terms

C2_BCSETS, C2_CORE, C2_EXCEPTION, C2_INTERFACES, C2_SERVER, C2_SERVER_FRAMEWORK, C2_SERVICES, SC2_IDE, SC2_IDE_APP_SYS, SC2_MDA_GEN, SC2_META_REP, SC2_PERSISTANCE, SC2_REP_SERVICES
