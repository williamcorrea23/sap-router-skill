---
item_id: SI-2.11
title: "2.11 S4TWL - Removal of Business Application Accelerator"
pages: 41-42
sap_notes: [1694697]
components: [BC-DB-DBI]
objects: []
---
## Application Components:BC-DB-DBI

Related Notes:

| Note Type       |   Note Number | Note Description                                     |
|-----------------|---------------|------------------------------------------------------|
| Business Impact |       1694697 | SAP Business Application Accelerator powered by HANA |

## Symptom

You are looking for information about the SAP Business Application Accelerator powered by HANA.

## Solution

The SAP Business Application Accelerator powered by HANA has been offered as ABAP Add-on in a restricted shipment mode until end of 2016.

Starting with 2017 the Add-on is no longer available for new customers.

The Add-on is in general not supported in S/4 HANA. The existence of the Add-on is blocking technical conversions to S/4HANA 1511 and 1610. Technical conversions to 1709 and beyond are possible.

Support for existing customers on non-4/HANA products is continued under the same conditions as before.

To benefit from SAP HANA it is recommended to migrate the entire system to SAP HANA, possibly with a multi node setup for optimized load distribution.

For a description of the functionality and usage of the SAP Business Application Accelerator powered by HANA please read the attached Customer Guide.

## Contents:

1 Introduction

2 Concept

2.1 Redirected Operations

2.1.1 Statements

2.1.2 Source

2.2 Context Definition

2.3 Context Evaluation at Runtime

3 Using the SAP Business Application Accelerator

3.1 Installation

3.2 General Activation

3.3 Loading Scenarios

3.3.1 Predefined SAP Scenarios

3.3.2 Custom Scenarios

3.4 Trouble Shooting

## Other Terms

Suite Accelerator, Scenarios, Context, RDA_MAINTAIN
