---
item_id: SI-5.2
title: "5.2 S4TWL -  CM: Simplified CPE Activation"
pages: 191-191
sap_notes: [2461004]
components: [LO-CMM-BF, SD-BF-CPE, MM-PUR-GF-CPE]
objects: []
---
## Application Components:LO-CMM-BF, SD-BF-CPE, MM-PUR-GF-CPE

Related Notes:

| Note Type       |   Note Number | Note Description                          |
|-----------------|---------------|-------------------------------------------|
| Business Impact |       2461004 | S4TWL - CM: CPE Simplified CPE Activation |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709 the activation of the Commodity Pricing Engine (CPE), the flagging of Condition Types to be relevant for CPE and the required settings in the pricing procedure are simplified. This is especially relevant if you are using CPE together with IS-OIL.

## Business Process related information

The settings for the activation of the CPE have to be adjusted manually, if you are using CPE together with IS-OIL. If no IS-OIL is active, the conversion is done automatically during the update.

## Required and Recommended Action(s)

In the assigned document 'Function in Details - Simplified CPE Activation', the process how to adjust the relevant settings is described.
