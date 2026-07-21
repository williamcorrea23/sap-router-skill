---
item_id: SI-2.29
title: "2.29 S4TWL - Change of Situation Types in Situation Handling"
pages: 69-71
sap_notes: [3271299, 3324958]
components: [CA-SIT]
objects: []
---
Application Components:CA-SIT

Related Notes:

| Note Type   | Note Number   | Note Description   |
|-------------|---------------|--------------------|

| Business Impact   | 3324958   | SIC for ZDM Upgrade Check in Situation Handling   |
|-------------------|-----------|---------------------------------------------------|

## Symptom

You execute a system conversion to S/4HANA, On-Premise - Edition 2023 or higher and are using the Situation Handling Framework - extended.

## Reason and Prerequisites

You use at least one of the following apps:

Manage Situation Types : Extended

Manage Situation Scenarios.

Manage Situation Objects

## Solution

The Simplification Item Check checks, if the requirements before the upgrade are met and all required SAP notes (currently SAP Note 3271299 ) have been implemented to ensure there is no concurrent access or attempt to write to the underlying tables during the data conversion.

If this is not the case the Software Update Manager (SUM) will be asking to install the required SAP notes before proceeding,

The checks performed by Simplification Item Check are

Check if any of the apps: Manage Situation Types- Extended, Manage Situation Scenarios or Manage Situation Objects  are active in the system. If this is not the case, the implementation of the Simplification Item Check is not required.

Check if the required SAP Note 3271299 is implemented in the system. The check is done by checking the availability of the interface

IF_SIT2_CHECK_ZDM_RUNNING that gets implemented by the SAP Note .

If the check is successful, it's ensured there is no concurrent access or attempt to write to the underlying tables during the data conversion and the Software Update Manager (SUM) can proceed with the system upgrade If the check is not successful, the SUM is aborted, and it cannot proceed with the system upgrade. SAP Note 3271299 needs to be implemented to proceed with the upgrade.

## Required and Recommended Action(s) :

After implementing the SIC (Simplification Item Check) : If the consistency check fails and the update in the Software Update Manager (SUM) is aborted, please implement the SAP Note 3271299 to ensure that all requirements before the upgrade are implemented and the system upgrade can happen properly.

## Other Terms

Situation Handling; Manage Situation Types - Extended; Manage Situation Scenarios , Manage Situation Objects
