---
item_id: SI-2.12
title: "2.12 ABAPTWL - VM Container not supported"
pages: 43-43
sap_notes: [2560708]
components: [BC-VMC]
objects: []
---
## Application Components:BC-VMC

Related Notes:

| Note Type       |   Note Number | Note Description                         |
|-----------------|---------------|------------------------------------------|
| Business Impact |       2560708 | Kernel for S/4 HANA does not support VMC |

## Symptom

Starting with S/4HANA release 1809, which corresponds to SAP Kernel version 7.73, the Virtual Machine Container (VMC) funtionality is no longer included.

## Reason and Prerequisites

S/4HANA release 1809 and later does not support Virtual Machine Container (VMC) functionality.

Kernel 7.73 and following are not compatible with earlier versions of the SAP kernel.

## Solution

Do not use a kernel version >= 7.73 with systems that require VMC functionality. For such systems, a SAP Kernel with a version <= 7.53 has to be used.

If you want to preserve Java functionality implemented on the VMC, you have to migrate it to a standalone Java program or Java container, like SAP Application Server Java.

## Other Terms

VMC
