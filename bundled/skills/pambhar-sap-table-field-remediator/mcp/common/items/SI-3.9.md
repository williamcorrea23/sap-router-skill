---
item_id: SI-3.9
title: "3.9 S4TWL - Business Partner BUT000/Header Level Time Dependency"
pages: 139-141
sap_notes: [1759416, 2379157]
components: [LO-MD-BP]
objects: []
---
Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                             |
|-----------------|---------------|--------------------------------------------------------------|
| Business Impact |       2379157 | S4TWL - Business Partner BUT000/Header Level Time Dependency |

## Symptom

You are doing a system conversion to SAP S/4HANA.The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

*** Note :  The attcahment of this note has been changed with a new report (Z_NTD_BUT000_NEW) on 2nd Jan,2018 to improve the performance . ***

## Business Value

Time dependency has been disabled at the header level of BUT000 in SAP S/4HANA to ensure that there are no inconsistencies in the master data.

## Description

The time dependency functionality in Business Partner is not supported in the header level (BUT000). Though the functionality is available through SPRO, SAP strongly recommends that the end user should NOT maintain the header level data using Customizing.

Customers who have activated time dependency in SAP ERP before the SAP S/4HANA system conversion or in the SAP S/4HANA, on-premise edition 1511 release, refer to the section Required and Recommended Action(s).

## Business Process Related Information

Switch-on and switch-off of the time dependency at BUT000 level will result in certain additional activities. For instance, switching OFF the table BUT000_TD converts the time dependent entries to time independent entries.

Once the BUT000_TD is ON, we can create time slice for central BP. The currently valid time slice will be stored in BUT000 table and the past/future time slice will be stored in BUT000_TD table.

When BUT000_TD is switched OFF:

If the BP had split validities in BUT000 and BUT000_TD tables, you will not be able to open or edit this BP.

The following error message appears:

'Data set BUT000 for BP 0000000XXX maintained time-dependently, despite inactive Time dep.' message appears (Hot News Note 1759416).

## Required and Recommended Action(s)

For customers who have not enabled time dependency:

Do not enable the time dependency at the header level (BUT000) using SPRO.

For customers who have enabled time dependency in releases prior to 1610/11:

You need to deactivate time dependency. It is a one-time process.

Run the report BUPTDTRANSMIT which will make BUT000 data up to date.

Run the report Z_NTD_BUT000_NEW attached with this Note. To run this:

Call up SE38.

Enter Z_NTD_BUT00_NEW and choose Create .

Choose type as Executable Program .

Paste the code content from the attachment.

Save, activate, and then execute the report.

This Z report will delete all the BUT000_TD entries (past and future entries) and extend the BUT000 entries (current entry) from 1.1.0001 to 31.12.9999 (which means loss of past/future data). Also , it will deactivate TD for BUT000 in V_TB056 view. Now you will not be able to maintain future/past entries for central BP.

## Notes :

The report Z_NTD_BUT000_NEW has a test run mode and BP range as the selection parameter.

## How to Determine Relevancy

This simplification item is relevant when time dependency is enabled for BUT000 at the header level. Meaning, the simplification item is relevant when DEV_ISACTIVE is X for development object (field DEVELOP) BUT000 (or) ALL_BP_TD in V_TB056 view. When the time dependency is enabled, BUT000_TD will have atleast one entry.

## Other Terms

Time dependency, BUT000, BUT000_TD, S/4HANA
