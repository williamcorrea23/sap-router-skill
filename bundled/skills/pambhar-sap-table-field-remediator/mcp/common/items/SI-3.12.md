---
item_id: SI-3.12
title: "3.12 S4TWL - MDG in Lama"
pages: 144-145
sap_notes: [2182725, 2379272]
components: [CA-MDG]
objects: []
---
## Application Components:CA-MDG

Related Notes:

| Note Type       |   Note Number | Note Description                                            |
|-----------------|---------------|-------------------------------------------------------------|
| Business Impact |       2379272 | S4TC MDG_APPL Master Check for S/4 System Conversion Checks |

## Symptom

Implementation of MDG_APPL check class for S/4 transformation checks as described in SAP note 2182725.

This note implements a "Precheck DIMP/LAMA upgrade to S/4 for MDG-M (Material Governance) in software component SAP_APPL."

## Reason and Prerequisites

If you upgrade master data material to S/4 it is recommended, to have no open change request for material (MDG-M)

If you upgrade a system with long material number (LAMA) it is mandatory to finalize (activate or delete) all open change request creating new materials, else you have to delete open change requests creating new materials in LAMA system manually after upgrade.

This change requests can not processed any more after upgrade.

## Solution

Implement the technical prerequisites for the S/4 transformation checks via this note.

## Other Terms

S4TC

MDG_APPL

MDGM
