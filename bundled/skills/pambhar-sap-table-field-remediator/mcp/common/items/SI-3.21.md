---
item_id: SI-3.21
title: "3.21 S4TWL - Simplified Product Master Tables Related to OMSR Transaction"
pages: 161-162
sap_notes: [2267138]
components: [LO-MD-MM]
objects: []
---
## Application Components:LO-MD-MM

Related Notes:

| Note Type       |   Note Number | Note Description                                                     |
|-----------------|---------------|----------------------------------------------------------------------|
| Business Impact |       2267138 | S4TWL - Simplified Product Master Tables related to OMSR transaction |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

In SAP S/4HANA, the tables related to OMSR transaction("Field groups and Field selection for data screens") such as T130F (Table of Field attributes), T130A (Table of Material master field selection), T133F (Table of Material master field selection part2) ,etc., has delivery class E (E = Control table, SAP and customer have separate key areas). In SAP Business Suite, the delivery class of these tables is G (G= Customizing table, protected against SAP Update, only INS all).

## Business Process related information

No influence on business processes expected

## Required and Recommended Action(s)

Customizing the field selection for data screens in SAP namespace is not recommended anymore.

To customize the field selection settings, kindly follow the below process.

In OMSR/OMS9 transaction, select the field ref. you want to change.

Click on Copy As icon or press F6.

Enter the Field reference ID in allowed namespace.

Make the required changes for the field groups and press enter.

Click on Save.

The created field reference can be assigned to required material type / plant.

To assign it to a material type, go to transaction OMS2.

Open the required material type, update the Field reference . Click on Save.

To assign it to a plant, go to transaction OMSA.

Add an entry by clicking New entries . Click on Save.

## General Recommendation

In S/4HANA the recommendation is to adjust the field references from a transaction based approach to a material type approach. In the SAP standard, the transaction based field references were set to optional, so that the field selection can be controlled via the field references of the material type.

In case you continue to work with a transaction based approach, you need to doublecheck the modifications you made to these field references after each upgrade, since the modifications to these field references might be overwritten with the SAP standard. Changing the field selection group also has to be double-checked after each upgrade, since the modifications of the field selection groups might also be overwritten with the SAP standard.
