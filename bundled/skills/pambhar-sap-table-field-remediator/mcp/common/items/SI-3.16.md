---
item_id: SI-3.16
title: "3.16 S4TWL - API RFC_CVI_EI_INBOUND_MAIN is obsolete"
pages: 148-149
sap_notes: [2417298, 2506041]
components: [LO-MD-BP]
objects: []
---
## Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                                              |
|-----------------|---------------|-------------------------------------------------------------------------------------------------------------------------------|
| Business Impact |       2506041 | S4TWL - API RFC_CVI_EI_INBOUND_MAIN is not supported from the release S/4 HANA OP 1709 FPS2 and in Cloud Edition 1805 onwards |

## Symptom

Customer is migrating to SAP S/4HANA on-premise edition, and they are using function module RFC_CVI_EI_INBOUND_MAIN to migrate business partners.

## Reason and Prerequisites

RFC_CVI_EI_INBOUND_MAIN in SAP S/4HANA, was initially used to migrate business partners.

## Solution

## Description

RFC_CVI_EI_INBOUND_MAIN is used to update/create BP in S/4 HANA. However, it is not the recommended approach as it doesn't cover all the features.

RFC_CVI_EI_INBOUND_MAIN is not an officially released SAP Function module and was created for internal use only. Hence, it has been decided to stop supporting this function module from the OP release 1709 FPS2  and in Cloud Edition 1805 onwards.

Customers should refer to the SAP Note 2417298 for maintenance of Business Partners.

## Business Process related information

No impact on business processes is expected.

## Required and Recommended Action(s)

Check if you use RFC CVI_EI_INBOUND_MAIN for creating/changing customer master or supplier master data. If yes, please switch to the recommended alternatives in the SAP Note 2417298.

## Other Terms

Business Partner, RFC CVI_EI_INBOUND_MAIN, Customer Master, Supplier Master
