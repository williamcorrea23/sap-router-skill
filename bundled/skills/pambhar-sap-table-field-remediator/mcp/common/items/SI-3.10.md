---
item_id: SI-3.10
title: "3.10 S4TWL - BADI ADDRESS_SEARCH (Duplicate Check) is Not Supported in SAP S/4HANA"
pages: 141-142
sap_notes: [2416027]
components: [LO-MD-BP]
objects: []
---
Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                    |
|-----------------|---------------|-----------------------------------------------------------------------------------------------------|
| Business Impact |       2416027 | S4TWL - BAdI ADDRESS_SEARCH (Duplicate Check) Neither Certified Nor Supported for SAP S/4HANA Fiori |

## Symptom

You are doing a system converson to S/4HANA On Premise. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

The BAdI ADDRESS_SEARCH was not designed to meet the newer generation codings of  SAP S/4HANA which gets called in Fiori smart template apps such as Manage Customer Master, Manage Supplier Master and so on. When this BAdI is activated, the apps generate errors such as program termination, or run time exceptions occur.

## Solution

## Business Value

The BAdI ADDRESS_SEARCH is not compatible with the new generation code of SAP S/4HANA Fiori and hence it is neither certified nor supported.

## Description

The duplicate check using the BAdI ADDRESS_SEARCH to find dupliacte addresses is neither certified nor supported in SAP S/4HANA Fiori. The BAdI is available with the standard implementation and will be inactive. If there is a requirement to use the BAdI, it can be used for SAP GUI applications.

## Business Process related information

This BAdI was used to implement a check that identifies potentially duplicate addresses (in create and edit mode) and notifies the user. The user could decide whether the new account or contact is required or is in fact a duplicate of an existing account or contact. While not supporting this BAdI implementation for Fiori applications, SAP S/4HANA is in a conceptualize stage for a better solution for Fiori Apps.

## Required and Recommended Action(s)

Be informed that the BAdI ADDRESS_SEARCH for duplicate check is no more certified and supported for Fiori Apps.

## How to Determine Relevancy

This is relevant for all SAP S/4HANA customers.

## Other Terms

Duplicate Check, BAdI SIC_ADDRESS_SEARCH, BAdI ADDRESS_SEARCH
