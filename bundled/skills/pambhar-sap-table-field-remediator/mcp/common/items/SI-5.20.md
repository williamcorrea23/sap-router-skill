---
item_id: SI-5.20
title: "5.20 S4TWL - Contract Processing Monitor & Logistical Options w/ GTM not supported"
pages: 210-211
sap_notes: [2672696]
components: [LO-GT-CMM, LO-CMM-BF]
objects: []
---
Application Components:LO-GT-CMM, LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                           |
|-----------------|---------------|------------------------------------------------------------------------------------------------------------|
| Business Impact |       2672696 | S4TWL - Integration of Contract Processing Monitor(CPM) and Logistical Options(LOP) with GTM not supported |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

With SAP S/4HANA, All on-premise editions, the integration of Global Trade Management (GTM) with Commodity Management processes (not ACM!) is partially supported.

Contract Processing Monitor (CPM) and Logistical Options (LOP) are not supported in S/4HANA. Also, there is no equivalent available for the same.

If you are okay with this limitation, you can add an exemption and continue in report /SDF/RC_START_CHECK.
