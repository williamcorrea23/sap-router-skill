---
item_id: SI-5.3
title: "5.3 S4TWL - CM: CPE Simplified Formula Assembly & Formula Evaluation"
pages: 191-192
sap_notes: [2461021]
components: [MM-PUR-GF-CPE, SD-BF-CPE, LO-CMM-BF]
objects: []
---
Application Components:MM-PUR-GF-CPE, SD-BF-CPE, LO-CMM-BF

Related Notes:

| Note Type   | Note Number   | Note Description   |
|-------------|---------------|--------------------|

| Business Impact   | 2461021   | S4TWL - CM: CPE Simplified Formula Assembley & Formula Evaluation   |
|-------------------|-----------|---------------------------------------------------------------------|

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709 the Formula Assembly of the Commodity Pricing Engine (CPE) is done based on BRF+ and for Forumla Evaluation, the access to document data has been simplified.

## Business Process related information

The configuration of Formula Assembly has to be transferred to BRF+.

Customer coding using the field mapping information in Formula Evaluation has to be adjusted.

The necessary adjustments are done in the target system

## Required and Recommended Action(s)

In the assigned document 'Cookbook Formula Assembly based on BRFplus', the process how to transfer Formula Assembly to BRF+ is described.

In the assigned document 'Function in Details - Formula Evaluation', all the necessary information how to adjust customer coding is included.
