---
item_id: SI-2.14
title: "2.14 ABAPTWL - Dual Stack not supported"
pages: 44-45
sap_notes: [2560791]
components: [BC-CST]
objects: []
---
Application Components:BC-CST

Related Notes:

| Note Type       |   Note Number | Note Description                                        |
|-----------------|---------------|---------------------------------------------------------|
| Business Impact |       2560791 | Kernel for S/4 HANA does not support Dual Stack Systems |

## Symptom

Starting with S/4HANA release 1809, which corresponds to SAP Kernel version 7.73, the Dual Stack system setup is no longer supported.

## Reason and Prerequisites

S/4HANA release 1809 and later does not support a dual stack system setup.

Kernel 7.73 and following are not compatible with earlier versions of the SAP kernel.

## Solution

Do not use a kernel version >= 7.73 with a dual-stack system. For systems with dualstack setup, a SAP Kernel with a version <= 7.53 has to be used.

If you need to migrate a dual-stack system to a release >= 1809, which corresponds to SAP Kernel version 7.73, you have to split the system into Java and ABAP parts befrore the upgrade. The Software Provisioning Manager (SWPM) offers such a migration option.

## Other Terms

Dual Stack, AS Java
