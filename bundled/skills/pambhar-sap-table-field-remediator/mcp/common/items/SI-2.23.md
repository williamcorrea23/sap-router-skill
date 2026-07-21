---
item_id: SI-2.23
title: "2.23 S4TWL - Changed Interfaces"
pages: 58-60
sap_notes: [2249880, 2259818, 2408693]
components: [XX-SER-REL]
objects: []
---
Application Components:XX-SER-REL

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                                                 |
|-----------------|---------------|----------------------------------------------------------------------------------------------------------------------------------|
| Business Impact |       2259818 | RFC enabled Function Modules with incompatible signature change compared to its version in ERP are blocked from external access. |

## Symptom

You are using SAP S/4HANA. Certain RFC enabled Function Modules have been blocked from external access using RFC Unified Connectivity Filter Services.

## Reason and Prerequisites

Many RFC Function Modules that were delivered with ERP, are now available in SAP S/4HANA delivering same functionality and services. RFC Function Modules can be categorized by their "Release"-Status: "Released" implies an RFC enabled Function Module can be called from any remote  SAP or non SAP Application. "Not Released" implies an RFC Function Module is not accessible by customer but can be called from any remote SAP application and hence used internally for cross application communication.

In SAP S/4HANA, some small percentage of RFC enabled Function Modules (with either "Released" and "Not Released" status) have had their signature modified in an incompatible way, compared to the signature of their version in ERP.  RFC enabled Function Module use memory copy to transfer parameters between the source and target in most cases and thus any incompatible change to the signature of the RFC enabled Function Module may lead to the target receiving incomplete or garbled data as parameter value.

Using these Function Modules across-system may harm the data integrity of your SAP S/4HANA System, since the caller might still use the old signature.

If all callers of such a Function Module have been explicitly adapted to the changed signature, and if there are no un-adapted calls from your landscape, then using such a module is possible.

If external non-SAP systems provided by 3rd parties want to use such a Function Module, then ask them explicitly, if they have adapted their coding to the new signatures.

Additionally, some RFC enabled Function Modules have been marked as "Obsolete" and hence they are also blocked from external access.

An RFC Enabled Function Module that has been blocked from external or remote access can be verified by remotely calling this RFC Enabled Function Module on your SAP S/4HANA system and receiving a short dump, as described in the note #2249880.

## Solution

## RFC blocklist

SAP uses a feature called RFC blocklist, whereby, those remote enabled function modules that need to be restricted from being called by external RFC Clients, are added a RFC blocklist object, which has the same identifity as a package. SAP releases one blocklist package per S/4HANA OP release. The names of the RFC blocklist packages are as follows:

## S/4HANA OP Release # | blocklist Package

S/4HANA OP 2023 | ABLMUCON2023

S/4HANA OP 2022 | ABLMUCON2022

S/4HANA OP 2021 | ABLMUCON2021

S/4HANA OP 2020 | ABLMUCON2020

S/4HANA OP 1909 | ABLMUCON1909

S/4HANA OP 1809 | ABLMUCON1809

S/4HANA OP 1709 | ABLMUCON1709

S/4HANA OP 1610 | ABLMUCON1610SP00

## View the contents of RFC blocklist

The RFC blocklist and its contents can be viewed from a program RS_RFC_BLACKLIST_COMPLETE. This program can be run on any S/4HANA OP instance. Upon executing this program you would be asked to provide the package name of the blocklist. For example, on an S/4HANA OP 1909 instance, provide the package name is ABLMUCON1909 & the names of blocklisted remote enabled Function Modules would appear in the result .

Applies to S/4HANA 1610 OP and above.

## Override the blocklist on your landscape

For any reason, you wish to unblock the access of any RFC enabled Function Module by an external RFC client, then please follow the instructions mentioned in the note #2408693.

## Other Terms

RFC UCON, RFC Unified Connectivity, Signature Incompatibility
