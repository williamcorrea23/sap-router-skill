---
item_id: SI-5.11
title: "5.11 S4TWL - Hedge Management for logistics transactions"
pages: 199-200
sap_notes: [2556106]
components: [LO-CMM-ANL, FIN-FSCM-TRM-CRM, LO-CMM-BF]
objects: []
---
Application Components:LO-CMM-ANL, FIN-FSCM-TRM-CRM, LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                        |
|-----------------|---------------|---------------------------------------------------------|
| Business Impact |       2556106 | S4TWL - CM: Hedge Management for Logistics Transactions |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709, the raw exposure interface for logistics transactions has been deprecated.

## Business Process related information

In the Business Suite, raw exposures were created from logistics documents based on the commodity pricing information.

For these raw exposures, risk hedges could be managed.

## Required and Recommended Action(s)

Check, whether you used raw exposure information for Hedge Accounting for Exposures .

In S4H 1709 FPS01, Commodity Position Reporting is provided without raw exposures.

Based on reported positions of logistics transactions, the corresponding risk hedges must be triggered manually.

## Other Terms

Hedge Accounting for Exposures, HACC
