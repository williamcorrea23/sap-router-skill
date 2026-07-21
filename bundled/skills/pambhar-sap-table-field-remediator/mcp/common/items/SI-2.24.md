---
item_id: SI-2.24
title: "2.24 S4TWL - SAP Support Desk ($$-Messages)"
pages: 60-61
sap_notes: [2852082]
components: [CA-NO, QM-QN]
objects: []
---
Application Components:CA-NO, QM-QN

Related Notes:

| Note Type       |   Note Number | Note Description                                                   |
|-----------------|---------------|--------------------------------------------------------------------|
| Business Impact |       2852082 | S4TWL - existence check for basis notification and $$ notification |

## Symptom

You use $$ notifications and basic notifications that were created in table DNOD_NOTIF. The function module DNO_OW_EXTERN_SEND_NOTIF_2_BC, which was used to create basic notifications, is no longer supported in SAP S/4HANA.

## Reason and Prerequisites

Renewal

## Solution

## Business value

Instead of the $$ notifications and basis notifications, SAP Support is available via SAP Support Portal at https://support.sap.com.

## Required and recommended action(s)

Check whether an entry has been defined in the table DNOD_NOTIF.

## Other Terms

$$, $$ notifications, support notifications, enter support notifications, DNOD_NOTIF, function module DNO_OW_EXTERN_SEND_NOTIF_2_BC, DNO_OW_EXTERN_SEND_NOTIF_2_BC
