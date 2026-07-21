---
item_id: SI-6.2
title: "6.2 S4TWL - Consolidation (EC-CS) and preparations for consolidation"
pages: 224-226
sap_notes: [2269324, 2371973, 2659672, 2833748, 2999249]
components: [EC-CS]
objects: []
---
Application Components:EC-CS

Related Notes:

| Note Type       |   Note Number | Note Description                                        |
|-----------------|---------------|---------------------------------------------------------|
| Business Impact |       2999249 | S4TWL - Consolidation and Preparation for Consolidation |

## Symptom

You are doing a system conversion from SAP ERP to SAP S/4HANA or an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

Description Consolidation (EC-CS) and preparations for consolidation are part of the SAP S/4HANA compatibility scope, which comes with limited usage rights. For more details on the compatibility scope and it's expiry date and links to further information please refer to SAP note 2269324 . In the compatibility matrix attached to SAP note 2269324, Consolidation (EC-CS) and preparations for consolidation can be found under the ID 434.

This means that you need to migrate from Consolidation (EC-CS) and preparations for consolidation to the designated alternative functionality SAP S/4HANA for Group Reporting . The license for SAP S/4HANA for Group Reporting includes usage right for EC-CS until December 31st, 2027. This note shall provide further information on what to do to move to the alternative functionality.

## Business Process related information

For a description of the functional scope of EC-CS in the context of SAP S/4HANA refer to SAP note 2371973 and to the SAP S/4HANA Feature Scope Description in sections SAP S/4HANA Compatibility Packs > Consolidation (EC-CS) and Preparations for Consolidation.

For information about the alternative solution SAP S/4HANA for Group Reporting refer to the SAP Help Portal and SAP note 2659672 - FAQ About SAP S/4HANA Finance for Group Reporting (On Premise).

## Required and Recommended Action(s)

Make yourself familiar with SAP S/4HANA for Group Reporting and define your strategy when to switch to the new solution.

For information how to transition from EC-CS to SAP S/4HANA for Group Reporting refer to SAP note 2833748.

Most important aspect to consider are as follows:

In SAP S/4HANA 1809, coexistence of EC-CS and SAP S/4HANA for Group Reporting in the same SAP S/4HANA instance is not supported. You must set up a separate (new) SAP S/4HANA instance for usage of Group Reporting.

As of SAP S/4HANA 1909, parallel usage of EC-CS and SAP S/4HANA for Group Reporting is possible ("hybrid system state"). This allows you to test usage of Group Reporting in parallel to the productive use of EC-CS.

If you are on SAP S/4HANA 1909 or later and wish to run your system in the hybrid state to prepare the transition to Group Reporting, you need to contact SAP Support because the transition from EC-CS into hybrid system state is executed in a multiple step procedure of which some steps are executed by SAP Support.

## Other Terms

SAP S/4HANA, Compatibility Scope, Compatibility Package, System Conversion, Upgrade, Consolidation, ID 434
