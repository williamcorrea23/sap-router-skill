---
item_id: SI-2.21
title: "2.21 S4TWL - Custom Fields"
pages: 53-55
sap_notes: [2320132]
components: [BC-SRV-APS-EXT-FLD]
objects: []
---
Application Components:BC-SRV-APS-EXT-FLD

Related Notes:

| Note Type       |   Note Number | Note Description      |
|-----------------|---------------|-----------------------|
| Business Impact |       2320132 | S4TWL - Custom Fields |

## Symptom

You have done a system conversion to SAP S/4HANA. Now, the following item of the SAP S/4HANA transition worklist is applicable if you have extension fields and want to use them in:

SAP Fiori apps

CDS-based analytical reports

Adobe-based print forms

Email templates

OData services

## Reason and Prerequisites

You have set up the adaptation transport organizer. For more information, see Configuration Information: Adaptation Transport Organizer.

## Solution

## Description

With SAP S/4HANA, custom fields can be managed with the SAP Fiori app Custom Fields and Logic. This app, together with other SAP Fiori apps, can be used to add custom fields to OData services, CDS views, or SAP Fiori apps, for example.

## Business Process-Related Information

In the SAP GUI transaction SCFD_EUI, existing custom fields can be enabled for use in the app Custom Fields and Logic. In some cases, existing fields need to be prepared in advance.

For more information, see Enabling Custom Database Fields for Usage in SAP Fiori Applications.

## Required and Recommended Actions

Use the transaction SCFD_EUI to enable your existing custom fields for use in the app Custom Fields and Logic, and to see preperation steps, if necessary.

For more information, see Enabling Custom Database Fields for Usage in SAP Fiori Applications.

## Other Terms

Extension, Custom, Fields
