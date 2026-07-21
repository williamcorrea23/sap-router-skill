---
item_id: SI-5.16
title: "5.16 S4TWL - Simplification of DCS based Market Data Handling for Fin Transactions"
pages: 205-206
sap_notes: [2553281, 2556164]
components: [FIN-FSCM-TRM-CRM, LO-CMM-BF]
objects: []
---
Application Components:FIN-FSCM-TRM-CRM, LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                   |
|-----------------|---------------|----------------------------------------------------------------------------------------------------|
| Business Impact |       2556164 | S4TWL - Simplification of DCS-Based Market Data Mngmt for Financial Transactions: DCS ID Extension |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case

## Reason and Prerequisites

The DCS ID with data type 6 chars used to be a restriction for customers and did not allow to enter a meaningful description, and to support longer market data codes from market data providers for commodity prices based on commodity forward indexes.

## Solution

With SAP S/4HANA, on-premise edition 1709 FPS1, the Derivative Contract Specification Identifier (DCSID) as defined in the system configuration has been extended by using a DCSID data type with 20 CHAR. With this data type you can describe the entity in more detail such as, for example, with reference to the material, the exchange and the location.

## Business Process-Related Information

The market data interface is adjusted to support the new DCSID data type.

The access to market data and commodity curves is now based on the longer DCSID. The Financial Transaction Management and the related processes are adjusted accordingly.

## Required and Recommended Action(s)

Actions are only nessecary for customer-specific coding. Manual conversion steps are need for the conversion of datafeed functionality. For more information, see SAP Note 2553281 - Cookbook Deprecation of Commodity ID in Commodity Management.

## Other Terms

Derivative Contract Specification (DCS), DCS ID, market data feed
