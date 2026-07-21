---
item_id: SI-3.8
title: "3.8 S4TWL - HANA-based Analytics for Master Data Governance"
pages: 138-139
sap_notes: [2375319]
components: [CA-MDG-ANR]
objects: []
---
Application Components:CA-MDG-ANR

Related Notes:

| Note Type       |   Note Number | Note Description                                            |
|-----------------|---------------|-------------------------------------------------------------|
| Business Impact |       2375319 | S4TWL - HANA-based Analytics for SAP Master Data Governance |

## Symptom

You are doing a system conversion to SAP S/4HANA. The following SAP S/4HANA Transition Worklist item is applicable in case SAP Master Data Governance is used.

## Solution

## Description

SAP HANA-based Analytics for SAP Master Data Governance is not available within SAP S/4HANA, on-premise edition 1511 and higher.

## Business Process related information

With this system conversion the content generation for SAP HANA-based Analytics for SAP Master Data Governance is no longer available.

## Required and Recommended Action(s)

The following check is only required in case that you have SAP Master Data Governance in active usage. In this case please check if also SAP HANA-based Analytics for SAP Master Data Governance is set up and running.

## How to Determine Relevancy

Check if content for SAP HANA-based Analytics for SAP Master Data Governance has been generated. This can be done via the following steps:

Use transaction SLG1 and check if log entries for MDG_ANA_HANA are existing.

Check if generated content is available on one of the SAP HANA Databases that are connected to the according system. This can be done for example by looking for calculation view 'ChangeRequestHeader'.
