---
item_id: SI-3.14
title: "3.14 S4TWL - MDG_MDC in Lama"
pages: 146-147
sap_notes: [2182725, 2442665]
components: [CA-MDG-CMP]
objects: []
---
Application Components:CA-MDG-CMP

Related Notes:

| Note Type       |   Note Number | Note Description                                           |
|-----------------|---------------|------------------------------------------------------------|
| Business Impact |       2442665 | S4TC MDG_MDC Master Check for S/4 System Conversion Checks |

## Symptom

Implementation of MDG_MDC check class for S/4 transformation checks as described in SAP note 2182725.

This note implements a "Precheck DIMP/LAMA upgrade to S/4 for MDC-M (Material Consolidation and Mass Change) in software component MDG_MDC."

## Reason and Prerequisites

If you upgrade master data material to S/4 it is recommended, to have no open process for material (MDG_MDC).

If you upgrade a system with long material number (LAMA) it is mandatory to finalize (activate or delete) all open processes (MDC) for materials, else you have to delete open processes manually after upgrade.

Also it is suggested to have no open imports or process drafts.

## Solution

Implement the technical prerequisites for the S/4 transformation checks via this note. The note checks for active processes for materials.

## Other Terms

S4TC

MDG_MDC

MDG-C
