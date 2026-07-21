---
item_id: SI-2.25
title: "2.25 S4TWL - Changes in Process Observer"
pages: 61-64
sap_notes: [2412899, 2461687, 2879911]
components: [CA-EPT-POC]
objects: []
---
## Application Components:CA-EPT-POC

Related Notes:

| Note Type       |   Note Number | Note Description                                                              |
|-----------------|---------------|-------------------------------------------------------------------------------|
| Business Impact |       2412899 | Changes in Process Observer when moving from SAP Business Suite to S/4HANA OP |

## Symptom

A few changes occurred in the implementation of Process Observer in S/4HANA, which may affect you when moving from SAP Business Suite to S/4HANA OP version.

Business Function FND_EPT_PROC_ORCH_1 for Process Observer is always on

Improved IMG structure in S/4HANA

Name change for background job for event processing

Authorization check for maintaining process definitions enabled

Predecessor determination by document relationship browser (DRB) is off by default

## Solution

Business Function FND_EPT_PROC_ORCH_1:

In order to use Process Observer in S/4HANA, there is no need to activate FND_EPT_PROC_ORCH_1 any more, as it is set to 'always on' in the s/4HANA systems. The remaining steps to activate process observer is the:

activation setting: via IMG or transaction POC_ACTIVE

scheduling of background job for event processing: via IMG or transaction POC_JOB_SCHEDULER

Improved IMG structure for Process Observer:

Please see note 2461687 to find information about the changes to the IMG structure of Process Observer, and to relocate the activities.

Background job for event processing:

The name of the running background job for event processing was changed from 'POC_JOB_<client>' in SAP Business Suite to 'SAP_POC_PROCESS_EVENT_QUEUES'. This may be relevant, for example when managing the job via SM37.

Authorization check for maintaining process definitions:

The authorization check for maintaining process definitions via IMG or transaction POC_MODEL was not activated by default SAP Business Suite. In S/4HANA the authorization object POC_DEFN is checked when trying to create, change or delete process definitions. Make sure the corresponding user roles in S/4HANA contain this authorization object with the appropriate settings.

## 5) Predecessor determination via DRB:

In your SAP Business Suite implementation you may be relying on predecessor determination for events using DRB, if the following appies:

you are using BOR events for monitoring

different business object types are part of one process definition

you did not implement or configure a specific predecessor determination for your objects (like referencing an attribute in BOR event, or BAdI implementation)

In order to activate the predecessor determination via DRB again in S/4HANA do the following: enter the relevant BOR events in the follwing IMG activity:

<...> Process Observer - Application Instrumentation - BOR Event Instrumentation Enable Data Relationship Browser (DRB) Usage

## Other Terms

Process Performance Monitoring in S/4HANA

## 2.26 ABAP4TWL - Removal of Transceiver Integration

Application Components:CA

Related Notes:

| Note Type       |   Note Number | Note Description        |
|-----------------|---------------|-------------------------|
| Business Impact |       2879911 | Package BALI is missing |

## Symptom

The package BALI covering transceiver functionality of R/3 up-to release 6.10 is missing.

## Reason and Prerequisites

Transceiver functionality is discontinued.

## Solution

The transceiver functionality has been withdrawn and has been replaced with new interfaces, see SAP Note 176927.

## Other Terms

Programs CONFQMID, RCONFCC1, RCONFCC2, RCONFCC3, RCONFCC4, RCONFCC5, SAPBAL10, SAPCDUP1, SVCTKANA

Function group TRAR

Business object types IDOCCONF11, IDOCCONF21, IDOCCONF22, IDOCCONF31, IDOCCONF32, IDOC CONF41, IDOCCONF42

Workflow tasks TS00200089, TS00200090, TS00200096, TS00200097, TS00200098, TS00200099, TS00200101
