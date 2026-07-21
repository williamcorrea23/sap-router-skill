---
item_id: SI-2.18
title: "2.18 S4TWL - FIORI APPLICATIONS FOR SUITE ON HANA ONPREMISE"
pages: 49-51
sap_notes: [2242596, 2288828, 2290488]
components: [XX-SER-REL]
objects: []
---
Application Components:XX-SER-REL

Related Notes:

| Note Type       |   Note Number | Note Description                                                      |
|-----------------|---------------|-----------------------------------------------------------------------|
| Business Impact |       2288828 | S4TWL - Fiori Applications for SAP Business Suite powered by SAP HANA |

You are doing a system conversion to SAP S/4HANA, on-premise edition. You already use existing Fiori Apps in your Business Suite (e.g. ERP Enhancement Packages) landscape and would like to understand the conversion behavior and adoption needs on the frontend server.

## Reason and Prerequisites

SAP S/4HANA, on-premise edition comes with a corresponding UI product for frontend server installation. The new SAP S/4HANA, on-premise edition UI product is not the successor of any Business Suite product and delivers a set of applications which is from a technical and scope perspective independent from any previous Business Suite UI product. This implies the following conversion behaviour:

## 1. Different product scope

There is no automatism that apps from Business Suite will be offered in the same way for SAP S/4HANA, on-premise edition as well. Apps might be replaced, enhanced, changed, implemented using different technology or not offered in the SAP S/4HANA context. The available app scope can be checked in the SAP Fiori apps reference library (see detailed description below).

## 2. No automated conversion

The central frontend server must support multiple back-end systems. Therefore it is not possible to convert the existing settings from Business Suite applications during the installation as this would break the existing apps and Business Suite installations on the same frontend server. The new S/4HANA UI product can be co-deployed and runs only against the SAP S/4HANA, on-premise edition back-end. Also the other way round, existing Business Suite UI products will not run against a SAP S/4HANA, on-premise edition back-end. Configuration details for every app can be found in the SAP Fiori apps reference library.

## Solution

Use the SAP Fiori apps reference library to check which applications are available for SAP S/4HANA, on-premise and for configuration details.

## Option 1: Filter those apps, which are available in S/4HANA on-premise edition

In SAP Fiori apps reference library, use the Filter 'Required Back-End Product' and select 'SAP S/4HANA, on-premise edition' to display a list of all Fiori apps available. This filter can be combined with other filters like Line of Business or Role.

Option 2: Check availability in SAP S/4HANA on-premise edition for a single app

Select the Fiori app in the SAP Fiori apps reference library. A drop-down list box will appear in the header area of the app details page, if the app is available in multiple products. In case the selected app is not available for S/4HANA on-premise edition check, whether a successor app exist. You will can directly navigate to the successor app from the bottom of the PRODUCT FEATURES tab.

Example: Fiori app 'My Spend' for ERP has a successor 'My Spend', which is available for ERP Add-On 'SAP FIORI for SAP SFIN 1503' as well as 'S/4 HANA on-premise 1511'

## Option 3: Check availability in in S/4HANA on-premise edition for multiple apps

Filter and select all apps you want to check. Activate 'Aggregate' at the bottom of the app list to display a consolidated view about all selected apps. Select 'SAP S/4HANA, on-premise edition' in the drop-down on top of the list. All apps which are not available for SAP S/4HANA, on-premise edition will be highlighted as not available at the bottom of the list of selected apps.

Check in the details of the individual apps whether a successor app is available (see option 2 above).

## Additional information provided per application area (where required):

Note 2242596 - Release Information: Changes in Fiori Content in S/4Hana Finance, on-premise edition 1605 (sFIN 3.0)

Note 2290488 - Changes in Fiori Application for SAP S/4 HANA in Sales and Distribution

## Other Terms

Fiori, Conversion, Business Suite, S/4HANA on-premise, Conversion
