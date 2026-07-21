---
item_id: SI-2.33
title: "2.33 S4TWL - Generic Check for SAP S/4HANA Conversion and Upgrade"
pages: 87-90
sap_notes: [1484142, 2241080, 2618018, 2749796]
components: [CA-TRS-PRCK]
objects: [BSEG, MARA, VBAK]
---
Application Components:CA-TRS-PRCK

Related Notes:

| Note Type       |   Note Number | Note Description                                             |
|-----------------|---------------|--------------------------------------------------------------|
| Business Impact |       2618018 | S4TWL - Generic Check for SAP S/4HANA Conversion and Upgrade |

## Symptom

You are planning to do

a system conversion from SAP ERP 6.0 or SAP S/4HANA Finance to SAP S/4HANA

or a release upgrade SAP S/4HANA to a higher SAP S/4HANA release

and want to learn about important things to know, critical preparation activities and checks to be done, which are directly related to the preparation of the the system conversion or upgrade.

## Solution

Unlike other Simplification Items, this Simplification Item does not describe a specific functional or technical change in SAP S/4HANA. But it is a collector for various generic, technical checks which need to run before a conversion or upgrade in SAP S/4HANA and which could affect any customer system - irrespective of the specific SAP S/4HANA target release. Many of these checks are not even SAP S/4HANA specific, but are checking for constellations which were already considered to be inconsistent in SAP ERP and could also have caused issues during an SAP ERP release upgrade.

As of now the check class CLS4SIC_GENERIC_CHECKS for this Simplification Item contains the following generic checks:

## Check for orphaned client dependent data

All client dependent data in a system must be associated with a client which officially exists in the system (in table T000). In case a client was improperly / incompletely deleted in the past, this might lead to the situation that orphaned, client dependent data exists in a system, which is no longer associated to a registered client. This can cause issues during lifecycle processes like upgrades and system conversions. Hence the check class will do a heuristic check as of SAP S/4HANA 1809, whether there is any orphaned, client dependent data in your system and raise a corresponding warning. While not mandatory, it's highly recommended to clean this up before a system conversion or release upgrade.

To avoid long check runtime, the check is only looking for usr02 (user master data) records which do not belong to a client that exists in the system. In order to further analyze to what extent orphaned, client dependent data exists in your system, for those clients mentioned in the check message, you can do additional manual checks on other commonly used, client dependent tables. e.g. if the check did report orphaned data in client 123, you can go to DBACOCKPIT=> Diagnostics => SQL Editor and run the following SQL "SELECT * FROM <table name> WHERE mandt = 123" for tables like MARA, BSEG, VBAK, EKKO, MARC, MARD...

Depending on whether you also find data in these other tables for this nonexistent client, you can decide, whether a cleanup activitiy is required.

The recommended approach for cleaning up such orphaned client data is, to first recreate the client for which orphaned data exists, then logon to this client and properly delete it with transaction SCC5. But before always check, if this orphaned data is indeed no longer required - the technical possibility to have client dependant data without an associated client is sometimes misused in consulting projects or by customer specific/3rd party coding e.g. to have "hidden" client backups in the system or for data replication purposes. To be on the safe side, keep a system backup from before deleting the data.

In addition the check also identifies clients that have no data but still an entry in T000. In such a case the orphaned T000 entry can be deleted with transaction SCC4.

## Existence and syntax check for check classes

Checks, whether the other check classes and related objects ( XS4SIC_* / CLS4SIC_* ) of the Simplification Item Check framework exist in the system and if they are syntactically correct. This check might prompt you to manually reactivate some objects or install specific notes, in case any issues are found.

## Check for inconsistent entries in tables TNIW5 / TNIW5W

Please see SAP Note 1484142 for further information.

## Check for inconsistent entries in tables TBP2B / TFB03T

Please see SAP Note 2749796 for further information.

In addition, this Simplification Item serves as an anchor for assigning custom code check related content (see SAP note 2241080), which is not related to any technical or functional changes in SAP S/4HANA. Most notably the deletion SAP development objects from the SAP S/4HANA codeline which are unused / orphaned. Therefore, in case this note is mentioned in the result of SAP S/4HANA specific ATC checks, please remove all usages of the related SAP objects from your custom code. There are no specific replacements for these objects.

## Other Terms

SAP S/4HANA, Generic Checks, Simplification Item
