---
item_id: SI-5.10
title: "5.10 S4TWL - Position Reporting on versioned pricing data"
pages: 198-199
sap_notes: [2547347]
components: [LO-CMM-ANL, LO-CMM-BF]
objects: []
---
Application Components:LO-CMM-ANL, LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                   |
|-----------------|---------------|--------------------------------------------------------------------|
| Business Impact |       2547347 | S4TWL - CM: Commodity Position Reporting on Versioned Pricing Data |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709 the database table and available infosources for commodiy price risk data required for commodity position reporting got unified and revised.

## Business Process related information

The Business Suite's Commodity Position Reporting used raw expsoures created from logistics documents and transactions.

Based on the raw exposures, the commodity position table TEXT_CTY_EXPOS was updated for the Commodity Position Reporting. In S4H, the  data footprint and processing layers were reduced.

Key figures, which were formerly exposed in different technology stacks (ODP/BEx versus CDS views) are now provided in one single technology and reporting stack only to allow a unified reporting for different commodities and scenarios.

## Required and Recommended Action(s)

As described in the attached ' Function in Details - Position Reporting on Versioned Pricing Data ' word file, the following steps need to be performed:

Historical position data should be exported BEFORE the S4HANA upgrade to keep the data accessible from an XLS or BW InfoCube

Logistics transactions need to be loaded to the database table, which is used in S4H 1709 FPS1 onwards for the Commodity Position Reporting

If BEx queries on top of Operational Data Providers (ODP) are used in the Business Suite, these BEx queries must be converted to CDS queries in S4H on top of the new CDS interface views

If CDS queries have been used for the Commodity Position Reporting in the Business Suite, these queries need to be converted to CDS queries in S4H on top of the new CDS interface views

## Other Terms

ODP, BEx Query, CDS views
