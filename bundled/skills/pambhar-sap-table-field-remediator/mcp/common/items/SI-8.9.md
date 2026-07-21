---
item_id: SI-8.9
title: "8.9 S4TWL -  Report Writer / Report Painter in Finance and Controlling"
pages: 265-267
sap_notes: [2269324, 2579584, 2993220, 2997574, 2999249, 3006586, 3572033]
components: [FI-GL-IS, FI-SL-IS, EC-PCA-IS, PS-IS, SD-IS, QM-QC-IS, PM-IS, PP-IS]
objects: []
---
Application Components:FI-GL-IS, FI-SL-IS, EC-PCA-IS, PS-IS, SD-IS, QM-QC-IS, PM-IS, PP-IS, CO-PC-IS, CO-OM-IS

Related Notes:

| Note Type       |   Note Number | Note Description                                                  |
|-----------------|---------------|-------------------------------------------------------------------|
| Business Impact |       2997574 | S4TWL - Report Writer / Report Painter in Finance and Controlling |

## Symptom

You are doing a system conversion from SAP ERP to SAP S/4HANA or an upgrade from a lower to a higher SAP S/4HANA release and are using the functionality described in this note. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Description

Report Writer and Report Painter are tools for creating reports that fulfil reporting requirements in Finance. The usage of Report Writer and Report Painter is partly included in the SAP S/4HANA compatibility scope, which comes with limited usage rights. For more details on the compatibility scope and it's expiry date and links to further information please refer to SAP note 2269324. In the compatibility matrix attached to SAP note 2269324, this topic is listed under the ID 433 - Reporting/Analytics in Finance and Controlling.

This note shall provide information on the restrictions that apply for Report Writer and Report Painter in SAP S/4HANA.

## Business Process related information

A general description of the functionality in compatibility scope you find in the SAP S/4HANA Feature Scope Description > section Report Writer and Report Painter: Usage in Finance.

Report Writer and Report Painter as tools are not part of compatibility scope, which means they will be available and supported beyond the compatibility scope expiry date. However, Report Writer / Painter libraries and respective reporting tables and reports for applications that are part of the compatibility scope will not be supported beyond expiry date. This applies to the following applications:

EC-PCA - Planning in classical profit center accounting (compatibility scope ID 427)

Cost of Sales ledger (compatibility scope ID 430)

Consolidation preparation - Closing Operations (compatibility scope ID 430)

Reporting for Product Cost Controlling based on KKBx tables

Custom-built reports and libraries will also not be support beyond expire date if they are based on reporting tables of the applications listed above. Refer to the attached document for detailed status description of the SAP delivered Report Writer libraries and related table structures and applications.

Please note that for Profit Center Accounting which was previously listed in this note only the planning functionality is part of compatibility packages. Actual values for Profit Center Accouting have been deprecated, but can still be used after expiry of compatiility packages. Because actual and plan data cannot be separated on library level, the respective report writer/painter reports are still available.

## Required and Recommended Action(s)

Which reporting capabilities you can use as alternative to Report Writer / Report Painter depends on the reporting strategies for the alternative applications of the functionalities in compatibility scope. Refer to the following notes and simplification items for further information.

Classical profit center accounting - note 2993220 (Plan) and 3572033 (actual)

Cost of Sales ledger - note 3006586

Consolidation preparation - Closing Operations - note 2999249

Reporting for Product Cost Controlling based on KKBx tables  - note 326525

General recommendations for financial reporting in SAP S/4HANA you find in note 2579584.

## Other Terms

SAP S/4HANA, Compatibility Scope, Compatibility Package, System Conversion, Upgrade, Report Painter, Report Writer, ID 433
