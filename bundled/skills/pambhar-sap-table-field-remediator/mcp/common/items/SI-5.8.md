---
item_id: SI-5.8
title: "5.8 S4TWL - Simplification in Position Reporting for Financial Transactions"
pages: 195-197
sap_notes: [2556089]
components: [LO-CMM-BF]
objects: []
---
Application Components:LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                        |
|-----------------|---------------|-------------------------------------------------------------------------|
| Business Impact |       2556089 | S4TWL - Simplification in Position Reporting for Financial Transactions |

Symptom You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case

## Solution

## Description

With SAP S/4HANA the Commodity Risk Management provides Position Reporting for the Financial Transaction Management. All analytical data is persisted based on versioned data records and exposed through Core Data Servcies (DCS) to the analytical tools like SAP Analysis for Microsoft Excel .

## Business Process related information

In the Business Suite the Financial Transaction data that is relevant for the analytical source data for position reporting was stored in the versioned data base table for commodity exposures (TEXT_CTY_EXPOS) . This data base table was also used for logistical data via the Logistics to Treasury Management interface (LOG2TRM). The update happened via a background process.

In S4 1709 FPS01 there is a new data flow to support analytical reporting. The Financial Transaction data is updated automatically from all relevant Financial Transaction business processes into a new data base table (CMM_VFIND)  in real time. In case of an error it is possible to monitor messages in the application log and to re-process.

S4 1709 FPS01 the analytical reporting keyfigures are provided in one single technology that provides a reporting CDS stack in order to allow commodity position snapshot reporting across commodities.

## Functional Restrictions

In S4 1709 FPS01 the Position Reporting for Financial Transactions does not support option delta factors.

## Required and Recommended Action(s)

As described in the attached 'Function in Details - Simplification in Postion Reporting for Financial Transactions'  a couple of steps need to be considered:

historical position data can not be migrated to the new S/4HANA analytical data model. The data should be exported BEFORE the S4 upgrade to keep it accessible from an XLS or BW InfoCube

Financial Transaction data can be loaded initially into the database table which is used in S4 1709 FPS1 onwards for position reporting if BEX Queries on top of Operational Data Providers are used in the Business Suite, these BEX Queries need to be converted into CDS Queries in S4 on top of the new CDS InterfaceViews if CDS Queries have been used for Position Reporting in the Suite, these need to be converted into CDS Queries in S4 on top of the new CDS InterfaceViews

## Other Terms

Commodity Risk Management, Commodity Exposure Positions
