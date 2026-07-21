---
item_id: SI-3.23
title: "3.23 S4TWL - Simplification of copy/reference handling"
pages: 171-173
sap_notes: [2206932, 2323185, 2324325, 2330063]
components: [LO-MD-MM]
objects: []
---
Application Components:LO-MD-MM

Related Notes:

| Note Type       |   Note Number | Note Description                                  |
|-----------------|---------------|---------------------------------------------------|
| Business Impact |       2330063 | S4TWL - Simplification of copy/reference handling |

## Symptom

During the preparation of the migration to an S/4 system, the preliminary checks return either an error or a warning with the check ID

SAP_APPL_LO_MD_MM_T130F_CHECK. The error message indicates that the table T130F contains entries that are either not yet included in the table T130F_C or that have differing contents.

In an S/4HANA system, the entries delivered by SAP can no longer be adjusted customer-specifically, with the result that deviating settings are overwritten with the SAP delivery settings during an upgrade. To prevent any customer-specific settings in T130F for the copy control being replaced in the material master and the article master, an SAP S/4HANA system Release 1610 or higher contains an additional Customizing table T130F_C. This allows alternative maintenance of the copy control to the SAP delivery. The settings in T130F_C are then taken into account during the maintenance of material master and article master data.

Therefore, all entries from the table T130F that are relevant for the copy control must be copied to the new table T130F_C, and their field contents must be identical.

If the precheck issues a warning message, it may be the case that the fields relevant for copying control from T130F have to be copied to the new table T130F_C. However, it is only necessary to copy the entries if the S/4HANA target release is higher than or equal to SAP S/4HANA 1610. In this case, it is advisable to migrate the entries from T130F to the table T130F_C to when the warning appears, as described in the "Solution" section. Otherwise the system will later issue an error message during the migration phase when you execute the precheck because the system only then contains the information concerning the S/4HANA target release to which the data is migrated. To proceed further, you must then first carry out the data migration.

If the S/4HANA target release is equal to SAP S/4HANA 1511, the system only issues a warning during the migration phase because the new table does not exist in this release. In this case, proceed with the migration process.

If you use an SAP ERP for Retail system that requires at least the S/4HANA target release version SAP S/4HANA 1610, the system issues an error message at all times if the precheck determines inconsistencies. The data migration must be carried out in any case.

## Reason and Prerequisites

You want to migrate an SAP ERP system to an S4 system Release SAP S/4HANA 1610.

## Solution

## Business value

The information provided in this Simplification Item ensure that customer-specific settings referring to the copy control of fields in the product master are still available after the migration to S/4HANA. This means that the copy control in S/4HANA will work in the same way as before the migration. The changes explained above under "Symptom" are necessary to define the 'Virtual Data Model' (VDM), which is needed for the new SAP Fiori application.

## Description

In SAP S/4HANA, the table type of the table T130F has been changed so that the entries delivered by SAP can no longer be changed in a customer system without a modification. It is simply possible to create new, customer-specific entries in customer namespaces predefined especially for the purpose. However, since some of the fields in T130F control the copy behavior during the creation of products, and in Retail also when you change them, these settings should be retained during a migration. For this purpose, the relevant fields of T130F must be copied beforehand to a new Customizing table T130F_C so that these settings can continue to be defined customer-specifically.

## Required and recommended actions

Execute the migration precheck.

Implement the report RMMT130F_CPY in your SAP ERP system with the aid of SAP Note 2323185. In addition, you must implement the new table T130F_C in your system based on the correction instructions in SAP Note 2324325.

Execute the report with the standard settings. If entries are to be migrated, remove the indicator for the test mode on the initial screen and execute the report again. Check the messages output to establish whether the entries in all clients have been migrated successfully.

## Related SAP Notes

| Migration precheck   | SAP Note: 2206932          |
|----------------------|----------------------------|
| Migration report     | SAP Note: 2323185, 2324325 |

## Other Terms

SAP_APPL_LO_MD_MM_T130F_CHECK S4 T130F field control
