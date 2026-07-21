---
item_id: SI-2.50
title: "2.50 S4TWL - LEGACY SYSTEM MIGRATION WORKBENCH"
pages: 117-122
sap_notes: [2239701, 2287723]
components: [BC-SRV-DX-LSM]
objects: []
---
Application Components:BC-SRV-DX-LSM

Related Notes:

| Note Type       |   Note Number | Note Description                        |
|-----------------|---------------|-----------------------------------------|
| Business Impact |       2287723 | LSMW in SAP S/4HANA on-premise (S4CORE) |

## Symptom

For the data migration to SAP ERP, SAP offered the legacy system migration workbench (transaction code LSMW). But for the migration of business data to SAP S/4HANA and SAP S/4HANA Cloud, the SAP S/4HANA migration cockpit is the tool of choice. It is designed for the initial data load of master data and open transactional data. LSMW is on the simplification list and the use of LSMW is restricted in the context of data migrations to SAP S/4HANA. Even if the LSMW could be used in some areas, it might propose incorrect migration interfaces that cannot be used in SAP S/4HANA anymore. There is no support given in the context of data migrations to SAP S/4HANA.

This SAP Note is valid only for customers implementing SAP S/4HANA or SAP S/4HANA Cloud Private Edition.

## Reason and Prerequisites

The Legacy System Migration Workbench (LSMW) is an SAP NetWeaver tool for data migration that was first introduced with R/2 to R/3 data migration. It uses standard interfaces like BAPIs, IDocs, Direct Input and Batch Input programs and recordings initially build for SAP ERP. Due to this nature, the use of LSMW is restricted in the context of data migrations to SAP S/4HANA.

For restrictions on certain BAPIs, IDocs, Batch Input or Direct Input programs that are used by LSMW, please get in touch with the application components directly.

## Solution

The use of LSMW for data load to SAP S/4HANA is not recommended and at the customer's own responsibility . Instead, the SAP S/4HANA migration cockpit is SAP's solution for data migration to SAP S/4HANA. You should always check if the object is available with the SAP S/4HANA migration cockpit before using the LSMW.

If you still use the LSMW, you have to carefully test the processes so that you can ensure that it is actually working for you. It might not work for you and in any case.

Expect restrictions around transaction recording (as this is not possible with the new SAP Fiori screens) and changed interfaces (for instance the Business Partner CVI). Standard Batch Input programs may also no longer work as transactions may have changed functionality or may be completely removed within some areas. For example, due to security reasons batch import has been limited for RCCLBI02 program. Also, transactions for customer master data (FD*/XD*) and vendor master data (FK*/XK*) cannot be used anymore due to the change to the Business Partner data model in SAP S/4HANA.

Option 1: SAP S/4HANA Migration Cockpit and Migration Object Modeler

The SAP S/4HANA migration cockpit is SAP's recommended tool of choice for the data migration to SAP S/4HANA and SAP S/4HANA Cloud. It provides all functions required for the migration of business data in a new implementation and is part of SAP S/4HANA and SAP S/4HANA Cloud Private Edition.

For the migration to SAP S/4HANA Cloud Public Edition, the migration cockpit is the only tool available to migrate business data.

For the data migration, the cockpit uses predefined migration content that is, standard migration objects such as customers, suppliers or purchase orders to identify and transfer the relevant data. These migration objects contain predefined mapping to facilitate the migration.

Since SAP S/4HANA 2020 and for SAP S/4HANA Cloud Private Edition, the SAP S/4HANA migration cockpit has the following two migration approaches:

## Migrate Data Using Staging Tables (SAP S/4HANA)

As of Release SAP S/4HANA 1709, FPS01, the migration cockpit contains the data transfer option using staging tables. As of SAP S/4HANA 2020 a new Fiori UI was introduced and since then, the file migration approach is embedded in the Staging tables approach ('Migrate Data Using Staging Tables', Migrate your Data - Migration Cockpit App) . This means that XML template files or CSV template files are provided for every migration object and, you can use these templates to fill the staging tables with data. Alternatively, you can fill the staging tables by using your preferred tools (for example SAP Data Services, SDI, etc.). The SAP S/4HANA migration cockpit creates staging tables for the migration objects that are relevant for your project and migrates data from these staging tables to the target SAP S/4HANA system.

## Migrate Data Directly from SAP System (as of SAP S/4HANA 1909)

This migration approach that is delivered new with SAP S/4HANA 1909 allows you to directly transfer data from SAP source systems to SAP S/4HANA. The migration cockpit selects the data relevant for dedicated migration objects in the source system with the help of predefined selection criteria and directly transfers them to the SAP S/4HANA target system via an RFC connection.

## Integration of custom data:

