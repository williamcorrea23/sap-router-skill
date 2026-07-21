---
item_id: SI-3.17
title: "3.17 S4TWL - Removal of Gender Domain Fixed Values"
pages: 149-152
sap_notes: [2928897]
components: [LO-MD-BP, BC-SRV-ADR, BC-SRV-BP]
objects: []
---
Application Components:LO-MD-BP, BC-SRV-ADR, BC-SRV-BP

Related Notes:

| Note Type   | Note Number   | Note Description   |
|-------------|---------------|--------------------|

| Business Impact   | 2928897   | S4TWL - Removal of Gender Domain Fixed Values   |
|-------------------|-----------|-------------------------------------------------|

## Symptom

You are doing a system conversion to SAP S/4HANA. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

Support for new gender codes in SAP Business Partner, Business Address Services, Customer and Supplier Master

## Solution

## Description

You are looking to maintain additional gender values such as Neutral or Diverse in SAP Business Partner (BP). It was not possible to maintain gender values other than Male, Female and Unknown in a Business Partner so far. With S/4HANA On-premise 2020, in addition to the existing values Male, Female and Unknown, two new gender values are available in Business Partner master data:

Nonbinary - an identity other than male or female. For example, Divers in Germany. Not specified - any identity with legal rights; but chooses not to specify the gender

Further details are available in SAP Help documentation for S/4HANA 2020.

To support new gender codes, the existing fixed values for gender related domains in Business Partner data model have been replaced with new value tables. These value tables will hold gender codes Male, Female and Unknown (existing from older releases) and new gender codes Nonbinary and Not specified (new from S/4HANA 2020)

## Business Value

SAP Business Partner now provides a possibility to maintain gender codes other than Male and Female maintainence.

## Business Process relation Information

All business processes which involve maintenance of Business Partner Master Data and in that specifically the Gender information for the Business Partner are affected. This includes primarily Business Partner maintenance via Transaction BP

Fiori Apps for Business Partner, Customer and Supplier maintenance

Supported external interfaces for like oData, SOAP, iDocs

Released APIs

SAP delivered business processes have been adjusted to make use of new value tables for gender codes instead of domain fixed values. Further sections in this Note provide guidelines on relevancy and recommended actions for customer specific coding for Business Partner maintenance.

## Compatibility Considerations

To support the new gender codes, a new field GENDER has been introduced in Business Partner main table BUT000. This field will support all existing gender codes (Female, Male and Unknown) and new gender codes (Nonbinary and Not Specified). To ensure compatibility, old fields XSEXF, XSEXM and XSEXU from the table BUT000 will continue to be maintained with gender values when chosen gender value is Female, Male, or Unknown.

Similarly, a new field GENDER has been introduced in the interface structures and can be used to maintain all five gender codes. Existing field SEX will continue to support gender codes Female, Male or Unknown. Further details are available in the cookbook attached to this SAP Note.

## How to determine Relevancy

As Business Partner is one of the most fundamental business objects in S/4HANA and as there would invariably be Business Partner of type Person in any organization, this simplification item is relevant in most customer cases.

ABAP domains listed below have been changed to support additional gender codes.

| Domain   | Fixed Values Removed     | Replacement Value Table   |
|----------|--------------------------|---------------------------|
| BU_SEXID | Female, Male and Unknown | TB995                     |
| AD_SEX   | Female, Male and Unknown | TSAD15                    |
| SEXKZ    | Female, Male             | TSAD15                    |

If you have custom ABAP artefacts (screens, programs, classes etc.) for BP Maintenance referring to these domains, the changes are relevant for you.

## Required and Recommended actions

Attached PDF document titled 'Cookbook_GenderDomainChanges.pdf' describes in detail the how the custom adoption has to be done for the data model changes listed above.

## Other Terms

Business Partner Gender Code, Nonbinary, Divers, BU_SEXID, AD_SEX, SEXKZ
