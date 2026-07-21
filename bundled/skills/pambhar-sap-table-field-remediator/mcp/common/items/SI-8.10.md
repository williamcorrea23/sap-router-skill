---
item_id: SI-8.10
title: "8.10 S4TWL - Schedule Manager"
pages: 267-268
sap_notes: [2269324, 2332547, 2873915, 3003364]
components: [CA-GTF-SCM, FI-GL-GL-G]
objects: []
---
Application Components:CA-GTF-SCM, FI-GL-GL-G

Related Notes:

| Note Type       |   Note Number | Note Description         |
|-----------------|---------------|--------------------------|
| Business Impact |       3003364 | S4TWL - Schedule Manager |

## Symptom

You are doing a system conversion from SAP ERP to SAP S/4HANA or an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

Schedule Manager is part of the SAP S/4HANA compatibility scope, which comes with limited usage rights. For more details on the compatibility scope and it's expiry date and links to further information please refer to SAP note 2269324. In the compatibility matrix attached to SAP note 2269324, Schedule Manager can be found under the ID 431.

This means that you need to migrate from Schedule Manager to its designated alternative functionality SAP Advanced Financial Closing before expiry of the compatibility pack license. This note shall provide an overview how you can migrate to the alternative functionality.

## Business Process related information

SAP Advanced Financial Closing can be  used for SAP S/4HANA as of release SAP S/4HANA 1909. You find information about functional scope and setup of SAP Advanced Financial Closing at help.sap.com.

Note that SAP Advanced Financial Closing requires an extra license. As an alternative you may consider using standard Closing Cockpit (without license). Refer to SAP note 2332547 - S4TWL - Closing Cockpit with S/4HANA OP for more information.

SAP Advanced Financial Closing is SAPs strategic solution for orchestrating the entity close across complet system landscapes. For further information refer to SAP note 2873915 - FAQ: SAP Advanced Financial Closing.

## Required and Recommended Action(s)

As Schedule Manager can be used until the expiry date of the compatibility pack license, it's up to each customer to decide, when (with which of the coming SAP S/4HANA releases) they want to migrate to the designated alternative functionality.

## Other Terms

SAP S/4HANA, Compatibility Scope, System Conversion, Upgrade, SCMA, ID 431

## 9. Financials - Accounts Payable/Accounts Receivable