In addition, the cockpit allows you to integrate your custom data objects into the migration using the migration object modeler which is part of the cockpit. For example, you can adjust the predefined standard migration objects delivered with the cockpit by adding fields to them. As of SAP S/4HANA 1610, FPS02 in the file and staging approach, you can also create your own custom-specific migration objects or SAP

standard objects that have not yet been included in the scope of the migration cockpit. For the direct transfer, the migration object modeler is also available.

## Required roles:

## For file and staging approach:

For current information and more details about the file and staging approaches and required roles for SAP S/4HANA (on-premise version), please see:

## SAP S/4HANA (S4CORE):

SAP Help Portal: SAP S/4HANA - SAP S/4HANA Migration Cockpit

Installation Guide for S/4HANA (on-premise only) available under: https://help.sap.com/viewer/p/SAP_S4HANA_ON-PREMISE → <Filter-Version>

Product Documentation → Installation Guide → 7. Installation Follow-Up Activities

For direct transfer approach:

For current information about the business roles needed and more details about the direct transfer, please see:

## SAP S/4HANA (S4CORE):

SAP Help Portal: SAP S/4HANA Migration Cockpit - Migrate Data Directly from an SAP System

available under:

Installation Guide for S/4HANA (on-premise only)

https://help.sap.com/viewer/p/SAP_S4HANA_ON-PREMISE → <FilterVersion> Product Documentation → Installation Guide → 7. Installation Follow-Up Activities

## Data Migration Objects available for the Migration Cockpit:

For a list of available migration objects that are supported with SAP S/4HANA 1909 or higher versions, see https://help.sap.com/S4_OP_MO

For further information about data migration and the migration cockpit (SAP S/4HANA), see the data migration landing page in the SAP Help Portal under https://help.sap.com/S4_OP_DM

Option 2: SAP Rapid Data Migration with SAP Data Services

SAP S/4HANA data migration content called SAP Rapid Data Migration based on SAP Data Services software is still available and will be maintained further to migrate data into SAP S/4HANA (on premise). But no new objects will be created. Yet, SAP will further invest into migration content for the SAP S/4HANA migration cockpit which already offers more migration objects than the RDS.

This package is part of SAP's Rapid deployment solution (RDS). You can find more information in SAP Note 2239701 - SAP Rapid Data Migration for SAP S/4HANA, on premise edition and under the link below:

## https://rapid.sap.com/bp/RDM_S4H_OP

This content has been specifically built for the new SAP S/4HANA target system, its interfaces and data structures. The content is free of charge and can be downloaded under the link above. There are two ways to leverage the content:

## Base: Data Integrator

SAP S/4HANA customers have access to a basic Data Integrator license key that comes with the underlying SAP HANA license (HANA REAB or HANA Enterprise). This key code applied to SAP Data Services provides full ETL functionalities (Extract, Transform, Load). Thus, it replaces a mapping and load tool like LSMW with the Rapid Data Migration content. With this basic data load functionality of SAP Data Services and together with the Rapid Data Migration content, legacy data can be loaded into SAP S/4HANA (on premise) including data validation but without further Data Quality (de-duplication, data cleansing) and reporting capabilities. For this use case with the before mentioned functionality, SAP Data Services is free of charge and there is no additional cost.

## Full: Data Services

Using the full SAP Data Services license (separately licensed and not part of SAP S/4HANA) unleashes all Data Quality features like data cleansing and deduplication for mitigating risk during the data migration process of a new SAP S/4HANA implementation.

The SAP S/4HANA migration cockpit can be  used in addition to the Rapid Data Migration content.

## How to Determine Relevancy

This simplification item is relevant if you plan to continue to use Legacy System Migration Workbench to migrate data into SAP S/4HANA after System Conversion

Migration Cockpit versus LSMW

As mentioned earlier, the SAP S/4HANA migration cockpit is SAP's recommended tool of choice for data migration to SAP S/4HANA. In this section we would like to point out a few advantages of the SAP S/4HANA migration cockpit against LSMW:

The cockpit's preconfigured migration content significantly facilitates data migration projects whereas the LSMW does not provide any content. Migration logic had to be created from scratch.

The migration object modeler is a powerful and easy-to-use state-of-the-art modeling environment that allows the creation of custom migration objects as well as the adaptation of SAP content.

More information on What Is the Difference Between the Legacy Migration Workbench (LSMW) and the SAP S/4HANA Migration Cockpit can be found in the following here.

If you have any feedback regarding the SAP S/4HANA migration cockpit compared to LSMW please feel free to share this via SAP_S4HANA_Migration_Cockpit@sap.com

## Other Terms

LSMW, Rapid Data Migration, RDS, Best Practices, SAP S/4HANA, SAP S/4HANA Migration Cockpit, SAP Data Services
