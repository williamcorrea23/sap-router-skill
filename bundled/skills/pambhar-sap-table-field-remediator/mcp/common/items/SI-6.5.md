---
item_id: SI-6.5
title: "6.5 S4TWL - Business Consolidation (SEM-BCS)"
pages: 229-230
sap_notes: [1330000, 2360258, 2659672, 3205515]
components: [FIN-SEM-BCS]
objects: []
---
Application Components:FIN-SEM-BCS

Related Notes:

| Note Type       |   Note Number | Note Description                                         |
|-----------------|---------------|----------------------------------------------------------|
| Business Impact |       3205515 | S4TWL - Business Consolidation (SEM- BCS) in SAP S/4HANA |

## Symptom

You are using Business Consolidation (SEM-BCS) in SAP S/4HANA based on Embedded BW. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

SAP regards Business Consolidation (SEM-BCS) in SAP S/4HANA no longer as strategic solution. Therefore, SAP has decided to phase out SEM-BCS from SAP S/4HANA. If you already use SEM-BCS in SAP S/4HANA releases up to release 2021, SEM-BCS is in deprecation state as of release SAP S/4HANA 2022. This means after an upgrade to SAP S/4HANA 2022 you can still continue using SEM-BCS with full support and maintenance. However, SAP does not plan to provide new features for SEM-BCS in SAP S/4HANA. Designated alternative for SEM-BCS in SAP S/4HANA is " SAP S/4HANA Finance for Group Reporting ".

Note that the features of SEM-BCS in SAP S/4HANA are only available for customers who have licensed these features before October 1st, 2022, including maintenance for these features.

If you want to deploy a consolidation solution on top of a data warehouse, outside of SAP S/4HANA, you can use " SAP BW/4HANA, Business Consolidation Add-On " (BCS/4HANA). The relevant release information on BCS/4HANA is provided in SAP Note 1330000 and in the rollout materials quoted therein.

## Business Process related information

For a description of the functional scope of SEM-BCS in the context of SAP S/4HANA refer to SAP Note 2360258 and to the SAP S/4HANA Feature Scope Description "Business Consolidation".

For information about the alternative solution " SAP S/4HANA Finance for Group Reporting " refer to the SAP Help Portal and SAP note 2659672 - FAQ About SAP S/4HANA Finance for Group Reporting (On Premise).

## Required and Recommended Action(s)

Make yourself familiar with " SAP S/4HANA Finance for Group Reporting " (S/4GR) and define your strategy when to switch to the new solution.

For technical setup of S/4GR, see the IMG (Implementation Guide) for this product. In particular, the following activities are required:

Either " Install SAP Best Practice Content " or execute the IMG activity " Initialize Settings "

Create master data for accounts, account hierarchies, organizational units and business configuration in S/4GR, in analogy with the existing entities which you have been using in SEM-BCS in SAP S/4HANA

Create opening balance in S/4GR based on legacy transaction data from SEM-BCS in SAP S/4HANA

For further information, please contact your SAP Account Executive.

## Other Terms

SAP S/4HANA, SEM-BCS, business consolidation, deprecation state
