---
item_id: SI-5.1
title: "5.1 S4TWL -  CM: Simplified Market Data"
pages: 189-190
sap_notes: [2460737]
components: [SD-BF-CPE, LO-CMM-BF, MM-PUR-GF-CPE]
objects: []
---
Application Components:SD-BF-CPE, LO-CMM-BF, MM-PUR-GF-CPE

Related Notes:

| Note Type       |   Note Number | Note Description                   |
|-----------------|---------------|------------------------------------|
| Business Impact |       2460737 | S4TWL - CPE Simplified Market Data |

Symptom You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

With SAP S/4HANA, on-premise edition 1709 the Commodity Pricing Engine only supports market data based on Derivative Contract Specifications (DCS). The market data defined using Quotation Source, - Type and - Name are no longer supported.

## Business Process related information

Quotations have to be defined based on Quotation Rules

All relevant quotation rules have to be transfered to use market data based on DCS.

Relevant open documents have to be closed before the conversion

MM Contracts are not supported in the current version

The assigned document 'Cookbook From Exchange to DCS' describes examples how to set up Derivative Contract Specifications (DCS).

## Required and Recommended Action(s)

Source system EHP 7 and EHP 8 (Conversion to DCS based market data has to be done in the source system)

In the assigned document 'Cookbook Market Data in Commodity Managment', the process how to replace quotation Source, -Type and - Name based market data to DCS based market data is described. This step has to be executred in the source system before starting the conversion.

Accessing market data moved to the quotation rule, the definition as part of the term itself is no longer supported. All relevant settings have to be transferred to a quoation rule, assigned to the term. The assigned document 'Function in Details Quotation Rule' describes the necessary steps to convert the data.

Source System before EHP 7 (Conversion to DCS based market data has to be done in the target system)

In the assigned document 'Conversion to DCS based Market Data before EHP7' a project based solution how to convert the data is described.
