---
item_id: SI-5.12
title: "5.12 S4TWL - Position Reports delivered by Agricultural Contract Management"
pages: 200-202
sap_notes: [2556134]
components: [LO-CMM-BF, LO-CMM-ANL]
objects: []
---
Application Components:LO-CMM-BF, LO-CMM-ANL

Related Notes:

| Note Type       |   Note Number | Note Description                                     |
|-----------------|---------------|------------------------------------------------------|
| Business Impact |       2556134 | S4TWL - CM: Agri-Specific Commodity Position Queries |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA transition worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709, the database table and available infosources for risk data required for position reporting got unified and revised.

New Core Data Services (CDS) views are provided to determine keyfigures for position reporting.

For keyfigures, which are specific for Futures/Basis pricing - as common in the Agricultural industry - CDS (interface) views are available.

However, queries on top of these are not provided with the software layer of Commodity Management.

Instead, these are provided in the Agicultural Contract Managament (ACM) software layer.

## Business Process related information

Agri-specific Queries include

Futures Risk / Slate report with a keyfigure layout tailored to Future / Basis pricing

Basis / Premium report

Price Type report

## Required and Recommended Action(s)

If you require Agri-specific queries, check the availability of Agicultural Contract Managament (ACM) in your system.

If ACM is not available you may need to create queries on top of the available (Commodity Management) interface views during system implementation.

## Other Terms

ACM, agricultural industry, commodity position reporting, CDS views
