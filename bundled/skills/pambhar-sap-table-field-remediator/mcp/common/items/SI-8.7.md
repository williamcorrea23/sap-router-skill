---
item_id: SI-8.7
title: "8.7 S4TWL -  Special Purpose Ledger"
pages: 262-263
sap_notes: [2269324, 2993220, 2999249, 3006586, 3015013, 3572033]
components: [FI-SL]
objects: []
---
Application Components:FI-SL

Related Notes:

| Note Type       |   Note Number | Note Description               |
|-----------------|---------------|--------------------------------|
| Business Impact |       3015013 | S4TWL - Special Purpose Ledger |

## Symptom

You are doing a system conversion from SAP ERP to SAP S/4HANA or an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

The usage of special purpose ledger is partly included in the

SAP S/4HANA compatibility scope, which comes with limited usage rights. For more details on the compatibility scope and it's expiry date and links to further information please refer to SAP note 2269324. In the compatibility matrix attached to SAP note 2269324, this topic is listed under the ID 430.

This note shall provide information on the restrictions that apply for special purpose ledger in SAP S/4HANA.

## Business Process related information

You find a description of the functionality in compatibility scope in the SAP S/4HANA Feature Scope Description > section Special Ledger (FI-SL).

Generally, special purpose ledger as framework is not part of compatibility scope, which means it will be available and supported beyond the compatibility scope expiry date. However, special ledgers and respective tables and reports which have been defined for applications that are part of the compatibility scope will not be supported beyond expiry date. This applies to the following applications

EC-PCA - Planning in classical profit center accounting (compatibility scope ID 427)

Cost of Sales ledger (compatibility scope ID 430)

Consolidation preparation - Closing Operations (compatibility scope ID 430)

Custom-defined ledgers based on the applications listed above will also not be support beyond expire date. Custom-defined ledgers based on any other SAP applications or custom-built tables will be supported.

Refer to the attached spreadsheet for detailed availability description of the SAP delivered ledgers and related tables.

## Required and Recommended Action(s)

Refer to the following notes and simplification items for further information on the handling the deprecated applications.

Classical profit center accounting - note 2993220 (plan) and 3572033 (actual)

Cost of Sales ledger - note 3006586

Consolidation preparation - Closing Operations - note 2999249

For all other special purpose ledgers no actions are required.

## Other Terms

SAP S/4HANA, Compatibility Scope, Compatibility Package, System Conversion, Upgrade, Special Ledger, ID 430
