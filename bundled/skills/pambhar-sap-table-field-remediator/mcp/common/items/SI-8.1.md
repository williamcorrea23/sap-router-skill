---
item_id: SI-8.1
title: "8.1 S4TWL - DMEE"
pages: 236-239
sap_notes: [3370503, 3435447, 3452702, 3515844]
components: [CA-GTF-CSC-DME]
objects: []
---
Application Components:CA-GTF-CSC-DME

Related Notes:

| Note Type   | Note Number   | Note Description   |
|-------------|---------------|--------------------|

| Business Impact   | 3370503   | S4TWL - DMEE   |
|-------------------|-----------|----------------|

## Symptom

You are converting to SAP S/4HANA or upgrading from a lower to a higher SAP S/4HANA release and are using the DMEE transaction. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Business Value

SAP has decided to replace legacy solution DMEE (Data Medium Exchange Engine) with the DMEEX (Data Medium Exchange Engine eXtended).

DMEEX delivers following new capabilities for the end-user:

| Faster processing of output files                                            | https://blogs.sap.com/2021/02/09/performance- acceleration-in-dmeex/   |
|------------------------------------------------------------------------------|------------------------------------------------------------------------|
| Format Trees delivered in hierarchy (standard - country - customer specific) | https://blogs.sap.com/2018/09/21/mass-synchronization-in- dmeex/       |
| Synchronization of Format Trees to be up to date with standard               | https://blogs.sap.com/2018/09/21/mass-synchronization-in- dmeex/       |
| Calculations and variables                                                   | https://blogs.sap.com/2018/12/11/calculations-in-dmeex/                |
| New syntax checks to ensure consistency of the format tree                   |                                                                        |
| Removing empty elements from XML file as native functionality                |                                                                        |

Apart from these, there are many improvements in conditions, faster UI, improved test tool and more. DMEEX is regularly updated with new features.

## Description

To learn about business features, please refer to Business Value section above.

## Business Process related information

DMEE consists of two main logical parts configuration and runtime.

Configuration is when you define a new or modify an existing format tree to comply with the requirements of your bank, financial institution or public administration institutions.

From SAP S/4HANA 2025, configuration of format trees in the outgoing direction (file

## generation) will no longer be possible in DMEE.

Configuration will be available only via DMEEX. Once a DMEE tree is opened in DMEEX transaction the Migration Assistant will start and guide you through the migration process.

Runtime is when the format tree is interpreted and filled with data to generate the output file.

For all existing customer format trees in DMEE the runtime phase will remain intact in SAP S/4HANA 2025. There will be no "Day one impact" for customer format trees. Some SAP delivered format trees will be deleted in SAP S/4HANA 2025. There will be "Day one impact" and your action is necessary if you are using those format trees. See SAP Note 3515844 (DMEE - format trees obsolete from release 2025) for more information.

All existing custom code integrations will remain functional after SAP S/4HANA 2025 regardless of whether DMEE or DMEEX is used. However, when a change is required for a DMEE tree, such tree will have to be migrated to the DMEEX.

The current plan is to obsolete the runtime part of DMEE from SAP S/4HANA 2029 . This means that migration to DMEEX will be necessary to ensure that the business process remains functional.

## Required and Recommended Action(s)

IMPORTANT: To simplify the migration process and to detect potential problems, implement SAP Note 3435447 before migrating your format tree.

To migrate a format tree from DMEE to DMEEX, open your DMEE tree in the DMEEX transaction and confirm the migration pop-up. Testing the format tree after migration is strongly recommended.

There is no need to migrate all your existing trees at once. More realistic option is to migrate when a certain change to an existing format tree is required. Usually, testing of such changed format tree would happen anyway.

After starting the migration in DMEEX, some syntax errors will usually appear in the error log. These are caused by more rigorous syntax checks that control the consistency of your format tree. Fixing these syntax checks shall, in typical situations, take only few minutes.

Please note: After you migrate from DMEE to DMEEX then the SAP S/4HANA  Simplification Item S4TWL - DMEE_BADI_01 (3452702) may become relevant for you.

How to Determine Relevancy You are using custom DMEE format trees to generate output files (payment formats, statutory reports etc.).

Version 1 - 2: Initial release.

Version 3: Added information about plan to obsolete the runtime part of DMEE from SAP S/4HANA 2029.

Version 4: Added information about possible relevance of SAP S/4HANA Simplification Item S4TWL - DMEE_BADI_01 (3452702).

Version 5: Minor text changes.

Version 6: Added information about obsolete format trees (note 3515844).

Version 7: Added information about the enhanced migration process (note 3435447).

Version 8: Minor text changes.

## Other Terms

SAP S/4HANA, System Conversion, Upgrade, deprecation, DMEE, DMEEX, DMEE to DMEEX migration
