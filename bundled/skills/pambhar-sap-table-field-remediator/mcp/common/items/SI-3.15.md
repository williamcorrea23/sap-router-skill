---
item_id: SI-3.15
title: "3.15 S4TWL - Batch Input for Customer Master/Supplier Master"
pages: 147-148
sap_notes: [2472030, 2492904]
components: [LO-MD-BP]
objects: []
---
Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                        |
|-----------------|---------------|---------------------------------------------------------|
| Business Impact |       2492904 | S4TWL - Batch Input for Customer Master/Supplier Master |

Symptom You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

Batch Input as a technology to maintain customer master and supplier master data will not be supported in release from SAP S/4HANA 1809 onwards.

Since we follow "Business Partner first" approach in SAP S/4HANA, Batch Input programs will now work with API based approach which would replace the traditional Batch Input technology as classical customer and supplier transactions have been made obsolete.

As an alternative, we recommend the usage of the following:

Business Partner SOAP Services. Refer to SAP Note 2472030 for more information.

IDocs (CREMAS/DEBMAS)

Mass Transactions (XK99/XD99)

## Business Process related information

No influence on business processes is expected.

## Required and Recommended Action(s)

Please check if you use Batch Input for creating/changing customer master or supplier master data. If yes, please switch to the recommended alternatives.
