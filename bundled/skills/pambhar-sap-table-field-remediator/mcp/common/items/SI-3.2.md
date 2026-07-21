---
item_id: SI-3.2
title: "3.2 S4TWL - SRM Product Master"
pages: 125-127
sap_notes: [2267297]
components: [AP-MD-PRO]
objects: []
---
Application Components:AP-MD-PRO

Related Notes:

| Note Type       |   Note Number | Note Description           |
|-----------------|---------------|----------------------------|
| Business Impact |       2267297 | S4TWL - SRM Product Master |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

The functional scope of SAP Supplier Relationship Management ( SAP SRM) will gradually be made available within SAP S/4HANA. The related functions will become part of the procurement solution of SAP S/4HANA. Technically, the procurement solution within SAP S/4HANA is not a successor to the SAP SRM components. Therefore, the SAP SRM software components and SAP S/4HANA cannot be installed on the same system.

For more details see Simplification Item Co-Deployment of SAP SRM .

Accordingly the SRM Product Master is not available in SAP S/4HANA, on-premise edition 1511.

## Business Process related information

There is no influence on the business processes, as the SRM product master was not used in ERP functionality.

| Transaction not available in SAP S/4HANA on-premise edition 1511   | COM_PR_MDCHECK COMC_MATERIALID_ALL COMC_PR_ALTID COMC_PR_ALTID_BSP COMC_PR_OBJ_FAM COMC_PR_OBJ_FAM1 COMC_PR_RFCDEST COMC_PRODUCT_IDX COMC_SERVICEID_ALL COMCMATERIALID COMCPRAUTHGROUP COMCPRD_BSP_ID COMCPRFORMAT COMCPRLOGSYS COMCPRMSG COMCPRTYPENRO COMCSERVICEID COMM_DEL_PRWB_USER COMM_EXTRSET COMM_HIERARCHY   |
|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| COMM_IOBJ_RECATEG COMM_MSG01 COMM_PRAPPLCAT COMM_PRDARC COMM_PROD_RECATEG COMMPR_PCUI COMMPR01 COMMPR02 CRM_PRODUCT_LOG CRM_PRODUCT_STA CRMCFSPRODID   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------|

## Required and Recommended Action(s)

In SAP S/4HANA the COMM* tables (COMM_PRODUCT, COMM_HIERARCHY ) are no longer available .It is recommended that users archive the ABAP Basis COMM* product master tables and proceed with the upgrade.

In a non-productive client, use reports COM_PRODUCT_DELETE_ALL to delete products and COM_HIERARCHY_DELETE_ALL to delete hierarchies.

For productive clients, set the deletion indicator using transaction COMMPR01 and archive the products using transaction SARA, then delete the hierarchies using COMM_HIERARCHY.

For SRM-OneClient deployment the users should be aware that the SRM product master data is not accessible after S/4 conversion.
