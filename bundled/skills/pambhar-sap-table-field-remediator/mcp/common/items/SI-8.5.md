---
item_id: SI-8.5
title: "8.5 S4TWL - Plan data is not migrated to SAP S/4HANA"
pages: 255-260
sap_notes: [1009299, 2226649, 2227515, 2253067, 2270407, 2346854, 2403964, 2474069, 2924568, 2977560]
components: [FI-SL-SL]
objects: []
---
Application Components:FI-SL-SL

Related Notes:

| Note Type       |   Note Number | Note Description        |
|-----------------|---------------|-------------------------|
| Business Impact |       2474069 | Reactivate G/L planning |

## Symptom

You have migrated from an ERP system to an S/4HANA Finance or an S/4HANA system. You have used the General Ledger Accounting (new) (FI-GL (new)) planning function. After the upgrade and the migration, you can no longer access the G/L planning data. The planning transactions have disappeared from the SAP menu, as have the IMG activities for G/L planning. In the columns for the planning data, the system always displays the value 0 if you have defined the following: drilldown reports, Report Painter reports, or Report Writer reports that read G/L planning data (such as planned/actual comparisons).

## Reason and Prerequisites

The classic ERP FI-GL (new) planning is no longer supported in S/4HANA Finance or S/4HANA and should be replaced with the component SAP Analytics Cloud (SAC). More info on SAC can be found in notes 2977560, 2270407 and blog https://community.sap.com/t5/technology-blogs-by-sap/integrated-financialplanning-an-overview/ba-p/13544197 .

## Solution

If you cannot immediately convert your entry of G/L planning data and your reporting to BPC for S/4HANA, you can continue to use your G/L planning function for a time in S/4HANA as well via the steps described below. The steps also contain modifications.

SAP reserves the right to deactivate the old ERP planning function definitively at some point.

Additional conditions are: The old G/L planning can really only continue to be used. In other words, planning can be done only for ledgers that already existed in the ERP system (but not, for example, for ledgers that were created after the migration). For example, you can no longer add any new customer fields to your old G/L table. Your existing planned/actual comparisons are restricted to the dimensions that they had before the migration. For instance, they cannot report about dimensions of your choice in the universal journal introduced in S/4HANA. The status is frozen to a certain extent.

Implement SAP Notes 2227515 and 2226649 to release deactivated functions (or import the relevant Support Package) if you have not already done so.

Implement the corrections of technical prerequisite note 2253067 or import the relevant Support Package.

In order to activate G/L planning, you must first execute the report FINS_SET_DEPR_STATUS (with the option 'Activate') - if this has not already been done - and then insert some transactions into the view FINS_DEPR_OBJECT using transaction SM30. This addition is a modification; SAP can change or delete these entries. The following list is to be considered as a superset; we recommend that you add only the ones that you actually require (Note: adding Transaction GP12N is mandatory). Point 3) is also the only thing that you have to do if all source code corrections are already present in your system (so if you have an S4CORE 100 system with an SP level above 1 or if you have an S4CORE 101 (or a higher release) system). If you are a greenfield customer, you must also refer to point 4 .

GP12N ("Enter planning data")

GP12NA (" Display Plan Data")

FAGLP03 ("Display Plan Line Items")

GLPLUP ("Upload Plan Data from Excel")

FAGLGP52N ("Copy Planning Data")

FAGL_PLAN_VT ("Balance Carryforward: Plan Data")

FAGLPLSET ("Set Planning Profile")

FAGLGA47 ("Create Plan Distribution")

FAGLGA48 ("Change Plan Distribution")

FAGLGA49 ("Display Plan Distribution")

FAGLGA4A ("Delete Plan Distribution")

FAGLGA4B ("Execute Plan Distribution")

FAGLGA4C (for the plan distribution overview)

FAGLGA27 ("Create Plan Assessment")

FAGLGA28 ("Change Plan Assessment")

FAGLGA29 ("Display Plan Assessment")

FAGLGA2A ("Delete Plan Assessment")

FAGLGA2B ("Execute Plan Assessment")

FAGLGA2C ("Plan Assessment Overview")

FAGLGCLE ("Activate Plan Line Items")

FAGLPLI ("Create Planning Layout")

FAGLPLC ("Change Planning Layout")

FAGLPLD ("Display Planning Layout")

GLPLD (also "Display Planning Layout")

FAGL_CO_PLAN ("Transfer Planning Data from CO-OM")

In the view FINS_DEPR_OBJECT, set the object type TRAN for all of these transactions.

If you use the BAPI BAPI_FAGL_PLANNING_POST for the external data transfer, you must also include the program (object type PROG)

SAPLFAGL_PLANNING_RFC in the view.

If you want to use the report FAGL_PLAN_ACT_SEC to activate/deactivate the update of planning data to secondary cost elements (see also SAP Note 1009299), you must also include the program (object type PROG) FAGL_PLAN_ACT_SEC here.

Save the newly added entries.

4. Only for customers who have installed a fresh S/4HANA Finance or S/4HANA system (a greenfield approach) or who have migrated from classic G/L (table GLT0):

