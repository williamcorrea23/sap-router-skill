---
item_id: SI-3.3
title: "3.3 S4TWL - Logistics Batch Management"
pages: 127-128
sap_notes: [2267298]
components: [LO-BM-MD]
objects: []
---
Application Components:LO-BM-MD

Related Notes:

| Note Type       |   Note Number | Note Description                   |
|-----------------|---------------|------------------------------------|
| Business Impact |       2267298 | S4TWL - Logistics Batch Management |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

The following transactions related to Logistics Batch Management are not available in SAP S/4HANA, on-premise edition 1511: MSC1, MSC2, MSC3 and MSC4. The functional equivalent in SAP S/4HANA, on-premise edition 1511 are the following transactions:

MSC1N Create Batch

MSC2N Change Batch

MSC3N Display Batch

MSC4N Display Change Documents for Batch

As of Release 4.6A, the maintenance of batch master data has been completely reworked and assigned to new transaction codes. Already at this point in time it was recommended to use the new transaction codes (MSC*N). The previous transactions and with that the belonging program code are not available within SAP S/4HANA, on-premise edition 1511.

## Business Process related information

No influence on the business process - alternatively mentioned transaction codes need to be used.

| Transaction not available in SAP S/4HANA on-premise edition 1511   | MSC1   |
|--------------------------------------------------------------------|--------|
