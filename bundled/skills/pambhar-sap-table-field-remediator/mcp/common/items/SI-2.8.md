---
item_id: SI-2.8
title: "2.8 ABAPTWL - No support for non simplified system flavour"
pages: 38-39
sap_notes: [2656503]
components: [BC-ABA-LA]
objects: []
---
Application Components:BC-ABA-LA

Related Notes:

| Note Type       |   Note Number | Note Description                             |
|-----------------|---------------|----------------------------------------------|
| Business Impact |       2656503 | No support for non simplified system flavour |

## Symptom

You are using profile parameter system/usage_flavor without any effect.

## Reason and Prerequisites

S/4 systems only support the simplified system flavor. This includes for example that it support Hana database only.

## Solution

The parameter is obsolete and shall no longer be set. The new behavior equals parameter value SIMPLE.

## Other Terms

Simplification
