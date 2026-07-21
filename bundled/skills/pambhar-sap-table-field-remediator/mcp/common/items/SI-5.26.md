---
item_id: SI-5.26
title: "5.26 S4TWL - Simplified Commodity Pricing Engine Data Model"
pages: 219-222
sap_notes: [3203753, 3207069]
components: [CA-GTF-CPE]
objects: []
---
## Application Components:CA-GTF-CPE

Related Notes:

| Note Type           |   Note Number | Note Description                                           |
|---------------------|---------------|------------------------------------------------------------|
| Release Restriction |       3207069 | Migration Process for Optimized CPE Database Model         |
| Business Impact     |       3203753 | S4TWL - Simplified Commodity Pricing Engine Database Model |

## Symptom

You plan a system conversion from SAP ERP to SAP S/4HANA, on-premise edition or an upgrade from a lower to a higher SAP S/4HANA release. The following SAP S/4HANA Simplification Item is applicable in this case.

## Solution

## Historical Background:

The development of the existing CPE architecture started 15 years ago, pointing to relational databases. The CPE database architecture was designed in a way that CPE object artefacts have been stored in application tables only in case that other data sources (customizing) where unavailable. Therefore, a huge amount of data were accessed on the fly during the pricing process.

This approach required several tables with different keys for the same CPE object type (formula, terms, conversions etc.), which were accessed each time an object were processed, even when the object wasn't changed by the user.

For accessing the objects, 'internal buffers' were used. Each CPE object had several, different buffers.

This apporach would greatly reduce the effort when developing future Fiori applications such as for Central Purchase Contract, Sourcing Projects & Supplier Quotations, etc based on RAP or BOPF.

Also, a mass data processing and the handling with documents with a high-complex pricing hierarchy would have a negative impact on the performance.

Change Reason:

The new database architecture can be used in a simple way for BOPF- and RAP-based developments and improves the CPE pricing performance.

In addition, the new architecture solves the problem that customizing entities, which are not stored in application tables, can be changed during the lifetime of a document.

## Summary of Changes:

Simplified data model: Each CPE object (formula, terms and so on) will have just one table. No changes in functional level and minimal changes to consuming SAP components. Therefore new buffers should be included as well, pointing to the new tables.

Changes in the key: New key DOCITEMCOND_GUID was introduced. All tables will share this GUID as well as additional fields required by the key.

Every update on the old buffer will be reflected simultaneously on the new buffer and will be recorded in the new DB.

Silent Data Migration (SDM) CL_SDM_CPED_MIGRATE_COMPLETE from the old to the new DB ensures that all continues to work properly. After the new installation, the system will automatically perform the migration report (SDM), so that both databases will be updated with the same records for a certain period of time.

New data model is activated by two business functions:

LOG_CMM_PRC_CPE_SMPLFCTN LOG_CMM_PRC_CPE_STOP_OLD. Before customers can use the new tables in transactions, both business function must have been activated.

Comparison report CMM_SCPE_COMPARISON_REPORT: With this report you check the results of the data migration from the old to the new CPE database tables. For more information, see the report documentation.

## List of the tables that are involved

| Original DB Table   | Corresponding Optimized DB Table   |
|---------------------|------------------------------------|
| CPED_FORMDOC        | CPE_FORMULA                        |
| CPED_FORMINPUT      | CPE_FORMULA                        |
| CPED_FORMCONVIN     | CPE_FORMCONV                       |
| CPED_FORMCONVOUT    | CPE_FORMCONV                       |
| CPED_FORMROUNDIN    | CPE_FORMROUNDING                   |
| CPED_TERMOUT        | CPE_TERM                           |

| CPED_TERMGRPOUT   | CPE_TERM         |
|-------------------|------------------|
| CPED_TERMINPUT    | CPE_TERM         |
| CPED_PERIODDTIN   | CPE_TERM         |
| CPED_PERIODDTOUT  | CPE_TERM         |
| CPED_PRIFIXDEF    | CEP_TERM         |
| CPED_TIER         | CPE_TERM         |
| CPED_TERMCONVIN   | CPE_TERMCONV     |
| CPED_TERMCONVOUT  | CPE_TERMCONV     |
| CPED_TERMROUNDIN  | CPE_TERMROUNDING |
| CPED_EXCHRATE     | CPE_EXCHANGERATE |
| CPED_QUOTATION    | CPE_QUOTATION    |

Total of original CPE tables: 18

Total of optimized CPE tables: 8

## Business Process related information

Since it expected that old and new data model are semantically equivalent, no impact on business processes is expected.

## Required and Recommended Action(s)

SAP delivers a 'Silent Database Migration', which will migrate all standard fields from the old data model to the new data model. Customers can use both data models in parallel for a certain time of period to check the consistency with a provided report. Two business functions are provided to finally switch to the new data model.

While standard fields are migrated without any manual work, please note that for custom fields and custom coding manual preparational steps might be necessary. This could mean, for example, that custom fields need to be added again to the new database table so that they can be filled during the migration by the SDM report.

For detailed description of the migration process, please refer to note 3207069

## Other Terms

CPE, Commodity Pricing, Commodity Management, CL_SDM_CPED_MIGRATE_COMPLETE, LOG_CMM_PRC_CPE_SM PLFCTN LOG_CMM_PRC_CPE_STOP_OLD
