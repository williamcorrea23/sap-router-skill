---
item_id: SI-5.14
title: "5.14 S4TWL - Unification of supported technologies in analytical data provisioning"
pages: 203-204
sap_notes: [2555990]
components: [LO-CMM-ANL, FIN-FSCM-TRM-CRM, LO-CMM-BF Related Notes:]
objects: []
---
Application Components:LO-CMM-ANL, FIN-FSCM-TRM-CRM, LO-CMM-BF Related Notes:

| Note Type       |   Note Number | Note Description                                                      |
|-----------------|---------------|-----------------------------------------------------------------------|
| Business Impact |       2555990 | S4TWL - CM: Unification of Technologies for Analytical Data Provision |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA transition worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709 the technologies by which analytical data is provided got unified:

Operational Data Providers (ODP), BW Extractors and BEX Queries on top of these providing Position Reporting and Mark-to-Market are deprecated

HANA Live calculation views are not supported for Commodity Position Reporting and Mark-to-Market valuation/reporting.

Instead, all analytical data is exposed through Core Data Services (CDS) views.

## Business Process related information

In the Business Suite's Commodity Position Reporting, different sources of analytical information were available in different technologies:

Some data were reported based on Operational Data Providers (ODPs), some data based on CDS views, some information was exposed through HANA Live calculation views.

In S4HANA, all analytical data for commodities is exposed through CDS views reducing the TCO by using a unified technology.

## Required and Recommended Action(s)

Check, whether the required analytical data is provided by CDS views with S4H 1709 FPS01.

Note, that some analytical information for commodities formerly provided in the Business Suite may not be supported yet. These restrictions are documented in other simplification items.

You may need to convert your queries to enable the consumption by the new CDS views available in S4H.

## Other Terms

ODP, BEx Query, CDS view, Commodity Position Reporting, Commodity Position Overview, MtM
