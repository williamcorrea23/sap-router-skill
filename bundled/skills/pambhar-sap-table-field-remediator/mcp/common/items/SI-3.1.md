---
item_id: SI-3.1
title: "3.1 S4TWL - MDM 3.0 integration"
pages: 124-125
sap_notes: [1529387, 2267295]
components: [LO-MD-MM]
objects: []
---
Application Components:LO-MD-MM

Related Notes:

| Note Type       |   Note Number | Note Description            |
|-----------------|---------------|-----------------------------|
| Business Impact |       2267295 | S4TWL - MDM 3.0 integration |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist Item is applicable in this case.

## Solution

## Description

The MDM specific transaction codes for IDoc processing (inbound and extraction) are not available within SAP S/4HANA, on-premise and cloud edition. The item is valid starting with S/4 HANA release 1511 as well as for all newer releases.

## Business Process related information

MDM 3.0 was discontinued. All known customer implementations have migrated to SAP NetWeaver MDM or SAP Master Data Governance, Central Governance. All known customer implementations have already replaced the SAP MDM 3.0 specific IDoc processing according to SAP note 1529387 "Tables MDMFDBEVENT, MDMFDBID, MDMFDBPR growing significantly".

## Required and Recommended Action(s)

None

## Related SAP Notes

| General SAP Note related to Simplification Item SAP Note: 1529387   |
|---------------------------------------------------------------------|
