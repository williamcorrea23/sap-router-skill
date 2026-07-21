---
item_id: SI-7.1
title: "7.1 S4TWL - Customer Service"
pages: 233-234
sap_notes: [2269324, 2962632]
components: [CS]
objects: []
---
Application Components:CS

Related Notes:

| Note Type       |   Note Number | Note Description         |
|-----------------|---------------|--------------------------|
| Business Impact |       2962632 | S4TWL - Customer Service |

## Symptom

You are currently using Customer Service (CS) as compatibility scope in SAP S/4HANA on-premise edition. More information on compatibility scope in S/4HANA can be found in the following note 2269324. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

Customer Service (CS) provides Service Management functionality for planning, executing and billing service orders. CS is used for field service, in-house repair as well as service projects. It works in conjunction with Plant Maintenance (PM) functionality and provides integration to Resource Related Billing as well as Service Contracts. Customer Service (CS) will be replaced by S/4HANA Service. S/4HANA  Service will be the new state-of-the-art Service Management backend as part of SAP S/4HANA.

## Required and Recommended Action(s)

Customer Service (CS) in S/4HANA is intended as a bridge or interim solution, which allows you a stepwise system conversion from SAP ERP to SAP S/4HANA on-premise edition and SAP S/4HANA Service.

## Custom Code related information

S/4HANA Service is an all-new and own Service Management solution that comes with a new solution scope, processes, objects, and capabilities. At the same time, it also reuses selected functionalities of ERP PM in order to simplify a transformation from ERP CS.

As a rough guideline, master data focused objects (e.g. equipment, functional location, maintenance plans) are mainly reused from ERP PM. Service transactional data (e.g. service order and service contract) for the commercial and operational service execution in S/4HANA Service are based on new objects.

For customers with a high need of CS service order capabilities for service planning and execution (e.g. task lists), S/4HANA Service provides the capability 'Service with Advanced Execution' since the release SAP S/4HANA 2023. This process uses maintenance orders for service planning and execution and the Dynamic Item Processor (DIP) for resource-related quotation and billing. Please consider the notes linked below to understand limitations of S/4HANA Service in the different SAP S/4HANA releases.
