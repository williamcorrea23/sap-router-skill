---
item_id: SI-3.18
title: "3.18 S4TWL - Usage of obsolete links in tables BD001 / BC001"
pages: 152-153
sap_notes: [3010257]
components: [LO-MD-BP]
objects: []
---
Application Components:LO-MD-BP

Related Notes:

| Note Type       |   Note Number | Note Description                                        |
|-----------------|---------------|---------------------------------------------------------|
| Business Impact |       3010257 | S4TWL - Usage of obsolete links in tables BD001 / BC001 |

## Symptom

You execute a system conversion to S/4HANA 2021 or lower. If you use the customer vendor integration (CVI) and still have entries in the old link tables BD001/BC001 ( Business Partner: Assignment Customer - Partner/Business Partner: Assign Vendor Partner) you need to migrate these entries to the new link tables CVI_CUST_LINK/CVI_VEND_LINK ( Assignment Between Customer and Business Partner/ Assignment Between Vendor and Business Partner) before migration.

## Reason and Prerequisites

With this note a new check is integrated into the pre-upgrade checks which enforces migration of the old link tables. Before migration can be executed the old link tables need to be migrated to the new ones.

## Solution

## Procedure to determine relevance

A new check class is integrated into the simplification element check report /SDF/RC_CHECK_START. (This is delivered as part of note3009162 Simplification Check in BD001 and BC001 Tables )

This class checks if there are still unmigrated entries in the database tables BD001/BC001. If so, a migration is not possible.

In detail the following checks are made:

select all entries from BD001/BC001 tables.

For all entries found in BD001 select entries in CVI_CUST_LINK

For all entries found in BC001 select entries in CVI_VEND_LINK

if at least one entry is found in BD001 that is not available in CVI_CUST_LINK or in BC001 that is not available in CVI_VEND_LINK an error is returned by the check class.

An error in the check class means that the migration cannot be executed until the underlying problem is solved.

## Required Action:

In case the check class returns an error, you need to execute the two migration reports CVI_MIGRATE_CUST_LINK and CVI_MIGRATE_VEND_LINK.

After that all links should be available in CVI_CUST_LINK/CVI_VEND_LINK tables and the check should not lead to an error anymore.

## Further actions sometime after the conversion

After the conversion all entries in the two tables- BD001/BC001 need to be deleted.

Before you do this, you should wait some time in order to be sure that the customer and BP link/Vendor and BP link is correctly working in all the relevant applications.

The deletion should be done at the latest, before you start planning the next upgrade to a higher release level of S/4HANA.

## Other Terms

BD001, BC001, CVI_CUST_LINK, CVI_VEND_LINK, CVI_MIGRATE_CUST_LINKS, CVI_MIGRATE_VEND_LINKS
