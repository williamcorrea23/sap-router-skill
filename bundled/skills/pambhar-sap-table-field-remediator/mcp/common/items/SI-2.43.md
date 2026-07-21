---
item_id: SI-2.43
title: "2.43 S4TWL - OUTPUT MANAGEMENT"
pages: 103-105
sap_notes: [2228611, 2470711]
components: [CA-GTF-OC]
objects: []
---
## Application Components:CA-GTF-OC

Related Notes:

| Note Type       |   Note Number | Note Description          |
|-----------------|---------------|---------------------------|
| Business Impact |       2470711 | S4TWL - OUTPUT MANAGEMENT |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

## Renovation

## Solution

## Business Value

SAP S/4HANA output management is a modern solution for output related tasks. It takes the functionality from existing SAP output solutions and adds additional features like seamless integration into Fiori apps, flexible email configuration and email templates as well as the support of SAP Cloud Platform Forms by Adobe.

## Description

SAP S/4HANA output management comes as an optional part of SAP S/4HANA. There are no mandatory actions for customers using this framework. All existing output management solutions like SD Output Control, FI Correspondence, FI-CA Print Workbench, and CRM Post-Processing are still supported. There are currently no plans to deprecate any of these solutions.

## Business Process Related Information

Business processes can benefit from one common output management solution across the product. Users always have the same look and feel and functionality, no matter if they perform output related tasks in Logistics, Procurement, or Financials. Also, an administrator only needs to setup and configure one output management framework. The SAP S/4HANA output management also offers at many places integration to standard extensibility, allowing business users to extend the solution without the need for an implementation project.

## Required and Recommended Action(s)

Business applications that already adopted to SAP S/4HANA output management should offer a switch to enable or disable the use of it.

Required actions for all business applications in scope:

Define the active output management framework for the individual business applications.

Open the customizing activity 'Manage Application Object Type Activation' under SAP Reference IMG -> Cross-Application Components -> Output Control.

Set the desired value in the column Status for all available Application Object Types by either changing an existing entry or by adding new entries.

All Application Object Types not listed in this customizing activity should have linked their corresponding simplicification item to SAP Note 2228611 providing individual information on how to enable or disable SAP S/4HANA output management. Please check the list of SAP Notes under section 'References' in this note.

If a business application is not listed in the customizing activity and has no simplification item or does not mention any changes regarding output management in its existing simplification item, it is likely not using SAP S/4HANA output management.

In case SAP S/4HANA output management is enabled, please refer to the SAP Note 2228611 for more information and related notes for the technical setup and configuration.

In case SAP S/4HANA output management is not enabled or disabled, please setup the according other output management solution for the particular business application.

## How to Determine Relevancy

The SAP S/4HANA output management might be relevant for you if:

The existing functionality described in SAP Note 2228611 fully meets your business requirements. According limitations / differentiations are listed in this note and linked subsequent SAP Notes. Additional functionality for SAP S/4HANA output management will only be delivered within a new release of SAP S/4HANA.

You want to use SAP delivered Fiori apps including output functionality.

The business applications of your business scope already adopted to SAP S/4HANA output management allowing the use of one output framework along the business processes.

The SAP S/4HANA output management might not be relevant for you if:

You want to continue using your existing output management setup in SAP S/4HANA.

You require functionality that is not covered by SAP S/4HANA output management.

Other Terms OM, Output Management, Output Control
