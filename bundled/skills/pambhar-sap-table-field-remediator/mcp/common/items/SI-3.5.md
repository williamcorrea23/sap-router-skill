---
item_id: SI-3.5
title: "3.5 S4TWL - Object Identifier Type Code"
pages: 131-132
sap_notes: [2267294]
components: [CA-MDG-KM]
objects: []
---
Application Components:CA-MDG-KM

Related Notes:

| Note Type       |   Note Number | Note Description                    |
|-----------------|---------------|-------------------------------------|
| Business Impact |       2267294 | S4TWL - Object Identifier Type Code |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Description

The field NO_CONVERSION is not available in the definition of object identifier type codes (also known as scheme IDs - table MDGI_IDSTC_BS). Any existing usages have already been switched to non-conversion data elements in their key structures. In the "key mapping" IMG activity "Define Object Identifiers", the checkbox "No Conversion" was removed, as it was not considered any more.

## Business Process related information

No influence on business processes expected.

## Required and Recommended Action(s)

None
