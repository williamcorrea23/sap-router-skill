---
item_id: SI-2.30
title: "2.30 ABAPTWL - Change of workflow system user and workflow system jobs"
pages: 71-73
sap_notes: [2190119, 2568271]
components: [BC-BMT-WFM]
objects: []
---
Application Components:BC-BMT-WFM

Related Notes:

| Note Type       |   Note Number | Note Description                                                                |
|-----------------|---------------|---------------------------------------------------------------------------------|
| Business Impact |       2568271 | Change of workflow system user and workflow system jobs with S/4HANA On-Premise |

## Symptom

You upgraded your system from a release prior to S/4 Hana On-Premise 1709 to S/4 Hana On-Premise 1709 or any higher S/4 Hana on premise release .

In "Automatic Workflow Customizing", transaction SWU3 you notice the status is not green for "Edit Runtime Environment".

## Reason and Prerequisites

Change of workflow system user and workflow system jobs with S/4HANA On-Premise 1709.

Solution

Description Starting with S/4 Hana OnPremise 1709 the workflow system user and workflow system jobs changed. The workflow system user is called SAP_WFRT now instead of WFBATCH. The workflow system jobs start with SAP_WORKFLOW now and are scheduled automatically by "Technical Job Repository", transaction SJOBREPO.

Starting with S/4 Hana OnPremise 1809 the workflow system jobs are scheduled under the user, under which the system jobs of Technical Job Repository run. This might be a different user than SAP_WFRT.

## Business-Process-Related Information

SAP Business Workflow does not continue after upgrade.

## Required and Recommended Action(s)

Deschedule the "old" workflow jobs in all system clients , in case these are still scheduled from the time before the upgrade. These are the following jobs:

SWEQSRV

SWWCLEAR

SWWCOND

SWWDHEX

SWWERRE

SWWRUNCNT

SWWWIM

Make sure that user SAP_WFRT exists in the system and has role SAP_BC_BMT_WFM_SERV_USER_PLV01 assigned.

Check role SAP_BC_BMT_WFM_SERV_USER_PLV01 e.g. in transaction PFCG:

Ensure that there is a green traffic light on tab "Authorizations". Regenerate the profile if necessary.

Afterwards check the traffic light on the tab "User". Run the "User Comparison" if the traffic light is not green.

In "Technical Job Repository" (transaction SJOBREPO) the automatic scheduling of jobs must be switched on. Note 2190119 - Background information about S/4HANA technical job repository - describes the prerequisites needed.

Wait for the next run of system job  "R_JR_BTCJOBS_GENERATOR" for the Technical Job Repository. It runs by default every hour and schedules all new workflow system jobs starting with SAP_WORKFLOW.

After the workflow jobs are scheduled, you will see green lights in transaction SWU3.

Job SAP_WORKFLOW_RESTART is automatically scheduled in the system. It runs once a day and restarts all workflows in error status automatically. These are workflows, you can find in transaction SWPR. If you do not want these workflows to be restarted, please deactivate the job in transaction SJOBREPO.

## Other Terms

SJOBREPO, SAP_WFRT, SWU3, 1709, 1809, 1909, 2020, 2021, 2022, 2023, 2024, 2025, 2026
