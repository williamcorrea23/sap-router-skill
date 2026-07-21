---
item_id: SI-3.4
title: "3.4 S4TWL - Product catalog"
pages: 129-131
sap_notes: [2267292, 2269324, 2371157]
components: [LO-MD-PC]
objects: []
---
## Application Components:LO-MD-PC

Related Notes:

| Note Type       |   Note Number | Note Description        |
|-----------------|---------------|-------------------------|
| Business Impact |       2267292 | S4TWL - Product Catalog |

## Symptom

You are doing a system conversion to SAP S/4HANA. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

Product Catalog functionality was used in the past as means of integration to webchannel solutions.

SAP Commerce Cloud is the strategic solution to support web-channel processes, with the respective backend Integration. Thus, Product Catalog functionality is not part of the target architecture.

## Business Process related information

SAP Commerce Cloud is the strategic solution to support web-channel processes, with the respective backend Integration. Thus, integration via Product Catalog is not part of the target architecture in SAP S/4HANA.

If the Product Catalog was used for other integration scenarios as the one mentioned above, a switch to alternatives availabe in S/4HANA is required.

## Required and Recommended Action(s)

There are other communication scenarios in SAP S/4HANA to send article and price information.

The alternatives include e.g.:

Article data (i.e. if retail Business Functions are active) combined with prices DRF SOAP Service ProductMerchandiseViewReplication (available with SAP S/4HANA 1909)

Assortment List IDoc WBBDLD

WES SOAP Service ReplicateMerchandiseDemandManagement: however, this is part of Compatibility Pack, see note 2371157 and 2269324.

Article data (i.e. if retail Business Functions are active)

DRF SOAP Service ProductMDMBulkReplicate  (available with SAP S/4HANA 2020)

ARTMAS IDoc

Material data (i.e. if retail Business Functions are not active)

DRF SOAP Service ProductMDMBulkReplicate  (available with SAP S/4HANA 2020)

MATMAS IDoc

Prices (independent of retail Business Functions)

DRF SOAP Service SalesPricingConditionRecord (available with SAP S/4HANA 1909)

## COND_A IDoc

| Transaction not available in SAP S/4HANA.   | WCU1 Maintain customer WCUM Maintain customer WPC1 Prepare product catalog IDocs WPC2 Prepare item IDocs WPC3 Prepare catalog change IDocs WPC4 Prepare item change IDocs WPC5 Convert product catalog WPCC Prepare prod. catalog change IDocs WPCI Prepare product catalog IDocs WPCJ Prepare product catalog IDocs WW10 IAC product catalog WW20 IAC Online Store WW30 SD part for IAC MM-SD link WWCD Product catalog:Display change docs. WWM1 Create product catalog WWM2 Change product catalog WWM3 Display product catalog WWM4 Copy product catalog WWM5 Delete product catalog   |
|---------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

Till SAP S/4HANA 1909 FPS0, transactions WWM1, WWM2, WWM3, WWM4, WWM5 can be executed. That is an error. In the blocklist (table ABLM_BLACKLIST) these transactions are only excluded for Cloud. They should be excluded for usage on-premise as weel. This will be corrected in a future release.

## Required and Recommended Action(s)

Switch to strategic solution.

In case you reuse ABAP objects of packet WWMB or WWMI in your custom code, please see attached note.

## How to Determine Relevancy

This Simplification Item is relevant if Product Functionality is used. This is the case if any of the following transactions are used: WCU1, WCUM, WPC1, WPC2, WPC3, WPC4, WPC5, WPCC, WPCI, WPCJ, WW10, WW20, WW30, WWCD, WWM1, WWM2, WWM3, WWM4, WWM5.
