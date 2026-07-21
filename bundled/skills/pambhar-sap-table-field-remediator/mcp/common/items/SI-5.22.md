---
item_id: SI-5.22
title: "5.22 S4TWL - Mark-to-Market & Profit-and-Loss Reporting for Derivatives"
pages: 213-214
sap_notes: [2596369]
components: [FIN-FSCM-TRM-CRM]
objects: []
---
## Application Components:FIN-FSCM-TRM-CRM

Related Notes:

| Note Type       |   Note Number | Note Description                                                    |
|-----------------|---------------|---------------------------------------------------------------------|
| Business Impact |       2596369 | S4TWL - Mark-to-Market & Profit-and- Loss Reporting for Derivatives |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA the Commodity Risk Management provides Markt-to-Market and Profit-and-Loss Reporting for the Financial Transaction Management. All analytical data and analytical results are persisted based on versioned data records and exposed through Core Data Servcies (DCS) to the analytical tools like SAP Analysis for Microsoft Excel .

## Business Process related information

In the Business Suite the Financial Transaction data that is relevant for the analytical source data for Markt-to-Market and Profit-and-Loss reporting was stored in Market Risk Analyzer (MRA) data base tables. The analytical results were provided in the framework of the MRA functionality 'Determination of Single Records' and stored in the Result Data Base.

In S/4HANA 1709 FPS02 there is a new data flow to support analytical reporting. The Financial Transaction data is updated automatically from all relevant Financial Transaction business processes into new data base tables. In case of an error it is possible to monitor messages in the application log and to re-process.

In S/4HANA 1709 FPS02 the analytical reporting key figures are provided in one single technology that provides a reporting CDS stack in order to allow Mark-to-Market and Profit-and-Loss snapshot reporting across commodities.

## Functional Restrictions

In S/4HANA 1709 FPS02 the Position, Markt-to-Market and Profit-and-Loss Reporting for Financial Transactions does not support option delta factors.

## Required and Recommended Action(s)

For the Simplification in Markt-to-Market and Profit-and-Loss Reporting for Financial Transactions a couple of steps need to be considered:

historical position data can not be migrated to the new S/4HANA analytical data model. The data should be exported BEFORE the S/4HANA upgrade to keep it accessible from an XLS or BW InfoCube

Financial Transaction data can be loaded initially into the database tables which is used in S/4HANA 1709 FPS2 onwards for Markt-to-Market and Profit-and-Loss reporting

if BEX Queries on top of Operational Data Providers are used in the Business Suite, these BEX Queries need to be converted into CDS Queries in S/4HANA on top of the new CDS InterfaceViews

if CDS Queries have been used for Markt-to-Market and Profit-and-Loss Reporting in the Suite, these need to be converted into CDS Queries in S/4HANA on top of the new CDS InterfaceViews

## Other Terms

Commodity Risk Management, Commodity Mark-to-Market Reporting for Derivatives, Commodity Profit -and -Loss Reporting for Derivatives
