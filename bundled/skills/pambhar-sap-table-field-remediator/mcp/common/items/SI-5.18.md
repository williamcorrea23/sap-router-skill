---
item_id: SI-5.18
title: "5.18 S4TWL - Deprecation of functions using Non DCS based Market Data"
pages: 208-209
sap_notes: [2556176]
components: [LO-CMM-BF, FIN-FSCM-TRM-CRM]
objects: []
---
## Application Components:LO-CMM-BF, FIN-FSCM-TRM-CRM

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                                                             |
|-----------------|---------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Business Impact |       2556176 | S4TWL - Deprecation of Non-DCS- Based Market Data for Financial Transactions 2: VaR, Market Data Shifts and Scenarios, Statistics Calculator |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case

## Solution

## Business Process-Related Information

In the Business Suite (ERP), the market data that was not related to derivative contracts specification (DCS) and was based on quotation name, quotation type, quotation source could be used for

volatilities with moneyness for OTC commodity options

the definition of shifts and scenarios

the statistics calculator for volatilities and correlations

calculation of value at risk results

creation of generic transactions for market risk analyzer analytics

Hedge Accounting for commodity price risks and exposures from financial and logistics transactions

## Required and Recommended Action(s)

These functions are not avaliable in S/4HANA 1709. It is planned to support these functions in a future release of Commodity Management.

## Other Terms

Commodity Risk Management, Value at Risk, Market Data Shift, Market Data Scenario, Market Risk Analyzer (MRA) MRA simulation, Statistics Calculator for Volatilities, Correlations
