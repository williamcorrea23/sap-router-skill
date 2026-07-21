---
item_id: SI-3.7
title: "3.7 S4TWL: Business partner data exchange between SAP CRM and S/4HANA"
pages: 135-138
sap_notes: [1968132, 2070408, 2231667, 2265093, 2283695, 2283810, 2285062, 2286880, 2289876, 2304337]
components: [S4CORE, CRM-MD-BP-IF]
objects: []
---
Application Components:S4CORE, CRM-MD-BP-IF

Related Notes:

| Note Type       |   Note Number | Note Description                                                                      |
|-----------------|---------------|---------------------------------------------------------------------------------------|
| Business Impact |       2285062 | S4TWL: Business partner data exchange between SAPCRM and S/4 HANA, on-premise edition |

## Symptom

This SAP Note is relevant for you if the following applies:

You are using an SAP ERP release and support package that is lower than the following releases and support packages:

SAP enhancement package 6 for SAP ERP 6.0

SAP enhancement package 7 (SP11) for SAP ERP 6.0

SAP enhancement package 8 (SP01) for SAP ERP 6.0

You are using a live integration of SAP CRM and SAP ERP.

You are planning to convert from SAP ERP to SAP S/4HANA, on-premise edition.

You are planning to activate the customer vendor integration (CVI) in SAP ERP and start a mass synchronization based on the customer master or vendor master (Customizing activity Synchronization of Mass Data ) to generate business partners.

## Introduction

In SAP S/4HANA, on-premise edition, the central business partner approach is mandatory. The master data is processed using the SAP Business Partner in combination with an activated CVI, and the customer or vendor master is updated automatically in the background. For more information, see the simplification item Business Partner Approach (SAP Note 2265093).

If you have not worked with the CVI beforehand, you need to activate it and generate business partners before converting your system to SAP S/4HANA, on-premise edition.

In addition, you have to make settings to set up the business partner data exchange between SAP S/4HANA, on-premise edition and SAP CRM.

## Business Process Information

There is no effect on business processes if the settings are performed as described in this SAP Note.

## Required and Recommended Actions

Note that you must perform the pre-conversion actions described in this SAP Note before activating the CVI and starting mass synchronization.

## Reason and Prerequisites

System landscape with CRM and S/4 HANA is planned or available

## Solution

## 1. Required Actions in SAP ERP

A Business Add-In (BadI) implementation has been provided to ensure that the mass synchronization does not generate new GUIDs instead of using the existing GUIDs from the CRM mapping tables. The BAdI is contained in SAP Note 2283695.

It is imperative that SAP Note 2283695 is implemented before the Customer Vendor Integration (CVI) is activated and the mass synchronization of customer master or customer vendor data for the generation of business partners is started. If you start the synchronization before SAP Note 2283695 has been implemented, the mapping between business partners that is used in an integration scenario with SAP CRM is irretrievably lost.

A check report has been provided to examine whether the BAdI implementation is available in your system. In addition, a check report is available that identifies any existing inconsistencies (if you have been using an active CVI already) or any inconsistencies that appear after mass synchronization. For more information about the check reports, see SAP Note 2304337.

## 2. Required actions in SAP S/4HANA, on-premise edition

Settings for integration of SAP CRM with SAP S/4HANA, on premise-edition 1511 Feature Package Stack 01

If you want to integrate your SAP CRM system with SAP S/4HANA, on premise-edition 1511 FPS 01, several limitations apply to the exchange of business partner data. For more information, see SAP Note 2231667. Most of the limitations are resolved with SAP S/4HANA, on premise-edition 1511 FPS 02.

In the integration scenario with SAP S/4HANA, on premise-edition 1511 FPS 01, you must make the settings described in SAP Notes 1968132 and 2070408.

Settings for integration of SAP CRM with SAP S/4HANA, on premise-edition 1511 FPS 02, or a higher FPS

You need to adjust the settings in transaction COM_BUPA_CALL_FU according to SAP Note 2283810.

Download Objects and Filters

(Note that the download objects named in the following paragraph are located in S/4HANA, on-premise edition, and the transactions are located in SAP CRM.)

We recommend to use the download objects BUPA_MAIN and BUPA_REL for initial loads and request. Due to the fact that in SAP S/4HANA, on-premise solution, the SAP Business Partner is the main master data object for processing customer and vendor master data, the download objects BUPA_MAIN and BUPA_REL now also support all general, customer-specific, and vendor-specific data.

Download object VENDOR_MAIN is not available. The download objects CUSTOMER_MAIN and CUSTOMER_REL continue to be available for initial loads (transaction R3AS) and requests (transactions R3AR2 and R3AR4). We recommend that you only use these download objects for specifying filters that are specific to the customer master, like sales area details, account IDs, and partner functions.

In addition, filter conditions maintained in transaction R3AC1 for CUSTOMER_MAIN and CUSTOMER_REL continue to be considered when downloading business partners and their related customers from SAP S/4HANA, on-premise edition, to SAP CRM.

## 3. Miscellaneous required actions

See SAP Note 2286880 for handling error messages regarding SEPA and partner functions in SAP CRM. No manual actions are required after implementing the SAP Note.

If you have implemented the user exits DE_BALE or DE_AALE in SAP ERP, see SAP Note 2289876.

For further information about business partner synchronization, see SAP Note 2265093.

## Other Terms

CUSTOMER_MAIN, CUSTOMER_REL

BUPA_MAIN, BUPA_REL

VENDOR_MAIN

R3AR2, R3AR4, R3AS, R3AC1

COM_BUPA_CALL_FU
