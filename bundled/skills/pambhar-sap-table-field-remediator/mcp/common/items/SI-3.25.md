---
item_id: SI-3.25
title: "3.25 S4TWL - MRP fields in Material Master"
pages: 174-178
sap_notes: [2224371, 2267246]
components: [LO-MD-MM]
objects: []
---
## Application Components:LO-MD-MM

Related Notes:

| Note Type       |   Note Number | Note Description                              |
|-----------------|---------------|-----------------------------------------------|
| Business Impact |       2267246 | S4TWL - MRP fields in Material/Article Master |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Simplification: MRP fields in Material Master in MM01/02/03

The SAP S/4HANA simplification is done on the following tabs in transaction MM01/02/03 .

Lot Size data in MRP1 Tab:

Unit of Measure Group (MARC-MEGRU)

Procurement in MRP2: MRP considers quota arrangements always, henceforth it is not required to switch it on in the material master.

Quota arr. usage.  (MARC-USEQU)

BOM explosion /dependent Requirement tab in MRP4

Selection Method (MARC-ALTSL)

Repetitive manufacturing /assembly /deployment strategy tab of MRP4

Action control (MARC-MDACH)

This field is made available from SAP S/4HANA 2020. However, there is no action required and no impact of existing data.

fair share rule (MARC-DPLFS)

push distribution (MARC-DPLPU)

Deployment horizon. (MARC-DPLHO)

Storage Location in MRP4

SLoc MRP indicator (MARD-DISKZ)

spec.proc.type SLoc (MARD-LSOBS)

## Reoder Point (MARD-LMINB)

## Replenishment qty. (MARD-LBSTF)

Also the backend database fields for these "omitted functionality" remains existing in the system.

## Simplification: MRP fields in Article Master in MM41/42/43

The SAP S/4HANA simplification is done on the following tabs/views in transaction MM41/42/43 .

Screen "Procurement" in views "MRP/Forecast Data: DC" and "MRP/Forecast Data: Store", screen "General plant parameters" in views "Other Logistics Data: DC" and "Other Logistics Data: Store"

Quota arr. usage.  (MARC-USEQU)

Screen "Repetitive manufacturing/assembly" in views "MRP/Forecast Data: DC", "Logistics: DC 2" and "MRP/Forecast Data: Store"

## Action control (MARC-MDACH)

This field is made available from SAP S/4HANA 2020. However, there is no action required and no impact of existing data.

Screen "BOM explosion/dependent requirements" in views "MRP/Forecast Data: DC", "Logistics: DC 2" and "MRP/Forecast Data: Store"

## Selection Method (MARC-ALTSL)

Screen "Storage location MRP" in views "MRP/Forecast Data: DC", "Logistics: DC 2" and "MRP/Forecast Data: Store"

SLoc MRP indicator (MARD-DISKZ)

spec.proc.type SLoc (MARD-LSOBS)

Reoder Point (MARD-LMINB)

Replenishment qty. (MARD-LBSTF)

Also the backend database fields for these "omitted functionality" remains existing in the system.

The retail customers do not need to adapt the usage of the fields MARC-MEGRU and MARC-MDACH (the field is made available from SAP S/4HANA 2020).

## Scheduling Margin Key

In S/4HANA, the scheduling margin key (field MARC-FHORI) is mandatory if defined in t-code OMSR. By default the scheduling margin key is not mandatory.

In ECC, the scheduling margin key (field MARC-FHORI) was mandatory if MRP Type was:

Not reorder point planning

Not time-phased planning

This was independent from the customizing in t-code OMSR.

## Reasons:

SAP strives to simplify material master maintenance in SAP S/4HANA. The scheduling margin key is not required for MRP in S/4HANA. If the scheduling margin key is not specified, then the floats before and after production will be zero as well as the opening period. Zero opening period means you should run the conversion of planned orders into production orders every day.

## Additional Information

For more information see simplification item in Production Planning 'Storage Location MRP'.

## Related SAP Notes

| General information about this Simplification Item   | SAP Note 2224371   |
|------------------------------------------------------|--------------------|
| MARC-MDACH                                           | MARC-MDACH         |

## Action control (MARC-MDACH)

This field is made available from SAP S/4HANA 2020. However, there is no action required and no impact of existing data.

fair share rule (MARC-DPLFS)

push distribution (MARC-DPLPU)

## Deployment horizon. (MARC-DPLHO)

## Other Terms

MRP, Simplification
