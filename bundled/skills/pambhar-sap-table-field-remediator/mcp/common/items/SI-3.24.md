---
item_id: SI-3.24
title: "3.24 S4TWL - Foreign Trade fields in Material Master"
pages: 173-174
sap_notes: [2204534, 2267225, 2458666, 2641097]
components: [LO-MD-MM]
objects: []
---
Application Components:LO-MD-MM

Related Notes:

| Note Type       |   Note Number | Note Description                                |
|-----------------|---------------|-------------------------------------------------|
| Business Impact |       2267225 | S4TWL - Foreign Trade fields in Material Master |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## 1.1.1.1.1        Description

The Foreign Trade functionality as part of Sales & Distribution is not available within SAP S/4HANA Product Master Data, from on-premise edition 1511.  For more information see Simplification Item related to Foreign Trade in Sales & Distribution

The below mentioned fields for Letter of Credit/ Legal control/ Export control/ Preference management in Foreign Trade is not available through Material Master:

CAP product list no. (MARC-MOWNR)

CAP prod. group (MARC-MOGRU)

Preference status (MARC-PREFE)

Vendor   decl. status  (MARC-PRENE)

Validity date of vendor declaration (MARC-PRENG)

Exemption Certificate (MARC-PRENC)

Exemption Cert. No. 9 (MARC-PRENO)

Iss.date of ex.cert. (MARC-PREND)

Military goods (MARC-ITARK)

## 1.1.1.1.2        Related SAP Notes

| General information about this Simplification Item      | SAP Note 2204534   |
|---------------------------------------------------------|--------------------|
| Information about the report ZUPDATE_MARC_FOREIGN_TRADE | SAP Note 2458666   |

## Required and Recommended Action(s)

In case any of the fields listed above contain data, the simplification item check generates a skippable error (RC7). This indicates that the customer can request an exemption for this scenario after having acknowledged that the information provided in the description has been understood and, he can continue the conversion process without making changes to the data. The data in the above mentioned fields should be deleted in the postconversion phase before release of SAP S/4HANA to users .

Note: The skippable error RC7 is only available if your note 2641097 has been implemented.
