---
item_id: SI-5.19
title: "5.19 S4TWL - Simplified Data Model/Master Data"
pages: 209-210
sap_notes: [2553281, 2554440, 2556176]
components: [LO-CMM-BF]
objects: []
---
Application Components:LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                 |
|-----------------|---------------|------------------------------------------------------------------|
| Business Impact |       2554440 | S4TWL - Simplified Commodity Management Data Model / Master Data |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

The master data model for the commodity master data in S/4HANA has been simplified and allows a single definition of the commodity as an attribute of the Derivative Contract Specification (DCS).  This allows  a standardized access to the DCS-based market data for derivative transactions and processes, and for logistics transactions.

The determination of market data by quotation name, quotation type and quotation source is deprecated in S/4HANA (see reference note).

## Solution

## Description

With SAP S/4HANA on-premise edition 1709 FPS1 the data model of Commodity Management master data has been simplified. The commodity as a system entity to represent traded material is defined as attribute of derivative contact specifications (DCS).  To make the deprecation of commodity master data possible, the definition of market data and the market data access were adjusted accordingly. For the assignment of the DCS and market identifier code (MIC) to financial transaction data, in order to replace the Commodity ID, all financial transactions and processes were adjusted.

## Business Process related information

The following functional areas are adjusted:

Financial Transaction Management

BAPIs for Financial Transactions

FUT and LOPT  - Class Data

BAPIs for Class Data

Commodity Price Adjustments

Mass Cash Settlement

MRA Basic Functions and Reports: Analysis Parameters, JBRX, TPM60,  AISGENKF

## Functional Restrictions

see business impact note 2556176

## Required and Recommended Action(s)

For customer specific coding and configuration please refer to the Custom Code Impact Note. Manual conversion steps are needed. Please refer to the details that are described in the SAP Note 2553281 - Cookbook Deprecation of Commodity ID in Commodity Risk Management.

## Other Terms

Commodity Risk Management, Commodity ID, Commodity Master Data, FCZZ, Financial Transactions, Real Commodity, Abstract Commodity, Physical Commodity, Derivative Contract Specification, DCS
