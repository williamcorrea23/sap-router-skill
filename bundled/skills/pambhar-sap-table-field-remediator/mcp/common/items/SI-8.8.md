---
item_id: SI-8.8
title: "8.8 S4TWL -  Cost of Sales Ledger"
pages: 263-265
sap_notes: [2269324, 2680760, 3006586]
components: [FI-SL]
objects: []
---
Application Components:FI-SL

Related Notes:

| Note Type       |   Note Number | Note Description             |
|-----------------|---------------|------------------------------|
| Business Impact |       3006586 | S4TWL - Cost of Sales Ledger |

## Symptom

You are doing a system conversion from SAP ERP to SAP S/4HANA or an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

The usage of the cost of sales ledger is part of the SAP S/4HANA compatibility scope, which comes with limited usage rights. For more details on the compatibility scope and it's expiry date and links to further information please refer to SAP note 2269324. In the compatibility matrix attached to SAP note 2269324, cost of sales ledger can be found under the ID 430.

This means that you need to migrate from cost of sales ledger to its designated alternative functionality cost of sales accounting (CSA) reporting in SAP S/4HANA based on the Universal Journal before expiry of the compatibility pack license.

Also refer to the SAP S/4HANA Feature Scope Description section Cost of Sales Ledger.

## Business Process related information

The cost of sales ledger is used to provide a type of profit and loss statement that matches sales revenues to the costs of the products sold. It is based on functional areas. In SAP ERP classic General Ledger Accounting, functional areas are always managed and reported only in FI Special Ledger. Table GLFUNCT, ledger 0F, contains the totals records for cost of sales accounting.

In SAP S/4HANA the contents of the cost of sales ledger and all special ledgers created in table GLFUNCT are included in the Universal Journal (table ACDOCA).

## Required and Recommended Action(s)

To use CSA reporting in SAP S/4HANA based on the Universal Journal, you need to fulfill several prerequistes. Refer to SAP note 932272 for a detailed explanation. The main points to consider for SAP S/4HANA are as follows:

If you have used classic General Ledger Accounting or General Ledger Accounting (new) without CSA in SAP ERP, CSA reporting cannot be used in S/4 for the years in question because the system cannot derive functional areas properly. Thus, after a conversion to SAP S/4HANA, CSA reporting would initially still need to be done in the FI-SL ledger 0F.

Once the correct derivation of a functional area has been set-up and complete and correct account assignments in Accounting can be ensured, CSA reporting based on the Universal Journal can take place.

However, SAP recommends that you still use CSA reporting in FI-SL for a transition period of at least one year.

To enable the complete assignment of allocations and postings from CO in SAP S/4HANA, refer to SAP Note 2680760.

## Other Terms

SAP S/4HANA, Compatibility Scope, Compatibility Package, System Conversion, Upgrade, Special Ledger, ID 430