Call transaction GLPLINST, enter the table FAGLFLEXT as the totals table, and press F8 ("Execute") and F3 ("Back").

## Use transaction SE38 to create the program

ZCOPY_ENTRIES_FOR_GL_PLANNING (in a valid customer package) with the title "Copying of Entries for GL Planning", type 1 ("Executable Program"). Copy and paste the coding of ZCOPY_ENTRIES_FOR_GL_PLANNING from the attachment 'ZCOPY_ENTRIES_FOR_GL_PLANNING'. After program was created, navigate to the text elements of the program. Create text symbol 001 with the text "Warning", text symbol 002 with the text "Do you want to continue? Integrated FI currencies of the non-leading ledgers for the company code can't be changed any more.", text symbol 003 with text "OK" and text symbol 004 with the text "Cancel". Activate the text elements.

Decide in which ledgers and company codes you want to use planning. If this includes new company codes just recently created, go to IMG activity Financial Accounting->Financial Accounting Global Settings->Ledgers->Ledger->Define Settings for Ledgers and Currency Types (transaction FINSC_LEDGER). Here, go to view 'Company Code Settings for the Ledger' for each of the affected ledgers and check and maintain currency settings according to your requirements in the new company codes.

Execute the program ZCOPY_ENTRIES_FOR_GL_PLANNING for all ledgers and all company codes in which you want to use planning.

## Attention:

Execute report ZCOPY_ENTRIES_FOR_GL_PLANNING only after you made sure currency settings are correctly maintained for the affected company codes in transaction FINSC_LEDGER.

The purpose of report ZCOPY_ENTRIES_FOR_GL_PLANNING is to create entries in obsolete tables T881 and T882G. These will be used in the reactivated classic G/L planning. Once created, there is no IMG activity to remove the entries from the obsolete tables T881 and T882G in S/4HANA. These entries have an influence on maintenace of the 2nd and 3rd integrated FI currency in transaction FINSC_LEDGER. If entries in table T882G exist, 2nd and 3rd integrated FI currencies are not inherited from the leading to the non-leading ledger, because migrated company codes are identified via existing entries in table T882G to prevent changes. In ECC integrated FI currencies were not automatically inherited to the non-leading ledgers. By contrast, these properties are inherited for new created company codes in S/4HANA.

Check the assignment of your ledgers to the General Ledger Accounting (new) update scenarios (transaction SM34, view cluster VC_FAGL_LEDGER) and, if necessary, assign the desired update scenarios to your ledgers. During the transfer of planning data from CO to GL, only the fields assigned here (via the scenarios) are updated. (These scenarios are irrelevant for the actual data update in S/4HANA; they apply only for classic planning data.)

If you are on S4CORE 100 or SAP_FIN 730 please make sure that SAP Note 2346854 is implemented. Otherwise, the system might think that you still need to carry out a migration (even though you are a greenfield customer) and might therefore set a posting lock; you are then unable to carry out any further actual postings.

If the planning layouts should be missing when executing planning transaction GP12N, please execute transaction GLPLIMPORT to import the following planning layouts from client 000:

0FAGL-01

0FAGL-02

0FAGL-03

0FAGL-04

0FAGL-05

0FAGL-06

0FAGL-07

You should now be able enter, display and report G/L planning data, and all of your functions in the G/L planning environment should exist and work properly.

If you migrate from classic G/L, the planning data which existed already before migration is copied to table GLT0_BCK. To copy this data to the reactivated planning tables, please ask the SAP support to give you access to pilot note 2924568 - SAP S/4HANA: Transfer of classic planning data from table GLT0_BCK.

The G/L planning transactions (see the list above) are no longer available in the SAP menu, and the G/L planning IMG activities are also not included in the SAP Reference

IMG. We recommend creating a folder in your favorites that contains all the transactions you require. The following is a list of the IMG activities or their transaction codes:

SM30, view V_T001B_PL ("Define Plan Periods")

GLPV (for defining planning versions)

GLP2 (for assigning and activating planning versions)

FAGLGCLE ("Activate Line Items")

GP30 (for defining distribution keys)

FAGLPLI ("Create Planning Layout")

FAGLPLC ("Change Planning Layout")

FAGLPLD ("Display Planning Layout")

GLPLADM (for creating/changing planner profiles)

GLPLANZ (for displaying planner profiles)

SM30, view V_FAGL_T889A ("Define Document Types for Planning")

SNRO, object FAGL_PL_LC ("Define Number Ranges for Plan Documents")

FAGL_CO_PLAN ("Transfer Planning Data from CO-OM")

KE1Z ("Transfer Planning Data from CO-PA")

If you are missing plan/actual reporting transactions like S_E38_98000088 or S_PL0_86000031, you can easily recreate them with transaction maintenance SE93>Create, on the next popup select "Transaction with parameters (parameter transaction)", Enter, on the next screen copy the all the values from the respective transaction in your ERP system (open SE93 in your ERP system, enter e.g. transaction S_E38_98000088, press "Display" and copy the values you find there)

Note that you only require SAP Note 2403964 if you want to reactivate certain planning transactions only for the component FI-SL. In this case this SAP Note 2474069 is not required.
