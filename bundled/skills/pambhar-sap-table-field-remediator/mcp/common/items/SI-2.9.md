---
item_id: SI-2.9
title: "2.9 ABAPTWL - Cleanup of orphaned objects"
pages: 39-40
sap_notes: [2190420, 2241080, 2672757]
components: [BC]
objects: []
---
Application Components:BC

Related Notes:

| Note Type       |   Note Number | Note Description                                    |
|-----------------|---------------|-----------------------------------------------------|
| Business Impact |       2672757 | Simplification of SAP_BASIS within SAP S/4HANA 1809 |

## Symptom

With SAP S/4HANA 1809 some technical features have been withdrawn, which are not available for SAP S/4HANA on-premise.

## Reason and Prerequisites

This SAP Note serves as a reference for SAP S/4HANA custom code checks (see SAP Notes 2190420, 2241080) related to some obsolete and orphaned objects which were deleted in SAP_BASIS 7.53.

The deleted objects do not belong to a specific, released functionality. Hence no functional impact of the deletion on customers is expected.

## Solution

Remove any usages of these deleted objects found by ABAP Test Cockpit in your custom code and replace them with equivalent objects in customer namespace.

## Other Terms

Conversion SAP ERP, SAP S/4HANA.
