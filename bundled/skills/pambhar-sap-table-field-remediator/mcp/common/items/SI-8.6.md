---
item_id: SI-8.6
title: "8.6 S4TWL - Migration from account solution to ledger solution"
pages: 261-262
sap_notes: [3042755]
components: [FI-AA, FI-GL]
objects: []
---
## Application Components:FI-AA, FI-GL

Related Notes:

| Note Type       |   Note Number | Note Description                                           |
|-----------------|---------------|------------------------------------------------------------|
| Business Impact |       3042755 | S4TWL - Migration from account solution to ledger solution |

## Symptom

You plan a system conversion from SAP ERP to SAP S/4HANA or you are already on SAP S/4HANA and you use parallel accounts to represent different accounting principles. You would like to use the parallel ledger functionality. The following SAP S/4HANA Transition Worklist item is applicable in this case.

## Solution

## Business Process related information

The whole financial accounting and management accounting functionality in SAP S/4HANA builds on the universal journal and the usage of parallel ledgers to manage parallel accounting principles. Future innovations assume the usage of parallel ledgers.

If you have used parallel GL accounts to represent different accounting principles in SAP ERP you can still perform a system conversion to SAP S/4HANA and continue using parallel GL accounts. However, to fully profit from recent and future innovations in SAP S/4HANA you would need to move to parallel ledgers.

## Required and recommended actions

For a move to parallel ledgers, you consider the following three options:

You can switch to parallel ledgers already in SAP ERP before converting to SAP S/4HANA. Prerequisite for this migration is the usage of the New General Ledger in SAP ERP. SAP offers services to perform the migration. Refer to SAP note 756146.

SAP DMLT offers one step approach to switch from accounts to ledger approach while migrating to S/4HANA using Selective Data Transition. For more details please contact: SAP DMLT Global Customer Engagement sap_dmlt_gce@sap.com.

If you already use SAP S/4HANA and would like to do the transformation from parallel accounts to parallel ledgers, SAP also offers a consulting service to do the migration. Please contact your SAP account team if you are interested.

Note: If you plan to do your transition from SAP ERP to SAP S/4HANA by a new implementation of SAP S/4HANA, we strongly recommend that you no longer use the account approach for parallel accounting.

## Other Terms

Parallel accounts, parallel ledgers, account approach, ledger approach
