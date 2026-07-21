---
item_id: SI-8.3
title: "8.3 S4TWL - REPLACED TRANSACTION CODES AND PROGRAMS IN FIN"
pages: 247-249
sap_notes: [1972819, 2119188, 2253067, 2257555, 2270387, 2270388, 2474069, 2726778, 2742613]
components: [FI, AC, FIN-FSCM, CO]
objects: []
---
## Application Components:FI, AC, FIN-FSCM, CO

Related Notes:

| Note Type       |   Note Number | Note Description                                                                   |
|-----------------|---------------|------------------------------------------------------------------------------------|
| Business Impact |       2742613 | Obsolete or replaced transaction codes and programs in Finance applications of S/4 |

## Symptom

You are doing a system conversion to SAP S/4HANA, on-premise edition.

With the installation of the SAP S/4HANA on-premise edition certain transaction codes and programs in the application areas of Controlling, General Ledger, Asset Accounting, Accounts Payable and Receivable, Treasury and Risk Management - compared to EhP7 for SAP ERP 6.0 - have been removed and partially replaced with newer transactions, programs or WebDynpro applications.

## Reason and Prerequisites

Task : Check if the customer uses any of the transactions or programs listed in the attached list of transactions and programs.

Procedure : Use transaction ST03N to list transaction codes and programs used in the system in the past.

## Solution

SAP recommends you to read the scope information in SAP Note 2119188 for a general overview on supported functions and compatibility information.

Note that with S/4HANA the logic of SAP General Ledger (New GL) is used. The Classic General Ledger application is automatically transformed into a basic implementation of New General Ledger (not adding addidional ledgers, nor document splitting functionality). Therefore transactions of classic General Ledger have to be replaced by the relevant transactions from New General ledger. These transactions are not explicitly mentioned in this note.

Transactions, programs and WebDynpro applications which are not supported are listed in the attached PDF document.

## Classic CO-OM planning transactions instead of SAP BPC optimized for SAP S/4HANA

In case you cannnot transition to SAP BPC optimized for SAP S/4HANA in the shortterm, but have strong reasons to continue to use the classic CO-OM planning functions, you may do so, but these transactions are not included in the SAP Easy Access Menu.

Please be aware that the classic planning functions don't update the new planning table (ACDOCP), which is available from SAP S/4HANA 1610. This means that legacy reports and follow-on processes will continue to work, but that Fiori apps based on the new table will not display plan data entered with classic planning functions.

## BW-Extractors and SAP BPC optimized for SAP S/4HANA

Customers that in the past used BW-extractors to extract and report FI-GL plan data will as of now make use of the SAP BPC optimized for SAP S/4HANA functionality. This new planning application serves to record plan data for FI and CO. In order to activate the SAP BPC optmized for SAP S/4HANA functionality, check SAP Note 1972819. The documentation can be found here: http://help.sap.com .

The classic GL planning functions can be reactivated for a transition period by following the instructions in the SAP Notes 2253067 and 2474069.

Treasury and Risk Management Obsolete Transactions and Programs in Treasury and Risk Management are described and listed in the SAP Note 2726778.

## Asset Accounting

The affected transactions, programs and WebDynpro applications and its replacements are listed in the release notes for Asset Accounting and the following notes:

Notes:

2270387: S4TWL - Asset Accounting: Changes to Data Structure

2270388: S4TWL - Asset Accounting: Parallel Valuation and Journal Entry

2257555: S4TWL - Asset Accounting: Business Functions from FI-AA and FI-GL

Release Notes:

EN:  ttp://help.sap.com/saphelp_sfin200/helpdata/en/ce/fbe15459e0713be10000000a441 76d/content.htm?frameset=/en/6f/bf8f546ac0c164e10000000a44176d/frameset.htm&curr ent_toc=/en/55/4b6154b6718c4ce10000000a4450e5/plain.htm&node_id=12

DE:  ttp://help.sap.com/saphelp_sfin200/helpdata/de/ce/fbe15459e0713be10000000a441 76d/content.htm?frameset=/de/6f/bf8f546ac0c164e10000000a44176d/frameset.htm&curr ent_toc=/de/55/4b6154b6718c4ce10000000a4450e5/plain.htm&node_id=12

## Other Terms

Out of scope, disabled transactions
