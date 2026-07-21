---
item_id: SI-2.37
title: "2.37 S4TWL - New Default Security Settings for SAP S/4HANA"
pages: 94-95
sap_notes: [2926224]
components: [XX-PROJ-CON-SEC]
objects: []
---
## Application Components:XX-PROJ-CON-SEC

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                 |
|-----------------|---------------|--------------------------------------------------------------------------------------------------|
| Business Impact |       2926224 | Collection Note: New security settings for SAP S/4HANA and SAP BW/4HANA using SL Toolset and SUM |

## Symptom

This is the central entry point for all information around new secure-by-default settings for SAP S/4HANA.

You want to know more details about the new secure-by-default settings for SAP S/4HANA systems. During SAP S/4HANA provisioning you were asked to review the profile parameters set by SL Toolset (e.g. SWPM, SUM).

## Reason and Prerequisites

You are using the latest SL Toolset or SUM. This will introduce the latest recommended security settings for SAP S/4HANA systems and SAP BW/4HANA systems.

From SAP S/4HANA 1909 onwards and SAP BW/4HANA 2021 onwards, new installations (with SWPM), system copies (with SWPM) and system conversions from SAP ERP to SAP S/4HANA (with SUM) will automatically receive the recommended security settings. An opt-out is possible for the security relevant profile parameters, but not recommended from SAP side.

In SAP S/4HANA and SAP BW/4HANA upgrades (with SUM), security settings are not adjusted automatically. In some cases, preparations are necessary before configurations / parameters can be switched to secure values in upgraded systems. That's why configurations / parameters are not changed during the upgrade process. Though it's recommended to also apply the updated security settings in system which have been upgraded from older SAP S/4HANA and BW/4HANA releases.

## Solution

For more details, how the security settings change in each SAP S/4HANA and SAP BW/4HANA release and what you need to do and know about these changes from system operations point of view, please refer to the release specific SAP notes linked in this note.

The attached spreadsheet contains the list of all security settings that are recommended. The attached spreadsheet was updated with the list of security settings for SAP S/4HANA 2023.

## Other Terms

Software Provisioning Manager (SWPM), SWPM, SAPinst, SL Toolset, security, profile parameter, Software Update Manager (SUM), SUM, security, conversion, upgrade
