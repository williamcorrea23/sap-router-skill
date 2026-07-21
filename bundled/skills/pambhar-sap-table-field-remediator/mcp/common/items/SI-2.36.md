---
item_id: SI-2.36
title: "2.36 S4TWL - Simplified data model in Joint Venture Accounting"
pages: 92-94
sap_notes: [2941622, 2967210, 2993369, 3044558]
components: [CA-JVA]
objects: []
---
Application Components:CA-JVA

Related Notes:

| Note Type       |   Note Number | Note Description                           |
|-----------------|---------------|--------------------------------------------|
| Business Impact |       2967210 | S4TWL - Joint Venture Accounting on ACDOCA |

## Symptom

You are planning to do a system conversion to SAP S/4HANA with Joint Venture Accounting. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

Renovation

Solution

Business Value As of OP1909, JVA customers can optionally run the Joint Venture Accounting on a new data model that is based on the ACDOCA table ("JVA on ACDOCA"). The new data model has several advantages compared with the classic JVA design: (a) The overall footprint of the JV accounting data is greatly reduced. (b) Automatic re-conciliation between FI, JVA and CO is guaranteed. (c) JVA can utilize the new functionalities introduced through the ACDOCA design, for example: up to 10 local currencies; fast retrieval of aggregated data; new reporting tools.

## Description

The classic JVA is based on a couple of separate database tables that basically contained copies of the documents posted to the FI and CO ledgers (plus additional JVA-only documents). When the new JVA_ON_ACDOCA business function is switched on in an S4HANA system, these separate tables are not used, anymore. Instead, all JVA processing is based on the ACDOCA table ("Universal Journal Entries" - UJE).

Important remark: It is not mandatory to run JVA on the new data model in S4HANA, that is, the classic data model can still be used in S4HANA. However, if the new data model is not used right from the start, there is no standard solution by SAP to migrate from classic JVA to JVA on ACDOCA at a later point of time!

## Business Process related information

Although the underlying data model of JVA on ACDOCA has changed fundamentally (which required a re-development of all JVA month-end processes), the general business logic remains the same. Even the old transaction codes can still be used (when using the SAP GUI). Major changes happened in three areas only: (a) The Venture Bank Switching transactions ared replaced by Funding transactions that make use of the special ACDOCA featuers. (b) The reconciliation transaction GJ90 is not required, anymore. (c) The JVA variants of FI valuation transaction are not required anymore (GJ91, GJNO); instead, the corresponding FI transaction can and need to be used; these were enhanced to cover the JVA requirements.

The main difference regarding user experience is in the JVA reporting where the old SAP GUI-based reporting transaction are replaced by Design Studio-based FIORI apps that can be accessed via the Fiori Launchpad, only.

The master data model, on the other hand, has not been changed; just a few options had to be added to adapted to meet the required of the above-mentioned functionalities. The maintenance transactions have changed in the related areas only.

## Required and Recommended Actions

Before a conversion project is started, several notes should be read and fully understood by all stakeholders:

The supported migration and switch scenarios are explained in detail in the following note:

2941622 - Migration to S4HANA with Joint Venture Accounting running on ACDOCA

Further information on configuration tasks and restrictions can be found in the following notes:

3044558 - Configuration/customizing help for JVA on ACDOCA

2993369 - Restrictions for SAP Joint Venture Accounting on ACDOCA

A technical consistency check of the JVA ledgers should be executed by running the reports RGUSLSEP (to check the summary table consistency) and RGUREP11 (to check the object number consistency). For more information, see notes 764523 and the above-mentioned note 2941622.

## How to Determine Relevancy

To check the relevancy of this simplification item, execute the following checks:

Check if the business function 'JVA' is active (via transaction SFW5).

Check if any company code has been activated for JVA (via transaction GJZA).

## Other Terms

JVA, Joint Venture Accounting, migration, worklist
