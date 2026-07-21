---
item_id: SI-3.13
title: "3.13 S4TWL - Migration of Business Partner Data specific to GST India"
pages: 145-146
sap_notes: [2285611, 2387589, 2421394, 2877717]
components: [XX-CSC-IN-SD, XX-CSC-IN-MM, XX-CSC-IN]
objects: [KNA1, LFA1]
---
Application Components:XX-CSC-IN-SD, XX-CSC-IN-MM, XX-CSC-IN

Related Notes:

| Note Type       |   Note Number | Note Description                                                                |
|-----------------|---------------|---------------------------------------------------------------------------------|
| Business Impact |       2877717 | GST IN: Tables J_1IMOVEND and J_1IMOCUST are not updated post S/4HANA migration |

## Symptom

CIN data isn't updated in tables J_1IMOCUST and J_1IMOVEND when BP is updated for customer and vendor role post S/4HANA migration.

## Reproducing the Issue

Go to transaction BP.

Save Vendor classification/Pan number data for vendor or customer role.

Go to tables J_1IMOCUST and J_1IMOVEND.

Fields Vendor classification/Pan number isn't updated with values.

## Cause

Customer or vendor master core data is completely integrated with Business Partner. The master data in the new transaction is being maintained in tables KNA1 and LFA1.

Fields from tables J_1IMOCUST and J_1IMOVEND are also migrated into tables KNA1 and LFA1 in S/4HANA system.

## Resolution

Implement the note '2285611 - BP Enhancements for CIN' and execute the transaction LOIN_CV_MD_MIG to migrate data from tables J_1IMOCUST and J_1IMOVEND into KNA1 and LFA1.

## See Also

2421394 - GST India: SAP ERP Solution Notes

2285611 - BP Enhancements for CIN

2387589 - BP Migration Report Log issue while processing huge number of records

## Keywords

GST, GST India, Master data, CIN, CIN data, S/4HANA, HANA, Migration, Upgrade, Conversion, XX-CSC-IN-MM, XX-CSC-IN-SD, XX-CSC-IN-FI, J_1IMOCUST, J_1IMOVEND, field, J_1IMOVEND-VEN_CLASS, vendor classification, PAN, J_1IPANNO, LFA1, KNA1, J_1IMOVEND-J_1IPANNO, J_1IEXCIVE.

## Environment

Sales And Distribution (SD)

Logistics Execution (LE)

SAP S/4HANA

This is relevant for India Localization or Country India version (CIN) component
