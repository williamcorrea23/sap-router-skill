---
item_id: SI-5.15
title: "5.15 S4TWL - Risk Determination on a schedule line level"
pages: 204-205
sap_notes: [2556063]
components: [LO-CMM-ANL, LO-CMM-BF]
objects: []
---
Application Components:LO-CMM-ANL, LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                   |
|-----------------|---------------|--------------------------------------------------------------------|
| Business Impact |       2556063 | S4TWL - CM: Commodity Price Risk Determination from Schedule Lines |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709, the commodity risk determination for commodity price risks got simplified.

## Business Process related information

In the Business Suite it was possible to activate the commodity price risk determination based on schedule lines of a purchase order or sales order.

For this purpose a price simulation was called in the background for each schedule line with the schedule line date as reference date and pertaining quantity.

This is not supported in S4HANA.

## Required and Recommended Action(s)

If you require to split and distribute commodity price risk information, you need to split it on the item level accordingly.

## Other Terms

Schedule Line Item, Purchase Order, Sales Order, Delivery Schedule
