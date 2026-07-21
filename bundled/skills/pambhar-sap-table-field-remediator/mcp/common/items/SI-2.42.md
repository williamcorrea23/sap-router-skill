---
item_id: SI-2.42
title: "2.42 S4TWL - Replacement of Add-ons in Compatibility Scope"
pages: 101-103
sap_notes: [2269324, 3502536]
components: [BC-UPG-ADDON]
objects: []
---
Application Components:BC-UPG-ADDON

Related Notes:

| Note Type   | Note Number   | Note Description   |
|-------------|---------------|--------------------|

| Business Impact   | 3502536   | S4TWL - Replacement of Add-ons in Compatibility Scope   |
|-------------------|-----------|---------------------------------------------------------|

## Symptom

You are doing a system conversion from SAP ERP to SAP S/4HANA or an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note.

## Solution

## Description

The add-ons listed below are part of the SAP S/4HANA compatibility scope, which comes with limited use rights. For more details on the compatibility scope and links to further information please refer to SAP note 2269324.

| Add-on technical software component   | Add-on product                                                                                                             | Compatibility ID   | Package   |   Alternative available as of SAP S/4HANA | Alternative add-on Software   | component   |
|---------------------------------------|----------------------------------------------------------------------------------------------------------------------------|--------------------|-----------|-------------------------------------------|-------------------------------|-------------|
| PAY- ENGINE                           | SAP Payment Engine                                                                                                         | 106                |           |                                      1909 | PES4                          |             |
| SMERP SMFND                           | SAP SAP Enterprise Integration for Work Manager mobile app SAP Enterprise Integration for Inventory Manager                | 111 113            |           |                                      1909 | retrofit to core              | S/4HANA     |
| CYT                                   | mobile app SAP Capital Yield Tax Mgmt, international version SAP Capital Yield Tax Mgmt, version for Germany / Switzerland | 121 122            |           |                                      1909 | CYT4HANA                      |             |
| SLCE 630 and below                    | SAP Configure, Price, and                                                                                                  | 129 130            |           |                                      1809 | SLCE 800                      |             |

| Quote for solution sales configuration, up to 20 units SAP Configure, Price, and Quote for solution sales configuration, above 20 units   |
|-------------------------------------------------------------------------------------------------------------------------------------------|

## Required and Recommended Action(s)

Use rights of the compatibility package licenses for the add-ons above expire as described in note 2269324. To stay compliant, you should upgrade to the latest SAP S/4HANA release, minimum to the listed SAP S/4HANA releases. You define the required target versions of the installed add-ons in Maintenance Planner. The update to the respective versions in the SAP S/4HANA target release is then done in the course of the technical upgrade.

The new add-on versions usually also come with new SAP S/4HANA licenses. Please get in touch with your SAP account team to check if required licenses are in place.

## Other Terms

SAP S/4HANA, Compatibility Scope, Compatibility Packages, System Conversion, Upgrade
