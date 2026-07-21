---
item_id: SI-3.19
title: "3.19 S4TWL - Business Partner Approach"
pages: 153-159
sap_notes: [1623677, 2265093, 2310884, 2472030]
components: [LO-MD-BP]
objects: []
---
## Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                  |
|-----------------|---------------|-----------------------------------|
| Business Impact |       2265093 | S4TWL - Business Partner Approach |

## Symptom

You are doing a system conversion to SAP S/4HANA, any of the listed on-premise editions -> 1511, 1610, 1709,1809, 1909, 2020, 2021, 2022. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Business Value

In SAP S/4HANA, Business Partner is the leading object and single entry point to maintain Business Partner, Customer and Supplier (formerly known as Vendor) master data. This is to ensure ease of maintenance of the above master data and to achieve harmonization between them. Compared to classical ERP transactions, maintenance of Customer and Supplier master data via Business Partner has multiple advantages. Some of them are as follows:

Business Partner allows maintenance of multiple addresses with corresponding address usages.

In classical transactions, one customer can only be associated to one account group. But in Business Partner, multiple roles can be associated to the same Business Partner.

Maximal data sharing and reuse of data which lead to an easier data consolidation.

General Data available for all different Business Partner roles, specific data is stored for each role.

Maintenance of multiple relationships to the same Business Partner.

Maintenance of Time Dependency at different sub-entities roles, address, relationship, bank data etc.

## Description

There are redundant object models in the traditional ERP system. Here the vendor master and customer master is used. The (mandatory) target approach in S/4HANA is the Business Partner approach.

Business Partner is now capable of centrally managing master data for business partners, customers, and vendors. With current development, BP is the single point of entry to create, edit, and display master data for business partners, customers, and vendors.

## Additional Remarks:

It is planned to check the introduction of the Customer/Vendor Integration in the prechecks and the technical Conversion procedure of SAP S/4HANA on-premise edition 1511, 1610, 1709, 1809, 1909 and 2020. A system where the customer/vendor integration is not in place will be declined for the transition.

The Business Partner Approach is not mandatory for the SAP Simple Finance, onpremise edition 1503 and 1605.

## Business Process related information

Only SAP Business Suite customer with C/V integration in place can move to SAP S/4HANA, on-premise(Conversion approach). It is recommended but not mandatory that BuPa ID and Customer-ID / Vendor ID are the same.

The user interface for SAP S/4HANA is transaction BP. There is no specific user interface for customer/vendor like known from SAP Business Suite (the specific transactions like XD01, XD02, XD03 or VD01, VD02, VD03/XK01, XK02, XK03 or MK01, MK02, MK03 etc. are not available in SAP S/4HANA on-premise)

| Transactions not available in SAP S/4HANA on-premise edition   | Transactions that get redirected to transaction BP: FD01,FD02,FD03, FK01,FK02,FK03,MAP1,MAP2,MAP3, MK01, MK02, MK03, V-03,V-04,V-05,V-06,V-07,V-08,V-09, V-11, VAP1, VAP2, VAP3, VD01, VD02,VD03, XD01, XD02, XD03, XK01, XK06, XK07, XK02, XK03   |
|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Transactions not available in SAP S/4HANA on-premise edition   | Transactions that are obsolete: FD06, FK06, MK06, MK12, MK18, MK19, VD06, XD06, V+22, V+23                                                                                                                                                         |
| Transactions not available in SAP S/4HANA on-premise edition   | V+21,                                                                                                                                                                                                                                              |

## Points to Note in SAP S/4HANA:

In addition, note the following points while using the following functionalities in SAP S/4HANA:

Consumer - While creating a consumer, ensure that you use the BP Grouping that is associated to the customer account group (Consumer) in TBD001 (Assignment of Account Group BP Grouping). Note that customer itself is a contact person, hence no further relationships can be maintained.

One-time Customer/Supplier - While creating a one-time customer or supplier, ensure that you use the BP Grouping that is associated to the customer/supplier account group (One time customer/supplier) in TBD001 and TBC001 (Assignment of Account Group BP Grouping).

The idocs DEBMS/CREMAS and cremas are not recommended for data integration between S/4HANA systems. In S/4HANA, BP is the leading object. Therefore, only customer or supplier integration should be avoided. In S/4HANA, Business Partner is the leading object. Therefore, customer or supplier only integration should be avoided. You can use Business Partner web services (SOAP) via API Business Hub for SAP S/4HANA integration. It is recommended to use IDocs only if the source system has Customer or Supplier (no Business Partner) master data.

Role Validity - In SAP S/4HANA, you can maintain the validity of roles. With this feature, the user can close the (prospect) role and move to another after the mentioned validity period. For example, a business partner with prospect role can set the role change to sold-to-party by specifying the validity and by closing the previous validity.

## Required and Recommended Action(s)

