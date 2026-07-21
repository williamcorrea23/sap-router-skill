---
item_id: SI-5.9
title: "5.9 S4TWL - Simplified Data Flow of logistics data for Risk Reporting Database"
pages: 197-198
sap_notes: [2547343]
components: [LO-CMM-BF, LO-CMM-ANL]
objects: []
---
Application Components:LO-CMM-BF, LO-CMM-ANL

Related Notes:

| Note Type       |   Note Number | Note Description                                                                    |
|-----------------|---------------|-------------------------------------------------------------------------------------|
| Business Impact |       2547343 | S4TWL - CM: Simplified Data Flow of Logistics Data for Commodity Position Reporting |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA transition worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709 the data flow and persistencies of commodity price risk data derived from logistics documents and transactions have been revised.

## Business Process related information

As described in the attached word file, a reduced number of background queues needs to be monitored for errors.

Error handling for commodity position data does not require the usage of transaction LITRMS anymore.

Instead, queues in error need to be monitored and re-started, after the errors were resolved.

## Required and Recommended Action(s)

In the attached document, you can find information on the revised handling of background processes and thus requirements on system monitoring.

## Other Terms

Error handling, Commodity Position Reporting
