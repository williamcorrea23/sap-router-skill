---
item_id: SI-2.45
title: "2.45 S4TWL - ENTERPRISE SEARCH"
pages: 107-108
sap_notes: [2227007, 2318521]
components: [BC-EIM-ESH]
objects: []
---
## Application Components:BC-EIM-ESH

Related Notes:

| Note Type       |   Note Number | Note Description          |
|-----------------|---------------|---------------------------|
| Business Impact |       2318521 | S4TWL - Enterprise Search |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

ESH_SEARCH was the generic search UI of Enterprise Search in previous releases. Its successor in SAP S/4HANA is the integrated search functionality in the Fiori Launchpad.

## Business Process related information

If a customer migrates from an older release to SAP S/4HANA and if he created his own search models or enhanced existing ones before, he needs to migrate his enhancements to the maybe changed standard search models of SAP S/4HANA.

Note that the navigation targets are not maintained any longer in the Enterprise Search model, but in the Fiori Launchpad Designer.

| Transaction not available in SAP S/4HANA 1511   | ESH_SEARCH   |
|-------------------------------------------------|--------------|

## Required and Recommended Action(s)

The search functionality is always available in the header area of the Fiori Launchpad. So you don't need a transaction code to start it.

The users may need a general introduction into the Fiori Launchpad. Only if the customer created his own search models or enhanced existing ones before, he needs to migrate his enhancements to the maybe changed standard search models of SAP S/4HANA. Note that the navigation targets are not maintained any longer in the Enterprise Search model, but in the Fiori Launchpad Designer.

## Related SAP Notes

| Custom Code related information   | SAP Note: 2227007   |
|-----------------------------------|---------------------|
