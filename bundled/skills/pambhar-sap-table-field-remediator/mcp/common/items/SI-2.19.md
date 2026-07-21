---
item_id: SI-2.19
title: "2.19 S4TWL - SAP S/4HANA AND SAP BUSINESS WAREHOUSE CONTENT"
pages: 51-53
sap_notes: [2289424, 2360258, 2500202, 2548065]
components: [BW-BCT-GEN]
objects: []
---
Application Components:BW-BCT-GEN

Related Notes:

| Note Type       |   Note Number | Note Description                                                           |
|-----------------|---------------|----------------------------------------------------------------------------|
| Business Impact |       2289424 | S4TWL - SAP S/4HANA and SAP Business Warehouse Content - BI_CONT / BW4CONT |

## Symptom

You are doing a new installation or system conversion to SAP S/4HANA, on-premise or cloud edition. The following item is applicable in this case.

## Solution

## Embedded BW in SAP S/4HANA

The software components BI_CONT (BI Content) and BI_CONT_XT (BI Content Extensions) are not supported in the Embedded BW client of all editions and releases of SAP S/4HANA (cloud and on premise), even though they are technically installable.

Exception: For usage of SEM-BCS in embedded BW in S/4HANA on premise as outlined in SAP Note 2360258, installation of BI_CONT is a necessary prerequisite

Content Bundle: The only supported Content Bundle in SAP S/4HANA system is /ERP/SFIN_PLANNING (Simplified Financials Planning). All other content bundles are not supported in SAP S/4HANA.

## Standalone SAP Netweaver BW

Only the SAP HANA-optimized Business Content shipped with the software component version BI_CONT 7.57 (BI Content 7.57; see also SAP Note 153967) is supported for the whitelisted DataSources delivered with SAP S/4HANA (as specified in SAP Note 2500202). For further details on SAP HANA-Optimized Business Content please check SAP Note 2548065.

## Standalone SAP BW/4HANA

All content included in the BW/4HANA Content Basis (software component BW4CONTB) and BW/4HANA Content (software component BW4CONT) is supported for the whitelisted DataSources delivered with SAP S/4HANA (as specified in SAP Note 2500202). For further details on SAP HANA-Optimized Business Content please check SAP Note 2548065.

## Other Terms

BI_CONT, BI_CONT_XT, BW4CONTB, BW4CONT, SAP BW, SAP BW/4 HANA, SAP_BW, DW4CORE, Business Content, SAP Netweaver, S/4HANA
