---
item_id: SI-2.48
title: "2.48 S4TWL - INTERNET PRICING AND CONFIGURATOR (SAP IPC)"
pages: 113-115
sap_notes: [2238670, 2318509]
components: [AP-CFG]
objects: []
---
Application Components:AP-CFG

Related Notes:

| Note Type       |   Note Number | Note Description                                    |
|-----------------|---------------|-----------------------------------------------------|
| Business Impact |       2318509 | S4TWL - INTERNET PRICING AND CONFIGURATOR (SAP IPC) |

Symptom You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

The Internet Pricing and Configurator (SAP IPC) is not released within SAP S/4HANA. For scenarios and business processes where the Internet Pricing and Configurator is currently used alternative functionality like ABAP-based configuration (LO-VC) can be used in SAP S/4HANA.

## Business Process related information

In the Business Suite, The Internet Pricing and Configurator (aka SAP AP Configuration Engine) is usually used for the following use cases:

Configuration Processes in SD/MM (incl. Pricing) as alternative to LO-VC

Creation of Material Variants

For the Vehicle Management System (VMS), SAP IPC could be used for vehicle configuration as alternative to the variant configuration (LO-VC). For each vehicle model defined as configurable material, the configuration engine could be switched from variant configuration to SAP IPC and vice versa

Configuration Simulation in combination with SAP CRM

Web Channel (aka Internet Sales) ERP Edition - this application is not released with S/4HANA

For scenarios and business processes where the Internet Pricing and Configurator is currently used alternative functionality like ABAP-based configuration (LO-VC) can be used in SAP S/4HANA.

## Required and Recommended Action(s)

Implement Business Scenarios and Business Processes based on the functionality available within SAP S/4HANA like ABAP-based configuration (LO-VC). Revert entries in CUCFGSW if needed.

## How to Determine Relevancy

There is no unambiguous single indicator whether IPC is productively used. However, there are a number of hints:

If table IBIB shows any entries in field KBID, configurations created with IPC have been stored. This is an indicator at least for usage in the past.

Table TCUUISCEN contains mandatory information for the configuration UI. If this table contains records, at least the installation has been set up. It is quite likely that IPC is actively used.

Table CUCFGSW contains the "IPC Switch". If this table contains records, master data has been set up to use IPC instead of VC. This is not only an indicator for IPC usage, moreover entries must be reverted prior to conversion to S/4HANA.

## Related SAP Notes

| Custom Code related information   | SAP Note: 2238670   |
|-----------------------------------|---------------------|
