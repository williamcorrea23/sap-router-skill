---
item_id: SI-3.11
title: "3.11 S4TWL - Business Partner Hierarchy Not Available"
pages: 143-144
sap_notes: [2409939]
components: [LO-MD-BP]
objects: []
---
## Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                 |
|-----------------|---------------|--------------------------------------------------|
| Business Impact |       2409939 | S4TWL - Business Partner Hierarchy Not Available |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Business Value

Business Partner hierarchy is removed in SAP S/4HANA to avoid redundancy as customer hierarchy is already available for the applications to consume.

## Description

The Business Partner Hierarchy is no more available in S/4HANA. S/4HANA is in conceptualize stage for a better hierarchy solution.

## Business Process related information

You will not be able to access the BP hierarchy data anymore after the system conversion to S/4HANA.

| Transaction not available in SAP S/4HANA on- premise edition      | BPH, BPH_TYPE                                                     |
|-------------------------------------------------------------------|-------------------------------------------------------------------|
| BAPIs not available in SAP S/4HANA on-premise edition             | BUHI_ASSIGN_BP_TO_NODE BUHI_CLEAR_BUFFER BUHI_DELETE_BP_FROM_NODE |
| IMG activity node not available in SAP S/4HANA on-premise edition | Business Partner Group Hierarchy                                  |
| BOR Object not available in SAP S/4HANA on- premise edition       | BUS1006004                                                        |

## Required and Recommended Action(s)

Knowledge transfer to key and end users

## How to Determine Relevancy

This item is relevant if you have created and are using Business Partner Hierarchies. You can check for the existence of Business Partner Hierarchies in transaction BPH or check for the existence of entries in table BUT_HIER_TREE.
