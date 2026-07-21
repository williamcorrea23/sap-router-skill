---
item_id: SI-2.46
title: "2.46 S4TWL - Duplicate request entries in Output Management"
pages: 108-109
sap_notes: [2679118]
components: [CA-GTF-OC]
objects: []
---
## Application Components:CA-GTF-OC

Related Notes:

| Note Type       |   Note Number | Note Description                                               |
|-----------------|---------------|----------------------------------------------------------------|
| Business Impact |       2679118 | Simplification item check for duplicate output request entries |

## Symptom

Upgrade to SAP S/4HANA 1809 On Premise release

## Reason and Prerequisites

SAP S/4HANA 1809 On Premise release introduces a new seconday key index to the following tables:

APOC_D_OR_ROOT

APOC_D_OR_ITEM

APOC_D_OR_ITEM_A

APOC_D_OR_ITEM_E

It is necessary to make sure that there are no multiple database entries in these tables that match with the new unique key. If there are any duplicate entries, the new seconday key index constraint cannot be added to the tables.

Therefore, to upgrade to SAP S/4HANA 1809 from any lower S/4HANA releases, the Simplification Item Check (SIC) has to be carried out to detect these duplicate entries. Once detected, duplicate entries are to be deleted from the tables to ensure a smooth upgrade.

## Solution

If there are duplicate entries (multiple entries in the database matching key constraints) in the following tables, the SIC will detect them:

APOC_D_OR_ROOT

APOC_D_OR_ITEM

APOC_D_OR_ITEM_A

APOC_D_OR_ITEM_E

Duplicate table entries detected by SIC must be deleted from their corresponding tables.

Please go to the table via transaction se16n. Enable &sap_edit. Filter the entries based on the key fields displayed by SIC.

You may now analyze the entries and delete the duplicate ones.
