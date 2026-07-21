---
item_id: SI-2.34
title: "2.34 S4TWL - Removal of Add-On CTS_PLUG"
pages: 90-90
sap_notes: [2630240, 2820229]
components: [BC-CTS-TMS-CTR]
objects: []
---
Application Components:BC-CTS-TMS-CTR

Related Notes:

| Note Type       |   Note Number | Note Description        |
|-----------------|---------------|-------------------------|
| Business Impact |       2820229 | S4TWL - Add-On CTS_PLUG |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case if add-on CTS_PLUG is installed in the system.

## Reason and Prerequisites

CTS_PLUG, as an add-on, is neither required nor support in S/4HANA contexts.

## Solution

## Description & Business Process related information

The add-on CTS_PLUG is no longer requried in SAP S/4HANA system contexts, as all coding changes have been migrated back into the basis of S/4HANA. Before a conversion to S/4HANA, on-premise addition can be performed, CTS_PLUG needs to be uninstalled. Please refer to note 2630240 for more details.

## Other Terms

cCTS, central CTS, CTS Server Plugin
