---
item_id: SI-2.10
title: "2.10 ABAPTWL - SSCR license key procedure is no longer supported"
pages: 40-41
sap_notes: [2309060]
components: [BC-ABA-LA]
objects: []
---
## Application Components:BC-ABA-LA

Related Notes:

| Note Type       |   Note Number | Note Description                                                |
|-----------------|---------------|-----------------------------------------------------------------|
| Business Impact |       2309060 | The SSCR license key procedure is not supported in SAP S/4 HANA |

## Symptom

You have developer authorization and use ABAP development tools, but the SSCR license key request is not shown.

## Reason and Prerequisites

Your system is either any of the SAP S/4HANA on premise system variants, starting with S/4HANA 1511, or any of the SAP BW/4HANA variants. The SSCR license key procedure is not implemented in S/4HANA or BW/4HANA.

Depending on your task and question you may proceed as outlined in the solution section of this SAP Note.

## Solution

## Q1 - Is it possible to activate SSCR license key?

The SSCR license key functionality is activated and deactivated by the product.

## Q2 - What feature substitute the control mechanism of SSCR Keys?

SSCR keys are no control mechanism of ABAP content. They are a licensing feature for some older products, but not for S/4HANA.

## Q3 - How is it possible to control development?

To keep control over development is multi-step approach.

You define changeability of SAP system by transaction SE06. You reach this setting by the button "System Change Option" in the toolbar of transaction SE06.

You define client specific behavior for development by transaction SCC4 'Clients: Overview'.

Developers getting to SAP delivered artifacts, receive message TR852 or are blocked, depending on above settings.

Furthermore, you should assign developer permissions (authorization objects S_TRANSPRT and S_DEVELOP) carefully. I.e. tailored to the organization of your development projects by using the authorization fields DEVCLASS, OBJTYPE, OBJNAME, P_GROUP, and ACTVT of S_DEVELOP.

## Q4 - How can I monitor, what SAP code has been changed?

Changes on SAP ABAP software can be found in transaction SE95.

## Q5 - Is there a difference between modification and correction instruction?

The ABAP development tools do not distinguish the reason for change. From software lifecycle every change on originally delivered version must be adjusted when new software version is implemented. The reason for the change is not relevant for the authority check.

## Other Terms

SAP S/4HANA, SSCR key, Developer key, Access key, object key , modification
