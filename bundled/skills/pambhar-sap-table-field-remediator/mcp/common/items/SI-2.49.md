---
item_id: SI-2.49
title: "2.49 S4TWL - JOB SCHEDULING"
pages: 115-117
sap_notes: [2190119, 2318468, 2499529]
components: [BC-CCM-BTC]
objects: []
---
## Application Components:BC-CCM-BTC

Related Notes:

| Note Type       |   Note Number | Note Description       |
|-----------------|---------------|------------------------|
| Business Impact |       2318468 | S4TWL - JOB SCHEDULING |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Reason and Prerequisites

SAP S/4HANA contains a new component which automatically schedules certain technical background jobs. Deleting or modifying such jobs manually (via transaction SM37) will not have a lasting effect since the automation mechanism will re-schedule these jobs with predefined attributes. Job Definitions can be customized or deactivated via transaction SJOBREPO.

## Solution

## Description

Scheduling (and monitoring) "Standard Jobs" (e.g. SAP_REORG_SPOOL, SAP_REORG_ABAPDUMPS, SAP_REORG_JOBS etc.) was a manual action in SAP

ERP.  Choosing Standard Jobs in transaction SM36 displayed a table of standard job templates which the customer could choose to schedule.

In SAP S/4HANA, this manual action has been replaced by an automatic mechanism, the Technical Job Repository. SAP S/4HANA Technical Job Repository takes care of scheduling (and de-scheduling) necessary standard jobs (as defined and delivered by SAP) automatically, without any user intervention.

Nevertheless, in case of conflicts, it is possible to do customizations to job definitions, for example modify the execution period (or start time) of a job or disable automatic job scheduling of a job entirely because you want to use an own job with different report variant.

Two important job definitions which should be reviewed by customers after upgrade to SAP S/4HANA are described here:

## 1) SAP_REORG_JOBS:

This job definition schedules report RSBTCDEL2 daily in client 000 with variant SAP&001. This report+variant performs deletion of background jobs older than 14 days. If customer desires different deletion criteria (for example delete all jobs older than 7 days or exclude certain jobs from deletion), disable SAP-delivered job definition SAP_REORG_JOBS via transaction SJOBREPO (must be logged on in client 000 because this job definition is only relevant for client 000) and schedule a custom job with custom variant.

## 2) SAP_REORG_SPOOL:

This job definition schedules report RSPO0041 daily in client 000 with variant SAP&001. This report+variant performs deletion of spool requests that have reached their deletion date in all clients. If customer desires different spool deletion criteria, disable SAP-delivered job definition SAP_REORG_SPOOL via transaction SJOBREPO (must be logged on in client 000) and schedule a custom job with custom variant.

Note: It is possible for customers to create customer-owned job definitions via transaction SE80.

For more information and a guide to SAP S/4HANA Technical Job Repository, see SAP Note 2190119.

## Business Process related information

No influence on business processes expected.

Required and Recommended Action(s)

IMPORTANT: Before the upgrade/migration to SAP S/4HANA (i.e. in your original system), apply SNOTE correction from note 2499529.

This correction ensures that automatic job scheduling of Technical Job Repository in the SAP S/4HANA system will be delayed even after the point in time when the technical upgrade is over. In other words, it ensures that no automatic job scheduling by Technical Job Repository occurs automatically after the conversion to SAP S/4HANA.

Applying the note prevents for example that jobs automatically scheduled by Job Repository in SAP S/4HANA (this can occur once the technical upgrade phase is over) delete valuable data (e.g. background jobs older than 14 days, spool requests that have reached their retention period) of your old system which the customer wants to retain after the technical upgrade phase.

Without above correction, Job Repository will schedule jobs (including SAP_REORG_JOBS, SAP_REORG_SPOOL) directly after the end of the technical upgrade phase, which may not be desired! For example, job SAP_REORG_JOBS (scheduled from Job Repository) deletes all background jobs older than 14 days.

IMPORTANT: After the upgrade/migration to SAP S/4HANA, apply the correction from note 2499529 also in your new system. This correction will ensure that automatic  job scheduling by Technical Job Repository will commence once report BTCTRNS2 is executed by the conversion team. Be sure to have deactivated unwanted job definitions (for example SAP_REORG_JOBS) in SJOBREPO by that time.

## Other Terms

Background Jobs, Batch, Standard Jobs, SM36
