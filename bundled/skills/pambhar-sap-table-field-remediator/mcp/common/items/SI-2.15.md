---
item_id: SI-2.15
title: "2.15 ABAPTWL - Instances without ICM not supported"
pages: 45-45
sap_notes: [2560792]
components: [BC-CST-IC]
objects: []
---
Application Components:BC-CST-IC

Related Notes:

| Note Type       |   Note Number | Note Description                                                 |
|-----------------|---------------|------------------------------------------------------------------|
| Business Impact |       2560792 | ABAP instances in SAP S/4HANA always start with an icman process |

## Symptom

AS ABAP instance always starts with an ICM process. Parameter rdisp/start_icman no longer exists and is ignored.

## Reason and Prerequisites

The configuration option was removed.

## Solution

Intended behaviour.

Other Terms

ICM, Instance
