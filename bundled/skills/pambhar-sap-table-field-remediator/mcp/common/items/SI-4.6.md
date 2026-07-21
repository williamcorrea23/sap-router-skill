---
item_id: SI-4.6
title: "4.6 S4TWL - CPM - Forecast from financial plan versions"
pages: 187-188
sap_notes: [2711002]
components: [CA-CPD, CA-CPD-FP]
objects: []
---
## Application Components:CA-CPD, CA-CPD-FP

Related Notes:

| Note Type       |   Note Number | Note Description                                    |
|-----------------|---------------|-----------------------------------------------------|
| Business Impact |       2711002 | S4TWL - CPM - Forecast from financial plan versions |

## Symptom

You are performing a system conversion of SAP Commercial Project Management 2.0 SP08 to SAP S/4HANA 1809 FPS01. The following SAP S/4HANA transition worklist item is applicable in this case.

## Solution

## Description

With SAP Commercial Project Management for SAP S/4HANA , the Forecast function which you can trigger for financial plan versions with various options is not available. Note that a functional equivalent is available.

## Required and Recommended Actions

Use transaction SE38 and execute the alternative program Mass Forecast and Transfer (/CPD/PFP_MASS_FORCAST_TRANSFER). This program enables you to perform in-period forecasting by selecting a cut-off date.

New KPIs (up to the cut-off date) which were available in SAP Customer Project Management 2.0 SP08 are calculated only if you select the forecast method Based on Actuals or With Constant EAC .

However, if you select the Based on Configuration option, the forecast program will calculate only KPIs that were made available in SAP S/4HANA 1809 FPS0. All additional KPIs that were delivered with SAP Commercial Project Management 2.0 SP08 will not be calculated or updated.

The configuration that is referred by this forecast method is available under Customizing for Commercial Project Management, under Project Cost and Revenue Planning à Define Plan Scenarios à Link Plan Scenario to Resource Types.

## Other Terms

In-period forecast with cut-off date, SAP Commercial Project Management, CA-CPD, S/4HANA,CA-CPD-FP,
