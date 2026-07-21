---
item_id: SI-3.20
title: "3.20 S4TWL - Reduction of Redundant Business Partner Data Storage in the 'BUTADRSEARC"
pages: 159-161
sap_notes: [2576961]
components: [LO-MD-BP]
objects: []
---
## Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                                                         |
|-----------------|---------------|------------------------------------------------------------------------------------------|
| Business Impact |       2576961 | S4TWL - Reduction of Redundant Business Partner Data Storage in the 'BUTADRSEARCH' Table |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

Renovation

## Solution

## Business Value

Fields BIRTHDT, AUGR, XDELE, XBLCK, TYPE, and REGION in table BUTADRSEARCH is no longer requried

as the redundancy of data storage is minimized in SAP S/4HANA.

## Description

Fields BIRTHDT, AUGRP, XDELE, XBLCK, TYPE, and REGION  were updated in BUTADRSEARCH if the indexing was activated in TB300 table.In S4/HANA this is no longer requried as we plan to phase this out to avoid redundant data storage.However these fields will be maintained in the respective table listed below.

BUT000-BIRTHDT

BUT000-AUGRP

BUT000-XDELE

BUT000-XBLCK

BUT000-TYPE

ADRC-REGION

## Business Process related information

No further development is planned.We instead plan to phase this out to avoid redundant data storage.

## Required and Recommended Action(s)

Be informed that the redundant storage of 'Business Partner' data in BUTADRSEARCH is only kept for compatibility reasons (customers doing a conversion that have already activated this indexing) and must not be activated by new customers.

How to Determine Relevancy This simplification list item is releavent if  TB300-ADDRSRCH_ACTIVE = 'X'  which means the indexing is activated.

## Other Terms

'BUTADRSEARCH', 'TB300'
