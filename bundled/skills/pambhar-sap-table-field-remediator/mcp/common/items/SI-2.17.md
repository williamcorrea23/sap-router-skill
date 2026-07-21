---
item_id: SI-2.17
title: "2.17 ABAPTWL - End of Support for Pool Tables"
pages: 46-49
sap_notes: [2234970, 2577406]
components: [BC-DWB-DIC]
objects: [BSEG, CDPOS, RFBLG]
---
Application Components:BC-DWB-DIC

Related Notes:

| Note Type       |   Note Number | Note Description                                                                                          |
|-----------------|---------------|-----------------------------------------------------------------------------------------------------------|
| Business Impact |       2577406 | S4TWL - End of support for pool tables, cluster tables, table pools and table clusters with S/4 HANA 1809 |

## Symptom

You are doing a system conversion or upgrade to SAP S/4HANA 1809 on-premise edition release 1809 or higher. You have been using pool tables or cluster tables. The following SAP S/4HANA Transition Worklist Item is applicable in this case.

## Solution

## Description

Starting with release S/4 HANA 1809 pool tables and cluster tables are no longer supported. Automatic transformation of pool tables and cluster tables to transparent tables and the removal of table pools and table clusters is integrated into the upgrade or migration to S/4 HANA 1809.

Hint: Table clusters (examples: CDCLS, RFBLG, DOKCLU, ...) or cluster tables (examples: CDPOS, BSEG, DOKTL, ... in non-HANA Systems) must not be mixed up with export/import-tables (examples: INDX, STXL, ...). Export/import tables are used to store object collections as data clusters with the ABAP statement "EXPORT ... TO DATABASE ...". Export/import tables are still supported in 1809.

## Business Process related information

The concept of pool and cluster tables is regarded as obsolete, particularly in the context of the HANA database. They implement an own limited in-memory mini-DBMS that is not transparent to the underlying database and that interferes with the optimization strategies of the underlying database. Accordingly, de-clustering and de-pooling is part of migrations to HANA based products already before release 1809. However, creation of new pool and cluster tables was still possible. With the mandatory transformation into transparent tables it is guaranteed that tables always have the optimal format for HANA.

## Required and Recommended Action(s)

As in release 1809 table pools and table clusters (both have the object type R3TR SQLT; example table pool is ATAB; example table cluster is CDCLS) are removed, customer coding that has references to table pools or table clusters needs to be adapted. Such references are typically rare. ABAP coding normally deals with the logical tables (pool table or cluster table), which are still existing as transparent tables after the conversion, and not with the container tables (i.e. the table pools or table clusters).

If references to table pools and table clusters are not removed, syntax errors will show up in coding with such references after the upgrade or conversion to release 1809.

In addition coding that referenced the repository tables for table pools and table clusters needs to be adapted. All access to the tables DD06L, DD06T, DD16S and to the views DD06V, DD06VV and DD16V needs to be removed, as those tables and views do no longer exist in release 1809.

## How to Determine Relevancy

Coding places that need to be adapted can be found as follows:

References to table pools and table clusters:

## Determine object list of references to table pools and table clusters:

All SQLT objects, that will no longer exist in release 1809 can be found in the table TADIR. Display the table content of table TADIR with transaction SE16 and select all SQLT object names with the selection "program id" = R3TR; "object type" = SQLT. Copy the list of SQLT objects into the clipboard.

## Quick Check:

Use the cross-reference table WBCROSSGT to find all coding places that use SQLT objects. First make sure that in the system you are using for the check the cross-reference tables are properly filled (see SAP Note 2234970 for details ). Then display the table content of table WBCROSSGT with transaction SE16 and select all programs that use SQLT objects with the selection "version number component" = TY; "object" = <paste the object list determined in step 1>. If the result list shows customer programs you are affected .

## Detailed Check:

Use the code inspector (transaction SCI) to get a detailed list of all coding places. Create a check variant using the check "Search Functions" -> "Objects used in programs". In the search pattern list enter \TY:<SQLT object> for all SQLT objects determined in step 1 (Example: \TY:ATAB ). Define an object set that includes all customer objects and run an inspection with the check variant and object set to get the detail list of all places.

Remove all usages of SQLT objects in your coding. Hint: Pure type references can be replaced by references to the fields of the logical tables. As an alternative you can use in releases based on ABAP Platform 1709 (SAP_BASIS 752) or newer the code inspector check variant "Pools/ClusterTypes used in Programs". With this check variant you don't need to enter the object list manually.

## References to SQLT repository tables and views:

## Repository tables object list:

DD06L, DD06T, DD16S, DD06V, DD06VV, DD16V

## Quick Check:

Use the cross-reference table WBCROSSGT to find all coding places that use the objects from step 1. Display the table content of table WBCROSSGT with transaction SE16 and select all programs that use the objects with the selection "version number component" = TY; "object" = <paste the object list from step 1>. If the result list shows customer programs you are affected .

## Detailed Check:

Use the code inspector (transaction SCI) to get a detailed list of all coding places. Create a check variant using the check "Search Functions" -> "Objects used in programs". In the search pattern list enter \TY:<object list from step

1>  (Example: \TY:DD06L ). Define an object set that includes all customer objects and run an inspection with the check variant and object set to get the detail list of all places.

Remove all usages of the repository tables and views in your coding.

## Transport behavior

Cross release transports (R3trans) are in general not recommended. The import behavior for pool- and cluster related objects and content in systems with release 1809 or higher is given below for your information:

## Importing definitions of table pools or table clusters (R3TR SQLT):

The object is not imported into the system. The transport finishes with RC = 4. In the DDIC import protocol a warning is issued.

## Importing content of a table pool or table cluster (R3TR TABU on table pool or table cluster):

The content is not imported as the table cluster or table pool does not exist in the target system. The R3trans return code is RC = 8.

## Importing definitions of pool tables or cluster tables (R3TR TABD/TABL for tables that are pool tables or cluster tables in the export system):

The table is treated as transparent table.

## Importing content of a pool table or cluster table (R3TR TABU on table pool or table cluster):

The content is imported as of today if an according transparent table is existing.
