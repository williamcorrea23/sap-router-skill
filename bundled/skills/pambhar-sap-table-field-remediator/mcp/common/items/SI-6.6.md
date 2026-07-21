---
item_id: SI-6.6
title: "6.6 S4TWL - Configuration Changes in Group Reporting"
pages: 230-233
sap_notes: [3326805]
components: [FIN-CS]
objects: []
---
## Application Components:FIN-CS

Related Notes:

| Note Type       |   Note Number | Note Description                                                                     |
|-----------------|---------------|--------------------------------------------------------------------------------------|
| Business Impact |       3326805 | S4TWL - Configuration in Group Reporting using Selections and FS item Role attribute |

## Symptom

You are preparing a system upgrade to SAP S/4HANA 2023 (S4CORE 108). The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

In the Global System Settings (transaction code CXB3), one of the following options for the Settings for Configuration Control are not marked:

Reclassification: Selection Object in Trigger

Validation in SAP S/4HANA

Breakdown Category: Selection Object in Maximum Selection

Currency Translation: Selection Object

Use Item Role Attribute

## Solution

## Business Value

The configuration of some functions in Group Reporting (breakdown categories, currency translation methods, reclassification methods, automatic postings on Selected FS items...) can be flexibly defined using

Selections  (https://help.sap.com/docs/SAP_S4HANA_ON-

PREMISE/4ebf1502064b406c964b0911adfb3f01/b3d1255de2244af486cb116919c1c5f1. html?locale=en-US) and using FS item Role attribute

(https://help.sap.com/docs/SAP_S4HANA_ON-

PREMISE/4ebf1502064b406c964b0911adfb3f01/bb5a08412bf145e9a950bee1bf4c6c6b. html?locale=en-US).

The options to use these feature are defined in the Global System Settings (transaction code CXB3). They are by default selected. Only in some circumstances (migration from EC-CS, initial release SAP S/4HANA 1809) some of these options are possibly not selected.

## Description

As of SAP S/4HANA 2023 (S4CORE 108), these options in the Global System Settings are always selected and cannot be edited.

## Business Process related Information

If some of these options are not selected in your system, you must adjust your configuration before the upgrade to use the Selections and the FS item Role.

## Required and Recommended Actions(s)

Check in the Global System Settings (transaction code CXB3) which of the following options are not selected:

Reclassification: Selection Object in Trigger

Validation in SAP S/4HANA

Breakdown Category: Selection Object in Maximum Selection

Currency Translation: Selection Object

Use Item Role Attribute

If you don't use the options Reclassification: Selection Object in Trigger, Breakdown Category: Selection Object in Maximum Selection, or Currency Translation: Selection Object

Follow this procedure to replace sets with selections in the configuration:

In the configuration activities Define Reclassification Methods, Define Breakdown Categories, and Define Currency Translation Methods, list all the sets you use and their content.

In the Check Global System Settings configuration activity, select the options Reclassification: Selection Object in Trigger, Breakdown Category: Selection Object in Maximum Selection, and Currency Translation: Selection Object.

In the Define Selections app, create a selection to replace the sets.

In the configuration activities Define Reclassification Methods, Define Breakdown Categories, and Define Currency Translation Methods, replace the sets by the Selections.

Check and test the configuration.

Follow this procedure to activate the usage of validations in SAP S/4HANA:

List the validation methods in use and how they are defined.

In the Define Validation Methods app, define new validations.

In the Assign Validation Methods app, assign the validations to consolidation units.

Check and test the configuration.

If you don't use the Use Item Role Attribute option, you can keep you configuration unchanged, or you can adjust your configuration to use the FS item Role attribute to select the FS item:

In the Check Global System Settings configuration activity, select the Use Item Role Attribute option.

In the Define Currency Translation Methods and Define Reclassification Methods configuration activities, check and adjust the configuration of selected FS items so that the role assigned corresponds to the correct FS item.

Check and test the configuration

## Other Terms

Sets, Selections, FS item Role attribute, Global System Settings, CXB3

## 7. Customer Service
