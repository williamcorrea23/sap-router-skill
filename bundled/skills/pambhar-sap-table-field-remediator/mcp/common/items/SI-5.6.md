---
item_id: SI-5.6
title: "5.6 S4TWL - Simplified Commodity Curves"
pages: 194-195
sap_notes: [2551913, 2553281]
components: [LO-CMM-BF, FIN-FSCM-TRM-MR]
objects: []
---
Application Components:LO-CMM-BF, FIN-FSCM-TRM-MR

Related Notes:

| Note Type       |   Note Number | Note Description                        |
|-----------------|---------------|-----------------------------------------|
| Business Impact |       2551913 | S4TWL - CM: Simplified Commodity Curves |

## Symptom

You are doing a system conversion to SAP S/4HANA FPS1, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

With SAP S/4HANA, on-premise edition 1709 FPS1, the master data of Commodity Curves have been sinplified. As part of the ovall simplification of the data model in Commodity Management, the Commodity ID has been deprecated. Based on this simplification, also the definition and the access to Commodity Curves is simplified and the only supported commodity Curve Category is '2 Based on DCS'. Commodity Curves are now defined and accessed using the DCS ID, MIC (optional) and Commodity Curve Type.

For the usage of Commodity Curves within the Commodity Pricing Engine, it is no loger required to activate The Business Functions of Commodity Management for Treasury (FIN_TRM_COMM_RM).

Note 2553281 describes the process regarding the depracation of the Commodity ID in Commodity Management. Details regarding the simplified Commodity Curves can be found in chapter 'Conversion of Commodity Curves'.
