---
item_id: SI-5.27
title: "5.27 S4TWL - Data Model Change in the Commodity Condition Types Mapping"
pages: 222-223
sap_notes: [3203820]
components: [CA-GTF-CPE]
objects: []
---
## Application Components:CA-GTF-CPE

Related Notes:

| Note Type       |   Note Number | Note Description                                                   |
|-----------------|---------------|--------------------------------------------------------------------|
| Business Impact |       3203820 | S4TWL - Data Model Change in the Commodity Condition Types Mapping |

## Symptom

You are using an SAP S/4HANA On Premise system, Commodity Management solution. When using Commodity pricing Engine in the area of central procurement(Central Purchase Contract and Sourcing Projects) the customizing activity "Map Purchase Condition types to commodities" has been maintained.

The custom code check shows those customer objects that are affected by simplifications.

SAP objects used by the customer objects have been changed in a way that the would give inconsistent results.

## Reason and Prerequisites

There is a data model change in the Commodity Condition Types Mapping. An Additional Key is added to the data base table CMM_CMDTY_CND. This additional key enables the mapping to be maintained for Sales Conditions. Previously the table was restricted to store only Purchase Conditions.

## Solution

Where ever the table CMM_CMDTY_CND is used in Customer Code to fetch data, the new additional key field must be included in the the code so as to maintian the consistency in the data fetch.

If CDS View I_CommodityConditionMapping is used then this should be replaced with the CDS View I_PurCommodityConditionMapping for Purchase and I_SlsCommodityConditionMapping for Sales.

## Other Terms

Commodity, Condition Types, Mapping

## 6. Corporate Close
