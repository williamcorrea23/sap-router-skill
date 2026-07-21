---
item_id: SI-2.38
title: "2.38 S4TWL - Extended Check of Output Device in Output Control"
pages: 95-97
sap_notes: [3057330, 3093397]
components: [CA-GTF-OC]
objects: []
---
Application Components:CA-GTF-OC

## Related Notes:

| Note Type       |   Note Number | Note Description                                          |
|-----------------|---------------|-----------------------------------------------------------|
| Business Impact |       3093397 | S4TWL - Extended Check of Output Device in Output Control |

## Symptom

You upgrade to SAP S/4HANA 2021 release and use SAP S/4HANA output control as output solution.

## Reason and Prerequisites

In the SAP S/4HANA 2021 release, the output solution SAP S/4HANA output control introduces an enhanced check for output devices defined within the spool administration, which are used for printing of output request items.

This simplification item is relevant for you if there already exist output control items for channel PRINT which should be still processed after the upgrade (e.g. as the status is 'In Preparation', etc.). If such an output control item uses an output device with now invalidated settings, any output action fails after the upgrade to SAP S/4HANA 2021. Refer to note 3057330 for details on the enhanced check.

## Solution

## Business Process related information

Talking about output devices, it is worth mentioning two points in advance:

Output devices are defined cross-client, i.e. a change in spool administration immediately affects all working clients

Output devices are used of course not only in output control, but within the complete business suite, and a change in spool administration does affect the complete business suite

## Required and Recommended Action(s)

To securely upgrade to SAP S/4HANA 2021 from any lower SAP S/4HANA release, the Simplification Item Check (SIC) has to be carried out to detect such invalidated output devices. Once detected, depending on your business data (see bullet points above), there are two possibilities to ensure a smooth upgrade:

Adapt the detected output devices in spool administration Create new output devices and exchange the detected output devices for relevant output request items (transaction data) and printer settings (configuration data)

For details refer to note 3057330.

Please notice that all errors of this simplificaction item are skippable, e.g. because the detected output control items are outdated, or in a state that there will be no further processing, or in a non-relevant client. Another option could be to accept the fact, that some output control items of channel PRINT will run into the output device error after the upgrade and to treat these cases manually. This could come in handy if there is only a low number of detected output control items.

However, especially if the findings point to a structural problem, i.e. an output device became invalid which is heavily used within relevant output control items through all working clients, it is highly recommended, to become active before the upgrade.

## Other Terms

SAP S/4HANA output control, Printing, Print Device, Printing Device, Device Type, CLS4SIC_APOC_CHK_ITEM_DEVICE, S4SIC_APOC_CHK_OPD_DEV
