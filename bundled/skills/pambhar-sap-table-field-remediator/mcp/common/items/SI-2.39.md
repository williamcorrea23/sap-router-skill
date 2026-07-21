---
item_id: SI-2.39
title: "2.39 S4TWL - Deprecation of Design Studio Apps"
pages: 97-98
sap_notes: [3081996, 3112220, 3133221, 3170381]
components: [CA-UX]
objects: []
---
Application Components:CA-UX

Related Notes:

| Note Type       |   Note Number | Note Description                          |
|-----------------|---------------|-------------------------------------------|
| Business Impact |       3133221 | S4TWL - Deprecation of Design Studio Apps |

## Symptom

You are doing an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

As of SAP S/4HANA 2021 SAP Design Studio apps have been deprecated. This includes all Finance apps based on the Design Studio technology. For all deprecated SAP Design Studio apps Web Dynpro data grid apps exist as alternatives. For a list of all deprecated SAP Design Studio apps and their alternatives refer to SAP note 3081996.

As of SAP S/4HANA 2022 most of these SAP Design Studio apps have been set to obsolete. This includes most Finance apps based on the Design Studio technology. Refer to SAP note 3170381 for more information.

## Business Process related information

Deprecated SAP Design Studio apps are no longer available by default on the SAP Fiori launchpad. However, you can still use them and also locate them using the app finder until they are deleted. Nevertheless, we strongly recommend switching to the SAP Web Dynpro successor apps as soon as possible. The Web Dynpro apps are already the default tiles on the SAP Fiori launchpad.

Obsolete SAP Design Studio apps are no longer supported and have been deleted from the system.

You can continue to use Design Studio reports that you created using the View Browser. However, you can no longer create new ones. We recommend creating Web Dynpro reports instead.

For more information refer to the What's New Viewer article on help.sap.com and note 3112220 - FAQ: Web Dynpro Apps and Design Studio Apps in SAP S/4HANA and SAP S/4HANA Cloud.

## Required and Recommended Action(s)

For deprecated SAP Design Studio apps:

Evaluate the SAP Web Dynpro apps as alternatives to the SAP Design Studio apps and decide when to switch to the successor apps. However, this need to happen latest before the next release upgrade of your SAP S/4HANA system.

If you use custom design studio apps note that they cannot be migrated automatically to Web Dynpro apps. You need to recreate them as Web Dynpro reports using the View Browser. Refer to SAP note 3081996 for details.

For obsolete SAP Design Studio apps:

Switch to the SAP Web Dynpro apps provided as alternatives to the SAP Design Studio apps latest with your upgrade.

## Other Terms
