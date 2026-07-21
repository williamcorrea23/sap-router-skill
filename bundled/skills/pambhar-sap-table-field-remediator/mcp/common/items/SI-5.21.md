---
item_id: SI-5.21
title: "5.21 S4TWL - Mark-to-Market & Profit-and-Loss Reporting for logistics transactions"
pages: 211-213
sap_notes: [2591598]
components: [LO-CMM-BF, LO-CMM-ANL]
objects: []
---
Application Components:LO-CMM-BF, LO-CMM-ANL

Related Notes:

| Note Type       |   Note Number | Note Description                                                         |
|-----------------|---------------|--------------------------------------------------------------------------|
| Business Impact |       2591598 | S4TWL - CM: Mark-to-Market & Profit- and-Loss for logistics transactions |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

Solution

Description With SAP S/4HANA, on-premise edition 1709, the database table used for Mark-toMarket Reporting got unified.

Instead of three database tables storing valuation results for Purchasing, Sales and Trading Contracts, only one table is supported storing versioned pricing source data.

## Business Process related information

The Business Suite's Mark-to-Market Reporting stored valuation results in the tables CMM_MTM_PO, CMM_MTM_SO and WB2B_CMM_MTM_TC.

However, this did not facilitate snapshot-based reporting (such as the End-of-Day Snapshot Mark-To-Market reporting) since the market data may not be present in the system at the time when these snapshots need to be valued.

For this purpose, to store versioned source data, table CMM_VLOGP had been introduced with SAP ERP 6.0 Enhancement Package 8.

Based on table CMM_VLOGP, the valuation with market data is performed at reporting time.

In S4H only, table CMM_VLOGP is supported as basis for the Mark-to-Market reporting on logistics transactions.

## Required and Recommended Action(s)

As described in the attached document ' Function in Details - Mark-to-Market and Profitand-Loss for Logistics Transactions ', the following steps need to be performed:

If using discounting, you need to make use of forward FX rates instead to convert between currencies towards a statistics currency.

If using aggregation, you need to define reporting groups in the Customizing for Commodity Risk Management and aggregate at these groups at reporting time.

If BEx queries on top of Operational Data Providers (ODP) are used in SAP ERP, these BEx queries must be converted to CDS queries in S4H on top of the provided CDS interface views.

## Other Terms

CMM_VLOGP CMM_MTM_PO CMM_MTM_SO WB2B_CMM_MTM_TC
