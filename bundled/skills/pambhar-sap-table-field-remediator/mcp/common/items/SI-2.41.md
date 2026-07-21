---
item_id: SI-2.41
title: "2.41 S4TWL - CATSXT"
pages: 100-101
sap_notes: [3150537, 3445075, 3445096]
components: [CA-TS-SV]
objects: []
---
## Application Components:CA-TS-SV

Related Notes:

| Note Type       |   Note Number | Note Description   |
|-----------------|---------------|--------------------|
| Business Impact |       3150537 | S4TWL - CATSXT     |

## Symptom

You are using the functionality 'Cross Application - Time Sheet Service Provider' (CATSXT) in release SAP S/4HANA on-premise 2022 or lower. The functionality was declared deprecated with SAP S/4HANA 2022 and set to obsolete with SAP S/4HANA 2023.

## Reason and Prerequisites

CATSXT was a special development for the service provider industry introduced already with SAP R/3. It was not released for non-service provider industry customers and regarded non-strategic even for service provider customers. Please refer to SAP note 304647. Therefore, the functionality was declared deprecated with SAP S/4HANA 2022 and set to obsolete with SAP S/4HANA 2023.

## Solution

## Description

As of SAP S/4HANA release 2023 the functionality cannot be used anymore. Please also refer to SAP Help Documentation. If you are not using CATSXT, there are no further actions.

If this functionality is still used and required, the capabilities of Fiori Apps 'My Timesheet' version 4 (App ID F307A) and 'Approve Timesheets' version 4 (App ID F2585A) can be explored as an alternative. With 'Assignment Group' in the Fiori App 'My Timesheet' version 4, a similar possibility as in CATSXT is provided, to enter for example consulting time, travel time, distance travelled and flag for travel per-diem in a single screen. Furthermore, the functionality 'Assignment Groups' allows employees to create a collection of saved assignments that individually cover for example maintaining the aforementioned information. Version 4 of the Fiori App 'My Timesheet' is available as of Q1/2024. Please refer to the SAP Roadmap Explorer and SAP Notes 3445096

(Approve Timesheets Version 4: Release Information) and 3445075 (My Timesheet Version 4: Release Information).

There is also Cross-Application Time Sheet (CATS) available, which is a crossapplication tool for recording working times and tasks. These functionalities and apps are based on CAT2 and CATSDB.

In general, CAT2 and CATSDB related transactions (Fiori and WebDynpro ABAP) will continue to be supported as per SAP S/4HANA timelines.

## Business Process related information

| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | CATSXC          |
|-----------------------------------------------------------------------|-----------------|
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | CATSXC_CHECK    |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | CATSXC_COMP_DTL |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | CATSXT          |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | CATSXT_ADMIN    |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_AL0_96000015  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100621  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100718  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100771  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100775  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100776  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100782  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_ALR_87100834  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_P00_07000122  |
| Transactions not available in SAP S/4HANA on-premise 2023 or higher   | S_P00_07000322  |

## Other Terms

CA-TS-SV, CATSXC, CATSXT, CATSXT_ADMIN, CATSXT_COMP_DTL,

S4TWL: S/4 HANA Transition Worklist Item.
