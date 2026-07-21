---
item_id: SI-2.44
title: "2.44 S4TWL - SAP HANA LIVE REPORTING"
pages: 106-107
sap_notes: [2270382]
components: [XX-SER-REL]
objects: []
---
Application Components:XX-SER-REL

Related Notes:

| Note Type       |   Note Number | Note Description                |
|-----------------|---------------|---------------------------------|
| Business Impact |       2270382 | S4TWL - SAP HANA Live Reporting |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

SAP HANA Live provides reporting capabilities for Business Suite and Suite on HANA customers. In S/4HANA, database tables have changed in many areas. Thus, the Hana Live Calc Views will not work on those changed structures. In addition, a strategic decision was taken to switch the technology from Calculation Views to CDS Views with SAP S/4HANA. Reporting scenarios built with the SAP HANA Live content in Business Suite, Suite on HANA, or Simple Finance installations have either to be adjusted manually to the changed DB-table structures or to be rebuilt manually with CDS Views in SAP S/4HANA.

## Business Process related information

It should be possible to rebuild all existing reporting scenarios with CDS Views. Limitations might exist with respect to consumption.

## Required and Recommended Action(s)

If HANA Live views are used, time and resources should be planned for migration to CDS Views or for implementation of the additional RDS package (if that is available).

## Related SAP Notes

| Custom Code related information   | If the customer copied calc views delivered by SAP or created user- defined calc views on top of SAP delivered views, those   |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------|

potentially need to be redone to reflect changed DB-table structures (in case there are some).