Before you begin the BP conversion from an SAP ERP system to an SAP S/4 HANA system, you have to answer the questions

Whether the Business Partner ID and Customer-ID /Vendor ID should be the same in the S/4 HANA System?

The keys for a smooth synchronization of the ERP customer/vendor into the S/4 system with the business partner as the leading object are beside Business Partner Know-How also consistent customer/vendor data and valid and consistent custom/vendor and Business Partner customizing entries. For this reason, the customer/vendor data has to be cleaned up before it can be converted into the S/4 Business Partner.

Prepare: Pre-Checks and clean-up customer/vendor data in the ERP System

Implement SAP S/4HANA Conversion Pre-Checks according to the SAP S/4HANA Conversion guide chapter Pre-Checks.

## Activate Business Function CA_BP_SOA.

In case that the Business Function CA_BP_SOA not yet in the system exist, you have to create a new Business Function in the customer namespace with the switches VENDOR_SFWS_SC1 and VENDOR_SFWS_SC2. The new customer specific Business Function must be of type Enterprise Business Function (G) - see also Mandatory checks for customer, vendor and contact.

Check CVI customizing and trigger necessary changes  e.g. missing BP Role Category, Define Number Assignments according to the S/4 Conversion guide chapter Introduce Business Partner Approach (Customer Vendor Integration).

Check and maintain BP customizing e.g. missing tax types.

Check master data consistency using CVI_MIGRATION_PRECHK and maintain consistency.

Check and clean-up customer/vendor data e.g. missing @-sign in the e-mail address.

## Synchronization

Synchronization (Data load) is done via Synchronization Cockpit according to the attached BP Conversion Document.pdf > Chapter 5. Convert Customer/Supplier Data into Business Partner .

In case of an error during the synchronization process due to data/customizing mismatch you can find the errors using Logs button. You can also view this via MDS_LOAD_COCKPIT> Monitor tab > Call PPO button in Synchronization Cockpit.

## Conversion Process

Conversion Process must be triggered according to the BP Conversion Document.pdf attached to this SAP Note.

## Business Partner Post Processing

The customer/vendor transformation is bidirectional. You can both process customer/vendor master records from business partner maintenance as well as populate data from customer/vendor processing to the business partner. After the successful S/4 conversion process you have to activate the post processing for direction Business Partner a Customer /Vendor.

## Related SAP Notes & Additional Information

| Other SAP Notes   | SAP Note: 1623677, 954816                                                                                                                                                                                                                                                                          |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SAP Help          | Refer to the attachments (in SAP Note 2265093): BP_Conversion Document.pdf: Description of Busines Partner Approach and conversion activities 01_TOP-Item_MD_Business-Partner-Approach_Version1.0.pdf: Presentation on Business Partner Approach and Customer Vendor Integration during Conversion |

## Custom Code Adaption

If you are writing a direct write statement or a custom code on the tables mentioned in piece list SI_MD_BP, Please follow the below mentioned steps instead.

Reason and Prerequisites:

You want to create BP/Customer/Supplier with direct write statements or a particular piece of custom code.

You need an API to create Business Partner with Customer and Supplier roles.

The following are possible use-cases:

Requirement to create business partners in the same system: You can use API CL_MD_BP_MAINTAIN. Pass the data in CVIS_EI_EXTERN structure format and pass it to the method VALIDATE_SINGLE. This method validates all the data that is passed; after that, you can use the method MAINTAIN to create business partners.

Integration of data with various landscapes: If you want to integrate BP/Customer/Supplier master data across different systems, you can use following interfaces:

## a. IDOCs

There are two types of IDocs available that can be used:

DEBMAS: If you want to integrate customer (without BP) data between two systems, this IDOC can be used.

CREMAS: If you want to integrate supplier (without BP) data between two systems, this IDOC can be used.

b. SOA Services If the system has data of Business Partners, use SOA services for integration. Business Partner SOAP services enable you to replicate data between two systems. There are both inbound and outbound services available. Refer to SAP Note 2472030 for more information.

However, the IDocs DEBMAS and CREMAS are not recommended for data integration between S/4HANA systems. In S/4HANA, Business Partner is the leading object. Therefore, you can use Business Partner web services (SOAP) for SAP S/4HANA integration.

## Industry Specific Actions

IS-OIL Specific Actions:

In S4HANA all the IS-OIL specific fields (including customer BDRP data fields) have been adapted as per the new Framework of BP.

The IS-OIL Fields related to Vendor and Customer now have been moved to BP under the roles FLCU01 (Customer), FLVN01 (Vendor).

## Retail Sites Specific Action:

Customers and vendors assigned to Retail sites are not handled by CVI synchronization (MDS_LOAD_COCKPIT) on SAP ERP as described in this note, but by a specific migration process during SAP S/4HANA conversion. See SAP Note 2310884 for more information.
