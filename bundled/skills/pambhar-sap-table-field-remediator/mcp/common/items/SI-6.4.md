---
item_id: SI-6.4
title: "6.4 S4TWL - Real-Time Consolidation (RTC)"
pages: 227-229
sap_notes: [2659672, 3205500]
components: [FIN-RTC]
objects: []
---
Application Components:FIN-RTC

Related Notes:

| Note Type       |   Note Number | Note Description                                     |
|-----------------|---------------|------------------------------------------------------|
| Business Impact |       3205500 | S4TWL - Real-Time Consolidation (RTC) in SAP S/4HANA |

Symptom You are using Real-Time Consolidation (RTC) in SAP S/4HANA. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

SAP regards Real-Time Consolidation (RTC) in SAP S/4HANA no longer as strategic solution. Therefore, SAP has decided to phase out RTC in SAP S/4HANA. If you already use RTC in SAP S/4HANA releases up to release 2021, RTC is in deprecation state as of release SAP S/4HANA 2022. This means after an upgrade to SAP S/4HANA 2022 you can still continue using RTC with full support and maintenance. However, SAP does not plan to provide new features for RTC. Designated alternative for RTC is SAP S/4HANA Finance for Group Reporting .

Note that the features of Real-Time Consolidation are only available for customers who have licensed these features before October 1st, 2022, including maintenance for these features.

## Business Process related information

For a description of the functional scope of RTC in the context of SAP S/4HANA refer to the SAP S/4HANA Feature Scope Description "Corporate Close - Data Preparation".

For information about the alternative solution " SAP S/4HANA Finance for Group Reporting " refer to the SAP Help Portal and SAP note 2659672 - FAQ About SAP S/4HANA Finance for Group Reporting (On Premise).

## Required and Recommended Action(s)

Make yourself familiar with SAP S/4HANA Finance for Group Reporting (S/4GR) and define your strategy when to switch to the new solution.

For technical setup of S/4GR, see the IMG (Implementation Guide) for this product. In particular, the following activities are required:

Either " Install SAP Best Practice Content " or execute the IMG activity " Initialize Settings "

Create master data for accounts, account hierarchies, organizational units and business configuration in S/4GR, in analogy with the existing entities which you have been using in RTC in SAP S/4HANA

Create opening balance in S/4GR based on legacy transaction data from RTC in SAP S/4HANA

For further information, please contact your SAP Account Executive.

## Other Terms

SAP S/4HANA, RTC, Real-Time Consolidation, deprecation state
