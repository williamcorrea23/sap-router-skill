---
item_id: SI-2.13
title: "2.13 ABAPTWL - AS Java not available"
pages: 43-44
sap_notes: [2560753]
components: [BC-JAS-SF]
objects: []
---
Application Components:BC-JAS-SF

Related Notes:

| Note Type       |   Note Number | Note Description                                         |
|-----------------|---------------|----------------------------------------------------------|
| Business Impact |       2560753 | Kernel for S/4 HANA cannot be used for NetWeaver AS Java |

## Symptom

Starting with SAP Kernel version 7.73 the NW AS Java is no longer supported.

## Reason and Prerequisites

S/4 HANA does not contain the NetWeaver Application Server Java (AS Java).

Kernel 7.73 and following are not compatible with earlier versions of the SAP kernel.

## Solution

Do not use a kernel version >= 7.73 with the NetWeaver AS Java.

## Other Terms

AS Java, J2EE
