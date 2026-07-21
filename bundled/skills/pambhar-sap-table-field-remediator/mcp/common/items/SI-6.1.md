---
item_id: SI-6.1
title: "6.1 S4TWL - Usage of long Material Number in EC-CS"
pages: 223-224
sap_notes: [2209784, 2471287]
components: [EC-CS]
objects: [MATNR]
---
Application Components:EC-CS

Related Notes:

| Note Type       |   Note Number | Note Description                               |
|-----------------|---------------|------------------------------------------------|
| Business Impact |       2471287 | S4TWL - Usage of long Material Number in EC-CS |

## Symptom

You are preparing a system conversion to SAP S/4HANA. Pre-transition checks for the application EC-CS SAP Consolidation must be carried out before the conversion.

This SAP Note describes simplification item SI01: EC_CS_MATNR. See also SAP note 2209784 for the old pre-check framework.

## Reason and Prerequisites

This SAP Note is relevant for you when your start release for the system conversion is an ERP release.

It is not relevant if your start release is SAP S/4HANA.

## Solution

## Description

In SAP S/4HANA, the material number was extended to a maximum length of 40 characters. As a result, the material number is longer than the maximum length defined for characteristics in the EC-CS data model.

Business Process Related Information If you have included a field of type MATNR (material number) as a customer-defined subassignment in the EC-CS data model, the EC-CS data model must be adjusted before the upgrade.

## Required and Recommended Action

If the check detects that such a field is used in the EC-CS data model as a customerdefined subassignment, contact SAP Support by creating a customer indicident on SAP Service Marketplace to application component EC-CS.

Rationale: The EC-CS data model in your system must be changed in this case. This change of the data model implies that the EC-CS Consolidation transaction data must be converted and information may also be lost during this process, because fields of type MATNR (material number) must be removed from the data model.

## Other Terms

S4TC, CLS4SIC_EC_CS, XS4SIC_EC_CS
