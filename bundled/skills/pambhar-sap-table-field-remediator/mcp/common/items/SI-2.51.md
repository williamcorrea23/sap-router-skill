---
item_id: SI-2.51
title: "2.51 ABAPTWL - Deprecation of Hana Rules Framework"
pages: 122-124
sap_notes: [3150564, 3243120]
components: [BC-SRV-BR]
objects: []
---
Application Components:BC-SRV-BR

Related Notes:

| Note Type       |   Note Number | Note Description                                |
|-----------------|---------------|-------------------------------------------------|
| Business Impact |       3243120 | S4TWL - Deprecation of SAP Hana Rules Framework |

## Symptom

You are upgrading your system to S/4HANA On-Premise 2022 FPS1 or following releases from an older release.

## Reason and Prerequisites

Deprecation of SAP HANA Rules Framework.

## Solution

## Description

The functionality to build and to model analytical rules via BRF+ and to push these rules down to HANA (SAP HANA Rules Framework) is deprecated now and will be removed as a comprised component in S/4HANA On-Premise 2023.

## Business Process related information

It will not be possible to create analytical functions in BRF+ projects. Already created analytical functions will stop working with S/4HANA On-Premise 2023.

## Required and Recommended Action(s)

Please carry out a manual migration or remodeling from HRF (analytical function) to Business Rule Framework plus (BRF+).

See

also https://help.sap.com/docs/ABAP_PLATFORM_NEW/9d5c91746d2f48199bd465c3 a4973b89/9a6b67ce7c26446483af079719edf679.html?version=201809.000

## Other Terms

Business Rule Framework plus (BRF+), SAP HANA Rules Framework (HRF)

## 2.52 ABAP Test Framework: Export of ATC Results to 3rd Party Tools

Application Components:BC-DWB-TOO-ATF

Related Notes:

| Note Type       |   Note Number | Note Description                                                       |
|-----------------|---------------|------------------------------------------------------------------------|
| Business Impact |       3150564 | ABAP package SATC_CI_EXT_TOOLS_INTEGRATION is not available in S/4HANA |

## Symptom

ABAP package SATC_CI_EXT_TOOLS_INTEGRATION is not available in S/4HANA.

## Reason and Prerequisites

Replication of scan results from Code Vulnerability Analyzer to external targets is discontinued.

## Solution

In case you have references in your custom programs to ABAP artifacts of package SATC_CI_EXT_TOOLS_INTEGRATION, please remove these usages before you migrate your SAP NetWeaver based custom ABAP to S/4HANA product family.

## Other Terms

Replicating CVA Results from ATC to external tools

## 3. Master Data
