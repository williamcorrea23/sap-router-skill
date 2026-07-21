---
item_id: SI-5.23
title: "5.23 S4TWL - Mark to Market Accounting Changes"
pages: 214-215
sap_notes: [2608098]
components: [LO-CMM-BF, LO-CMM-ANL]
objects: []
---
Application Components:LO-CMM-BF, LO-CMM-ANL

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                            |
|-----------------|---------------|-------------------------------------------------------------------------------------------------------------|
| Business Impact |       2608098 | S4 PreChecks: Conversion Report of Mark-to-Market Accounting for transition from Business Suite to S/4 HANA |

## Symptom

S4TC Pre-Transition Checks for Mark-to-Market Accounting returns following error messages:

"Action Required in client XXX: WBRP entries available for conversion exist. Migration cannot proceed without pre-conversion. See SAP Note 2608098."

## Reason and Prerequisites

Mark-to-Market(MtM) Accounting uses Agency Business (AB) as a vehicle to create and reverse accounting documents. Data base optimization in S/4 HANA are performed in AB.The pre-conversion report RCMM_MTM_CONVERSION from this note executes the obligatory conversion of data for already created AB documents with MtM references. The S4TC Pre-Transition Checks for Mark-to-Market Accounting has to be successful after the execution of the pre-conversion report RCMM_MTM_CONVERSION

## Solution

For source release SAP_APPL 618 implement this note. (Further releases up to and including S/4HANA 1709 FPS1 are added here to keep the report version in sync.)

For all conversions, run the report RCMM_MTM_CONVERSION in the source system in execution mode using the check box. Do this for each client indicated in the error messages.

## Other Terms

S/4 HANA migration, Pre-Checks, LO-CMM, Conversion Report, Markt-to-Market Accounting
