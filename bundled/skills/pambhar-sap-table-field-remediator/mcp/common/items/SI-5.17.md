---
item_id: SI-5.17
title: "5.17 S4TWL - Deprecation of Non DCS based Market Data for Financial Transactions"
pages: 206-208
sap_notes: [2553281, 2556220]
components: [FIN-FSCM-TRM-CRM, LO-CMM-BF]
objects: []
---
Application Components:FIN-FSCM-TRM-CRM, LO-CMM-BF

Related Notes:

| Note Type       |   Note Number | Note Description                                                                      |
|-----------------|---------------|---------------------------------------------------------------------------------------|
| Business Impact |       2556220 | S4TWL - Simplification of DCS-Based Market Data Management for Financial Transactions |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case

## Reason and Prerequisites

Check in your business suite (ERP) implementation, whether and which market data are based on DCS

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709, the commodity market data is based only on definitions of derivative constract specifications (DCS). The following derivative categories are supported for using the DCS:

Commodity Future

Listed Option

Commodity Forward Index

Financial transaction pricing data uses DCS-based market data only.

## Business Process-Related Information

To support the DCS-based market data including DCS-based commodity curves, the Financial Transaction Management and its commodity-specific processes like price adjustments for unpriced commodity derivatives were adjusted accordingly.

## Required and Recommended Action(s)

Check your Business Suite (SAP ERP) implementation, whether you used market data based on quotation source, quotation type, quotation name.

The market data must be converted to support DCS-based market data.

The financial transactions pricing data based on the previous market data concept can be converted according to the cookbook (see SAP note 2553281 - Cookbook Deprecation of Commodity ID in Commodity Risk Management).

## Other Terms

Commodity Risk Management, Derivative Contract Specification/DCS, Market Identifier Code/MIC, commodity
