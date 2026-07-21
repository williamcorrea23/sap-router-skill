---
item_id: SI-2.40
title: "2.40 SWTL - Deprecation of Obsolete Data Handling Tool"
pages: 99-100
sap_notes: [2661837, 3335020, 3358954]
components: [CA-EPT-ODH, BC-CCM-ODH]
objects: []
---
## Application Components:CA-EPT-ODH, BC-CCM-ODH

Related Notes:

| Note Type           |   Note Number | Note Description                                    |
|---------------------|---------------|-----------------------------------------------------|
| Release Restriction |       3335020 | New Obsolete Data Handling Framework in SAP S/4HANA |
| Business Impact     |       3358954 | SWTL - Deprecation of Obsolete Data Handling Tool   |

## Symptom

You are doing an upgrade from a lower SAP S/4HANA release to release 2023 (or higher) and have been already using the obsolete data handling tool (report/transaction code ODH_Data_processing) in the past for deleting obsolete data that remains after the conversion of your system from SAP ERP to SAP S/4HANA 2023, or after a previous SAP S/4HANA upgrade. The following SAP S/4HANA Simplification Item is applicable in this case.

## Reason and Prerequisites

With SAP S/4HANA release 2023 a new obsolete data handling tool is delivered.

The old tool (report/transaction code ODH_Data_processing) is deprecated and can only be used with SAP S/4HANA release 2023 to view the logs of already finished cleaning runs.

We plan to make it obsolete in favor of the designated successor functionality as of release SAP S/4HANA 2025.

For more details on the old obsolete data handling tool, see SAP Note 2661837.

## Solution

All new obsolete data cleaning activity must be done with the new, class-based tool (transaction code SODH).

For information on how to enable and use this tool in the productive SAP S/4HANA 2023 system, see SAP Note 3335020.

## Other Terms

SAP S/4HANA, System Conversion, Upgrade, deprecation, ODH, ODH_Data_processing
