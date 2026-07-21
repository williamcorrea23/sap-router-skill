---
item_id: SI-2.27
title: "2.27 S4TWL - BI Extractors in SAP S/4HANA"
pages: 64-69
sap_notes: [2267784, 2270133, 2270505, 2270550, 2273294, 2299213, 2333141, 2382662, 2496759, 2498211, 2498786, 2499310, 2499589, 2499716, 2499728, 2500202, 2504508, 2533548, 2543469, 2543543, 2544193, 2546102, 2552797, 2556359, 2559556, 2576363, 2796696]
components: [XX-SER-REL]
objects: []
---
Application Components:XX-SER-REL

Related Notes:

| Note Type       |   Note Number | Note Description                     |
|-----------------|---------------|--------------------------------------|
| Business Impact |       2500202 | S4TWL - BW Extractors in SAP S/4HANA |

## Symptom

Customers considering moving to SAP S/4HANA (on premise) seek information whether BW extractors (aka data sources) known form SAP ERP still work, to be able to evaluate the potential impact on the BW environment when moving to SAP S/4HANA. To meet this requirement, SAP reviewed the status and the attached list (MS Excel document) provides the information that we have per extractor. The results are valid from SAP S/4HANA 1709 (on premise) until further notice or otherwise and in most cases apply to SAP S/4HANA 1610 and SAP S/4HANA 1511 as well (see respective flags in attached MS Excel document).

## Reason and Prerequisites

Parts of this information are already available in CSS and can be found through 2333141 - SAP S/4HANA 1610: Restriction Note. The status of the extractors is collected in one list (the attached MS Excel document), see the attached MS Powerpoint document for information how the list is typically used. Not all extractors that are technically available in SAP S/4HANA are covered, SAP is planning to provide clarifications for additional extractors and share new versions of the list via this note. Hence it is recommended to review this note for updates.

The information in this file is dated as of 10.09.2018. Please acknowledge that S/4HANA functionality is set forth in the S/4HANA Feature Scope Description. All business functionality not set forth therein is not licensed for use by customer.

Please note that extractors in the namespace 0BWTC*, 0TCT* and 8* are related to the "Embedded BW" that is offered as a technology component within the S/4HANA software stack. They are all not explicitly whitelisted in this SAP Note as they are not part of the delivered Business Content by the S/4HANA Lines of Business but can be used for extraction.

0BWTC* and 0TCT* are extractors providing technical statistical information from the Embedded BW such as query runtime statistics or data loading statistics.

8* are Export DataSources for transferring business data from InfoProviders of the 'Embedded BW' system to a target system

For a SAP BW target systems this is achieved by the SAP Source System type

For a data transfer via the ODP Source System type (only option in SAP BW/4HANA target system) these Export DataSources are obsolete and invisible. Instead, the ODP-BW context is used. For more information on Operational Data Provisioning see the ODP FAQ document.

For more information and positioning on the "Embedded BW" see: https://www.sap.com/documents/2015/06/3ccee34c-577c-0010-82c7-eda71af511fa.html

For more information on partner registered data sources and to find partner details from partner namespaces, please create a message on component XX-SER-DNSP.

This is a collective note, containing information of several industries and areas. In case issues arrise with extractors listed in the Excel, or missing extractors, please do raise an incident on the APPLICATION COMPONENT of the respective EXTRACTOR. This is the only way to ensure that your incident reaches the responsible desk in the shortest time. You can find this in column E,

'Appl.component' in the attached excel document. Do not use the component from this note. Thank you!

## Solution

Details can be found in the respective note per area:

| Item Area - Line of Business                | Note number for details                                                                                                                           |
|---------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Asset Management                            | 2299213 - Restrictions for BW-Extractors in S/4HANA in the Enterprise Asset Management domain (EAM)                                               |
| Business Process Management                 | 2796696 - Restrictions for BW extractors relevant for S/4HANA as part of SAP S/4HANA, on-premise edition 1709 and above                           |
| Customer Services                           | 2533548 - Restrictions for BW-Extractors in S/4HANA in the CS (Customer Service) area                                                             |
| Enterprise Portfolio and Project Management | 2496759 - Restrictions for BW extractors relevant for S/4HANA in the area of Enterprise Portfolio and Project Management                          |
| Financials                                  | 2270133 - Restrictions for BW extractors relevant for S/4HANA Finance as part of SAP S/4HANA, on-premise edition 1511                             |
| Flexible Real Estate                        | 2270550 - S4TWL - Real Estate Classic                                                                                                             |
| Global Trade                                |                                                                                                                                                   |
| Globalization Services Finance              | 2559556 - Restrictions for BW extractors in Financial Localizations relevant for S/4HANA Finance as part of SAP S/4HANA, on- premise edition 1511 |
| Human Resources                             |                                                                                                                                                   |
| Incident Management and Risk Assessment     | 2267784 - S4TWL - Simplification in Incident Management and Risk Assessment                                                                       |
| Master Data                                 | 2498786 - Data Sources supported by Central Master Data in S/4HANA 2576363 - Data Sources supported by Master Data Governance in S/4HANA          |

| Procurement                                  | 2504508 - Restrictions for BW Extractors relevant for S/4 HANA Procurement as part of SAP S/4HANA, on premise edition 1709 and above                                                                                                                                                                                                                                                                                                    |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Produce                                      | 2499728 - Restrictions for BW extractors relevant for S/4HANA in the area of Production Planning and Detailed Scheduling 2499716 - Restrictions for BW extractors relevant for S/4HANA in the area of Production Planning and Control 2499589 - Restrictions for BW extractors relevant for S/4HANA in the area of Quality Management 2499310 - Restrictions for BW extractors relevant for S/4HANA in the area of Inventory Management |
| Sales and Distribution                       | 2498211 - Restrictions for BW extractors relevant for S/4HANA Sales as part of SAP S/4HANA, on-premise edition 1709                                                                                                                                                                                                                                                                                                                     |
| Supply Chain - Extended Warehouse Management | 2552797 List of BI Data Sources used in EWM 2382662 List of BI Data Sources from SCM Basis used in EWM Context                                                                                                                                                                                                                                                                                                                          |
| Supply Chain - Transportation Management     | All Data Sources working and whitelisted, no separate note exists                                                                                                                                                                                                                                                                                                                                                                       |
| Master data governance for Finance           | All Data Sources working and whitelisted, no separate note exists                                                                                                                                                                                                                                                                                                                                                                       |

| Item Area - Industry                             | Note number for details                                                                                                                                                                          |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DIMP Automotive                                  |                                                                                                                                                                                                  |
| Defense and Security                             | 2544193 - Restrictions for BW extractors relevant for S/4HANA in the area of Defense & Security 2273294 - S4TWL - BI content, Datasources and Extractors for DFPS                                |
| Financial Services                               | 2543469 - "SAP for Banking": SAP extractors in connection with "SAP S/4HANA on-premise edition 2546102 - "SAP for Insurance": SAP extractors in connection with "SAP S/4HANA on-premise edition' |
| Higher Education                                 |                                                                                                                                                                                                  |
| IS Healthcare                                    | -                                                                                                                                                                                                |
| IS Utilities                                     | 2270505 - S4TWL - IS-U Stock, Transaction and Master Data Statistics (UIS, BW)                                                                                                                   |
| Oil and Gas                                      |                                                                                                                                                                                                  |
| Public Sector Collection and Disbursement (PSCD) | All Data Sources working and whitelisted, no separate note exists                                                                                                                                |

| Public Sector Management (PSM)   | 2556359 - Restrictions for BW extractors relevant for S/4HANA in the area of Public Sector Management   |
|----------------------------------|---------------------------------------------------------------------------------------------------------|
| IS Retail                        | 2543543 - Restrictions for BW extractors relevant for S/4HANA in the area of Retail                     |

## The classification scheme is:

| Current status                 | Status for Publication                                                                      | Description                                                                                                                                                                              |
|--------------------------------|---------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Whitelisted                    | DS working - no restrictions                                                                | DataSource is available with S/4 and works without any restrictions compared to ERP                                                                                                      |
| Whitelisted                    | DS working - regeneration of extractor and check of BW content based on this DS is needed . | DataSource is working, because of data model changes, it is recommended to check the upward dataflow.                                                                                    |
| Not Whitelisted                | DS working - restrictions                                                                   | DataSource is available with S/4 but works with noteworthy restrictions; e.g. not all fields are available                                                                               |
| Not Whitelisted                | DS not working - alternative exists                                                         | DataSource is not working with S/4 but an alternative exists, such as a new extractor, CDS view                                                                                          |
| Not Whitelisted                | DS not working - alternative planned                                                        | DataSource is not working with S/4 but equivalent available on roadmap for future release                                                                                                |
| Deprecated                     | DS obsolete                                                                                 | DataSource is obsolete - legacy extractors                                                                                                                                               |
| Deprecated                     | DS not working - no alternative exists                                                      | DataSource is not working with S/4 but no alternative exists                                                                                                                             |
| Generated Data Source          | DS working - no restrictions                                                                | Because of the nature of the extractors, being generated in the system, we cannot whitelist those in general. Experience so far showed that they should be working without restrictions. |
| Not relevant for BW extraction | DS not relevant                                                                             | Datasource is available in ROOSOURCE, however, not to be used for extraction by BW.                                                                                                      |

## Other Terms

BW, Extractors, Datasources, SAP S/4HANA
